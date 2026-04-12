"""Type-Driven Schema Generation — Dataclasses and TypedDicts.

Real-world scenario: Your codebase already defines data models using Python
dataclasses or TypedDicts. Instead of manually mapping field names to
DataForge providers, you want to automatically generate matching test data
from your type definitions.

This example demonstrates:
- schema_from_dataclass(): auto-mapping dataclass fields to DataForge fields
- schema_from_typed_dict(): auto-mapping TypedDict keys to DataForge fields
- The 3-tier resolution order (exact match → alias → type fallback)
- Handling of unmapped fields (warnings)
- Generating test data from your existing models
"""

import warnings
from dataclasses import dataclass
from typing import TypedDict

from dataforge import DataForge

forge = DataForge(seed=42)

# --- Example 1: Basic dataclass -------------------------------------------

print("=== Basic Dataclass Schema ===\n")


@dataclass
class User:
    first_name: str
    last_name: str
    email: str
    city: str
    phone_number: str


schema = forge.schema_from_dataclass(User)
rows = schema.generate(count=5)

print("Users from @dataclass:")
for row in rows:
    print(
        f"  {row['first_name']:12s} {row['last_name']:12s} "
        f"{row['email']:28s} {row['city']:15s} {row['phone_number']}"
    )
print()

# --- Example 2: Dataclass with alias resolution ---------------------------

print("=== Alias Resolution (Tier 2) ===\n")


@dataclass
class Employee:
    """Uses field names that map via _FIELD_ALIASES (Tier 2 resolution)."""

    fname: str  # alias → first_name
    lname: str  # alias → last_name
    mail: str  # alias → email
    company: str  # alias → company_name
    occupation: str  # alias → job_title
    dob: str  # alias → date_of_birth


schema = forge.schema_from_dataclass(Employee)
rows = schema.generate(count=3)

print("Employees (alias-resolved fields):")
for row in rows:
    print(
        f"  {row['fname']:12s} {row['lname']:12s} {row['mail']:28s} "
        f"{row['company']:20s} {row['occupation']}"
    )
print()

# --- Example 3: Type-based fallback (Tier 3) ------------------------------

print("=== Type-Based Fallback (Tier 3) ===\n")


@dataclass
class Event:
    """Uses type annotations for Tier 3 resolution."""

    email: str  # Tier 1: exact match
    username: str  # Tier 2: alias
    active: bool  # Tier 3: bool → boolean


schema = forge.schema_from_dataclass(Event)
rows = schema.generate(count=3)

print("Events (with type fallback for 'active'):")
for row in rows:
    print(
        f"  email={row['email']:28s} user={row['username']:12s} active={row['active']}"
    )
print()

# --- Example 4: Handling unmapped fields ----------------------------------

print("=== Handling Unmapped Fields (Warnings) ===\n")


@dataclass
class ProductReview:
    """Some fields won't map — they'll produce warnings."""

    email: str
    city: str
    # These will be skipped with a warning:
    rating: int
    custom_metadata: str


# Capture warnings to display them
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    schema = forge.schema_from_dataclass(ProductReview)

print("Warnings for unmapped fields:")
for w in caught:
    print(f"  ⚠ {w.message}")
print()

rows = schema.generate(count=3)
print("Generated records (only mapped fields):")
for row in rows:
    print(f"  email={row['email']:28s} city={row['city']}")
print()

# --- Example 5: TypedDict basic usage ------------------------------------

print("=== TypedDict Schema ===\n")


class CustomerDict(TypedDict):
    first_name: str
    last_name: str
    email: str
    city: str
    country: str


schema = forge.schema_from_typed_dict(CustomerDict)
rows = schema.generate(count=5)

print("Customers from TypedDict:")
for row in rows:
    print(
        f"  {row['first_name']:12s} {row['last_name']:12s} "
        f"{row['email']:28s} {row['city']:15s} {row['country']}"
    )
print()

# --- Example 6: TypedDict with aliases ------------------------------------

print("=== TypedDict with Aliases ===\n")


class ContactDict(TypedDict):
    name: str  # alias → full_name
    mail: str  # alias → email
    phone: str  # alias → phone_number
    address: str  # alias → full_address


schema = forge.schema_from_typed_dict(ContactDict)
rows = schema.generate(count=3)

print("Contacts from TypedDict (alias-resolved):")
for row in rows:
    print(
        f"  {row['name']:22s} {row['mail']:28s} "
        f"{row['phone']:18s} {row['address'][:30]}"
    )
print()

# --- Example 7: Resolution order demonstration ---------------------------

print("=== 3-Tier Resolution Order ===\n")

print("DataForge resolves dataclass/TypedDict fields in order:\n")
print("  Tier 1 — Exact match:   'first_name' → provider.first_name()")
print("  Tier 2 — Alias lookup:  'fname' → _FIELD_ALIASES → first_name")
print("  Tier 3 — Type fallback: bool → boolean, datetime → datetime")
print("  (skip)  — Unresolved:   warning emitted, field omitted\n")


# Show the mapping for each field of a dataclass
@dataclass
class DemoModel:
    email: str  # Tier 1: exact match in registry
    company: str  # Tier 2: alias → company_name
    active: bool  # Tier 3: type → boolean


with warnings.catch_warnings(record=True):
    warnings.simplefilter("always")
    schema = forge.schema_from_dataclass(DemoModel)

rows = schema.generate(count=3)
print("Demo records:")
for row in rows:
    print(
        f"  email={row['email']:28s} company={row['company']:20s} active={row['active']}"
    )
print()

# --- Example 8: Using generated data for testing -------------------------

print("=== Using Generated Data for Testing ===\n")


@dataclass
class Account:
    username: str
    email: str
    first_name: str
    last_name: str
    date_of_birth: str
    ssn: str


schema = forge.schema_from_dataclass(Account)
rows = schema.generate(count=5)

print("Test accounts:")
for row in rows:
    print(
        f"  @{row['username']:12s} {row['first_name']:10s} {row['last_name']:10s} "
        f"DOB={row['date_of_birth']}  SSN={row['ssn']}"
    )
print()

print("These can be used directly in unit tests, fixtures, or seed scripts.")
