"""Tests for Feature 9: XLSX Export."""

import os
import tempfile

import pytest

openpyxl = pytest.importorskip("openpyxl")

from dataforge import DataForge


class TestSchemaToExcel:
    def test_basic_export(self) -> None:
        forge = DataForge(seed=42)
        schema = forge.schema(["first_name", "email"])
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            path = f.name

        try:
            written = schema.to_excel(path, count=10)
            assert written == 10
            assert os.path.exists(path)

            wb = openpyxl.load_workbook(path)
            ws = wb.active
            # Header + 10 rows
            rows = list(ws.iter_rows(values_only=True))
            assert rows[0] == ("first_name", "email")
            assert len(rows) == 11  # header + 10 data rows
            # Check emails contain @
            for row in rows[1:]:
                assert "@" in str(row[1])
        finally:
            os.unlink(path)

    def test_custom_sheet_name(self) -> None:
        forge = DataForge(seed=42)
        schema = forge.schema(["city"])
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            path = f.name

        try:
            schema.to_excel(path, count=5, sheet_name="Cities")
            wb = openpyxl.load_workbook(path)
            assert "Cities" in wb.sheetnames
        finally:
            os.unlink(path)

    def test_returns_count(self) -> None:
        forge = DataForge(seed=42)
        schema = forge.schema(["first_name"])
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            path = f.name

        try:
            result = schema.to_excel(path, count=25)
            assert result == 25
        finally:
            os.unlink(path)


class TestForgeToExcel:
    def test_convenience_method(self) -> None:
        forge = DataForge(seed=42)
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            path = f.name

        try:
            written = forge.to_excel(
                ["first_name", "email"],
                path=path,
                count=5,
            )
            assert written == 5
            assert os.path.exists(path)
        finally:
            os.unlink(path)

    def test_dict_fields(self) -> None:
        forge = DataForge(seed=42)
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            path = f.name

        try:
            written = forge.to_excel(
                {"Name": "full_name", "Email": "email"},
                path=path,
                count=3,
            )
            assert written == 3

            wb = openpyxl.load_workbook(path)
            ws = wb.active
            rows = list(ws.iter_rows(values_only=True))
            assert rows[0] == ("Name", "Email")
        finally:
            os.unlink(path)
