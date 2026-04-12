"""Tests for Feature 4: Field Transform Pipeline."""

import base64

from dataforge import DataForge
from dataforge.transforms import (
    apply_if,
    camel_case,
    decode_b64,
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


class TestPipeFunction:
    def test_pipe_returns_dict(self) -> None:
        result = pipe("full_name", upper)
        assert isinstance(result, dict)
        assert result["field"] == "full_name"
        assert "_pipe_transforms" in result

    def test_pipe_stores_transforms(self) -> None:
        result = pipe("email", upper, lower)
        assert len(result["_pipe_transforms"]) == 2

    def test_pipe_in_schema(self) -> None:
        forge = DataForge(seed=42)
        schema = forge.schema({"name": pipe("full_name", upper)})
        rows = schema.generate(3)
        assert len(rows) == 3
        for row in rows:
            assert row["name"] == row["name"].upper()

    def test_pipe_multiple_transforms(self) -> None:
        forge = DataForge(seed=42)
        schema = forge.schema(
            {
                "name": pipe("full_name", upper, lambda s: s[:5]),
            }
        )
        rows = schema.generate(3)
        for row in rows:
            assert len(row["name"]) <= 5
            assert row["name"] == row["name"].upper()

    def test_pipe_with_plain_fields(self) -> None:
        """Pipe fields can coexist with plain string fields."""
        forge = DataForge(seed=42)
        schema = forge.schema(
            {
                "name": pipe("full_name", upper),
                "email": "email",
            }
        )
        rows = schema.generate(3)
        for row in rows:
            assert row["name"] == row["name"].upper()
            assert "@" in row["email"]


class TestUpperLower:
    def test_upper(self) -> None:
        assert upper("hello") == "HELLO"

    def test_upper_non_string(self) -> None:
        assert upper(123) == "123"

    def test_lower(self) -> None:
        assert lower("HELLO") == "hello"

    def test_lower_non_string(self) -> None:
        assert lower(123) == "123"


class TestCaseTransforms:
    def test_snake_case_from_spaces(self) -> None:
        assert snake_case("Hello World") == "hello_world"

    def test_snake_case_from_camel(self) -> None:
        assert snake_case("helloWorld") == "hello_world"

    def test_snake_case_from_pascal(self) -> None:
        assert snake_case("HelloWorld") == "hello_world"

    def test_camel_case(self) -> None:
        assert camel_case("hello world") == "helloWorld"

    def test_camel_case_from_snake(self) -> None:
        assert camel_case("hello_world") == "helloWorld"

    def test_kebab_case(self) -> None:
        assert kebab_case("Hello World") == "hello-world"

    def test_title_case(self) -> None:
        assert title_case("hello world") == "Hello World"


class TestTruncate:
    def test_truncate_short_string(self) -> None:
        fn = truncate(50)
        assert fn("hello") == "hello"

    def test_truncate_long_string(self) -> None:
        fn = truncate(10)
        result = fn("this is a long string")
        assert len(result) <= 10
        assert result.endswith("...")

    def test_truncate_custom_suffix(self) -> None:
        fn = truncate(10, suffix="~")
        result = fn("this is a long string")
        assert result.endswith("~")
        assert len(result) <= 10


class TestMaybeNull:
    def test_maybe_null_zero_probability(self) -> None:
        fn = maybe_null(0.0)
        for _ in range(100):
            assert fn("value") == "value"

    def test_maybe_null_full_probability(self) -> None:
        fn = maybe_null(1.0)
        for _ in range(100):
            assert fn("value") is None

    def test_maybe_null_partial(self) -> None:
        fn = maybe_null(0.5)
        results = [fn("value") for _ in range(200)]
        null_count = results.count(None)
        # With 0.5, expect roughly 100 nulls. Allow wide margin.
        assert 30 < null_count < 170


class TestHash:
    def test_hash_sha256(self) -> None:
        fn = hash_with("sha256")
        result = fn("hello")
        assert isinstance(result, str)
        assert len(result) == 64  # SHA-256 hex digest

    def test_hash_md5(self) -> None:
        fn = hash_with("md5")
        result = fn("hello")
        assert len(result) == 32  # MD5 hex digest

    def test_hash_deterministic(self) -> None:
        fn = hash_with("sha256")
        assert fn("hello") == fn("hello")


class TestBase64:
    def test_encode_b64(self) -> None:
        result = encode_b64("hello")
        expected = base64.b64encode(b"hello").decode()
        assert result == expected

    def test_decode_b64(self) -> None:
        encoded = base64.b64encode(b"hello").decode()
        result = decode_b64(encoded)
        assert result == "hello"

    def test_roundtrip(self) -> None:
        original = "test string 123"
        assert decode_b64(encode_b64(original)) == original


class TestRedact:
    def test_redact_full(self) -> None:
        fn = redact()
        result = fn("hello")
        assert result == "*****"

    def test_redact_keep_start(self) -> None:
        fn = redact(keep_start=2)
        result = fn("hello")
        assert result == "he***"

    def test_redact_keep_end(self) -> None:
        fn = redact(keep_end=2)
        result = fn("hello")
        assert result == "***lo"

    def test_redact_keep_both(self) -> None:
        fn = redact(keep_start=1, keep_end=1)
        result = fn("hello")
        assert result == "h***o"

    def test_redact_custom_char(self) -> None:
        fn = redact(char="X")
        result = fn("hello")
        assert result == "XXXXX"


class TestApplyIf:
    def test_apply_when_true(self) -> None:
        fn = apply_if(lambda x: len(str(x)) > 3, upper)
        assert fn("hello") == "HELLO"

    def test_skip_when_false(self) -> None:
        fn = apply_if(lambda x: len(str(x)) > 10, upper)
        assert fn("hello") == "hello"


class TestStringTransforms:
    def test_prefix(self) -> None:
        fn = prefix("Mr. ")
        assert fn("Smith") == "Mr. Smith"

    def test_suffix(self) -> None:
        fn = suffix(" Jr.")
        assert fn("Smith") == "Smith Jr."

    def test_wrap(self) -> None:
        fn = wrap("[", "]")
        assert fn("hello") == "[hello]"

    def test_replace(self) -> None:
        fn = replace("old", "new")
        assert fn("old value old") == "new value new"

    def test_strip(self) -> None:
        assert strip("  hello  ") == "hello"
