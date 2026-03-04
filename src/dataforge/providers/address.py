"""Address provider — generates fake addresses."""

from types import ModuleType
from typing import Literal, overload

from dataforge.backend import RandomEngine
from dataforge.providers.base import BaseProvider

# ISO 3166-1 countries — separate tuples for direct batch access
_COUNTRY_NAMES: tuple[str, ...] = (
    "United States",
    "United Kingdom",
    "Canada",
    "Australia",
    "Germany",
    "France",
    "Spain",
    "Italy",
    "Brazil",
    "Japan",
    "South Korea",
    "China",
    "India",
    "Mexico",
    "Russia",
    "Netherlands",
    "Belgium",
    "Switzerland",
    "Sweden",
    "Norway",
    "Denmark",
    "Finland",
    "Poland",
    "Austria",
    "Portugal",
    "Ireland",
    "New Zealand",
    "South Africa",
    "Argentina",
    "Colombia",
    "Chile",
    "Turkey",
    "Thailand",
    "Indonesia",
    "Malaysia",
    "Singapore",
    "Philippines",
    "Vietnam",
    "Egypt",
    "Nigeria",
    "Saudi Arabia",
    "UAE",
    "Israel",
    "Czech Republic",
    "Romania",
    "Hungary",
    "Greece",
    "Ukraine",
    "Peru",
    "Pakistan",
)

_COUNTRY_CODES: tuple[str, ...] = (
    "US",
    "GB",
    "CA",
    "AU",
    "DE",
    "FR",
    "ES",
    "IT",
    "BR",
    "JP",
    "KR",
    "CN",
    "IN",
    "MX",
    "RU",
    "NL",
    "BE",
    "CH",
    "SE",
    "NO",
    "DK",
    "FI",
    "PL",
    "AT",
    "PT",
    "IE",
    "NZ",
    "ZA",
    "AR",
    "CO",
    "CL",
    "TR",
    "TH",
    "ID",
    "MY",
    "SG",
    "PH",
    "VN",
    "EG",
    "NG",
    "SA",
    "AE",
    "IL",
    "CZ",
    "RO",
    "HU",
    "GR",
    "UA",
    "PE",
    "PK",
)


