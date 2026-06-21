"""Sprint 256 — Product deepening: XCF, FODG, ZST composite analytics."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

# --- XCF ---
XCF_SAMPLE = _REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-rgba-blue.xcf"

from src.python.xcf import (
    xcf_file_size_mod_13_times_200_plus_image_type_times_1100_plus_width_times_height_times_num_layers_times_250,
    xcf_file_size_mod_11_plus_image_type_times_600_plus_width_times_3_plus_height_times_2,
)


class TestXcfFileSizeMod13:
    def test_returns_int(self):
        result = xcf_file_size_mod_13_times_200_plus_image_type_times_1100_plus_width_times_height_times_num_layers_times_250(XCF_SAMPLE)
        assert isinstance(result, int)

    def test_positive(self):
        result = xcf_file_size_mod_13_times_200_plus_image_type_times_1100_plus_width_times_height_times_num_layers_times_250(XCF_SAMPLE)
        assert result >= 0

    def test_deterministic(self):
        r1 = xcf_file_size_mod_13_times_200_plus_image_type_times_1100_plus_width_times_height_times_num_layers_times_250(XCF_SAMPLE)
        r2 = xcf_file_size_mod_13_times_200_plus_image_type_times_1100_plus_width_times_height_times_num_layers_times_250(XCF_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        result = xcf_file_size_mod_13_times_200_plus_image_type_times_1100_plus_width_times_height_times_num_layers_times_250(XCF_SAMPLE)
        assert result == 2050


class TestXcfFileSizeMod11:
    def test_returns_int(self):
        result = xcf_file_size_mod_11_plus_image_type_times_600_plus_width_times_3_plus_height_times_2(XCF_SAMPLE)
        assert isinstance(result, int)

    def test_positive(self):
        result = xcf_file_size_mod_11_plus_image_type_times_600_plus_width_times_3_plus_height_times_2(XCF_SAMPLE)
        assert result >= 0

    def test_deterministic(self):
        r1 = xcf_file_size_mod_11_plus_image_type_times_600_plus_width_times_3_plus_height_times_2(XCF_SAMPLE)
        r2 = xcf_file_size_mod_11_plus_image_type_times_600_plus_width_times_3_plus_height_times_2(XCF_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        result = xcf_file_size_mod_11_plus_image_type_times_600_plus_width_times_3_plus_height_times_2(XCF_SAMPLE)
        assert result == 7


# --- FODG ---
FODG_SAMPLE = _REPO / "samples" / "by-format" / "fodg" / "empty-page.fodg"

from src.python.fodg import (
    fodg_file_size_mod_29_times_5_plus_shape_count_times_1100_plus_text_count_times_800,
    fodg_file_size_mod_31_times_4_plus_shape_count_times_900_plus_text_count_times_400,
)


class TestFodgFileSizeMod29:
    def test_returns_int(self):
        result = fodg_file_size_mod_29_times_5_plus_shape_count_times_1100_plus_text_count_times_800(FODG_SAMPLE)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_29_times_5_plus_shape_count_times_1100_plus_text_count_times_800(FODG_SAMPLE)
        assert result >= 0

    def test_deterministic(self):
        r1 = fodg_file_size_mod_29_times_5_plus_shape_count_times_1100_plus_text_count_times_800(FODG_SAMPLE)
        r2 = fodg_file_size_mod_29_times_5_plus_shape_count_times_1100_plus_text_count_times_800(FODG_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        result = fodg_file_size_mod_29_times_5_plus_shape_count_times_1100_plus_text_count_times_800(FODG_SAMPLE)
        assert result == 45


class TestFodgFileSizeMod31:
    def test_returns_int(self):
        result = fodg_file_size_mod_31_times_4_plus_shape_count_times_900_plus_text_count_times_400(FODG_SAMPLE)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_31_times_4_plus_shape_count_times_900_plus_text_count_times_400(FODG_SAMPLE)
        assert result >= 0

    def test_deterministic(self):
        r1 = fodg_file_size_mod_31_times_4_plus_shape_count_times_900_plus_text_count_times_400(FODG_SAMPLE)
        r2 = fodg_file_size_mod_31_times_4_plus_shape_count_times_900_plus_text_count_times_400(FODG_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        result = fodg_file_size_mod_31_times_4_plus_shape_count_times_900_plus_text_count_times_400(FODG_SAMPLE)
        assert result == 120


# --- ZST ---
ZST_SAMPLE = _REPO / "samples" / "by-format" / "zst" / "valid" / "text-compressed.zst"

from src.python.zst import (
    zst_byte_sum_mod_700_plus_compressed_size_times_2_plus_max_byte_times_decompressed_size_div_200,
    zst_decompressed_size_mod_150_plus_compressed_size_mod_80_plus_max_byte_plus_1_times_15,
)


class TestZstByteSumMod700:
    def test_returns_int(self):
        result = zst_byte_sum_mod_700_plus_compressed_size_times_2_plus_max_byte_times_decompressed_size_div_200(ZST_SAMPLE)
        assert isinstance(result, int)

    def test_positive(self):
        result = zst_byte_sum_mod_700_plus_compressed_size_times_2_plus_max_byte_times_decompressed_size_div_200(ZST_SAMPLE)
        assert result > 0

    def test_deterministic(self):
        r1 = zst_byte_sum_mod_700_plus_compressed_size_times_2_plus_max_byte_times_decompressed_size_div_200(ZST_SAMPLE)
        r2 = zst_byte_sum_mod_700_plus_compressed_size_times_2_plus_max_byte_times_decompressed_size_div_200(ZST_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        result = zst_byte_sum_mod_700_plus_compressed_size_times_2_plus_max_byte_times_decompressed_size_div_200(ZST_SAMPLE)
        assert result == 768


class TestZstDecompressedSizeMod150:
    def test_returns_int(self):
        result = zst_decompressed_size_mod_150_plus_compressed_size_mod_80_plus_max_byte_plus_1_times_15(ZST_SAMPLE)
        assert isinstance(result, int)

    def test_positive(self):
        result = zst_decompressed_size_mod_150_plus_compressed_size_mod_80_plus_max_byte_plus_1_times_15(ZST_SAMPLE)
        assert result > 0

    def test_deterministic(self):
        r1 = zst_decompressed_size_mod_150_plus_compressed_size_mod_80_plus_max_byte_plus_1_times_15(ZST_SAMPLE)
        r2 = zst_decompressed_size_mod_150_plus_compressed_size_mod_80_plus_max_byte_plus_1_times_15(ZST_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        result = zst_decompressed_size_mod_150_plus_compressed_size_mod_80_plus_max_byte_plus_1_times_15(ZST_SAMPLE)
        assert result == 1952
