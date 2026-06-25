"""Clean consumer proof: DIF load -> inspect -> mutate -> save -> export.

DIF (Data Interchange Format) uses a flat column-major cell model.
DifDocument has vectors (columns), tuples (rows), and a single flat rows list.

Steps:
  1. Load .dif file to DifDocument
  2. Inspect: vectors, tuples, cells, spec_qname
  3. Mutate: append cells (DIF mutation is append to rows[0])
  4. Save and reload
  5. Export to HTML

DOGFOOD CONTRACT:
  - uses `import dif` (installed package, not src/)
  - no src/ path manipulation
  - asserts real semantic result at every boundary

Runnable:
  python examples/python/dif/consumer_roundtrip.py
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]

import dif as dif_pkg
from dif import parse_dif_strict, write_dif, export_to_html
from dif.dif_parser import DifDocument, DifCell

SAMPLE_DIF = _REPO / "samples" / "by-format" / "dif" / "valid" / "minimal-2x2.dif"
OUTPUT_DIR = _REPO / ".local" / "dogfood-proofs" / "dif"


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Source: {SAMPLE_DIF}")
    print(f"DIF package: {dif_pkg.__file__}")
    print()

    # Step 1: Load
    doc = parse_dif_strict(str(SAMPLE_DIF))
    assert isinstance(doc, DifDocument), f"Expected DifDocument, got {type(doc)}"
    print(f"[LOAD] spec_qname={doc.spec_qname}")
    print(f"  vectors={doc.vectors}, tuples={doc.tuples}")
    print(f"  cells in row[0]: {len(doc.rows[0])}")
    assert doc.vectors >= 1 and doc.tuples >= 1

    # Step 2: Inspect cells
    string_cells = [c for c in doc.rows[0] if c.value_type == "string"]
    numeric_cells = [c for c in doc.rows[0] if c.value_type == "numeric"]
    print(f"[INSPECT] string cells={len(string_cells)}, numeric cells={len(numeric_cells)}")
    first_string = next((c.value for c in doc.rows[0] if c.value_type == "string"), None)
    print(f"  first string value={first_string!r}")

    # Step 3: Mutate — append cells (DIF is column-major, all cells are in rows[0])
    doc2 = copy.deepcopy(doc)
    doc2.rows[0].append(DifCell(value='"CONSUMER_PROOF"', value_type="special"))
    doc2.rows[0].append(DifCell(value="V", value_type="string"))
    doc2.rows[0].append(DifCell(value='"VERIFIED"', value_type="special"))
    doc2.rows[0].append(DifCell(value="V", value_type="string"))

    out_path = str(OUTPUT_DIR / "consumer_proof.dif")
    write_dif(doc2, out_path)
    size = Path(out_path).stat().st_size
    print(f"\n[MUTATE+SAVE] appended CONSUMER_PROOF cells -> {out_path} ({size} bytes)")

    # Step 4: Reload and verify
    doc3 = parse_dif_strict(out_path)
    all_values = [c.value for c in doc3.rows[0]]
    assert '"CONSUMER_PROOF"' in all_values, f"Mutation not found: {all_values}"
    print(f"[RELOAD] total cells={len(doc3.rows[0])}, CONSUMER_PROOF present  OK")

    # Step 5: Export to HTML
    html = export_to_html(out_path)
    assert "CONSUMER_PROOF" in html, f"HTML missing mutation: {html[:100]}"
    html_path = OUTPUT_DIR / "consumer_proof_export.html"
    html_path.write_text(html, encoding="utf-8")
    print(f"\n[EXPORT] HTML ({len(html)} chars, saved to {html_path.name})")
    print(html[:200])

    print("\nCONSUMER_PROOF: PASS -- load -> inspect -> mutate -> save -> reload -> html-export verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
