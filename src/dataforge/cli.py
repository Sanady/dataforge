"""dataforge CLI — generate fake data from the command line.

Usage::

    dataforge --count 100 --format csv name email phone
    dataforge --count 10 --format json first_name last_name city
    dataforge --locale de_DE --count 5 full_name address
    dataforge --list-fields

Supported output formats: text, csv, json, jsonl
"""

import argparse
import csv
import io
import json
import sys

from dataforge import DataForge
from dataforge.registry import get_field_map


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dataforge",
        description="Generate fake data for testing from the command line.",
    )
    parser.add_argument(
        "fields",
        nargs="*",
        help="Fields to generate (e.g. first_name email city). "
        "Use --list-fields to see all available fields.",
    )
    parser.add_argument(
        "-n",
        "--count",
        type=int,
        default=10,
        help="Number of rows to generate (default: 10).",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=("text", "csv", "json", "jsonl"),
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "-l",
        "--locale",
        default="en_US",
        help="Locale for data generation (default: en_US).",
    )
    parser.add_argument(
        "-s",
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible output.",
    )
    parser.add_argument(
        "--list-fields",
        action="store_true",
        help="List all available field names and exit.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        metavar="FILE",
        help="Write output to FILE instead of stdout.",
    )
    parser.add_argument(
        "--no-header",
        action="store_true",
        help="Omit header row in text and csv output formats.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for the dataforge CLI."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    field_map = get_field_map()

    if args.list_fields:
        # Group fields by provider
        for name in sorted(field_map.keys()):
            provider, method = field_map[name]
            print(f"  {name:24s}  ({provider}.{method})")
        return 0

    if not args.fields:
        # Default fields
        args.fields = ["first_name", "last_name", "email"]

    # Validate fields before generating
    for field in args.fields:
        if field not in field_map:
            print(
                f"Error: unknown field '{field}'. Use --list-fields to see options.",
                file=sys.stderr,
            )
            return 1

    forge = DataForge(locale=args.locale, seed=args.seed)

    # Column-first batch generation — dramatically faster than row-by-row
    headers = args.fields
    rows = forge.to_dict(headers, count=args.count)

    # Determine output destination
    out_file = None
    if args.output:
        out_file = open(args.output, "w", encoding="utf-8", newline="")
    out = out_file or sys.stdout

    try:
        # Output
        fmt = args.format

        if fmt == "text":
            # Aligned columns
            col_widths = [len(h) for h in headers]
            for row in rows:
                for i, h in enumerate(headers):
                    col_widths[i] = max(col_widths[i], len(row[h]))

            if not args.no_header:
                header_line = "  ".join(
                    h.ljust(col_widths[i]) for i, h in enumerate(headers)
                )
                sep_line = "  ".join("-" * col_widths[i] for i in range(len(headers)))
                print(header_line, file=out)
                print(sep_line, file=out)
            for row in rows:
                line = "  ".join(
                    row[h].ljust(col_widths[i]) for i, h in enumerate(headers)
                )
                print(line, file=out)

        elif fmt == "csv":
            buf = io.StringIO()
            writer = csv.DictWriter(buf, fieldnames=headers)
            if not args.no_header:
                writer.writeheader()
            writer.writerows(rows)
            print(buf.getvalue(), end="", file=out)

        elif fmt == "json":
            print(json.dumps(rows, indent=2, ensure_ascii=False), file=out)

        elif fmt == "jsonl":
            for row in rows:
                print(json.dumps(row, ensure_ascii=False), file=out)
    finally:
        if out_file is not None:
            out_file.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
