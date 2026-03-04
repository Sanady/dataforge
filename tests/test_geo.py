"""Tests for the GeoProvider."""

import re

from dataforge import DataForge


class TestContinent:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_returns_str(self) -> None:
        assert isinstance(self.forge.geo.continent(), str)

    def test_valid(self) -> None:
        valid = {
            "Africa",
            "Antarctica",
            "Asia",
            "Europe",
            "North America",
            "Oceania",
            "South America",
        }
        for _ in range(50):
            assert self.forge.geo.continent() in valid

    def test_batch(self) -> None:
        results = self.forge.geo.continent(count=50)
        assert len(results) == 50


class TestOcean:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_returns_str(self) -> None:
        assert isinstance(self.forge.geo.ocean(), str)

    def test_batch(self) -> None:
        results = self.forge.geo.ocean(count=50)
        assert len(results) == 50


class TestSea:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_returns_str(self) -> None:
        assert isinstance(self.forge.geo.sea(), str)

    def test_batch(self) -> None:
        results = self.forge.geo.sea(count=50)
        assert len(results) == 50


class TestMountainRange:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_returns_str(self) -> None:
        assert isinstance(self.forge.geo.mountain_range(), str)

    def test_batch(self) -> None:
        results = self.forge.geo.mountain_range(count=50)
        assert len(results) == 50


class TestRiver:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_returns_str(self) -> None:
        assert isinstance(self.forge.geo.river(), str)

    def test_batch(self) -> None:
        results = self.forge.geo.river(count=50)
        assert len(results) == 50


class TestCompassDirection:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_returns_str(self) -> None:
        direction = self.forge.geo.compass_direction()
        assert isinstance(direction, str)
        assert len(direction) <= 3

    def test_batch(self) -> None:
        results = self.forge.geo.compass_direction(count=50)
        assert len(results) == 50


class TestGeoCoordinate:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_format(self) -> None:
        coord = self.forge.geo.geo_coordinate()
        assert re.match(r"^-?\d+\.\d{4}, -?\d+\.\d{4}$", coord)

    def test_batch(self) -> None:
        results = self.forge.geo.geo_coordinate(count=50)
        assert len(results) == 50


class TestDMSLatitude:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_format(self) -> None:
        lat = self.forge.geo.dms_latitude()
        assert isinstance(lat, str)
        assert lat[-1] in ("N", "S")

    def test_batch(self) -> None:
        results = self.forge.geo.dms_latitude(count=50)
        assert len(results) == 50


class TestDMSLongitude:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_format(self) -> None:
        lon = self.forge.geo.dms_longitude()
        assert isinstance(lon, str)
        assert lon[-1] in ("E", "W")

    def test_batch(self) -> None:
        results = self.forge.geo.dms_longitude(count=50)
        assert len(results) == 50


class TestGeoHash:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_format(self) -> None:
        h = self.forge.geo.geo_hash()
        assert isinstance(h, str)
        assert 6 <= len(h) <= 12
        # Base32 chars only (no a, i, l, o)
        valid_chars = set("0123456789bcdefghjkmnpqrstuvwxyz")
        assert all(c in valid_chars for c in h)

    def test_batch(self) -> None:
        results = self.forge.geo.geo_hash(count=50)
        assert len(results) == 50


class TestGeoInSchema:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_schema_fields(self) -> None:
        rows = self.forge.to_dict(
            fields=["continent", "ocean", "river"],
            count=5,
        )
        assert len(rows) == 5
        for row in rows:
            assert "continent" in row
            assert "ocean" in row
            assert "river" in row
