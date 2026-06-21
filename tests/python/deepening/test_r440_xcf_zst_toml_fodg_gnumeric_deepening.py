"""Sprint R440 — XCF/ZST/TOML/FODG/Gnumeric deepening round 6.

Functions under test (10 total, 2 per format):
  XCF:      xcf_width_times_two, xcf_height_times_two
  ZST:      zst_decompressed_size_times_two, zst_min_byte_value_times_two
  TOML:     toml_depth_squared, toml_table_count_squared
  FODG:     fodg_shape_plus_page_squared, fodg_text_count_times_page_count_squared
  Gnumeric: gnumeric_sheet_count_times_two, gnumeric_total_row_count_times_two
"""
import pathlib, sys, pytest

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

# --- sample paths ---
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-rgba-blue.xcf"
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid" / "text-compressed.zst"
_TOML = _REPO / "samples" / "by-format" / "toml" / "minimal.toml"
_FODG = _REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg"
_GNUMERIC = _REPO / "samples" / "by-format" / "gnumeric" / "minimal-spreadsheet.gnumeric"

# ── XCF ──────────────────────────────────────────────────────────────
from src.python.xcf.xcf_parser import (
    xcf_width,
    xcf_height,
    xcf_width_times_two,
    xcf_height_times_two,
)

class TestXcfWidthTimesTwo:
    def test_returns_int(self):
        assert isinstance(xcf_width_times_two(_XCF), int)
    def test_double_of_base(self):
        assert xcf_width_times_two(_XCF) == xcf_width(_XCF) * 2
    def test_positive(self):
        assert xcf_width_times_two(_XCF) > 0

class TestXcfHeightTimesTwo:
    def test_returns_int(self):
        assert isinstance(xcf_height_times_two(_XCF), int)
    def test_double_of_base(self):
        assert xcf_height_times_two(_XCF) == xcf_height(_XCF) * 2
    def test_positive(self):
        assert xcf_height_times_two(_XCF) > 0

# ── ZST ──────────────────────────────────────────────────────────────
from src.python.zst.zst_codec import (
    zst_decompressed_size,
    zst_min_byte_value,
    zst_decompressed_size_times_two,
    zst_min_byte_value_times_two,
)

class TestZstDecompressedSizeTimesTwo:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_two(_ZST), int)
    def test_double_of_base(self):
        assert zst_decompressed_size_times_two(_ZST) == zst_decompressed_size(_ZST) * 2
    def test_non_negative(self):
        assert zst_decompressed_size_times_two(_ZST) >= 0

class TestZstMinByteValueTimesTwo:
    def test_returns_int(self):
        assert isinstance(zst_min_byte_value_times_two(_ZST), int)
    def test_double_of_base(self):
        assert zst_min_byte_value_times_two(_ZST) == zst_min_byte_value(_ZST) * 2
    def test_non_negative(self):
        assert zst_min_byte_value_times_two(_ZST) >= 0

# ── TOML ─────────────────────────────────────────────────────────────
from src.python.toml.toml_codec import (
    toml_depth,
    toml_table_count,
    toml_depth_squared,
    toml_table_count_squared,
)

class TestTomlDepthSquared:
    def test_returns_int(self):
        assert isinstance(toml_depth_squared(_TOML), int)
    def test_square_of_base(self):
        d = toml_depth(_TOML)
        assert toml_depth_squared(_TOML) == d * d
    def test_non_negative(self):
        assert toml_depth_squared(_TOML) >= 0

class TestTomlTableCountSquared:
    def test_returns_int(self):
        assert isinstance(toml_table_count_squared(_TOML), int)
    def test_square_of_base(self):
        tc = toml_table_count(_TOML)
        assert toml_table_count_squared(_TOML) == tc * tc
    def test_non_negative(self):
        assert toml_table_count_squared(_TOML) >= 0

# ── FODG ─────────────────────────────────────────────────────────────
from src.python.fodg.fodg_codec import (
    fodg_total_shape_count,
    fodg_page_count,
    fodg_text_item_count,
    fodg_shape_plus_page_squared,
    fodg_text_count_times_page_count_squared,
)

class TestFodgShapePlusPageSquared:
    def test_returns_int(self):
        assert isinstance(fodg_shape_plus_page_squared(_FODG), int)
    def test_value(self):
        s = fodg_total_shape_count(_FODG) + fodg_page_count(_FODG)
        assert fodg_shape_plus_page_squared(_FODG) == s * s
    def test_non_negative(self):
        assert fodg_shape_plus_page_squared(_FODG) >= 0

class TestFodgTextCountTimesPageCountSquared:
    def test_returns_int(self):
        assert isinstance(fodg_text_count_times_page_count_squared(_FODG), int)
    def test_value(self):
        expected = fodg_text_item_count(_FODG) * (fodg_page_count(_FODG) ** 2)
        assert fodg_text_count_times_page_count_squared(_FODG) == expected
    def test_non_negative(self):
        assert fodg_text_count_times_page_count_squared(_FODG) >= 0

# ── Gnumeric ─────────────────────────────────────────────────────────
from src.python.gnumeric.gnumeric_codec import (
    gnumeric_sheet_count,
    gnumeric_total_row_count,
    gnumeric_sheet_count_times_two,
    gnumeric_total_row_count_times_two,
)

class TestGnumericSheetCountTimesTwo:
    def test_returns_int(self):
        assert isinstance(gnumeric_sheet_count_times_two(_GNUMERIC), int)
    def test_double_of_base(self):
        assert gnumeric_sheet_count_times_two(_GNUMERIC) == gnumeric_sheet_count(_GNUMERIC) * 2
    def test_positive(self):
        assert gnumeric_sheet_count_times_two(_GNUMERIC) > 0

class TestGnumericTotalRowCountTimesTwo:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_two(_GNUMERIC), int)
    def test_double_of_base(self):
        assert gnumeric_total_row_count_times_two(_GNUMERIC) == gnumeric_total_row_count(_GNUMERIC) * 2
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_two(_GNUMERIC) >= 0
