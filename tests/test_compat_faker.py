"""Tests for Feature 1: Faker Compatibility Layer."""

import pytest

from dataforge.compat import Faker
from dataforge.compat.faker import _FAKER_METHOD_MAP


class TestFakerInit:
    def test_default_locale(self) -> None:
        fake = Faker()
        assert fake._forge.locale == "en_US"

    def test_custom_locale(self) -> None:
        fake = Faker("de_DE")
        assert fake._forge.locale == "de_DE"

    def test_multi_locale(self) -> None:
        fake = Faker(["en_US", "ja_JP"])
        assert len(fake._forge.locales) == 2

    def test_seed_kwarg(self) -> None:
        fake = Faker(seed=42)
        name1 = fake.name()
        fake2 = Faker(seed=42)
        name2 = fake2.name()
        assert name1 == name2

    def test_repr(self) -> None:
        fake = Faker()
        assert "Faker" in repr(fake)
        assert "en_US" in repr(fake)


class TestFakerSeeding:
    def test_seed_instance(self) -> None:
        fake = Faker()
        fake.seed_instance(99)
        name1 = fake.name()
        fake.seed_instance(99)
        name2 = fake.name()
        assert name1 == name2

    def test_global_seed(self) -> None:
        Faker.seed(123)
        fake1 = Faker()
        name1 = fake1.name()
        fake2 = Faker()
        name2 = fake2.name()
        assert name1 == name2
        # Reset global seed
        Faker.seed(None)  # type: ignore[arg-type]

    def test_seed_locale_compat(self) -> None:
        """seed_locale is a no-op but should not raise."""
        fake = Faker()
        fake.seed_locale("en_US", 42)


# ── Parametrized method resolution ──────────────────────────────────────


_METHOD_CASES: list[tuple[str, type, object | None]] = [
    # (method_name, expected_type, extra_assertion_or_None)
    ("name", str, None),
    ("email", str, lambda r: "@" in r),
    ("address", str, None),
    ("city", str, None),
    ("company", str, None),
    ("job", str, None),
    ("phone_number", str, None),
    ("ssn", str, None),
    ("sentence", str, None),
    ("url", str, lambda r: r.startswith("http")),
    ("uuid4", str, lambda r: len(r) == 36),
    ("boolean", bool, None),
    ("ipv4", str, lambda r: len(r.split(".")) == 4),
    ("date", str, None),
    ("credit_card_number", str, None),
]


class TestFakerMethodResolution:
    @pytest.mark.parametrize(
        "method, expected_type, check",
        _METHOD_CASES,
        ids=[c[0] for c in _METHOD_CASES],
    )
    def test_method_returns_correct_type(
        self,
        method: str,
        expected_type: type,
        check: object | None,
    ) -> None:
        fake = Faker(seed=1)
        result = getattr(fake, method)()
        assert isinstance(result, expected_type)
        if check is not None:
            assert check(result)  # type: ignore[operator]


class TestFakerMethodCache:
    def test_method_cached_after_first_call(self) -> None:
        fake = Faker(seed=1)
        fake.name()
        assert "name" in fake._method_cache

    def test_cache_speeds_up_repeated_calls(self) -> None:
        fake = Faker(seed=1)
        # Call multiple times to verify no errors
        for _ in range(100):
            fake.email()


class TestFakerUnknownMethod:
    def test_raises_attribute_error(self) -> None:
        fake = Faker()
        with pytest.raises(AttributeError, match="no method"):
            fake.nonexistent_method_xyz()


class TestFakerMethodMapCoverage:
    """Verify all methods in _FAKER_METHOD_MAP resolve to working callables."""

    def test_all_mapped_methods_are_callable(self) -> None:
        fake = Faker(seed=42)
        for method_name in _FAKER_METHOD_MAP:
            fn = fake._resolve_method(method_name)
            assert callable(fn), f"{method_name} did not resolve to callable"

    def test_all_mapped_methods_produce_values(self) -> None:
        fake = Faker(seed=42)
        for method_name in _FAKER_METHOD_MAP:
            result = getattr(fake, method_name)()
            assert result is not None, f"{method_name}() returned None"
