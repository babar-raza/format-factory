"""Dogfood example: Read a CSV file with Format Factory, transform, and write output.

Demonstrates real-world usage of the format-factory-csv library.
Runnable: python examples/dogfood_csv_export.py
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Import using the Format Factory convention for the csv module
# (stdlib csv conflict requires explicit path insertion)
from src.python.csv.csv_parser import parse_csv  # type: ignore

SAMPLE_CSV = REPO_ROOT / "samples" / "by-format" / "csv" / "minimal-2x2.csv"
OUTPUT_DIR = REPO_ROOT / ".local" / "dogfood-output"


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Parse input CSV
    print(f"Reading: {SAMPLE_CSV}")
    result = parse_csv(str(SAMPLE_CSV))

    if not result or "rows" not in result:
        print(f"ERROR: Could not parse {SAMPLE_CSV}")
        return 1

    rows = result["rows"]
    print(f"Parsed {len(rows)} rows")

    # Step 2: Transform — add a row number column
    transformed_rows = []
    for i, row in enumerate(rows):
        new_row = [str(i)] + list(row)
        transformed_rows.append(new_row)

    # Step 3: Write output CSV
    output_path = OUTPUT_DIR / "dogfood-csv-output.csv"
    with output_path.open("w", encoding="utf-8", newline="") as f:
        for row in transformed_rows:
            f.write(",".join(row) + "\n")

    print(f"Wrote {len(transformed_rows)} rows to: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
