"""Multi-Locale Data Generation — Internationalized Test Data.

Real-world scenario: You are building a global SaaS platform that supports
users from multiple countries. You need realistic test data in different
languages and cultural formats for names, addresses, phone numbers, and more.

This example demonstrates:
- Creating single-locale DataForge instances
- Multi-locale mode with automatic locale mixing
- Locale-specific data in schemas
- Inspecting available locales and providers
- Generating locale-blended datasets for internationalization testing
"""

from dataforge import DataForge

# --- Example 1: Single-locale instances ------------------------------------

print("=== Single-Locale Instances ===\n")

locales = {
    "en_US": "United States",
    "de_DE": "Germany",
    "fr_FR": "France",
    "ja_JP": "Japan",
    "pt_BR": "Brazil",
    "es_MX": "Mexico",
    "it_IT": "Italy",
    "ko_KR": "South Korea",
}

for code, country in locales.items():
    forge = DataForge(locale=code, seed=42)
    name = forge.person.full_name()
    city = forge.address.city()
    print(f"  {code} ({country:14s}): {name:25s} — {city}")
print()

# --- Example 2: Multi-locale mixing ---------------------------------------

print("=== Multi-Locale Mixing ===\n")

# Pass a list of locales — each call randomly selects a locale
forge = DataForge(locale=["en_US", "fr_FR", "ja_JP", "de_DE"], seed=42)

print("Random locale selection per call:")
for i in range(10):
    name = forge.person.full_name()
    city = forge.address.city()
    print(f"  {i + 1:2d}. {name:30s} — {city}")
print()

# --- Example 3: Multi-locale in schemas -----------------------------------

print("=== Multi-Locale Schema ===\n")

forge = DataForge(locale=["en_US", "fr_FR", "pt_BR"], seed=42)

schema = forge.schema(
    {
        "id": "misc.uuid4",
        "name": "person.full_name",
        "email": "internet.email",
        "city": "address.city",
        "country": "address.country",
    }
)

rows = schema.generate(count=8)
print("Internationalized customer records:")
for row in rows:
    uuid_short = row["id"][:8]
    print(
        f"  {uuid_short}... {row['name']:25s} "
        f"{row['email']:30s} {row['city']}, {row['country']}"
    )
print()

# --- Example 4: Deterministic multi-locale output -------------------------

print("=== Deterministic Output with Seeds ===\n")

# Same seed + same locales = same output every time
forge_a = DataForge(locale=["en_US", "de_DE"], seed=777)
forge_b = DataForge(locale=["en_US", "de_DE"], seed=777)

names_a = [forge_a.person.full_name() for _ in range(5)]
names_b = [forge_b.person.full_name() for _ in range(5)]

print("Run A:", names_a)
print("Run B:", names_b)
print(f"Identical: {names_a == names_b}")
print()

# --- Example 5: Locale-specific formatting ---------------------------------

print("=== Locale-Specific Formatting ===\n")

for code in ("en_US", "de_DE", "ja_JP"):
    forge = DataForge(locale=code, seed=42)
    print(f"  {code}:")
    print(f"    Name:    {forge.person.full_name()}")
    print(f"    Address: {forge.address.full_address()}")
    print(f"    Phone:   {forge.phone.phone_number()}")
    print()

# --- Example 6: Building a multi-region test dataset ----------------------

print("=== Multi-Region Test Dataset ===\n")

regions = {
    "North America": ["en_US"],
    "Europe": ["de_DE", "fr_FR", "it_IT"],
    "Asia": ["ja_JP", "ko_KR"],
    "South America": ["pt_BR", "es_MX"],
}

all_records = []
for region, region_locales in regions.items():
    forge = DataForge(locale=region_locales, seed=42)
    schema = forge.schema(["full_name", "email", "city", "country"])
    records = schema.generate(count=3)
    for rec in records:
        rec["region"] = region
    all_records.extend(records)

print(f"Generated {len(all_records)} records across {len(regions)} regions:\n")
for rec in all_records:
    print(
        f"  [{rec['region']:14s}] {rec['full_name']:25s} "
        f"{rec['email']:30s} {rec['city']}"
    )
print()

# --- Example 7: Inspecting locale configuration ---------------------------

print("=== Inspecting Locale Configuration ===\n")

forge = DataForge(locale=["en_US", "fr_FR", "ja_JP"], seed=42)

print(f"  Primary locale:  {forge.locale}")
print(f"  All locales:     {forge.locales}")
print(f"  Multi-locale:    {len(forge.locales) > 1}")
print()

# Single locale instance
forge_single = DataForge(locale="en_US", seed=42)
print(f"  Single locale:   {forge_single.locale}")
print(f"  All locales:     {forge_single.locales}")
