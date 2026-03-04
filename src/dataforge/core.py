"""DataForge — the main entry point for fake data generation.

Usage::

    from dataforge import DataForge

    forge = DataForge(locale="en_US", seed=42)

    forge.person.first_name()           # "James"
    forge.person.full_name(count=1000)  # list of 1000 full names
    forge.address.full_address()        # "4821 Oak Ave, Chicago, IL 60614"
    forge.internet.email()              # "james.smith@gmail.com"
    forge.company.company_name()        # "Acme Inc"
    forge.phone.phone_number()          # "555-123-4567"
    forge.lorem.sentence()              # "Lorem ipsum dolor sit amet."
    forge.dt.date()                     # "2024-03-15"
"""

import importlib
from typing import TYPE_CHECKING, Any
from types import ModuleType

from dataforge.backend import RandomEngine
from dataforge.providers.base import BaseProvider

# ------------------------------------------------------------------
# Heuristic field-name mappings for ORM / model introspection
# ------------------------------------------------------------------

# Maps common model field names to DataForge field shorthand names.
# Used by schema_from_pydantic() and schema_from_sqlalchemy().
_FIELD_ALIASES: dict[str, str] = {
    # Person
    "name": "full_name",
    "full_name": "full_name",
    "fname": "first_name",
    "lname": "last_name",
    "surname": "last_name",
    "last": "last_name",
    "first": "first_name",
    "given_name": "first_name",
    "family_name": "last_name",
    "username": "username",
    "user_name": "username",
    # Contact
    "email_address": "email",
    "mail": "email",
    "phone": "phone_number",
    "phone_num": "phone_number",
    "telephone": "phone_number",
    "cell": "cell_number",
    "mobile": "cell_number",
    "cell_phone": "cell_number",
    "mobile_phone": "cell_number",
    # Address
    "street": "street_address",
    "street_addr": "street_address",
    "addr": "full_address",
    "address": "full_address",
    "zip": "zipcode",
    "zip_code": "zipcode",
    "postal_code": "zipcode",
    "postcode": "zipcode",
    "state_abbr": "state_abbreviation",
    "country_name": "country",
    # Internet
    "url": "url",
    "website": "url",
    "domain": "domain_name",
    "ip": "ipv4",
    "ip_address": "ipv4",
    "ipv4_address": "ipv4",
    "ipv6_address": "ipv6",
    "mac": "mac_address",
    "user_agent_string": "user_agent",
    # Company
    "company": "company_name",
    "company_nm": "company_name",
    "job": "job_title",
    "job_name": "job_title",
    "occupation": "job_title",
    "title": "job_title",
    # Finance
    "credit_card": "credit_card_number",
    "cc_number": "credit_card_number",
    "card_number": "credit_card_number",
    "iban_code": "iban",
    "currency": "currency_code",
    # Datetime
    "date": "date",
    "dob": "date_of_birth",
    "birth_date": "date_of_birth",
    "birthday": "date_of_birth",
    "time": "time",
    "datetime": "datetime",
    "created_at": "datetime",
    "updated_at": "datetime",
    "timestamp": "datetime",
    # Misc
    "uuid": "uuid4",
    "guid": "uuid4",
    "description": "sentence",
    "bio": "paragraph",
    "summary": "sentence",
    "note": "sentence",
    "notes": "paragraph",
    "comment": "sentence",
    "body": "paragraph",
    "text": "paragraph",
    "content": "paragraph",
    # Color
    "color": "color_name",
    "colour": "color_name",
    "hex_color": "hex_color",
    # File
    "filename": "file_name",
    "file": "file_name",
    "extension": "file_extension",
    "mime": "mime_type",
    "mime_type": "mime_type",
    # Network
    "port": "port",
    "hostname": "hostname",
    # Geo
    "latitude": "latitude",
    "lat": "latitude",
    "longitude": "longitude",
    "lng": "longitude",
    "lon": "longitude",
    # Government
    "ssn": "ssn",
    "tax_id": "tax_id",
    "passport": "passport_number",
    "passport_no": "passport_number",
}


def _pydantic_heuristic(field_name: str) -> str | None:
    """Map a Pydantic field name to a DataForge field name (or None)."""
    return _FIELD_ALIASES.get(field_name)


