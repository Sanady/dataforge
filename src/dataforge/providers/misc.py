"""MiscProvider — utility generators for common testing needs.

All methods are locale-independent and optimized for speed.
"""

import time as _time
from typing import Any, Literal, overload

from dataforge.providers.base import BaseProvider

# Pre-computed bit-mask constants for UUID version/variant setting.
# Combined masks reduce 4 bitmask ops to 2 per UUID generation.
_UUID4_CLEAR = ~(0xF << 76) & ~(0x3 << 62)  # clear version + variant in one AND
_UUID4_SET = (0x4 << 76) | (0x2 << 62)  # set version 4 + variant 1 in one OR


class MiscProvider(BaseProvider):
    """Generates UUIDs, booleans, and utility random selections.

    This provider is locale-independent.

    Parameters
    ----------
    engine : RandomEngine
        The shared random engine instance.
    """

    __slots__ = ()

    _provider_name = "misc"
    _locale_modules = ()
    _field_map = {
        "uuid4": "uuid4",
        "uuid": "uuid4",
        "uuid7": "uuid7",
        "boolean": "boolean",
    }

    # ------------------------------------------------------------------
    # Scalar helpers
    # ------------------------------------------------------------------

    def _one_uuid4(self) -> str:
        # 128 random bits → set version 4 and variant 1 with 2 ops
        n = (self._engine._rng.getrandbits(128) & _UUID4_CLEAR) | _UUID4_SET
        h = f"{n:032x}"
        return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:]}"

    def _one_uuid7(self) -> str:
        # 48-bit millisecond Unix timestamp
        ts_ms = int(_time.time() * 1000) & 0xFFFF_FFFF_FFFF
        # 74 random bits (12 + 62) from the seeded RNG
        rand_bits = self._engine._rng.getrandbits(74)
        rand_a = (rand_bits >> 62) & 0xFFF  # 12 bits
        rand_b = rand_bits & 0x3FFF_FFFF_FFFF_FFFF  # 62 bits
        # Assemble 128-bit UUID7 as a single int
        n = (ts_ms << 80) | (0x7 << 76) | (rand_a << 64) | (0x2 << 62) | rand_b
        h = f"{n:032x}"
        return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:]}"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @overload
    def uuid4(self) -> str: ...
    @overload
    def uuid4(self, count: Literal[1]) -> str: ...
    @overload
    def uuid4(self, count: int) -> str | list[str]: ...
    def uuid4(self, count: int = 1) -> str | list[str]:
        """Generate a random UUID4 string.

        Uses direct hex formatting from ``getrandbits(128)`` with
        version/variant bits set arithmetically — avoids ``bytearray``,
        ``bytes``, and ``uuid.UUID()`` constructor overhead entirely.

        Parameters
        ----------
        count : int
            Number of UUIDs to generate.
        """
        if count == 1:
            return self._one_uuid4()
        rng_bits = self._engine._rng.getrandbits
        result: list[str] = []
        _clr = _UUID4_CLEAR
        _set = _UUID4_SET
        for _ in range(count):
            n = (rng_bits(128) & _clr) | _set
            h = f"{n:032x}"
            result.append(f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:]}")
        return result

    @overload
    def uuid7(self) -> str: ...
    @overload
    def uuid7(self, count: Literal[1]) -> str: ...
    @overload
    def uuid7(self, count: int) -> str | list[str]: ...
    def uuid7(self, count: int = 1) -> str | list[str]:
        """Generate a random UUID7 string (time-ordered, monotonic).

        UUID7 (RFC 9562) embeds a millisecond-precision Unix timestamp
        in the first 48 bits, making the values naturally sortable by
        creation time — ideal for database primary keys.

        The timestamp uses real wall-clock time for time-ordering.
        The random portion uses the shared engine RNG, so output is
        deterministic when a seed is set (only the random bits are
        reproducible; the timestamp reflects actual generation time).

        Uses direct hex formatting — avoids ``to_bytes``, ``bytearray``,
        and ``uuid.UUID()`` constructor overhead entirely.

        Parameters
        ----------
        count : int
            Number of UUIDs to generate.

        Returns
        -------
        str or list[str]

        .. versionadded:: 1.1.0
            Custom RFC 9562 implementation — no stdlib ``uuid.uuid7()``
            dependency.  Works on Python >= 3.12.
        """
        if count == 1:
            return self._one_uuid7()
        rng_bits = self._engine._rng.getrandbits
        _time_time = _time.time
        result: list[str] = []
        for _ in range(count):
            ts_ms = int(_time_time() * 1000) & 0xFFFF_FFFF_FFFF
            rand_bits = rng_bits(74)
            rand_a = (rand_bits >> 62) & 0xFFF
            rand_b = rand_bits & 0x3FFF_FFFF_FFFF_FFFF
            n = (ts_ms << 80) | (0x7 << 76) | (rand_a << 64) | (0x2 << 62) | rand_b
            h = f"{n:032x}"
            result.append(f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:]}")
        return result

    def boolean(self, count: int = 1, probability: float = 0.5) -> bool | list[bool]:
        """Generate a random boolean.

        Parameters
        ----------
        count : int
            Number of booleans to generate.
        probability : float
            Probability of ``True`` (0.0–1.0). Default 0.5.
        """
        rng = self._engine._rng
        if count == 1:
            return rng.random() < probability
        return [rng.random() < probability for _ in range(count)]

    def random_element(
        self, elements: tuple[Any, ...] | list[Any], count: int = 1
    ) -> Any:
        """Pick random element(s) from a user-provided collection.

        Parameters
        ----------
        elements : tuple or list
            The items to choose from.
        count : int
            Number of items to pick.

        Returns
        -------
        Any or list[Any]
        """
        data = tuple(elements) if isinstance(elements, list) else elements
        if count == 1:
            return self._engine.choice(data)
        return self._engine.choices(data, count)

    def null_or(self, value: Any, probability: float = 0.1) -> Any:
        """Return ``None`` with *probability*, otherwise return *value*.

        Parameters
        ----------
        value : Any
            The value to return when not null.
        probability : float
            Probability of returning ``None`` (0.0–1.0).

        Returns
        -------
        Any
        """
        if self._engine._rng.random() < probability:
            return None
        return value
