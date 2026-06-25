"""Clean consumer proof: FODG load -> inspect -> mutate -> save -> export.

FODG (Flat ODF Graphics) is a flat XML drawing format.
load() returns a dict with pages/shapes/text_content.

Steps:
  1. Load .fodg file to neutral model dict
  2. Inspect: page_count, pages, shapes, text
  3. Mutate: add text_content entry, write_fodg
  4. Reload and verify
  5. Export to JSON/text

DOGFOOD CONTRACT:
  - uses `import fodg` (installed package, not src/)
  - no src/ path manipulation
  - asserts real semantic result at every boundary

Runnable:
  python examples/python/fodg/consumer_roundtrip.py
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]

import fodg as fodg_pkg
from fodg import load, get_page_count, export_to_txt, export_to_json, write_fodg

SAMPLE_FODG = _REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg"
OUTPUT_DIR = _REPO / ".local" / "dogfood-proofs" / "fodg"


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Source: {SAMPLE_FODG}")
    print(f"FODG package: {fodg_pkg.__file__}")
    print()

    # Step 1: Load
    model = load(str(SAMPLE_FODG))
    assert isinstance(model, dict)
    assert model.get("is_fodg") is True
    page_count = model["page_count"]
    print(f"[LOAD] page_count={page_count}, shapes_total={model['shapes_total']}")
    assert page_count >= 1

    # Step 2: Inspect
    page0 = model["pages"][0]
    print(f"[INSPECT] page[0]: name={page0['name']!r}, shape_count={page0['shape_count']}")
    print(f"  text_content={page0['text_content']!r}")
    txt = export_to_txt(str(SAMPLE_FODG))
    print(f"  export_to_txt: {txt!r}")
    json_str = export_to_json(model)
    print(f"  export_to_json: {json_str[:80]!r}...")

    # Step 3: Mutate
    model2 = copy.deepcopy(model)
    model2["pages"][0]["text_content"].append("CONSUMER_PROOF")

    out_path = str(OUTPUT_DIR / "consumer_proof.fodg")
    write_fodg(model2, out_path)
    size = Path(out_path).stat().st_size
    print(f"\n[MUTATE+SAVE] added 'CONSUMER_PROOF' text -> {out_path} ({size} bytes)")

    # Step 4: Reload and verify
    model3 = load(out_path)
    text3 = model3["pages"][0]["text_content"]
    assert "CONSUMER_PROOF" in text3, f"Mutation not found: {text3}"
    print(f"[RELOAD] text_content={text3}  OK")

    # Step 5: Export
    txt3 = export_to_txt(out_path)
    assert "CONSUMER_PROOF" in txt3, f"Export missing mutation: {txt3}"
    print(f"\n[EXPORT] text: {txt3!r}  OK")

    print("\nCONSUMER_PROOF: PASS -- load -> inspect -> mutate -> save -> reload -> export verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
