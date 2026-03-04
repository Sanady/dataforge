"""Tests for the EcommerceProvider."""

import re

from dataforge import DataForge


class TestEcommerceProductName:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_product_name_is_string(self) -> None:
        name = self.forge.ecommerce.product_name()
        assert isinstance(name, str)
        assert len(name) > 0

    def test_product_name_has_three_parts(self) -> None:
        name = self.forge.ecommerce.product_name()
        parts = name.split(" ", 2)
        assert len(parts) >= 3

    def test_product_name_batch(self) -> None:
        results = self.forge.ecommerce.product_name(count=100)
        assert isinstance(results, list)
        assert len(results) == 100


class TestEcommerceCategory:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_category_is_string(self) -> None:
        cat = self.forge.ecommerce.product_category()
        assert isinstance(cat, str)
        assert len(cat) > 0

    def test_category_batch(self) -> None:
        results = self.forge.ecommerce.product_category(count=50)
        assert len(results) == 50


class TestEcommerceSKU:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_sku_format(self) -> None:
        sku = self.forge.ecommerce.sku()
        assert re.match(r"^[A-Z]{3}-\d{6}$", sku)

    def test_sku_batch(self) -> None:
        results = self.forge.ecommerce.sku(count=50)
        assert len(results) == 50
        for s in results:
            assert re.match(r"^[A-Z]{3}-\d{6}$", s)


class TestEcommercePriceWithCurrency:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_price_format(self) -> None:
        price = self.forge.ecommerce.price_with_currency()
        assert isinstance(price, str)
        assert len(price) > 0

    def test_price_batch(self) -> None:
        results = self.forge.ecommerce.price_with_currency(count=50)
        assert len(results) == 50


class TestEcommerceReview:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_rating_range(self) -> None:
        for _ in range(100):
            r = self.forge.ecommerce.review_rating()
            assert 1 <= r <= 5

    def test_rating_batch(self) -> None:
        results = self.forge.ecommerce.review_rating(count=100)
        assert len(results) == 100
        for r in results:
            assert 1 <= r <= 5

    def test_review_title(self) -> None:
        title = self.forge.ecommerce.review_title()
        assert isinstance(title, str)
        assert len(title) > 0


class TestEcommerceTracking:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_tracking_number(self) -> None:
        tn = self.forge.ecommerce.tracking_number()
        assert isinstance(tn, str)
        assert len(tn) > 10

    def test_tracking_batch(self) -> None:
        results = self.forge.ecommerce.tracking_number(count=50)
        assert len(results) == 50


class TestEcommerceOrderId:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_order_id_format(self) -> None:
        oid = self.forge.ecommerce.order_id()
        assert oid.startswith("ORD-")
        assert len(oid) == 14  # ORD- + 10 digits

    def test_order_id_batch(self) -> None:
        results = self.forge.ecommerce.order_id(count=50)
        assert len(results) == 50


class TestEcommerceInSchema:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_schema_fields(self) -> None:
        rows = self.forge.to_dict(fields=["product_name", "sku", "order_id"], count=5)
        assert len(rows) == 5
        for row in rows:
            assert "product_name" in row
            assert "sku" in row
            assert "order_id" in row
