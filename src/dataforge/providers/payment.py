"""Payment provider — credit card types, payment methods, processors, etc."""

from typing import Literal, overload

from dataforge.providers.base import BaseProvider

_CARD_TYPES: tuple[str, ...] = (
    "Visa",
    "Mastercard",
    "American Express",
    "Discover",
    "Diners Club",
    "JCB",
    "UnionPay",
    "Maestro",
    "Mir",
    "Elo",
)

_PAYMENT_METHODS: tuple[str, ...] = (
    "Credit Card",
    "Debit Card",
    "PayPal",
    "Apple Pay",
    "Google Pay",
    "Samsung Pay",
    "Bank Transfer",
    "Wire Transfer",
    "Cash",
    "Check",
    "Cryptocurrency",
    "Venmo",
    "Zelle",
    "Alipay",
    "WeChat Pay",
    "Klarna",
    "Afterpay",
    "Cash App",
    "Money Order",
    "ACH Transfer",
)

_PROCESSORS: tuple[str, ...] = (
    "Stripe",
    "Square",
    "Adyen",
    "Braintree",
    "Worldpay",
    "Checkout.com",
    "PayPal Commerce",
    "Authorize.Net",
    "2Checkout",
    "BlueSnap",
    "Payoneer",
    "Razorpay",
    "Mollie",
    "dLocal",
    "Nuvei",
)

_TRANSACTION_STATUSES: tuple[str, ...] = (
    "pending",
    "processing",
    "completed",
    "failed",
    "refunded",
    "partially_refunded",
    "voided",
    "disputed",
    "chargeback",
    "authorized",
)

_CURRENCIES: tuple[str, ...] = (
    "USD",
    "EUR",
    "GBP",
    "JPY",
    "CHF",
    "CAD",
    "AUD",
    "CNY",
    "HKD",
    "NZD",
    "SEK",
    "NOK",
    "DKK",
    "SGD",
    "KRW",
    "INR",
    "BRL",
    "MXN",
    "ZAR",
    "PLN",
    "TRY",
    "RUB",
    "THB",
    "TWD",
    "AED",
)

_CURRENCY_SYMBOLS: tuple[str, ...] = (
    "$",
    "€",
    "£",
    "¥",
    "Fr",
    "C$",
    "A$",
    "¥",
    "HK$",
    "NZ$",
    "kr",
    "kr",
    "kr",
    "S$",
    "₩",
    "₹",
    "R$",
    "MX$",
    "R",
    "zł",
    "₺",
    "₽",
    "฿",
    "NT$",
    "د.إ",
)


