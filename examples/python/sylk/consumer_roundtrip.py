"""Clean consumer proof: SYLK load -> inspect -> mutate -> save -> export.

SYLK (Symbolic Link) uses a flat document model — no sheets, just row/col
coordinates. Mutation is file-based: set_cell_value(src, dest, row, col, value).

Steps:
  1. Load SYLK file to SylkDocument
  2. Inspect: cells, rows, spec_qname
  3. Mutate: set cell value (file-based), add row
  4. Reload and verify mutations persisted
  5. Export to CSV

DOGFOOD CONTRACT:
  - uses `import sylk` (installed package, not src/)
  - no src/ path manipulation
  - asserts real semantic result at every boundary

Runnable:
  python examples/python/sylk/consumer_roundtrip.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]

import sylk
from sylk import (
    parse_sylk_strict,
    set_cell_value,
    add_row,
    sylk_to_csv,
    SylkDocument,
    SylkCell,
)

SAMPLE_SYLK = _REPO / "samples" / "by-format" / "sylk" / "valid" / "minimal-2x2.slk"
OUTPUT_DIR = _REPO / ".local" / "dogfood-proofs" / "sylk"


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Source: {SAMPLE_SYLK}")
    print(f"SYLK package: {sylk.__file__}")
    print()

    # Step 1: Load
    doc = parse_sylk_strict(str(SAMPLE_SYLK))
    assert isinstance(doc, SylkDocument), f"Expected SylkDocument, got {type(doc)}"
    print(f"[LOAD] spec_qname={doc.spec_qname}")
    print(f"  rows={doc.rows}, cells={len(doc.cells)}")
    assert doc.rows >= 1
    assert len(doc.cells) >= 1

    # Step 2: Inspect
    cell00 = next((c for c in doc.cells if c.row == 1 and c.col == 1), None)
    assert cell00 is not None, "Cell [1,1] not found"
    print(f"[INSPECT] Cell[1,1]: value={cell00.value!r}, type={cell00.value_type!r}")
    original_value = cell00.value

    numeric_cells = [c for c in doc.cells if c.value_type == "numeric"]
    print(f"[INSPECT] Numeric cells: {len(numeric_cells)}")
    assert len(numeric_cells) >= 1

    # Step 3: Mutate — file-based API
    step1_path = str(OUTPUT_DIR / "step1_mutated.slk")
    result = set_cell_value(str(SAMPLE_SYLK), step1_path, 1, 1, "CONSUMER_PROOF", "string")
    assert result.get("ok"), f"set_cell_value failed: {result}"
    print(f"[MUTATE] set_cell_value -> ok={result['ok']}, old={result['old_value']!r} -> new={result['new_value']!r}")

    out_path = str(OUTPUT_DIR / "consumer_proof.slk")
    result2 = add_row(step1_path, out_path, ["NewItem", 777])
    assert result2.get("success"), f"add_row failed: {result2}"
    print(f"[MUTATE] add_row -> row_index={result2['row_index']}, cell_count={result2['cell_count']}")

    # Step 4: Reload and verify
    doc2 = parse_sylk_strict(out_path)
    print(f"\n[RELOAD] rows={doc2.rows}, cells={len(doc2.cells)}")
    assert doc2.rows == 3, f"Expected 3 rows, got {doc2.rows}"

    cell11 = next((c for c in doc2.cells if c.row == 1 and c.col == 1), None)
    assert cell11 is not None
    assert cell11.value == "CONSUMER_PROOF", f"Cell mutation failed: {cell11.value!r}"
    print(f"  Cell[1,1]: {cell11.value!r}  OK")

    last_row_cells = [c for c in doc2.cells if c.row == doc2.rows]
    last_vals = sorted(last_row_cells, key=lambda c: c.col)
    assert last_vals[0].value == "NewItem", f"add_row item: {last_vals[0].value!r}"
    assert last_vals[1].value == 777, f"add_row numeric: {last_vals[1].value!r}"
    print(f"  Last row: {[c.value for c in last_vals]}  OK")

    # Step 5: CSV export
    csv_text = sylk_to_csv(out_path)
    assert csv_text.strip(), "CSV export empty"
    assert "CONSUMER_PROOF" in csv_text, f"CSV missing mutation: {csv_text[:80]}"
    csv_path = OUTPUT_DIR / "consumer_proof_export.csv"
    csv_path.write_text(csv_text, encoding="utf-8")
    print(f"\n[EXPORT] CSV ({len(csv_text)} chars):")
    print(csv_text.strip())

    print("\nCONSUMER_PROOF: PASS -- load -> inspect -> mutate -> reload -> export verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
