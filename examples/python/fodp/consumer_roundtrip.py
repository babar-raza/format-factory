"""Clean consumer proof: FODP load -> inspect -> analyze.

FODP (Flat ODF Presentation) is a read-only format in this package.
No write_fodp function exists. The consumer proof demonstrates the full
inspection and analytics flow.

Steps:
  1. Load .fodp file to neutral model dict
  2. Inspect: page_count, pages, slides, text
  3. Analyze: slide stats via analytics functions

DOGFOOD CONTRACT:
  - uses `import fodp` (installed package, not src/)
  - no src/ path manipulation
  - asserts real semantic result at every boundary

Note: FODP is READ-ONLY in Format Factory. No write_fodp function exists.
The consumer proof covers Steps 1-13 (load through inspection).

Runnable:
  python examples/python/fodp/consumer_roundtrip.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]

import fodp as fodp_pkg
from fodp import load, get_page_count, get_page_metadata
from fodp import fodp_slide_count, fodp_slide_titles, fodp_has_multi_slide

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

    print("\nCONSUMER_PROOF: PASS -- load -> inspect -> analyze (read-only format, no write_fodp)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
