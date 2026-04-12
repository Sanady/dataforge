"""Tests for Feature 10: Statistical Distribution Fitting."""

import math
import random

from dataforge import DataForge
from dataforge.inference import (
    ColumnAnalysis,
    SchemaInferrer,
    _fit_distribution,
)


class TestFitDistribution:
    def test_returns_none_for_string_type(self) -> None:
        assert _fit_distribution(["a", "b", "c"], "str") is None

    def test_returns_none_for_too_few_values(self) -> None:
        assert _fit_distribution([1, 2, 3], "int") is None

    def test_normal_detection(self) -> None:
        rng = random.Random(42)
        values = [rng.gauss(100, 15) for _ in range(500)]
        result = _fit_distribution(values, "float")
        assert result is not None
        assert result["name"] in ("normal", "lognormal")
        # If normal, check params
        if result["name"] == "normal":
            assert abs(result["params"]["mean"] - 100) < 5
            assert abs(result["params"]["std"] - 15) < 5

    def test_exponential_detection(self) -> None:
        rng = random.Random(42)
        values = [rng.expovariate(0.5) for _ in range(500)]
        result = _fit_distribution(values, "float")
        assert result is not None
        # Exponential data should be detected as exponential or lognormal
        assert result["name"] in ("exponential", "lognormal")

    def test_beta_detection(self) -> None:
        rng = random.Random(42)
        values = [rng.betavariate(2, 5) for _ in range(500)]
        result = _fit_distribution(values, "float")
        assert result is not None
        # Beta values are in (0,1) range
        assert result["name"] in ("beta", "normal", "lognormal")

    def test_none_values_skipped(self) -> None:
        rng = random.Random(42)
        values = [rng.gauss(50, 10) for _ in range(100)]
        values += [None] * 20
        result = _fit_distribution(values, "float")
        # Should still work, ignoring None values
        assert result is not None

    def test_constant_values_returns_none(self) -> None:
        values = [5.0] * 100
        result = _fit_distribution(values, "float")
        assert result is None  # std = 0, no distribution


class TestColumnAnalysis:
    def test_slots(self) -> None:
        ca = ColumnAnalysis("col", "str", None, 0.0, {}, None)
        assert ca.name == "col"
        assert ca.distribution is None

    def test_repr_without_distribution(self) -> None:
        ca = ColumnAnalysis("col", "str", None, 0.0, {}, None)
        r = repr(ca)
        assert "col" in r
        assert "dist=" not in r

    def test_repr_with_distribution(self) -> None:
        dist = {"name": "normal", "params": {"mean": 0, "std": 1}}
        ca = ColumnAnalysis("col", "float", None, 0.0, {}, None, distribution=dist)
        r = repr(ca)
        assert "dist=normal" in r


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


class TestZipfDetection:
    def test_zipf_integer_data(self) -> None:
        """Zipf-distributed integer data should be detected."""
        rng = random.Random(42)
        # Generate Zipf-like data: many 1s, fewer 2s, even fewer 3s...
        values = []
        for _ in range(500):
            # Simple Zipf approximation
            u = rng.random()
            val = int(1.0 / (u**0.5))  # roughly Zipf with s≈2
            values.append(max(1, val))

        result = _fit_distribution(values, "int")
        # Should detect some distribution (might be zipf, exponential, etc.)
        assert result is not None
