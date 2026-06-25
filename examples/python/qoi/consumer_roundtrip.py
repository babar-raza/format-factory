"""QOI consumer roundtrip — TC-D-009 (ALLFORMAT-DEEPENING-20260625).

QOI is read-only (no write_qoi). Consumer proof: domain model + analytics.

Usage:
    python examples/python/qoi/consumer_roundtrip.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]

try:
    from qoi.models import QoiDocument
    from qoi.image_document import (
        qoi_dimensions, qoi_pixel_count, qoi_channel_count,
        qoi_is_opaque, qoi_average_brightness, qoi_total_brightness,
    )
except ImportError:
    sys.path.insert(0, str(_REPO / "src" / "python"))
    from qoi.models import QoiDocument  # type: ignore
    from qoi.image_document import (  # type: ignore
        qoi_dimensions, qoi_pixel_count, qoi_channel_count,
        qoi_is_opaque, qoi_average_brightness, qoi_total_brightness,
    )

SAMPLE = _REPO / "samples" / "by-format" / "qoi" / "valid" / "4x1-gradient.qoi"


def main() -> int:
    print("=== QOI Consumer Roundtrip Proof ===")

    # Step 1: Domain model
    doc = QoiDocument.from_file(SAMPLE)
    print(f"[MODEL] spec_qname={doc.spec_qname!r}, {doc.width}x{doc.height}, channels={doc.channels}")
    assert doc.spec_qname == "qoi:image"
    assert doc.width > 0 and doc.height > 0

    # Step 2: Analytics
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
    assert d["width"] == doc.width and d["height"] == doc.height
    print(f"[DICT] keys={sorted(d.keys())}")

    print("\nNOTE: QOI is read-only in this track — no write_qoi() available.")
    print("\nCONSUMER_PROOF: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
