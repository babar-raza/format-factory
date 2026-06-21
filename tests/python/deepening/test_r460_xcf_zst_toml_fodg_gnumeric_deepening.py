"""Sprint R460 — XCF/ZST/TOML/FODG/Gnumeric round 11 deepening tests."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import xcf_width_times_four, xcf_height_times_four, xcf_width, xcf_height
from src.python.zst import zst_compressed_size_times_four, zst_frame_count_times_four, zst_compressed_size, zst_frame_count
from src.python.toml import toml_total_keys_times_four, toml_table_count_times_four, toml_total_keys, toml_table_count
from src.python.fodg import fodg_file_size_times_four, fodg_total_text_items_times_four, fodg_file_size_bytes, fodg_total_text_items
from src.python.gnumeric import gnumeric_sheet_count_times_four, gnumeric_total_cell_count_times_four, gnumeric_sheet_count, gnumeric_total_cell_count

SAMPLES = _REPO / "samples" / "by-format"
XCF_SAMPLE = SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf"
ZST_SAMPLE = SAMPLES / "zst" / "valid" / "text-compressed.zst"
TOML_SAMPLE = SAMPLES / "toml" / "minimal.toml"
FODG_SAMPLE = SAMPLES / "fodg" / "minimal-drawing.fodg"
GNUMERIC_SAMPLE = SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric"


class TestXcfWidthTimesFour:
    def test_returns_int(self):
        assert isinstance(xcf_width_times_four(XCF_SAMPLE), int)
    def test_is_quadruple(self):
        assert xcf_width_times_four(XCF_SAMPLE) == xcf_width(XCF_SAMPLE) * 4
    def test_non_negative(self):
        assert xcf_width_times_four(XCF_SAMPLE) >= 0


class TestXcfHeightTimesFour:
    def test_returns_int(self):
        assert isinstance(xcf_height_times_four(XCF_SAMPLE), int)
    def test_is_quadruple(self):
        assert xcf_height_times_four(XCF_SAMPLE) == xcf_height(XCF_SAMPLE) * 4
    def test_non_negative(self):
        assert xcf_height_times_four(XCF_SAMPLE) >= 0


class TestZstCompressedSizeTimesFour:
    def test_returns_int(self):
        assert isinstance(zst_compressed_size_times_four(ZST_SAMPLE), int)
    def test_is_quadruple(self):
        assert zst_compressed_size_times_four(ZST_SAMPLE) == zst_compressed_size(ZST_SAMPLE) * 4
    def test_non_negative(self):
        assert zst_compressed_size_times_four(ZST_SAMPLE) >= 0


class TestZstFrameCountTimesFour:
    def test_returns_int(self):
        assert isinstance(zst_frame_count_times_four(ZST_SAMPLE), int)
    def test_is_quadruple(self):
        assert zst_frame_count_times_four(ZST_SAMPLE) == zst_frame_count(ZST_SAMPLE) * 4
    def test_non_negative(self):
        assert zst_frame_count_times_four(ZST_SAMPLE) >= 0


class TestTomlTotalKeysTimesFour:
    def test_returns_int(self):
        assert isinstance(toml_total_keys_times_four(TOML_SAMPLE), int)
    def test_is_quadruple(self):
        assert toml_total_keys_times_four(TOML_SAMPLE) == toml_total_keys(TOML_SAMPLE) * 4
    def test_non_negative(self):
        assert toml_total_keys_times_four(TOML_SAMPLE) >= 0


class TestTomlTableCountTimesFour:
    def test_returns_int(self):
        assert isinstance(toml_table_count_times_four(TOML_SAMPLE), int)
    def test_is_quadruple(self):
        assert toml_table_count_times_four(TOML_SAMPLE) == toml_table_count(TOML_SAMPLE) * 4
    def test_non_negative(self):
        assert toml_table_count_times_four(TOML_SAMPLE) >= 0


class TestFodgFileSizeTimesFour:
    def test_returns_int(self):
        assert isinstance(fodg_file_size_times_four(FODG_SAMPLE), int)
    def test_is_quadruple(self):
        assert fodg_file_size_times_four(FODG_SAMPLE) == fodg_file_size_bytes(FODG_SAMPLE) * 4
    def test_non_negative(self):
        assert fodg_file_size_times_four(FODG_SAMPLE) >= 0


class TestFodgTotalTextItemsTimesFour:
    def test_returns_int(self):
        assert isinstance(fodg_total_text_items_times_four(FODG_SAMPLE), int)
    def test_is_quadruple(self):
        assert fodg_total_text_items_times_four(FODG_SAMPLE) == fodg_total_text_items(FODG_SAMPLE) * 4
    def test_non_negative(self):
        assert fodg_total_text_items_times_four(FODG_SAMPLE) >= 0


class TestGnumericSheetCountTimesFour:
    def test_returns_int(self):
        assert isinstance(gnumeric_sheet_count_times_four(GNUMERIC_SAMPLE), int)
    def test_is_quadruple(self):
        assert gnumeric_sheet_count_times_four(GNUMERIC_SAMPLE) == gnumeric_sheet_count(GNUMERIC_SAMPLE) * 4
    def test_non_negative(self):
        assert gnumeric_sheet_count_times_four(GNUMERIC_SAMPLE) >= 0


class TestGnumericTotalCellCountTimesFour:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_cell_count_times_four(GNUMERIC_SAMPLE), int)
    def test_is_quadruple(self):
        assert gnumeric_total_cell_count_times_four(GNUMERIC_SAMPLE) == gnumeric_total_cell_count(GNUMERIC_SAMPLE) * 4
    def test_non_negative(self):
        assert gnumeric_total_cell_count_times_four(GNUMERIC_SAMPLE) >= 0
