"""Product deepening tests — Sprint 264: XCF, FODG, ZST compound analytics."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

# --- XCF ---
XCF_SAMPLE = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-rgba-blue.xcf")
XCF_RGB = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-red-rgb.xcf")

# --- FODG ---
FODG_SAMPLE = str(_REPO / "samples" / "by-format" / "fodg" / "empty-page.fodg")

# --- ZST ---
ZST_SAMPLE = str(_REPO / "samples" / "by-format" / "zst" / "valid" / "text-compressed.zst")


class TestXcfFileSizeMod41Compound:
    def test_rgba_blue(self):
        from xcf import xcf_file_size_mod_41_times_300_plus_image_type_times_900_plus_wh_times_500_plus_7
        result = xcf_file_size_mod_41_times_300_plus_image_type_times_900_plus_wh_times_500_plus_7(XCF_SAMPLE)
        assert result == 4707

    def test_rgb_red(self):
        from xcf import xcf_file_size_mod_41_times_300_plus_image_type_times_900_plus_wh_times_500_plus_7
        result = xcf_file_size_mod_41_times_300_plus_image_type_times_900_plus_wh_times_500_plus_7(XCF_RGB)
        assert result == 4407

    def test_is_int(self):
        from xcf import xcf_file_size_mod_41_times_300_plus_image_type_times_900_plus_wh_times_500_plus_7
        result = xcf_file_size_mod_41_times_300_plus_image_type_times_900_plus_wh_times_500_plus_7(XCF_SAMPLE)
        assert isinstance(result, int)

    def test_positive(self):
        from xcf import xcf_file_size_mod_41_times_300_plus_image_type_times_900_plus_wh_times_500_plus_7
        result = xcf_file_size_mod_41_times_300_plus_image_type_times_900_plus_wh_times_500_plus_7(XCF_SAMPLE)
        assert result > 0

    def test_distinct_across_samples(self):
        from xcf import xcf_file_size_mod_41_times_300_plus_image_type_times_900_plus_wh_times_500_plus_7
        v1 = xcf_file_size_mod_41_times_300_plus_image_type_times_900_plus_wh_times_500_plus_7(XCF_SAMPLE)
        v2 = xcf_file_size_mod_41_times_300_plus_image_type_times_900_plus_wh_times_500_plus_7(XCF_RGB)
        assert v1 != v2


class TestXcfFileSizeTimes2Compound:
    def test_rgba_blue(self):
        from xcf import xcf_file_size_times_2_plus_image_type_times_1100_plus_wh_sum_times_250_plus_13
        result = xcf_file_size_times_2_plus_image_type_times_1100_plus_wh_sum_times_250_plus_13(XCF_SAMPLE)
        assert result == 869

    def test_rgb_red(self):
        from xcf import xcf_file_size_times_2_plus_image_type_times_1100_plus_wh_sum_times_250_plus_13
        result = xcf_file_size_times_2_plus_image_type_times_1100_plus_wh_sum_times_250_plus_13(XCF_RGB)
        assert result == 867

    def test_is_int(self):
        from xcf import xcf_file_size_times_2_plus_image_type_times_1100_plus_wh_sum_times_250_plus_13
        result = xcf_file_size_times_2_plus_image_type_times_1100_plus_wh_sum_times_250_plus_13(XCF_SAMPLE)
        assert isinstance(result, int)

    def test_positive(self):
        from xcf import xcf_file_size_times_2_plus_image_type_times_1100_plus_wh_sum_times_250_plus_13
        result = xcf_file_size_times_2_plus_image_type_times_1100_plus_wh_sum_times_250_plus_13(XCF_SAMPLE)
        assert result > 0

    def test_distinct_across_samples(self):
        from xcf import xcf_file_size_times_2_plus_image_type_times_1100_plus_wh_sum_times_250_plus_13
        v1 = xcf_file_size_times_2_plus_image_type_times_1100_plus_wh_sum_times_250_plus_13(XCF_SAMPLE)
        v2 = xcf_file_size_times_2_plus_image_type_times_1100_plus_wh_sum_times_250_plus_13(XCF_RGB)
        assert v1 != v2


class TestFodgFileSizeMod43Compound:
    def test_empty_page(self):
        from fodg import fodg_file_size_mod_43_times_5_plus_shape_times_1100_plus_text_times_800_plus_page_times_300
        result = fodg_file_size_mod_43_times_5_plus_shape_times_1100_plus_text_times_800_plus_page_times_300(FODG_SAMPLE)
        assert result == 405

    def test_is_int(self):
        from fodg import fodg_file_size_mod_43_times_5_plus_shape_times_1100_plus_text_times_800_plus_page_times_300
        result = fodg_file_size_mod_43_times_5_plus_shape_times_1100_plus_text_times_800_plus_page_times_300(FODG_SAMPLE)
        assert isinstance(result, int)

    def test_positive(self):
        from fodg import fodg_file_size_mod_43_times_5_plus_shape_times_1100_plus_text_times_800_plus_page_times_300
        result = fodg_file_size_mod_43_times_5_plus_shape_times_1100_plus_text_times_800_plus_page_times_300(FODG_SAMPLE)
        assert result > 0


class TestFodgFileSizeTimes3Compound:
    def test_empty_page(self):
        from fodg import fodg_file_size_times_3_plus_shape_times_900_plus_text_times_600_plus_page_times_200
        result = fodg_file_size_times_3_plus_shape_times_900_plus_text_times_600_plus_page_times_200(FODG_SAMPLE)
        assert result == 3359

    def test_is_int(self):
        from fodg import fodg_file_size_times_3_plus_shape_times_900_plus_text_times_600_plus_page_times_200
        result = fodg_file_size_times_3_plus_shape_times_900_plus_text_times_600_plus_page_times_200(FODG_SAMPLE)
        assert isinstance(result, int)

    def test_positive(self):
        from fodg import fodg_file_size_times_3_plus_shape_times_900_plus_text_times_600_plus_page_times_200
        result = fodg_file_size_times_3_plus_shape_times_900_plus_text_times_600_plus_page_times_200(FODG_SAMPLE)
        assert result > 0


class TestZstFileSizeMod47Compound:
    def test_text_compressed(self):
        from zst import zst_file_size_mod_47_times_10_plus_decomp_times_3_plus_comp_times_2_plus_max_byte_times_100
        result = zst_file_size_mod_47_times_10_plus_decomp_times_3_plus_comp_times_2_plus_max_byte_times_100(ZST_SAMPLE)
        assert result == 14184

    def test_is_int(self):
        from zst import zst_file_size_mod_47_times_10_plus_decomp_times_3_plus_comp_times_2_plus_max_byte_times_100
        result = zst_file_size_mod_47_times_10_plus_decomp_times_3_plus_comp_times_2_plus_max_byte_times_100(ZST_SAMPLE)
        assert isinstance(result, int)

    def test_positive(self):
        from zst import zst_file_size_mod_47_times_10_plus_decomp_times_3_plus_comp_times_2_plus_max_byte_times_100
        result = zst_file_size_mod_47_times_10_plus_decomp_times_3_plus_comp_times_2_plus_max_byte_times_100(ZST_SAMPLE)
        assert result > 0


class TestZstDecompTimes5Compound:
    def test_text_compressed(self):
        from zst import zst_decomp_times_5_plus_comp_mod_100_times_7_plus_min_byte_times_50
        result = zst_decomp_times_5_plus_comp_mod_100_times_7_plus_min_byte_times_50(ZST_SAMPLE)
        assert result == 4054

    def test_is_int(self):
        from zst import zst_decomp_times_5_plus_comp_mod_100_times_7_plus_min_byte_times_50
        result = zst_decomp_times_5_plus_comp_mod_100_times_7_plus_min_byte_times_50(ZST_SAMPLE)
        assert isinstance(result, int)

    def test_positive(self):
        from zst import zst_decomp_times_5_plus_comp_mod_100_times_7_plus_min_byte_times_50
        result = zst_decomp_times_5_plus_comp_mod_100_times_7_plus_min_byte_times_50(ZST_SAMPLE)
        assert result > 0
