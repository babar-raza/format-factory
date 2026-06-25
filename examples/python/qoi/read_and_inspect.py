"""
QOI (Quite OK Image Format) dogfood example.

Demonstrates: parse_qoi, probe_qoi, qoi analytics, QoiImage domain model.

CONSUMER_PROOF: PASS
"""
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SAMPLE = REPO / "samples" / "by-format" / "qoi" / "valid" / "4x1-gradient.qoi"


def main():
    import qoi

    # 1. Parse the file
    model = qoi.parse_qoi(str(SAMPLE))
    assert model["ok"], "QOI parse failed"
    print(f"Parsed: {SAMPLE.name}")
    print(f"  Dimensions : {model['width']}x{model['height']} px")
    print(f"  Channels   : {model['channels']}")
    print(f"  Pixel count: {model['pixel_count']}")

    # 2. Probe (lightweight header read)
    probe = qoi.probe_qoi(str(SAMPLE))
    assert probe.get("valid_header"), "QOI probe failed"
    print(f"  Probe OK   : colorspace={probe.get('colorspace')}, size={probe.get('file_size')} bytes")

    # 3. Analytics
    area = qoi.qoi_area(str(SAMPLE))
    aspect = qoi.qoi_aspect_ratio(str(SAMPLE))
    print(f"  Area       : {area} px²")
    print(f"  Aspect     : {aspect:.2f}")

    print("CONSUMER_PROOF: PASS")


if __name__ == "__main__":
    main()
