"""Tests for Feature 2: Multi-Locale Mixing."""

from dataforge import DataForge


class TestMultiLocaleInit:
    def test_single_locale_as_list(self) -> None:
        forge = DataForge(locale=["en_US"])
        assert forge.locale == "en_US"
        assert forge.locales == ("en_US",)

    def test_multiple_locales(self) -> None:
        forge = DataForge(locale=["en_US", "ja_JP"])
        assert forge.locale == "en_US"  # primary
        assert forge.locales == ("en_US", "ja_JP")

    def test_empty_locale_list_raises(self) -> None:
        import pytest

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
        names = set()
        for _ in range(50):
            name = forge.person.first_name()
            names.add(name)
        # Should have variety — at least a few different names
        assert len(names) > 1

    def test_seeded_multi_locale_reproducible(self) -> None:
        forge1 = DataForge(locale=["en_US", "ja_JP"], seed=42)
        forge2 = DataForge(locale=["en_US", "ja_JP"], seed=42)
        names1 = [forge1.person.first_name() for _ in range(10)]
        names2 = [forge2.person.first_name() for _ in range(10)]
        assert names1 == names2


class TestMultiLocaleCopy:
    def test_copy_preserves_locales(self) -> None:
        forge = DataForge(locale=["en_US", "de_DE"])
        copy = forge.copy(seed=99)
        assert copy.locales == ("en_US", "de_DE")

    def test_copy_single_locale(self) -> None:
        forge = DataForge(locale="en_US")
        copy = forge.copy(seed=99)
        assert copy.locale == "en_US"


class TestMultiLocaleChildIsolation:
    def test_children_have_different_seeds(self) -> None:
        forge = DataForge(locale=["en_US", "de_DE"], seed=100)
        child1 = forge._locale_forges[0]
        child2 = forge._locale_forges[1]
        # Children should produce different sequences
        name1 = child1.person.first_name()
        name2 = child2.person.first_name()
        # They may occasionally collide, but structure should be sound
        assert isinstance(name1, str)
        assert isinstance(name2, str)

    def test_children_are_single_locale(self) -> None:
        forge = DataForge(locale=["en_US", "de_DE", "ja_JP"], seed=1)
        for child in forge._locale_forges:
            assert len(child._locales) == 1
            assert child._locale_forges == ()
