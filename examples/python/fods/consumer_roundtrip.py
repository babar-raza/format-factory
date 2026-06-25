"""FODS consumer roundtrip — TC-D-002 (ALLFORMAT-DEEPENING-20260625).

load → inspect → add row → write → reload → verify roundtrip.

Usage:
    python examples/python/fods/consumer_roundtrip.py
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]

try:
    from fods import parse_fods_strict, write_fods
except ImportError:
    sys.path.insert(0, str(_REPO / "src" / "python"))
    from fods import parse_fods_strict, write_fods  # type: ignore

SAMPLE = _REPO / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods"


def main() -> int:
    print("=== FODS Consumer Roundtrip Proof ===")

    # Step 1: Load
    workbook = parse_fods_strict(str(SAMPLE))
    assert isinstance(workbook, dict), "parse_fods_strict() must return dict"
    sheet_count = workbook.get("sheet_count", len(workbook.get("sheets", [])))
    print(f"[LOAD] sheet_count={sheet_count}")
    assert len(workbook.get("sheets", [])) >= 1

    # Step 2: Inspect first sheet
    sheet = workbook["sheets"][0]
    rows_before = len(sheet.get("rows", []))
    print(f"[INSPECT] sheet={sheet['name']!r}, rows={rows_before}")

    # Step 3: Add a new row
    new_row = {"cells": [
        {"value": "CONSUMER_PROOF_ENTRY", "value_type": "string"},
        {"value": 42.0, "value_type": "float"},
    ]}
    workbook["sheets"][0].setdefault("rows", []).append(new_row)
    print(f"[MUTATE] added row; new row count={len(workbook['sheets'][0]['rows'])}")

    # Step 5: Write to temp file
    with tempfile.NamedTemporaryFile(suffix=".fods", delete=False) as tf:
        out_path = Path(tf.name)
    write_fods(workbook, str(out_path))
    assert out_path.exists() and out_path.stat().st_size > 0
    print(f"[WRITE] {out_path.stat().st_size} bytes")

    # Step 6: Reload and verify
    wb2 = parse_fods_strict(str(out_path))
    rows2 = wb2["sheets"][0].get("rows", [])
    assert len(rows2) == rows_before + 1, f"Expected {rows_before+1} rows, got {len(rows2)}"
    # Find the proof entry
    last_row = rows2[-1]
    values = [c.get("value") for c in last_row.get("cells", [])]
    assert "CONSUMER_PROOF_ENTRY" in values, f"Proof entry missing; got {values}"
    print(f"[VERIFY] roundtrip OK -- {len(rows2)} rows, proof entry confirmed")

    out_path.unlink(missing_ok=True)

    print("\nCONSUMER_PROOF: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
