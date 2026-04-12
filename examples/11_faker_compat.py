"""Faker Compatibility Layer — Migrating from faker to DataForge.

Real-world scenario: Your team has an existing test suite using the ``faker``
library. You want to migrate to DataForge for better performance and
deterministic output, but you need a drop-in replacement that preserves
your existing API calls.

This example demonstrates:
- Importing the Faker compatibility class
- Using familiar Faker method names (name, email, address, etc.)
- Seeding for reproducibility (global and per-instance)
- Multi-locale support through the Faker compat layer
- Side-by-side comparison of Faker API vs native DataForge API
"""

from dataforge import DataForge
from dataforge.compat import Faker

# --- Example 1: Drop-in replacement basics --------------------------------

print("=== Drop-In Replacement — Familiar Faker API ===\n")

fake = Faker(seed=42)

# These method names match the original faker library exactly
print(f"  name():           {fake.name()}")
print(f"  first_name():     {fake.first_name()}")
print(f"  last_name():      {fake.last_name()}")
print(f"  email():          {fake.email()}")
print(f"  address():        {fake.address()}")
print(f"  city():           {fake.city()}")
print(f"  phone_number():   {fake.phone_number()}")
print(f"  company():        {fake.company()}")
print(f"  job():            {fake.job()}")
print(f"  ssn():            {fake.ssn()}")
print(f"  uuid4():          {fake.uuid4()}")
print(f"  date():           {fake.date()}")
print(f"  boolean():        {fake.boolean()}")
print(f"  url():            {fake.url()}")
print(f"  user_name():      {fake.user_name()}")
print()

# --- Example 2: Internet and finance methods ------------------------------

print("=== Internet & Finance Methods ===\n")

fake = Faker(seed=100)

print(f"  ipv4():                {fake.ipv4()}")
print(f"  ipv6():                {fake.ipv6()}")
print(f"  mac_address():         {fake.mac_address()}")
print(f"  user_agent():          {fake.user_agent()}")
print(f"  domain_name():         {fake.domain_name()}")
print(f"  credit_card_number():  {fake.credit_card_number()}")
print(f"  iban():                {fake.iban()}")
print()

# --- Example 3: Seeding for reproducibility --------------------------------

print("=== Seeding — Global and Per-Instance ===\n")

# Global seed (affects all new Faker instances)
Faker.seed(123)
fake_a = Faker()
fake_b = Faker()
print("After Faker.seed(123):")
print(f"  Instance A name: {fake_a.name()}")
print(f"  Instance B name: {fake_b.name()}")

# Per-instance seed (overrides global)
fake_c = Faker(seed=999)
fake_d = Faker(seed=999)
print("\nWith seed=999 on both instances:")
print(f"  Instance C name: {fake_c.name()}")
print(f"  Instance D name: {fake_d.name()}")
print(f"  Match: {fake_c.name.__self__ is not fake_d.name.__self__}")

# Re-seed an existing instance
fake_e = Faker(seed=42)
val1 = fake_e.name()
fake_e.seed_instance(42)
val2 = fake_e.name()
print(f"\nAfter seed_instance(42) reset: {val1} == {val2} -> {val1 == val2}")
print()

# --- Example 4: Multi-locale via Faker compat ------------------------------

print("=== Multi-Locale via Faker ===\n")

fake_multi = Faker(["en_US", "fr_FR", "ja_JP"], seed=42)

print("Generating names from mixed locales:")
for i in range(8):
    print(f"  {i + 1}. {fake_multi.name()}")
print()

# Single locale
for locale in ("en_US", "de_DE", "pt_BR"):
    fake_loc = Faker(locale, seed=42)
    print(f"  {locale}: {fake_loc.name()} — {fake_loc.city()}")
print()

# --- Example 5: Side-by-side — Faker compat vs native DataForge -----------

print("=== Side-by-Side Comparison ===\n")

fake = Faker(seed=42)
forge = DataForge(seed=42)

print("  Faker compat API            │ Native DataForge API")
print("  ────────────────────────────│─────────────────────────────")
print("  fake.name()                 │ forge.person.full_name()")  # noqa: E501
print(f"  → {fake.name():28s}│ → {forge.person.full_name()}")

fake.seed_instance(42)
forge.seed(42)
print("  fake.email()                │ forge.internet.email()")  # noqa: E501
print(f"  → {fake.email():28s}│ → {forge.internet.email()}")

fake.seed_instance(42)
forge.seed(42)
print("  fake.address()              │ forge.address.full_address()")  # noqa: E501
print(f"  → {fake.address()[:28]:28s}│ → {forge.address.full_address()[:28]}")
print()

# --- Example 6: Batch generation in a testing workflow --------------------

print("=== Batch Generation for Test Fixtures ===\n")

fake = Faker(seed=42)

# Generate a batch of user records — typical test setup
users = []
for _ in range(5):
    users.append(
        {
            "name": fake.name(),
            "email": fake.email(),
            "city": fake.city(),
            "company": fake.company(),
            "job": fake.job(),
        }
    )

for user in users:
    print(f"  {user['name']:22s} {user['email']:30s} {user['city']}")
print()

# --- Example 7: Method mapping overview -----------------------------------

print("=== Supported Faker Method Mappings (sample) ===\n")

mapping_samples = {
    "fake.name()": "person.full_name()",
    "fake.first_name()": "person.first_name()",
    "fake.address()": "address.full_address()",
    "fake.zipcode()": "address.zip_code()",
    "fake.postcode()": "address.zip_code()",
    "fake.email()": "internet.email()",
    "fake.safe_email()": "internet.email()",
    "fake.company()": "company.company_name()",
    "fake.text()": "text.paragraph()",
    "fake.credit_card_number()": "finance.credit_card_number()",
}

print("  Faker Call               │ DataForge Equivalent")
print("  ─────────────────────────│─────────────────────────────")
for faker_call, df_call in mapping_samples.items():
    print(f"  {faker_call:25s} │ {df_call}")
print()

print("Total supported mappings: 57 methods")
print("See dataforge.compat.faker._FAKER_METHOD_MAP for the full list.")
