"""Sprint R428 — XCF/ZST/TOML/FODG/Gnumeric deepening round 3."""
import sys, pathlib, pytest

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf.xcf_parser import xcf_num_layers_squared, xcf_image_type_id_squared, parse_xcf_strict
from src.python.zst.zst_codec import zst_frame_count_squared, zst_overhead_bytes_squared, zst_frame_count, zst_overhead_bytes
from src.python.toml.toml_codec import toml_nested_table_count_squared, toml_string_count_plus_key_count, toml_nested_table_count, toml_string_count, toml_total_keys
from src.python.fodg.fodg_codec import fodg_page_count_plus_shape_count, fodg_shape_count_squared, fodg_page_count, fodg_total_shape_count
from src.python.gnumeric.gnumeric_codec import gnumeric_row_count_squared, gnumeric_avg_cells_plus_max_cells, gnumeric_total_row_count, gnumeric_avg_cells_per_sheet, gnumeric_max_cell_per_sheet

_SAMPLES = _REPO / "samples" / "by-format"
_XCF = _SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf"
_ZST = _SAMPLES / "zst" / "valid" / "block-128k.zst"
_FODG = _SAMPLES / "fodg" / "empty-page.fodg"
_GNUMERIC = _SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric"


# === XCF ===
class TestXcfNumLayersSquared:
    def test_returns_int(self):
        assert isinstance(xcf_num_layers_squared(_XCF), int)

    def test_equals_square(self):
        img = parse_xcf_strict(_XCF)
        assert xcf_num_layers_squared(_XCF) == img.num_layers * img.num_layers

    def test_non_negative(self):
        assert xcf_num_layers_squared(_XCF) >= 0


class TestXcfImageTypeIdSquared:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_squared(_XCF), int)

    def test_equals_square(self):
        img = parse_xcf_strict(_XCF)
        assert xcf_image_type_id_squared(_XCF) == img.image_type * img.image_type

    def test_non_negative(self):
        assert xcf_image_type_id_squared(_XCF) >= 0


# === ZST ===
class TestZstFrameCountSquared:
    def test_returns_int(self):
        assert isinstance(zst_frame_count_squared(_ZST), int)

    def test_equals_square(self):
        fc = zst_frame_count(_ZST)
        assert zst_frame_count_squared(_ZST) == fc * fc

    def test_non_negative(self):
        assert zst_frame_count_squared(_ZST) >= 0


class TestZstOverheadBytesSquared:
    def test_returns_int(self):
        assert isinstance(zst_overhead_bytes_squared(_ZST), int)

    def test_equals_square(self):
        ob = zst_overhead_bytes(_ZST)
        assert zst_overhead_bytes_squared(_ZST) == ob * ob

    def test_non_negative(self):
        assert zst_overhead_bytes_squared(_ZST) >= 0


# === TOML ===
class TestTomlNestedTableCountSquared:
    def test_returns_int(self, tmp_path):
        p = tmp_path / "test.toml"
        p.write_text('[a]\nb = 1\n[a.c]\nd = 2\n')
        assert isinstance(toml_nested_table_count_squared(str(p)), int)

    def test_equals_square(self, tmp_path):
        p = tmp_path / "test.toml"
        p.write_text('[a]\nb = 1\n[a.c]\nd = 2\n')
        nc = toml_nested_table_count(str(p))
        assert toml_nested_table_count_squared(str(p)) == nc * nc

    def test_non_negative(self, tmp_path):
        p = tmp_path / "test.toml"
        p.write_text('a = 1\n')
        assert toml_nested_table_count_squared(str(p)) >= 0


class TestTomlStringCountPlusKeyCount:
    def test_returns_int(self, tmp_path):
        p = tmp_path / "test.toml"
        p.write_text('a = "hello"\nb = 42\n')
        assert isinstance(toml_string_count_plus_key_count(str(p)), int)

    def test_equals_sum(self, tmp_path):
        p = tmp_path / "test.toml"
        p.write_text('a = "hello"\nb = 42\n')
        assert toml_string_count_plus_key_count(str(p)) == toml_string_count(str(p)) + toml_total_keys(str(p))

    def test_exceeds_key_count(self, tmp_path):
        p = tmp_path / "test.toml"
        p.write_text('a = "hello"\nb = "world"\n')
        assert toml_string_count_plus_key_count(str(p)) >= toml_total_keys(str(p))


# === FODG ===
class TestFodgPageCountPlusShapeCount:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_plus_shape_count(_FODG), int)

    def test_equals_sum(self):
        assert fodg_page_count_plus_shape_count(_FODG) == fodg_page_count(_FODG) + fodg_total_shape_count(_FODG)

    def test_non_negative(self):
        assert fodg_page_count_plus_shape_count(_FODG) >= 0


class TestFodgShapeCountSquared:
    def test_returns_int(self):
        assert isinstance(fodg_shape_count_squared(_FODG), int)

    def test_equals_square(self):
        sc = fodg_total_shape_count(_FODG)
        assert fodg_shape_count_squared(_FODG) == sc * sc

    def test_non_negative(self):
        assert fodg_shape_count_squared(_FODG) >= 0


# === Gnumeric ===
class TestGnumericRowCountSquared:
    def test_returns_int(self):
        assert isinstance(gnumeric_row_count_squared(_GNUMERIC), int)

    def test_equals_square(self):
        rc = gnumeric_total_row_count(_GNUMERIC)
        assert gnumeric_row_count_squared(_GNUMERIC) == rc * rc

    def test_non_negative(self):
        assert gnumeric_row_count_squared(_GNUMERIC) >= 0


class TestGnumericAvgCellsPlusMaxCells:
    def test_returns_number(self):
        assert isinstance(gnumeric_avg_cells_plus_max_cells(_GNUMERIC), (int, float))

    def test_equals_sum(self):
        assert gnumeric_avg_cells_plus_max_cells(_GNUMERIC) == gnumeric_avg_cells_per_sheet(_GNUMERIC) + gnumeric_max_cell_per_sheet(_GNUMERIC)

    def test_non_negative(self):
        assert gnumeric_avg_cells_plus_max_cells(_GNUMERIC) >= 0
