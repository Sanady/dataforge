"""Tests for the ScienceProvider."""

from dataforge import DataForge


class TestChemicalElement:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_returns_str(self) -> None:
        assert isinstance(self.forge.science.chemical_element(), str)

    def test_batch(self) -> None:
        results = self.forge.science.chemical_element(count=50)
        assert isinstance(results, list)
        assert len(results) == 50


class TestElementSymbol:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_returns_str(self) -> None:
        sym = self.forge.science.element_symbol()
        assert isinstance(sym, str)
        assert 1 <= len(sym) <= 2

    def test_batch(self) -> None:
        results = self.forge.science.element_symbol(count=50)
        assert len(results) == 50


class TestSIUnit:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_returns_str(self) -> None:
        unit = self.forge.science.si_unit()
        assert isinstance(unit, str)
        assert "(" in unit  # format: "meter (m)"

    def test_batch(self) -> None:
        results = self.forge.science.si_unit(count=50)
        assert len(results) == 50


class TestPlanet:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_returns_str(self) -> None:
        assert isinstance(self.forge.science.planet(), str)

    def test_valid(self) -> None:
        valid = {
            "Mercury",
            "Venus",
            "Earth",
            "Mars",
            "Jupiter",
            "Saturn",
            "Uranus",
            "Neptune",
        }
        for _ in range(50):
            assert self.forge.science.planet() in valid

    def test_batch(self) -> None:
        results = self.forge.science.planet(count=50)
        assert len(results) == 50


class TestGalaxy:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_returns_str(self) -> None:
        assert isinstance(self.forge.science.galaxy(), str)

    def test_batch(self) -> None:
        results = self.forge.science.galaxy(count=50)
        assert len(results) == 50


class TestConstellation:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_returns_str(self) -> None:
        assert isinstance(self.forge.science.constellation(), str)

    def test_batch(self) -> None:
        results = self.forge.science.constellation(count=50)
        assert len(results) == 50


class TestScientificDiscipline:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_returns_str(self) -> None:
        assert isinstance(self.forge.science.scientific_discipline(), str)

    def test_batch(self) -> None:
        results = self.forge.science.scientific_discipline(count=50)
        assert len(results) == 50


class TestMetricPrefix:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_returns_str(self) -> None:
        prefix = self.forge.science.metric_prefix()
        assert isinstance(prefix, str)
        assert "(" in prefix  # format: "kilo (k)"

    def test_batch(self) -> None:
        results = self.forge.science.metric_prefix(count=50)
        assert len(results) == 50


class TestScienceInSchema:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_schema_fields(self) -> None:
        rows = self.forge.to_dict(
            fields=["element", "planet", "constellation"],
            count=5,
        )
        assert len(rows) == 5
        for row in rows:
            assert "element" in row
            assert "planet" in row
            assert "constellation" in row
