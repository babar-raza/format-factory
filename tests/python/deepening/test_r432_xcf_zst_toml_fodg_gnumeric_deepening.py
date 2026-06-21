"""Sprint R432 — product deepening round 3 for XCF/ZST/TOML/FODG/Gnumeric.

New analytics:
  XCF:      xcf_width_squared, xcf_height_squared
  ZST:      zst_compressed_size_squared, zst_decompressed_plus_compressed
  TOML:     toml_key_count_squared, toml_table_count_plus_key_count
  FODG:     fodg_text_item_count_plus_page_count, fodg_total_shape_count_times_page_count
  Gnumeric: gnumeric_sheet_count_times_row_count, gnumeric_total_cells_squared
"""
import sys, pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

# ── XCF ──────────────────────────────────────────────────────────────
from src.python.xcf.xcf_parser import (
    xcf_width_squared,
    xcf_height_squared,
    parse_xcf_strict,
)

_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"


class TestXcfWidthSquared:
    def test_minimal(self):
        p = _XCF / "1x1-rgba-blue.xcf"
        img = parse_xcf_strict(p)
        assert xcf_width_squared(p) == img.width ** 2

    def test_type(self):
        p = _XCF / "1x1-rgba-blue.xcf"
        assert isinstance(xcf_width_squared(p), int)

    def test_nonneg(self):
        p = _XCF / "1x1-rgba-blue.xcf"
        assert xcf_width_squared(p) >= 0


class TestXcfHeightSquared:
    def test_minimal(self):
        p = _XCF / "1x1-rgba-blue.xcf"
        img = parse_xcf_strict(p)
        assert xcf_height_squared(p) == img.height ** 2

    def test_type(self):
        p = _XCF / "1x1-rgba-blue.xcf"
        assert isinstance(xcf_height_squared(p), int)

    def test_nonneg(self):
        p = _XCF / "1x1-rgba-blue.xcf"
        assert xcf_height_squared(p) >= 0


# ── ZST ──────────────────────────────────────────────────────────────
from src.python.zst.zst_codec import (
    zst_compressed_size_squared,
    zst_decompressed_plus_compressed,
    zst_compressed_size,
    zst_decompressed_size,
)

_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"


class TestZstCompressedSizeSquared:
    def test_minimal(self):
        p = _ZST / "text-compressed.zst"
        cs = zst_compressed_size(p)
        assert zst_compressed_size_squared(p) == cs * cs

    def test_type(self):
        p = _ZST / "text-compressed.zst"
        assert isinstance(zst_compressed_size_squared(p), int)

    def test_nonneg(self):
        p = _ZST / "text-compressed.zst"
        assert zst_compressed_size_squared(p) >= 0


class TestZstDecompressedPlusCompressed:
    def test_minimal(self):
        p = _ZST / "text-compressed.zst"
        expected = zst_decompressed_size(p) + zst_compressed_size(p)
        assert zst_decompressed_plus_compressed(p) == expected

    def test_type(self):
        p = _ZST / "text-compressed.zst"
        assert isinstance(zst_decompressed_plus_compressed(p), int)

    def test_positive(self):
        p = _ZST / "text-compressed.zst"
        assert zst_decompressed_plus_compressed(p) > 0


# ── TOML ─────────────────────────────────────────────────────────────
from src.python.toml.toml_codec import (
    toml_key_count_squared,
    toml_table_count_plus_key_count,
    toml_total_keys,
    toml_table_count,
)

_TOML = _REPO / "samples" / "by-format" / "toml"


class TestTomlKeyCountSquared:
    def test_minimal(self):
        p = _TOML / "minimal.toml"
        kc = toml_total_keys(p)
        assert toml_key_count_squared(p) == kc * kc

    def test_type(self):
        p = _TOML / "minimal.toml"
        assert isinstance(toml_key_count_squared(p), int)

    def test_nonneg(self):
        p = _TOML / "minimal.toml"
        assert toml_key_count_squared(p) >= 0


class TestTomlTableCountPlusKeyCount:
    def test_minimal(self):
        p = _TOML / "minimal.toml"
        expected = toml_table_count(p) + toml_total_keys(p)
        assert toml_table_count_plus_key_count(p) == expected

    def test_type(self):
        p = _TOML / "minimal.toml"
        assert isinstance(toml_table_count_plus_key_count(p), int)

    def test_nonneg(self):
        p = _TOML / "minimal.toml"
        assert toml_table_count_plus_key_count(p) >= 0


# ── FODG ─────────────────────────────────────────────────────────────
from src.python.fodg.fodg_codec import (
    fodg_text_item_count_plus_page_count,
    fodg_total_shape_count_times_page_count,
    fodg_text_item_count,
    fodg_page_count,
    fodg_total_shape_count,
)

_FODG = _REPO / "samples" / "by-format" / "fodg"


class TestFodgTextItemCountPlusPageCount:
    def test_minimal(self):
        p = _FODG / "minimal-drawing.fodg"
        expected = fodg_text_item_count(p) + fodg_page_count(p)
        assert fodg_text_item_count_plus_page_count(p) == expected

    def test_type(self):
        p = _FODG / "minimal-drawing.fodg"
        assert isinstance(fodg_text_item_count_plus_page_count(p), int)

    def test_nonneg(self):
        p = _FODG / "minimal-drawing.fodg"
        assert fodg_text_item_count_plus_page_count(p) >= 0


class TestFodgTotalShapeCountTimesPageCount:
    def test_minimal(self):
        p = _FODG / "minimal-drawing.fodg"
        expected = fodg_total_shape_count(p) * fodg_page_count(p)
        assert fodg_total_shape_count_times_page_count(p) == expected

    def test_type(self):
        p = _FODG / "minimal-drawing.fodg"
        assert isinstance(fodg_total_shape_count_times_page_count(p), int)

    def test_nonneg(self):
        p = _FODG / "minimal-drawing.fodg"
        assert fodg_total_shape_count_times_page_count(p) >= 0


# ── Gnumeric ─────────────────────────────────────────────────────────
from src.python.gnumeric.gnumeric_codec import (
    gnumeric_sheet_count_times_row_count,
    gnumeric_total_cells_squared,
    gnumeric_sheet_count,
    gnumeric_total_row_count,
    gnumeric_total_cell_count,
)

_GNUMERIC = _REPO / "samples" / "by-format" / "gnumeric"


class TestGnumericSheetCountTimesRowCount:
    def test_minimal(self):
        p = _GNUMERIC / "minimal-spreadsheet.gnumeric"
        expected = gnumeric_sheet_count(p) * gnumeric_total_row_count(p)
        assert gnumeric_sheet_count_times_row_count(p) == expected

    def test_type(self):
        p = _GNUMERIC / "minimal-spreadsheet.gnumeric"
        assert isinstance(gnumeric_sheet_count_times_row_count(p), int)

    def test_nonneg(self):
        p = _GNUMERIC / "minimal-spreadsheet.gnumeric"
        assert gnumeric_sheet_count_times_row_count(p) >= 0


class TestGnumericTotalCellsSquared:
    def test_minimal(self):
        p = _GNUMERIC / "minimal-spreadsheet.gnumeric"
        tc = gnumeric_total_cell_count(p)
        assert gnumeric_total_cells_squared(p) == tc * tc

    def test_type(self):
        p = _GNUMERIC / "minimal-spreadsheet.gnumeric"
        assert isinstance(gnumeric_total_cells_squared(p), int)

    def test_nonneg(self):
        p = _GNUMERIC / "minimal-spreadsheet.gnumeric"
        assert gnumeric_total_cells_squared(p) >= 0
