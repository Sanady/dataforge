"""Tests for Feature 5: Type-Driven Schema for stdlib types."""

import warnings
from dataclasses import dataclass
from typing import Optional, TypedDict

import pytest

from dataforge import DataForge


# --- Test dataclasses ---


@dataclass
class User:
    first_name: str
    last_name: str
    email: str
    city: str


@dataclass
class WithBool:
    first_name: str
    is_active: bool


@dataclass
class Unmappable:
    xyzzy_field: str
    plugh_field: int


@dataclass
class PartialMatch:
    first_name: str
    xyzzy: str


@dataclass
class WithAlias:
    fname: str  # alias → first_name
    mail: str  # alias → email
    phone: str  # alias → phone_number


@dataclass
class WithOptional:
    first_name: str
    email: Optional[str]


# --- Test TypedDicts ---


class UserDict(TypedDict):
    first_name: str
    email: str
    city: str


class UnmappableDict(TypedDict):
    xyzzy: str
    plugh: int


class AliasDictType(TypedDict):
    fname: str
    mail: str


class TestSchemaFromDataclass:
    def test_basic_dataclass(self) -> None:
        forge = DataForge(seed=42)
        schema = forge.schema_from_dataclass(User)
        rows = schema.generate(5)
        assert len(rows) == 5
        for row in rows:
            assert "first_name" in row
            assert "last_name" in row
            assert "email" in row
            assert "@" in row["email"]

    def test_bool_type_fallback(self) -> None:
        forge = DataForge(seed=42)
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            schema = forge.schema_from_dataclass(WithBool)
        rows = schema.generate(5)
        for row in rows:
            assert "first_name" in row

    def test_unmappable_raises(self) -> None:
        forge = DataForge(seed=42)
        with pytest.raises(ValueError, match="No fields"):
            with warnings.catch_warnings(record=True):
                warnings.simplefilter("always")
                forge.schema_from_dataclass(Unmappable)

    def test_partial_match_warns(self) -> None:
        forge = DataForge(seed=42)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            schema = forge.schema_from_dataclass(PartialMatch)
        # Should have at least one warning for the unmapped field
        unmapped_warnings = [x for x in w if "could not be mapped" in str(x.message)]
        assert len(unmapped_warnings) >= 1
        rows = schema.generate(3)
        assert all("first_name" in row for row in rows)

    def test_alias_fields(self) -> None:
        forge = DataForge(seed=42)
        schema = forge.schema_from_dataclass(WithAlias)
        rows = schema.generate(3)
        for row in rows:
            assert "fname" in row
            assert "mail" in row
            assert "phone" in row

    def test_not_a_dataclass_raises(self) -> None:
        forge = DataForge()
        with pytest.raises(TypeError, match="Expected a dataclass"):
            forge.schema_from_dataclass(str)  # type: ignore[arg-type]


class TestSchemaFromTypedDict:
    def test_basic_typed_dict(self) -> None:
        forge = DataForge(seed=42)
        schema = forge.schema_from_typed_dict(UserDict)
        rows = schema.generate(5)
        assert len(rows) == 5
        for row in rows:
            assert "first_name" in row
            assert "email" in row
            assert "city" in row

    def test_unmappable_typed_dict_raises(self) -> None:
        forge = DataForge(seed=42)
        with pytest.raises(ValueError, match="No fields"):
            with warnings.catch_warnings(record=True):
                warnings.simplefilter("always")
                forge.schema_from_typed_dict(UnmappableDict)

    def test_alias_typed_dict(self) -> None:
        forge = DataForge(seed=42)
        schema = forge.schema_from_typed_dict(AliasDictType)
        rows = schema.generate(3)
        for row in rows:
            assert "fname" in row
            assert "mail" in row

    def test_no_annotations_raises(self) -> None:
        forge = DataForge()
        with pytest.raises((TypeError, ValueError)):
            forge.schema_from_typed_dict(object)  # type: ignore[arg-type]


class TestTypeResolution:
    def test_optional_str_resolves(self) -> None:
        """Optional[str] should resolve the inner str type."""
        forge = DataForge(seed=42)
        schema = forge.schema_from_dataclass(WithOptional)
        rows = schema.generate(3)
        for row in rows:
            assert "first_name" in row
            assert "email" in row
