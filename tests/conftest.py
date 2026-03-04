"""Shared fixtures for the dataforge test suite."""

import pytest

from dataforge import DataForge


@pytest.fixture
def forge() -> DataForge:
    """Seeded DataForge instance for deterministic tests."""
    return DataForge(locale="en_US", seed=42)


@pytest.fixture
def unseeded_forge() -> DataForge:
    """Unseeded DataForge instance for randomness tests."""
    return DataForge(locale="en_US")
