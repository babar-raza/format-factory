"""Clean consumer proof: ODS load -> inspect -> mutate -> save -> reload -> export.

Demonstrates the full PROOF_LEVEL_4 flow using only the installed
aspose-format-factory-ods / format-factory-ods package API.

Steps:
  1. Load a real ODS file to OdsDocument
  2. Inspect: sheets, rows, cells
  3. Mutate: set cell value, add row, rename sheet
  4. Save to a new ODS file
  5. Reload from the saved file and verify mutations persisted
  6. Export to CSV

DOGFOOD CONTRACT:
  - uses `import ods` (installed package, not src/)
  - no src/ path manipulation
  - asserts real semantic result at every boundary

Runnable:
  python examples/python/ods/clean_consumer_roundtrip.py
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

# Resolve repo root to find sample files — but import ods as an installed package
_REPO = Path(__file__).resolve().parents[3]

import ods
from ods.ods_parser import parse_ods_strict, OdsDocument, OdsSheet, OdsRow, OdsCell
from ods.ods_writer import (
    write_ods,
    set_cell_value,
    add_row,
    add_sheet,
    rename_sheet,
    delete_row,
)
from ods.ods_csv_exporter import export_ods_to_csv

SAMPLE_ODS = _REPO / "samples" / "by-format" / "ods" / "valid" / "minimal-spreadsheet.ods"
OUTPUT_DIR = _REPO / ".local" / "dogfood-proofs" / "ods"


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Source: {SAMPLE_ODS}")
    print(f"ODS package: {ods.__file__}")
    print()

    # ── Step 1: Load ──────────────────────────────────────────────────────────
    doc = parse_ods_strict(str(SAMPLE_ODS))
    assert isinstance(doc, OdsDocument), f"Expected OdsDocument, got {type(doc)}"
    print(f"[LOAD] spec_qname={OdsDocument.spec_qname}")
    print(f"  Sheets: {len(doc.sheets)}")
    assert len(doc.sheets) >= 1, "Expected at least 1 sheet"

    # ── Step 2: Inspect ───────────────────────────────────────────────────────
    sheet = doc.sheets[0]
    print(f"[INSPECT] Sheet: {sheet.name!r}  spec_qname={OdsSheet.spec_qname}")
    print(f"  Rows: {len(sheet.rows)}")
    assert len(sheet.rows) >= 1

    row0 = sheet.rows[0]
    print(f"  Row[0] cells: {len(row0.cells)}  spec_qname={OdsRow.spec_qname}")
    assert len(row0.cells) >= 1

    cell00 = row0.cells[0]
    print(f"  Cell[0,0]: value={cell00.value!r}  type={cell00.value_type!r}  spec_qname={OdsCell.spec_qname}")
    original_value = cell00.value

    # ── Step 3: Mutate ────────────────────────────────────────────────────────
    print()
    ok, msg = set_cell_value(doc, 0, 0, 0, "CONSUMER_PROOF", "string")
    assert ok, f"set_cell_value failed: {msg}"
    print(f"[MUTATE] set_cell_value -> {msg}")

    ok, msg = add_row(doc, 0, ["NewItem", 777.0])
    assert ok, f"add_row failed: {msg}"
    print(f"[MUTATE] add_row -> {msg}")

    ok, msg = rename_sheet(doc, sheet.name, "ConsumerSheet")
    assert ok, f"rename_sheet failed: {msg}"
    print(f"[MUTATE] rename_sheet -> {msg}")

    ok, msg = add_sheet(doc, "EmptyTab")
    assert ok, f"add_sheet failed: {msg}"
    print(f"[MUTATE] add_sheet -> {msg}")

    # ── Step 4: Save ──────────────────────────────────────────────────────────
    out_path = OUTPUT_DIR / "consumer_proof.ods"
    write_ods(doc, str(out_path))
    assert out_path.exists() and out_path.stat().st_size > 0
    print(f"\n[SAVE] {out_path} ({out_path.stat().st_size} bytes)")

    # ── Step 5: Reload and verify ─────────────────────────────────────────────
    doc2 = parse_ods_strict(str(out_path))
    print(f"\n[RELOAD] Sheets: {len(doc2.sheets)}")
    assert len(doc2.sheets) == 2, f"Expected 2 sheets, got {len(doc2.sheets)}"

    sheet2 = doc2.sheets[0]
    assert sheet2.name == "ConsumerSheet", f"Sheet rename failed: got {sheet2.name!r}"
    print(f"  Sheet[0].name: {sheet2.name!r}  OK")

    cell2 = sheet2.rows[0].cells[0]
    assert cell2.value == "CONSUMER_PROOF", f"Cell mutation failed: got {cell2.value!r}"
    print(f"  Cell[0,0]: {cell2.value!r}  OK")

    last_row = sheet2.rows[-1]
    assert last_row.cells[0].value == "NewItem", f"add_row failed: {last_row.cells}"
    assert last_row.cells[1].value == 777.0, f"add_row numeric: {last_row.cells[1].value}"
    print(f"  Last row: {[c.value for c in last_row.cells]}  OK")

    empty_sheet = doc2.sheets[1]
    assert empty_sheet.name == "EmptyTab", f"add_sheet failed: {empty_sheet.name!r}"
    print(f"  Sheet[1].name: {empty_sheet.name!r}  OK")

    # ── Step 6: CSV export ────────────────────────────────────────────────────
    csv_text = export_ods_to_csv(doc2)
    assert csv_text.strip(), "CSV export empty"
    assert "CONSUMER_PROOF" in csv_text, f"CSV missing mutation: {csv_text[:100]}"
    csv_path = OUTPUT_DIR / "consumer_proof_export.csv"
    csv_path.write_text(csv_text, encoding="utf-8")
    print(f"\n[EXPORT] CSV ({len(csv_text)} chars):")
    print(csv_text.strip())

    print("\nCONSUMER_PROOF: PASS — load -> inspect -> mutate -> save -> reload -> export all verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
