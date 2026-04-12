"""Data Contract Validation — Ensuring Data Quality.

Real-world scenario: You generate synthetic data for testing or seeding,
but you need to verify that the data conforms to expected patterns
(valid emails, proper UUIDs, non-null required fields). DataForge's
validation module lets you define and enforce data contracts.

This example demonstrates:
- validate_records(): validating dicts against a field mapping
- schema.validate(): validating data against a schema's contract
- validate_csv(): validating CSV files
- Understanding Violation objects and ValidationReport
- Handling null fields and semantic pattern checks
- Validating external (non-DataForge) data
"""

from dataforge import DataForge
from dataforge.validation import validate_records

forge = DataForge(seed=42)

# --- Example 1: Validating generated data (should pass) -------------------

print("=== Validating Generated Data ===\n")

schema = forge.schema(
    {
        "name": "person.full_name",
        "email": "internet.email",
        "phone": "phone_number",
        "ssn": "government.ssn",
    }
)

# Generate some data and validate it
data = schema.generate(count=20)
report = schema.validate(data)

print(f"  Records validated: {report.total_rows}")
print(f"  Columns checked:   {report.total_columns}")
print(f"  Is valid:          {report.is_valid}")
print(f"  Violations:        {report.violation_count}")
print()

# --- Example 2: Validating bad data (should fail) ------------------------

print("=== Validating Bad Data ===\n")

# Intentionally bad records
bad_data = [
    {
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "phone": "+1-555-0100",
        "ssn": "123-45-6789",
    },
    {
        "name": "",  # empty name — violation
        "email": "not-an-email",  # invalid format — violation
        "phone": "+1-555-0101",
        "ssn": "12345",  # wrong SSN format — violation
    },
    {
        "name": "Bob Smith",
        "email": "bob@test.com",
        "phone": "abc",  # too short for phone — violation
        "ssn": "987-65-4321",
    },
    {
        "name": "Charlie Brown",
        # missing "email" key — violation
        "phone": "+1-555-0102",
        "ssn": "111-22-3333",
    },
]

field_map = {
    "name": "full_name",
    "email": "email",
    "phone": "phone_number",
    "ssn": "ssn",
}

report = validate_records(bad_data, field_map)

print(f"  Records validated: {report.total_rows}")
print(f"  Is valid:          {report.is_valid}")
print(f"  Violations found:  {report.violation_count}")
print()

# Print the full summary
print(report.summary())
print()

# --- Example 3: Inspecting individual violations -------------------------

print("=== Inspecting Violations ===\n")

for v in report.violations:
    print(f"  Row {v.row}, Column '{v.column}': {v.reason}")
    print(f"    Value: {v.value!r}")
    print()

# --- Example 4: Violations grouped by column -----------------------------

print("=== Violations by Column ===\n")

by_col = report.violations_by_column()
for col, viols in sorted(by_col.items()):
    print(f"  {col}: {len(viols)} violation(s)")
    for v in viols:
        print(f"    Row {v.row}: {v.reason} (value={v.value!r})")
print()

# --- Example 5: Schema-based validation ----------------------------------

print("=== Schema-Based Validation ===\n")

# Create a schema and validate external data against it
schema = forge.schema(["email", "uuid4", "date", "ipv4"])

external_data = [
    {
        "email": "user@domain.com",
        "uuid4": "550e8400-e29b-41d4-a716-446655440000",
        "date": "2024-01-15",
        "ipv4": "192.168.1.1",
    },
    {
        "email": "bad-email",
        "uuid4": "not-a-uuid",
        "date": "January 15",
        "ipv4": "999.999.999.999",
    },
    {
        "email": "good@test.org",
        "uuid4": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
        "date": "2024-12-31",
        "ipv4": "10.0.0.1",
    },
]

report = schema.validate(external_data)
print(f"  Is valid: {report.is_valid}")
print(f"  Violations: {report.violation_count}")
print()
print(report.summary())
print()

# --- Example 6: Null field allowances ------------------------------------

print("=== Null Field Allowances ===\n")

# Some columns are allowed to be null
data_with_nulls = [
    {"name": "Alice", "email": "alice@test.com", "phone": None},
    {"name": "Bob", "email": "bob@test.com", "phone": "+1-555-0100"},
    {"name": "", "email": "charlie@test.com", "phone": None},
]

# Without null allowance — phone nulls will be fine (no non-empty check),
# but empty name will trigger violation
report_strict = validate_records(
    data_with_nulls,
    {"name": "full_name", "email": "email", "phone": "phone_number"},
)
print(f"  Strict validation: {report_strict.violation_count} violation(s)")

# With null allowance for phone
report_lenient = validate_records(
    data_with_nulls,
    {"name": "full_name", "email": "email", "phone": "phone_number"},
    null_fields={"phone": 0.5},
)
print(f"  Lenient validation: {report_lenient.violation_count} violation(s)")
print()

# --- Example 7: CSV validation -------------------------------------------

print("=== CSV Validation ===\n")

import os  # noqa: E402
import tempfile  # noqa: E402

csv_content = schema.to_csv(count=50)
csv_path = os.path.join(tempfile.gettempdir(), "dataforge_validation_test.csv")
with open(csv_path, "w", encoding="utf-8") as f:
    f.write(csv_content)

# Validate it using schema.validate(path)
report = schema.validate(csv_path)
print(f"  CSV file: {csv_path}")
print(f"  Rows validated: {report.total_rows}")
print(f"  Is valid: {report.is_valid}")
print(f"  Violations: {report.violation_count}")

# Clean up
os.unlink(csv_path)
print()

# --- Example 8: Validation report as a testing assertion ------------------

print("=== Using Validation in Tests ===\n")

schema = forge.schema(["first_name", "email", "city"])
data = schema.generate(count=100)
report = schema.validate(data)

# In a real test you would: assert report.is_valid, report.summary()
if report.is_valid:
    print("  PASS: All 100 generated records pass validation.")
else:
    print(f"  FAIL: {report.violation_count} violation(s) found.")
    print(report.summary())

print()
print("Typical test assertion:")
print("  report = schema.validate(data)")
print("  assert report.is_valid, report.summary()")
