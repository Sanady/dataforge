"""Tests for the PaymentProvider."""

import re

from dataforge import DataForge


class TestCardType:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_returns_str(self) -> None:
        assert isinstance(self.forge.payment.card_type(), str)

    def test_batch(self) -> None:
        results = self.forge.payment.card_type(count=50)
        assert isinstance(results, list)
        assert len(results) == 50


class TestPaymentMethod:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_returns_str(self) -> None:
        assert isinstance(self.forge.payment.payment_method(), str)

    def test_batch(self) -> None:
        results = self.forge.payment.payment_method(count=50)
        assert len(results) == 50


class TestPaymentProcessor:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_returns_str(self) -> None:
        assert isinstance(self.forge.payment.payment_processor(), str)

    def test_batch(self) -> None:
        results = self.forge.payment.payment_processor(count=50)
        assert len(results) == 50


class TestTransactionStatus:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_returns_str(self) -> None:
        assert isinstance(self.forge.payment.transaction_status(), str)

    def test_batch(self) -> None:
        results = self.forge.payment.transaction_status(count=50)
        assert len(results) == 50


class TestTransactionId:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_format(self) -> None:
        txn = self.forge.payment.transaction_id()
        assert re.match(r"^TXN-\d{12}$", txn)

    def test_batch(self) -> None:
        results = self.forge.payment.transaction_id(count=50)
        assert len(results) == 50
        for txn in results:
            assert txn.startswith("TXN-")


class TestCurrencyCode:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_returns_3_letters(self) -> None:
        code = self.forge.payment.currency_code()
        assert len(code) == 3
        assert code.isupper()

    def test_batch(self) -> None:
        results = self.forge.payment.currency_code(count=50)
        assert len(results) == 50


class TestPaymentAmount:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_format(self) -> None:
        amount = self.forge.payment.payment_amount()
        assert re.match(r"^\d+\.\d{2}$", amount)

    def test_batch(self) -> None:
        results = self.forge.payment.payment_amount(count=50)
        assert len(results) == 50


class TestCVV:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_length(self) -> None:
        cvv = self.forge.payment.cvv()
        assert len(cvv) in (3, 4)
        assert cvv.isdigit()

    def test_batch(self) -> None:
        results = self.forge.payment.cvv(count=50)
        assert len(results) == 50


class TestExpiryDate:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_format(self) -> None:
        exp = self.forge.payment.expiry_date()
        assert re.match(r"^\d{2}/\d{2}$", exp)

    def test_batch(self) -> None:
        results = self.forge.payment.expiry_date(count=50)
        assert len(results) == 50


class TestPaymentInSchema:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_schema_fields(self) -> None:
        rows = self.forge.to_dict(
            fields=["card_type", "payment_method", "transaction_id"],
            count=5,
        )
        assert len(rows) == 5
        for row in rows:
            assert "card_type" in row
            assert "payment_method" in row
            assert "transaction_id" in row
