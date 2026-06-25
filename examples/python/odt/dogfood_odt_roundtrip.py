"""Dogfood example: Read an ODT file with Format Factory, transform, and write output.

Demonstrates real-world usage of the ODT read + write capability.
New in sprint ff-domain-models-ext-20260624: odt_writer.py added.

Runnable: python examples/python/odt/dogfood_odt_roundtrip.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO / "src" / "python") not in sys.path:
    sys.path.insert(0, str(_REPO / "src" / "python"))

from odt.odt_parser import parse_odt_strict
from odt.odt_writer import odt_from_model, write_odt

SAMPLE_ODT = _REPO / "samples" / "by-format" / "odt" / "valid" / "two-paragraphs.odt"
OUTPUT_DIR = _REPO / ".local" / "dogfood-proofs" / "odt-roundtrip"


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Parse input ODT
    print(f"Reading: {SAMPLE_ODT}")
    doc = parse_odt_strict(str(SAMPLE_ODT))
    print(f"Parsed {len(doc.paragraphs)} paragraphs")
    for i, p in enumerate(doc.paragraphs):
        print(f"  [{i}] {p.text!r}")

    # Step 2: Write the document back out using odt_from_model (round-trip)
    roundtrip_path = OUTPUT_DIR / "roundtrip-output.odt"
    odt_from_model(doc, roundtrip_path)
    print(f"\nRound-trip write: {roundtrip_path}")

    # Step 3: Verify round-trip fidelity
    doc2 = parse_odt_strict(str(roundtrip_path))
    original_texts = [p.text for p in doc.paragraphs]
    roundtrip_texts = [p.text for p in doc2.paragraphs]
    if original_texts != roundtrip_texts:
        print(f"ERROR: round-trip mismatch: {original_texts!r} != {roundtrip_texts!r}")
        return 1
    print(f"Round-trip verified: {len(doc2.paragraphs)} paragraphs match")

    # Step 4: Create a new ODT from plain text strings
    new_path = OUTPUT_DIR / "new-from-text.odt"
    write_odt(["Format Factory dogfood", "ODT writer capability", "Sprint 20260624"], new_path, heading="FF Dogfood Export")
    doc3 = parse_odt_strict(str(new_path))
    print(f"\nNew ODT created: {new_path} ({len(doc3.paragraphs)} paragraphs)")

    print("\nDOGFOOD PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
