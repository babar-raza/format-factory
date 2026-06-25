"""QOI consumer proof — TC-FL-009.

Demonstrates full QOI inspection using domain model and analytics.
QOI is a read-only format in this track (no write_qoi available).
Consumer proof covers: parse + domain model + full analytics suite.

DOGFOOD_PASS: read + inspect + analytics verified.

Usage:
    python examples/python/qoi/qoi_consumer_roundtrip.py
"""

import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.qoi.models import QoiDocument
from src.python.qoi.image_document import (
    qoi_dimensions,
    qoi_pixel_count,
    qoi_channel_count,
    qoi_is_opaque,
    qoi_average_brightness,
    qoi_total_brightness,
)

SAMPLE = _REPO / "samples" / "by-format" / "qoi" / "valid" / "4x1-gradient.qoi"


def main():
    print("=== QOI Consumer Proof ===")

    # Step 1: Domain model
    doc = QoiDocument.from_file(SAMPLE)
    print(f"[MODEL] spec_qname={doc.spec_qname!r}")
    assert doc.spec_qname == "qoi:image", f"Expected 'qoi:image', got {doc.spec_qname!r}"
    assert doc.width > 0 and doc.height > 0, "Dimensions must be positive"
    print(f"[MODEL] {doc.width}×{doc.height}, channels={doc.channels}")

    # Step 2: Analytics inspection
    dims = qoi_dimensions(str(SAMPLE))
    assert dims["width"] == doc.width and dims["height"] == doc.height
    pixel_count = qoi_pixel_count(str(SAMPLE))
    assert pixel_count == doc.width * doc.height
    channel_count = qoi_channel_count(str(SAMPLE))
    is_opaque = qoi_is_opaque(str(SAMPLE))
    avg_brightness = qoi_average_brightness(str(SAMPLE))
    total_brightness = qoi_total_brightness(str(SAMPLE))

    print(f"[ANALYTICS] pixels={pixel_count}, channels={channel_count}, opaque={is_opaque}")
    print(f"[ANALYTICS] avg_brightness={avg_brightness:.3f}, total={total_brightness:.1f}")

    # Step 3: to_dict verification
    d = doc.to_dict()
    assert "width" in d
    assert d["width"] == doc.width
    assert d["height"] == doc.height
    assert doc.spec_qname == "qoi:image"
    print(f"[DICT] to_dict keys: {sorted(d.keys())}")

    print("\nDOGFOOD_PASS: QOI domain model + analytics inspection verified")
    print("NOTE: QOI write-back not available in this track (read-only format)")


if __name__ == "__main__":
    main()
