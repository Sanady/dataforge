"""Hypothesis Strategy Bridge — Property-Based Testing with DataForge.

Real-world scenario: You use Hypothesis for property-based testing and want
to use DataForge's realistic data as test inputs. The hypothesis bridge
creates Hypothesis strategies from DataForge fields, allowing you to combine
realistic fake data with Hypothesis's shrinking and test-case generation.

This example demonstrates:
- strategy(): single-field Hypothesis strategies
- forge_strategy(): multi-field dict strategies
- Writing property-based tests with @given
- Combining DataForge strategies with other Hypothesis strategies

NOTE: This example requires the ``hypothesis`` package.
      Install with: pip install hypothesis
"""

try:
    import hypothesis  # noqa: F401
except ModuleNotFoundError:
    print("This example requires 'hypothesis'. Install with: pip install hypothesis")
    print("Skipping example.")
    raise SystemExit(0)

from hypothesis import given, settings

from hypothesis import find  # noqa: E402

from dataforge.compat.hypothesis import forge_strategy, strategy  # noqa: E402

# --- Example 1: Single-field strategies -----------------------------------

print("=== Single-Field Strategies ===\n")

# Create strategies from DataForge field names
email_st = strategy("email")
name_st = strategy("first_name")
city_st = strategy("city")

# Find an example that satisfies a trivial condition
example_email = find(email_st, lambda x: "@" in x)
example_name = find(name_st, lambda x: len(x) > 0)

print(f"  Example email: {example_email}")
print(f"  Example name:  {example_name}")
print()

# --- Example 2: Property-based test — email validation --------------------

print("=== Property: All Emails Contain '@' ===\n")


@given(email=strategy("email"))
@settings(max_examples=50)
def test_email_has_at_sign(email: str) -> None:
    assert "@" in str(email), f"Email missing '@': {email}"


test_email_has_at_sign()
print("  PASS: 50 generated emails all contain '@'")
print()

# --- Example 3: Property-based test — name is non-empty -------------------

print("=== Property: Names Are Non-Empty ===\n")


@given(name=strategy("full_name"))
@settings(max_examples=50)
def test_name_not_empty(name: str) -> None:
    assert len(str(name).strip()) > 0, "Name should not be empty"


test_name_not_empty()
print("  PASS: 50 generated names are all non-empty")
print()

# --- Example 4: Multi-field strategies (dict output) ----------------------

print("=== Multi-Field Strategy (Dict Output) ===\n")

# Using a list of field names
user_st = forge_strategy(["first_name", "email", "city"])

example_user = find(user_st, lambda d: "first_name" in d)
print(f"  Example user dict: {example_user}")
print()

# Using a column→field mapping
contact_st = forge_strategy(
    {
        "name": "full_name",
        "mail": "email",
        "phone": "phone_number",
    }
)

example_contact = find(contact_st, lambda d: "name" in d)
print(f"  Example contact dict: {example_contact}")
print()

# --- Example 5: Property test with multi-field strategy -------------------

print("=== Property: User Records Have Required Keys ===\n")


@given(data=forge_strategy(["first_name", "last_name", "email", "city"]))
@settings(max_examples=30)
def test_user_has_required_keys(data: dict) -> None:
    assert "first_name" in data
    assert "last_name" in data
    assert "email" in data
    assert "city" in data
    assert all(v is not None for v in data.values()), "No values should be None"


test_user_has_required_keys()
print("  PASS: 30 generated user records all have required keys")
print()

# --- Example 6: Locale-specific strategies --------------------------------

print("=== Locale-Specific Strategies ===\n")

jp_name_st = strategy("full_name", locale="ja_JP")
de_name_st = strategy("full_name", locale="de_DE")

jp_name = find(jp_name_st, lambda x: len(str(x)) > 0)
de_name = find(de_name_st, lambda x: len(str(x)) > 0)

print(f"  Japanese name: {jp_name}")
print(f"  German name:   {de_name}")
print()

# --- Example 7: Combining with standard Hypothesis strategies -------------

print("=== Combining with Standard Hypothesis Strategies ===\n")

from hypothesis import strategies as st  # noqa: E402


@given(
    name=strategy("full_name"),
    age=st.integers(min_value=18, max_value=99),
    score=st.floats(min_value=0.0, max_value=100.0, allow_nan=False),
)
@settings(max_examples=30)
def test_mixed_strategies(name: str, age: int, score: float) -> None:
    assert len(str(name)) > 0
    assert 18 <= age <= 99
    assert 0.0 <= score <= 100.0


test_mixed_strategies()
print("  PASS: 30 examples with mixed DataForge + Hypothesis strategies")
print()

print("Hypothesis + DataForge enables powerful property-based testing")
print("with realistic, locale-aware fake data.")
