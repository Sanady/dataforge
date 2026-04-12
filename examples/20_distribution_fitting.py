"""Distribution Fitting — Inferring Statistical Distributions from Data.

Real-world scenario: You have production data with numeric columns that
follow specific statistical distributions (e.g., response times follow a
log-normal distribution, user counts follow a Zipf distribution). You want
DataForge to detect these patterns so it can generate realistic synthetic
data that matches your production characteristics.

This example demonstrates:
- Generating data with known distributions
- Using SchemaInferrer to analyze and fit distributions
- Inspecting ColumnAnalysis objects
- Understanding the supported distribution types (Normal, LogNormal,
  Exponential, Beta, Zipf)
- The describe() method for human-readable analysis summaries
"""

import math
import random
from collections import Counter

from dataforge import DataForge
from dataforge.inference import SchemaInferrer

forge = DataForge(seed=42)

# --- Example 1: Normal distribution detection -----------------------------

print("=== Normal Distribution Detection ===\n")

# Generate data that follows a normal distribution
rng = random.Random(42)
normal_data = [{"value": rng.gauss(100, 15), "label": "sample"} for _ in range(200)]

inferrer = SchemaInferrer(forge)
# Note: from_records() may fail if column names don't map to DataForge fields.
# The analysis still happens internally — we can inspect _analyses directly.
try:
    schema = inferrer.from_records(normal_data)
except ValueError:
    # Expected: "value" and "label" don't map to known DataForge fields
    # but _analyze_column was still called, so _analyses is populated
    pass

# Inspect the analysis
for analysis in inferrer._analyses:
    if analysis.name == "value":
        print(f"  Column:       {analysis.name}")
        print(f"  Base type:    {analysis.base_type}")
        print(f"  Distribution: {analysis.distribution}")
        if analysis.distribution:
            params = analysis.distribution.get("params", {})
            print(f"  Detected:     {analysis.distribution['name']}")
            if "mean" in params:
                print(f"  Mean:         {params['mean']:.2f} (expected ~100)")
            if "std" in params:
                print(f"  Std:          {params['std']:.2f} (expected ~15)")
print()

# --- Example 2: Log-normal distribution detection -------------------------

print("=== Log-Normal Distribution Detection ===\n")

# Response times typically follow a log-normal distribution
rng = random.Random(42)
lognormal_data = [
    {"response_ms": math.exp(rng.gauss(4.5, 0.8)), "endpoint": "/api/data"}
    for _ in range(200)
]

inferrer = SchemaInferrer(forge)
try:
    schema = inferrer.from_records(lognormal_data)
except ValueError:
    pass

for analysis in inferrer._analyses:
    if analysis.name == "response_ms":
        print(f"  Column:       {analysis.name}")
        print(f"  Base type:    {analysis.base_type}")
        print(f"  Distribution: {analysis.distribution}")
        if analysis.distribution:
            print(f"  Detected:     {analysis.distribution['name']}")
            params = analysis.distribution.get("params", {})
            if "mu" in params:
                print(f"  Mu:           {params['mu']:.2f} (expected ~4.5)")
            if "sigma" in params:
                print(f"  Sigma:        {params['sigma']:.2f} (expected ~0.8)")

        # Show some stats
        values = [r["response_ms"] for r in lognormal_data]
        print(f"  Data range:   {min(values):.1f} — {max(values):.1f} ms")
        print(f"  Median:       {sorted(values)[len(values) // 2]:.1f} ms")
print()

# --- Example 3: Exponential distribution detection ------------------------

print("=== Exponential Distribution Detection ===\n")

# Time between events (inter-arrival times) follows exponential
rng = random.Random(42)
exponential_data = [{"wait_seconds": rng.expovariate(0.5)} for _ in range(200)]

inferrer = SchemaInferrer(forge)
try:
    schema = inferrer.from_records(exponential_data)
except ValueError:
    pass

for analysis in inferrer._analyses:
    if analysis.name == "wait_seconds":
        print(f"  Column:       {analysis.name}")
        print(f"  Distribution: {analysis.distribution}")
        if analysis.distribution:
            print(f"  Detected:     {analysis.distribution['name']}")