def _sqlalchemy_heuristic(col_name: str, column: "Any") -> str | None:
    """Map a SQLAlchemy column name to a DataForge field name (or None).

    Uses the column name first, then falls back to type-based
    heuristics for common SQL column types.
    """
    alias = _FIELD_ALIASES.get(col_name)
    if alias:
        return alias
    # Type-based fallback: if the column is an Integer primary key
    # we already skip it.  Other type-based heuristics could go here.
    return None


if TYPE_CHECKING:
    from dataforge.providers.address import AddressProvider
    from dataforge.providers.automotive import AutomotiveProvider
    from dataforge.providers.barcode import BarcodeProvider
    from dataforge.providers.color import ColorProvider
    from dataforge.providers.company import CompanyProvider
    from dataforge.providers.crypto import CryptoProvider
    from dataforge.providers.datetime import DateTimeProvider
    from dataforge.providers.ecommerce import EcommerceProvider
    from dataforge.providers.education import EducationProvider
    from dataforge.providers.file import FileProvider
    from dataforge.providers.finance import FinanceProvider
    from dataforge.providers.geo import GeoProvider
    from dataforge.providers.government import GovernmentProvider
    from dataforge.providers.internet import InternetProvider
    from dataforge.providers.lorem import LoremProvider
    from dataforge.providers.medical import MedicalProvider
    from dataforge.providers.misc import MiscProvider
    from dataforge.providers.network import NetworkProvider
    from dataforge.providers.payment import PaymentProvider
    from dataforge.providers.person import PersonProvider
    from dataforge.providers.phone import PhoneProvider
    from dataforge.providers.profile import ProfileProvider
    from dataforge.providers.science import ScienceProvider
    from dataforge.providers.text import TextProvider
    from dataforge.providers.ai_prompt import AiPromptProvider
    from dataforge.providers.llm import LlmProvider
    from dataforge.providers.ai_chat import AiChatProvider


