"""Geo provider — coordinates, countries, continents, places, distances."""

from typing import Literal, overload

from dataforge.providers.base import BaseProvider

_CONTINENTS: tuple[str, ...] = (
    "Africa",
    "Antarctica",
    "Asia",
    "Europe",
    "North America",
    "Oceania",
    "South America",
)

_OCEANS: tuple[str, ...] = (
    "Pacific Ocean",
    "Atlantic Ocean",
    "Indian Ocean",
    "Southern Ocean",
    "Arctic Ocean",
)

_SEAS: tuple[str, ...] = (
    "Mediterranean Sea",
    "Caribbean Sea",
    "South China Sea",
    "Bering Sea",
    "Gulf of Mexico",
    "Sea of Okhotsk",
    "Sea of Japan",
    "Hudson Bay",
    "East China Sea",
    "Andaman Sea",
    "Black Sea",
    "Red Sea",
    "North Sea",
    "Baltic Sea",
    "Caspian Sea",
    "Arabian Sea",
    "Coral Sea",
    "Tasman Sea",
    "Banda Sea",
    "Timor Sea",
)

_MOUNTAIN_RANGES: tuple[str, ...] = (
    "Himalayas",
    "Andes",
    "Alps",
    "Rocky Mountains",
    "Appalachian Mountains",
    "Ural Mountains",
    "Atlas Mountains",
    "Carpathian Mountains",
    "Scandinavian Mountains",
    "Pyrenees",
    "Caucasus Mountains",
    "Sierra Nevada",
    "Karakoram",
    "Hindu Kush",
    "Tian Shan",
    "Kunlun Mountains",
    "Altai Mountains",
    "Drakensberg",
    "Great Dividing Range",
    "Brooks Range",
)

_RIVERS: tuple[str, ...] = (
    "Amazon",
    "Nile",
    "Yangtze",
    "Mississippi",
    "Yenisei",
    "Yellow River",
    "Ob",
    "Congo",
    "Amur",
    "Lena",
    "Mekong",
    "Mackenzie",
    "Niger",
    "Murray",
    "Tocantins",
    "Volga",
    "Danube",
    "Ganges",
    "Rhine",
    "Euphrates",
    "Indus",
    "Tigris",
    "Colorado",
    "Columbia",
    "Thames",
)

_COMPASS_DIRECTIONS: tuple[str, ...] = (
    "N",
    "NNE",
    "NE",
    "ENE",
    "E",
    "ESE",
    "SE",
    "SSE",
    "S",
    "SSW",
    "SW",
    "WSW",
    "W",
    "WNW",
    "NW",
    "NNW",
)

_COORDINATE_DMS_DIRS_LAT: tuple[str, ...] = ("N", "S")
_COORDINATE_DMS_DIRS_LON: tuple[str, ...] = ("E", "W")

# Geohash base32 alphabet — module-level constant to avoid per-call
# string creation inside _one_geo_hash().
_BASE32: str = "0123456789bcdefghjkmnpqrstuvwxyz"


