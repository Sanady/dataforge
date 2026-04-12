"""Tests for Feature 2: Multi-Locale Mixing."""

import pytest

from dataforge import DataForge


# ── Parametrized init scenarios ─────────────────────────────────────────

_INIT_CASES = [
    # (locale_arg, expected_primary, expected_locales_tuple)
    (["en_US"], "en_US", ("en_US",)),
    (["en_US", "ja_JP"], "en_US", ("en_US", "ja_JP")),
    (["de_DE", "en_US", "ja_JP"], "de_DE", ("de_DE", "en_US", "ja_JP")),
]


class TestMultiLocaleInit:
    @pytest.mark.parametrize(
        "locale_arg, expected_primary, expected_locales",
        _INIT_CASES,
        ids=["-".join(c[0]) for c in _INIT_CASES],
    )
    def test_locale_init(
        self,
        locale_arg: list[str],
        expected_primary: str,
        expected_locales: tuple[str, ...],
    ) -> None:
        forge = DataForge(locale=locale_arg)
        assert forge.locale == expected_primary
        assert forge.locales == expected_locales

    def test_empty_locale_list_raises(self) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            DataForge(locale=[])

    def test_repr_multi_locale(self) -> None:
        forge = DataForge(locale=["en_US", "ja_JP"])
        r = repr(forge)
        assert "locales=" in r
        assert "en_US" in r
        assert "ja_JP" in r

    def test_repr_single_locale(self) -> None:
        forge = DataForge(locale="en_US")
        assert "locale=" in repr(forge)

    def test_locale_forges_created(self) -> None:
        forge = DataForge(locale=["en_US", "ja_JP"])
        assert len(forge._locale_forges) == 2


class TestMultiLocaleGeneration:
    def test_produces_names_from_multiple_locales(self) -> None:
        forge = DataForge(locale=["en_US", "ja_JP"], seed=42)
        names = {forge.person.first_name() for _ in range(50)}
        # Should have variety — at least a few different names
        assert len(names) > 1

    def test_seeded_multi_locale_reproducible(self) -> None:
        forge1 = DataForge(locale=["en_US", "ja_JP"], seed=42)
        forge2 = DataForge(locale=["en_US", "ja_JP"], seed=42)
        names1 = [forge1.person.first_name() for _ in range(10)]
        names2 = [forge2.person.first_name() for _ in range(10)]
        assert names1 == names2


class TestMultiLocaleCopy:
    @pytest.mark.parametrize(
        "locale_arg, expected",
        [
            (["en_US", "de_DE"], ("en_US", "de_DE")),
            ("en_US", ("en_US",)),
        ],
        ids=["multi", "single"],
    )
    def test_copy_preserves_locales(
        self, locale_arg: str | list[str], expected: tuple[str, ...]
    ) -> None:
        forge = DataForge(locale=locale_arg)
        copy = forge.copy(seed=99)
        assert copy.locales == expected


class TestMultiLocaleChildIsolation:
    def test_children_have_different_seeds(self) -> None:
        forge = DataForge(locale=["en_US", "de_DE"], seed=100)
        child1 = forge._locale_forges[0]
        child2 = forge._locale_forges[1]
        name1 = child1.person.first_name()
        name2 = child2.person.first_name()
        assert isinstance(name1, str)
        assert isinstance(name2, str)

    def test_children_are_single_locale(self) -> None:
        forge = DataForge(locale=["en_US", "de_DE", "ja_JP"], seed=1)
        for child in forge._locale_forges:
            assert len(child._locales) == 1
            assert child._locale_forges == ()
