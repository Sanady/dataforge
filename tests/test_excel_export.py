"""Tests for Feature 9: XLSX Export."""

import os
import tempfile

import pytest

openpyxl = pytest.importorskip("openpyxl")

from dataforge import DataForge  # noqa: E402


# ── Parametrized export scenarios ───────────────────────────────────────

_EXPORT_CASES = [
    # (fields, count, sheet_name, expected_header, check_col_idx, check_fn)
    (
        ["first_name", "email"],
        10,
        None,
        ("first_name", "email"),
        1,
        lambda v: "@" in str(v),
    ),
    (["city"], 5, "Cities", None, None, None),
    (["first_name"], 25, None, None, None, None),
]


class TestSchemaToExcel:
    @pytest.mark.parametrize(
        "fields, count, sheet_name, expected_header, check_col_idx, check_fn",
        _EXPORT_CASES,
        ids=["basic_export", "custom_sheet", "returns_count"],
    )
    def test_export(
        self,
        fields: list[str],
        count: int,
        sheet_name: str | None,
        expected_header: tuple | None,
        check_col_idx: int | None,
        check_fn: object | None,
    ) -> None:
        forge = DataForge(seed=42)
        schema = forge.schema(fields)
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            path = f.name

        try:
            kwargs = {"count": count}
            if sheet_name:
                kwargs["sheet_name"] = sheet_name
            written = schema.to_excel(path, **kwargs)
            assert written == count
            assert os.path.exists(path)

            wb = openpyxl.load_workbook(path)
            if sheet_name:
                assert sheet_name in wb.sheetnames
            ws = wb.active
            rows = list(ws.iter_rows(values_only=True))
            if expected_header:
                assert rows[0] == expected_header
                assert len(rows) == count + 1  # header + data
            if check_col_idx is not None and check_fn is not None:
                for row in rows[1:]:
                    assert check_fn(row[check_col_idx])  # type: ignore[operator]
        finally:
            os.unlink(path)


class TestForgeToExcel:
    @pytest.mark.parametrize(
        "fields, count, expected_header",
        [
            (["first_name", "email"], 5, None),
            ({"Name": "full_name", "Email": "email"}, 3, ("Name", "Email")),
        ],
        ids=["list_fields", "dict_fields"],
    )
    def test_convenience_method(
        self,
        fields: list[str] | dict[str, str],
        count: int,
        expected_header: tuple | None,
    ) -> None:
        forge = DataForge(seed=42)
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            path = f.name

        try:
            written = forge.to_excel(fields, path=path, count=count)
            assert written == count
            assert os.path.exists(path)

            if expected_header:
                wb = openpyxl.load_workbook(path)
                ws = wb.active
                rows = list(ws.iter_rows(values_only=True))
                assert rows[0] == expected_header
        finally:
            os.unlink(path)
