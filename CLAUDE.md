# CLAUDE.md — DataForge Project Guide for AI Coding Agents

This file defines the project scope, architecture, and non-negotiable constraints for AI coding agents working in this repository. It mirrors `AGENTS.md` — keep both files in sync when editing. Read this fully before making any change.

---

## What This Project Is

**DataForge** is a high-performance, zero-dependency fake/synthetic data generator for Python, published on PyPI as `dataforge-py`. It is a ground-up, orders-of-magnitude-faster alternative to Faker, with a drop-in compatibility layer (`dataforge.compat.Faker`).

The project's identity rests on four pillars. **Every change must preserve all four:**

1. **Performance** — the primary selling point. ~18M items/s batch generation, ~343K rows/s schema generation. Performance regressions are release blockers.
2. **Zero runtime dependencies** — the core library (`pip install dataforge-py`) must remain stdlib-only. Never add a required dependency. Optional features live in extras (`[db]`, `[kafka]`, `[rabbitmq]`, `[tui]`, `[all]`) and must degrade gracefully with a clear error when the extra is missing.
3. **Stock Python** — supports Python >= 3.12 (CI tests 3.12 and 3.13). No C extensions, no Rust, no compiled components. Pure Python only.
4. **Extensibility** — providers, locales, and integrations are designed to be extended. New providers register declaratively; new locales are pure data modules; third-party providers can register via the `dataforge.providers` entry point group.

---

## Repository Layout

```
src/dataforge/
  core.py             # DataForge main class — entry point, provider wiring, schema/bulk/stream APIs
  backend.py          # RandomEngine — the single source of randomness (wraps random.Random)
  registry.py         # Provider auto-discovery, field resolution, entry-point loading
  schema.py           # Schema API — columnar-first generation, pre-resolved field lookups
  unique.py           # Three-layer unique proxy (set-based dedup + adaptive over-sampling)
  decorators.py       # define() dynamic fields, pipe() transform pipelines
  transforms.py       # Composable field transforms (casing, truncation, hashing, redaction)
  validation.py       # Data contract validation
  constraints.py      # Constraint engine (geographic, temporal, correlation, conditional)
  inference.py        # Schema inference + statistical distribution fitting
  timeseries.py       # Time-series generation (trend, seasonality, noise, anomalies)
  chaos.py            # Chaos testing (nulls, type mismatches, boundary values, encoding)
  anonymizer.py       # PII anonymization (HMAC-SHA256, format-preserving)
  seeder.py           # DatabaseSeeder (SQLAlchemy — optional extra)
  openapi.py          # OpenAPI / JSON Schema import
  streaming.py        # Streaming export (CSV/JSONL) + HTTP/Kafka/RabbitMQ sinks
  schema_io.py        # Schema save/load (YAML/JSON serialization)
  relational.py       # Multi-table relational generation with foreign keys
  cli.py              # `dataforge` CLI entry point
  pytest_plugin.py    # pytest fixtures (forge, fake, forge_unseeded) via pytest11 entry point
  providers/          # 30+ providers — one module per domain
    base.py           # BaseProvider — __slots__, _choice_fields auto-generation, registry metadata
  locales/            # 23 locales — one subpackage per locale, data stored as immutable tuples
  compat/
    faker.py          # Drop-in Faker replacement (57 method mappings)
    hypothesis.py     # Hypothesis strategy bridge
  tui/                # Interactive TUI (textual — optional extra)
tests/                # ~2000 tests, one test module per provider + one per feature module
examples/             # 21 numbered example scripts (01_timeseries.py ... 21_advanced_scenarios.py)
benchmark.py          # Performance benchmark suite — run before any perf-sensitive change
```

---

## Non-Negotiable Rules

### 1. Performance Rules (highest priority)

These come from the project's performance guidelines and are enforced in review:

- **Never regress benchmarks.** Run `uv run python benchmark.py --save after.json --compare before.json` for any change touching hot paths (`backend.py`, `core.py`, `schema.py`, `providers/`, `unique.py`, `streaming.py`).
- **`__slots__` on all classes.** No exceptions.
- **Immutable tuples for static data.** Locale data and constant pools are `tuple[str, ...]`, never `list`. Tuples compile to bytecode constants and are memory-efficient.
- **Batch paths are mandatory.** Every public generation method must accept `count=N` and use an optimized batch code path (e.g., `engine.choices(data, count)` — never a Python loop of single calls).
- **Inline hot paths.** Avoid unnecessary function calls inside batch loops. Module-level constants over per-call lookups.
- **Columnar-first generation.** Schema generates data column-by-column, then transposes to rows — preserve this architecture.
- **Use the fast primitives that already exist:** `csv.writer` (not `DictWriter`), cached cumulative weights for weighted choices, `binomialvariate()` + `random.sample()` for bulk null injection, `deque.popleft()` for BFS, in-place list mutation in `numerify()`/`bothify()`.

