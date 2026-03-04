"""Person provider — generates fake personal names."""

from types import ModuleType
from typing import Literal, overload

from dataforge.backend import RandomEngine
from dataforge.providers.base import BaseProvider

# Module-level constants for zero per-call overhead
_PREFIXES: tuple[str, ...] = ("Mr.", "Mrs.", "Ms.", "Dr.")
_SUFFIXES: tuple[str, ...] = ("Jr.", "Sr.", "III", "IV", "V")


class PersonProvider(BaseProvider):
    """Generates fake first names, last names, and full names.

    Parameters
    ----------
    engine : RandomEngine
        The shared random engine instance.
    locale_data : ModuleType
        The imported locale module (e.g. ``dataforge.locales.en_US.person``).
    """

    __slots__ = (
        "_first_names",
        "_last_names",
        "_male_first_names",
        "_female_first_names",
    )

    _provider_name = "person"
    _locale_modules = ("person",)
    _field_map = {
        "first_name": "first_name",
        "last_name": "last_name",
        "full_name": "full_name",
        "name": "full_name",
        "prefix": "prefix",
        "suffix": "suffix",
        "male_first_name": "male_first_name",
        "female_first_name": "female_first_name",
    }

    def __init__(self, engine: RandomEngine, locale_data: ModuleType) -> None:
        super().__init__(engine)
        self._first_names: tuple[str, ...] = locale_data.first_names
        self._last_names: tuple[str, ...] = locale_data.last_names
        # Gendered names — optional in locale data; fall back to full list
        self._male_first_names: tuple[str, ...] = getattr(
            locale_data, "male_first_names", locale_data.first_names
        )
        self._female_first_names: tuple[str, ...] = getattr(
            locale_data, "female_first_names", locale_data.first_names
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @overload
    def first_name(self) -> str: ...
    @overload
    def first_name(self, count: Literal[1]) -> str: ...
    @overload
    def first_name(self, count: int) -> str | list[str]: ...
    def first_name(self, count: int = 1) -> str | list[str]:
        """Generate a random first name.

        Parameters
        ----------
        count : int
            Number of names to generate.  ``1`` returns a single ``str``;
            any value > 1 returns a ``list[str]``.
        """
        if count == 1:
            return self._engine.choice(self._first_names)
        return self._engine.choices(self._first_names, count)

    @overload
    def last_name(self) -> str: ...
    @overload
    def last_name(self, count: Literal[1]) -> str: ...
    @overload
    def last_name(self, count: int) -> str | list[str]: ...
    def last_name(self, count: int = 1) -> str | list[str]:
        """Generate a random last name.

        Parameters
        ----------
        count : int
            Number of names to generate.  ``1`` returns a single ``str``;
            any value > 1 returns a ``list[str]``.
        """
        if count == 1:
            return self._engine.choice(self._last_names)
        return self._engine.choices(self._last_names, count)

    @overload
    def full_name(self) -> str: ...
    @overload
    def full_name(self, count: Literal[1]) -> str: ...
    @overload
    def full_name(self, count: int) -> str | list[str]: ...
    def full_name(self, count: int = 1) -> str | list[str]:
        """Generate a random full name (first + last).

        Parameters
        ----------
        count : int
            Number of names to generate.  ``1`` returns a single ``str``;
            any value > 1 returns a ``list[str]``.
        """
        if count == 1:
            first = self._engine.choice(self._first_names)
            last = self._engine.choice(self._last_names)
            return f"{first} {last}"

        firsts = self._engine.choices(self._first_names, count)
        lasts = self._engine.choices(self._last_names, count)
        return [f"{f} {ln}" for f, ln in zip(firsts, lasts)]

    @overload
    def prefix(self) -> str: ...
    @overload
    def prefix(self, count: Literal[1]) -> str: ...
    @overload
    def prefix(self, count: int) -> str | list[str]: ...
    def prefix(self, count: int = 1) -> str | list[str]:
        """Generate a name prefix (Mr., Mrs., Ms., Dr.).

        Parameters
        ----------
        count : int
            Number of prefixes to generate.
        """
        prefixes = _PREFIXES
        if count == 1:
            return self._engine.choice(prefixes)
        return self._engine.choices(prefixes, count)

    @overload
    def suffix(self) -> str: ...
    @overload
    def suffix(self, count: Literal[1]) -> str: ...
    @overload
    def suffix(self, count: int) -> str | list[str]: ...
    def suffix(self, count: int = 1) -> str | list[str]:
        """Generate a name suffix (Jr., Sr., III, IV, V).

        Parameters
        ----------
        count : int
            Number of suffixes to generate.
        """
        suffixes = _SUFFIXES
        if count == 1:
            return self._engine.choice(suffixes)
        return self._engine.choices(suffixes, count)

    @overload
    def male_first_name(self) -> str: ...
    @overload
    def male_first_name(self, count: Literal[1]) -> str: ...
    @overload
    def male_first_name(self, count: int) -> str | list[str]: ...
    def male_first_name(self, count: int = 1) -> str | list[str]:
        """Generate a random male first name.

        Parameters
        ----------
        count : int
            Number of names to generate.
        """
        if count == 1:
            return self._engine.choice(self._male_first_names)
        return self._engine.choices(self._male_first_names, count)

    @overload
    def female_first_name(self) -> str: ...
    @overload
    def female_first_name(self, count: Literal[1]) -> str: ...
    @overload
    def female_first_name(self, count: int) -> str | list[str]: ...
    def female_first_name(self, count: int = 1) -> str | list[str]:
        """Generate a random female first name.

        Parameters
        ----------
        count : int
            Number of names to generate.
        """
        if count == 1:
            return self._engine.choice(self._female_first_names)
        return self._engine.choices(self._female_first_names, count)