class PaymentProvider(BaseProvider):
    """Generates fake payment and transaction data."""

    __slots__ = ()

    _provider_name = "payment"
    _locale_modules: tuple[str, ...] = ()
    _field_map: dict[str, str] = {
        "card_type": "card_type",
        "payment_method": "payment_method",
        "payment_processor": "payment_processor",
        "processor": "payment_processor",
        "transaction_status": "transaction_status",
        "transaction_id": "transaction_id",
        "txn_id": "transaction_id",
        "currency_code": "currency_code",
        "currency_symbol": "currency_symbol",
        "payment_amount": "payment_amount",
        "cvv": "cvv",
        "expiry_date": "expiry_date",
        "card_expiry": "expiry_date",
    }

    # --- Scalar helpers ---

    def _one_transaction_id(self) -> str:
        return f"TXN-{self._engine.random_digits_str(12)}"

    def _one_payment_amount(self) -> str:
        dollars = self._engine.random_int(1, 9999)
        cents = self._engine.random_int(0, 99)
        return f"{dollars}.{cents:02d}"

    def _one_cvv(self) -> str:
        return self._engine.random_digits_str(
            4 if self._engine.random_int(0, 1) == 0 else 3
        )

    def _one_expiry_date(self) -> str:
        month = self._engine.random_int(1, 12)
        year = self._engine.random_int(25, 32)
        return f"{month:02d}/{year:02d}"

    # --- Public API ---

    @overload
    def card_type(self) -> str: ...
    @overload
    def card_type(self, count: Literal[1]) -> str: ...
    @overload
    def card_type(self, count: int) -> str | list[str]: ...
    def card_type(self, count: int = 1) -> str | list[str]:
        """Generate a credit/debit card type (e.g., Visa, Mastercard)."""
        if count == 1:
            return self._engine.choice(_CARD_TYPES)
        return self._engine.choices(_CARD_TYPES, count)

    @overload
    def payment_method(self) -> str: ...
    @overload
    def payment_method(self, count: Literal[1]) -> str: ...
    @overload
    def payment_method(self, count: int) -> str | list[str]: ...
    def payment_method(self, count: int = 1) -> str | list[str]:
        """Generate a payment method (e.g., Credit Card, PayPal)."""
        if count == 1:
            return self._engine.choice(_PAYMENT_METHODS)
        return self._engine.choices(_PAYMENT_METHODS, count)

    @overload
    def payment_processor(self) -> str: ...
    @overload
    def payment_processor(self, count: Literal[1]) -> str: ...
    @overload
    def payment_processor(self, count: int) -> str | list[str]: ...
    def payment_processor(self, count: int = 1) -> str | list[str]:
        """Generate a payment processor name (e.g., Stripe, Square)."""
        if count == 1:
            return self._engine.choice(_PROCESSORS)
        return self._engine.choices(_PROCESSORS, count)

    @overload
    def transaction_status(self) -> str: ...
    @overload
    def transaction_status(self, count: Literal[1]) -> str: ...
    @overload
    def transaction_status(self, count: int) -> str | list[str]: ...
    def transaction_status(self, count: int = 1) -> str | list[str]:
        """Generate a transaction status (e.g., pending, completed)."""
        if count == 1:
            return self._engine.choice(_TRANSACTION_STATUSES)
        return self._engine.choices(_TRANSACTION_STATUSES, count)

    @overload
    def transaction_id(self) -> str: ...
    @overload
    def transaction_id(self, count: Literal[1]) -> str: ...
    @overload
    def transaction_id(self, count: int) -> str | list[str]: ...
    def transaction_id(self, count: int = 1) -> str | list[str]:
        """Generate a transaction ID (TXN-############)."""
        if count == 1:
            return self._one_transaction_id()
        # Inlined batch with local-bound random_digits_str
        _rds = self._engine.random_digits_str
        return [f"TXN-{_rds(12)}" for _ in range(count)]

    @overload
    def currency_code(self) -> str: ...
    @overload
    def currency_code(self, count: Literal[1]) -> str: ...
    @overload
    def currency_code(self, count: int) -> str | list[str]: ...
    def currency_code(self, count: int = 1) -> str | list[str]:
        """Generate an ISO 4217 currency code (e.g., USD, EUR)."""
        if count == 1:
            return self._engine.choice(_CURRENCIES)
        return self._engine.choices(_CURRENCIES, count)

    @overload
    def currency_symbol(self) -> str: ...
    @overload
    def currency_symbol(self, count: Literal[1]) -> str: ...
    @overload
    def currency_symbol(self, count: int) -> str | list[str]: ...
    def currency_symbol(self, count: int = 1) -> str | list[str]:
        """Generate a currency symbol (e.g., $, EUR, GBP)."""
        if count == 1:
            return self._engine.choice(_CURRENCY_SYMBOLS)
        return self._engine.choices(_CURRENCY_SYMBOLS, count)

    @overload
    def payment_amount(self) -> str: ...
    @overload
    def payment_amount(self, count: Literal[1]) -> str: ...
    @overload
    def payment_amount(self, count: int) -> str | list[str]: ...
    def payment_amount(self, count: int = 1) -> str | list[str]:
        """Generate a payment amount (e.g., 49.99)."""
        if count == 1:
            return self._one_payment_amount()
        _ri = self._engine.random_int
        return [f"{_ri(1, 9999)}.{_ri(0, 99):02d}" for _ in range(count)]

    @overload
    def cvv(self) -> str: ...
    @overload
    def cvv(self, count: Literal[1]) -> str: ...
    @overload
    def cvv(self, count: int) -> str | list[str]: ...
    def cvv(self, count: int = 1) -> str | list[str]:
        """Generate a CVV code (3 or 4 digits)."""
        if count == 1:
            return self._one_cvv()
        _rds = self._engine.random_digits_str
        _ri = self._engine.random_int
        return [_rds(4 if _ri(0, 1) == 0 else 3) for _ in range(count)]

    @overload
    def expiry_date(self) -> str: ...
    @overload
    def expiry_date(self, count: Literal[1]) -> str: ...
    @overload
    def expiry_date(self, count: int) -> str | list[str]: ...
    def expiry_date(self, count: int = 1) -> str | list[str]:
        """Generate a card expiry date (MM/YY)."""
        if count == 1:
            return self._one_expiry_date()
        _ri = self._engine.random_int
        return [f"{_ri(1, 12):02d}/{_ri(25, 32):02d}" for _ in range(count)]
