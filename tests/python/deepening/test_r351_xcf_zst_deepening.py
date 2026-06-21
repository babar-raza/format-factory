"""Sprint 141 deepening tests: XCF area_plus_file_size/layers_times_width, ZST byte_range/is_single_byte."""
import sys, pathlib, pytest
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf.xcf_parser import xcf_area_plus_file_size, xcf_layers_times_width
from src.python.zst.zst_codec import zst_byte_range, zst_is_single_byte

X1 = str(_REPO / "samples/by-format/xcf/valid/1x1-red-rgb.xcf")
X2 = str(_REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf")
X3 = str(_REPO / "samples/by-format/xcf/valid/2x2-gray.xcf")
Z1 = str(_REPO / "samples/by-format/zst/valid/block-128k.zst")
Z2 = str(_REPO / "samples/by-format/zst/valid/dict-compressed.zst")
Z3 = str(_REPO / "samples/by-format/zst/valid/empty-block.zst")


class TestXcfAreaPlusFileSize:
    def test_red_rgb(self):
        assert xcf_area_plus_file_size(X1) == 178

    def test_rgba_blue(self):
        assert xcf_area_plus_file_size(X2) == 179

    def test_gray(self):
        assert xcf_area_plus_file_size(X3) == 182

    def test_return_type(self):
        assert isinstance(xcf_area_plus_file_size(X1), int)

    def test_positive(self):
        assert xcf_area_plus_file_size(X1) > 0


class TestXcfLayersTimesWidth:
    def test_red_rgb(self):
        assert xcf_layers_times_width(X1) == 1

    def test_rgba_blue(self):
        assert xcf_layers_times_width(X2) == 1

    def test_gray_2x2(self):
        assert xcf_layers_times_width(X3) == 2

    def test_return_type(self):
        assert isinstance(xcf_layers_times_width(X1), int)

    def test_positive(self):
        assert xcf_layers_times_width(X3) > 0


class TestZstByteRange:
    def test_uniform_block(self):
        assert zst_byte_range(Z1) == 0

    def test_dict_compressed(self):
        assert zst_byte_range(Z2) == 112

    def test_empty(self):
        assert zst_byte_range(Z3) == 0

    def test_return_type(self):
        assert isinstance(zst_byte_range(Z1), int)

    def test_nonnegative(self):
        assert zst_byte_range(Z2) >= 0


class TestZstIsSingleByte:
    def test_uniform_block(self):
        assert zst_is_single_byte(Z1) is True

    def test_dict_compressed(self):
        assert zst_is_single_byte(Z2) is False

    def test_empty(self):
        assert zst_is_single_byte(Z3) is False

    def test_return_type(self):
        assert isinstance(zst_is_single_byte(Z1), bool)

    def test_nonempty_uniform(self):
        assert zst_is_single_byte(Z1) is True
