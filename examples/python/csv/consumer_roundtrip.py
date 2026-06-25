"""Clean consumer proof: CSV load -> inspect -> mutate -> save -> reload.

NOTE: The FF CSV package is named 'csv' which conflicts with Python's stdlib csv.
This example uses sys.path.insert to import from src/python/csv/ directly.
This is the established pattern for CSV examples in this repo.

Steps:
  1. Load CSV file to neutral model dict
  2. Inspect: headers, rows, CsvDocument domain model
  3. Mutate: append row, write to new file
  4. Reload and verify mutation persisted

Runnable:
  python examples/python/csv/consumer_roundtrip.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import parse_csv  # type: ignore
from src.python.csv.csv_writer import write_csv_to_file  # type: ignore
from src.python.csv.models import CsvDocument  # type: ignore

SAMPLE_CSV = _REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv"
OUTPUT_DIR = _REPO / ".local" / "dogfood-proofs" / "csv-consumer"


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Source: {SAMPLE_CSV}")
    print()

    # Step 1: Load
    model = parse_csv(str(SAMPLE_CSV))
    assert isinstance(model, dict), f"Expected dict, got {type(model)}"
    print(f"[LOAD] headers={model['headers']!r}, row_count={model['row_count']}")
    assert model["row_count"] >= 1

    # Step 2: Inspect via CsvDocument
    doc = CsvDocument.from_file(str(SAMPLE_CSV))
    assert doc.spec_qname in ("csv:document", "csv:record"), f"spec_qname={doc.spec_qname!r}"
    print(f"[INSPECT] spec_qname={doc.spec_qname}")
    print(f"  headers={doc.headers!r}")
    print(f"  row_count={doc.row_count}, column_count={doc.column_count}")
    assert doc.row_count == model["row_count"]

    row0 = doc.rows[0]
    print(f"  row[0]={row0!r}")

    # Step 3: Mutate — list-based
    headers = model["headers"]
    new_rows = list(model["rows"]) + [["CONSUMER_PROOF", "VERIFIED"]]
    out_path = OUTPUT_DIR / "consumer_proof.csv"
    write_csv_to_file(new_rows, out_path, headers=headers)
    print(f"\n[MUTATE+SAVE] appended row, saved ({out_path.stat().st_size} bytes)")

    # Step 4: Reload and verify
    model2 = parse_csv(str(out_path))
    assert model2["row_count"] == model["row_count"] + 1, \
        f"Expected {model['row_count']+1} rows, got {model2['row_count']}"
    last = model2["rows"][-1]
    assert last[0] == "CONSUMER_PROOF", f"Last row: {last!r}"
    assert last[1] == "VERIFIED"
    print(f"[RELOAD] row_count={model2['row_count']}, last={last!r}  OK")

    doc2 = CsvDocument.from_file(str(out_path))
    assert doc2.row_count == model["row_count"] + 1
    print(f"[RELOAD] CsvDocument.row_count={doc2.row_count}  OK")

    print("\nCONSUMER_PROOF: PASS -- load -> inspect -> mutate -> save -> reload verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
