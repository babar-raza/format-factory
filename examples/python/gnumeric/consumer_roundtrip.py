"""Clean consumer proof: Gnumeric load -> inspect -> mutate -> save -> export.

Gnumeric uses a neutral model dict with sheets/cell_grid.
Mutation is dict-based: update cell_grid, then write_gnumeric().

Steps:
  1. Load .gnumeric file to neutral model dict
  2. Inspect: sheet_count, cell_count, GnumericDocument domain model
  3. Mutate: add cells to grid, write to new file
  4. Reload and verify mutations persisted
  5. Export to CSV

DOGFOOD CONTRACT:
  - uses `import gnumeric` (installed package, not src/)
  - no src/ path manipulation
  - asserts real semantic result at every boundary

Runnable:
  python examples/python/gnumeric/consumer_roundtrip.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]

import gnumeric as gn_pkg
from gnumeric import GnumericDocument, load, write_gnumeric, export_to_csv

SAMPLE_GNUMERIC = _REPO / "samples" / "by-format" / "gnumeric" / "minimal-spreadsheet.gnumeric"
OUTPUT_DIR = _REPO / ".local" / "dogfood-proofs" / "gnumeric"


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Source: {SAMPLE_GNUMERIC}")
    print(f"Gnumeric package: {gn_pkg.__file__}")
    print()

    # Step 1: Load
    model = load(str(SAMPLE_GNUMERIC))
    assert isinstance(model, dict), f"Expected dict, got {type(model)}"
    assert model.get("is_gnumeric") is True
    print(f"[LOAD] sheet_count={model['sheet_count']}, cell_count={model['cell_count']}")
    assert model["sheet_count"] >= 1

    # Step 2: Inspect via GnumericDocument
    doc = GnumericDocument.from_file(str(SAMPLE_GNUMERIC))
    assert doc.spec_qname == "gnumeric:workbook", f"spec_qname={doc.spec_qname!r}"
    print(f"[INSPECT] spec_qname={doc.spec_qname}")
    print(f"  sheet_count={doc.sheet_count}")
    sheet0 = model["sheets"][0]
    print(f"  sheet[0]: name={sheet0['name']!r}, cells={sheet0['cell_count']}")
    grid0 = sheet0["cell_grid"]
    print(f"  cell[0,0]={grid0.get((0, 0))!r}")

    # Step 3: Mutate — dict-based
    sheet0["cell_grid"][(1, 0)] = "CONSUMER_PROOF"
    sheet0["cell_grid"][(1, 1)] = "VERIFIED"
    sheet0["cell_count"] = len(sheet0["cell_grid"])
    model["cell_count"] = sum(s["cell_count"] for s in model["sheets"])

    out_path = str(OUTPUT_DIR / "consumer_proof.gnumeric")
    write_gnumeric(model, out_path)
    size = Path(out_path).stat().st_size
    print(f"\n[MUTATE+SAVE] cell[1,0]=CONSUMER_PROOF, cell[1,1]=VERIFIED -> {out_path} ({size} bytes)")

    # Step 4: Reload and verify
    model2 = load(out_path)
    grid2 = model2["sheets"][0]["cell_grid"]
    assert grid2.get((1, 0)) == "CONSUMER_PROOF", f"Mutation failed: {grid2}"
    assert grid2.get((1, 1)) == "VERIFIED", f"Mutation failed: {grid2}"
    print(f"[RELOAD] cell[1,0]={grid2[(1, 0)]!r}  OK")
    print(f"[RELOAD] cell[1,1]={grid2[(1, 1)]!r}  OK")

    # Step 5: CSV export
    csv_text = export_to_csv(out_path)
    assert "CONSUMER_PROOF" in csv_text, f"CSV missing mutation: {csv_text[:80]}"
    csv_path = OUTPUT_DIR / "consumer_proof_export.csv"
    csv_path.write_text(csv_text, encoding="utf-8")
    print(f"\n[EXPORT] CSV ({len(csv_text)} chars):")
    print(csv_text.strip())

    print("\nCONSUMER_PROOF: PASS -- load -> inspect -> mutate -> save -> reload -> export verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
