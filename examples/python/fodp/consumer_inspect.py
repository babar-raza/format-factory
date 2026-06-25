"""Consumer proof: FODP load -> inspect -> analyze -> export.

FODP is a read-only format. write_fodp() raises NotImplementedError.
Use load() + export_to_*() for all read/export workflows.

Steps:
  1. Load .fodp file to neutral model dict
  2. Inspect: page_count, pages, slides, text
  3. Analyze: slide stats via analytics functions
  4. Export: export_to_txt, export_to_csv, export_to_json

DOGFOOD CONTRACT:
  - uses `import fodp` (installed package, not src/)
  - no src/ path manipulation
  - asserts real semantic result at every boundary

Runnable:
  python examples/python/fodp/consumer_inspect.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]

import fodp as fodp_pkg
from fodp import load, get_page_count, get_page_metadata
from fodp import fodp_slide_count, fodp_slide_titles, fodp_has_multi_slide
from fodp import export_to_txt, export_to_csv, export_to_json

SAMPLE_FODP = _REPO / "samples" / "by-format" / "fodp" / "two-slides-basic.fodp"
MINIMAL_FODP = _REPO / "samples" / "by-format" / "fodp" / "minimal-presentation.fodp"
OUTPUT_DIR = _REPO / ".local" / "dogfood-proofs" / "fodp"


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Source: {SAMPLE_FODP}")
    print(f"FODP package: {fodp_pkg.__file__}")
    print()

    # Step 1: Load
    model = load(str(SAMPLE_FODP))
    assert isinstance(model, dict)
    assert model.get("is_fodp") is True
    print(f"[LOAD] page_count={model['page_count']}, styles_count={model['styles_count']}")
    assert model["page_count"] >= 1

    # Step 2: Inspect
    page_count = get_page_count(str(SAMPLE_FODP))
    assert page_count == model["page_count"]
    print(f"[INSPECT] get_page_count={page_count}")

    for i, page in enumerate(model["pages"]):
        print(f"  slide[{i}]: name={page['name']!r}, title={page.get('title')!r}, texts={page['text_content']}")
    assert len(model["pages"]) == page_count

    # Step 3: Analytics
    slide_count = fodp_slide_count(str(SAMPLE_FODP))
    titles = fodp_slide_titles(str(SAMPLE_FODP))
    multi = fodp_has_multi_slide(str(SAMPLE_FODP))
    print(f"\n[ANALYZE] slide_count={slide_count}, titles={titles!r}, has_multi_slide={multi}")
    assert slide_count == page_count
    assert isinstance(titles, list)
    assert multi == (page_count > 1)

    # Step 4: Minimal presentation inspect
    model2 = load(str(MINIMAL_FODP))
    assert model2.get("is_fodp") is True
    minimal_pages = get_page_count(str(MINIMAL_FODP))
    print(f"\n[MINIMAL] {MINIMAL_FODP.name}: pages={minimal_pages}, text={model2['pages'][0]['text_content']!r}")

    # Step 5: Export
    txt = export_to_txt(str(SAMPLE_FODP))
    csv_out = export_to_csv(str(SAMPLE_FODP))
    json_out = export_to_json(str(SAMPLE_FODP))
    assert isinstance(txt, str)
    assert "slide_index" in csv_out
    import json as _json
    parsed = _json.loads(json_out)
    assert parsed.get("is_fodp") is True
    print(f"\n[EXPORT] txt={len(txt)}chars, csv_rows={csv_out.count(chr(10))}, json_pages={len(parsed['pages'])}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "export.csv").write_text(csv_out)
    (OUTPUT_DIR / "export.json").write_text(json_out)

    print("\nCONSUMER_PROOF: PASS -- load -> inspect -> analyze -> export (txt/csv/json)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
