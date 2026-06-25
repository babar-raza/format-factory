"""
edit_save_fods.py — Example: load, edit, and save a FODS spreadsheet.

This example demonstrates the R76 edit-and-save workflow for FODS:

1. Parse an existing FODS file into the neutral model
2. Use workbook_set_cell_value() to modify a cell
3. Check workbook_warnings_for_unsupported_edit() for safety disclosures
4. Write the modified workbook back to a new FODS file

Requirements:
    pip install format-factory-fods

Usage:
    python examples/python/fods/edit_save_fods.py

License: Apache-2.0 — Format Factory Python FOSS track
"""
from __future__ import annotations

import sys
from pathlib import Path

# Allow running from repo root without install
REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

try:
    from fods import (
except ImportError:
    import sys
    from pathlib import Path as _Path
    sys.path.insert(0, str(_Path(__file__).resolve().parents[3]))
from src.python.fods import (
    parse_fods,
    write_fods,
    workbook_set_cell_value,
    workbook_warnings_for_unsupported_edit,
    workbook_sheet_summary,
)

SAMPLE_FODS = REPO_ROOT / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods"


def main() -> None:
    print("=== FODS Edit-and-Save Example ===\n")

    # Step 1: Parse
    print(f"Loading: {SAMPLE_FODS.name}")
    wb = parse_fods(SAMPLE_FODS)
    summary = workbook_sheet_summary(wb)
    print(f"Sheets: {[s['name'] for s in summary]}")
    print(f"Total cells: {sum(s['cell_count'] for s in summary)}")

    sheet_name = wb["sheets"][0]["name"]

    # Step 2: Check for edit warnings
    warnings = workbook_warnings_for_unsupported_edit(wb, sheet_name, 0, 0)
    if warnings:
        print("\nEdit warnings:")
        for w in warnings:
            print(f"  WARNING: {w}")
    else:
        print("\nNo edit warnings for cell (0, 0)")

    # Step 3: Edit
    print(f"\nBefore edit: {wb['sheets'][0]['rows'][0]['cells'][0]['value']!r}")
    ok, msg = workbook_set_cell_value(wb, sheet_name, 0, 0, "Edited by Format Factory", "string")
    if not ok:
        print(f"Edit failed: {msg}")
        sys.exit(1)
    print(f"After edit: {wb['sheets'][0]['rows'][0]['cells'][0]['value']!r}")
    print(f"Edit result: {msg}")

    # Step 4: Save
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".fods", delete=False) as tf:
        out_path = Path(tf.name)

    write_fods(wb, out_path)
    print(f"\nSaved to: {out_path}")

    # Step 5: Verify round-trip
    wb2 = parse_fods(out_path)
    val = wb2["sheets"][0]["rows"][0]["cells"][0]["value"]
    assert val == "Edited by Format Factory", f"Round-trip mismatch: {val!r}"
    print("Round-trip verification: PASS")

    print("\n=== Edit-and-Save Example Complete ===")


if __name__ == "__main__":
    main()