class AddressProvider(BaseProvider):
    """Generates fake street addresses, cities, states, and zip codes.

    Parameters
    ----------
    engine : RandomEngine
        The shared random engine instance.
    locale_data : ModuleType
        The imported locale module (e.g. ``dataforge.locales.en_US.address``).
    """

    __slots__ = (
        "_street_names",
        "_street_suffixes",
        "_cities",
        "_states",
        "_zip_formats",
        "_building_number_formats",
    )

    _provider_name = "address"
    _locale_modules = ("address",)
    _field_map = {
        "address": "full_address",
        "full_address": "full_address",
        "street_address": "street_address",
        "street_name": "street_name",
        "city": "city",
        "state": "state",
        "zip_code": "zip_code",
        "building_number": "building_number",
        "country": "country",
        "country_code": "country_code",
        "latitude": "latitude",
        "longitude": "longitude",
        "coordinate": "coordinate",
    }

    def __init__(self, engine: RandomEngine, locale_data: ModuleType) -> None:
        super().__init__(engine)
        self._street_names: tuple[str, ...] = locale_data.street_names
        self._street_suffixes: tuple[str, ...] = locale_data.street_suffixes
        self._cities: tuple[str, ...] = locale_data.cities
        self._states: tuple[str, ...] = locale_data.states
        self._zip_formats: tuple[str, ...] = locale_data.zip_formats
        self._building_number_formats: tuple[str, ...] = (
            locale_data.building_number_formats
        )

    # ------------------------------------------------------------------
    # Scalar helpers (always return a single str)
    # ------------------------------------------------------------------

    def _one_building_number(self) -> str:
        fmt = self._engine.choice(self._building_number_formats)
        return self._engine.numerify(fmt)

    def _one_street(self) -> str:
        name = self._engine.choice(self._street_names)
        suffix = self._engine.choice(self._street_suffixes)
        return f"{name} {suffix}" if suffix else name

    def _one_zip_code(self) -> str:
        fmt = self._engine.choice(self._zip_formats)
        return self._engine.numerify(fmt)

    def _one_full_address(self) -> str:
        building = self._one_building_number()
        street = self._one_street()
        city = self._engine.choice(self._cities)
        state = self._engine.choice(self._states)
        zip_code = self._one_zip_code()
        return f"{building} {street}, {city}, {state} {zip_code}"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @overload
    def building_number(self) -> str: ...
    @overload
    def building_number(self, count: Literal[1]) -> str: ...
    @overload
    def building_number(self, count: int) -> str | list[str]: ...
    def building_number(self, count: int = 1) -> str | list[str]:
        """Generate a random building number.

        Parameters
        ----------
        count : int
            Number of building numbers to generate.
        """
        if count == 1:
            return self._one_building_number()
        return [self._one_building_number() for _ in range(count)]

    @overload
    def street_name(self) -> str: ...
    @overload
    def street_name(self, count: Literal[1]) -> str: ...
    @overload
    def street_name(self, count: int) -> str | list[str]: ...
    def street_name(self, count: int = 1) -> str | list[str]:
        """Generate a random street name (e.g. ``"Oak Ave"``).

        Parameters
        ----------
        count : int
            Number of street names to generate.
        """
        if count == 1:
            return self._one_street()
        return [self._one_street() for _ in range(count)]

    @overload
    def street_address(self) -> str: ...
    @overload
    def street_address(self, count: Literal[1]) -> str: ...
    @overload
    def street_address(self, count: int) -> str | list[str]: ...
    def street_address(self, count: int = 1) -> str | list[str]:
        """Generate a random street address (e.g. ``"4821 Oak Ave"``).

        Parameters
        ----------
        count : int
            Number of street addresses to generate.
        """
        if count == 1:
            return f"{self._one_building_number()} {self._one_street()}"
        return [
            f"{self._one_building_number()} {self._one_street()}" for _ in range(count)
        ]

    @overload
    def city(self) -> str: ...
    @overload
    def city(self, count: Literal[1]) -> str: ...
    @overload
    def city(self, count: int) -> str | list[str]: ...
    def city(self, count: int = 1) -> str | list[str]:
        """Generate a random city name.

        Parameters
        ----------
        count : int
            Number of city names to generate.
        """
        if count == 1:
            return self._engine.choice(self._cities)
        return self._engine.choices(self._cities, count)

    @overload
    def state(self) -> str: ...
    @overload
    def state(self, count: Literal[1]) -> str: ...
    @overload
    def state(self, count: int) -> str | list[str]: ...
    def state(self, count: int = 1) -> str | list[str]:
        """Generate a random US state abbreviation.

        Parameters
        ----------
        count : int
            Number of state abbreviations to generate.
        """
        if count == 1:
            return self._engine.choice(self._states)
        return self._engine.choices(self._states, count)

    @overload
    def zip_code(self) -> str: ...
    @overload
    def zip_code(self, count: Literal[1]) -> str: ...
    @overload
    def zip_code(self, count: int) -> str | list[str]: ...
    def zip_code(self, count: int = 1) -> str | list[str]:
        """Generate a random zip code (e.g. ``"90210"`` or ``"90210-1234"``).

        Parameters
        ----------
        count : int
            Number of zip codes to generate.
        """
        if count == 1:
            return self._one_zip_code()
        return [self._one_zip_code() for _ in range(count)]

    @overload
    def full_address(self) -> str: ...
    @overload
    def full_address(self, count: Literal[1]) -> str: ...
    @overload
    def full_address(self, count: int) -> str | list[str]: ...
    def full_address(self, count: int = 1) -> str | list[str]:
        """Generate a complete fake address.

        Example: ``"4821 Oak Ave, Chicago, IL 60614"``

        Parameters
        ----------
        count : int
            Number of full addresses to generate.
        """
        if count == 1:
            return self._one_full_address()
        # Vectorized batch: bulk choices() for cities/states (2 calls
        # instead of 2N scalar calls). Building/street/zip inlined with
        # local-bound engine methods for tighter inner loop.
        _choice = self._engine.choice
        _numerify = self._engine.numerify
        cities = self._engine.choices(self._cities, count)
        states = self._engine.choices(self._states, count)
        _bn_fmts = self._building_number_formats
        _st_names = self._street_names
        _st_suffixes = self._street_suffixes
        _zip_fmts = self._zip_formats
        result: list[str] = []
        for i in range(count):
            bldg = _numerify(_choice(_bn_fmts))
            sname = _choice(_st_names)
            ssuf = _choice(_st_suffixes)
            street = f"{sname} {ssuf}" if ssuf else sname
            zipcode = _numerify(_choice(_zip_fmts))
            result.append(f"{bldg} {street}, {cities[i]}, {states[i]} {zipcode}")
        return result

    @overload
    def country(self) -> str: ...
    @overload
    def country(self, count: Literal[1]) -> str: ...
    @overload
    def country(self, count: int) -> str | list[str]: ...
    def country(self, count: int = 1) -> str | list[str]:
        """Generate a random country name (e.g. ``"Germany"``).

        Parameters
        ----------
        count : int
            Number of country names to generate.
        """
        if count == 1:
            return self._engine.choice(_COUNTRY_NAMES)
        return self._engine.choices(_COUNTRY_NAMES, count)

    @overload
    def country_code(self) -> str: ...
    @overload
    def country_code(self, count: Literal[1]) -> str: ...
    @overload
    def country_code(self, count: int) -> str | list[str]: ...
    def country_code(self, count: int = 1) -> str | list[str]:
        """Generate a random ISO 3166-1 alpha-2 country code (e.g. ``"DE"``).

        Parameters
        ----------
        count : int
            Number of country codes to generate.
        """
        if count == 1:
            return self._engine.choice(_COUNTRY_CODES)
        return self._engine.choices(_COUNTRY_CODES, count)

    @overload
    def latitude(self) -> str: ...
    @overload
    def latitude(self, count: Literal[1]) -> str: ...
    @overload
    def latitude(self, count: int) -> str | list[str]: ...
    def latitude(self, count: int = 1) -> str | list[str]:
        """Generate a random latitude (``-90.0`` to ``90.0``).

        Parameters
        ----------
        count : int
            Number of latitudes to generate.

        Returns
        -------
        str or list[str]
            Latitude as a decimal string with 6 decimal places.
        """
        ri = self._engine.random_int
        if count == 1:
            return f"{ri(-90_000_000, 90_000_000) / 1_000_000:.6f}"
        return [f"{ri(-90_000_000, 90_000_000) / 1_000_000:.6f}" for _ in range(count)]

    @overload
    def longitude(self) -> str: ...
    @overload
    def longitude(self, count: Literal[1]) -> str: ...
    @overload
    def longitude(self, count: int) -> str | list[str]: ...
    def longitude(self, count: int = 1) -> str | list[str]:
        """Generate a random longitude (``-180.0`` to ``180.0``).

        Parameters
        ----------
        count : int
            Number of longitudes to generate.

        Returns
        -------
        str or list[str]
            Longitude as a decimal string with 6 decimal places.
        """
        ri = self._engine.random_int
        if count == 1:
            return f"{ri(-180_000_000, 180_000_000) / 1_000_000:.6f}"
        return [
            f"{ri(-180_000_000, 180_000_000) / 1_000_000:.6f}" for _ in range(count)
        ]

    @overload
    def coordinate(self) -> tuple[str, str]: ...
    @overload
    def coordinate(self, count: Literal[1]) -> tuple[str, str]: ...
    @overload
    def coordinate(self, count: int) -> tuple[str, str] | list[tuple[str, str]]: ...
    def coordinate(self, count: int = 1) -> tuple[str, str] | list[tuple[str, str]]:
        """Generate a random (latitude, longitude) pair.

        Parameters
        ----------
        count : int
            Number of coordinate pairs to generate.

        Returns
        -------
        tuple[str, str] or list[tuple[str, str]]
        """
        ri = self._engine.random_int
        if count == 1:
            return (
                f"{ri(-90_000_000, 90_000_000) / 1_000_000:.6f}",
                f"{ri(-180_000_000, 180_000_000) / 1_000_000:.6f}",
            )
        return [
            (
                f"{ri(-90_000_000, 90_000_000) / 1_000_000:.6f}",
                f"{ri(-180_000_000, 180_000_000) / 1_000_000:.6f}",
            )
            for _ in range(count)
        ]
