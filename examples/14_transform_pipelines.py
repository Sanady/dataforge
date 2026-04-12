"""Transform Pipelines with pipe() — Post-Generation Data Transformation.

Real-world scenario: You need generated data to match specific formats
required by your application — uppercase names for legacy systems, slugified
titles for URLs, hashed emails for privacy, or truncated descriptions for
database column limits.

This example demonstrates:
- Basic pipe() usage with single transforms
- Chaining multiple transforms in sequence
- All 18 built-in transform functions
- Creating custom transform functions
- Real-world patterns: slug generation, PII masking, data normalization
"""

from dataforge import DataForge
from dataforge.transforms import (
    apply_if,
    camel_case,
    encode_b64,
    hash_with,
    kebab_case,
    lower,
    maybe_null,
    pipe,
    prefix,
    redact,
    replace,
    snake_case,
    strip,
    suffix,
    title_case,
    truncate,
    upper,
    wrap,
)

forge = DataForge(seed=42)

# --- Example 1: Basic transforms -----------------------------------------

print("=== Basic Transforms ===\n")

# Uppercase names
schema = forge.schema({"name": pipe("full_name", upper)})
rows = schema.generate(count=3)
print("Uppercase names:")
for row in rows:
    print(f"  {row['name']}")
print()

# Lowercase emails (already lowercase, but demonstrates the transform)
schema = forge.schema({"email": pipe("email", lower)})
rows = schema.generate(count=3)
print("Lowercase emails:")
for row in rows:
    print(f"  {row['email']}")
print()

# Title case
schema = forge.schema({"title": pipe("job_title", title_case)})
rows = schema.generate(count=3)
print("Title case job titles:")
for row in rows:
    print(f"  {row['title']}")
print()

# --- Example 2: Case conversion transforms --------------------------------

print("=== Case Conversion Transforms ===\n")

sample_text = "Hello World Example"
print(f"  Original:     '{sample_text}'")
print(f"  snake_case:   '{snake_case(sample_text)}'")
print(f"  camel_case:   '{camel_case(sample_text)}'")
print(f"  kebab_case:   '{kebab_case(sample_text)}'")
print(f"  title_case:   '{title_case(sample_text)}'")
print(f"  upper:        '{upper(sample_text)}'")
print(f"  lower:        '{lower(sample_text)}'")
print()

# Using in schemas
schema = forge.schema(
    {
        "snake": pipe("full_name", snake_case),
        "camel": pipe("full_name", camel_case),
        "kebab": pipe("full_name", kebab_case),
    }
)
rows = schema.generate(count=3)
print("Case conversions in schema:")
for row in rows:
    print(f"  snake={row['snake']:25s} camel={row['camel']:20s} kebab={row['kebab']}")
print()

# --- Example 3: Truncation -----------------------------------------------

print("=== Truncation ===\n")

# Truncate long text to fit database column limits
schema = forge.schema(
    {
        "short_bio": pipe("paragraph", truncate(50)),
        "tweet": pipe("sentence", truncate(140)),
        "snippet": pipe("paragraph", truncate(30, suffix="…")),
    }
)

rows = schema.generate(count=3)
print("Truncated text fields:")
for row in rows:
    print(f"  bio ({len(row['short_bio']):2d} chars): {row['short_bio']}")
    print(f"  tweet:   {row['tweet']}")
    print(f"  snippet: {row['snippet']}")
    print()

# --- Example 4: Hashing and encoding -------------------------------------

print("=== Hashing and Encoding ===\n")

# Hash emails for anonymization
schema = forge.schema(
    {
        "email_hash": pipe("email", hash_with("sha256")),
        "email_md5": pipe("email", hash_with("md5")),
        "name_b64": pipe("full_name", encode_b64),
    }
)

rows = schema.generate(count=3)
print("Hashed and encoded fields:")
for row in rows:
    print(f"  SHA-256: {row['email_hash'][:40]}...")
    print(f"  MD5:     {row['email_md5']}")
    print(f"  Base64:  {row['name_b64']}")
    print()

# --- Example 5: Redaction for PII masking ---------------------------------

print("=== PII Redaction ===\n")

