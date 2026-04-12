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
    fname: str  # alias -> first_name
    mail: str  # alias -> email
    phone: str  # alias -> phone_number


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


# ── Parametrized dataclass happy-path ───────────────────────────────────

_DATACLASS_CASES = [
    # (cls, count, required_keys, extra_check_column, extra_check)
    (User, 5, ["first_name", "last_name", "email"], "email", lambda v: "@" in v),
    (WithAlias, 3, ["fname", "mail", "phone"], None, None),
    (WithOptional, 3, ["first_name", "email"], None, None),
]


class TestSchemaFromDataclass:
    @pytest.mark.parametrize(
        "cls, count, required_keys, check_col, check_fn",
        _DATACLASS_CASES,
        ids=[c[0].__name__ for c in _DATACLASS_CASES],
    )
    def test_dataclass(
        self,
        cls: type,
        count: int,
        required_keys: list[str],
        check_col: str | None,
        check_fn: object | None,
    ) -> None:
        forge = DataForge(seed=42)
        schema = forge.schema_from_dataclass(cls)
        rows = schema.generate(count)
        assert len(rows) == count
        for row in rows:
            for key in required_keys:
                assert key in row
            if check_col and check_fn:
                assert check_fn(row[check_col])  # type: ignore[operator]

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
        unmapped_warnings = [x for x in w if "could not be mapped" in str(x.message)]
        assert len(unmapped_warnings) >= 1
        rows = schema.generate(3)
        assert all("first_name" in row for row in rows)

    def test_not_a_dataclass_raises(self) -> None:
        forge = DataForge()
        with pytest.raises(TypeError, match="Expected a dataclass"):
            forge.schema_from_dataclass(str)  # type: ignore[arg-type]


# ── Parametrized TypedDict cases ────────────────────────────────────────

_TYPEDDICT_CASES = [
    (UserDict, 5, ["first_name", "email", "city"]),
    (AliasDictType, 3, ["fname", "mail"]),
]


class TestSchemaFromTypedDict:
    @pytest.mark.parametrize(
        "cls, count, required_keys",
        _TYPEDDICT_CASES,
        ids=[c[0].__name__ for c in _TYPEDDICT_CASES],
    )
    def test_typed_dict(self, cls: type, count: int, required_keys: list[str]) -> None:
        forge = DataForge(seed=42)
        schema = forge.schema_from_typed_dict(cls)
        rows = schema.generate(count)
        assert len(rows) == count
        for row in rows:
            for key in required_keys:
                assert key in row

    def test_unmappable_typed_dict_raises(self) -> None:
        forge = DataForge(seed=42)
        with pytest.raises(ValueError, match="No fields"):
            with warnings.catch_warnings(record=True):
                warnings.simplefilter("always")
                forge.schema_from_typed_dict(UnmappableDict)

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
