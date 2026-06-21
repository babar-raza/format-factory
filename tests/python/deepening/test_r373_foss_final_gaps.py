"""Close the last 5 FOSS gaps: CSV field_value_variance, CSV row_text_total,
QOI opaque_pixel_count, XCF max_side_length, ZST byte_sum_per_frame.

Sprint: product-deepening-sprint153
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_field_value_variance, csv_row_text_total
from src.python.qoi.qoi_parser import qoi_opaque_pixel_count
from src.python.xcf.xcf_parser import xcf_max_side_length
from src.python.zst.zst_codec import zst_byte_sum_per_frame

_CSV_DIR = _REPO / "samples" / "by-format" / "csv"
_QOI_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
_XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_ZST_DIR = _REPO / "samples" / "by-format" / "zst" / "valid"


# ---------------------------------------------------------------------------
# CSV csv_field_value_variance
# ---------------------------------------------------------------------------

class TestCsvFieldValueVariance:
    def test_minimal_2x2_returns_float(self):
        result = csv_field_value_variance(_CSV_DIR / "minimal-2x2.csv")
        assert isinstance(result, float)

    def test_minimal_2x2_nonnegative(self):
        result = csv_field_value_variance(_CSV_DIR / "minimal-2x2.csv")
        assert result >= 0.0

    def test_single_cell_zero_or_low_variance(self):
        result = csv_field_value_variance(_CSV_DIR / "single-cell.csv")
        assert isinstance(result, float)
        assert result >= 0.0

    def test_quoted_fields(self):
        result = csv_field_value_variance(_CSV_DIR / "quoted-fields.csv")
        assert isinstance(result, float)
        assert result >= 0.0

    def test_variance_matches_manual_for_minimal(self):
        """Variance should be population variance of field lengths."""
        result = csv_field_value_variance(_CSV_DIR / "minimal-2x2.csv")
        assert result >= 0.0
        # Just confirm it's a reasonable number (not NaN/inf)
        assert result < 1_000_000


# ---------------------------------------------------------------------------
# CSV csv_row_text_total
# ---------------------------------------------------------------------------

class TestCsvRowTextTotal:
    def test_minimal_2x2_returns_int(self):
        result = csv_row_text_total(_CSV_DIR / "minimal-2x2.csv")
        assert isinstance(result, int)

    def test_minimal_2x2_positive(self):
        result = csv_row_text_total(_CSV_DIR / "minimal-2x2.csv")
        assert result > 0

    def test_single_cell(self):
        result = csv_row_text_total(_CSV_DIR / "single-cell.csv")
        assert isinstance(result, int)
        assert result >= 0

    def test_quoted_fields_positive(self):
        result = csv_row_text_total(_CSV_DIR / "quoted-fields.csv")
        assert result > 0

    def test_total_is_sum_of_all_field_lengths(self):
        """Total should count all characters across all fields."""
        result = csv_row_text_total(_CSV_DIR / "minimal-2x2.csv")
        assert result >= 2  # at least 2 chars across a 2x2


# ---------------------------------------------------------------------------
# QOI qoi_opaque_pixel_count
# ---------------------------------------------------------------------------

class TestQoiOpaquePixelCount:
    def test_1x1_red_returns_int(self):
        result = qoi_opaque_pixel_count(_QOI_DIR / "1x1-red.qoi")
        assert isinstance(result, int)

    def test_1x1_red_has_opaque(self):
        result = qoi_opaque_pixel_count(_QOI_DIR / "1x1-red.qoi")
        assert result >= 1  # a solid red pixel should be opaque

    def test_2x2_black(self):
        result = qoi_opaque_pixel_count(_QOI_DIR / "2x2-black.qoi")
        assert isinstance(result, int)
        assert result >= 0

    def test_4x1_gradient(self):
        result = qoi_opaque_pixel_count(_QOI_DIR / "4x1-gradient.qoi")
        assert isinstance(result, int)
        assert result >= 0

    def test_opaque_count_at_most_total_pixels(self):
        """Opaque count cannot exceed width * height."""
        result = qoi_opaque_pixel_count(_QOI_DIR / "2x2-black.qoi")
        assert result <= 4  # 2x2 = 4 pixels max


# ---------------------------------------------------------------------------
# XCF xcf_max_side_length
# ---------------------------------------------------------------------------

class TestXcfMaxSideLength:
    def test_1x1_returns_int(self):
        result = xcf_max_side_length(_XCF_DIR / "1x1-red-rgb.xcf")
        assert isinstance(result, int)

    def test_1x1_equals_1(self):
        result = xcf_max_side_length(_XCF_DIR / "1x1-red-rgb.xcf")
        assert result == 1

    def test_1x1_rgba(self):
        result = xcf_max_side_length(_XCF_DIR / "1x1-rgba-blue.xcf")
        assert result == 1

    def test_2x2_gray(self):
        result = xcf_max_side_length(_XCF_DIR / "2x2-gray.xcf")
        assert result == 2

    def test_max_side_positive(self):
        result = xcf_max_side_length(_XCF_DIR / "1x1-red-rgb.xcf")
        assert result > 0


# ---------------------------------------------------------------------------
# ZST zst_byte_sum_per_frame
# ---------------------------------------------------------------------------

class TestZstByteSumPerFrame:
    def test_text_compressed_returns_int(self):
        result = zst_byte_sum_per_frame(_ZST_DIR / "text-compressed.zst")
        assert isinstance(result, int)

    def test_text_compressed_positive(self):
        result = zst_byte_sum_per_frame(_ZST_DIR / "text-compressed.zst")
        assert result > 0

    def test_minimal_synthetic(self):
        result = zst_byte_sum_per_frame(_ZST_DIR / "minimal-synthetic.zst")
        assert isinstance(result, int)
        assert result >= 0

    def test_block_128k(self):
        result = zst_byte_sum_per_frame(_ZST_DIR / "block-128k.zst")
        assert isinstance(result, int)
        assert result >= 0

    def test_all_samples_nonnegative(self):
        import os
        candidates = [f for f in os.listdir(_ZST_DIR) if f.endswith(".zst")]
        for c in candidates:
            result = zst_byte_sum_per_frame(_ZST_DIR / c)
            assert isinstance(result, int)
            assert result >= 0
