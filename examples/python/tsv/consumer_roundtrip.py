"""Clean consumer proof: TSV load -> inspect -> mutate -> save -> reload.

TSV uses a neutral model dict with headers/rows (list-of-lists).
Mutation: modify rows list, then write_tsv(rows, dest, headers=headers).

Steps:
  1. Load TSV file to neutral model dict
  2. Inspect: headers, rows, TsvDocument domain model
  3. Mutate: append row, write to new file
  4. Reload and verify mutation persisted

DOGFOOD CONTRACT:
  - uses `import tsv` (installed package, not src/)
  - no src/ path manipulation
  - asserts real semantic result at every boundary

Runnable:
  python examples/python/tsv/consumer_roundtrip.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]

import tsv as tsv_pkg
from tsv import load_tsv, write_tsv, TsvDocument

SAMPLE_TSV = _REPO / "samples" / "by-format" / "tsv" / "multi-column.tsv"
OUTPUT_DIR = _REPO / ".local" / "dogfood-proofs" / "tsv"


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Source: {SAMPLE_TSV}")
    print(f"TSV package: {tsv_pkg.__file__}")
    print()

    # Step 1: Load
    model = load_tsv(str(SAMPLE_TSV))
    assert isinstance(model, dict), f"Expected dict, got {type(model)}"
    print(f"[LOAD] headers={model['headers']!r}, row_count={model['row_count']}")
    assert model["row_count"] >= 1

    # Step 2: Inspect via TsvDocument
    doc = TsvDocument.from_file(str(SAMPLE_TSV))
    assert doc.spec_qname == "tsv:record", f"spec_qname={doc.spec_qname!r}"
    print(f"[INSPECT] spec_qname={doc.spec_qname}")
    print(f"  headers={doc.headers!r}")
    print(f"  row_count={doc.row_count}, column_count={doc.column_count}")
    assert doc.row_count == model["row_count"]
    assert doc.column_count == len(model["headers"])

    row0 = doc.rows[0]
    print(f"  row[0]={row0!r}")

    # Step 3: Mutate — list-based
    headers = model["headers"]
    new_rows = list(model["rows"]) + [["CONSUMER_PROOF", "VERIFIED", "999", "true"]]
    out_path = str(OUTPUT_DIR / "consumer_proof.tsv")
    write_tsv(new_rows, out_path, headers=headers)
    print(f"\n[MUTATE+SAVE] appended row, saved to {out_path}")

    # Step 4: Reload and verify
    model2 = load_tsv(out_path)
    assert model2["row_count"] == model["row_count"] + 1, \
        f"Expected {model['row_count']+1} rows, got {model2['row_count']}"
    last = model2["rows"][-1]
    assert last[0] == "CONSUMER_PROOF", f"Last row: {last!r}"
    assert last[1] == "VERIFIED"
    print(f"[RELOAD] row_count={model2['row_count']}, last={last!r}  OK")

    doc2 = TsvDocument.from_file(out_path)
    assert doc2.row_count == model["row_count"] + 1
    print(f"[RELOAD] TsvDocument.row_count={doc2.row_count}  OK")

    print("\nCONSUMER_PROOF: PASS -- load -> inspect -> mutate -> save -> reload verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
