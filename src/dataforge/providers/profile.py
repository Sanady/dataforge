"""ProfileProvider — generates coherent fake user profiles.

Each profile composes data from multiple providers (person, internet,
address, phone) to produce a consistent record where names, emails,
and usernames relate to each other.

Individual string fields are exposed in ``_field_map`` for Schema
compatibility.  The compound ``profile()`` method returns a ``dict``
and is available only via direct API use.
"""

from typing import TYPE_CHECKING, Literal, overload

from dataforge.backend import RandomEngine
from dataforge.providers.base import BaseProvider

if TYPE_CHECKING:
    from dataforge.core import DataForge


class ProfileProvider(BaseProvider):
    """Generates coherent fake user profiles.

    Unlike other providers, ``ProfileProvider`` needs a reference to
    the parent :class:`DataForge` instance so it can delegate to
    ``person``, ``internet``, ``address``, and ``phone`` providers.

    Parameters
    ----------
    engine : RandomEngine
        The shared random engine instance.
    forge : DataForge
        The parent DataForge instance for cross-provider access.
    """

    __slots__ = ("_forge",)

    _provider_name = "profile"
    _locale_modules: tuple[str, ...] = ()
    _needs_forge: bool = True
    _field_map: dict[str, str] = {
        "profile_first_name": "profile_first_name",
        "profile_last_name": "profile_last_name",
        "profile_email": "profile_email",
        "profile_phone": "profile_phone",
        "profile_city": "profile_city",
        "profile_state": "profile_state",
        "profile_zip_code": "profile_zip_code",
        "profile_job_title": "profile_job_title",
    }

    def __init__(self, engine: RandomEngine, forge: "DataForge") -> None:
        super().__init__(engine)
        self._forge = forge

    # ------------------------------------------------------------------
    # Individual field methods (for _field_map / Schema compatibility)
    # These delegate to sub-providers — values are independent per call.
    # For coherent profiles, use profile() instead.
    # ------------------------------------------------------------------

    @overload
    def profile_first_name(self) -> str: ...
    @overload
    def profile_first_name(self, count: Literal[1]) -> str: ...
    @overload
    def profile_first_name(self, count: int) -> str | list[str]: ...
    def profile_first_name(self, count: int = 1) -> str | list[str]:
        """Generate a first name (delegates to PersonProvider).

        Parameters
        ----------
        count : int
            Number of names to generate.

        Returns
        -------
        str or list[str]
        """
        return self._forge.person.first_name(count)

    @overload
    def profile_last_name(self) -> str: ...
    @overload
    def profile_last_name(self, count: Literal[1]) -> str: ...
    @overload
    def profile_last_name(self, count: int) -> str | list[str]: ...
    def profile_last_name(self, count: int = 1) -> str | list[str]:
        """Generate a last name (delegates to PersonProvider).

        Parameters
        ----------
        count : int
            Number of names to generate.

        Returns
        -------
        str or list[str]
        """
        return self._forge.person.last_name(count)

    @overload
    def profile_email(self) -> str: ...
    @overload
    def profile_email(self, count: Literal[1]) -> str: ...
    @overload
    def profile_email(self, count: int) -> str | list[str]: ...
    def profile_email(self, count: int = 1) -> str | list[str]:
        """Generate an email address (delegates to InternetProvider).

        Parameters
        ----------
        count : int
            Number of emails to generate.

        Returns
        -------
        str or list[str]
        """
        return self._forge.internet.email(count)

    @overload
    def profile_phone(self) -> str: ...
    @overload
    def profile_phone(self, count: Literal[1]) -> str: ...
    @overload
    def profile_phone(self, count: int) -> str | list[str]: ...
    def profile_phone(self, count: int = 1) -> str | list[str]:
        """Generate a phone number (delegates to PhoneProvider).

        Parameters
        ----------
        count : int
            Number of phone numbers to generate.

        Returns
        -------
        str or list[str]
        """
        return self._forge.phone.phone_number(count)

    @overload
    def profile_city(self) -> str: ...
    @overload
    def profile_city(self, count: Literal[1]) -> str: ...
    @overload
    def profile_city(self, count: int) -> str | list[str]: ...
    def profile_city(self, count: int = 1) -> str | list[str]:
        """Generate a city name (delegates to AddressProvider).

        Parameters
        ----------
        count : int
            Number of cities to generate.

        Returns
        -------
        str or list[str]
        """
        return self._forge.address.city(count)

    @overload
    def profile_state(self) -> str: ...
    @overload
    def profile_state(self, count: Literal[1]) -> str: ...
    @overload
    def profile_state(self, count: int) -> str | list[str]: ...
    def profile_state(self, count: int = 1) -> str | list[str]:
        """Generate a state name (delegates to AddressProvider).

        Parameters
        ----------
        count : int
            Number of states to generate.

        Returns
        -------
        str or list[str]
        """
        return self._forge.address.state(count)

    @overload
    def profile_zip_code(self) -> str: ...
    @overload
    def profile_zip_code(self, count: Literal[1]) -> str: ...
    @overload
    def profile_zip_code(self, count: int) -> str | list[str]: ...
    def profile_zip_code(self, count: int = 1) -> str | list[str]:
        """Generate a zip code (delegates to AddressProvider).

        Parameters
        ----------
        count : int
            Number of zip codes to generate.

        Returns
        -------
        str or list[str]
        """
        return self._forge.address.zip_code(count)

    @overload
    def profile_job_title(self) -> str: ...
    @overload
    def profile_job_title(self, count: Literal[1]) -> str: ...
    @overload
    def profile_job_title(self, count: int) -> str | list[str]: ...
    def profile_job_title(self, count: int = 1) -> str | list[str]:
        """Generate a job title (delegates to CompanyProvider).

        Parameters
        ----------
        count : int
            Number of job titles to generate.

        Returns
        -------
        str or list[str]
        """
        return self._forge.company.job_title(count)

    # ------------------------------------------------------------------
    # Compound profile method (direct API only, not in _field_map)
    # ------------------------------------------------------------------

    def profile(self, count: int = 1) -> dict[str, str] | list[dict[str, str]]:
        """Generate a coherent user profile.

        Each profile is a ``dict`` with keys: ``first_name``,
        ``last_name``, ``email``, ``phone``, ``city``, ``state``,
        ``zip_code``, ``job_title``.

        The ``email`` is derived from the same first/last name for
        coherence within each profile.

        Parameters
        ----------
        count : int
            Number of profiles to generate.

        Returns
        -------
        dict[str, str] or list[dict[str, str]]
        """

        def _one_profile() -> dict[str, str]:
            first = self._forge.person.first_name()
            last = self._forge.person.last_name()
            # Build a coherent email from the person's name
            domain = self._forge.internet.domain()
            email = f"{first.lower()}.{last.lower()}@{domain}"
            return {
                "first_name": first,
                "last_name": last,
                "email": email,
                "phone": self._forge.phone.phone_number(),
                "city": self._forge.address.city(),
                "state": self._forge.address.state(),
                "zip_code": self._forge.address.zip_code(),
                "job_title": self._forge.company.job_title(),
            }

        if count == 1:
            return _one_profile()
        return [_one_profile() for _ in range(count)]
