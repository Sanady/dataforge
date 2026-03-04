"""pytest plugin — auto-provides ``forge`` and ``fake`` fixtures.

Registers automatically when ``dataforge`` is installed thanks to
the ``pytest11`` entry point.  Users can also load it manually via
``pytest_plugins = ["dataforge.pytest_plugin"]``.

Fixtures
--------
forge
    A seeded ``DataForge`` instance (seed=0) for deterministic tests.
    Override the seed via the ``--forge-seed`` CLI option or the
    ``forge_seed`` marker::

        @pytest.mark.forge_seed(42)
        def test_something(forge):
            assert forge.person.first_name() == "James"

fake
    Alias for ``forge`` — convenient shorthand.

forge_unseeded
    An unseeded ``DataForge`` instance for non-deterministic tests.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from dataforge import DataForge

if TYPE_CHECKING:
    pass


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add ``--forge-seed`` command-line option."""
    parser.addoption(
        "--forge-seed",
        type=int,
        default=0,
        help="Default seed for the ``forge`` fixture (default: 0)",
    )


@pytest.fixture
def forge(request: pytest.FixtureRequest) -> DataForge:
    """Seeded ``DataForge`` instance for deterministic tests.

    The seed defaults to 0 or the value of ``--forge-seed``.
    Override per-test with ``@pytest.mark.forge_seed(N)``.
    """
    # Per-test marker takes priority
    marker = request.node.get_closest_marker("forge_seed")
    if marker is not None:
        seed = marker.args[0]
    else:
        seed = request.config.getoption("--forge-seed", default=0)
    return DataForge(seed=seed)


@pytest.fixture
def fake(forge: DataForge) -> DataForge:
    """Alias for the ``forge`` fixture."""
    return forge


@pytest.fixture
def forge_unseeded() -> DataForge:
    """Unseeded ``DataForge`` instance (non-deterministic)."""
    return DataForge()


def pytest_configure(config: pytest.Config) -> None:
    """Register the ``forge_seed`` marker."""
    config.addinivalue_line(
        "markers",
        "forge_seed(seed): Set the seed for the ``forge`` fixture",
    )
