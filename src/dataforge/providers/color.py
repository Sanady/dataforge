"""Color provider — generates fake colors in various formats."""

from typing import Literal, overload

from dataforge.providers.base import BaseProvider

_COLOR_NAMES: tuple[str, ...] = (
    "Red",
    "Green",
    "Blue",
    "Yellow",
    "Orange",
    "Purple",
    "Pink",
    "Brown",
    "Black",
    "White",
    "Gray",
    "Cyan",
    "Magenta",
    "Lime",
    "Maroon",
    "Navy",
    "Olive",
    "Teal",
    "Aqua",
    "Silver",
    "Gold",
    "Coral",
    "Salmon",
    "Turquoise",
    "Indigo",
    "Violet",
    "Crimson",
    "Khaki",
    "Ivory",
    "Lavender",
    "Beige",
    "Mint",
    "Plum",
    "Orchid",
    "Sienna",
    "Tan",
    "Azure",
    "Peach",
    "Chartreuse",
    "Fuchsia",
    "Tomato",
    "SteelBlue",
    "SlateGray",
    "RoyalBlue",
    "DarkGreen",
    "DarkRed",
    "DodgerBlue",
    "ForestGreen",
    "Chocolate",
    "Firebrick",
)


class ColorProvider(BaseProvider):
    """Generates fake color values in various formats.

    Parameters
    ----------
    engine : RandomEngine
        The shared random engine instance.
    """

    __slots__ = ()

    _provider_name = "color"
    _locale_modules = ()
    _field_map = {
        "color_name": "color_name",
        "color": "color_name",
        "hex_color": "hex_color",
        "rgb_color": "rgb_string",
        "hsl_color": "hsl_string",
    }

    # ------------------------------------------------------------------
    # Scalar helpers
    # ------------------------------------------------------------------

    def _one_hex(self) -> str:
        return f"#{self._engine._rng.getrandbits(24):06x}"

    def _one_rgb(self) -> tuple[int, int, int]:
        bits = self._engine._rng.getrandbits(24)
        return (bits >> 16) & 0xFF, (bits >> 8) & 0xFF, bits & 0xFF

    def _one_rgba(self) -> tuple[int, int, int, float]:
        r, g, b = self._one_rgb()
        a = self._engine.random_int(0, 100) / 100.0
        return (r, g, b, a)

    def _one_hsl(self) -> tuple[int, int, int]:
        return (
            self._engine.random_int(0, 360),
            self._engine.random_int(0, 100),
            self._engine.random_int(0, 100),
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @overload
    def color_name(self) -> str: ...
    @overload
    def color_name(self, count: Literal[1]) -> str: ...
    @overload
    def color_name(self, count: int) -> str | list[str]: ...
    def color_name(self, count: int = 1) -> str | list[str]:
        """Generate a random color name (e.g. ``"Red"``, ``"Teal"``).

        Parameters
        ----------
        count : int
            Number of color names to generate.
        """
        if count == 1:
            return self._engine.choice(_COLOR_NAMES)
        return self._engine.choices(_COLOR_NAMES, count)

    @overload
    def hex_color(self) -> str: ...
    @overload
    def hex_color(self, count: Literal[1]) -> str: ...
    @overload
    def hex_color(self, count: int) -> str | list[str]: ...
    def hex_color(self, count: int = 1) -> str | list[str]:
        """Generate a random hex color (e.g. ``"#a3f2c1"``).

        Parameters
        ----------
        count : int
            Number of hex colors to generate.
        """
        if count == 1:
            return self._one_hex()
        return [self._one_hex() for _ in range(count)]

    @overload
    def rgb(self) -> tuple[int, int, int]: ...
    @overload
    def rgb(self, count: Literal[1]) -> tuple[int, int, int]: ...
    @overload
    def rgb(self, count: int) -> tuple[int, int, int] | list[tuple[int, int, int]]: ...
    def rgb(self, count: int = 1) -> tuple[int, int, int] | list[tuple[int, int, int]]:
        """Generate a random RGB tuple (e.g. ``(123, 45, 200)``).

        Parameters
        ----------
        count : int
            Number of RGB tuples to generate.
        """
        if count == 1:
            return self._one_rgb()
        return [self._one_rgb() for _ in range(count)]

    @overload
    def rgba(self) -> tuple[int, int, int, float]: ...
    @overload
    def rgba(self, count: Literal[1]) -> tuple[int, int, int, float]: ...
    @overload
    def rgba(
        self, count: int
    ) -> tuple[int, int, int, float] | list[tuple[int, int, int, float]]: ...
    def rgba(
        self, count: int = 1
    ) -> tuple[int, int, int, float] | list[tuple[int, int, int, float]]:
        """Generate a random RGBA tuple (e.g. ``(123, 45, 200, 0.75)``).

        Parameters
        ----------
        count : int
            Number of RGBA tuples to generate.
        """
        if count == 1:
            return self._one_rgba()
        return [self._one_rgba() for _ in range(count)]

    @overload
    def rgb_string(self) -> str: ...
    @overload
    def rgb_string(self, count: Literal[1]) -> str: ...
    @overload
    def rgb_string(self, count: int) -> str | list[str]: ...
    def rgb_string(self, count: int = 1) -> str | list[str]:
        """Generate a random RGB CSS string (e.g. ``"rgb(123, 45, 200)"``).

        Parameters
        ----------
        count : int
            Number of RGB strings to generate.
        """
        if count == 1:
            r, g, b = self._one_rgb()
            return f"rgb({r}, {g}, {b})"
        result: list[str] = []
        for _ in range(count):
            r, g, b = self._one_rgb()
            result.append(f"rgb({r}, {g}, {b})")
        return result

    @overload
    def hsl(self) -> tuple[int, int, int]: ...
    @overload
    def hsl(self, count: Literal[1]) -> tuple[int, int, int]: ...
    @overload
    def hsl(self, count: int) -> tuple[int, int, int] | list[tuple[int, int, int]]: ...
    def hsl(self, count: int = 1) -> tuple[int, int, int] | list[tuple[int, int, int]]:
        """Generate a random HSL tuple (e.g. ``(210, 65, 50)``).

        Parameters
        ----------
        count : int
            Number of HSL tuples to generate.
        """
        if count == 1:
            return self._one_hsl()
        return [self._one_hsl() for _ in range(count)]

    @overload
    def hsl_string(self) -> str: ...
    @overload
    def hsl_string(self, count: Literal[1]) -> str: ...
    @overload
    def hsl_string(self, count: int) -> str | list[str]: ...
    def hsl_string(self, count: int = 1) -> str | list[str]:
        """Generate a random HSL CSS string (e.g. ``"hsl(210, 65%, 50%)"``).

        Parameters
        ----------
        count : int
            Number of HSL strings to generate.
        """
        if count == 1:
            h, s, lt = self._one_hsl()
            return f"hsl({h}, {s}%, {lt}%)"
        result: list[str] = []
        for _ in range(count):
            h, s, lt = self._one_hsl()
            result.append(f"hsl({h}, {s}%, {lt}%)")
        return result