print()

# --- Example 4: Zipf distribution detection -------------------------------

print("=== Zipf Distribution Detection ===\n")

# Word frequencies, city populations, etc. follow Zipf's law
rng = random.Random(42)


def zipf_sample(s: float, n: int, size: int) -> list[int]:
    """Generate Zipf-distributed integers."""
    weights = [1.0 / (k**s) for k in range(1, n + 1)]
    total = sum(weights)
    probs = [w / total for w in weights]
    return rng.choices(range(1, n + 1), weights=probs, k=size)


zipf_values = zipf_sample(s=1.5, n=50, size=300)
zipf_data = [{"rank": v} for v in zipf_values]

inferrer = SchemaInferrer(forge)
try:
    schema = inferrer.from_records(zipf_data)
except ValueError:
    pass  # may not map to a DataForge field, that's OK

for analysis in inferrer._analyses:
    if analysis.name == "rank":
        print(f"  Column:       {analysis.name}")
        print(f"  Distribution: {analysis.distribution}")
        if analysis.distribution:
            print(f"  Detected:     {analysis.distribution['name']}")
            params = analysis.distribution.get("params", {})
            if "s" in params:
                print(f"  S parameter:  {params['s']:.2f} (expected ~1.5)")

        # Show frequency distribution
        freq = Counter(zipf_values)
        top5 = freq.most_common(5)
        print(f"  Top-5 values: {top5}")
print()

# --- Example 5: Mixed-column dataset analysis -----------------------------

print("=== Mixed-Column Dataset Analysis ===\n")

# Create a realistic dataset with multiple column types
rng = random.Random(42)
mixed_data = []
for _ in range(150):
    mixed_data.append(
        {
            "email": f"user{rng.randint(1, 999)}@example.com",
            "response_time": math.exp(rng.gauss(3.0, 0.5)),
            "active": rng.choice(["true", "false"]),
        }
    )

inferrer = SchemaInferrer(forge)
schema = inferrer.from_records(mixed_data)

print("Column-by-column analysis:")
for analysis in inferrer._analyses:
    dist = analysis.distribution
    dist_name = dist["name"] if dist else "none"
    print(
        f"  {analysis.name:18s} type={analysis.base_type:6s} "
        f"semantic={str(analysis.semantic_type):10s} "
        f"distribution={dist_name}"
    )
print()

# --- Example 6: The describe() method ------------------------------------

print("=== Human-Readable Analysis (describe()) ===\n")

description = inferrer.describe()
print(description)
print()

# --- Example 7: ColumnAnalysis object details -----------------------------

print("=== ColumnAnalysis Object Details ===\n")

for analysis in inferrer._analyses:
    print(f"  ColumnAnalysis for '{analysis.name}':")
    print(f"    base_type:       {analysis.base_type}")
    print(f"    semantic_type:   {analysis.semantic_type}")
    print(f"    null_rate:       {analysis.null_rate:.2%}")
    print(f"    dataforge_field: {analysis.dataforge_field}")
    print(f"    distribution:    {analysis.distribution}")
    print(f"    stats:           {analysis.stats}")
    print()

# --- Example 8: Round-trip: generate → infer → compare -------------------

print("=== Round-Trip: Generate → Infer → Compare ===\n")

# Generate data with a known schema
original_schema = forge.schema(
    {
        "name": "person.full_name",
        "email": "internet.email",
        "city": "address.city",
    }
)

original_data = original_schema.generate(count=200)

# Infer schema from the generated data
inferrer = SchemaInferrer(forge)
inferred_schema = inferrer.from_records(original_data)

print("Original schema fields vs inferred fields:")
for analysis in inferrer._analyses:
    print(f"  {analysis.name:12s} → inferred as '{analysis.dataforge_field}'")
print()

# Generate new data from the inferred schema
new_data = inferred_schema.generate(count=5)
print("Data from inferred schema:")
for row in new_data:
    print(f"  {row}")
