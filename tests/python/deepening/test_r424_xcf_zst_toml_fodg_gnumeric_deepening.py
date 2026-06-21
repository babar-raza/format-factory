"""Tests for 10 new analytics: XCF/ZST/TOML/FODG/Gnumeric deepening sprint R424."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from src.python.xcf.xcf_parser import (
    xcf_height_squared,
    xcf_height_plus_num_layers,
    parse_xcf_strict,
)

from src.python.zst.zst_codec import (
    zst_header_size_plus_frame_count,
    zst_decompressed_size_squared,
    zst_header_size,
    zst_frame_count,
    zst_decompressed_size,
)

from src.python.toml.toml_codec import (
    toml_total_keys_squared,
    toml_key_count_times_two,
    toml_total_keys,
)

from src.python.fodg.fodg_codec import (
    fodg_page_count_squared,
    fodg_shape_count_plus_text_count,
    fodg_page_count,
    fodg_total_shape_count,
    fodg_text_item_count,
)

from src.python.gnumeric.gnumeric_codec import (
    gnumeric_total_cell_count_squared,
    gnumeric_max_cells_plus_sheet_count,
    gnumeric_total_cell_count,
    gnumeric_max_cell_per_sheet,
    gnumeric_sheet_count,
)

_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-rgba-blue.xcf"
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid" / "block-128k.zst"
_FODG = _REPO / "samples" / "by-format" / "fodg" / "empty-page.fodg"
_GNUMERIC = _REPO / "samples" / "by-format" / "gnumeric" / "minimal-spreadsheet.gnumeric"


def _toml_path(tmp_path):
    p = tmp_path / "test.toml"
    p.write_text('[section]\na = 1\nb = "hello"\nc = true\n')
    return p


class TestXcfHeightSquared:
    def test_returns_int(self):
        assert isinstance(xcf_height_squared(_XCF), int)

    def test_matches_formula(self):
        img = parse_xcf_strict(_XCF)
        assert xcf_height_squared(_XCF) == img.height * img.height

    def test_positive(self):
        assert xcf_height_squared(_XCF) >= 1


class TestXcfHeightPlusNumLayers:
    def test_returns_int(self):
        assert isinstance(xcf_height_plus_num_layers(_XCF), int)

    def test_matches_formula(self):
        img = parse_xcf_strict(_XCF)
        assert xcf_height_plus_num_layers(_XCF) == img.height + img.num_layers

    def test_positive(self):
        assert xcf_height_plus_num_layers(_XCF) >= 1


class TestZstHeaderSizePlusFrameCount:
    def test_returns_int(self):
        assert isinstance(zst_header_size_plus_frame_count(_ZST), int)

    def test_matches_sum(self):
        assert zst_header_size_plus_frame_count(_ZST) == zst_header_size(_ZST) + zst_frame_count(_ZST)

    def test_non_negative(self):
        assert zst_header_size_plus_frame_count(_ZST) >= 0


class TestZstDecompressedSizeSquared:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_squared(_ZST), int)

    def test_matches_formula(self):
        ds = zst_decompressed_size(_ZST)
        assert zst_decompressed_size_squared(_ZST) == ds * ds

    def test_non_negative(self):
        assert zst_decompressed_size_squared(_ZST) >= 0


class TestTomlTotalKeysSquared:
    def test_returns_int(self, tmp_path):
        assert isinstance(toml_total_keys_squared(_toml_path(tmp_path)), int)

    def test_matches_formula(self, tmp_path):
        p = _toml_path(tmp_path)
        k = toml_total_keys(p)
        assert toml_total_keys_squared(p) == k * k

    def test_positive(self, tmp_path):
        assert toml_total_keys_squared(_toml_path(tmp_path)) >= 1


class TestTomlKeyCountTimesTwo:
    def test_returns_int(self, tmp_path):
        assert isinstance(toml_key_count_times_two(_toml_path(tmp_path)), int)

    def test_matches_formula(self, tmp_path):
        p = _toml_path(tmp_path)
        assert toml_key_count_times_two(p) == toml_total_keys(p) * 2

    def test_positive(self, tmp_path):
        assert toml_key_count_times_two(_toml_path(tmp_path)) >= 2


class TestFodgPageCountSquared:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_squared(_FODG), int)

    def test_matches_formula(self):
        pc = fodg_page_count(_FODG)
        assert fodg_page_count_squared(_FODG) == pc * pc

    def test_non_negative(self):
        assert fodg_page_count_squared(_FODG) >= 0


class TestFodgShapeCountPlusTextCount:
    def test_returns_int(self):
        assert isinstance(fodg_shape_count_plus_text_count(_FODG), int)

    def test_matches_sum(self):
        assert fodg_shape_count_plus_text_count(_FODG) == fodg_total_shape_count(_FODG) + fodg_text_item_count(_FODG)

    def test_non_negative(self):
        assert fodg_shape_count_plus_text_count(_FODG) >= 0


class TestGnumericTotalCellCountSquared:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_cell_count_squared(_GNUMERIC), int)

    def test_matches_formula(self):
        tc = gnumeric_total_cell_count(_GNUMERIC)
        assert gnumeric_total_cell_count_squared(_GNUMERIC) == tc * tc

    def test_non_negative(self):
        assert gnumeric_total_cell_count_squared(_GNUMERIC) >= 0


class TestGnumericMaxCellsPlusSheetCount:
    def test_returns_int(self):
        assert isinstance(gnumeric_max_cells_plus_sheet_count(_GNUMERIC), int)

    def test_matches_sum(self):
        assert gnumeric_max_cells_plus_sheet_count(_GNUMERIC) == gnumeric_max_cell_per_sheet(_GNUMERIC) + gnumeric_sheet_count(_GNUMERIC)

    def test_positive(self):
        assert gnumeric_max_cells_plus_sheet_count(_GNUMERIC) >= 1
