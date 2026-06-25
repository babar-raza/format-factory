"""PBM consumer roundtrip — TC-D-006 (ALLFORMAT-DEEPENING-20260625).

load (domain model) → inspect → parse strict → write → reload → verify pixels.

Usage:
    python examples/python/pbm/consumer_roundtrip.py
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]

try:
    from pbm.pbm_parser import parse_pbm_strict, write_pbm
    from pbm.models import PbmDocument
except ImportError:
    sys.path.insert(0, str(_REPO / "src" / "python"))
    from pbm.pbm_parser import parse_pbm_strict, write_pbm  # type: ignore
    from pbm.models import PbmDocument  # type: ignore

SAMPLE = _REPO / "samples" / "by-format" / "pbm" / "valid" / "2x2-checker.pbm"


def main() -> int:
    print("=== PBM Consumer Roundtrip Proof ===")

    # Step 1: Domain model
    doc = PbmDocument.from_file(SAMPLE)
    print(f"[MODEL] spec_qname={doc.spec_qname!r}, {doc.width}x{doc.height}")
    assert doc.spec_qname == "pbm:image"
    assert doc.width > 0 and doc.height > 0

    # Step 2: Strict parse → inspect pixels
    img = parse_pbm_strict(SAMPLE)
    assert len(img.pixels) == img.width * img.height
    print(f"[PARSE] {img.width}x{img.height}, {len(img.pixels)} pixels")

    # Step 3: Write to temp file
    with tempfile.NamedTemporaryFile(suffix=".pbm", delete=False) as tf:
        dest = Path(tf.name)
    write_pbm(img.pixels, img.width, img.height, dest, comment="consumer_roundtrip")
    assert dest.exists() and dest.stat().st_size > 0
    print(f"[WRITE] {dest.stat().st_size} bytes")

    # Step 4: Reload and verify
    img2 = parse_pbm_strict(dest)
    assert img2.width == img.width and img2.height == img.height
    assert img2.pixels == img.pixels
    print(f"[VERIFY] {img2.width}x{img2.height}, {len(img2.pixels)} pixels match")

    dest.unlink(missing_ok=True)

    print("\nCONSUMER_PROOF: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
