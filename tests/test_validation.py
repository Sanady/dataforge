"""Tests for Feature 6: Data Contract Validation."""

import os
import tempfile

from dataforge import DataForge
from dataforge.validation import (
    ValidationReport,
    Violation,
    validate_csv,
    validate_records,
)


class TestViolation:
    def test_violation_repr(self) -> None:
        v = Violation(0, "email", "email", "bad", "invalid format")
        r = repr(v)
        assert "row=0" in r
        assert "email" in r
        assert "invalid format" in r

    def test_violation_slots(self) -> None:
        v = Violation(1, "name", "full_name", "Alice", "too short")
        assert v.row == 1
        assert v.column == "name"
        assert v.field == "full_name"
        assert v.value == "Alice"
        assert v.reason == "too short"


class TestValidationReport:
    def test_valid_report(self) -> None:
        report = ValidationReport([], 10, 3)
        assert report.is_valid
        assert report.violation_count == 0

    def test_invalid_report(self) -> None:
        v = Violation(0, "email", "email", "bad", "invalid")
        report = ValidationReport([v], 10, 3)
        assert not report.is_valid
        assert report.violation_count == 1

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

    def test_summary_valid(self) -> None:
        report = ValidationReport([], 5, 2)
        summary = report.summary()
        assert "valid" in summary.lower()

    def test_summary_invalid(self) -> None:
        v = Violation(0, "email", "email", "not-an-email", "pattern mismatch")
        report = ValidationReport([v], 5, 2)
        summary = report.summary()
        assert "violation" in summary.lower()

    def test_repr(self) -> None:
        report = ValidationReport([], 5, 2)
        assert "VALID" in repr(report)
        v = Violation(0, "x", "x", "y", "z")
        report2 = ValidationReport([v], 5, 2)
        assert "INVALID" in repr(report2)


class TestValidateRecords:
    def test_valid_data(self) -> None:
        records = [
            {"email": "alice@example.com", "name": "Alice"},
            {"email": "bob@test.org", "name": "Bob"},
        ]
        field_map = {"email": "email", "name": "full_name"}
        report = validate_records(records, field_map)
        assert report.is_valid

    def test_invalid_email(self) -> None:
        records = [
            {"email": "not-an-email", "name": "Alice"},
        ]
        field_map = {"email": "email", "name": "full_name"}
        report = validate_records(records, field_map)
        assert not report.is_valid
        assert report.violation_count >= 1

    def test_empty_non_nullable_field(self) -> None:
        records = [
            {"email": "alice@test.com", "name": ""},
        ]
        field_map = {"email": "email", "name": "full_name"}
        report = validate_records(records, field_map)
        assert not report.is_valid
        # full_name is in _NON_EMPTY_FIELDS

    def test_null_allowed_for_nullable(self) -> None:
        records = [
            {"email": "", "name": "Alice"},
        ]
        field_map = {"email": "email", "name": "full_name"}
        null_fields = {"email": 0.5}
        report = validate_records(records, field_map, null_fields=null_fields)
        # email is nullable, so empty email should not be a violation
        email_violations = [v for v in report.violations if v.column == "email"]
        assert len(email_violations) == 0

    def test_missing_column(self) -> None:
        records = [{"name": "Alice"}]  # missing 'email'
        field_map = {"email": "email", "name": "full_name"}
        report = validate_records(records, field_map)
        assert not report.is_valid
        missing = [v for v in report.violations if v.reason == "missing column"]
        assert len(missing) == 1

    def test_empty_records(self) -> None:
        report = validate_records([], {"email": "email"})
        assert report.is_valid
        assert report.total_rows == 0

    def test_valid_ipv4(self) -> None:
        records = [{"ip": "192.168.1.1"}]
        field_map = {"ip": "ipv4"}
        report = validate_records(records, field_map)
        assert report.is_valid

    def test_invalid_ipv4(self) -> None:
        records = [{"ip": "not-an-ip"}]
        field_map = {"ip": "ipv4"}
        report = validate_records(records, field_map)
        assert not report.is_valid

    def test_valid_uuid(self) -> None:
        records = [{"id": "550e8400-e29b-41d4-a716-446655440000"}]
        field_map = {"id": "uuid4"}
        report = validate_records(records, field_map)
        assert report.is_valid


class TestValidateCsv:
    def test_validate_csv_file(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, newline=""
        ) as f:
            f.write("email,name\n")
            f.write("alice@example.com,Alice\n")
            f.write("bob@test.org,Bob\n")
            path = f.name

        try:
            field_map = {"email": "email", "name": "full_name"}
            report = validate_csv(path, field_map)
            assert report.is_valid
            assert report.total_rows == 2
        finally:
            os.unlink(path)

    def test_validate_csv_with_errors(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, newline=""
        ) as f:
            f.write("email,name\n")
            f.write("not-email,Alice\n")
            path = f.name

        try:
            field_map = {"email": "email", "name": "full_name"}
            report = validate_csv(path, field_map)
            assert not report.is_valid
        finally:
            os.unlink(path)


class TestSchemaValidateMethod:
    def test_schema_validate_valid(self) -> None:
        forge = DataForge(seed=42)
        schema = forge.schema(["first_name", "email"])
        data = schema.generate(10)
        report = schema.validate(data)
        assert report.is_valid

    def test_schema_validate_invalid(self) -> None:
        forge = DataForge(seed=42)
        schema = forge.schema(["email"])
        data = [{"email": "not-an-email"}]
        report = schema.validate(data)
        assert not report.is_valid

    def test_schema_validate_csv(self) -> None:
        forge = DataForge(seed=42)
        schema = forge.schema(["first_name", "email"])

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, newline=""
        ) as f:
            f.write("first_name,email\n")
            f.write("Alice,alice@test.com\n")
            path = f.name

        try:
            report = schema.validate(path)
            assert report.is_valid
        finally:
            os.unlink(path)
