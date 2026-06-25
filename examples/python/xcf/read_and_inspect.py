"""
XCF (GIMP image format) dogfood example.

Demonstrates: parse_xcf, xcf_layer_name_list, xcf analytics.

CONSUMER_PROOF: PASS
"""
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SAMPLE = REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-red-rgb.xcf"


def main():
    import xcf

    # 1. Parse the file
    model = xcf.parse_xcf(str(SAMPLE))
    assert model["ok"], "XCF parse failed"
    print(f"Parsed: {SAMPLE.name}")
    print(f"  Dimensions : {model['width']}x{model['height']} px")
    print(f"  Image type : {model['image_type_name']}")
    print(f"  XCF version: {model['version']}")
    print(f"  Num layers : {model['num_layers']}")

    # 2. Layer names (real names from XCF binary)
    layer_names = xcf.xcf_layer_name_list(str(SAMPLE))
    print(f"  Layer names: {layer_names}")

    # 3. Analytics
    layer_count = xcf.xcf_layer_count(str(SAMPLE))
    print(f"  Layer count: {layer_count}")

    print("CONSUMER_PROOF: PASS")


if __name__ == "__main__":
    main()
