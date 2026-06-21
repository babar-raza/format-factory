"""Sprint 257 — Product deepening: XCF, FODG, ZST composite analytics (batch 2)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

XCF_SAMPLE = _REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-rgba-blue.xcf"
FODG_SAMPLE = _REPO / "samples" / "by-format" / "fodg" / "empty-page.fodg"
ZST_SAMPLE = _REPO / "samples" / "by-format" / "zst" / "valid" / "text-compressed.zst"

from src.python.xcf import (
    xcf_width_times_height_plus_file_size_mod_17_times_100_plus_num_layers_times_300,
    xcf_image_type_times_700_plus_width_squared_plus_height_squared,
)
from src.python.fodg import (
    fodg_page_count_times_shape_count_times_1000_plus_text_count_times_500_plus_file_size_mod_37,
    fodg_shape_count_squared_plus_text_count_squared_plus_page_count_times_100,
)
from src.python.zst import (
    zst_compressed_size_squared_plus_decompressed_size_mod_300_plus_max_byte_value_times_10,
    zst_frame_count_times_1000_plus_compressed_size_mod_500_plus_decompressed_size_div_100,
)


class TestXcfWidthTimesHeight:
    def test_returns_int(self):
        assert isinstance(xcf_width_times_height_plus_file_size_mod_17_times_100_plus_num_layers_times_300(XCF_SAMPLE), int)

    def test_positive(self):
        assert xcf_width_times_height_plus_file_size_mod_17_times_100_plus_num_layers_times_300(XCF_SAMPLE) > 0

    def test_deterministic(self):
        r1 = xcf_width_times_height_plus_file_size_mod_17_times_100_plus_num_layers_times_300(XCF_SAMPLE)
        r2 = xcf_width_times_height_plus_file_size_mod_17_times_100_plus_num_layers_times_300(XCF_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert xcf_width_times_height_plus_file_size_mod_17_times_100_plus_num_layers_times_300(XCF_SAMPLE) == 1101


class TestXcfImageTypeTimes700:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_times_700_plus_width_squared_plus_height_squared(XCF_SAMPLE), int)

    def test_non_negative(self):
        assert xcf_image_type_times_700_plus_width_squared_plus_height_squared(XCF_SAMPLE) >= 0

    def test_deterministic(self):
        r1 = xcf_image_type_times_700_plus_width_squared_plus_height_squared(XCF_SAMPLE)
        r2 = xcf_image_type_times_700_plus_width_squared_plus_height_squared(XCF_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert xcf_image_type_times_700_plus_width_squared_plus_height_squared(XCF_SAMPLE) == 2


class TestFodgPageCountTimesShapeCount:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_shape_count_times_1000_plus_text_count_times_500_plus_file_size_mod_37(FODG_SAMPLE), int)

    def test_non_negative(self):
        assert fodg_page_count_times_shape_count_times_1000_plus_text_count_times_500_plus_file_size_mod_37(FODG_SAMPLE) >= 0

    def test_deterministic(self):
        r1 = fodg_page_count_times_shape_count_times_1000_plus_text_count_times_500_plus_file_size_mod_37(FODG_SAMPLE)
        r2 = fodg_page_count_times_shape_count_times_1000_plus_text_count_times_500_plus_file_size_mod_37(FODG_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert fodg_page_count_times_shape_count_times_1000_plus_text_count_times_500_plus_file_size_mod_37(FODG_SAMPLE) == 17


class TestFodgShapeCountSquared:
    def test_returns_int(self):
        assert isinstance(fodg_shape_count_squared_plus_text_count_squared_plus_page_count_times_100(FODG_SAMPLE), int)

    def test_non_negative(self):
        assert fodg_shape_count_squared_plus_text_count_squared_plus_page_count_times_100(FODG_SAMPLE) >= 0

    def test_deterministic(self):
        r1 = fodg_shape_count_squared_plus_text_count_squared_plus_page_count_times_100(FODG_SAMPLE)
        r2 = fodg_shape_count_squared_plus_text_count_squared_plus_page_count_times_100(FODG_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert fodg_shape_count_squared_plus_text_count_squared_plus_page_count_times_100(FODG_SAMPLE) == 100


class TestZstCompressedSizeSquared:
    def test_returns_int(self):
        assert isinstance(zst_compressed_size_squared_plus_decompressed_size_mod_300_plus_max_byte_value_times_10(ZST_SAMPLE), int)

    def test_positive(self):
        assert zst_compressed_size_squared_plus_decompressed_size_mod_300_plus_max_byte_value_times_10(ZST_SAMPLE) > 0

    def test_deterministic(self):
        r1 = zst_compressed_size_squared_plus_decompressed_size_mod_300_plus_max_byte_value_times_10(ZST_SAMPLE)
        r2 = zst_compressed_size_squared_plus_decompressed_size_mod_300_plus_max_byte_value_times_10(ZST_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert zst_compressed_size_squared_plus_decompressed_size_mod_300_plus_max_byte_value_times_10(ZST_SAMPLE) == 75284


class TestZstFrameCountTimes1000:
    def test_returns_int(self):
        assert isinstance(zst_frame_count_times_1000_plus_compressed_size_mod_500_plus_decompressed_size_div_100(ZST_SAMPLE), int)

    def test_positive(self):
        assert zst_frame_count_times_1000_plus_compressed_size_mod_500_plus_decompressed_size_div_100(ZST_SAMPLE) > 0

    def test_deterministic(self):
        r1 = zst_frame_count_times_1000_plus_compressed_size_mod_500_plus_decompressed_size_div_100(ZST_SAMPLE)
        r2 = zst_frame_count_times_1000_plus_compressed_size_mod_500_plus_decompressed_size_div_100(ZST_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert zst_frame_count_times_1000_plus_compressed_size_mod_500_plus_decompressed_size_div_100(ZST_SAMPLE) == 1275
