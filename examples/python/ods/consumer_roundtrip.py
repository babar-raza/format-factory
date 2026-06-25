"""ODS consumer roundtrip — TC-D-004 (ALLFORMAT-DEEPENING-20260625).

load → inspect → mutate → write bytes → reload → verify roundtrip.

Usage:
    python examples/python/ods/consumer_roundtrip.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]

try:
    import ods
except ImportError:
    sys.path.insert(0, str(_REPO / "src" / "python"))
    import ods  # type: ignore

SAMPLE = _REPO / "samples" / "by-format" / "ods" / "valid" / "minimal-spreadsheet.ods"
OUT_DIR = _REPO / ".local" / "dogfood-proofs" / "ods-consumer-roundtrip"


def main() -> int:
    print("=== ODS Consumer Roundtrip Proof ===")

    # Step 1: Load and inspect
    doc = ods.parse_ods_strict(str(SAMPLE))
    sheet_names = ods.get_sheet_names(str(SAMPLE))
    row_count = ods.get_row_count(str(SAMPLE), 0)
    cell_00 = ods.get_cell_value(str(SAMPLE), 0, 0, 0)
    print(f"[LOAD] sheets={sheet_names}, rows={row_count}, cell(0,0,0)={cell_00!r}")
    assert len(doc.sheets) >= 1

    # Step 2: Export to CSV
    csv_text = ods.export_ods_to_csv(doc, 0)
    assert isinstance(csv_text, str)
    print(f"[EXPORT-CSV] {len(csv_text.splitlines())} lines")

    # Step 3: Mutate — set a cell and add a row
    ok1, msg1 = ods.set_cell_value(doc, 0, 1, 0, "CONSUMER_PROOF_ENTRY", "string")
    assert ok1, f"set_cell_value failed: {msg1}"
    ok2, msg2 = ods.add_row(doc, 0, ["RoundtripRow", 99.0])
    assert ok2, f"add_row failed: {msg2}"
    print(f"[MUTATE] row_count after mutation={len(doc.sheets[0].rows)}")

    # Step 4: Write to bytes and save
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "output.ods"
    ods_bytes = ods.document_to_ods_bytes(doc)
    out_path.write_bytes(ods_bytes)
    print(f"[WRITE] {out_path} ({len(ods_bytes)} bytes)")

    # Step 5: Reload and verify
    doc2 = ods.parse_ods_strict(str(out_path))
    rows2 = doc2.sheets[0].rows
    assert len(rows2) == len(doc.sheets[0].rows), f"Row count mismatch after roundtrip"
    proof_val = doc2.sheets[0].rows[1].cells[0].value
    last_val = doc2.sheets[0].rows[-1].cells[0].value
    assert proof_val == "CONSUMER_PROOF_ENTRY", f"proof entry missing: {proof_val!r}"
    assert last_val == "RoundtripRow", f"last row missing: {last_val!r}"
    print(f"[VERIFY] roundtrip OK — {len(rows2)} rows, proof entries confirmed")

    # Step 6: Analytics
    is_empty = ods.ods_is_empty(str(out_path))
    is_multi = ods.ods_is_multi_sheet(str(out_path))
    print(f"[ANALYTICS] is_empty={is_empty}, is_multi_sheet={is_multi}")

    print("\nCONSUMER_PROOF: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
