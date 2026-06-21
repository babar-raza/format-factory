"""Sprint R448 — XCF/ZST/TOML/FODG/Gnumeric round 8 deepening tests."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import xcf_file_size_bytes_squared, xcf_total_pixel_count_times_two, xcf_file_size_bytes, xcf_total_pixel_count
from src.python.zst import zst_max_byte_value_squared, zst_avg_byte_value_int_squared, zst_max_byte_value, zst_avg_byte_value_int
from src.python.toml import toml_file_size_times_two, toml_depth_times_two, toml_file_size_bytes, toml_depth
from src.python.fodg import fodg_max_shapes_per_page_squared, fodg_non_text_shape_count_squared, fodg_max_shapes_per_page, fodg_non_text_shape_count
from src.python.gnumeric import gnumeric_file_size_squared, gnumeric_total_row_count_squared, gnumeric_file_size_bytes, gnumeric_total_row_count

SAMPLES = _REPO / "samples" / "by-format"
XCF_SAMPLE = SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf"
ZST_SAMPLE = SAMPLES / "zst" / "valid" / "text-compressed.zst"
TOML_SAMPLE = SAMPLES / "toml" / "minimal.toml"
FODG_SAMPLE = SAMPLES / "fodg" / "minimal-drawing.fodg"
GNUMERIC_SAMPLE = SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric"


# --- XCF: xcf_file_size_bytes_squared ---
class TestXcfFileSizeBytesSquared:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_squared(XCF_SAMPLE), int)

    def test_is_square(self):
        fs = xcf_file_size_bytes(XCF_SAMPLE)
        assert xcf_file_size_bytes_squared(XCF_SAMPLE) == fs * fs

    def test_positive(self):
        assert xcf_file_size_bytes_squared(XCF_SAMPLE) > 0


# --- XCF: xcf_total_pixel_count_times_two ---
class TestXcfTotalPixelCountTimesTwo:
    def test_returns_int(self):
        assert isinstance(xcf_total_pixel_count_times_two(XCF_SAMPLE), int)

    def test_is_double(self):
        assert xcf_total_pixel_count_times_two(XCF_SAMPLE) == xcf_total_pixel_count(XCF_SAMPLE) * 2

    def test_positive(self):
        assert xcf_total_pixel_count_times_two(XCF_SAMPLE) > 0


# --- ZST: zst_max_byte_value_squared ---
class TestZstMaxByteValueSquared:
    def test_returns_int(self):
        assert isinstance(zst_max_byte_value_squared(ZST_SAMPLE), int)

    def test_is_square(self):
        mb = zst_max_byte_value(ZST_SAMPLE)
        assert zst_max_byte_value_squared(ZST_SAMPLE) == mb * mb

    def test_non_negative(self):
        assert zst_max_byte_value_squared(ZST_SAMPLE) >= 0


# --- ZST: zst_avg_byte_value_int_squared ---
class TestZstAvgByteValueIntSquared:
    def test_returns_int(self):
        assert isinstance(zst_avg_byte_value_int_squared(ZST_SAMPLE), int)

    def test_is_square(self):
        av = zst_avg_byte_value_int(ZST_SAMPLE)
        assert zst_avg_byte_value_int_squared(ZST_SAMPLE) == av * av

    def test_non_negative(self):
        assert zst_avg_byte_value_int_squared(ZST_SAMPLE) >= 0


# --- TOML: toml_file_size_times_two ---
class TestTomlFileSizeTimesTwo:
    def test_returns_int(self):
        assert isinstance(toml_file_size_times_two(TOML_SAMPLE), int)

    def test_is_double(self):
        assert toml_file_size_times_two(TOML_SAMPLE) == toml_file_size_bytes(TOML_SAMPLE) * 2

    def test_positive(self):
        assert toml_file_size_times_two(TOML_SAMPLE) > 0


# --- TOML: toml_depth_times_two ---
class TestTomlDepthTimesTwo:
    def test_returns_int(self):
        assert isinstance(toml_depth_times_two(TOML_SAMPLE), int)

    def test_is_double(self):
        assert toml_depth_times_two(TOML_SAMPLE) == toml_depth(TOML_SAMPLE) * 2

    def test_non_negative(self):
        assert toml_depth_times_two(TOML_SAMPLE) >= 0


# --- FODG: fodg_max_shapes_per_page_squared ---
class TestFodgMaxShapesPerPageSquared:
    def test_returns_int(self):
        assert isinstance(fodg_max_shapes_per_page_squared(FODG_SAMPLE), int)

    def test_is_square(self):
        ms = fodg_max_shapes_per_page(FODG_SAMPLE)
        assert fodg_max_shapes_per_page_squared(FODG_SAMPLE) == ms * ms

    def test_non_negative(self):
        assert fodg_max_shapes_per_page_squared(FODG_SAMPLE) >= 0


# --- FODG: fodg_non_text_shape_count_squared ---
class TestFodgNonTextShapeCountSquared:
    def test_returns_int(self):
        assert isinstance(fodg_non_text_shape_count_squared(FODG_SAMPLE), int)

    def test_is_square(self):
        nt = fodg_non_text_shape_count(FODG_SAMPLE)
        assert fodg_non_text_shape_count_squared(FODG_SAMPLE) == nt * nt

    def test_non_negative(self):
        assert fodg_non_text_shape_count_squared(FODG_SAMPLE) >= 0


# --- Gnumeric: gnumeric_file_size_squared ---
class TestGnumericFileSizeSquared:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_squared(GNUMERIC_SAMPLE), int)

    def test_is_square(self):
        fs = gnumeric_file_size_bytes(GNUMERIC_SAMPLE)
        assert gnumeric_file_size_squared(GNUMERIC_SAMPLE) == fs * fs

    def test_positive(self):
        assert gnumeric_file_size_squared(GNUMERIC_SAMPLE) > 0


# --- Gnumeric: gnumeric_total_row_count_squared ---
class TestGnumericTotalRowCountSquared:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_squared(GNUMERIC_SAMPLE), int)

    def test_is_square(self):
        rc = gnumeric_total_row_count(GNUMERIC_SAMPLE)
        assert gnumeric_total_row_count_squared(GNUMERIC_SAMPLE) == rc * rc

    def test_non_negative(self):
        assert gnumeric_total_row_count_squared(GNUMERIC_SAMPLE) >= 0
