"""E-commerce provider — products, SKUs, tracking, reviews."""

from typing import Literal, overload

from dataforge.providers.base import BaseProvider

_PRODUCT_ADJECTIVES: tuple[str, ...] = (
    "Premium",
    "Deluxe",
    "Ultra",
    "Pro",
    "Essential",
    "Classic",
    "Modern",
    "Smart",
    "Eco",
    "Advanced",
    "Elite",
    "Basic",
    "Compact",
    "Portable",
    "Wireless",
    "Digital",
    "Organic",
    "Vintage",
    "Artisan",
    "Custom",
    "Heavy-Duty",
    "Lightweight",
    "Industrial",
    "Professional",
    "Commercial",
    "Residential",
)

_PRODUCT_MATERIALS: tuple[str, ...] = (
    "Steel",
    "Aluminum",
    "Bamboo",
    "Cotton",
    "Leather",
    "Silk",
    "Wooden",
    "Ceramic",
    "Glass",
    "Rubber",
    "Plastic",
    "Granite",
    "Marble",
    "Carbon Fiber",
    "Titanium",
    "Bronze",
    "Copper",
    "Linen",
    "Wool",
    "Concrete",
    "Paper",
    "Foam",
    "Nylon",
)

_PRODUCT_ITEMS: tuple[str, ...] = (
    "Chair",
    "Table",
    "Lamp",
    "Keyboard",
    "Mouse",
    "Monitor",
    "Headphones",
    "Speaker",
    "Camera",
    "Watch",
    "Bag",
    "Wallet",
    "Bottle",
    "Mug",
    "Plate",
    "Bowl",
    "Knife",
    "Pan",
    "Pillow",
    "Blanket",
    "Towel",
    "Mirror",
    "Clock",
    "Frame",
    "Shelf",
    "Desk",
    "Sofa",
    "Bench",
    "Stool",
    "Rack",
    "Cabinet",
    "Drawer",
    "Basket",
    "Box",
    "Case",
    "Cover",
    "Mat",
    "Rug",
    "Curtain",
    "Vase",
    "Candle",
    "Planter",
    "Tray",
    "Hook",
    "Stand",
)

_PRODUCT_CATEGORIES: tuple[str, ...] = (
    "Electronics",
    "Clothing",
    "Home & Garden",
    "Sports & Outdoors",
    "Books",
    "Toys & Games",
    "Automotive",
    "Health & Beauty",
    "Food & Beverages",
    "Office Supplies",
    "Pet Supplies",
    "Jewelry",
    "Music",
    "Tools & Hardware",
    "Baby Products",
    "Arts & Crafts",
    "Industrial",
    "Software",
    "Furniture",
)

_TRACKING_PREFIXES: tuple[str, ...] = (
    "1Z",
    "94",
    "92",
    "TBA",
    "JD",
    "SF",
    "YT",
)

_REVIEW_TITLES: tuple[str, ...] = (
    "Great product!",
    "Highly recommended",
    "Good value for money",
    "Exceeded expectations",
    "Exactly as described",
    "Decent quality",
    "Not bad",
    "Could be better",
    "Disappointed",
    "Amazing!",
    "Perfect fit",
    "Solid build quality",
    "Love it!",
    "Just okay",
    "Works as expected",
    "Would buy again",
    "Five stars",
    "Better than expected",
    "Fantastic purchase",
    "Very satisfied",
)


