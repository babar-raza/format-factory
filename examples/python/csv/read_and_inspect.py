"""Dogfood example: Read and inspect a CSV file using Format Factory CSV parser.

Demonstrates:
  - parse_csv() / CsvDocument.from_file() for structured access
  - csv_row_count, csv_column_count, csv_has_header
  - csv_to_dicts for dict-row access
  - csv_is_all_numeric, csv_has_duplicates for analytics
  - Round-trip: write CSV then reload

Runnable: python examples/python/csv/read_and_inspect.py
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
# TC-PA-013: Package renamed from csv to ff_csv to avoid stdlib collision.
# With ff_csv, direct import works without sys.path hacks.
_SRC = _REPO / "src" / "python"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from ff_csv.csv_parser import (  # type: ignore
    parse_csv,
    csv_row_count,
    csv_column_count,
    csv_has_header,
    csv_to_dicts,
    csv_is_all_numeric,
    csv_has_duplicates,
    csv_numeric_sum,
)
from ff_csv.models import CsvDocument  # type: ignore

SAMPLE_CSV = """\
product,price,qty
Widget,9.99,100
Gadget,24.50,50
Thingamajig,4.99,200
"""

OUTPUT_DIR = _REPO / ".local" / "dogfood-proofs" / "csv"


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Write sample file
    csv_path = OUTPUT_DIR / "sample.csv"
    csv_path.write_text(SAMPLE_CSV, encoding="utf-8")
    path_str = str(csv_path)

    print(f"Source: {csv_path}")

    # Step 1: Low-level parse
    model = parse_csv(path_str)
    print(f"\n[parse_csv] model keys: {sorted(model.keys())}")

    # Step 2: Shape analytics
    rows = csv_row_count(path_str)
    cols = csv_column_count(path_str)
    has_header = csv_has_header(path_str)
    print(f"\n[shape] rows={rows}, cols={cols}, has_header={has_header}")
    assert rows == 3, f"Expected 3 rows, got {rows}"
    assert cols == 3, f"Expected 3 cols, got {cols}"
    assert has_header is True

    # Step 3: Dict access
    dicts = csv_to_dicts(path_str)
    print(f"\n[to_dicts] first row: {dicts[0]}")
    assert dicts[0]["product"] == "Widget"

    # Step 4: CsvDocument domain model
    doc = CsvDocument.from_file(path_str)
    print(f"\n[CsvDocument] row_count={doc.row_count}, column_count={doc.column_count}")
    print(f"  headers={doc.headers}")
    print(f"  cell(0,0)={doc.get_cell(0, 0)}")
    assert doc.row_count == 3
    assert doc.headers == ["product", "price", "qty"]
    assert doc.get_cell(0, 0) == "Widget"

    # Step 5: Numeric analytics on a numeric-only CSV
    numeric_csv_path = OUTPUT_DIR / "numeric.csv"
    numeric_csv_path.write_text("1,2,3\n4,5,6\n7,8,9\n", encoding="utf-8")
    npath = str(numeric_csv_path)
    assert csv_is_all_numeric(npath) is True
    total = csv_numeric_sum(npath)
    print(f"\n[numeric] all_numeric=True, sum={total}")
    assert total == 45.0

    # Step 6: Duplicate detection
    dupe_csv_path = OUTPUT_DIR / "dupe.csv"
    dupe_csv_path.write_text("a,b\n1,2\n1,2\n3,4\n", encoding="utf-8")
    assert csv_has_duplicates(str(dupe_csv_path)) is True
    print(f"\n[duplicates] has_duplicates=True (verified)")

    print("\nDOGFOOD PASS: CSV parse, shape, dict-access, CsvDocument, numeric analytics all OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
