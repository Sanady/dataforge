"""Faker compatibility layer — drop-in replacement powered by DataForge.

Provides a ``Faker`` class that mimics the ``faker.Faker`` API while
delegating all data generation to DataForge's high-performance engine.

Usage::

    from dataforge.compat import Faker

    fake = Faker()
    fake.name()
    fake.email()
    fake.address()

    # Multi-locale
    fake = Faker(["en_US", "ja_JP"])
    fake.name()  # mixes locales randomly

    # Seeding
    Faker.seed(42)
    fake.seed_instance(42)
"""

from __future__ import annotations

from typing import Any

from dataforge.core import DataForge, _FIELD_ALIASES


# Mapping from common Faker method names to DataForge field shorthand names.
# Faker uses slightly different naming conventions than DataForge.
_FAKER_METHOD_MAP: dict[str, str] = {
    # Faker name → DataForge field
    "name": "full_name",
    "first_name": "first_name",
    "last_name": "last_name",
    "prefix": "prefix",
    "suffix": "suffix",
    "address": "full_address",
    "street_address": "street_address",
    "city": "city",
    "state": "state",
    "state_abbr": "state",
    "zipcode": "zip_code",
    "postcode": "zip_code",
    "country": "country",
    "email": "email",
    "safe_email": "email",
    "free_email": "email",
    "company_email": "email",
    "phone_number": "phone_number",
    "ssn": "ssn",
    "company": "company_name",
    "bs": "company_name",
    "catch_phrase": "company_name",
    "job": "job_title",
    "text": "paragraph",
    "sentence": "sentence",
    "word": "word",
    "paragraph": "paragraph",
    "paragraphs": "paragraph",
    "url": "url",
    "domain_name": "domain",
    "user_name": "username",
    "ipv4": "ipv4",
    "ipv6": "ipv6",
    "mac_address": "mac_address",
    "user_agent": "user_agent",
    "credit_card_number": "credit_card_number",
    "credit_card_provider": "card_type",
    "iban": "iban",
    "uuid4": "uuid4",
    "boolean": "boolean",
    "date": "date",
    "date_of_birth": "date_of_birth",
    "time": "time",
    "date_time": "datetime",
    "iso8601": "datetime",
    "color_name": "color_name",
    "hex_color": "hex_color",
    "rgb_color": "rgb_color",
    "file_name": "file_name",
    "file_extension": "file_extension",
    "mime_type": "mime_type",
    "latitude": "latitude",
    "longitude": "longitude",
    "ean13": "ean13",
    "isbn13": "isbn13",
}

_GLOBAL_SEED: int | None = None


class Faker:
    """Drop-in replacement for ``faker.Faker`` backed by DataForge.

    Parameters
    ----------
    locale : str or list[str], optional
        A locale or list of locales. Default is ``"en_US"``.
    seed : int or None, optional
        Random seed for reproducible output.
    """

    __slots__ = ("_forge", "_method_cache")

    def __init__(
        self,
        locale: str | list[str] = "en_US",
        *,
        seed: int | None = None,
    ) -> None:
        effective_seed = seed if seed is not None else _GLOBAL_SEED
        self._forge = DataForge(locale=locale, seed=effective_seed)
        self._method_cache: dict[str, Any] = {}

    # --- Faker-compatible seeding API ---

    @staticmethod
    def seed(value: int) -> None:
        """Set the global seed (like ``faker.Faker.seed()``)."""
        global _GLOBAL_SEED
        _GLOBAL_SEED = value

    def seed_instance(self, value: int) -> None:
        """Re-seed this instance's random engine."""
        self._forge.seed(value)

    def seed_locale(self, locale: str, value: int) -> None:
        """Seed a specific locale (no-op in DataForge, for API compat)."""
        self._forge.seed(value)

    # --- Dynamic method resolution ---

    def _resolve_method(self, name: str) -> Any:
        """Resolve a Faker-style method name to a DataForge callable."""
        cached = self._method_cache.get(name)
        if cached is not None:
            return cached

        # Build candidates list: Faker map → core aliases → direct name
        # Iterate once with a single try/except per candidate.
        forge = self._forge
        _resolve = forge._resolve_field
        _getattr = getattr
        candidates = (
            _FAKER_METHOD_MAP.get(name),
            _FIELD_ALIASES.get(name),
            name,
        )
        for candidate in candidates:
            if candidate is None:
                continue
            try:
                prov_attr, method = _resolve(candidate)
                fn = _getattr(_getattr(forge, prov_attr), method)
                self._method_cache[name] = fn
                return fn
            except (ValueError, AttributeError):
                continue

        raise AttributeError(
            f"Faker compatibility layer has no method '{name}'. "
            f"This method may not have a DataForge equivalent."
        )

    def __getattr__(self, name: str) -> Any:
        return self._resolve_method(name)

    def __repr__(self) -> str:
        return f"Faker(locale={self._forge.locale!r})"