class EcommerceProvider(BaseProvider):
    """Generates fake e-commerce data."""

    __slots__ = ()

    _provider_name = "ecommerce"
    _locale_modules: tuple[str, ...] = ()
    _field_map: dict[str, str] = {
        "product_name": "product_name",
        "product": "product_name",
        "product_category": "product_category",
        "category": "product_category",
        "sku": "sku",
        "price_with_currency": "price_with_currency",
        "review_rating": "review_rating",
        "rating": "review_rating",
        "review_title": "review_title",
        "tracking_number": "tracking_number",
        "order_id": "order_id",
    }

    _CURRENCIES: tuple[tuple[str, str], ...] = (
        ("$", "USD"),
        ("€", "EUR"),
        ("£", "GBP"),
        ("¥", "JPY"),
        ("$", "CAD"),
        ("$", "AUD"),
    )

    # --- Scalar helpers ---

    def _one_product_name(self) -> str:
        _c = self._engine.choice
        return (
            f"{_c(_PRODUCT_ADJECTIVES)} {_c(_PRODUCT_MATERIALS)} {_c(_PRODUCT_ITEMS)}"
        )

    def _one_sku(self) -> str:
        letters = "".join(chr(self._engine.random_int(65, 90)) for _ in range(3))
        return f"{letters}-{self._engine.random_digits_str(6)}"

    def _one_tracking(self) -> str:
        prefix = self._engine.choice(_TRACKING_PREFIXES)
        return prefix + self._engine.random_digits_str(18)

    def _one_order_id(self) -> str:
        return f"ORD-{self._engine.random_digits_str(10)}"

    # --- Public API ---

    @overload
    def product_name(self) -> str: ...
    @overload
    def product_name(self, count: Literal[1]) -> str: ...
    @overload
    def product_name(self, count: int) -> str | list[str]: ...
    def product_name(self, count: int = 1) -> str | list[str]:
        """Generate a fake product name."""
        if count == 1:
            return self._one_product_name()
        return [self._one_product_name() for _ in range(count)]

    @overload
    def product_category(self) -> str: ...
    @overload
    def product_category(self, count: Literal[1]) -> str: ...
    @overload
    def product_category(self, count: int) -> str | list[str]: ...
    def product_category(self, count: int = 1) -> str | list[str]:
        """Generate a product category."""
        if count == 1:
            return self._engine.choice(_PRODUCT_CATEGORIES)
        return self._engine.choices(_PRODUCT_CATEGORIES, count)

    @overload
    def sku(self) -> str: ...
    @overload
    def sku(self, count: Literal[1]) -> str: ...
    @overload
    def sku(self, count: int) -> str | list[str]: ...
    def sku(self, count: int = 1) -> str | list[str]:
        """Generate a product SKU (e.g., ABC-123456)."""
        if count == 1:
            return self._one_sku()
        return [self._one_sku() for _ in range(count)]

    @overload
    def price_with_currency(self) -> str: ...
    @overload
    def price_with_currency(self, count: Literal[1]) -> str: ...
    @overload
    def price_with_currency(self, count: int) -> str | list[str]: ...
    def price_with_currency(self, count: int = 1) -> str | list[str]:
        """Generate a price with currency symbol (e.g., $49.99)."""
        if count == 1:
            sym, _ = self._engine.choice(self._CURRENCIES)
            return f"{sym}{self._engine.random_int(1, 99999) / 100:.2f}"
        _ri = self._engine.random_int
        _c = self._engine.choice
        return [
            f"{_c(self._CURRENCIES)[0]}{_ri(1, 99999) / 100:.2f}" for _ in range(count)
        ]

    @overload
    def review_rating(self) -> int: ...
    @overload
    def review_rating(self, count: Literal[1]) -> int: ...
    @overload
    def review_rating(self, count: int) -> int | list[int]: ...
    def review_rating(self, count: int = 1) -> int | list[int]:
        """Generate a review rating (1-5)."""
        if count == 1:
            return self._engine.random_int(1, 5)
        return [self._engine.random_int(1, 5) for _ in range(count)]

    @overload
    def review_title(self) -> str: ...
    @overload
    def review_title(self, count: Literal[1]) -> str: ...
    @overload
    def review_title(self, count: int) -> str | list[str]: ...
    def review_title(self, count: int = 1) -> str | list[str]:
        """Generate a product review title."""
        if count == 1:
            return self._engine.choice(_REVIEW_TITLES)
        return self._engine.choices(_REVIEW_TITLES, count)

    @overload
    def tracking_number(self) -> str: ...
    @overload
    def tracking_number(self, count: Literal[1]) -> str: ...
    @overload
    def tracking_number(self, count: int) -> str | list[str]: ...
    def tracking_number(self, count: int = 1) -> str | list[str]:
        """Generate a shipping tracking number."""
        if count == 1:
            return self._one_tracking()
        return [self._one_tracking() for _ in range(count)]

    @overload
    def order_id(self) -> str: ...
    @overload
    def order_id(self, count: Literal[1]) -> str: ...
    @overload
    def order_id(self, count: int) -> str | list[str]: ...
    def order_id(self, count: int = 1) -> str | list[str]:
        """Generate an order ID (e.g., ORD-1234567890)."""
        if count == 1:
            return self._one_order_id()
        return [self._one_order_id() for _ in range(count)]
