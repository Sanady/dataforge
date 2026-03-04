"""Science provider — elements, units, formulas, planets, etc."""

from typing import Literal, overload

from dataforge.providers.base import BaseProvider

_CHEMICAL_ELEMENTS: tuple[str, ...] = (
    "Hydrogen",
    "Helium",
    "Lithium",
    "Beryllium",
    "Boron",
    "Carbon",
    "Nitrogen",
    "Oxygen",
    "Fluorine",
    "Neon",
    "Sodium",
    "Magnesium",
    "Aluminum",
    "Silicon",
    "Phosphorus",
    "Sulfur",
    "Chlorine",
    "Argon",
    "Potassium",
    "Calcium",
    "Scandium",
    "Titanium",
    "Vanadium",
    "Chromium",
    "Manganese",
    "Iron",
    "Cobalt",
    "Nickel",
    "Copper",
    "Zinc",
    "Gallium",
    "Germanium",
    "Arsenic",
    "Selenium",
    "Bromine",
    "Krypton",
    "Rubidium",
    "Strontium",
    "Yttrium",
    "Zirconium",
    "Niobium",
    "Molybdenum",
    "Technetium",
    "Ruthenium",
    "Rhodium",
    "Palladium",
    "Silver",
    "Gold",
    "Platinum",
    "Iridium",
)

_ELEMENT_SYMBOLS: tuple[str, ...] = (
    "H",
    "He",
    "Li",
    "Be",
    "B",
    "C",
    "N",
    "O",
    "F",
    "Ne",
    "Na",
    "Mg",
    "Al",
    "Si",
    "P",
    "S",
    "Cl",
    "Ar",
    "K",
    "Ca",
    "Sc",
    "Ti",
    "V",
    "Cr",
    "Mn",
    "Fe",
    "Co",
    "Ni",
    "Cu",
    "Zn",
    "Ga",
    "Ge",
    "As",
    "Se",
    "Br",
    "Kr",
    "Rb",
    "Sr",
    "Y",
    "Zr",
    "Nb",
    "Mo",
    "Tc",
    "Ru",
    "Rh",
    "Pd",
    "Ag",
    "Au",
    "Pt",
    "Ir",
)

_SI_UNITS: tuple[str, ...] = (
    "meter (m)",
    "kilogram (kg)",
    "second (s)",
    "ampere (A)",
    "kelvin (K)",
    "mole (mol)",
    "candela (cd)",
    "hertz (Hz)",
    "newton (N)",
    "pascal (Pa)",
    "joule (J)",
    "watt (W)",
    "coulomb (C)",
    "volt (V)",
    "farad (F)",
    "ohm (Ω)",
    "siemens (S)",
    "weber (Wb)",
    "tesla (T)",
    "henry (H)",
    "lumen (lm)",
    "lux (lx)",
    "becquerel (Bq)",
    "gray (Gy)",
    "sievert (Sv)",
)

_PLANETS: tuple[str, ...] = (
    "Mercury",
    "Venus",
    "Earth",
    "Mars",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
)

_GALAXIES: tuple[str, ...] = (
    "Milky Way",
    "Andromeda",
    "Triangulum",
    "Centaurus A",
    "Messier 87",
    "Sombrero Galaxy",
    "Whirlpool Galaxy",
    "Pinwheel Galaxy",
    "Cartwheel Galaxy",
    "Cigar Galaxy",
    "Black Eye Galaxy",
    "Sunflower Galaxy",
    "Tadpole Galaxy",
    "Hoag's Object",
    "NGC 1300",
)

_CONSTELLATIONS: tuple[str, ...] = (
    "Orion",
    "Ursa Major",
    "Ursa Minor",
    "Cassiopeia",
    "Scorpius",
    "Leo",
    "Gemini",
    "Taurus",
    "Sagittarius",
    "Andromeda",
    "Aquarius",
    "Aries",
    "Cancer",
    "Capricornus",
    "Libra",
    "Pisces",
    "Virgo",
    "Cygnus",
    "Lyra",
    "Pegasus",
    "Perseus",
    "Draco",
    "Centaurus",
    "Canis Major",
    "Canis Minor",
)

_SCIENTIFIC_DISCIPLINES: tuple[str, ...] = (
    "Physics",
    "Chemistry",
    "Biology",
    "Mathematics",
    "Astronomy",
    "Geology",
    "Ecology",
    "Genetics",
    "Neuroscience",
    "Biochemistry",
    "Quantum Mechanics",
    "Thermodynamics",
    "Electrodynamics",
    "Organic Chemistry",
    "Inorganic Chemistry",
    "Molecular Biology",
    "Astrophysics",
    "Cosmology",
    "Paleontology",
    "Oceanography",
    "Meteorology",
    "Seismology",
    "Virology",
    "Immunology",
    "Epidemiology",
)

