"""Data contract validation — validate data against a DataForge Schema.

Validates that generated or external data conforms to the schema's
field types, null constraints, and semantic patterns.

Usage::

    from dataforge import DataForge

    forge = DataForge(seed=42)
    schema = forge.schema(["first_name", "email", "city"])
    report = schema.validate([
        {"first_name": "Alice", "email": "alice@example.com", "city": "NYC"},
        {"first_name": "", "email": "not-an-email", "city": "LA"},
    ])
    print(report.is_valid)   # False
    print(report.summary())  # human-readable summary
"""

from __future__ import annotations

import csv as _csv
import re as _re
from typing import Any


# Lightweight semantic validators (regex-based, no dependencies)
_VALIDATORS: dict[str, _re.Pattern[str]] = {
    "email": _re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$"),
    "ipv4": _re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"),
    "ipv6": _re.compile(r"^[0-9a-f:]{3,39}$", _re.I),
    "url": _re.compile(r"^https?://[^\s]+$"),
    "uuid4": _re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", _re.I
    ),
    "date": _re.compile(r"^\d{4}-\d{2}-\d{2}$"),
    "datetime": _re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}"),
    "time": _re.compile(r"^\d{2}:\d{2}(:\d{2})?$"),
    "phone_number": _re.compile(r"^[\+]?[\d\s\-\(\)]{7,20}$"),
    "zipcode": _re.compile(r"^\d{5}(-\d{4})?$"),
    "ssn": _re.compile(r"^\d{3}-\d{2}-\d{4}$"),
    "mac_address": _re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$"),
    "hex_color": _re.compile(r"^#[0-9a-fA-F]{6}$"),
    "credit_card_number": _re.compile(r"^\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}$"),
}

# Fields that should always have a non-empty string value
_NON_EMPTY_FIELDS: frozenset[str] = frozenset(
    {
        "first_name",
        "last_name",
        "full_name",
        "email",
        "city",
        "state",
        "country",
        "company_name",
        "job_title",
        "username",
        "domain_name",
    }
)


class Violation:
    """A single validation violation."""

    __slots__ = ("row", "column", "field", "value", "reason")

    def __init__(
        self,
        row: int,
        column: str,
        field: str,
        value: Any,
        reason: str,
    ) -> None:
        self.row = row
        self.column = column
        self.field = field
        self.value = value
        self.reason = reason

    def __repr__(self) -> str:
        return f"Violation(row={self.row}, col={self.column!r}, reason={self.reason!r})"


class ValidationReport:
    """Result of validating data against a schema contract."""

    __slots__ = ("violations", "total_rows", "total_columns")

    def __init__(
        self,
        violations: list[Violation],
        total_rows: int,
        total_columns: int,
    ) -> None:
        self.violations = violations
        self.total_rows = total_rows
        self.total_columns = total_columns

    @property
    def is_valid(self) -> bool:
        """``True`` if no violations were found."""
        return len(self.violations) == 0

    @property
    def violation_count(self) -> int:
        return len(self.violations)

    def violations_by_column(self) -> dict[str, list[Violation]]:
        """Group violations by column name."""
        by_col: dict[str, list[Violation]] = {}
        for v in self.violations:
            by_col.setdefault(v.column, []).append(v)
        return by_col

    def summary(self) -> str:
        """Return a human-readable summary of the validation results."""
        lines: list[str] = [
            f"Validation Report: {self.total_rows} rows, {self.total_columns} columns",
            "=" * 60,
        ]
        if self.is_valid:
            lines.append("  All data is valid.")
        else:
            lines.append(f"  {self.violation_count} violation(s) found:")
            by_col = self.violations_by_column()
            for col, viols in sorted(by_col.items()):
                lines.append(f"  {col}: {len(viols)} violation(s)")
                for v in viols[:5]:
                    val_str = repr(v.value)
                    if len(val_str) > 40:
                        val_str = val_str[:37] + "..."
                    lines.append(f"    row {v.row}: {v.reason} (value={val_str})")
                if len(viols) > 5:
                    lines.append(f"    ... and {len(viols) - 5} more")
        lines.append("=" * 60)
        return "\n".join(lines)

    def __repr__(self) -> str:
        status = (
            "VALID" if self.is_valid else f"INVALID ({self.violation_count} violations)"
        )
        return f"ValidationReport({status}, rows={self.total_rows})"


def validate_records(
    records: list[dict[str, Any]],
    field_map: dict[str, str],
    null_fields: dict[str, float] | None = None,
) -> ValidationReport:
    """Validate a list of dicts against a field mapping.

    Parameters
    ----------
    records : list of dict
        The data to validate.
    field_map : dict
        Mapping of column name → DataForge field name.
    null_fields : dict or None
        Allowed null rates per column (columns not listed must not be null).
    """
    if not records:
        return ValidationReport([], 0, len(field_map))

    violations: list[Violation] = []
    nullable = null_fields or {}

    for row_idx, row in enumerate(records):
        for col_name, field_name in field_map.items():
            value = row.get(col_name)

            # Check for missing column
            if col_name not in row:
                violations.append(
                    Violation(row_idx, col_name, field_name, None, "missing column")
                )
                continue

            # Check null
            is_null = value is None or (isinstance(value, str) and value.strip() == "")
            if is_null:
                if col_name not in nullable and field_name in _NON_EMPTY_FIELDS:
                    violations.append(
                        Violation(
                            row_idx,
                            col_name,
                            field_name,
                            value,
                            "unexpected null/empty value",
                        )
                    )
                continue

            # Semantic pattern validation
            base_field = field_name.split(".")[-1] if "." in field_name else field_name
            pattern = _VALIDATORS.get(base_field)
            if pattern is not None:
                if not pattern.match(str(value)):
                    violations.append(
                        Violation(
                            row_idx,
                            col_name,
                            field_name,
                            value,
                            f"does not match expected {base_field} pattern",
                        )
                    )

    return ValidationReport(violations, len(records), len(field_map))


def validate_csv(
    path: str,
    field_map: dict[str, str],
    null_fields: dict[str, float] | None = None,
    max_rows: int = 10_000,
    encoding: str = "utf-8",
    delimiter: str = ",",
) -> ValidationReport:
    """Validate a CSV file against a field mapping.

    Parameters
    ----------
    path : str
        Path to the CSV file.
    field_map : dict
        Mapping of column name → DataForge field name.
    null_fields : dict or None
        Allowed null rates per column.
    max_rows : int
        Maximum rows to validate (default 10,000).
    """
    records: list[dict[str, Any]] = []
    with open(path, "r", encoding=encoding, newline="") as f:
        reader = _csv.DictReader(f, delimiter=delimiter)
        for i, row in enumerate(reader):
            if i >= max_rows:
                break
            records.append(dict(row))
    return validate_records(records, field_map, null_fields)
