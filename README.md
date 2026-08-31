# DataForge

[![PyPI version](https://img.shields.io/pypi/v/dataforge-py.svg)](https://pypi.org/project/dataforge-py/)
[![Python versions](https://img.shields.io/pypi/pyversions/dataforge-py.svg)](https://pypi.org/project/dataforge-py/)
[![CI](https://github.com/Sanady/dataforge-py/actions/workflows/ci.yml/badge.svg)](https://github.com/Sanady/dataforge-py/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**The fastest fake data generator for Python. Zero dependencies. 18M items/second. Drop-in Faker replacement.**

```bash
pip install dataforge-py
```

```python
from dataforge import DataForge

forge = DataForge(seed=42)

forge.person.full_name()                  # "James Smith"
forge.internet.email()                    # "james.smith@gmail.com"
forge.person.first_name(count=1_000_000)  # 1M names in ~55ms
```

---

## Why DataForge?

| | DataForge | Faker |
|---|---|---|
| **Throughput** | **18M items/s** | ~50K items/s |
| **Dependencies** | **Zero** | 3+ |
| **Batch generation** | `count=N` on every method | Loop manually |
| **Schema API** | Built-in, columnar | Third-party |
| **Bulk export** | CSV, JSONL, SQL, Parquet, Arrow, Polars | None |
| **CLI** | Built-in | None |
| **Pytest plugin** | Built-in fixtures | Third-party |
| **Type hints** | Full PEP 484 + `@overload` | Partial |
| **Migration effort** | `from dataforge.compat import Faker` | — |

DataForge isn't a wrapper around Faker — it's a ground-up rewrite with vectorized batch paths, pre-resolved field lookups, lazy locale loading, and columnar-first schema generation. If you're generating more than a few hundred records, the difference is measurable in orders of magnitude.

---

## Quick Start

### Single values

```python
from dataforge import DataForge

forge = DataForge(locale="en_US", seed=42)

forge.person.first_name()     # "James"
forge.internet.email()        # "james.smith@gmail.com"
forge.address.city()          # "Chicago"
forge.finance.price()         # "49.99"
forge.llm.model_name()        # "gpt-4o"
```

### Batch generation

Every method accepts `count=N` and returns a list:

```python
names  = forge.person.first_name(count=1000)
emails = forge.internet.email(count=1000)
cities = forge.address.city(count=1000)
```

### Reproducible output

```python
forge_a = DataForge(seed=42)
forge_b = DataForge(seed=42)
assert forge_a.person.first_name() == forge_b.person.first_name()
```

### Migrating from Faker

Change one import. Keep your existing code:

```python
# Before
# from faker import Faker

# After — same API, ~360x faster
from dataforge.compat import Faker

fake = Faker(locale="en_US", seed=42)
fake.name()     # "James Smith"
fake.email()    # "james.smith@gmail.com"
fake.address()  # "4821 Oak Ave, Chicago, IL 60614"
```

57 Faker methods are mapped. Unknown methods fall back to alias lookup, then direct field matching.

---

## Schema API

Define reusable blueprints for structured data generation:

```python
schema = forge.schema({
    "Name": "person.full_name",
    "Email": "internet.email",
    "City": "address.city",
    "Price": "finance.price",
})

rows = schema.generate(1000)        # list[dict]
csv_str = schema.to_csv(count=5000)
sql_str = schema.to_sql(count=5000, table="users")
df = schema.to_dataframe(count=5000)  # requires pandas
```

Row-dependent fields for correlated data:

```python
schema = forge.schema({
    "City": "address.city",
    "Greeting": lambda row: f"Hello from {row['City']}!",
})
```

---

## Bulk Export

```python
# List of dicts
rows = forge.to_dict(fields=["first_name", "email"], count=100)

# CSV
forge.to_csv(fields={"Name": "person.full_name"}, count=5000, path="users.csv")

# JSONL
forge.to_jsonl(fields=["first_name", "email"], count=1000, path="users.jsonl")

# SQL INSERT statements
forge.to_sql(fields=["first_name", "email"], count=500, table="users", dialect="postgresql")

# Pandas / PyArrow / Polars / Parquet (requires optional deps)
df = forge.to_dataframe(fields=["first_name"], count=10_000)
table = forge.to_arrow(fields=["first_name"], count=1_000_000)
df = forge.to_polars(fields=["first_name"], count=1_000_000)
forge.to_parquet(fields=["first_name"], path="out.parquet", count=1_000_000)
```

### Streaming Export

For datasets that don't fit in memory:

```python
forge.stream_to_csv(fields=["first_name", "email"], path="users.csv", count=10_000_000)
forge.stream_to_jsonl(fields=["first_name", "email"], path="users.jsonl", count=10_000_000)
```

---

## CLI

Generate data from the terminal — no Python required:

```bash
dataforge --count 10 --format csv first_name last_name email
dataforge -n 100 -f jsonl -o users.jsonl first_name email city
dataforge --locale fr_FR --seed 42 -n 5 first_name city
dataforge --list-fields
```

| Flag | Short | Description |
|------|-------|-------------|
| `--count N` | `-n` | Number of rows (default: 10) |
| `--format FMT` | `-f` | `text`, `csv`, `json`, `jsonl` |
| `--locale LOC` | `-l` | Locale code (default: `en_US`) |
| `--seed S` | `-s` | Random seed |
| `--output PATH` | `-o` | Write to file |
| `--no-header` | | Omit header row |
| `--list-fields` | | List all available fields |

---

## Pytest Plugin

Auto-registers via `pytest11` entry point. Three fixtures, zero config:

```python
def test_name(forge):
    assert isinstance(forge.person.first_name(), str)

def test_email(fake):  # alias for forge
    assert "@" in fake.internet.email()

@pytest.mark.forge_seed(42)
def test_deterministic(forge):
    assert forge.person.first_name() == "James"
```

```bash
pytest --forge-seed 42  # session-wide seed
```

---

## 27 Providers, 198 Methods

Every method accepts `count=N` for batch generation.

<details>
<summary><strong>person, address, internet, company, phone, finance, datetime</strong> — Core providers</summary>

### `person`

| Method | Example |
|--------|---------|
| `first_name()` | `"James"` |
| `last_name()` | `"Smith"` |
| `full_name()` | `"James Smith"` |
| `male_first_name()` | `"Robert"` |
| `female_first_name()` | `"Jennifer"` |
| `prefix()` | `"Mr."` |
| `suffix()` | `"Jr."` |

### `address`

| Method | Example |
|--------|---------|
| `street_name()` | `"Elm Street"` |
| `street_address()` | `"742 Elm Street"` |
| `city()` | `"Chicago"` |
| `state()` | `"California"` |
| `zip_code()` | `"90210"` |
| `full_address()` | `"742 Elm St, Chicago, IL 90210"` |
| `country()` | `"United States"` |
| `country_code()` | `"US"` |
| `latitude()` / `longitude()` | `"41.8781"` / `"-87.6298"` |

### `internet`

| Method | Example |
|--------|---------|
| `email()` | `"james.smith@gmail.com"` |
| `safe_email()` | `"james@example.com"` |
| `username()` | `"jsmith42"` |
| `domain()` | `"example.com"` |
| `url()` | `"https://example.com"` |
| `ipv4()` | `"192.168.1.1"` |
| `slug()` | `"lorem-ipsum-dolor"` |

### `company`

| Method | Example |
|--------|---------|
| `company_name()` | `"Acme Corp"` |
| `job_title()` | `"Software Engineer"` |
| `catch_phrase()` | `"Innovative solutions"` |

### `phone`

| Method | Example |
|--------|---------|
| `phone_number()` | `"(555) 123-4567"` |
| `cell_phone()` | `"555-987-6543"` |

### `finance`

| Method | Example |
|--------|---------|
| `credit_card_number()` | `"4532015112830366"` |
| `iban()` | `"DE89370400440532013000"` |
| `bic()` | `"DEUTDEFFXXX"` |
| `price(min_val, max_val)` | `"49.99"` |
| `currency_code()` | `"USD"` |
| `bitcoin_address()` | `"1A1zP1eP5QGefi2DMPTfTL..."` |

### `dt` (datetime)

| Method | Example |
|--------|---------|
| `date(start, end, fmt)` | `"2024-03-15"` |
| `datetime(start, end, fmt)` | `"2024-03-15 14:30:00"` |
| `date_of_birth(min_age, max_age)` | `"1990-05-12"` |
| `timezone()` | `"US/Eastern"` |
| `unix_timestamp(start, end)` | `1710504600` |

</details>

<details>
<summary><strong>color, file, network, lorem, barcode, misc</strong> — Utility providers</summary>

### `color`

| Method | Example |
|--------|---------|
| `color_name()` | `"red"` |
| `hex_color()` | `"#ff5733"` |
| `rgb_color()` | `"rgb(255, 87, 51)"` |

### `file`

| Method | Example |
|--------|---------|
| `file_name()` | `"report.pdf"` |
| `file_extension()` | `"pdf"` |
| `mime_type()` | `"application/pdf"` |

### `network`

| Method | Example |
|--------|---------|
| `mac_address()` | `"00:1B:44:11:3A:B7"` |
| `user_agent()` | `"Mozilla/5.0 ..."` |
| `port()` | `8080` |

### `lorem`

| Method | Example |
|--------|---------|
| `word()` | `"lorem"` |
| `sentence()` | `"Lorem ipsum dolor sit amet."` |
| `paragraph()` | `"Lorem ipsum dolor sit amet, ..."` |
| `text()` | Multi-paragraph string |

### `barcode`

| Method | Example |
|--------|---------|
| `ean13()` | `"5901234123457"` |
| `ean8()` | `"96385074"` |
| `upc_a()` | `"012345678905"` |

### `misc`

| Method | Example |
|--------|---------|
| `boolean()` | `True` |
| `uuid4()` | `"f47ac10b-58cc-..."` |
| `md5()` / `sha1()` / `sha256()` | Hex digest strings |
| `password()` | `"aB3$xK9p"` |

</details>

<details>
<summary><strong>automotive, crypto, ecommerce, education, geo, government, medical, payment, profile, science, text</strong> — Domain providers</summary>

### `automotive`

| Method | Example |
|--------|---------|
| `vin()` | `"1HGBH41JXMN109186"` |
| `license_plate()` | `"ABC-1234"` |

### `crypto`

| Method | Example |
|--------|---------|
| `bitcoin_address()` | `"1A1zP1eP5QGefi2..."` |
| `ethereum_address()` | `"0x742d35Cc6634C0532925a3b8D..."` |

### `ecommerce`

| Method | Example |
|--------|---------|
| `product_name()` | `"Wireless Bluetooth Headphones"` |
| `category()` | `"Electronics"` |
| `sku()` | `"ELC-2847-BLK"` |

### `education`

| Method | Example |
|--------|---------|
| `university()` | `"MIT"` |
| `degree()` | `"Bachelor of Science"` |
| `course_name()` | `"Introduction to Computer Science"` |

### `geo`

| Method | Example |
|--------|---------|
| `continent()` | `"North America"` |
| `timezone_name()` | `"America/Chicago"` |

### `government`

| Method | Example |
|--------|---------|
| `ssn()` | `"123-45-6789"` |
| `passport_number()` | `"X1234567"` |

### `medical`

| Method | Example |
|--------|---------|
| `blood_type()` | `"O+"` |
| `diagnosis()` | `"Hypertension"` |
| `medication()` | `"Lisinopril"` |

### `payment`

| Method | Example |
|--------|---------|
| `credit_card()` | `{"type": "Visa", "number": "...", ...}` |
| `card_type()` | `"Visa"` |

### `profile`

| Method | Example |
|--------|---------|
| `profile()` | Full profile dict |
| `simple_profile()` | Simplified profile dict |

### `science`

| Method | Example |
|--------|---------|
| `chemical_element()` | `"Carbon"` |
| `scientist()` | `"Marie Curie"` |

### `text`

| Method | Example |
|--------|---------|
| `sentence()` | Contextual sentence |
| `paragraph()` | Contextual paragraph |

</details>

<details>
<summary><strong>ai_prompt, llm, ai_chat</strong> — AI/LLM providers</summary>

### `ai_prompt`

| Method | Example |
|--------|---------|
| `system_prompt()` | `"You are a helpful assistant..."` |
| `user_prompt()` | `"Explain quantum computing..."` |

### `llm`

| Method | Example |
|--------|---------|
| `model_name()` | `"gpt-4o"` |
| `provider()` | `"OpenAI"` |
| `token_count()` | `1024` |

### `ai_chat`

| Method | Example |
|--------|---------|
| `conversation()` | Multi-turn chat dict |
| `message()` | Single chat message dict |

</details>

---

## 17 Locales

```python
forge = DataForge(locale="fr_FR")
forge.address.city()      # "Paris"
forge.person.full_name()  # "Jean Dupont"

forge = DataForge(locale="ja_JP")
forge.person.full_name()  # "田中太郎"
```

| | | | |
|---|---|---|---|
| `en_US` | `en_GB` | `en_AU` | `en_CA` |
| `de_DE` | `fr_FR` | `es_ES` | `it_IT` |
| `pt_BR` | `nl_NL` | `pl_PL` | `ru_RU` |
| `ar_SA` | `hi_IN` | `ja_JP` | `ko_KR` |
| `zh_CN` | | | |

Multi-locale mixing:

```python
forge = DataForge(locale=["en_US", "fr_FR", "de_DE"])
forge.person.full_name()  # randomly picks a locale per call
```

---

## Unique Values

```python
name1 = forge.unique.person.first_name()
name2 = forge.unique.person.first_name()
assert name1 != name2

names = forge.unique.person.first_name(count=100)
assert len(names) == len(set(names))

forge.unique.clear()  # reset tracking
```

Uses adaptive over-sampling — starts at 20% extra and scales with collision rate.

---

## Advanced Features

<details>
<summary><strong>Dynamic Fields (define())</strong> — Custom data pools and generators</summary>

```python
from dataforge import define

schema = forge.schema({
    "Status": define(["active", "inactive", "pending"]),
    "Priority": define(["low", "medium", "high"], weights=[0.5, 0.3, 0.2]),
    "Score": define(lambda: forge.misc.boolean()),
})
```

</details>

<details>
<summary><strong>Transform Pipelines (pipe())</strong> — Post-generation data transformation</summary>

```python
from dataforge import pipe

schema = forge.schema({
    "Username": pipe("internet.username", str.upper),
    "Bio": pipe("lorem.sentence", lambda s: s[:50]),
})
```

</details>

<details>
<summary><strong>Type-Driven Schema</strong> — Generate from dataclasses and TypedDicts</summary>

```python
from dataclasses import dataclass

@dataclass
class User:
    first_name: str
    last_name: str
    email: str

schema = forge.schema_from_dataclass(User)
rows = schema.generate(1000)
```

</details>

<details>
<summary><strong>Data Contract Validation</strong> — Semantic pattern and constraint checking</summary>

```python
from dataforge.validation import validate

errors = validate(rows, {
    "email": {"pattern": r"^[^@]+@[^@]+\.[^@]+$"},
    "name": {"non_empty": True},
})
```

</details>

<details>
<summary><strong>Hypothesis Strategy Bridge</strong> — Property-based testing integration</summary>

```python
from dataforge.hypothesis import strategy

@given(strategy("person.full_name"))
def test_name_format(name):
    assert " " in name
```

</details>

<details>
<summary><strong>HTTP Mock Data Server</strong> — Zero-dependency JSON API</summary>

```bash
dataforge --serve --port 8080
curl http://localhost:8080/api/users?count=10
```

</details>

<details>
<summary><strong>XLSX Export</strong> — Excel spreadsheet generation</summary>

```python
schema.to_excel(count=5000, path="users.xlsx")
```

Requires `openpyxl`.

</details>

<details>
<summary><strong>Statistical Distribution Fitting</strong> — Infer distributions from data</summary>

```python
from dataforge.inference import fit_distribution

fit = fit_distribution(data)
# Normal, LogNormal, Exponential, Beta, Zipf
```

</details>

<details>
<summary><strong>Time-Series Generation</strong> — Trends, seasonality, anomalies</summary>

```python
from dataforge.timeseries import TimeSeriesGenerator

ts = TimeSeriesGenerator(forge)
data = ts.generate(points=1000, trend="linear", seasonality="daily", noise=0.1)
```

</details>

<details>
<summary><strong>Schema Inference</strong> — Auto-detect types from CSV, DataFrames, records</summary>

```python
schema = forge.infer_schema(records)
schema = forge.infer_schema_from_csv("data.csv")
```

</details>

<details>
<summary><strong>Chaos Testing</strong> — Inject data quality issues</summary>

```python
from dataforge.chaos import ChaosConfig

chaos = ChaosConfig(null_rate=0.05, type_mismatch_rate=0.02)
rows = forge.with_chaos(chaos).to_dict(fields=["first_name", "email"], count=1000)
```

</details>

<details>
<summary><strong>Constraint Engine</strong> — Geographic, temporal, statistical constraints</summary>

```python
from dataforge.constraints import Constraint

schema = forge.schema({
    "City": "address.city",
    "State": Constraint("address.state", depends_on="City"),
})
```

</details>

<details>
<summary><strong>PII Anonymization</strong> — HMAC-SHA256 with format preservation</summary>

```python
from dataforge.anonymizer import Anonymizer

anon = Anonymizer(key="secret")
anon.anonymize(rows, fields=["email", "ssn"])
```

</details>

<details>
<summary><strong>Database Seeding</strong> — SQLAlchemy-powered bulk insertion</summary>

```python
from dataforge.seeder import DatabaseSeeder

seeder = DatabaseSeeder(engine)
seeder.seed(User, count=10_000)
```

</details>

<details>
<summary><strong>OpenAPI / JSON Schema Import</strong> — Generate from API specs</summary>

```python
schema = forge.schema_from_openapi("openapi.json")
schema = forge.schema_from_json_schema("schema.json")
```

</details>

<details>
<summary><strong>Streaming to Message Queues</strong> — HTTP, Kafka, RabbitMQ</summary>

```python
forge.stream_to_http(fields=["first_name"], url="http://api.example.com", count=1000)
forge.stream_to_kafka(fields=["first_name"], topic="users", count=1000)
forge.stream_to_rabbitmq(fields=["first_name"], queue="users", count=1000)
```

</details>

<details>
<summary><strong>Interactive TUI</strong> — Terminal UI for browsing and exporting</summary>

```bash
dataforge --tui
```

Requires `textual`.

</details>

---

## Integrations

### PyArrow

```python
table = forge.to_arrow(fields=["first_name", "email"], count=1_000_000)
forge.to_parquet(fields=["first_name", "email"], path="users.parquet", count=1_000_000)
```

### Polars

```python
df = forge.to_polars(fields=["first_name", "email"], count=1_000_000)
```

### Pydantic

```python
from pydantic import BaseModel

class User(BaseModel):
    first_name: str
    email: str

schema = forge.schema_from_pydantic(User)
rows = schema.generate(1000)
```

### SQLAlchemy

```python
schema = forge.schema_from_sqlalchemy(User)
rows = schema.generate(1000)  # primary keys auto-skipped
```

---

## Benchmarks

Measured on a standard developer machine:

| Operation | Throughput |
|-----------|-----------|
| `misc.boolean()` | **8.5M items/s** |
| `person.first_name()` | **3.7M items/s** |
| `address.city()` | **3.4M items/s** |
| `person.first_name(count=1M)` | **15M items/s** |
| `dt.timezone(count=1M)` | **18M items/s** |
| `network.user_agent(count=1M)` | **18M items/s** |
| Schema `generate(100K)` | **343K rows/s** |
| Schema `to_csv(100K)` | **312K rows/s** |

Run locally:

```bash
uv run python benchmark.py
uv run python benchmark.py --compare  # against saved baseline
```

<details>
<summary><strong>Performance architecture details</strong></summary>

- **Columnar generation** — Schema generates column-first, then transposes to rows
- **`csv.writer` over `csv.DictWriter`** — ~36% faster CSV writes
- **Cumulative weight caching** — weighted choices cache at module level
- **Bulk null injection** — `binomialvariate()` + `random.sample()` instead of per-element flips
- **Vectorized batch paths** — internet, datetime, finance providers use dedicated batch code
- **`deque` for BFS traversal** — O(1) `popleft()` in relational generation
- **Adaptive unique over-sampling** — scales with observed collision rate
- **In-place list mutation** — `numerify()`/`bothify()` avoid re-allocation

</details>

---

## Examples

The [`examples/`](examples/) directory contains 21 runnable scripts covering every feature:

| File | Topic |
|------|-------|
| [`01_timeseries.py`](examples/01_timeseries.py) | IoT sensor monitoring with regime changes |
| [`02_schema_inference.py`](examples/02_schema_inference.py) | Auto-detect schemas from records and CSV |
| [`03_chaos_testing.py`](examples/03_chaos_testing.py) | Data quality issue injection |
| [`04_constraints.py`](examples/04_constraints.py) | Geographic, temporal, correlation constraints |
| [`05_anonymizer.py`](examples/05_anonymizer.py) | PII masking with referential integrity |
| [`06_database_seeding.py`](examples/06_database_seeding.py) | SQLAlchemy introspection and seeding |
| [`07_openapi_import.py`](examples/07_openapi_import.py) | Generate from JSON Schema / OpenAPI specs |
| [`08_streaming.py`](examples/08_streaming.py) | HTTP/Kafka/RabbitMQ streaming |
| [`09_tui.py`](examples/09_tui.py) | Interactive TUI |
| [`10_real_world_scenarios.py`](examples/10_real_world_scenarios.py) | E-commerce, healthcare, IoT, API testing |
| [`11_faker_compat.py`](examples/11_faker_compat.py) | Faker migration |
| [`12_multi_locale.py`](examples/12_multi_locale.py) | Multi-locale generation |
| [`13_dynamic_fields.py`](examples/13_dynamic_fields.py) | Custom data pools with `define()` |
| [`14_transform_pipelines.py`](examples/14_transform_pipelines.py) | Transform chains with `pipe()` |
| [`15_type_driven_schema.py`](examples/15_type_driven_schema.py) | Dataclass / TypedDict schemas |
| [`16_data_validation.py`](examples/16_data_validation.py) | Data contract validation |
| [`17_hypothesis_bridge.py`](examples/17_hypothesis_bridge.py) | Hypothesis property-based testing |
| [`18_mock_server.py`](examples/18_mock_server.py) | HTTP mock data server |
| [`19_xlsx_export.py`](examples/19_xlsx_export.py) | Excel spreadsheet generation |
| [`20_distribution_fitting.py`](examples/20_distribution_fitting.py) | Statistical distribution inference |
| [`21_advanced_scenarios.py`](examples/21_advanced_scenarios.py) | Multi-feature workflows |

---

## Installation

```bash
pip install dataforge-py        # zero dependencies
uv add dataforge-py             # with uv
```

Optional extras:

```bash
pip install dataforge-py[db]       # SQLAlchemy (database seeding)
pip install dataforge-py[kafka]    # confluent-kafka
pip install dataforge-py[rabbitmq] # pika
pip install dataforge-py[tui]      # textual (interactive TUI)
pip install dataforge-py[all]      # everything
```

Optional integrations (install separately):

```bash
pip install pyarrow polars pandas pydantic sqlalchemy openpyxl hypothesis
```

**Requires Python >= 3.12.**

---

## Contributing

Contributions welcome. See an issue? Open one. Want to add a provider or locale? PRs appreciated.

```bash
git clone https://github.com/Sanady/dataforge-py.git
cd dataforge-py
uv sync
uv run pytest          # 1870 tests
uv run ruff check src/ tests/
uv run python benchmark.py
```

All commits use [Conventional Commits](https://www.conventionalcommits.org/). Performance is the primary selling point — all PRs must pass `benchmark.py --compare` without regressions.

If DataForge saves you time, a star helps others find it.

---

## License

[MIT](LICENSE)
