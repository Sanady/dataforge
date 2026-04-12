"""Field transform pipeline — composable post-generation transforms.

Provides ``pipe()`` to chain transforms and a library of built-in transforms
for common data manipulation tasks (casing, truncation, hashing, etc.).

Usage::

    from dataforge.transforms import pipe, upper, truncate, maybe_null

    forge = DataForge(seed=42)
    schema = forge.schema({
        "name": pipe("full_name", upper),
        "bio": pipe("sentence", truncate(50)),
        "email": pipe("email", maybe_null(0.2)),
    })
"""

from __future__ import annotations

import base64 as _b64
import hashlib as _hashlib
import random as _rng
import re as _re
from typing import Any, Callable

# Type alias for a transform function: str → str (or Any → Any)
Transform = Callable[[Any], Any]

# Pre-compiled regex patterns for snake_case (avoids re-compiling per call)
_SNAKE_RE1 = _re.compile(r"([A-Z]+)([A-Z][a-z])")
_SNAKE_RE2 = _re.compile(r"([a-z0-9])([A-Z])")
_SNAKE_RE3 = _re.compile(r"[\s\-]+")

# Pre-compiled regex pattern for camel_case
_CAMEL_SPLIT = _re.compile(r"[\s_\-]+")


def pipe(field: str, *transforms: Transform) -> dict[str, Any]:
    """Create a field spec with a transform pipeline.

    Parameters
    ----------
    field : str
        The DataForge field name to generate.
    *transforms : callable
        One or more ``(value) -> value`` callables applied in order.

    Returns
    -------
    dict
        A dict spec suitable for use in ``forge.schema({...})``.
    """
    chain = tuple(transforms)

    def _apply(row: dict[str, Any]) -> Any:
        val = row.get(f"__pipe_{field}")
        for fn in chain:
            val = fn(val)
        return val

    return {
        "field": field,
        "_pipe_transforms": chain,
    }


# ---------------------------------------------------------------------------
# Built-in transforms
# ---------------------------------------------------------------------------


def upper(value: Any) -> str:
    """Convert to uppercase."""
    return str(value).upper()


def lower(value: Any) -> str:
    """Convert to lowercase."""
    return str(value).lower()


def snake_case(value: Any) -> str:
    """Convert to snake_case (e.g. ``"Hello World"`` → ``"hello_world"``)."""
    s = str(value).strip()
    s = _SNAKE_RE1.sub(r"\1_\2", s)
    s = _SNAKE_RE2.sub(r"\1_\2", s)
    s = _SNAKE_RE3.sub("_", s)
    return s.lower()


def camel_case(value: Any) -> str:
    """Convert to camelCase (e.g. ``"hello world"`` → ``"helloWorld"``)."""
    s = str(value).strip()
    parts = _CAMEL_SPLIT.split(s)
    if not parts:
        return ""
    return parts[0].lower() + "".join(p.capitalize() for p in parts[1:])


def kebab_case(value: Any) -> str:
    """Convert to kebab-case (e.g. ``"Hello World"`` → ``"hello-world"``)."""
    return snake_case(value).replace("_", "-")


def title_case(value: Any) -> str:
    """Convert to Title Case."""
    return str(value).title()


def truncate(max_len: int, suffix: str = "...") -> Transform:
    """Return a transform that truncates to *max_len* characters.

    Parameters
    ----------
    max_len : int
        Maximum length of the output string.
    suffix : str
        Appended when the string is truncated (default ``"..."``).
    """

    def _trunc(value: Any) -> str:
        s = str(value)
        if len(s) <= max_len:
            return s
        cut = max_len - len(suffix)
        return s[:cut] + suffix if cut > 0 else s[:max_len]

    return _trunc


def maybe_null(probability: float = 0.1) -> Transform:
    """Return a transform that replaces the value with ``None`` randomly.

    Parameters
    ----------
    probability : float
        Chance of returning ``None`` (0.0–1.0).
    """
    _random = _rng.random

    def _null(value: Any) -> Any:
        return None if _random() < probability else value

    return _null


def hash_with(algorithm: str = "sha256") -> Transform:
    """Return a transform that hashes the value with the given algorithm.

    Parameters
    ----------
    algorithm : str
        Hash algorithm name (e.g. ``"sha256"``, ``"md5"``).
    """
    _proto = _hashlib.new(algorithm)

    def _hash(value: Any) -> str:
        h = _proto.copy()
        h.update(str(value).encode())
        return h.hexdigest()

    return _hash


def encode_b64(value: Any) -> str:
    """Base64-encode the value."""
    return _b64.b64encode(str(value).encode()).decode()


def decode_b64(value: Any) -> str:
    """Base64-decode the value."""
    return _b64.b64decode(str(value).encode()).decode()


def redact(char: str = "*", keep_start: int = 0, keep_end: int = 0) -> Transform:
    """Return a transform that redacts the value, optionally preserving edges.

    Parameters
    ----------
    char : str
        Replacement character (default ``"*"``).
    keep_start : int
        Number of characters to keep at the start.
    keep_end : int
        Number of characters to keep at the end.
    """

    def _redact(value: Any) -> str:
        s = str(value)
        total = len(s)
        if keep_start + keep_end >= total:
            return s
        mid_len = total - keep_start - keep_end
        if keep_end > 0:
            return s[:keep_start] + char * mid_len + s[-keep_end:]
        return s[:keep_start] + char * mid_len

    return _redact


def apply_if(condition: Callable[[Any], bool], transform: Transform) -> Transform:
    """Apply *transform* only when *condition(value)* is ``True``."""

    def _cond(value: Any) -> Any:
        return transform(value) if condition(value) else value

    return _cond


def prefix(pre: str) -> Transform:
    """Return a transform that prepends *pre* to the value."""

    def _prefix(value: Any) -> str:
        return pre + str(value)

    return _prefix


def suffix(suf: str) -> Transform:
    """Return a transform that appends *suf* to the value."""

    def _suffix(value: Any) -> str:
        return str(value) + suf

    return _suffix


def wrap(before: str, after: str) -> Transform:
    """Return a transform that wraps the value with *before* and *after*."""

    def _wrap(value: Any) -> str:
        return before + str(value) + after

    return _wrap


def replace(old: str, new: str) -> Transform:
    """Return a transform that replaces occurrences of *old* with *new*."""

    def _replace(value: Any) -> str:
        return str(value).replace(old, new)

    return _replace


def strip(value: Any) -> str:
    """Strip leading and trailing whitespace."""
    return str(value).strip()
