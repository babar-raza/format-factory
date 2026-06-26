"""
ODS (OpenDocument Spreadsheet) — read, inspect, mutate, write, export to CSV.

CONSUMER_PROOF: PASS
"""
from pathlib import Path
import sys

_REPO = Path(__file__).resolve().parent.parent.parent.parent
try:
    import ods
except ImportError:
    sys.path.insert(0, str(_REPO))
    import src.python.ods as ods

SAMPLE = _REPO / "samples/by-format/ods/valid/minimal-spreadsheet.ods"


def main() -> None:
    # --- READ ---
    doc = ods.parse_ods_strict(str(SAMPLE))
    print(f"sheet_count: {len(doc.sheets)}")
    print(f"sheet_names: {ods.get_sheet_names(str(SAMPLE))}")
    print(f"row_count(sheet 0): {ods.get_row_count(str(SAMPLE), 0)}")
    print(f"cell(0,0,0): {ods.get_cell_value(str(SAMPLE), 0, 0, 0)}")
    print(f"cell(0,0,1): {ods.get_cell_value(str(SAMPLE), 0, 0, 1)}")

    # --- EXPORT TO CSV ---
    csv_text = ods.export_ods_to_csv(doc, 0)
    print(f"CSV export:\n{csv_text}")

    # --- MUTATE ---
    ok, msg = ods.set_cell_value(doc, 0, 1, 0, "Consumer_Proof", "string")
    assert ok, f"set_cell_value failed: {msg}"

    ok2, msg2 = ods.add_row(doc, 0, ["Zeta", 99.0])
    assert ok2, f"add_row failed: {msg2}"

    print(f"After mutation — row_count(sheet 0): {len(doc.sheets[0].rows)}")

    # --- WRITE & ROUNDTRIP ---
    out_dir = _REPO / ".local/dogfood-proofs/ods-roundtrip"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "output.ods"
    ods_bytes = ods.document_to_ods_bytes(doc)
    out_path.write_bytes(ods_bytes)
    print(f"Written: {out_path} ({len(ods_bytes)} bytes)")

    doc2 = ods.parse_ods_strict(str(out_path))
    assert len(doc2.sheets[0].rows) == 3, "roundtrip row count mismatch"
    assert doc2.sheets[0].rows[1].cells[0].value == "Consumer_Proof"
    assert doc2.sheets[0].rows[2].cells[0].value == "Zeta"
    print("ROUNDTRIP: PASS")

    # --- ANALYTICS ---
    print(f"spec_qname: {ods.spec_qname}")
    print(f"ods_is_empty: {ods.ods_is_empty(str(out_path))}")
    print(f"ods_is_multi_sheet: {ods.ods_is_multi_sheet(str(out_path))}")
    print(f"ods_numeric_cell_count: {ods.ods_numeric_cell_count(str(out_path))}")

    print("\nCONSUMER_PROOF: PASS")


if __name__ == "__main__":
    main()
