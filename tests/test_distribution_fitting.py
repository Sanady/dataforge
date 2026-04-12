"""Tests for Feature 10: Statistical Distribution Fitting."""

import random

import pytest

from dataforge import DataForge
from dataforge.inference import (
    ColumnAnalysis,
    SchemaInferrer,
    _fit_distribution,
)


# ── Parametrized distribution detection ─────────────────────────────────


def _normal_data(rng: random.Random) -> list[float]:
    return [rng.gauss(100, 15) for _ in range(500)]


def _exponential_data(rng: random.Random) -> list[float]:
    return [rng.expovariate(0.5) for _ in range(500)]


def _beta_data(rng: random.Random) -> list[float]:
    return [rng.betavariate(2, 5) for _ in range(500)]


def _zipf_data(rng: random.Random) -> list[int]:
    values = []
    for _ in range(500):
        u = rng.random()
        val = int(1.0 / (u**0.5))
        values.append(max(1, val))
    return values


_DIST_CASES = [
    # (generator_fn, dtype, expected_names)
    (_normal_data, "float", {"normal", "lognormal"}),
    (_exponential_data, "float", {"exponential", "lognormal"}),
    (_beta_data, "float", {"beta", "normal", "lognormal"}),
    (_zipf_data, "int", {"zipf", "exponential", "lognormal", "normal"}),
]


class TestFitDistribution:
    @pytest.mark.parametrize(
        "gen_fn, dtype, expected_names",
        _DIST_CASES,
        ids=["normal", "exponential", "beta", "zipf"],
    )
    def test_distribution_detection(
        self,
        gen_fn: object,
        dtype: str,
        expected_names: set[str],
    ) -> None:
        rng = random.Random(42)
        values = gen_fn(rng)  # type: ignore[operator]
        result = _fit_distribution(values, dtype)
        assert result is not None
        assert result["name"] in expected_names

    def test_normal_params_reasonable(self) -> None:
        rng = random.Random(42)
        values = [rng.gauss(100, 15) for _ in range(500)]
        result = _fit_distribution(values, "float")
        assert result is not None
        if result["name"] == "normal":
            assert abs(result["params"]["mean"] - 100) < 5
            assert abs(result["params"]["std"] - 15) < 5

    @pytest.mark.parametrize(
        "values, dtype",
        [
            (["a", "b", "c"], "str"),
            ([1, 2, 3], "int"),
            ([5.0] * 100, "float"),
        ],
        ids=["string_type", "too_few", "constant"],
    )
    def test_returns_none(self, values: list, dtype: str) -> None:
        assert _fit_distribution(values, dtype) is None

    def test_none_values_skipped(self) -> None:
        rng = random.Random(42)
        values: list = [rng.gauss(50, 10) for _ in range(100)]
        values += [None] * 20
        result = _fit_distribution(values, "float")
        assert result is not None


# ── ColumnAnalysis ──────────────────────────────────────────────────────

_CA_REPR_CASES = [
    # (distribution, check_contains, check_not_contains)
    (None, "col", "dist="),
    ({"name": "normal", "params": {"mean": 0, "std": 1}}, "dist=normal", None),
]


class TestColumnAnalysis:
    def test_slots(self) -> None:
        ca = ColumnAnalysis("col", "str", None, 0.0, {}, None)
        assert ca.name == "col"
        assert ca.distribution is None

    @pytest.mark.parametrize(
        "distribution, check_in, check_not_in",
        _CA_REPR_CASES,
        ids=["no_dist", "with_dist"],
    )
    def test_repr(
        self,
        distribution: dict | None,
        check_in: str,
        check_not_in: str | None,
    ) -> None:
        kwargs = {"distribution": distribution} if distribution else {}
        ca = ColumnAnalysis(
            "col", "float" if distribution else "str", None, 0.0, {}, None, **kwargs
        )
        r = repr(ca)
        assert check_in in r
        if check_not_in:
            assert check_not_in not in r


class TestSchemaInferrerDistribution:
    def test_infer_adds_distribution(self) -> None:
        """Numeric columns in inferred schemas should have distribution info."""
        rng = random.Random(42)
        records = [
            {
                "name": f"Person{i}",
                "email": f"p{i}@test.com",
                "score": rng.gauss(50, 10),
            }
            for i in range(100)
        ]
        forge = DataForge(seed=42)
        inferrer = SchemaInferrer(forge)
        inferrer.from_records(records)

        analyses = inferrer.analyses
        score_analysis = next((a for a in analyses if a.name == "score"), None)
        assert score_analysis is not None
        assert score_analysis.distribution is not None
        assert score_analysis.distribution["name"] in (
            "normal",
            "lognormal",
            "exponential",
            "beta",
            "zipf",
        )

    def test_describe_shows_distribution(self) -> None:
        """describe() should mention distribution when present."""
        rng = random.Random(42)
        records = [
            {
                "email": f"p{i}@test.com",
                "value": rng.gauss(0, 1),
            }
            for i in range(100)
        ]
        forge = DataForge(seed=42)
        inferrer = SchemaInferrer(forge)
        inferrer.from_records(records)
        desc = inferrer.describe()
        assert "distribution:" in desc
