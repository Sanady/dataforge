"""Dynamic Fields with define() — Custom Data Pools and Generators.

Real-world scenario: Your application has domain-specific data that does not
map to any built-in provider (e.g., custom status codes, department names,
product tiers). You need to define reusable custom fields that integrate
seamlessly with schemas and batch generation.

This example demonstrates:
- Defining fields from a fixed element list
- Weighted element pools for realistic distributions
- Custom callable functions as field generators
- Batch generation with count parameter
- Integrating custom fields into schemas
"""

from collections import Counter

from dataforge import DataForge

forge = DataForge(seed=42)

# --- Example 1: Simple element list ---------------------------------------

print("=== Simple Element List ===\n")

forge.define("status", elements=["active", "inactive", "pending", "suspended"])

print("Random status values:")
for i in range(8):
    print(f"  {i + 1}. {forge.status()}")
print()

# --- Example 2: Weighted element pools ------------------------------------

print("=== Weighted Element Pools ===\n")

# Most users are active, fewer are pending, rare are suspended
forge.define(
    "user_status",
    elements=["active", "inactive", "pending", "suspended"],
    weights=[0.60, 0.20, 0.15, 0.05],
)

# Generate a sample and count the distribution
sample = forge.user_status(count=200)

counts = Counter(sample)
print("Distribution of 200 user statuses:")
for status, count in sorted(counts.items(), key=lambda x: -x[1]):
    bar = "#" * (count // 2)
    print(f"  {status:12s} {count:3d} ({count / 200:.0%}) {bar}")
print()

# Another weighted example: subscription tiers
forge.define(
    "tier",
    elements=["free", "basic", "pro", "enterprise"],
    weights=[0.50, 0.30, 0.15, 0.05],
)

sample = forge.tier(count=100)
counts = Counter(sample)
print("Subscription tier distribution (100 samples):")
for tier, count in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  {tier:12s} {count:3d}")
print()

# --- Example 3: Callable function generators ------------------------------

print("=== Callable Function Generators ===\n")

# Use a lambda for simple derived values
forge.define("score", func=lambda: forge._engine.random_int(1, 100))
print("Random scores:")
for i in range(5):
    print(f"  Score {i + 1}: {forge.score()}")
print()

# More complex callable — generates formatted order IDs
order_counter = 0


def make_order_id() -> str:
    global order_counter
    order_counter += 1
    return f"ORD-{order_counter:06d}"


forge.define("order_id", func=make_order_id)

print("Sequential order IDs:")
for i in range(5):
    print(f"  {forge.order_id()}")
print()

# Callable with randomness from the forge's engine
forge.define(
    "temperature",
    func=lambda: round(
        forge._engine.random_int(15, 35) + forge._engine.random_int(0, 9) / 10, 1
    ),
)

print("Random temperatures:")
for i in range(5):
    print(f"  {forge.temperature()}°C")
print()

# --- Example 4: Batch generation with count parameter ---------------------

print("=== Batch Generation ===\n")

forge.define("color", elements=["red", "green", "blue", "yellow", "purple"])

# Single value (default)
single = forge.color()
print(f"Single value:  {single}")

# Batch of values
batch = forge.color(count=10)
print(f"Batch of 10:   {batch}")
print()

# Weighted batch
forge.define(
    "priority",
    elements=["low", "medium", "high", "critical"],
    weights=[0.40, 0.35, 0.20, 0.05],
)

batch = forge.priority(count=20)
counts = Counter(batch)
print("Priority batch (20 items):")
for p, c in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  {p:10s} {c}")
print()

# --- Example 5: Custom fields in schemas ---------------------------------

print("=== Custom Fields in Schemas ===\n")

# Define domain-specific fields
forge.define(
    "department",
    elements=[
        "Engineering",
        "Marketing",
        "Sales",
        "HR",
        "Finance",
        "Legal",
        "Support",
    ],
)
forge.define(
    "seniority",
    elements=["junior", "mid", "senior", "lead", "principal"],
    weights=[0.30, 0.30, 0.25, 0.10, 0.05],
)

# Now use them in a schema alongside built-in fields
schema = forge.schema(
    {
        "employee_id": "misc.uuid4",
        "name": "person.full_name",
        "email": "internet.email",
        "department": "department",
        "seniority": "seniority",
    }
)

employees = schema.generate(count=8)
print("Employee records with custom fields:")
for emp in employees:
    uid = emp["employee_id"][:8]
    print(
        f"  {uid}... {emp['name']:22s} {emp['department']:12s} "
        f"{emp['seniority']:10s} {emp['email']}"
    )
print()

# --- Example 6: Overriding built-in fields --------------------------------

print("=== Building Domain-Specific Vocabularies ===\n")

# Define multiple related fields for a gaming application
forge.define(
    "game_class",
    elements=[
        "Warrior",
        "Mage",
        "Rogue",
        "Healer",
        "Ranger",
        "Paladin",
    ],
)
forge.define(
    "rarity",
    elements=["common", "uncommon", "rare", "epic", "legendary"],
    weights=[0.40, 0.30, 0.18, 0.10, 0.02],
)
forge.define("power_level", func=lambda: forge._engine.random_int(1, 100))

# Build a game-item schema
print("Generated game characters:")
for i in range(5):
    char_class = forge.game_class()
    rarity_val = forge.rarity()
    power = forge.power_level()
    name = forge.person.first_name()
    print(f"  {name:12s} | {char_class:8s} | {rarity_val:10s} | Power: {power:3d}")
