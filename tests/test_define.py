"""Tests for Feature 3: DynamicProvider / define()."""

import pytest

from dataforge import DataForge


class TestDefineElements:
    def test_define_simple_elements(self) -> None:
        forge = DataForge(seed=42)
        forge.define("status", elements=["active", "inactive", "pending"])
        result = forge.status()
        assert result in ("active", "inactive", "pending")

    def test_define_elements_count(self) -> None:
        forge = DataForge(seed=42)
        forge.define("color", elements=["red", "green", "blue"])
        results = forge.color(count=10)
        assert isinstance(results, list)
        assert len(results) == 10
        assert all(c in ("red", "green", "blue") for c in results)

    def test_define_elements_tuple(self) -> None:
        forge = DataForge(seed=42)
        forge.define("tier", elements=("gold", "silver", "bronze"))
        result = forge.tier()
        assert result in ("gold", "silver", "bronze")

    def test_define_elements_reproducible(self) -> None:
        forge1 = DataForge(seed=42)
        forge1.define("status", elements=["a", "b", "c"])
        forge2 = DataForge(seed=42)
        forge2.define("status", elements=["a", "b", "c"])
        assert forge1.status() == forge2.status()


class TestDefineWeightedElements:
    def test_define_weighted(self) -> None:
        forge = DataForge(seed=42)
        forge.define(
            "priority", elements=["low", "mid", "high"], weights=[0.7, 0.2, 0.1]
        )
        result = forge.priority()
        assert result in ("low", "mid", "high")

    def test_define_weighted_distribution(self) -> None:
        """Weighted elements should reflect the distribution roughly."""
        forge = DataForge(seed=42)
        forge.define("coin", elements=["heads", "tails"], weights=[0.9, 0.1])
        results = forge.coin(count=1000)
        heads_count = results.count("heads")
        # With 0.9 weight, expect ~900 heads. Allow wide margin for randomness.
        assert heads_count > 700


class TestDefineFunc:
    def test_define_func(self) -> None:
        forge = DataForge(seed=42)
        forge.define("greeting", func=lambda: "hello")
        assert forge.greeting() == "hello"

    def test_define_func_using_forge(self) -> None:
        forge = DataForge(seed=42)
        forge.define("upper_name", func=lambda: forge.person.first_name().upper())
        result = forge.upper_name()
        assert isinstance(result, str)
        assert result == result.upper()


class TestDefineErrors:
    def test_define_no_args_raises(self) -> None:
        forge = DataForge()
        with pytest.raises(ValueError, match="requires either"):
            forge.define("bad_field")


class TestDefineInSchema:
    def test_custom_field_in_schema(self) -> None:
        forge = DataForge(seed=42)
        forge.define("status", elements=["active", "inactive"])
        schema = forge.schema({"name": "full_name", "status": "status"})
        rows = schema.generate(5)
        assert len(rows) == 5
        for row in rows:
            assert row["status"] in ("active", "inactive")
            assert isinstance(row["name"], str)

    def test_custom_field_resolve(self) -> None:
        forge = DataForge(seed=42)
        forge.define("role", elements=["admin", "user"])
        provider_attr, method_name = forge._resolve_field("role")
        assert provider_attr == "_custom_fields"
        assert method_name == "role"


class TestDefineOverwrite:
    def test_redefine_field(self) -> None:
        forge = DataForge(seed=42)
        forge.define("status", elements=["a", "b"])
        forge.define("status", elements=["x", "y"])
        result = forge.status()
        assert result in ("x", "y")
