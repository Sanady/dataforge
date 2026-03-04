"""RandomEngine — the speed engine behind dataforge.

Provides a unified interface for random selection using stdlib
``random`` — optimised for both scalar picks and batch generation.
"""

import random as _random
from typing import TypeVar

_T = TypeVar("_T")

# Pre-computed power-of-10 table for random_digits_str — eliminates
# per-call ``10**n`` computation for n=1..18.
_POW10: tuple[int, ...] = tuple(10**i for i in range(19))  # _POW10[0]=1 .. _POW10[18]


class RandomEngine:
    """Core randomness engine.

    Parameters
    ----------
    seed : int | None
        Optional seed for reproducibility.
    """

    __slots__ = ("_rng",)

    def __init__(self, seed: int | None = None) -> None:
        self._rng: _random.Random = _random.Random(seed)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def choice(self, data: tuple[_T, ...]) -> _T:
        """Return a single random element from *data*.

        Uses stdlib ``random.Random.choice`` which is the fastest path
        for picking one item.
        """
        return self._rng.choice(data)

    def choices(self, data: tuple[_T, ...], count: int) -> list[_T]:
        """Return *count* random elements from *data*."""
        return self._rng.choices(data, k=count)

    def random_int(self, min_val: int = 0, max_val: int = 9999) -> int:
        """Return a random integer between *min_val* and *max_val* inclusive."""
        return self._rng.randint(min_val, max_val)

    def numerify(self, pattern: str) -> str:
        """Replace every ``#`` in *pattern* with a random digit.

        Example: ``"#####"`` → ``"38201"``

        Optimized: if the pattern is all ``#`` characters, generates
        all digits in a single call via :meth:`random_digits_str`.
        For mixed patterns, pre-counts ``#`` and generates all digits
        in one bulk call, then substitutes via iterator.
        """
        # Fast path: pattern is entirely # characters (very common).
        # Use length check instead of iterating all characters with all().
        hash_count = pattern.count("#")
        if hash_count == len(pattern):
            return self.random_digits_str(hash_count)
        if hash_count == 0:
            return pattern
        # Slow path optimized: generate all digits in one call, then
        # substitute via iterator — avoids N random_digit() calls.
        digits = self.random_digits_str(hash_count)
        it = iter(digits)
        return "".join(next(it) if ch == "#" else ch for ch in pattern)

    def getrandbits(self, k: int) -> int:
        """Return a random integer with *k* random bits.

        This is the fastest way to generate a large block of randomness
        in a single call — used by providers that need to build strings
        from many random hex/decimal digits (IPv6, MAC, barcodes, etc.).
        """
        return self._rng.getrandbits(k)

    def random_digits_str(self, n: int) -> str:
        """Return a string of *n* random decimal digits.

        Uses a pre-computed ``_POW10`` lookup table to avoid per-call
        ``10**n`` computation.  For small n (≤ 18), a single
        ``randint`` call is the fastest path.
        """
        _pow10 = _POW10
        if n <= 18:
            val = self._rng.randint(0, _pow10[n] - 1)
            return str(val).zfill(n)
        # For larger n, concatenate chunks of 18 digits
        parts: list[str] = []
        remaining = n
        _max18 = _pow10[18] - 1
        _randint = self._rng.randint
        while remaining > 0:
            chunk = min(remaining, 18)
            val = _randint(0, _pow10[chunk] - 1)
            parts.append(str(val).zfill(chunk))
            remaining -= chunk
        return "".join(parts)

    def seed(self, value: int) -> None:
        """Re-seed the engine for reproducibility."""
        self._rng.seed(value)

    def weighted_choices(
        self,
        data: tuple[_T, ...],
        weights: tuple[float, ...] | list[float],
        count: int,
    ) -> list[_T]:
        """Return *count* random elements from *data* with *weights*.

        Each element in *data* is selected with probability proportional
        to its corresponding weight.

        Parameters
        ----------
        data : tuple
            The items to choose from.
        weights : tuple[float, ...] or list[float]
            Non-negative weights (need not sum to 1).
        count : int
            Number of items to pick.

        Returns
        -------
        list
        """
        # Accept both tuple and list directly — stdlib choices() handles
        # both; avoid redundant list() conversion.
        return self._rng.choices(data, weights=weights, k=count)

    def weighted_choice(
        self,
        data: tuple[_T, ...],
        weights: tuple[float, ...] | list[float],
    ) -> _T:
        """Return a single random element from *data* with *weights*.

        Scalar version of :meth:`weighted_choices`.
        """
        return self._rng.choices(data, weights=weights, k=1)[0]