# Redact keeping edges for display purposes
schema = forge.schema(
    {
        "email_redacted": pipe("email", redact("*", keep_start=2, keep_end=4)),
        "phone_redacted": pipe("phone_number", redact("X", keep_start=0, keep_end=4)),
        "ssn_redacted": pipe("ssn", redact("#", keep_start=0, keep_end=4)),
        "name_full_redact": pipe("full_name", redact()),
    }
)

rows = schema.generate(count=3)
print("Redacted PII fields:")
for row in rows:
    print(f"  Email: {row['email_redacted']}")
    print(f"  Phone: {row['phone_redacted']}")
    print(f"  SSN:   {row['ssn_redacted']}")
    print(f"  Name:  {row['name_full_redact']}")
    print()

# --- Example 6: Prefix, suffix, and wrap ---------------------------------

print("=== Prefix, Suffix, and Wrap ===\n")

schema = forge.schema(
    {
        "user_id": pipe("username", prefix("user_")),
        "tagged_email": pipe("email", suffix(" [verified]")),
        "quoted_name": pipe("full_name", wrap('"', '"')),
        "xml_city": pipe("city", wrap("<city>", "</city>")),
    }
)

rows = schema.generate(count=3)
print("Prefixed, suffixed, and wrapped fields:")
for row in rows:
    print(f"  ID:    {row['user_id']}")
    print(f"  Email: {row['tagged_email']}")
    print(f"  Name:  {row['quoted_name']}")
    print(f"  City:  {row['xml_city']}")
    print()

# --- Example 7: Replace and strip ----------------------------------------

print("=== Replace and Strip ===\n")

# Replace spaces with underscores
schema = forge.schema(
    {
        "slug": pipe("full_name", lower, replace(" ", "_")),
        "cleaned": pipe("full_name", strip),
    }
)

rows = schema.generate(count=3)
print("Replace and strip:")
for row in rows:
    print(f"  slug: {row['slug']}  |  cleaned: {row['cleaned']}")
print()

# --- Example 8: Conditional transforms with apply_if ---------------------

print("=== Conditional Transforms ===\n")

# Only uppercase names longer than 10 characters
schema = forge.schema(
    {
        "name": pipe("full_name", apply_if(lambda v: len(str(v)) > 10, upper)),
    }
)

rows = schema.generate(count=6)
print("Conditionally uppercased (>10 chars):")
for row in rows:
    print(f"  {row['name']}")
print()

# --- Example 9: maybe_null for sparse data --------------------------------

print("=== Nullable Fields with maybe_null ===\n")

schema = forge.schema(
    {
        "name": pipe("full_name"),
        "phone": pipe("phone_number", maybe_null(0.3)),
        "bio": pipe("sentence", maybe_null(0.5)),
    }
)

rows = schema.generate(count=10)
null_phones = sum(1 for r in rows if r["phone"] is None)
null_bios = sum(1 for r in rows if r["bio"] is None)
print(f"10 records: {null_phones} null phones, {null_bios} null bios")
for row in rows[:5]:
    phone = row["phone"] or "(null)"
    bio = (row["bio"] or "(null)")[:40]
    print(f"  {row['name']:22s} Phone: {phone:20s} Bio: {bio}")
print()

# --- Example 10: Chaining multiple transforms (real-world patterns) -------

print("=== Real-World Transform Chains ===\n")

# URL slug: full name → lowercase → replace spaces with hyphens
schema = forge.schema(
    {
        "url_slug": pipe("full_name", lower, replace(" ", "-")),
    }
)

rows = schema.generate(count=3)
print("URL slugs:")
for row in rows:
    print(f"  /users/{row['url_slug']}")
print()

# API key style: hash → truncate → uppercase
schema = forge.schema(
    {
        "api_key": pipe("uuid4", hash_with("sha256"), truncate(32, suffix=""), upper),
    }
)

rows = schema.generate(count=3)
print("API keys:")
for row in rows:
    print(f"  {row['api_key']}")
print()

# Masked email for display: redact middle, add prefix
schema = forge.schema(
    {
        "display_email": pipe("email", redact("*", keep_start=3, keep_end=4)),
    }
)

rows = schema.generate(count=3)
print("Display emails:")
for row in rows:
    print(f"  {row['display_email']}")
