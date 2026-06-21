"""Sprint 133 — XCF bytes_per_pixel_area/layer_count_plus_image_type, ZST compression_ratio_percent/size_ratio."""
import sys, pathlib, pytest
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.xcf.xcf_parser import xcf_bytes_per_pixel_area, xcf_layer_count_plus_image_type
from src.python.zst.zst_codec import zst_compression_ratio_percent, zst_size_ratio

XR = str(_REPO / "samples/by-format/xcf/valid/1x1-red-rgb.xcf")
XB = str(_REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf")
XG = str(_REPO / "samples/by-format/xcf/valid/2x2-gray.xcf")
ZB = str(_REPO / "samples/by-format/zst/valid/block-128k.zst")
ZD = str(_REPO / "samples/by-format/zst/valid/dict-compressed.zst")
ZE = str(_REPO / "samples/by-format/zst/valid/empty-block.zst")

class TestXcfBytesPerPixelArea:
    def test_red_rgb(self):
        assert xcf_bytes_per_pixel_area(XR) == 177.0
    def test_rgba_blue(self):
        assert xcf_bytes_per_pixel_area(XB) == 178.0
    def test_gray(self):
        assert xcf_bytes_per_pixel_area(XG) == 44.5
    def test_return_type(self):
        assert isinstance(xcf_bytes_per_pixel_area(XR), float)
    def test_positive(self):
        assert xcf_bytes_per_pixel_area(XR) > 0

class TestXcfLayerCountPlusImageType:
    def test_red_rgb(self):
        assert xcf_layer_count_plus_image_type(XR) == 1
    def test_rgba_blue(self):
        assert xcf_layer_count_plus_image_type(XB) == 1
    def test_gray(self):
        assert xcf_layer_count_plus_image_type(XG) == 2
    def test_return_type(self):
        assert isinstance(xcf_layer_count_plus_image_type(XR), int)
    def test_non_negative(self):
        assert xcf_layer_count_plus_image_type(XR) >= 0

class TestZstCompressionRatioPercent:
    def test_block(self):
        assert abs(zst_compression_ratio_percent(ZB) - 100.0099) < 0.01
    def test_dict(self):
        assert abs(zst_compression_ratio_percent(ZD) - 1.7788) < 0.01
    def test_empty(self):
        assert zst_compression_ratio_percent(ZE) == 0.0
    def test_return_type(self):
        assert isinstance(zst_compression_ratio_percent(ZB), float)
    def test_non_negative(self):
        assert zst_compression_ratio_percent(ZB) >= 0.0

class TestZstSizeRatio:
    def test_block(self):
        assert abs(zst_size_ratio(ZB) - 0.9999) < 0.001
    def test_dict(self):
        assert abs(zst_size_ratio(ZD) - 56.2162) < 0.01
    def test_empty(self):
        assert zst_size_ratio(ZE) == 0.0
    def test_return_type(self):
        assert isinstance(zst_size_ratio(ZB), float)
    def test_non_negative(self):
        assert zst_size_ratio(ZB) >= 0.0
