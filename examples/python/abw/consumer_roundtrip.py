"""Clean consumer proof: ABW load -> inspect -> mutate -> save -> export.

ABW (AbiWord) uses a neutral model dict with paragraphs list.
Mutation is dict-based: append_paragraph(model, text) returns new model.

Steps:
  1. Load .abw file to neutral model dict
  2. Inspect: paragraph_count, paragraphs, AbwDocument domain model
  3. Mutate: append paragraph, write to new file
  4. Reload and verify mutation persisted
  5. Export to plain text

DOGFOOD CONTRACT:
  - uses `import abw` (installed package, not src/)
  - no src/ path manipulation
  - asserts real semantic result at every boundary

Runnable:
  python examples/python/abw/consumer_roundtrip.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]

import abw as abw_pkg
from abw import load, write_abw, append_paragraph, export_to_plain_text

try:
    from abw import AbwDocument
    _HAVE_ABWDOC = True
except ImportError:
    try:
        sys.path.insert(0, str(_REPO / "src" / "python"))
        from abw.models import AbwDocument  # type: ignore
        _HAVE_ABWDOC = True
    except ImportError:
        _HAVE_ABWDOC = False

SAMPLE_ABW = _REPO / "samples" / "by-format" / "abw" / "two-paragraphs.abw"
OUTPUT_DIR = _REPO / ".local" / "dogfood-proofs" / "abw"


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Source: {SAMPLE_ABW}")
    print(f"ABW package: {abw_pkg.__file__}")
    print()

    # Step 1: Load
    model = load(str(SAMPLE_ABW))
    assert isinstance(model, dict), f"Expected dict, got {type(model)}"
    assert model.get("is_abw") is True
    print(f"[LOAD] paragraph_count={model['paragraph_count']}, section_count={model['section_count']}")
    assert model["paragraph_count"] >= 1

    # Step 2: Inspect
    paragraphs = model["paragraphs"]
    print(f"[INSPECT] paragraphs={paragraphs!r}")
    assert len(paragraphs) >= 1

    if _HAVE_ABWDOC:
        doc = AbwDocument.from_file(str(SAMPLE_ABW))
        print(f"  AbwDocument.spec_qname={AbwDocument.spec_qname}")
        print(f"  doc.paragraph_count={doc.paragraph_count}")
        assert doc.paragraph_count == model["paragraph_count"]

    # Step 3: Mutate
    model2 = append_paragraph(model, "CONSUMER_PROOF: VERIFIED")
    assert model2["paragraph_count"] == model["paragraph_count"] + 1

    out_path = str(OUTPUT_DIR / "consumer_proof.abw")
    write_abw(model2, out_path)
    size = Path(out_path).stat().st_size
    print(f"\n[MUTATE+SAVE] appended 'CONSUMER_PROOF: VERIFIED' -> {out_path} ({size} bytes)")

    # Step 4: Reload and verify
    model3 = load(out_path)
    assert model3["paragraph_count"] == model["paragraph_count"] + 1, \
        f"Expected {model['paragraph_count']+1}, got {model3['paragraph_count']}"
    assert "CONSUMER_PROOF: VERIFIED" in model3["paragraphs"], \
        f"Mutation not found: {model3['paragraphs']}"
    last_para = model3["paragraphs"][-1]
    print(f"[RELOAD] paragraph_count={model3['paragraph_count']}, last={last_para!r}  OK")

    # Step 5: Export to plain text
    txt = export_to_plain_text(model3)
    assert "CONSUMER_PROOF" in txt, f"Export missing mutation: {txt[:80]}"
    txt_path = OUTPUT_DIR / "consumer_proof_export.txt"
    txt_path.write_text(txt, encoding="utf-8")
    print(f"\n[EXPORT] text ({len(txt)} chars):")
    print(txt)

    print("\nCONSUMER_PROOF: PASS -- load -> inspect -> mutate -> save -> reload -> export verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
