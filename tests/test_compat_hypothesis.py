"""Tests for Feature 7: Hypothesis Strategy Bridge."""

import pytest

hypothesis = pytest.importorskip("hypothesis")

from hypothesis import given, settings

from dataforge.compat.hypothesis import forge_strategy, strategy


class TestStrategy:
    @given(email=strategy("email"))
    @settings(max_examples=10)
    def test_email_strategy(self, email: str) -> None:
        assert isinstance(email, str)
        assert "@" in email

    @given(name=strategy("first_name"))
    @settings(max_examples=10)
    def test_first_name_strategy(self, name: str) -> None:
        assert isinstance(name, str)
        assert len(name) > 0

    @given(city=strategy("city"))
    @settings(max_examples=10)
    def test_city_strategy(self, city: str) -> None:
        assert isinstance(city, str)

    @given(ip=strategy("ipv4"))
    @settings(max_examples=10)
    def test_ipv4_strategy(self, ip: str) -> None:
        assert isinstance(ip, str)
        parts = ip.split(".")
        assert len(parts) == 4


class TestForgeStrategy:
    @given(data=forge_strategy(["first_name", "email", "city"]))
    @settings(max_examples=10)
    def test_list_fields(self, data: dict) -> None:
        assert isinstance(data, dict)
        assert "first_name" in data
        assert "email" in data
        assert "city" in data

    @given(data=forge_strategy({"name": "full_name", "mail": "email"}))
    @settings(max_examples=10)
    def test_dict_fields(self, data: dict) -> None:
        assert isinstance(data, dict)
        assert "name" in data
        assert "mail" in data
        assert "@" in data["mail"]


class TestStrategyLocale:
    @given(name=strategy("first_name", locale="en_US"))
    @settings(max_examples=5)
    def test_locale_parameter(self, name: str) -> None:
        assert isinstance(name, str)
