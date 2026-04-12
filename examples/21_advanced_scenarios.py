"""Advanced Scenarios — Multi-Feature Workflows Combining DataForge Capabilities.

This example shows complete workflows that combine multiple DataForge
features into realistic end-to-end scenarios: schema inference with
validation, Faker migration with transforms, type-driven schemas with
XLSX export, and multi-locale data pipelines.
"""

import os
import tempfile
import warnings
from collections import Counter
from dataclasses import dataclass
from typing import TypedDict

from dataforge import DataForge
from dataforge.compat import Faker
from dataforge.inference import SchemaInferrer
from dataforge.transforms import (
    hash_with,
    kebab_case,
    lower,
    maybe_null,
    pipe,
    prefix,
    redact,
    replace,
    truncate,
    upper,
)
from dataforge.validation import validate_records

forge = DataForge(seed=42)

# ---------------------------------------------------------------------------
# Scenario 1: Infer → Validate → Transform Pipeline
# ---------------------------------------------------------------------------
print("=" * 60)
print("SCENARIO 1: Infer → Validate → Transform Pipeline")
print("=" * 60)

# Step 1: Start with existing production-like data
print("\nStep 1: Simulating production data...")
source_data = []
for i in range(100):
    f = DataForge(seed=i)
    source_data.append(
        {
            "email": f.internet.email(),
            "full_name": f.person.full_name(),
            "city": f.address.city(),
        }
    )
print(f"  Source records: {len(source_data)}")
print(f"  Sample: {source_data[0]}")

# Step 2: Infer schema from the data
print("\nStep 2: Inferring schema...")
inferrer = SchemaInferrer(forge)
inferred_schema = inferrer.from_records(source_data)
print(f"  Inferred schema: {inferred_schema}")
print(f"  Analysis:\n{inferrer.describe()}")

# Step 3: Validate the original data against the inferred schema
print("Step 3: Validating source data...")
report = inferred_schema.validate(source_data)
print(f"  Valid: {report.is_valid}")
print(f"  Violations: {report.violation_count}")

# Step 4: Generate new data with transforms applied
print("\nStep 4: Generating transformed data...")
transformed_schema = forge.schema(
    {
        "email_hash": pipe("email", hash_with("sha256")),
        "name_upper": pipe("full_name", upper),
        "city": "address.city",
        "url_slug": pipe("full_name", lower, replace(" ", "-")),
    }
)

new_data = transformed_schema.generate(count=5)
print("  Transformed records:")
for row in new_data:
    print(
        f"    hash={row['email_hash'][:16]}... "
        f"name={row['name_upper']:22s} "
        f"slug={row['url_slug']}"
    )

# ---------------------------------------------------------------------------
# Scenario 2: Faker Migration with Validation
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("SCENARIO 2: Faker Migration with Validation")
print("=" * 60)

# Step 1: Generate data using Faker compat layer (migration path)
print("\nStep 1: Generating data with Faker compat layer...")
fake = Faker(seed=42)

faker_records = []
for _ in range(50):
    faker_records.append(
        {
            "name": fake.name(),
            "email": fake.email(),
            "phone": fake.phone_number(),
            "ssn": fake.ssn(),
            "city": fake.city(),
        }
    )
print(f"  Generated {len(faker_records)} records via Faker compat")
print(f"  Sample: {faker_records[0]}")

# Step 2: Validate the Faker-generated data
print("\nStep 2: Validating Faker-generated data...")
field_map = {
    "name": "full_name",
    "email": "email",
    "phone": "phone_number",
    "ssn": "ssn",
    "city": "city",
}
report = validate_records(faker_records, field_map)
print(f"  Valid: {report.is_valid}")
print(f"  Violations: {report.violation_count}")

# Step 3: Compare with native DataForge
print("\nStep 3: Comparing with native DataForge schema...")
native_schema = forge.schema(
    {
        "name": "person.full_name",
        "email": "internet.email",
        "phone": "phone_number",
        "ssn": "government.ssn",
        "city": "address.city",
    }
)
native_records = native_schema.generate(count=50)
native_report = native_schema.validate(native_records)
print(f"  Native valid: {native_report.is_valid}")
print(f"  Both produce valid data: {report.is_valid and native_report.is_valid}")

# ---------------------------------------------------------------------------
# Scenario 3: Type-Driven Schema with Transforms
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("SCENARIO 3: Type-Driven Schema with Transforms")
print("=" * 60)


@dataclass
class CustomerProfile:
    first_name: str
    last_name: str
    email: str
    city: str
    country: str


# Step 1: Auto-generate schema from dataclass
print("\nStep 1: Creating schema from dataclass...")
with warnings.catch_warnings(record=True):
    warnings.simplefilter("always")
    base_schema = forge.schema_from_dataclass(CustomerProfile)

base_data = base_schema.generate(count=5)
print(f"  Schema columns: {list(base_data[0].keys())}")

# Step 2: Create an enhanced schema with transforms
print("\nStep 2: Adding transform pipeline...")
enhanced_schema = forge.schema(
    {
        "first_name": pipe("first_name", upper),
        "last_name": pipe("last_name", upper),
        "email": pipe("email", lower),
        "display_name": pipe("full_name", truncate(20)),
        "city": "address.city",
        "country": "address.country",
        "profile_slug": pipe("full_name", kebab_case),
    }
)

enhanced_data = enhanced_schema.generate(count=5)
print("  Enhanced records:")
for row in enhanced_data:
    print(
        f"    {row['first_name']:12s} {row['last_name']:12s} "
        f"slug=/{row['profile_slug']}  city={row['city']}"
    )

