"""PBM consumer roundtrip proof — TC-FL-009.

Demonstrates the full read → inspect → write → re-read cycle for PBM files.
Proves DOGFOOD_PASS for the PBM write-back roundtrip capability.

Usage:
    python examples/python/pbm/pbm_consumer_roundtrip.py
"""

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

try:
    from pbm.pbm_parser import parse_pbm_strict, write_pbm
    from pbm.models import PbmDocument
except ImportError:
    import sys
    from pathlib import Path as _Path
    sys.path.insert(0, str(_Path(__file__).resolve().parents[3]))
from src.python.pbm.pbm_parser import parse_pbm_strict, write_pbm
from src.python.pbm.models import PbmDocument

SAMPLE = _REPO / "samples" / "by-format" / "pbm" / "valid" / "2x2-checker.pbm"


def main():
    print("=== PBM Consumer Roundtrip Proof ===")

    # Step 1: Read using domain model
    doc = PbmDocument.from_file(SAMPLE)
    print(f"[READ] spec_qname={doc.spec_qname!r}")
    print(f"[READ] width={doc.width}, height={doc.height}")
    assert doc.spec_qname == "pbm:image", f"Expected 'pbm:image', got {doc.spec_qname!r}"
    assert doc.width > 0 and doc.height > 0, "Dimensions must be positive"

    # Step 2: Parse to raw pixels using strict parser
    img = parse_pbm_strict(SAMPLE)
    pixels = img.pixels
    width = img.width
    height = img.height
    print(f"[INSPECT] {len(pixels)} pixels ({width}×{height})")
    assert len(pixels) == width * height, "Pixel count must match dimensions"

    # Step 3: Write to temp file
    with tempfile.NamedTemporaryFile(suffix=".pbm", delete=False) as tf:
        dest = Path(tf.name)

    write_pbm(pixels, width, height, dest, comment="consumer_roundtrip_proof")
    assert dest.exists(), "Write must produce a file"
    print(f"[WRITE] Wrote {dest.stat().st_size} bytes to temp file")

    # Step 4: Re-read and verify
    img2 = parse_pbm_strict(dest)
    assert img2.width == width, f"Width mismatch: {img2.width} != {width}"
    assert img2.height == height, f"Height mismatch: {img2.height} != {height}"
    assert img2.pixels == pixels, "Pixel data must survive roundtrip"
    print(f"[VERIFY] Re-read matches original — {width}×{height}, {len(pixels)} pixels")

    # Cleanup
    dest.unlink(missing_ok=True)

    print("\nDOGFOOD_PASS: PBM read + inspect + write + re-read roundtrip verified")


if __name__ == "__main__":
    main()