_METRIC_PREFIXES: tuple[str, ...] = (
    "yotta (Y)",
    "zetta (Z)",
    "exa (E)",
    "peta (P)",
    "tera (T)",
    "giga (G)",
    "mega (M)",
    "kilo (k)",
    "hecto (h)",
    "deca (da)",
    "deci (d)",
    "centi (c)",
    "milli (m)",
    "micro (μ)",
    "nano (n)",
    "pico (p)",
    "femto (f)",
    "atto (a)",
)


class ScienceProvider(BaseProvider):
    """Generates fake science data — elements, planets, units, etc."""

    __slots__ = ()

    _provider_name = "science"
    _locale_modules: tuple[str, ...] = ()
    _field_map: dict[str, str] = {
        "chemical_element": "chemical_element",
        "element": "chemical_element",
        "element_symbol": "element_symbol",
        "si_unit": "si_unit",
        "unit": "si_unit",
        "planet": "planet",
        "galaxy": "galaxy",
        "constellation": "constellation",
        "scientific_discipline": "scientific_discipline",
        "discipline": "scientific_discipline",
        "metric_prefix": "metric_prefix",
    }

    # --- Public API ---

    @overload
    def chemical_element(self) -> str: ...
    @overload
    def chemical_element(self, count: Literal[1]) -> str: ...
    @overload
    def chemical_element(self, count: int) -> str | list[str]: ...
    def chemical_element(self, count: int = 1) -> str | list[str]:
        """Generate a chemical element name (e.g., Hydrogen, Carbon)."""
        if count == 1:
            return self._engine.choice(_CHEMICAL_ELEMENTS)
        return self._engine.choices(_CHEMICAL_ELEMENTS, count)

    @overload
    def element_symbol(self) -> str: ...
    @overload
    def element_symbol(self, count: Literal[1]) -> str: ...
    @overload
    def element_symbol(self, count: int) -> str | list[str]: ...
    def element_symbol(self, count: int = 1) -> str | list[str]:
        """Generate a chemical element symbol (e.g., H, C, Fe)."""
        if count == 1:
            return self._engine.choice(_ELEMENT_SYMBOLS)
        return self._engine.choices(_ELEMENT_SYMBOLS, count)

    @overload
    def si_unit(self) -> str: ...
    @overload
    def si_unit(self, count: Literal[1]) -> str: ...
    @overload
    def si_unit(self, count: int) -> str | list[str]: ...
    def si_unit(self, count: int = 1) -> str | list[str]:
        """Generate an SI unit (e.g., meter (m), joule (J))."""
        if count == 1:
            return self._engine.choice(_SI_UNITS)
        return self._engine.choices(_SI_UNITS, count)

    @overload
    def planet(self) -> str: ...
    @overload
    def planet(self, count: Literal[1]) -> str: ...
    @overload
    def planet(self, count: int) -> str | list[str]: ...
    def planet(self, count: int = 1) -> str | list[str]:
        """Generate a planet name from our solar system."""
        if count == 1:
            return self._engine.choice(_PLANETS)
        return self._engine.choices(_PLANETS, count)

    @overload
    def galaxy(self) -> str: ...
    @overload
    def galaxy(self, count: Literal[1]) -> str: ...
    @overload
    def galaxy(self, count: int) -> str | list[str]: ...
    def galaxy(self, count: int = 1) -> str | list[str]:
        """Generate a galaxy name (e.g., Milky Way, Andromeda)."""
        if count == 1:
            return self._engine.choice(_GALAXIES)
        return self._engine.choices(_GALAXIES, count)

    @overload
    def constellation(self) -> str: ...
    @overload
    def constellation(self, count: Literal[1]) -> str: ...
    @overload
    def constellation(self, count: int) -> str | list[str]: ...
    def constellation(self, count: int = 1) -> str | list[str]:
        """Generate a constellation name (e.g., Orion, Leo)."""
        if count == 1:
            return self._engine.choice(_CONSTELLATIONS)
        return self._engine.choices(_CONSTELLATIONS, count)

    @overload
    def scientific_discipline(self) -> str: ...
    @overload
    def scientific_discipline(self, count: Literal[1]) -> str: ...
    @overload
    def scientific_discipline(self, count: int) -> str | list[str]: ...
    def scientific_discipline(self, count: int = 1) -> str | list[str]:
        """Generate a scientific discipline (e.g., Physics, Genetics)."""
        if count == 1:
            return self._engine.choice(_SCIENTIFIC_DISCIPLINES)
        return self._engine.choices(_SCIENTIFIC_DISCIPLINES, count)

    @overload
    def metric_prefix(self) -> str: ...
    @overload
    def metric_prefix(self, count: Literal[1]) -> str: ...
    @overload
    def metric_prefix(self, count: int) -> str | list[str]: ...
    def metric_prefix(self, count: int = 1) -> str | list[str]:
        """Generate a metric prefix (e.g., kilo (k), nano (n))."""
        if count == 1:
            return self._engine.choice(_METRIC_PREFIXES)
        return self._engine.choices(_METRIC_PREFIXES, count)