# Step 3: Export to CSV
print("\nStep 3: Exporting to CSV...")
csv_output = enhanced_schema.to_csv(count=100)
lines = csv_output.strip().split("\n")
print(f"  CSV lines: {len(lines)} (including header)")
print(f"  Header: {lines[0]}")

# ---------------------------------------------------------------------------
# Scenario 4: Multi-Locale + Custom Fields + Validation
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("SCENARIO 4: Multi-Locale + Custom Fields + Validation")
print("=" * 60)

# Step 1: Set up multi-locale forge with custom fields
print("\nStep 1: Setting up multi-locale forge with custom fields...")
global_forge = DataForge(locale=["en_US", "fr_FR", "de_DE", "ja_JP"], seed=42)

# Define domain-specific fields on a separate forge (custom fields
# don't propagate to multi-locale children)
single_forge = DataForge(seed=42)
single_forge.define(
    "membership",
    elements=["free", "basic", "premium", "enterprise"],
    weights=[0.40, 0.30, 0.20, 0.10],
)

# Step 2: Generate international customer data
print("\nStep 2: Generating international customer data...")
intl_schema = global_forge.schema(
    {
        "name": "person.full_name",
        "email": "internet.email",
        "city": "address.city",
        "country": "address.country",
    }
)
intl_records = intl_schema.generate(count=12)

# Add membership from the single forge
for rec in intl_records:
    rec["membership"] = single_forge.membership()

print(f"  Generated {len(intl_records)} international records")
for rec in intl_records[:6]:
    print(
        f"    {rec['name']:25s} {rec['city']:15s} "
        f"{rec['country']:12s} [{rec['membership']}]"
    )
print(f"    ... and {len(intl_records) - 6} more")

# Step 3: Validate the international data
print("\nStep 3: Validating international data...")
report = validate_records(
    intl_records,
    {
        "name": "full_name",
        "email": "email",
        "city": "city",
        "country": "country",
    },
)
print(f"  Valid: {report.is_valid}")
print(f"  Violations: {report.violation_count}")

# Step 4: Analyze membership distribution
print("\nStep 4: Membership distribution:")
memberships = Counter(r["membership"] for r in intl_records)
for tier, count in sorted(memberships.items(), key=lambda x: -x[1]):
    print(f"    {tier:12s} {count}")

# ---------------------------------------------------------------------------
# Scenario 5: Data Pipeline — Generate, Transform, Validate, Export
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("SCENARIO 5: Complete Data Pipeline")
print("=" * 60)

# Step 1: Define schema with transforms
print("\nStep 1: Building schema with transforms...")
pipeline_schema = forge.schema(
    {
        "id": "misc.uuid4",
        "name": pipe("full_name", upper),
        "email": pipe("email", lower),
        "email_masked": pipe("email", redact("*", keep_start=3, keep_end=4)),
        "phone": pipe("phone_number", maybe_null(0.1)),
        "city": "address.city",
        "tag": pipe("username", prefix("user-"), lower),
    }
)

# Step 2: Generate data
print("Step 2: Generating 200 records...")
pipeline_data = pipeline_schema.generate(count=200)
null_phones = sum(1 for r in pipeline_data if r["phone"] is None)
print(f"  Records: {len(pipeline_data)}")
print(f"  Null phones: {null_phones} (~10% expected)")

# Step 3: Export to CSV
print("\nStep 3: Exporting to CSV...")
csv_path = os.path.join(tempfile.gettempdir(), "dataforge_pipeline.csv")
pipeline_schema.to_csv(count=200, path=csv_path)
file_size = os.path.getsize(csv_path)
print(f"  CSV path: {csv_path}")
print(f"  File size: {file_size:,} bytes")

# Step 4: Show sample records
print("\nStep 4: Sample records:")
for row in pipeline_data[:3]:
    print(f"  ID:     {row['id'][:8]}...")
    print(f"  Name:   {row['name']}")
    print(f"  Email:  {row['email']}")
    print(f"  Masked: {row['email_masked']}")
    print(f"  Phone:  {row['phone'] or '(null)'}")
    print(f"  City:   {row['city']}")
    print(f"  Tag:    {row['tag']}")
    print()

# Clean up
os.unlink(csv_path)

# ---------------------------------------------------------------------------
# Scenario 6: TypedDict Schema with XLSX Export
# ---------------------------------------------------------------------------
print("=" * 60)
print("SCENARIO 6: TypedDict + XLSX Export")
print("=" * 60)


class InvoiceRecord(TypedDict):
    first_name: str
    last_name: str
    email: str
    company: str
    city: str
    country: str


print("\nStep 1: Creating schema from TypedDict...")
with warnings.catch_warnings(record=True):
    warnings.simplefilter("always")
    invoice_schema = forge.schema_from_typed_dict(InvoiceRecord)

records = invoice_schema.generate(count=5)
print(f"  Columns: {list(records[0].keys())}")
for rec in records:
    print(
        f"    {rec['first_name']:12s} {rec['last_name']:12s} "
        f"{rec['email']:28s} {rec['company']}"
    )

# XLSX export (if openpyxl available)
try:
    import openpyxl  # noqa: F401

    xlsx_path = os.path.join(tempfile.gettempdir(), "dataforge_invoices.xlsx")
    rows = invoice_schema.to_excel(path=xlsx_path, count=100, sheet_name="Invoices")
    print(f"\nStep 2: Exported {rows} rows to XLSX")
    print(f"  Path: {xlsx_path}")
    os.unlink(xlsx_path)
except ModuleNotFoundError:
    print("\nStep 2: XLSX export skipped (openpyxl not installed)")

print()
print("All 6 advanced scenarios completed successfully.")
