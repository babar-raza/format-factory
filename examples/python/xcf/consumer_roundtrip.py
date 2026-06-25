"""XCF consumer roundtrip — TC-D-010 (ALLFORMAT-DEEPENING-20260625).

parse → inspect layer names (real names) → analytics → verify.
XCF is read-only (no write_xcf). Consumer proof covers inspection + analytics.

Usage:
    python examples/python/xcf/consumer_roundtrip.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]

try:
    import xcf
except ImportError:
    sys.path.insert(0, str(_REPO / "src" / "python"))
    import xcf  # type: ignore

SAMPLE = _REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-red-rgb.xcf"


def main() -> int:
    print("=== XCF Consumer Roundtrip Proof ===")

    # Step 1: Parse
    model = xcf.parse_xcf(str(SAMPLE))
    assert model.get("ok"), f"XCF parse failed: {model}"
    print(f"[PARSE] {SAMPLE.name}: {model['width']}x{model['height']}, version={model['version']!r}")
    print(f"  image_type={model['image_type_name']!r}, num_layers={model['num_layers']}")

    # Step 2: Real layer names (fixed in 2026-06-25 sprint)
    layer_names = xcf.xcf_layer_name_list(str(SAMPLE))
    assert isinstance(layer_names, list)
    print(f"[LAYERS] {len(layer_names)} layer(s): {layer_names}")

    # Step 3: Analytics
    layer_count = xcf.xcf_layer_count(str(SAMPLE))
    assert layer_count == model["num_layers"]
    print(f"[ANALYTICS] layer_count={layer_count}")

    print("\nNOTE: XCF is read-only in this track — no write_xcf() available.")
    print("\nCONSUMER_PROOF: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
