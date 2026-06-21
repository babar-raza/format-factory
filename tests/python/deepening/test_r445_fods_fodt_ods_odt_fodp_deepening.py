"""Sprint R445 — FODS/FODT/ODS/ODT/FODP round 7 deepening tests."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods import parse_fods_strict, fods_row_count_times_two, fods_string_cell_count_times_two, fods_total_row_count
from src.python.fodt import fodt_heading_count_times_two, fodt_total_chars_times_two, fodt_heading_count, fodt_total_char_count
from src.python.ods import ods_total_cells_squared, ods_string_cell_count_times_two, ods_total_cell_count, ods_string_cell_count
from src.python.odt import odt_char_count_squared, odt_total_chars_times_two, odt_char_count, odt_total_char_count
from src.python.fodp import fodp_slide_count_times_three, fodp_total_shapes_times_two, fodp_slide_count, fodp_total_shape_count

SAMPLES = _REPO / "samples" / "by-format"
FODS_SAMPLE = SAMPLES / "fods" / "minimal-spreadsheet.fods"
FODT_SAMPLE = SAMPLES / "fodt" / "minimal-document.fodt"
ODS_SAMPLE = SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods"
ODT_SAMPLE = SAMPLES / "odt" / "valid" / "minimal-document.odt"
FODP_SAMPLE = SAMPLES / "fodp" / "title-only.fodp"


# --- FODS: fods_row_count_times_two ---
class TestFodsRowCountTimesTwo:
    def test_returns_int(self):
        wb = parse_fods_strict(FODS_SAMPLE)
        assert isinstance(fods_row_count_times_two(wb), int)

    def test_is_double_row_count(self):
        wb = parse_fods_strict(FODS_SAMPLE)
        assert fods_row_count_times_two(wb) == fods_total_row_count(wb) * 2

    def test_non_negative(self):
        wb = parse_fods_strict(FODS_SAMPLE)
        assert fods_row_count_times_two(wb) >= 0


# --- FODS: fods_string_cell_count_times_two ---
class TestFodsStringCellCountTimesTwo:
    def test_returns_int(self):
        wb = parse_fods_strict(FODS_SAMPLE)
        assert isinstance(fods_string_cell_count_times_two(wb), int)

    def test_is_double(self):
        wb = parse_fods_strict(FODS_SAMPLE)
        from src.python.fods import fods_string_cell_count
        assert fods_string_cell_count_times_two(wb) == fods_string_cell_count(wb) * 2

    def test_non_negative(self):
        wb = parse_fods_strict(FODS_SAMPLE)
        assert fods_string_cell_count_times_two(wb) >= 0


# --- FODT: fodt_heading_count_times_two ---
class TestFodtHeadingCountTimesTwo:
    def test_returns_int(self):
        assert isinstance(fodt_heading_count_times_two(FODT_SAMPLE), int)

    def test_is_double_heading_count(self):
        assert fodt_heading_count_times_two(FODT_SAMPLE) == fodt_heading_count(FODT_SAMPLE) * 2

    def test_non_negative(self):
        assert fodt_heading_count_times_two(FODT_SAMPLE) >= 0


# --- FODT: fodt_total_chars_times_two ---
class TestFodtTotalCharsTimesTwo:
    def test_returns_int(self):
        assert isinstance(fodt_total_chars_times_two(FODT_SAMPLE), int)

    def test_is_double_total_char_count(self):
        assert fodt_total_chars_times_two(FODT_SAMPLE) == fodt_total_char_count(FODT_SAMPLE) * 2

    def test_non_negative(self):
        assert fodt_total_chars_times_two(FODT_SAMPLE) >= 0


# --- ODS: ods_total_cells_squared ---
class TestOdsTotalCellsSquared:
    def test_returns_int(self):
        assert isinstance(ods_total_cells_squared(ODS_SAMPLE), int)

    def test_is_square_of_total_cell_count(self):
        tc = ods_total_cell_count(ODS_SAMPLE)
        assert ods_total_cells_squared(ODS_SAMPLE) == tc * tc

    def test_non_negative(self):
        assert ods_total_cells_squared(ODS_SAMPLE) >= 0


# --- ODS: ods_string_cell_count_times_two ---
class TestOdsStringCellCountTimesTwo:
    def test_returns_int(self):
        assert isinstance(ods_string_cell_count_times_two(ODS_SAMPLE), int)

    def test_is_double_string_cell_count(self):
        assert ods_string_cell_count_times_two(ODS_SAMPLE) == ods_string_cell_count(ODS_SAMPLE) * 2

    def test_non_negative(self):
        assert ods_string_cell_count_times_two(ODS_SAMPLE) >= 0


# --- ODT: odt_char_count_squared ---
class TestOdtCharCountSquared:
    def test_returns_int(self):
        assert isinstance(odt_char_count_squared(ODT_SAMPLE), int)

    def test_is_square_of_char_count(self):
        cc = odt_char_count(ODT_SAMPLE)
        assert odt_char_count_squared(ODT_SAMPLE) == cc * cc

    def test_non_negative(self):
        assert odt_char_count_squared(ODT_SAMPLE) >= 0


# --- ODT: odt_total_chars_times_two ---
class TestOdtTotalCharsTimesTwo:
    def test_returns_int(self):
        assert isinstance(odt_total_chars_times_two(ODT_SAMPLE), int)

    def test_is_double_total_char_count(self):
        assert odt_total_chars_times_two(ODT_SAMPLE) == odt_total_char_count(ODT_SAMPLE) * 2

    def test_non_negative(self):
        assert odt_total_chars_times_two(ODT_SAMPLE) >= 0


# --- FODP: fodp_slide_count_times_three ---
class TestFodpSlideCountTimesThree:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_three(FODP_SAMPLE), int)

    def test_is_triple_slide_count(self):
        assert fodp_slide_count_times_three(FODP_SAMPLE) == fodp_slide_count(FODP_SAMPLE) * 3

    def test_non_negative(self):
        assert fodp_slide_count_times_three(FODP_SAMPLE) >= 0


# --- FODP: fodp_total_shapes_times_two ---
class TestFodpTotalShapesTimesTwo:
    def test_returns_int(self):
        assert isinstance(fodp_total_shapes_times_two(FODP_SAMPLE), int)

    def test_is_double_total_shape_count(self):
        assert fodp_total_shapes_times_two(FODP_SAMPLE) == fodp_total_shape_count(FODP_SAMPLE) * 2

    def test_non_negative(self):
        assert fodp_total_shapes_times_two(FODP_SAMPLE) >= 0
