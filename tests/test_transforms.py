"""Tests for Feature 4: Field Transform Pipeline."""

import base64

import pytest

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


# ── Parametrized case / string transforms ───────────────────────────────

_UPPER_LOWER_CASES = [
    (upper, "hello", "HELLO"),
    (upper, 123, "123"),
    (lower, "HELLO", "hello"),
    (lower, 123, "123"),
]

_CASE_TRANSFORMS = [
    (snake_case, "Hello World", "hello_world"),
    (snake_case, "helloWorld", "hello_world"),
    (snake_case, "HelloWorld", "hello_world"),
    (camel_case, "hello world", "helloWorld"),
    (camel_case, "hello_world", "helloWorld"),
    (kebab_case, "Hello World", "hello-world"),
    (title_case, "hello world", "Hello World"),
]

_STRING_TRANSFORMS = [
    ("prefix", prefix("Mr. "), "Smith", "Mr. Smith"),
    ("suffix", suffix(" Jr."), "Smith", "Smith Jr."),
    ("wrap", wrap("[", "]"), "hello", "[hello]"),
    ("replace", replace("old", "new"), "old value old", "new value new"),
    ("strip", strip, "  hello  ", "hello"),
]


class TestUpperLower:
    @pytest.mark.parametrize(
        "fn, inp, expected",
        _UPPER_LOWER_CASES,
        ids=["upper_str", "upper_int", "lower_str", "lower_int"],
    )
    def test_upper_lower(self, fn: object, inp: object, expected: str) -> None:
        assert fn(inp) == expected  # type: ignore[operator]


class TestCaseTransforms:
    @pytest.mark.parametrize(
        "fn, inp, expected",
        _CASE_TRANSFORMS,
        ids=[
            "snake_spaces",
            "snake_camel",
            "snake_pascal",
            "camel_spaces",
            "camel_snake",
            "kebab",
            "title",
        ],
    )
    def test_case_transform(self, fn: object, inp: str, expected: str) -> None:
        assert fn(inp) == expected  # type: ignore[operator]


class TestTruncate:
    @pytest.mark.parametrize(
        "max_len, sfx, inp, check_endswith, check_maxlen",
        [
            (50, "...", "hello", None, None),  # short string, no truncation
            (10, "...", "this is a long string", "...", 10),
            (10, "~", "this is a long string", "~", 10),
        ],
        ids=["no_truncation", "default_suffix", "custom_suffix"],
    )
    def test_truncate(
        self,
        max_len: int,
        sfx: str,
        inp: str,
        check_endswith: str | None,
        check_maxlen: int | None,
    ) -> None:
        fn = truncate(max_len) if sfx == "..." else truncate(max_len, suffix=sfx)
        result = fn(inp)
        if check_endswith:
            assert result.endswith(check_endswith)
        if check_maxlen:
            assert len(result) <= check_maxlen
        if check_endswith is None:
            assert result == inp  # no truncation


class TestMaybeNull:
    @pytest.mark.parametrize(
        "probability, expect_all_value, expect_all_none",
        [
            (0.0, True, False),
            (1.0, False, True),
        ],
        ids=["zero", "full"],
    )
    def test_maybe_null_deterministic(
        self, probability: float, expect_all_value: bool, expect_all_none: bool
    ) -> None:
        fn = maybe_null(probability)
        results = [fn("value") for _ in range(100)]
        if expect_all_value:
            assert all(r == "value" for r in results)
        if expect_all_none:
            assert all(r is None for r in results)

    def test_maybe_null_partial(self) -> None:
        fn = maybe_null(0.5)
        results = [fn("value") for _ in range(200)]
        null_count = results.count(None)
        assert 30 < null_count < 170


# ── Parametrized hash / redact / b64 ───────────────────────────────────

_HASH_CASES = [
    ("sha256", 64),
    ("md5", 32),
]


class TestHash:
    @pytest.mark.parametrize(
        "algo, expected_len", _HASH_CASES, ids=[c[0] for c in _HASH_CASES]
    )
    def test_hash(self, algo: str, expected_len: int) -> None:
        fn = hash_with(algo)
        result = fn("hello")
        assert isinstance(result, str)
        assert len(result) == expected_len

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
        assert decode_b64(encoded) == "hello"

    def test_roundtrip(self) -> None:
        original = "test string 123"
        assert decode_b64(encode_b64(original)) == original


_REDACT_CASES = [
    # (kwargs, input, expected)
    ({}, "hello", "*****"),
    ({"keep_start": 2}, "hello", "he***"),
    ({"keep_end": 2}, "hello", "***lo"),
    ({"keep_start": 1, "keep_end": 1}, "hello", "h***o"),
    ({"char": "X"}, "hello", "XXXXX"),
]


class TestRedact:
    @pytest.mark.parametrize(
        "kwargs, inp, expected",
        _REDACT_CASES,
        ids=["full", "keep_start", "keep_end", "keep_both", "custom_char"],
    )
    def test_redact(self, kwargs: dict, inp: str, expected: str) -> None:
        fn = redact(**kwargs)
        assert fn(inp) == expected


class TestApplyIf:
    @pytest.mark.parametrize(
        "predicate, inp, expected",
        [
            (lambda x: len(str(x)) > 3, "hello", "HELLO"),
            (lambda x: len(str(x)) > 10, "hello", "hello"),
        ],
        ids=["apply", "skip"],
    )
    def test_apply_if(self, predicate: object, inp: str, expected: str) -> None:
        fn = apply_if(predicate, upper)  # type: ignore[arg-type]
        assert fn(inp) == expected


class TestStringTransforms:
    @pytest.mark.parametrize(
        "name, fn, inp, expected",
        _STRING_TRANSFORMS,
        ids=[c[0] for c in _STRING_TRANSFORMS],
    )
    def test_string_transform(
        self, name: str, fn: object, inp: str, expected: str
    ) -> None:
        result = fn(inp) if callable(fn) else fn  # type: ignore[operator]
        assert result == expected
