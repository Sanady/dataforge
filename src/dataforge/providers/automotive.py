"""AutomotiveProvider — generates fake vehicle-related data.

Includes license plates, VINs, vehicle makes, models, years, and colors.
All data is stored as immutable ``tuple[str, ...]`` for cache friendliness.
"""

from typing import Literal, overload

from dataforge.providers.base import BaseProvider

# ------------------------------------------------------------------
# Data tuples (immutable, module-level for zero per-call overhead)
# ------------------------------------------------------------------

_VEHICLE_MAKES: tuple[str, ...] = (
    "Toyota",
    "Honda",
    "Ford",
    "Chevrolet",
    "BMW",
    "Mercedes-Benz",
    "Audi",
    "Volkswagen",
    "Hyundai",
    "Kia",
    "Nissan",
    "Subaru",
    "Mazda",
    "Lexus",
    "Tesla",
    "Jeep",
    "Ram",
    "GMC",
    "Dodge",
    "Buick",
    "Cadillac",
    "Lincoln",
    "Acura",
    "Infiniti",
    "Volvo",
    "Porsche",
    "Land Rover",
    "Jaguar",
    "Mitsubishi",
    "Chrysler",
    "Fiat",
    "Alfa Romeo",
    "Genesis",
    "Rivian",
    "Lucid",
    "Polestar",
    "Mini",
    "Maserati",
    "Ferrari",
    "Lamborghini",
)

_VEHICLE_MODELS: tuple[str, ...] = (
    "Camry",
    "Civic",
    "F-150",
    "Silverado",
    "3 Series",
    "C-Class",
    "A4",
    "Golf",
    "Elantra",
    "Forte",
    "Altima",
    "Outback",
    "CX-5",
    "RX",
    "Model 3",
    "Wrangler",
    "1500",
    "Sierra",
    "Charger",
    "Encore",
    "Escalade",
    "Navigator",
    "MDX",
    "Q50",
    "XC90",
    "911",
    "Range Rover",
    "F-Type",
    "Outlander",
    "Pacifica",
    "500",
    "Giulia",
    "G70",
    "R1T",
    "Air",
    "Polestar 2",
    "Cooper",
    "Ghibli",
    "488",
    "Urus",
    "Corolla",
    "Accord",
    "Mustang",
    "Malibu",
    "X5",
    "E-Class",
    "Q7",
    "Passat",
    "Tucson",
    "Sportage",
    "Sentra",
    "Forester",
    "Mazda3",
    "ES",
    "Model Y",
    "Grand Cherokee",
    "2500",
    "Yukon",
    "Challenger",
    "Enclave",
    "CT5",
    "Corsair",
    "TLX",
    "QX60",
    "XC60",
    "Cayenne",
    "Defender",
    "XE",
    "Eclipse Cross",
    "300",
)

_VEHICLE_COLORS: tuple[str, ...] = (
    "Black",
    "White",
    "Silver",
    "Gray",
    "Red",
    "Blue",
    "Green",
    "Brown",
    "Beige",
    "Gold",
    "Orange",
    "Yellow",
    "Purple",
    "Burgundy",
    "Navy",
    "Charcoal",
    "Pearl White",
    "Midnight Blue",
    "Racing Red",
    "Arctic Silver",
)

_PLATE_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_PLATE_DIGITS = "0123456789"

# VIN character set (excludes I, O, Q per standard)
_VIN_CHARS = "ABCDEFGHJKLMNPRSTUVWXYZ0123456789"
_VIN_WEIGHTS = (8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2)
_VIN_TRANSLITERATE = {
    "A": 1,
    "B": 2,
    "C": 3,
    "D": 4,
    "E": 5,
    "F": 6,
    "G": 7,
    "H": 8,
    "J": 1,
    "K": 2,
    "L": 3,
    "M": 4,
    "N": 5,
    "P": 7,
    "R": 9,
    "S": 2,
    "T": 3,
    "U": 4,
    "V": 5,
    "W": 6,
    "X": 7,
    "Y": 8,
    "Z": 9,
    "0": 0,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
}