class DataForge:
    """High-performance fake data generator.

    Providers are loaded **lazily** — nothing is imported until a
    provider property is first accessed.  The provider registry
    (:mod:`dataforge.registry`) resolves field names and provider
    classes automatically, so new providers can be added without
    editing this file.

    Parameters
    ----------
    locale : str
        The locale to use for data generation (e.g. ``"en_US"``).
        Locale data is loaded **lazily** — nothing is imported until
        a provider property is first accessed.
    seed : int | None
        Optional seed for reproducible output.  When set, the stdlib
        ``random`` backend is seeded for deterministic generation.

    Examples
    --------
    >>> forge = DataForge(seed=42)
    >>> forge.person.first_name()
    '...'
    >>> forge.address.city()
    '...'
    >>> forge.internet.email()
    '...'
    >>> forge.company.company_name()
    '...'
    >>> forge.phone.phone_number()
    '...'
    >>> forge.lorem.sentence()
    '...'
    >>> forge.dt.date()
    '...'
    >>> forge.finance.credit_card_number()
    '...'
    >>> forge.color.hex_color()
    '...'
    >>> forge.file.file_name()
    '...'
    >>> forge.network.ipv6()
    '...'
    >>> forge.misc.uuid4()
    '...'
    >>> forge.barcode.ean13()
    '...'
    """

    __slots__ = (
        "_engine",
        "_locale",
        "_providers",
        "_locale_cache",
        "_unique_proxy",
    )

    def __init__(self, locale: str = "en_US", seed: int | None = None) -> None:
        self._engine = RandomEngine(seed=seed)
        self._locale = locale
        self._providers: dict[str, BaseProvider] = {}
        self._locale_cache: dict[str, ModuleType] = {}
        self._unique_proxy: Any = None

    # ------------------------------------------------------------------
    # Dynamic provider access via registry
    # ------------------------------------------------------------------

    def _get_provider(self, name: str) -> BaseProvider:
        """Lazily instantiate and cache a provider by registry name.

        Uses the provider registry to resolve the class and its
        locale module requirements.  Providers are instantiated once
        and cached in ``_providers``.
        """
        prov = self._providers.get(name)
        if prov is not None:
            return prov

        from dataforge.registry import get_provider_info

        info = get_provider_info()
        if name not in info:
            raise AttributeError(
                f"DataForge has no provider '{name}'. "
                f"Available: {', '.join(sorted(info))}"
            )

        cls, locale_modules = info[name]
        if getattr(cls, "_needs_forge", False):
            # Compound provider that needs access to the DataForge instance
            prov = cls(self._engine, self)
        elif locale_modules:
            # Provider needs locale data modules
            locale_args = [self._load_locale_module(mod) for mod in locale_modules]
            prov = cls(self._engine, *locale_args)
        else:
            prov = cls(self._engine)

        self._providers[name] = prov
        return prov

    # ------------------------------------------------------------------
    # Explicit provider properties (for IDE autocomplete + type safety)
    # These delegate to _get_provider() which uses the registry.
    # ------------------------------------------------------------------

    @property
    def person(self) -> "PersonProvider":
        """Access the person data provider (names, prefixes, suffixes)."""
        return self._get_provider("person")  # type: ignore[return-value]

    @property
    def address(self) -> "AddressProvider":
        """Access the address data provider (streets, cities, zip codes)."""
        return self._get_provider("address")  # type: ignore[return-value]

    @property
    def internet(self) -> "InternetProvider":
        """Access the internet data provider (emails, usernames, domains, IPs)."""
        return self._get_provider("internet")  # type: ignore[return-value]

    @property
    def company(self) -> "CompanyProvider":
        """Access the company data provider (names, catch phrases, job titles)."""
        return self._get_provider("company")  # type: ignore[return-value]

    @property
    def phone(self) -> "PhoneProvider":
        """Access the phone data provider (phone numbers, cell numbers)."""
        return self._get_provider("phone")  # type: ignore[return-value]

    @property
    def lorem(self) -> "LoremProvider":
        """Access the Lorem Ipsum text provider (words, sentences, paragraphs)."""
        return self._get_provider("lorem")  # type: ignore[return-value]

    @property
    def dt(self) -> "DateTimeProvider":
        """Access the datetime provider (dates, times, datetimes)."""
        return self._get_provider("dt")  # type: ignore[return-value]

    @property
    def finance(self) -> "FinanceProvider":
        """Access the finance provider (credit cards, IBANs, currencies)."""
        return self._get_provider("finance")  # type: ignore[return-value]

    @property
    def color(self) -> "ColorProvider":
        """Access the color provider (hex, RGB, HSL, color names)."""
        return self._get_provider("color")  # type: ignore[return-value]

    @property
    def file(self) -> "FileProvider":
        """Access the file provider (file names, extensions, MIME types, paths)."""
        return self._get_provider("file")  # type: ignore[return-value]

    @property
    def network(self) -> "NetworkProvider":
        """Access the network provider (IPv6, MAC, port, hostname, user agent)."""
        return self._get_provider("network")  # type: ignore[return-value]

    @property
    def misc(self) -> "MiscProvider":
        """Access the misc provider (UUID4, boolean, random_element, null_or)."""
        return self._get_provider("misc")  # type: ignore[return-value]

    @property
    def barcode(self) -> "BarcodeProvider":
        """Access the barcode provider (EAN-13, EAN-8, ISBN-13, ISBN-10)."""
        return self._get_provider("barcode")  # type: ignore[return-value]

    @property
    def crypto(self) -> "CryptoProvider":
        """Access the crypto provider (MD5, SHA-1, SHA-256 hex strings)."""
        return self._get_provider("crypto")  # type: ignore[return-value]

    @property
    def automotive(self) -> "AutomotiveProvider":
        """Access the automotive provider (plates, VINs, makes, models)."""
        return self._get_provider("automotive")  # type: ignore[return-value]

    @property
    def education(self) -> "EducationProvider":
        """Access the education provider (universities, degrees, fields)."""
        return self._get_provider("education")  # type: ignore[return-value]

    @property
    def profile(self) -> "ProfileProvider":
        """Access the profile provider (coherent user profiles)."""
        return self._get_provider("profile")  # type: ignore[return-value]

    @property
    def government(self) -> "GovernmentProvider":
        """Access the government provider (SSN, tax ID, passports)."""
        return self._get_provider("government")  # type: ignore[return-value]

    @property
    def ecommerce(self) -> "EcommerceProvider":
        """Access the e-commerce provider (products, SKUs, orders)."""
        return self._get_provider("ecommerce")  # type: ignore[return-value]

    @property
    def medical(self) -> "MedicalProvider":
        """Access the medical provider (ICD-10, drugs, blood types)."""
        return self._get_provider("medical")  # type: ignore[return-value]

    @property
    def payment(self) -> "PaymentProvider":
        """Access the payment provider (card types, processors, transactions)."""
        return self._get_provider("payment")  # type: ignore[return-value]

    @property
    def text(self) -> "TextProvider":
        """Access the text provider (quotes, headlines, paragraphs)."""
        return self._get_provider("text")  # type: ignore[return-value]

    @property
    def geo(self) -> "GeoProvider":
        """Access the geo provider (continents, oceans, rivers, coordinates)."""
        return self._get_provider("geo")  # type: ignore[return-value]

    @property
    def science(self) -> "ScienceProvider":
        """Access the science provider (elements, planets, units)."""
        return self._get_provider("science")  # type: ignore[return-value]

    @property
    def ai_prompt(self) -> "AiPromptProvider":
        """Access the AI prompt provider (user/system/creative prompts)."""
        return self._get_provider("ai_prompt")  # type: ignore[return-value]

    @property
    def llm(self) -> "LlmProvider":
        """Access the LLM provider (models, agents, RAG, moderation, billing)."""
        return self._get_provider("llm")  # type: ignore[return-value]

    @property
    def ai_chat(self) -> "AiChatProvider":
        """Access the AI chat provider (conversation turns, messages)."""
        return self._get_provider("ai_chat")  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Unique value generation
    # ------------------------------------------------------------------

    @property
    def unique(self) -> "Any":
        """Access the unique-value proxy.

        Returns a proxy that ensures every value returned by a
        provider method is unique within the proxy's lifetime.
        Call ``forge.unique.clear()`` to reset tracking.

        Examples
        --------
        >>> forge = DataForge(seed=42)
        >>> a = forge.unique.person.first_name()
        >>> b = forge.unique.person.first_name()
        >>> a != b
        True
        """
        if self._unique_proxy is None:
            from dataforge.unique import UniqueProxy

            self._unique_proxy = UniqueProxy(self)
        return self._unique_proxy

    # ------------------------------------------------------------------
    # Provider registration
    # ------------------------------------------------------------------

    def register_provider(
        self,
        provider_cls: type[BaseProvider],
        name: str | None = None,
    ) -> None:
        """Register a custom provider class at runtime.

        The provider is added to this ``DataForge`` instance's
        internal registry and can be accessed via ``getattr``.

        Parameters
        ----------
        provider_cls : type[BaseProvider]
            The provider class to register.  Must be a
            ``BaseProvider`` subclass with ``_provider_name``.
        name : str | None
            Override the provider name.  Defaults to the class's
            ``_provider_name`` attribute.

        Examples
        --------
        >>> from dataforge.providers.base import BaseProvider
        >>> from dataforge.backend import RandomEngine
        >>> class MyProvider(BaseProvider):
        ...     _provider_name = "my"
        ...     _field_map = {"greeting": "greeting"}
        ...     def greeting(self, count=1):
        ...         return "hello" if count == 1 else ["hello"] * count
        >>> forge = DataForge()
        >>> forge.register_provider(MyProvider)
        >>> forge.my.greeting()
        'hello'
        """
        prov_name = name or getattr(provider_cls, "_provider_name", "")
        if not prov_name:
            raise ValueError(
                f"{provider_cls.__name__} does not define '_provider_name'."
            )
        locale_modules = getattr(provider_cls, "_locale_modules", ())
        if getattr(provider_cls, "_needs_forge", False):
            prov = provider_cls(self._engine, self)  # type: ignore[call-arg]
        elif locale_modules:
            locale_args = [self._load_locale_module(mod) for mod in locale_modules]
            prov = provider_cls(self._engine, *locale_args)  # type: ignore[call-arg]
        else:
            prov = provider_cls(self._engine)
        self._providers[prov_name] = prov

        # Register field mappings so Schema/to_dict can find them
        from dataforge.registry import register_runtime_provider

        register_runtime_provider(prov_name, provider_cls, locale_modules)

    def __getattr__(self, name: str) -> Any:
        """Dynamic attribute access for registered providers.

        Allows ``forge.my_provider`` to work for providers
        registered via :meth:`register_provider` at runtime,
        without requiring a ``@property`` on the class.
        """
        # Check if it's a cached provider
        providers = object.__getattribute__(self, "_providers")
        if name in providers:
            return providers[name]
        # Try registry lookup
        try:
            return self._get_provider(name)
        except AttributeError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            ) from None

    # ------------------------------------------------------------------
    # Seed control
    # ------------------------------------------------------------------

    def seed(self, value: int) -> None:
        """Re-seed the random engine for reproducible output.

        This resets the internal state of the stdlib ``random`` backend.
        """
        self._engine.seed(value)

    def copy(self, seed: int | None = None) -> "DataForge":
        """Create a new ``DataForge`` instance with the same locale.

        Parameters
        ----------
        seed : int | None
            Optional seed for the new instance.  If ``None``, the new
            instance is unseeded (non-deterministic).

        Returns
        -------
        DataForge
        """
        return DataForge(locale=self._locale, seed=seed)

    # ------------------------------------------------------------------
    # Schema API
    # ------------------------------------------------------------------

    def schema(self, fields: "list[str] | dict[str, Any]") -> "Any":
        """Create a pre-resolved :class:`Schema` for maximum throughput.

        Parameters
        ----------
        fields : list[str] | dict[str, str | Callable]
            Fields to generate.  String values are resolved to provider
            methods.  Callable values receive the current row dict and
            can reference previously generated columns.

        Returns
        -------
        Schema

        Examples
        --------
        >>> forge = DataForge(seed=42)
        >>> s = forge.schema(["first_name", "email"])
        >>> rows = s.generate(count=1000)
        """
        from dataforge.schema import Schema

        return Schema(self, fields)

    # ------------------------------------------------------------------
    # Locale management
    # ------------------------------------------------------------------

    @property
    def locale(self) -> str:
        """The currently active locale string (e.g. ``"en_US"``)."""
        return self._locale

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_locale_module(self, module_name: str) -> ModuleType:
        """Dynamically import a locale data module.

        Results are cached so that repeated access to the same provider
        does not re-import the module.

        If the requested locale does not provide the specified module,
        falls back to ``en_US`` and emits a warning.

        Parameters
        ----------
        module_name : str
            The name of the submodule inside the locale package
            (e.g. ``"person"``, ``"address"``).
        """
        key = f"{self._locale}.{module_name}"
        if key not in self._locale_cache:
            try:
                mod = importlib.import_module(
                    f"dataforge.locales.{self._locale}.{module_name}"
                )
            except ModuleNotFoundError:
                if self._locale == "en_US":
                    raise ValueError(
                        f"Locale 'en_US' does not have a '{module_name}' data module."
                    )
                import warnings

                warnings.warn(
                    f"Locale '{self._locale}' does not have a '{module_name}' "
                    f"data module — falling back to 'en_US'.",
                    UserWarning,
                    stacklevel=3,
                )
                mod = importlib.import_module(f"dataforge.locales.en_US.{module_name}")
            self._locale_cache[key] = mod
        return self._locale_cache[key]

    def _resolve_field(self, field: str) -> tuple[str, str]:
        """Resolve a field name to (provider_attr, method_name).

        Supports both direct names (e.g. ``"first_name"``) and
        dotted paths (e.g. ``"person.first_name"``).
        """
        # Dotted path: "person.first_name" → ("person", "first_name")
        if "." in field:
            provider_attr, method_name = field.split(".", 1)
            return provider_attr, method_name

        from dataforge.registry import get_field_map

        fm = get_field_map()
        if field in fm:
            return fm[field]
        raise ValueError(
            f"Unknown field '{field}'. Use dotted notation "
            f"(e.g. 'person.first_name') or a known shorthand."
        )

    # ------------------------------------------------------------------
    # Bulk data generation
    # ------------------------------------------------------------------

    def to_dict(
        self,
        fields: list[str] | dict[str, str],
        count: int = 10,
    ) -> list[dict[str, str]]:
        """Generate *count* rows of fake data as a list of dicts.

        Uses **column-first** batch generation for maximum throughput:
        each field is generated in bulk via its ``count=N`` batch path,
        then columns are zipped into row dicts.

        Parameters
        ----------
        fields : list[str] | dict[str, str]
            Fields to generate.  Can be a list of field names (e.g.
            ``["first_name", "email"]``) or a dict mapping output column
            names to field names (e.g. ``{"Name": "full_name"}``).
        count : int
            Number of rows to generate.

        Returns
        -------
        list[dict[str, str]]
            Each dict maps column name → generated value.

        Examples
        --------
        >>> forge = DataForge(seed=42)
        >>> rows = forge.to_dict(["first_name", "email"], count=3)
        >>> len(rows)
        3
        """
        if count == 0:
            return []

        # Normalize fields
        if isinstance(fields, list):
            field_defs = [(f, f) for f in fields]
        else:
            field_defs = list(fields.items())

        # Resolve providers and methods
        columns: list[str] = []
        callables: list[object] = []
        for col_name, field_name in field_defs:
            provider_attr, method_name = self._resolve_field(field_name)
            provider = getattr(self, provider_attr)
            method = getattr(provider, method_name)
            columns.append(col_name)
            callables.append(method)

        # Column-first: generate all values for each column in one batch call
        col_data: list[list[str]] = []
        for fn in callables:
            if count == 1:
                val = fn()  # type: ignore[operator]
                col_data.append([val if isinstance(val, str) else str(val)])
            else:
                values = fn(count=count)  # type: ignore[operator]
                # Most providers return list[str] — skip redundant str()
                if values and isinstance(values[0], str):
                    col_data.append(values)  # type: ignore[arg-type]
                else:
                    col_data.append([str(v) for v in values])

        # Zip columns into row dicts
        col_tuple = tuple(columns)
        return [dict(zip(col_tuple, row)) for row in zip(*col_data)]

    def to_csv(
        self,
        fields: list[str] | dict[str, str],
        count: int = 10,
        path: str | None = None,
    ) -> str:
        """Generate fake data and return (or write) as CSV.

        Delegates to :meth:`Schema.to_csv` for zero-duplication.

        Parameters
        ----------
        fields : list[str] | dict[str, str]
            Fields to generate (same format as :meth:`to_dict`).
        count : int
            Number of rows.
        path : str | None
            If provided, write CSV to this file path. Otherwise return
            the CSV as a string.

        Returns
        -------
        str
            The CSV content as a string.
        """
        return self.schema(fields).to_csv(count=count, path=path)

    def to_jsonl(
        self,
        fields: list[str] | dict[str, str],
        count: int = 10,
        path: str | None = None,
    ) -> str:
        """Generate fake data and return (or write) as JSON Lines.

        Delegates to :meth:`Schema.to_jsonl` for zero-duplication.

        Parameters
        ----------
        fields : list[str] | dict[str, str]
            Fields to generate (same format as :meth:`to_dict`).
        count : int
            Number of rows.
        path : str | None
            If provided, write JSONL to this file path.

        Returns
        -------
        str
            The JSONL content as a string.
        """
        return self.schema(fields).to_jsonl(count=count, path=path)

    def to_sql(
        self,
        fields: list[str] | dict[str, str],
        table: str,
        count: int = 10,
        dialect: str = "sqlite",
        path: str | None = None,
    ) -> str:
        """Generate fake data and return as SQL INSERT statements.

        Delegates to :meth:`Schema.to_sql` for zero-duplication.

        Parameters
        ----------
        fields : list[str] | dict[str, str]
            Fields to generate (same format as :meth:`to_dict`).
        table : str
            Target table name.
        count : int
            Number of rows.
        dialect : str
            SQL dialect: ``"sqlite"``, ``"mysql"``, or ``"postgresql"``.
        path : str | None
            If provided, write SQL to this file path.

        Returns
        -------
        str
            SQL INSERT statements as a string.
        """
        return self.schema(fields).to_sql(
            table=table, count=count, dialect=dialect, path=path
        )

    def to_dataframe(
        self,
        fields: list[str] | dict[str, str],
        count: int = 10,
    ) -> "Any":
        """Generate fake data as a pandas DataFrame.

        Delegates to :meth:`Schema.to_dataframe` for zero-duplication.
        Requires ``pandas`` to be installed.

        Parameters
        ----------
        fields : list[str] | dict[str, str]
            Fields to generate (same format as :meth:`to_dict`).
        count : int
            Number of rows.

        Returns
        -------
        pandas.DataFrame
            A DataFrame with one column per field.
        """
        return self.schema(fields).to_dataframe(count=count)

    def stream_to_csv(
        self,
        fields: list[str] | dict[str, str],
        path: str,
        count: int = 10,
        batch_size: int | None = None,
    ) -> int:
        """Stream fake data directly to a CSV file.

        Memory-efficient: writes in batches without materializing
        all rows in memory.

        Parameters
        ----------
        fields : list[str] | dict[str, str]
            Fields to generate.
        path : str
            File path to write.
        count : int
            Number of rows.
        batch_size : int | None
            Rows per batch.  Auto-tuned when ``None``.

        Returns
        -------
        int
            Number of rows written.
        """
        return self.schema(fields).stream_to_csv(
            path=path, count=count, batch_size=batch_size
        )

    def stream_to_jsonl(
        self,
        fields: list[str] | dict[str, str],
        path: str,
        count: int = 10,
        batch_size: int | None = None,
    ) -> int:
        """Stream fake data directly to a JSON Lines file.

        Memory-efficient: writes in batches without materializing
        all rows in memory.

        Parameters
        ----------
        fields : list[str] | dict[str, str]
            Fields to generate.
        path : str
            File path to write.
        count : int
            Number of rows.
        batch_size : int | None
            Rows per batch.  Auto-tuned when ``None``.

        Returns
        -------
        int
            Number of rows written.
        """
        return self.schema(fields).stream_to_jsonl(
            path=path, count=count, batch_size=batch_size
        )

    def to_arrow(
        self,
        fields: list[str] | dict[str, str],
        count: int = 10,
        batch_size: int | None = None,
    ) -> "Any":
        """Generate fake data as a PyArrow Table.

        Delegates to :meth:`Schema.to_arrow` for zero-duplication.
        Requires ``pyarrow`` to be installed.

        Parameters
        ----------
        fields : list[str] | dict[str, str]
            Fields to generate (same format as :meth:`to_dict`).
        count : int
            Number of rows.
        batch_size : int | None
            Rows per internal batch.  Auto-tuned when ``None``.

        Returns
        -------
        pyarrow.Table
        """
        return self.schema(fields).to_arrow(count=count, batch_size=batch_size)

    def to_polars(
        self,
        fields: list[str] | dict[str, str],
        count: int = 10,
        batch_size: int | None = None,
    ) -> "Any":
        """Generate fake data as a Polars DataFrame.

        Delegates to :meth:`Schema.to_polars` for zero-duplication.
        Requires ``polars`` to be installed.

        Parameters
        ----------
        fields : list[str] | dict[str, str]
            Fields to generate (same format as :meth:`to_dict`).
        count : int
            Number of rows.
        batch_size : int | None
            Rows per internal batch.  Auto-tuned when ``None``.

        Returns
        -------
        polars.DataFrame
        """
        return self.schema(fields).to_polars(count=count, batch_size=batch_size)

    def to_parquet(
        self,
        fields: list[str] | dict[str, str],
        path: str,
        count: int = 10,
        batch_size: int | None = None,
    ) -> int:
        """Generate fake data and write as a Parquet file.

        Requires ``pyarrow`` to be installed.  Data is written in
        batched row-groups for bounded memory usage.

        Parameters
        ----------
        fields : list[str] | dict[str, str]
            Fields to generate.
        path : str
            File path to write.
        count : int
            Number of rows.
        batch_size : int | None
            Rows per row-group.  Auto-tuned when ``None``.

        Returns
        -------
        int
            Number of rows written.
        """
        return self.schema(fields).to_parquet(
            path=path, count=count, batch_size=batch_size
        )

    def __repr__(self) -> str:
        return f"DataForge(locale={self._locale!r})"

    # ------------------------------------------------------------------
    # Schema factories from ORM / model introspection
    # ------------------------------------------------------------------

    def schema_from_pydantic(self, model: type) -> "Any":
        """Create a :class:`Schema` by introspecting a Pydantic model.

        Maps model field names to DataForge fields using the field
        registry.  Fields that cannot be mapped are silently skipped
        (a warning is emitted).  If the model has a field whose name
        exactly matches a registered DataForge field (e.g.
        ``first_name``, ``email``, ``city``), it is mapped
        automatically.

        Requires ``pydantic`` to be installed.

        Parameters
        ----------
        model : type
            A Pydantic ``BaseModel`` subclass.

        Returns
        -------
        Schema

        Examples
        --------
        >>> from pydantic import BaseModel
        >>> class User(BaseModel):
        ...     first_name: str
        ...     email: str
        ...     city: str
        >>> forge = DataForge(seed=42)
        >>> s = forge.schema_from_pydantic(User)
        >>> rows = s.generate(count=5)
        """
        from dataforge.schema import Schema

        try:
            from pydantic import BaseModel  # noqa: F811
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "pydantic is required for schema_from_pydantic(). "
                "Install it with: pip install pydantic"
            ) from exc

        if not (isinstance(model, type) and issubclass(model, BaseModel)):
            raise TypeError(f"Expected a Pydantic BaseModel subclass, got {model!r}")

        from dataforge.registry import get_field_map

        field_map = get_field_map()
        mapped: dict[str, str] = {}

        # Pydantic v2 uses model_fields; v1 used __fields__
        model_fields: dict[str, Any] = {}
        if hasattr(model, "model_fields"):
            model_fields = model.model_fields
        elif hasattr(model, "__fields__"):
            model_fields = model.__fields__
        else:
            raise TypeError(
                f"Cannot introspect fields from {model.__name__}. "
                "Ensure it is a valid Pydantic BaseModel."
            )

        import warnings

        for field_name in model_fields:
            if field_name in field_map:
                mapped[field_name] = field_name
            else:
                # Try common aliases / heuristic mapping
                alias = _pydantic_heuristic(field_name)
                if alias and alias in field_map:
                    mapped[field_name] = alias
                else:
                    warnings.warn(
                        f"Pydantic field '{field_name}' on {model.__name__} "
                        f"could not be mapped to a DataForge field — skipping.",
                        UserWarning,
                        stacklevel=2,
                    )

        if not mapped:
            raise ValueError(
                f"No fields on {model.__name__} could be mapped to "
                f"DataForge fields. Ensure the model uses recognisable "
                f"field names (e.g. 'first_name', 'email', 'city')."
            )

        return Schema(self, mapped)

    def schema_from_sqlalchemy(self, model: type) -> "Any":
        """Create a :class:`Schema` by introspecting a SQLAlchemy model.

        Maps column names to DataForge fields using the field
        registry.  Columns that cannot be mapped are silently skipped
        (a warning is emitted).  Primary key columns named ``id``
        are skipped automatically.

        Requires ``sqlalchemy`` to be installed.

        Parameters
        ----------
        model : type
            A SQLAlchemy declarative model class (must have
            ``__table__`` attribute).

        Returns
        -------
        Schema

        Examples
        --------
        >>> from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
        >>> class Base(DeclarativeBase): pass
        >>> class User(Base):
        ...     __tablename__ = "users"
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     first_name: Mapped[str]
        ...     email: Mapped[str]
        >>> forge = DataForge(seed=42)
        >>> s = forge.schema_from_sqlalchemy(User)
        >>> rows = s.generate(count=5)
        """
        from dataforge.schema import Schema

        try:
            import sqlalchemy  # noqa: F401
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "sqlalchemy is required for schema_from_sqlalchemy(). "
                "Install it with: pip install sqlalchemy"
            ) from exc

        if not hasattr(model, "__table__"):
            raise TypeError(
                f"Expected a SQLAlchemy declarative model with __table__, got {model!r}"
            )

        from dataforge.registry import get_field_map

        field_map = get_field_map()
        mapped: dict[str, str] = {}

        import warnings

        table = model.__table__
        for column in table.columns:
            col_name = column.name
            # Skip primary key 'id' columns — not fake-able
            if col_name == "id" and column.primary_key:
                continue
            if col_name in field_map:
                mapped[col_name] = col_name
            else:
                alias = _sqlalchemy_heuristic(col_name, column)
                if alias and alias in field_map:
                    mapped[col_name] = alias
                else:
                    warnings.warn(
                        f"SQLAlchemy column '{col_name}' on "
                        f"{model.__name__} could not be mapped to a "
                        f"DataForge field — skipping.",
                        UserWarning,
                        stacklevel=2,
                    )

        if not mapped:
            raise ValueError(
                f"No columns on {model.__name__} could be mapped to "
                f"DataForge fields. Ensure the model uses recognisable "
                f"column names (e.g. 'first_name', 'email', 'city')."
            )

        return Schema(self, mapped)
