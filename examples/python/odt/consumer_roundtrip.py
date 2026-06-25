"""ODT consumer roundtrip — TC-D-005 (ALLFORMAT-DEEPENING-20260625).

load → inspect paragraphs → write (roundtrip) → reload → verify.

Usage:
    python examples/python/odt/consumer_roundtrip.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]

try:
    from odt.odt_parser import parse_odt_strict
    from odt.odt_writer import odt_from_model, write_odt
except ImportError:
    sys.path.insert(0, str(_REPO / "src" / "python"))
    from odt.odt_parser import parse_odt_strict  # type: ignore
    from odt.odt_writer import odt_from_model, write_odt  # type: ignore

SAMPLE = _REPO / "samples" / "by-format" / "odt" / "valid" / "minimal-document.odt"
OUT_DIR = _REPO / ".local" / "dogfood-proofs" / "odt-consumer-roundtrip"


def main() -> int:
    print("=== ODT Consumer Roundtrip Proof ===")

    # Step 1: Load and inspect
    doc = parse_odt_strict(str(SAMPLE))
    print(f"[LOAD] {len(doc.paragraphs)} paragraph(s)")
    for i, p in enumerate(doc.paragraphs):
        print(f"  [{i}] {p.text!r}")
    assert len(doc.paragraphs) >= 1

    # Step 2: Write (roundtrip via odt_from_model)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    roundtrip_path = OUT_DIR / "roundtrip.odt"
    odt_from_model(doc, roundtrip_path)
    assert roundtrip_path.exists() and roundtrip_path.stat().st_size > 0
    print(f"[WRITE] roundtrip -> {roundtrip_path} ({roundtrip_path.stat().st_size} bytes)")

    # Step 3: Reload and verify
    doc2 = parse_odt_strict(str(roundtrip_path))
    original = [p.text for p in doc.paragraphs]
    roundtrip = [p.text for p in doc2.paragraphs]
    assert original == roundtrip, f"Paragraph mismatch: {original!r} != {roundtrip!r}"
    print(f"[VERIFY] {len(doc2.paragraphs)} paragraph(s) match")

    # Step 4: Create a new ODT from scratch
    new_path = OUT_DIR / "new-from-text.odt"
    write_odt(["Format Factory consumer roundtrip", "ODT writer capability verified"], new_path)
    doc3 = parse_odt_strict(str(new_path))
    assert len(doc3.paragraphs) >= 2
    print(f"[NEW] created from scratch: {len(doc3.paragraphs)} paragraph(s)")

    print("\nCONSUMER_PROOF: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