class AutomotiveProvider(BaseProvider):
    """Generates fake automotive / vehicle data.

    This provider is locale-independent.

    Parameters
    ----------
    engine : RandomEngine
        The shared random engine instance.
    """

    __slots__ = ()

    _provider_name = "automotive"
    _locale_modules: tuple[str, ...] = ()
    _field_map: dict[str, str] = {
        "license_plate": "license_plate",
        "vin": "vin",
        "vehicle_make": "vehicle_make",
        "vehicle_model": "vehicle_model",
        "vehicle_year": "vehicle_year_str",
        "vehicle_color": "vehicle_color",
    }

    # ------------------------------------------------------------------
    # Scalar helpers
    # ------------------------------------------------------------------

    def _one_plate(self) -> str:
        """Generate a single US-style license plate (ABC-1234)."""
        choice = self._engine._rng.choice
        a = choice(_PLATE_LETTERS)
        b = choice(_PLATE_LETTERS)
        c = choice(_PLATE_LETTERS)
        d = choice(_PLATE_DIGITS)
        e = choice(_PLATE_DIGITS)
        f = choice(_PLATE_DIGITS)
        g = choice(_PLATE_DIGITS)
        return f"{a}{b}{c}-{d}{e}{f}{g}"

    def _one_vin(self) -> str:
        """Generate a single 17-char VIN with valid check digit."""
        choices = self._engine._rng.choices
        # Positions: 0-7 (WMI + VDS), 8 (check digit), 9-16 (VIS)
        chars = choices(_VIN_CHARS, k=17)
        # Calculate check digit (position 8)
        total = 0
        for i, ch in enumerate(chars):
            if i == 8:
                continue  # skip check digit position
            total += _VIN_TRANSLITERATE[ch] * _VIN_WEIGHTS[i]
        remainder = total % 11
        chars[8] = "X" if remainder == 10 else str(remainder)
        return "".join(chars)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @overload
    def license_plate(self) -> str: ...
    @overload
    def license_plate(self, count: Literal[1]) -> str: ...
    @overload
    def license_plate(self, count: int) -> str | list[str]: ...
    def license_plate(self, count: int = 1) -> str | list[str]:
        """Generate a US-style license plate (e.g. ``"ABC-1234"``).

        Parameters
        ----------
        count : int
            Number of plates to generate.

        Returns
        -------
        str or list[str]
        """
        if count == 1:
            return self._one_plate()
        return [self._one_plate() for _ in range(count)]

    @overload
    def vin(self) -> str: ...
    @overload
    def vin(self, count: Literal[1]) -> str: ...
    @overload
    def vin(self, count: int) -> str | list[str]: ...
    def vin(self, count: int = 1) -> str | list[str]:
        """Generate a 17-character Vehicle Identification Number.

        The check digit (position 9) is computed correctly per the
        ISO 3779 / FMVSS 115 algorithm.

        Parameters
        ----------
        count : int
            Number of VINs to generate.

        Returns
        -------
        str or list[str]
        """
        if count == 1:
            return self._one_vin()
        return [self._one_vin() for _ in range(count)]

    @overload
    def vehicle_make(self) -> str: ...
    @overload
    def vehicle_make(self, count: Literal[1]) -> str: ...
    @overload
    def vehicle_make(self, count: int) -> str | list[str]: ...
    def vehicle_make(self, count: int = 1) -> str | list[str]:
        """Generate a vehicle manufacturer name (e.g. ``"Toyota"``).

        Parameters
        ----------
        count : int
            Number of makes to generate.

        Returns
        -------
        str or list[str]
        """
        if count == 1:
            return self._engine.choice(_VEHICLE_MAKES)
        return self._engine.choices(_VEHICLE_MAKES, count)

    @overload
    def vehicle_model(self) -> str: ...
    @overload
    def vehicle_model(self, count: Literal[1]) -> str: ...
    @overload
    def vehicle_model(self, count: int) -> str | list[str]: ...
    def vehicle_model(self, count: int = 1) -> str | list[str]:
        """Generate a vehicle model name (e.g. ``"Camry"``).

        Parameters
        ----------
        count : int
            Number of models to generate.

        Returns
        -------
        str or list[str]
        """
        if count == 1:
            return self._engine.choice(_VEHICLE_MODELS)
        return self._engine.choices(_VEHICLE_MODELS, count)

    @overload
    def vehicle_year(self) -> int: ...
    @overload
    def vehicle_year(self, count: Literal[1]) -> int: ...
    @overload
    def vehicle_year(self, count: int) -> int | list[int]: ...
    def vehicle_year(self, count: int = 1) -> int | list[int]:
        """Generate a vehicle model year (1990–2026).

        Parameters
        ----------
        count : int
            Number of years to generate.

        Returns
        -------
        int or list[int]
        """
        ri = self._engine.random_int
        if count == 1:
            return ri(1990, 2026)
        return [ri(1990, 2026) for _ in range(count)]

    @overload
    def vehicle_year_str(self) -> str: ...
    @overload
    def vehicle_year_str(self, count: Literal[1]) -> str: ...
    @overload
    def vehicle_year_str(self, count: int) -> str | list[str]: ...
    def vehicle_year_str(self, count: int = 1) -> str | list[str]:
        """Generate a vehicle model year as a string (``"1990"``–``"2026"``).

        This variant is used by the ``_field_map`` for Schema
        compatibility (all Schema fields must produce strings).

        Parameters
        ----------
        count : int
            Number of years to generate.

        Returns
        -------
        str or list[str]
        """
        ri = self._engine.random_int
        if count == 1:
            return str(ri(1990, 2026))
        return [str(ri(1990, 2026)) for _ in range(count)]

    @overload
    def vehicle_color(self) -> str: ...
    @overload
    def vehicle_color(self, count: Literal[1]) -> str: ...
    @overload
    def vehicle_color(self, count: int) -> str | list[str]: ...
    def vehicle_color(self, count: int = 1) -> str | list[str]:
        """Generate a vehicle color (e.g. ``"Midnight Blue"``).

        Parameters
        ----------
        count : int
            Number of colors to generate.

        Returns
        -------
        str or list[str]
        """
        if count == 1:
            return self._engine.choice(_VEHICLE_COLORS)
        return self._engine.choices(_VEHICLE_COLORS, count)