### 2. Dependency Rules

- **Core = stdlib only.** The `dependencies = []` array in `pyproject.toml` stays empty.
- New integrations go in `[project.optional-dependencies]` and the import must be lazy (inside the function/method that needs it) with a helpful `ImportError` message telling the user which extra to install.
- Optional deps already in use: `pyarrow`, `polars`, `pandas`, `pydantic`, `sqlalchemy`, `openpyxl`, `hypothesis`, `confluent-kafka`, `pika`, `textual`. Reuse these rather than adding new ones for the same job.

### 3. API Stability Rules

- The public API is everything documented in `README.md`: `DataForge`, all provider methods, `forge.schema(...)`, `forge.to_*`, `forge.stream_*`, `forge.unique.*`, `forge.compat.Faker`, the CLI flags, and the pytest fixtures.
- **Breaking changes require `feat!:` or a `BREAKING CHANGE:` footer** (release-please handles the major bump).
- The Faker compatibility layer must stay a faithful drop-in: existing mappings don't change behavior; new mappings only extend.
- Seeded output should remain stable within a release line — changing what `DataForge(seed=42)` produces breaks user tests. Treat deterministic output as a compat surface.

### 4. Type & Style Rules

- Full PEP 484 type hints; `@overload` triplets for `count` narrowing (no args → scalar, `Literal[1]` → scalar, `int` → list) where applicable.
- Lint: `uv run ruff check src/ tests/` must pass. Format: `uv run ruff format --check src/ tests/` must pass. Ruff config is minimal (`E4, E7, E9, F`) — don't expand it without discussion.
- Python `>=3.12` idioms are fine (e.g., `X | Y` unions, `match`).

### 5. Testing Rules

- Every new provider method, feature, or bug fix ships with tests in `tests/`. Current suite: ~2000 tests via `uv run pytest`.
- Tests must be deterministic — always seed the `DataForge` instance in tests.
- Integration tests for optional deps live in `tests/test_integrations.py` and are exercised by the Integrations workflow.

### 6. Commit & Release Rules

- **Conventional Commits are enforced by commitlint** (pre-commit hook + CI). Format: `<type>: <description>`.
- Types: `feat` (minor bump), `fix` (patch bump), `perf`, `refactor`, `test`, `docs`, `chore`.
- Releases are fully automated by **release-please**: merges to `main` update a Release PR; merging it tags a bare version (`0.5.0`) and publishes to PyPI via OIDC trusted publishing. **Never edit `CHANGELOG.md` or bump `pyproject.toml` version by hand.**

---

## How To Extend (the intended extension points)

### Adding a provider

1. Create `src/dataforge/providers/<name>.py` with a class extending `BaseProvider`.
2. Set `_provider_name`, `_locale_modules` (or `()` if locale-independent), `_field_map`, and prefer declarative `_choice_fields` for simple random-choice methods (auto-generated, zero boilerplate, same performance as hand-written).
3. Register in `pyproject.toml` under `[project.entry-points."dataforge.providers"]` **and** in the import list in `registry.py`.
4. Add `tests/test_<name>.py`.
5. Update `README.md` provider docs.

### Adding a locale

1. Create `src/dataforge/locales/<locale>/` with one data module per locale-dependent provider (`person.py`, `address.py`, `company.py`, `internet.py`, `phone.py` — match the existing structure).
2. All data as module-level `tuple[str, ...]` constants.
3. Locales load lazily — only when first accessed. Keep it that way.

### Adding an integration

Lazy import inside the method, clear `ImportError` naming the extra, add to optional-dependencies and the Integrations CI workflow, document in README with a copy-pasteable snippet.

---

## Development Commands

```bash
uv sync                                        # install everything
uv run pytest                                  # full test suite (~2000 tests)
uv run pytest tests/test_person.py             # single module
uv run ruff check src/ tests/                  # lint
uv run ruff format --check src/ tests/         # format check
uv run python benchmark.py                     # run benchmarks
uv run python benchmark.py --save base.json    # save baseline
uv run python benchmark.py --compare base.json # compare against baseline
```

CI (GitHub Actions): `ci.yml` (commitlint + ruff + pytest on 3.12/3.13), `integrations.yml` (optional deps), `benchmarks.yml` (perf comparison on main), `release-please.yml` + `publish.yml` (automated PyPI releases).

---

## When In Doubt

- Favor the existing pattern over a new one — look at `providers/person.py` (locale-backed) or `providers/misc.py` (self-contained) as canonical examples.
- If a change would trade performance for elegance, keep the performance and document the trade-off in a comment.
- If you're unsure whether something is a hot path, assume it is.
