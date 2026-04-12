"""HTTP Mock Data Server — Serving Fake Data over HTTP.

Real-world scenario: Your frontend team needs a mock API that returns
realistic data during development. DataForge's ``--serve`` CLI flag
starts a lightweight HTTP server that returns JSON data for any schema,
no backend coding required.

This example is documentation-style since starting a server would block
execution. It shows the CLI commands and expected behavior.

This example demonstrates:
- Starting the mock server with CLI commands
- Customizing fields, count, port, and locale
- Query string parameters for dynamic requests
- Using schema files with the server
- Integration with frontend development workflows
"""

import json

from dataforge import DataForge

forge = DataForge(seed=42)

# --- Example 1: CLI usage -------------------------------------------------

print("=== HTTP Mock Server — CLI Usage ===\n")

print("The DataForge CLI includes a built-in HTTP mock data server.")
print("Start it with the --serve flag:\n")

print("  # Basic usage — serves default fields (first_name, last_name, email)")
print("  $ dataforge --serve\n")

print("  # Custom fields")
print("  $ dataforge --serve first_name last_name email city phone_number\n")

print("  # Custom port")
print("  $ dataforge --serve --port 3000 first_name email\n")

print("  # With locale")
print("  $ dataforge --serve --locale ja_JP first_name city\n")

print("  # With a seed for reproducible output")
print("  $ dataforge --serve --seed 42 first_name email city\n")

print("  # With column aliases (column_name:field_name)")
print("  $ dataforge --serve user_email:email user_name:full_name user_city:city\n")

# --- Example 2: Query parameters -----------------------------------------

print("=== Query Parameters ===\n")

print("Once the server is running, make GET requests with ?count=N:\n")

print("  # Default count (from --count flag, default 10)")
print("  $ curl http://localhost:8080/\n")

print("  # Custom count")
print("  $ curl http://localhost:8080/?count=5\n")

print("  # Large dataset")
print("  $ curl http://localhost:8080/?count=1000\n")

# --- Example 3: Expected JSON response -----------------------------------

print("=== Expected JSON Response ===\n")

# Show what the server would return
schema = forge.schema(
    {
        "first_name": "person.first_name",
        "last_name": "person.last_name",
        "email": "internet.email",
    }
)

rows = schema.generate(count=3)
print("GET http://localhost:8080/?count=3\n")
print("Response:")
print(json.dumps(rows, indent=2, default=str))
print()

# --- Example 4: Using with a schema file ---------------------------------

print("=== Using with a Schema File ===\n")

print("You can also use a schema definition file:\n")

print("  # JSON schema file")
print("  $ dataforge --serve --schema my_schema.json\n")

print("  # YAML schema file")
print("  $ dataforge --serve --schema my_schema.yaml\n")

print("Example schema file (my_schema.json):")
print(
    json.dumps(
        {
            "fields": {
                "user_id": "misc.uuid4",
                "name": "person.full_name",
                "email": "internet.email",
                "city": "address.city",
            },
            "count": 10,
        },
        indent=2,
    )
)
print()

# --- Example 5: Frontend integration patterns ----------------------------

print("=== Frontend Integration Patterns ===\n")

print("JavaScript fetch example:\n")
print('  const response = await fetch("http://localhost:8080/?count=20");')
print("  const users = await response.json();")
print("  // users is an array of objects with the specified fields")
print()

print("Python requests example:\n")
print("  import requests")
print('  resp = requests.get("http://localhost:8080/?count=50")')
print("  data = resp.json()")
print()

# --- Example 6: Server response headers ----------------------------------

print("=== Response Headers ===\n")

print("The mock server returns these headers:\n")
print("  Content-Type: application/json; charset=utf-8")
print("  Access-Control-Allow-Origin: *")
print()
print("CORS is enabled by default, so frontend apps on different")
print("origins can fetch data directly during development.")
print()

# --- Example 7: What the server generates (live demo) --------------------

print("=== Live Data Preview (what the server would return) ===\n")

# Simulate different field configurations
configs = [
    ("User API", ["full_name", "email", "city"]),
    ("Product API", ["ecommerce.product_name", "ecommerce.sku", "finance.price"]),
    ("Contact API", ["full_name", "phone_number", "address.full_address"]),
]

for name, fields in configs:
    schema = forge.schema(fields)
    rows = schema.generate(count=2)
    print(f"  {name}:")
    for row in rows:
        print(f"    {row}")
    print()

print("Start the server and point your frontend at it for instant mock data!")
