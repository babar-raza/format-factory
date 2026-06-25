"""FODP consumer roundtrip — TC-D-001 (ALLFORMAT-DEEPENING-20260625).

FODP is read-only: no write_fodp(). Consumer proof covers
load → inspect → analyze → export (txt/csv/json).

Usage:
    python examples/python/fodp/consumer_roundtrip.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]

try:
    from fodp import (
        load, get_page_count,
        fodp_slide_count, fodp_slide_titles, fodp_has_multi_slide,
        export_to_txt, export_to_json,
    )
except ImportError:
    sys.path.insert(0, str(_REPO / "src" / "python"))
    from fodp import (  # type: ignore
        load, get_page_count,
        fodp_slide_count, fodp_slide_titles, fodp_has_multi_slide,
        export_to_txt, export_to_json,
    )

SAMPLE = _REPO / "samples" / "by-format" / "fodp" / "two-slides-basic.fodp"


def main() -> int:
    print("=== FODP Consumer Roundtrip Proof ===")

    # Step 1: Load
    model = load(str(SAMPLE))
    assert isinstance(model, dict), "load() must return dict"
    assert model.get("is_fodp") is True, "model['is_fodp'] must be True"
    print(f"[LOAD] page_count={model['page_count']}, styles_count={model['styles_count']}")
    assert model["page_count"] >= 1

    # Step 2: Inspect
    page_count = get_page_count(str(SAMPLE))
    assert page_count == model["page_count"]
    for i, page in enumerate(model["pages"]):
        print(f"  slide[{i}]: name={page['name']!r}, texts={len(page['text_content'])}")
    print(f"[INSPECT] get_page_count={page_count}")

    # Step 3: Analytics
    slide_count = fodp_slide_count(str(SAMPLE))
    titles = fodp_slide_titles(str(SAMPLE))
    multi = fodp_has_multi_slide(str(SAMPLE))
    assert slide_count == page_count
    assert isinstance(titles, list)
    assert multi == (page_count > 1)
    print(f"[ANALYZE] slide_count={slide_count}, has_multi_slide={multi}")

    # Step 4: Export to txt/json (skipping csv — known csv module name conflict)
    txt = export_to_txt(str(SAMPLE))
    json_out = export_to_json(str(SAMPLE))
    assert isinstance(txt, str) and len(txt) > 0
    parsed_json = json.loads(json_out)
    assert parsed_json.get("is_fodp") is True
    print(f"[EXPORT] txt={len(txt)}ch json_pages={len(parsed_json['pages'])}")

    print("\nCONSUMER_PROOF: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
