"""Schema inference — analyze data and auto-create matching Schemas."""

from __future__ import annotations

import math as _math
import re as _re
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from dataforge.core import DataForge

_SEMANTIC_PATTERNS: list[tuple[str, _re.Pattern[str], str]] = [
    ("email", _re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$"), "email"),
    ("phone", _re.compile(r"^[\+]?[\d\s\-\(\)]{7,20}$"), "phone_number"),
    (
        "uuid",
        _re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", _re.I
        ),
        "uuid4",
    ),
    ("ipv4", _re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"), "ipv4"),
    ("ipv6", _re.compile(r"^[0-9a-f:]{3,39}$", _re.I), "ipv6"),
    ("url", _re.compile(r"^https?://[^\s]+$"), "url"),
    ("mac", _re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$"), "mac_address"),
    ("date_iso", _re.compile(r"^\d{4}-\d{2}-\d{2}$"), "date"),
    ("datetime_iso", _re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}"), "datetime"),
    ("time_iso", _re.compile(r"^\d{2}:\d{2}(:\d{2})?$"), "time"),
    ("zipcode_us", _re.compile(r"^\d{5}(-\d{4})?$"), "zip_code"),
    ("ssn", _re.compile(r"^\d{3}-\d{2}-\d{4}$"), "ssn"),
    (
        "credit_card",
        _re.compile(r"^\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}$"),
        "credit_card_number",
    ),
    ("hex_color", _re.compile(r"^#[0-9a-fA-F]{6}$"), "hex_color"),
    ("ean13", _re.compile(r"^\d{13}$"), "ean13"),
    ("isbn", _re.compile(r"^97[89]-?\d{1,5}-?\d{1,7}-?\d{1,7}-?\d$"), "isbn13"),
]

_CACHED_ALIASES: dict[str, str] | None = None


def _get_field_aliases() -> dict[str, str]:
    """Import and return field aliases from core (cached after first call)."""
    global _CACHED_ALIASES
    if _CACHED_ALIASES is None:
        from dataforge.core import _FIELD_ALIASES

        _CACHED_ALIASES = _FIELD_ALIASES
    return _CACHED_ALIASES


_INT_PATTERN = _re.compile(r"^-?\d+$")
_FLOAT_PATTERN = _re.compile(r"^-?\d+\.\d*$|^-?\d*\.\d+$|^-?\d+[eE][+-]?\d+$")


def _detect_base_type(values: list[Any]) -> str:
    """Detect the base type of a column's values."""
    type_counts: dict[str, int] = {}
    _int_match = _INT_PATTERN.match
    _float_match = _FLOAT_PATTERN.match
    for val in values:
        if val is None or (isinstance(val, str) and val.strip() == ""):
            type_counts["none"] = type_counts.get("none", 0) + 1
            continue
        t = type(val).__name__
        if t == "str":
            s = val.strip()
            if _int_match(s):
                type_counts["int"] = type_counts.get("int", 0) + 1
                continue
            if _float_match(s):
                type_counts["float"] = type_counts.get("float", 0) + 1
                continue
            if s.lower() in ("true", "false", "yes", "no"):
                type_counts["bool"] = type_counts.get("bool", 0) + 1
                continue
        type_counts[t] = type_counts.get(t, 0) + 1

    non_none = {k: v for k, v in type_counts.items() if k != "none"}
    if not non_none:
        return "none"
    dominant = max(non_none, key=lambda k: non_none[k])
    total_non_none = sum(non_none.values())
    if non_none[dominant] / total_non_none >= 0.8:
        return dominant
    return "mixed"


def _detect_semantic_type(
    col_name: str,
    values: list[Any],
    base_type: str,
) -> str | None:
    """Detect the semantic type of a column."""
    aliases = _get_field_aliases()
    name_lower = col_name.lower().strip().replace(" ", "_")
    if name_lower in aliases:
        return aliases[name_lower]

    for prefix in ("user_", "customer_", "order_", "item_"):
        if name_lower.startswith(prefix):
            stripped = name_lower[len(prefix) :]
            if stripped in aliases:
                return aliases[stripped]

    if base_type == "str":
        sample = [str(v) for v in values if v is not None and str(v).strip()][:100]
        if sample:
            for _name, pattern, field in _SEMANTIC_PATTERNS:
                matches = sum(1 for s in sample if pattern.match(s))
                if matches / len(sample) >= 0.7:
                    return field

    if base_type == "bool":
        return "boolean"
    if base_type == "int":
        if "age" in name_lower:
            return "misc.random_int"
        if "port" in name_lower:
            return "port"
        if "year" in name_lower:
            return "date"

    return None


def _compute_null_rate(values: list[Any]) -> float:
    """Compute the null/empty rate of a column."""
    if not values:
        return 0.0
    n_null = sum(
        1 for v in values if v is None or (isinstance(v, str) and v.strip() == "")
    )
    return round(n_null / len(values), 3)


def _compute_stats(values: list[Any], base_type: str) -> dict[str, Any]:
    """Compute basic statistics for a column."""
    stats: dict[str, Any] = {"count": len(values)}

    if base_type in ("int", "float"):
        nums = []
        for v in values:
            if v is None:
                continue
            try:
                nums.append(float(v))
            except (ValueError, TypeError):
                pass
        if nums:
            stats["min"] = min(nums)
            stats["max"] = max(nums)
            stats["mean"] = sum(nums) / len(nums)
            stats["unique"] = len(set(nums))

    elif base_type == "str":
        strs = [str(v) for v in values if v is not None]
        if strs:
            lengths = [len(s) for s in strs]
            stats["min_length"] = min(lengths)
            stats["max_length"] = max(lengths)
            stats["avg_length"] = round(sum(lengths) / len(lengths), 1)
            stats["unique"] = len(set(strs))

    return stats


# ---------------------------------------------------------------------------
# Distribution fitting — pure stdlib, no scipy
# ---------------------------------------------------------------------------


def _fit_distribution(values: list[Any], base_type: str) -> dict[str, Any] | None:
    """Detect the best-fitting distribution for numeric data (stdlib only).

    Checks: Normal, LogNormal, Exponential, Beta, Zipf.
    Returns a dict with ``{"name": ..., "params": {...}}`` or ``None``.
    """
    if base_type not in ("int", "float"):
        return None

    nums: list[float] = []
    for v in values:
        if v is None:
            continue
        try:
            nums.append(float(v))
        except (ValueError, TypeError):
            pass

    n = len(nums)
    if n < 20:
        return None

    mean = sum(nums) / n
    var = sum((x - mean) ** 2 for x in nums) / n
    std = _math.sqrt(var) if var > 0 else 0.0

    if std < 1e-12:
        return None

    # --- Normality test (Jarque-Bera, simplified) ---
    skew = sum((x - mean) ** 3 for x in nums) / (n * std**3) if std > 0 else 0
    kurtosis = sum((x - mean) ** 4 for x in nums) / (n * std**4) - 3.0 if std > 0 else 0
    jb = n / 6 * (skew**2 + kurtosis**2 / 4)

    # --- Check if all positive (needed for LogNormal, Exponential, Beta) ---
    min_val = min(nums)
    max_val = max(nums)
    all_positive = min_val > 0

    best: dict[str, Any] | None = None
    best_score = float("inf")

    # Normal: JB ≈ 0 means normal
    normal_score = jb
    if normal_score < best_score:
        best_score = normal_score
        best = {
            "name": "normal",
            "params": {"mean": round(mean, 4), "std": round(std, 4)},
        }

    # LogNormal: if all positive, check log-normality
    if all_positive:
        log_vals = [_math.log(x) for x in nums]
        log_mean = sum(log_vals) / n
        log_var = sum((x - log_mean) ** 2 for x in log_vals) / n
        log_std = _math.sqrt(log_var) if log_var > 0 else 0.0
        if log_std > 1e-12:
            log_skew = sum((x - log_mean) ** 3 for x in log_vals) / (n * log_std**3)
            log_kurt = (
                sum((x - log_mean) ** 4 for x in log_vals) / (n * log_std**4) - 3.0
            )
            log_jb = n / 6 * (log_skew**2 + log_kurt**2 / 4)
            if log_jb < best_score:
                best_score = log_jb
                best = {
                    "name": "lognormal",
                    "params": {"mu": round(log_mean, 4), "sigma": round(log_std, 4)},
                }

    # Exponential: check if data matches (memoryless, all positive)
    if all_positive and skew > 1.5:
        # For exponential, skewness ≈ 2, kurtosis ≈ 6
        exp_score = abs(skew - 2.0) + abs(kurtosis - 6.0) / 3
        if exp_score < best_score:
            best_score = exp_score
            rate = 1.0 / mean if mean > 0 else 1.0
            best = {
                "name": "exponential",
                "params": {"rate": round(rate, 4)},
            }

    # Beta: values in (0, 1) range
    if all_positive and max_val <= 1.0:
        sample_mean = mean
        sample_var = var
        if sample_var < sample_mean * (1 - sample_mean):
            common = sample_mean * (1 - sample_mean) / sample_var - 1
            alpha = sample_mean * common
            beta_param = (1 - sample_mean) * common
            if alpha > 0 and beta_param > 0:
                beta_score = abs(skew) + abs(kurtosis) / 2
                if beta_score < best_score:
                    best_score = beta_score
                    best = {
                        "name": "beta",
                        "params": {
                            "alpha": round(alpha, 4),
                            "beta": round(beta_param, 4),
                        },
                    }

    # Zipf: check if data is integer, positive, and heavy-tailed
    if base_type == "int" and all_positive and min_val >= 1:
        int_vals = sorted([int(x) for x in nums])
        if int_vals[-1] > 1:
            # Estimate Zipf parameter via log-log regression
            from collections import Counter

            freq = Counter(int_vals)
            ranks = sorted(freq.keys())
            if len(ranks) >= 5:
                log_r = [_math.log(r) for r in ranks]
                log_f = [_math.log(freq[r]) for r in ranks]
                n_pts = len(ranks)
                mean_lr = sum(log_r) / n_pts
                mean_lf = sum(log_f) / n_pts
                num = sum(
                    (log_r[i] - mean_lr) * (log_f[i] - mean_lf) for i in range(n_pts)
                )
                den = sum((log_r[i] - mean_lr) ** 2 for i in range(n_pts))
                if den > 0:
                    slope = num / den
                    if slope < -0.5:  # Zipf-like negative slope
                        s_param = -slope
                        # Compute R² for goodness of fit
                        ss_res = sum(
                            (log_f[i] - (mean_lf + slope * (log_r[i] - mean_lr))) ** 2
                            for i in range(n_pts)
                        )
                        ss_tot = sum((log_f[i] - mean_lf) ** 2 for i in range(n_pts))
                        r_sq = 1 - ss_res / ss_tot if ss_tot > 0 else 0
                        if r_sq > 0.8:
                            zipf_score = (1 - r_sq) * 10
                            if zipf_score < best_score:
                                best_score = zipf_score
                                best = {
                                    "name": "zipf",
                                    "params": {"s": round(s_param, 4)},
                                }

    return best


class ColumnAnalysis:
    """Analysis result for a single column."""

    __slots__ = (
        "name",
        "base_type",
        "semantic_type",
        "null_rate",
        "stats",
        "dataforge_field",
        "distribution",
    )

    def __init__(
        self,
        name: str,
        base_type: str,
        semantic_type: str | None,
        null_rate: float,
        stats: dict[str, Any],
        dataforge_field: str | None,
        distribution: dict[str, Any] | None = None,
    ) -> None:
        self.name = name
        self.base_type = base_type
        self.semantic_type = semantic_type
        self.null_rate = null_rate
        self.stats = stats
        self.dataforge_field = dataforge_field
        self.distribution = distribution

    def __repr__(self) -> str:
        dist_str = f", dist={self.distribution['name']}" if self.distribution else ""
        return (
            f"ColumnAnalysis(name={self.name!r}, type={self.base_type}, "
            f"semantic={self.semantic_type!r}, field={self.dataforge_field!r}{dist_str})"
        )


class SchemaInferrer:
    """Analyze data sources and build matching DataForge Schemas."""

    __slots__ = ("_forge", "_sample_size", "_analyses")

    def __init__(self, forge: DataForge, sample_size: int = 1000) -> None:
        self._forge = forge
        self._sample_size = sample_size
        self._analyses: list[ColumnAnalysis] = []

    def from_records(
        self,
        records: list[dict[str, Any]],
    ) -> Any:
        """Infer a Schema from a list of dicts."""
        if not records:
            raise ValueError("Cannot infer schema from empty data.")

        sample = records[: self._sample_size]
        columns = list(sample[0].keys())

        self._analyses = []
        field_map: dict[str, str] = {}
        null_fields: dict[str, float] = {}

        for col_name in columns:
            values = [row.get(col_name) for row in sample]
            analysis = self._analyze_column(col_name, values)
            self._analyses.append(analysis)

            if analysis.dataforge_field:
                field_map[col_name] = analysis.dataforge_field
                if analysis.null_rate > 0.01:
                    null_fields[col_name] = analysis.null_rate

        if not field_map:
            raise ValueError(
                "Could not map any columns to DataForge fields. "
                "Columns found: " + ", ".join(columns)
            )

        from dataforge.schema import Schema

        return Schema(
            self._forge,
            field_map,
            null_fields=null_fields if null_fields else None,
        )

    def from_csv(
        self,
        path: str,
        delimiter: str = ",",
        encoding: str = "utf-8",
    ) -> Any:
        """Infer a Schema from a CSV file."""
        import csv

        with open(path, "r", encoding=encoding, newline="") as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            records: list[dict[str, Any]] = []
            for i, row in enumerate(reader):
                if i >= self._sample_size:
                    break
                records.append(dict(row))

        return self.from_records(records)

    def from_dataframe(self, df: Any) -> Any:
        """Infer a Schema from a pandas DataFrame."""
        sample = df.head(self._sample_size)
        records = sample.to_dict("records")
        return self.from_records(records)

    def _analyze_column(
        self,
        col_name: str,
        values: list[Any],
    ) -> ColumnAnalysis:
        """Analyze a single column."""
        base_type = _detect_base_type(values)
        semantic_type = _detect_semantic_type(col_name, values, base_type)
        null_rate = _compute_null_rate(values)
        stats = _compute_stats(values, base_type)
        distribution = _fit_distribution(values, base_type)

        dataforge_field: str | None = None
        if semantic_type:
            try:
                self._forge._resolve_field(semantic_type)
                dataforge_field = semantic_type
            except ValueError:
                dataforge_field = None

        if dataforge_field is None:
            try:
                self._forge._resolve_field(col_name)
                dataforge_field = col_name
            except ValueError:
                pass

        if dataforge_field is None:
            if base_type == "bool":
                dataforge_field = "boolean"

        return ColumnAnalysis(
            name=col_name,
            base_type=base_type,
            semantic_type=semantic_type,
            null_rate=null_rate,
            stats=stats,
            dataforge_field=dataforge_field,
            distribution=distribution,
        )

    def describe(self) -> str:
        """Return a human-readable description of the inferred schema."""
        if not self._analyses:
            return "No schema has been inferred yet."

        lines: list[str] = ["Inferred Schema:", "=" * 60]
        for a in self._analyses:
            status = "mapped" if a.dataforge_field else "UNMAPPED"
            field_str = a.dataforge_field or "???"
            lines.append(
                f"  {a.name:<25} {a.base_type:<8} -> {field_str:<20} "
                f"[{status}] null={a.null_rate:.1%}"
            )
            if a.stats:
                stat_parts = [f"{k}={v}" for k, v in a.stats.items() if k != "count"]
                if stat_parts:
                    lines.append(f"  {'':25} stats: {', '.join(stat_parts)}")
            if a.distribution:
                dist = a.distribution
                params = ", ".join(f"{k}={v}" for k, v in dist["params"].items())
                lines.append(f"  {'':25} distribution: {dist['name']}({params})")
        lines.append("=" * 60)
        mapped_count = sum(1 for a in self._analyses if a.dataforge_field)
        lines.append(
            f"  {mapped_count}/{len(self._analyses)} columns mapped to DataForge fields"
        )
        return "\n".join(lines)

    @property
    def analyses(self) -> list[ColumnAnalysis]:
        """Access the column analyses from the last inference."""
        return list(self._analyses)

    def __repr__(self) -> str:
        if self._analyses:
            return f"SchemaInferrer(columns={len(self._analyses)})"
        return "SchemaInferrer(no analysis performed)"