class GeoProvider(BaseProvider):
    """Generates fake geographic data — coordinates, places, features."""

    __slots__ = ()

    _provider_name = "geo"
    _locale_modules: tuple[str, ...] = ()
    _field_map: dict[str, str] = {
        "continent": "continent",
        "ocean": "ocean",
        "sea": "sea",
        "mountain_range": "mountain_range",
        "river": "river",
        "compass_direction": "compass_direction",
        "compass": "compass_direction",
        "geo_coordinate": "geo_coordinate",
        "dms_latitude": "dms_latitude",
        "dms_longitude": "dms_longitude",
        "geo_hash": "geo_hash",
    }

    # --- Scalar helpers ---

    def _one_geo_coordinate(self) -> str:
        lat = self._engine.random_int(-9000, 9000) / 100.0
        lon = self._engine.random_int(-18000, 18000) / 100.0
        return f"{lat:.4f}, {lon:.4f}"

    def _one_dms_lat(self) -> str:
        deg = self._engine.random_int(0, 90)
        mins = self._engine.random_int(0, 59)
        secs = self._engine.random_int(0, 59)
        d = self._engine.choice(_COORDINATE_DMS_DIRS_LAT)
        return f"{deg}°{mins:02d}'{secs:02d}\"{d}"

    def _one_dms_lon(self) -> str:
        deg = self._engine.random_int(0, 180)
        mins = self._engine.random_int(0, 59)
        secs = self._engine.random_int(0, 59)
        d = self._engine.choice(_COORDINATE_DMS_DIRS_LON)
        return f"{deg}°{mins:02d}'{secs:02d}\"{d}"

    def _one_geo_hash(self) -> str:
        # Geohash: base32 string, typically 6-12 chars
        length = self._engine.random_int(6, 12)
        bits = self._engine.getrandbits(length * 5)
        chars: list[str] = []
        b32 = _BASE32
        for _ in range(length):
            chars.append(b32[bits & 0x1F])
            bits >>= 5
        return "".join(chars)

    # --- Public API ---

    @overload
    def continent(self) -> str: ...
    @overload
    def continent(self, count: Literal[1]) -> str: ...
    @overload
    def continent(self, count: int) -> str | list[str]: ...
    def continent(self, count: int = 1) -> str | list[str]:
        """Generate a continent name."""
        if count == 1:
            return self._engine.choice(_CONTINENTS)
        return self._engine.choices(_CONTINENTS, count)

    @overload
    def ocean(self) -> str: ...
    @overload
    def ocean(self, count: Literal[1]) -> str: ...
    @overload
    def ocean(self, count: int) -> str | list[str]: ...
    def ocean(self, count: int = 1) -> str | list[str]:
        """Generate an ocean name."""
        if count == 1:
            return self._engine.choice(_OCEANS)
        return self._engine.choices(_OCEANS, count)

    @overload
    def sea(self) -> str: ...
    @overload
    def sea(self, count: Literal[1]) -> str: ...
    @overload
    def sea(self, count: int) -> str | list[str]: ...
    def sea(self, count: int = 1) -> str | list[str]:
        """Generate a sea name."""
        if count == 1:
            return self._engine.choice(_SEAS)
        return self._engine.choices(_SEAS, count)

    @overload
    def mountain_range(self) -> str: ...
    @overload
    def mountain_range(self, count: Literal[1]) -> str: ...
    @overload
    def mountain_range(self, count: int) -> str | list[str]: ...
    def mountain_range(self, count: int = 1) -> str | list[str]:
        """Generate a mountain range name."""
        if count == 1:
            return self._engine.choice(_MOUNTAIN_RANGES)
        return self._engine.choices(_MOUNTAIN_RANGES, count)

    @overload
    def river(self) -> str: ...
    @overload
    def river(self, count: Literal[1]) -> str: ...
    @overload
    def river(self, count: int) -> str | list[str]: ...
    def river(self, count: int = 1) -> str | list[str]:
        """Generate a river name."""
        if count == 1:
            return self._engine.choice(_RIVERS)
        return self._engine.choices(_RIVERS, count)

    @overload
    def compass_direction(self) -> str: ...
    @overload
    def compass_direction(self, count: Literal[1]) -> str: ...
    @overload
    def compass_direction(self, count: int) -> str | list[str]: ...
    def compass_direction(self, count: int = 1) -> str | list[str]:
        """Generate a compass direction (e.g., N, NE, SSW)."""
        if count == 1:
            return self._engine.choice(_COMPASS_DIRECTIONS)
        return self._engine.choices(_COMPASS_DIRECTIONS, count)

    @overload
    def geo_coordinate(self) -> str: ...
    @overload
    def geo_coordinate(self, count: Literal[1]) -> str: ...
    @overload
    def geo_coordinate(self, count: int) -> str | list[str]: ...
    def geo_coordinate(self, count: int = 1) -> str | list[str]:
        """Generate a geographic coordinate pair (lat, lon)."""
        if count == 1:
            return self._one_geo_coordinate()
        # Inlined batch with local binding — avoids method call overhead
        _ri = self._engine.random_int
        return [
            f"{_ri(-9000, 9000) / 100.0:.4f}, {_ri(-18000, 18000) / 100.0:.4f}"
            for _ in range(count)
        ]

    @overload
    def dms_latitude(self) -> str: ...
    @overload
    def dms_latitude(self, count: Literal[1]) -> str: ...
    @overload
    def dms_latitude(self, count: int) -> str | list[str]: ...
    def dms_latitude(self, count: int = 1) -> str | list[str]:
        """Generate a latitude in degrees-minutes-seconds format."""
        if count == 1:
            return self._one_dms_lat()
        # Inlined batch with local binding
        _ri = self._engine.random_int
        _choice = self._engine.choice
        _dirs = _COORDINATE_DMS_DIRS_LAT
        return [
            f"{_ri(0, 90)}°{_ri(0, 59):02d}'{_ri(0, 59):02d}\"{_choice(_dirs)}"
            for _ in range(count)
        ]

    @overload
    def dms_longitude(self) -> str: ...
    @overload
    def dms_longitude(self, count: Literal[1]) -> str: ...
    @overload
    def dms_longitude(self, count: int) -> str | list[str]: ...
    def dms_longitude(self, count: int = 1) -> str | list[str]:
        """Generate a longitude in degrees-minutes-seconds format."""
        if count == 1:
            return self._one_dms_lon()
        # Inlined batch with local binding
        _ri = self._engine.random_int
        _choice = self._engine.choice
        _dirs = _COORDINATE_DMS_DIRS_LON
        return [
            f"{_ri(0, 180)}°{_ri(0, 59):02d}'{_ri(0, 59):02d}\"{_choice(_dirs)}"
            for _ in range(count)
        ]

    @overload
    def geo_hash(self) -> str: ...
    @overload
    def geo_hash(self, count: Literal[1]) -> str: ...
    @overload
    def geo_hash(self, count: int) -> str | list[str]: ...
    def geo_hash(self, count: int = 1) -> str | list[str]:
        """Generate a geohash string (base32, 6-12 chars)."""
        if count == 1:
            return self._one_geo_hash()
        # Inlined batch with local binding — avoids per-item method
        # call overhead and re-binding _BASE32 inside the loop.
        _ri = self._engine.random_int
        _getrandbits = self._engine.getrandbits
        b32 = _BASE32
        result: list[str] = []
        for _ in range(count):
            length = _ri(6, 12)
            bits = _getrandbits(length * 5)
            chars: list[str] = []
            for _j in range(length):
                chars.append(b32[bits & 0x1F])
                bits >>= 5
            result.append("".join(chars))
        return result
