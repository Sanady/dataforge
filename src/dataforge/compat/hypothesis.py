"""Hypothesis strategy bridge — use DataForge fields as Hypothesis strategies.

Requires ``hypothesis`` to be installed (optional dependency).

Usage::

    from dataforge.compat.hypothesis import strategy, forge_strategy

    # Single field strategy
    @given(email=strategy("email"))
    def test_email(email):
        assert "@" in email

    # Multi-field strategy (returns dicts)
    @given(data=forge_strategy(["first_name", "email", "city"]))
    def test_user(data):
        assert "first_name" in data
"""

from __future__ import annotations

from typing import Any


def _import_hypothesis_st() -> Any:
    """Import and return ``hypothesis.strategies``, raising a clear error if missing."""
    try:
        from hypothesis import strategies as st
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "hypothesis is required for DataForge's Hypothesis bridge. "
            "Install it with: pip install hypothesis"
        ) from exc
    return st


def strategy(
    field: str,
    locale: str = "en_US",
    **kwargs: Any,
) -> Any:
    """Create a Hypothesis ``SearchStrategy`` from a DataForge field name.

    Parameters
    ----------
    field : str
        A DataForge field name (e.g. ``"email"``, ``"first_name"``).
    locale : str
        Locale for data generation (default ``"en_US"``).

    Returns
    -------
    hypothesis.strategies.SearchStrategy
        A strategy that yields values from the specified field.
    """
    st = _import_hypothesis_st()

    from dataforge.core import DataForge

    # Resolve the field callable once at strategy creation time
    # so we only pay the lookup cost once, not per draw.
    probe_forge = DataForge(locale=locale, seed=0)
    prov_attr, method_name = probe_forge._resolve_field(field)

    @st.composite
    def _field_strategy(draw: Any) -> Any:
        seed = draw(st.integers(min_value=0, max_value=2**31 - 1))
        forge = DataForge(locale=locale, seed=seed)
        provider = getattr(forge, prov_attr)
        fn = getattr(provider, method_name)
        return fn(**kwargs)

    return _field_strategy()


def forge_strategy(
    fields: list[str] | dict[str, str],
    locale: str = "en_US",
) -> Any:
    """Create a Hypothesis ``SearchStrategy`` that yields dicts from a DataForge schema.

    Parameters
    ----------
    fields : list or dict
        Field names or column→field mapping.
    locale : str
        Locale for data generation (default ``"en_US"``).

    Returns
    -------
    hypothesis.strategies.SearchStrategy
        A strategy that yields ``dict[str, Any]`` matching the schema.
    """
    st = _import_hypothesis_st()

    from dataforge.core import DataForge

    @st.composite
    def _schema_strategy(draw: Any) -> dict[str, Any]:
        seed = draw(st.integers(min_value=0, max_value=2**31 - 1))
        forge = DataForge(locale=locale, seed=seed)
        schema = forge.schema(fields)
        rows = schema.generate(count=1)
        return rows[0]

    return _schema_strategy()
