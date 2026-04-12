"""Tests for Feature 6: Data Contract Validation."""

import os
import tempfile

import pytest

from dataforge import DataForge
from dataforge.validation import (
    ValidationReport,
    Violation,
    validate_csv,
    validate_records,
)


class TestViolation:
    @pytest.mark.parametrize(
        "row, column, field, value, reason",
        [
            (0, "email", "email", "bad", "invalid format"),
            (1, "name", "full_name", "Alice", "too short"),
        ],
        ids=["email_violation", "name_violation"],
    )
    def test_violation_fields(
        self, row: int, column: str, field: str, value: str, reason: str
    ) -> None:
        v = Violation(row, column, field, value, reason)
        assert v.row == row
        assert v.column == column
        assert v.field == field
        assert v.value == value
        assert v.reason == reason

    def test_violation_repr(self) -> None:
        v = Violation(0, "email", "email", "bad", "invalid format")
        r = repr(v)
        assert "row=0" in r
        assert "email" in r
        assert "invalid format" in r


# ── Parametrized report checks ──────────────────────────────────────────


class TestValidationReport:
    @pytest.mark.parametrize(
        "violations, total, cols, is_valid, count, repr_contains",
        [
            ([], 10, 3, True, 0, "VALID"),
            (
                [Violation(0, "email", "email", "bad", "invalid")],
                10,
                3,
                False,
                1,
                "INVALID",
            ),
        ],
        ids=["valid", "invalid"],
    )
    def test_report_properties(
        self,
        violations: list[Violation],
        total: int,
        cols: int,
        is_valid: bool,
        count: int,
        repr_contains: str,
    ) -> None:
        report = ValidationReport(violations, total, cols)
        assert report.is_valid is is_valid
        assert report.violation_count == count
        assert repr_contains in repr(report)

    def test_violations_by_column(self) -> None:
        violations = [
            Violation(0, "email", "email", "bad1", "invalid"),
            Violation(1, "email", "email", "bad2", "invalid"),
            Violation(0, "name", "full_name", "", "empty"),
        ]
        report = ValidationReport(violations, 10, 3)
        by_col = report.violations_by_column()
        assert len(by_col["email"]) == 2
        assert len(by_col["name"]) == 1

    @pytest.mark.parametrize(
        "violations, keyword",
        [
            ([], "valid"),
            ([Violation(0, "email", "email", "x", "pattern mismatch")], "violation"),
        ],
        ids=["valid_summary", "invalid_summary"],
    )
    def test_summary(self, violations: list[Violation], keyword: str) -> None:
        report = ValidationReport(violations, 5, 2)
        assert keyword in report.summary().lower()


# ── Parametrized record validation ──────────────────────────────────────

_VALID_RECORDS = [
    # (records, field_map, null_fields, expected_valid)
    (
        [{"email": "alice@example.com", "name": "Alice"}],
        {"email": "email", "name": "full_name"},
        None,
        True,
    ),
    (
        [{"email": "bob@test.org", "name": "Bob"}],
        {"email": "email", "name": "full_name"},
        None,
        True,
    ),
    ([{"ip": "192.168.1.1"}], {"ip": "ipv4"}, None, True),
    (
        [{"id": "550e8400-e29b-41d4-a716-446655440000"}],
        {"id": "uuid4"},
        None,
        True,
    ),
    ([], {"email": "email"}, None, True),  # empty records
]

_INVALID_RECORDS = [
    # (records, field_map, null_fields, expected_valid)
    (
        [{"email": "not-an-email", "name": "Alice"}],
        {"email": "email", "name": "full_name"},
        None,
        False,
    ),
    (
        [{"email": "alice@test.com", "name": ""}],
        {"email": "email", "name": "full_name"},
        None,
        False,
    ),
    ([{"ip": "not-an-ip"}], {"ip": "ipv4"}, None, False),
    ([{"name": "Alice"}], {"email": "email", "name": "full_name"}, None, False),
]


class TestValidateRecords:
    @pytest.mark.parametrize(
        "records, field_map, null_fields, expected_valid",
        _VALID_RECORDS,
        ids=[f"valid_{i}" for i in range(len(_VALID_RECORDS))],
    )
    def test_valid_records(
        self,
        records: list[dict],
        field_map: dict,
        null_fields: dict | None,
        expected_valid: bool,
    ) -> None:
        kwargs = {} if null_fields is None else {"null_fields": null_fields}
        report = validate_records(records, field_map, **kwargs)
        assert report.is_valid is expected_valid

    @pytest.mark.parametrize(
        "records, field_map, null_fields, expected_valid",
        _INVALID_RECORDS,
        ids=[f"invalid_{i}" for i in range(len(_INVALID_RECORDS))],
    )
    def test_invalid_records(
        self,
        records: list[dict],
        field_map: dict,
        null_fields: dict | None,
        expected_valid: bool,
    ) -> None:
        kwargs = {} if null_fields is None else {"null_fields": null_fields}
        report = validate_records(records, field_map, **kwargs)
        assert report.is_valid is expected_valid

    def test_null_allowed_for_nullable(self) -> None:
        records = [{"email": "", "name": "Alice"}]
        field_map = {"email": "email", "name": "full_name"}
        null_fields = {"email": 0.5}
        report = validate_records(records, field_map, null_fields=null_fields)
        email_violations = [v for v in report.violations if v.column == "email"]
        assert len(email_violations) == 0


class TestValidateCsv:
    @pytest.mark.parametrize(
        "csv_content, field_map, expected_valid",
        [
            (
                "email,name\nalice@example.com,Alice\nbob@test.org,Bob\n",
                {"email": "email", "name": "full_name"},
                True,
            ),
            (
                "email,name\nnot-email,Alice\n",
                {"email": "email", "name": "full_name"},
                False,
            ),
        ],
        ids=["valid_csv", "invalid_csv"],
    )
    def test_validate_csv(
        self, csv_content: str, field_map: dict, expected_valid: bool
    ) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, newline=""
        ) as f:
            f.write(csv_content)
            path = f.name
        try:
            report = validate_csv(path, field_map)
            assert report.is_valid is expected_valid
        finally:
            os.unlink(path)


class TestSchemaValidateMethod:
    @pytest.mark.parametrize(
        "fields, data_override, expected_valid",
        [
            (["first_name", "email"], None, True),
            (["email"], [{"email": "not-an-email"}], False),
        ],
        ids=["valid_schema", "invalid_schema"],
    )
    def test_schema_validate(
        self,
        fields: list[str],
        data_override: list[dict] | None,
        expected_valid: bool,
    ) -> None:
        forge = DataForge(seed=42)
        schema = forge.schema(fields)
        data = data_override if data_override else schema.generate(10)
        report = schema.validate(data)
        assert report.is_valid is expected_valid

    def test_schema_validate_csv(self) -> None:
        forge = DataForge(seed=42)
        schema = forge.schema(["first_name", "email"])
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, newline=""
        ) as f:
            f.write("first_name,email\nAlice,alice@test.com\n")
            path = f.name
        try:
            report = schema.validate(path)
            assert report.is_valid
        finally:
            os.unlink(path)
