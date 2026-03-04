"""Base provider — shared foundation for all data providers."""

from dataforge.backend import RandomEngine


class BaseProvider:
    """Abstract base for all dataforge providers.

    Holds a reference to the shared :class:`RandomEngine` so every
    provider can generate random values without owning its own RNG
    state.

    Subclasses should define class-level metadata for the provider
    registry:

    - ``_provider_name``: short name used as attribute on ``DataForge``
      (e.g. ``"person"``, ``"address"``).
    - ``_locale_modules``: tuple of locale module names needed to
      construct this provider (e.g. ``("person",)``).  Empty tuple
      ``()`` for locale-independent providers.
    - ``_field_map``: dict mapping shorthand field names to method
      names (e.g. ``{"first_name": "first_name", "name": "full_name"}``).
    """

    __slots__ = ("_engine",)

    # Registry metadata — subclasses override these
    _provider_name: str = ""
    _locale_modules: tuple[str, ...] = ()
    _field_map: dict[str, str] = {}
    _needs_forge: bool = False

    def __init__(self, engine: RandomEngine) -> None:
        self._engine = engine
