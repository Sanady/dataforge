"""Schema — zero-overhead bulk data generation via pre-resolved fields.

A ``Schema`` pre-resolves provider/method lookups once at creation time,
then generates rows with a tight loop over pre-bound callables — no
per-row field resolution, no ``getattr`` calls during generation.

Usage::

    from dataforge import DataForge

    forge = DataForge(seed=42)
    schema = forge.schema(["first_name", "email", "city"])
    rows   = schema.generate(count=1_000_000)

    # Lambda / correlated fields:
    schema = forge.schema({
        "name": "full_name",
        "email": "email",
        "username": lambda row: row["name"].lower().replace(" ", "."),
    })
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable, Iterator
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from dataforge.core import DataForge

# Sentinel for columns that depend on the current row
_ROW_LAMBDA = object()


class Schema:
    """Pre-resolved generation blueprint for maximum throughput.

    All field lookups are performed **once** during ``__init__``.
    Subsequent ``generate()`` calls execute only the bound methods
    with zero overhead from name resolution.

    Parameters
    ----------
    forge : DataForge
        The parent generator instance.
    fields : list[str] | dict[str, str | Callable]
        Fields to generate.  String values are resolved to provider
        methods.  Callable values receive the current row dict and
        can reference previously generated columns.
    """

    __slots__ = ("_columns", "_callables", "_row_lambdas")

    def __init__(
        self,
        forge: DataForge,
        fields: "list[str] | dict[str, Any]",
    ) -> None:
        # Normalize to (column_name, field_spec) pairs
        if isinstance(fields, list):
            field_defs: list[tuple[str, str | Callable[..., Any]]] = [
                (f, f) for f in fields
            ]
        else:
            field_defs = list(fields.items())

        columns: list[str] = []
        callables: list[object] = []
        row_lambdas: dict[int, Callable[..., Any]] = {}

        for idx, (col_name, field_spec) in enumerate(field_defs):
            columns.append(col_name)
            if callable(field_spec):
                # Row-dependent lambda — stored separately, executed
                # per-row after batch columns are generated.
                callables.append(_ROW_LAMBDA)
                row_lambdas[idx] = field_spec
            else:
                # String field name — resolve to provider method
                provider_attr, method_name = forge._resolve_field(field_spec)
                provider = getattr(forge, provider_attr)
                method = getattr(provider, method_name)
                callables.append(method)

        # Store as tuples for fastest iteration (bytecode LOAD_FAST)
        self._columns: tuple[str, ...] = tuple(columns)
        self._callables: tuple[object, ...] = tuple(callables)
        self._row_lambdas: dict[int, Callable[..., Any]] = row_lambdas

    # ------------------------------------------------------------------
    # Core generation
    # ------------------------------------------------------------------

    def _generate_columns(self, count: int) -> list[list[str]]:
        """Generate column data in bulk (column-first).

        Shared by :meth:`generate`, :meth:`stream`, and export helpers.
        Each field is generated in one batch call via its ``count=N``
        path — no per-row field resolution overhead.

        Row-lambda columns are filled with empty strings here and
        populated later by :meth:`_apply_row_lambdas`.

        Parameters
        ----------
        count : int
            Number of values per column.

        Returns
        -------
        list[list[str]]
        """
        col_data: list[list[str]] = []
        _sentinel = _ROW_LAMBDA
        _str = str
        _isinstance = isinstance
        for fn in self._callables:
            if fn is _sentinel:
                # Placeholder — filled by _apply_row_lambdas
                col_data.append([""] * count)
            elif count == 1:
                val = fn()  # type: ignore[operator]
                col_data.append([val if _isinstance(val, _str) else _str(val)])
            else:
                values = fn(count=count)  # type: ignore[operator]
                # Most providers return list[str] — skip redundant str()
                if values and _isinstance(values[0], _str):
                    col_data.append(values)  # type: ignore[arg-type]
                else:
                    col_data.append([_str(v) for v in values])
        return col_data

    def _apply_row_lambdas(self, rows: list[dict[str, str]]) -> list[dict[str, str]]:
        """Apply row-dependent lambdas to generated rows in-place.

        Each lambda receives the current row dict and its return
        value is converted to ``str`` and stored in the row.
        Lambdas are applied in column order, so later lambdas
        can reference earlier lambda-generated columns.
        """
        if not self._row_lambdas:
            return rows
        columns = self._columns
        for row in rows:
            for idx, fn in self._row_lambdas.items():
                val = fn(row)
                row[columns[idx]] = val if isinstance(val, str) else str(val)
        return rows

    def generate(self, count: int = 10) -> list[dict[str, str]]:
        """Generate *count* rows as a list of dicts.

        Uses **column-first generation**: each field is generated in
        bulk via its ``count=N`` batch path, then columns are zipped
        into row dicts. This replaces ``count × num_fields`` scalar
        calls with ``num_fields`` batch calls — significantly faster
        for large counts.

        Parameters
        ----------
        count : int
            Number of rows to generate.

        Returns
        -------
        list[dict[str, str]]
        """
        if count == 0:
            return []

        columns = self._columns
        col_data = self._generate_columns(count)

        # Zip columns into row dicts — transposed vectorized assembly
        rows = [dict(zip(columns, row)) for row in zip(*col_data)]
        return self._apply_row_lambdas(rows)

    def stream(
        self,
        count: int,
        batch_size: int | None = None,
    ) -> Iterator[dict[str, str]]:
        """Yield rows lazily in batches — avoids materializing all rows.

        Internally generates data in column-first batches for
        performance, but yields rows one at a time.

        Parameters
        ----------
        count : int
            Total number of rows to yield.
        batch_size : int | None
            Internal batch size for column-first generation.
            When ``None`` (default), the batch size is auto-tuned
            based on the number of columns and total count to
            balance throughput and memory usage.

        Yields
        ------
        dict[str, str]
        """
        columns = self._columns
        num_cols = len(columns)

        # Auto-tune batch size when not explicitly set.
        # More columns → smaller batches to bound memory; fewer columns
        # → larger batches to amortize per-batch overhead.  The floor
        # of 1000 keeps overhead low; the ceiling avoids over-allocating
        # when count is small.
        if batch_size is None:
            batch_size = min(count, max(1000, 100_000 // max(num_cols, 1)))

        remaining = count

        row_lambdas = self._row_lambdas
        while remaining > 0:
            chunk = min(remaining, batch_size)
            col_data = self._generate_columns(chunk)
            # Yield row dicts — transposed vectorized assembly
            if row_lambdas:
                batch_rows = [dict(zip(columns, row)) for row in zip(*col_data)]
                self._apply_row_lambdas(batch_rows)
                yield from batch_rows
            else:
                for row in zip(*col_data):
                    yield dict(zip(columns, row))
            remaining -= chunk

    async def async_stream(
        self,
        count: int,
        batch_size: int | None = None,
    ) -> AsyncIterator[dict[str, str]]:
        """Yield rows lazily via ``async for`` — one row at a time.

        Internally uses the same column-first batch generation as
        :meth:`stream` for maximum throughput.  Each batch is generated
        synchronously (CPU-bound work), then rows are yielded with an
        ``await``-compatible suspend point between batches so the event
        loop can service other coroutines.

        Usage::

            async for row in schema.async_stream(100_000):
                await process(row)

        Parameters
        ----------
        count : int
            Total number of rows to yield.
        batch_size : int | None
            Internal batch size.  Auto-tuned when ``None``.

        Yields
        ------
        dict[str, str]
        """
        import asyncio

        columns = self._columns
        num_cols = len(columns)

        if batch_size is None:
            batch_size = min(count, max(1000, 100_000 // max(num_cols, 1)))

        remaining = count
        row_lambdas = self._row_lambdas
        _sleep = asyncio.sleep

        while remaining > 0:
            chunk = min(remaining, batch_size)
            col_data = self._generate_columns(chunk)
            if row_lambdas:
                batch_rows = [dict(zip(columns, row)) for row in zip(*col_data)]
                self._apply_row_lambdas(batch_rows)
                for row in batch_rows:
                    yield row
            else:
                for row in zip(*col_data):
                    yield dict(zip(columns, row))
            remaining -= chunk
            # Yield control to the event loop between batches
            await _sleep(0)

    # ------------------------------------------------------------------
    # Export helpers
    # ------------------------------------------------------------------

    def to_csv(self, count: int = 10, path: str | None = None) -> str:
        """Generate rows and return as CSV string.

        Parameters
        ----------
        count : int
            Number of rows.
        path : str | None
            Optional file path to write.

        Returns
        -------
        str
        """
        import csv
        import io

        rows = self.generate(count)
        if not rows:
            return ""

        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=self._columns)
        writer.writeheader()
        writer.writerows(rows)
        content = buf.getvalue()

        if path is not None:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(content)

        return content

    def stream_to_csv(
        self,
        path: str,
        count: int = 10,
        batch_size: int | None = None,
    ) -> int:
        """Stream rows to a CSV file without materializing all data.

        Writes rows in batches to keep memory usage constant
        regardless of *count*.

        Parameters
        ----------
        path : str
            File path to write.
        count : int
            Total number of rows.
        batch_size : int | None
            Internal batch size.  Auto-tuned when ``None``.

        Returns
        -------
        int
            Number of rows written.
        """
        import csv

        columns = self._columns
        num_cols = len(columns)

        if batch_size is None:
            batch_size = min(count, max(1000, 100_000 // max(num_cols, 1)))

        written = 0
        row_lambdas = self._row_lambdas
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(columns)

            remaining = count
            while remaining > 0:
                chunk = min(remaining, batch_size)
                col_data = self._generate_columns(chunk)
                if row_lambdas:
                    batch_rows = [dict(zip(columns, row)) for row in zip(*col_data)]
                    self._apply_row_lambdas(batch_rows)
                    writer.writerows([row[c] for c in columns] for row in batch_rows)
                else:
                    # Write all rows in one call — avoids per-row Python
                    # function call overhead for csv.writer.writerow().
                    writer.writerows(zip(*col_data))
                written += chunk
                remaining -= chunk

        return written

    def to_jsonl(self, count: int = 10, path: str | None = None) -> str:
        """Generate rows and return as JSON Lines string.

        Parameters
        ----------
        count : int
            Number of rows.
        path : str | None
            Optional file path to write.

        Returns
        -------
        str
        """
        import json

        rows = self.generate(count)
        lines = [json.dumps(row, ensure_ascii=False) for row in rows]

        content = "\n".join(lines)
        if content:
            content += "\n"

        if path is not None:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

        return content

    def stream_to_jsonl(
        self,
        path: str,
        count: int = 10,
        batch_size: int | None = None,
    ) -> int:
        """Stream rows to a JSON Lines file without materializing all data.

        Writes rows in batches to keep memory usage constant
        regardless of *count*.

        Parameters
        ----------
        path : str
            File path to write.
        count : int
            Total number of rows.
        batch_size : int | None
            Internal batch size.  Auto-tuned when ``None``.

        Returns
        -------
        int
            Number of rows written.
        """
        import json

        columns = self._columns
        num_cols = len(columns)

        if batch_size is None:
            batch_size = min(count, max(1000, 100_000 // max(num_cols, 1)))

        _dumps = json.dumps
        written = 0
        row_lambdas = self._row_lambdas
        with open(path, "w", encoding="utf-8") as f:
            _write = f.write
            remaining = count
            while remaining > 0:
                chunk = min(remaining, batch_size)
                col_data = self._generate_columns(chunk)
                if row_lambdas:
                    batch_rows = [dict(zip(columns, row)) for row in zip(*col_data)]
                    self._apply_row_lambdas(batch_rows)
                    # Buffer entire batch into a single write call
                    _write(
                        "\n".join(_dumps(row, ensure_ascii=False) for row in batch_rows)
                        + "\n"
                    )
                else:
                    # Buffer entire batch — single write per batch instead
                    # of 2× write per row (data + newline).
                    _write(
                        "\n".join(
                            _dumps(dict(zip(columns, row)), ensure_ascii=False)
                            for row in zip(*col_data)
                        )
                        + "\n"
                    )
                written += chunk
                remaining -= chunk

        return written

    def to_sql(
        self,
        table: str,
        count: int = 10,
        dialect: str = "sqlite",
        path: str | None = None,
    ) -> str:
        """Generate rows and return as SQL INSERT statements.

        Parameters
        ----------
        table : str
            Target table name.
        count : int
            Number of rows.
        dialect : str
            SQL dialect: ``"sqlite"``, ``"mysql"``, or ``"postgresql"``.
        path : str | None
            If provided, write SQL to this file path.

        Returns
        -------
        str
        """
        rows = self.generate(count)
        if not rows:
            return ""

        columns = self._columns

        # Quote identifiers per dialect
        if dialect == "mysql":
            col_list = ", ".join(f"`{c}`" for c in columns)
            tbl = f"`{table}`"
        else:  # sqlite, postgresql — both use double quotes
            col_list = ", ".join(f'"{c}"' for c in columns)
            tbl = f'"{table}"'

        # Multi-row INSERT: batch 1000 rows per statement for
        # significantly fewer SQL statements and better throughput.
        _BATCH = 1000
        prefix = f"INSERT INTO {tbl} ({col_list}) VALUES"
        parts: list[str] = []
        for batch_start in range(0, len(rows), _BATCH):
            batch = rows[batch_start : batch_start + _BATCH]
            value_rows = []
            for row in batch:
                vals = ", ".join("'" + row[c].replace("'", "''") + "'" for c in columns)
                value_rows.append(f"({vals})")
            parts.append(f"{prefix}\n" + ",\n".join(value_rows) + ";")

        content = "\n".join(parts) + "\n"

        if path is not None:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

        return content

    def to_dataframe(self, count: int = 10) -> "Any":
        """Generate rows as a pandas DataFrame.

        Requires ``pandas`` to be installed.

        Parameters
        ----------
        count : int
            Number of rows.

        Returns
        -------
        pandas.DataFrame
        """
        try:
            import pandas as pd
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "pandas is required for to_dataframe(). "
                "Install it with: pip install pandas"
            ) from exc

        rows = self.generate(count)
        return pd.DataFrame(rows)

    def to_parquet(
        self,
        path: str,
        count: int = 10,
        batch_size: int | None = None,
    ) -> int:
        """Generate rows and write as a Parquet file.

        Uses **PyArrow** for zero-copy columnar writes.  Data is
        generated in batches and written as row-groups so memory
        stays bounded even for very large counts.

        Requires ``pyarrow`` to be installed.

        Parameters
        ----------
        path : str
            File path to write.
        count : int
            Number of rows.
        batch_size : int | None
            Rows per row-group.  Auto-tuned when ``None``.

        Returns
        -------
        int
            Number of rows written.
        """
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "pyarrow is required for to_parquet(). "
                "Install it with: pip install pyarrow"
            ) from exc

        columns = self._columns
        num_cols = len(columns)

        if batch_size is None:
            batch_size = min(count, max(1000, 100_000 // max(num_cols, 1)))

        schema = pa.schema([(col, pa.string()) for col in columns])
        written = 0
        row_lambdas = self._row_lambdas

        with pq.ParquetWriter(path, schema) as writer:
            remaining = count
            while remaining > 0:
                chunk = min(remaining, batch_size)
                col_data = self._generate_columns(chunk)
                if row_lambdas:
                    # Must apply lambdas row-wise, then re-extract columns
                    batch_rows = [dict(zip(columns, row)) for row in zip(*col_data)]
                    self._apply_row_lambdas(batch_rows)
                    col_data = [[row[c] for row in batch_rows] for c in columns]
                arrays = [pa.array(col, type=pa.string()) for col in col_data]
                batch = pa.RecordBatch.from_arrays(arrays, schema=schema)
                writer.write_batch(batch)
                written += chunk
                remaining -= chunk

        return written

    def __repr__(self) -> str:
        return f"Schema(columns={list(self._columns)!r})"

    # ------------------------------------------------------------------
    # Arrow / Polars output
    # ------------------------------------------------------------------

    def to_arrow(
        self,
        count: int = 10,
        batch_size: int | None = None,
    ) -> "Any":
        """Generate rows and return as a PyArrow Table.

        Uses **column-first generation** directly into Arrow arrays —
        no intermediate row-dict materialisation.  This is the fastest
        bulk export path because the data never leaves columnar form.

        When *count* exceeds *batch_size*, data is generated in batches
        and concatenated via ``pyarrow.concat_tables`` for bounded
        memory usage during generation.

        Requires ``pyarrow`` to be installed.

        Parameters
        ----------
        count : int
            Number of rows.
        batch_size : int | None
            Rows per internal batch.  Auto-tuned when ``None``.

        Returns
        -------
        pyarrow.Table
        """
        try:
            import pyarrow as pa
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "pyarrow is required for to_arrow(). "
                "Install it with: pip install pyarrow"
            ) from exc

        columns = self._columns
        num_cols = len(columns)

        if batch_size is None:
            batch_size = min(count, max(1000, 100_000 // max(num_cols, 1)))

        schema = pa.schema([(col, pa.string()) for col in columns])
        row_lambdas = self._row_lambdas

        if count <= batch_size:
            # Single-shot: no concat overhead
            col_data = self._generate_columns(count)
            if row_lambdas:
                batch_rows = [dict(zip(columns, row)) for row in zip(*col_data)]
                self._apply_row_lambdas(batch_rows)
                col_data = [[row[c] for row in batch_rows] for c in columns]
            arrays = [pa.array(col, type=pa.string()) for col in col_data]
            return pa.table(dict(zip(columns, arrays)), schema=schema)

        # Multi-batch: generate batches → concat
        batches: list[Any] = []
        remaining = count
        while remaining > 0:
            chunk = min(remaining, batch_size)
            col_data = self._generate_columns(chunk)
            if row_lambdas:
                batch_rows = [dict(zip(columns, row)) for row in zip(*col_data)]
                self._apply_row_lambdas(batch_rows)
                col_data = [[row[c] for row in batch_rows] for c in columns]
            arrays = [pa.array(col, type=pa.string()) for col in col_data]
            batches.append(pa.record_batch(arrays, schema=schema))
            remaining -= chunk

        return pa.Table.from_batches(batches, schema=schema)

    def to_polars(
        self,
        count: int = 10,
        batch_size: int | None = None,
    ) -> "Any":
        """Generate rows and return as a Polars DataFrame.

        Uses **column-first generation** directly into Polars Series —
        no intermediate row-dict materialisation.  This is significantly
        faster than converting via pandas because we skip the pandas
        intermediate entirely.

        When *count* exceeds *batch_size*, data is generated in batches
        and concatenated via ``polars.concat`` for bounded memory.

        Requires ``polars`` to be installed.

        Parameters
        ----------
        count : int
            Number of rows.
        batch_size : int | None
            Rows per internal batch.  Auto-tuned when ``None``.

        Returns
        -------
        polars.DataFrame
        """
        try:
            import polars as pl
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "polars is required for to_polars(). "
                "Install it with: pip install polars"
            ) from exc

        columns = self._columns
        num_cols = len(columns)

        if batch_size is None:
            batch_size = min(count, max(1000, 100_000 // max(num_cols, 1)))

        row_lambdas = self._row_lambdas

        if count <= batch_size:
            col_data = self._generate_columns(count)
            if row_lambdas:
                batch_rows = [dict(zip(columns, row)) for row in zip(*col_data)]
                self._apply_row_lambdas(batch_rows)
                col_data = [[row[c] for row in batch_rows] for c in columns]
            return pl.DataFrame(
                {col: data for col, data in zip(columns, col_data)},
                schema={col: pl.Utf8 for col in columns},
            )

        # Multi-batch: generate batches → concat
        frames: list[Any] = []
        remaining = count
        while remaining > 0:
            chunk = min(remaining, batch_size)
            col_data = self._generate_columns(chunk)
            if row_lambdas:
                batch_rows = [dict(zip(columns, row)) for row in zip(*col_data)]
                self._apply_row_lambdas(batch_rows)
                col_data = [[row[c] for row in batch_rows] for c in columns]
            frames.append(
                pl.DataFrame(
                    {col: data for col, data in zip(columns, col_data)},
                    schema={col: pl.Utf8 for col in columns},
                )
            )
            remaining -= chunk

        return pl.concat(frames)
