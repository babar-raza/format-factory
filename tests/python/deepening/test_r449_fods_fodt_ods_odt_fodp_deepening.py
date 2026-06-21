"""Sprint R449 — FODS/FODT/ODS/ODT/FODP round 8 deepening tests."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods import parse_fods_strict, fods_sheet_count_times_three, fods_total_row_count_squared, fods_sheet_count, fods_total_row_count
from src.python.fodt import fodt_paragraph_count_times_three, fodt_word_count_times_three, fodt_paragraph_count, fodt_word_count
from src.python.ods import ods_total_row_count_squared, ods_sheet_count_times_three, ods_total_row_count, ods_sheet_count
from src.python.odt import odt_heading_count_squared, odt_file_size_squared, odt_heading_count, odt_file_size_bytes
from src.python.fodp import fodp_total_text_chars_times_three, fodp_shape_count_times_three, fodp_total_text_chars, fodp_total_shape_count

SAMPLES = _REPO / "samples" / "by-format"
FODS_SAMPLE = SAMPLES / "fods" / "minimal-spreadsheet.fods"
FODT_SAMPLE = SAMPLES / "fodt" / "minimal-document.fodt"
ODS_SAMPLE = SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods"
ODT_SAMPLE = SAMPLES / "odt" / "valid" / "minimal-document.odt"
FODP_SAMPLE = SAMPLES / "fodp" / "title-only.fodp"


# --- FODS ---
class TestFodsSheetCountTimesThree:
    def test_returns_int(self):
        wb = parse_fods_strict(FODS_SAMPLE)
        assert isinstance(fods_sheet_count_times_three(wb), int)

    def test_is_triple(self):
        wb = parse_fods_strict(FODS_SAMPLE)
        assert fods_sheet_count_times_three(wb) == fods_sheet_count(wb) * 3

    def test_non_negative(self):
        wb = parse_fods_strict(FODS_SAMPLE)
        assert fods_sheet_count_times_three(wb) >= 0


class TestFodsTotalRowCountSquared:
    def test_returns_int(self):
        wb = parse_fods_strict(FODS_SAMPLE)
        assert isinstance(fods_total_row_count_squared(wb), int)

    def test_is_square(self):
        wb = parse_fods_strict(FODS_SAMPLE)
        rc = fods_total_row_count(wb)
        assert fods_total_row_count_squared(wb) == rc * rc

    def test_non_negative(self):
        wb = parse_fods_strict(FODS_SAMPLE)
        assert fods_total_row_count_squared(wb) >= 0


# --- FODT ---
class TestFodtParagraphCountTimesThree:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_three(FODT_SAMPLE), int)

    def test_is_triple(self):
        assert fodt_paragraph_count_times_three(FODT_SAMPLE) == fodt_paragraph_count(FODT_SAMPLE) * 3

    def test_non_negative(self):
        assert fodt_paragraph_count_times_three(FODT_SAMPLE) >= 0


class TestFodtWordCountTimesThree:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_three(FODT_SAMPLE), int)

    def test_is_triple(self):
        assert fodt_word_count_times_three(FODT_SAMPLE) == fodt_word_count(FODT_SAMPLE) * 3

    def test_non_negative(self):
        assert fodt_word_count_times_three(FODT_SAMPLE) >= 0


# --- ODS ---
class TestOdsTotalRowCountSquared:
    def test_returns_int(self):
        assert isinstance(ods_total_row_count_squared(ODS_SAMPLE), int)

    def test_is_square(self):
        rc = ods_total_row_count(ODS_SAMPLE)
        assert ods_total_row_count_squared(ODS_SAMPLE) == rc * rc

    def test_non_negative(self):
        assert ods_total_row_count_squared(ODS_SAMPLE) >= 0


class TestOdsSheetCountTimesThree:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_three(ODS_SAMPLE), int)

    def test_is_triple(self):
        assert ods_sheet_count_times_three(ODS_SAMPLE) == ods_sheet_count(ODS_SAMPLE) * 3

    def test_positive(self):
        assert ods_sheet_count_times_three(ODS_SAMPLE) > 0


# --- ODT ---
class TestOdtHeadingCountSquared:
    def test_returns_int(self):
        assert isinstance(odt_heading_count_squared(ODT_SAMPLE), int)

    def test_is_square(self):
        hc = odt_heading_count(ODT_SAMPLE)
        assert odt_heading_count_squared(ODT_SAMPLE) == hc * hc

    def test_non_negative(self):
        assert odt_heading_count_squared(ODT_SAMPLE) >= 0


class TestOdtFileSizeSquared:
    def test_returns_int(self):
        assert isinstance(odt_file_size_squared(ODT_SAMPLE), int)

    def test_is_square(self):
        fs = odt_file_size_bytes(ODT_SAMPLE)
        assert odt_file_size_squared(ODT_SAMPLE) == fs * fs

    def test_positive(self):
        assert odt_file_size_squared(ODT_SAMPLE) > 0


# --- FODP ---
class TestFodpTotalTextCharsTimesThree:
    def test_returns_int(self):
        assert isinstance(fodp_total_text_chars_times_three(FODP_SAMPLE), int)

    def test_is_triple(self):
        assert fodp_total_text_chars_times_three(FODP_SAMPLE) == fodp_total_text_chars(FODP_SAMPLE) * 3

    def test_non_negative(self):
        assert fodp_total_text_chars_times_three(FODP_SAMPLE) >= 0


class TestFodpShapeCountTimesThree:
    def test_returns_int(self):
        assert isinstance(fodp_shape_count_times_three(FODP_SAMPLE), int)

    def test_is_triple(self):
        assert fodp_shape_count_times_three(FODP_SAMPLE) == fodp_total_shape_count(FODP_SAMPLE) * 3

    def test_non_negative(self):
        assert fodp_shape_count_times_three(FODP_SAMPLE) >= 0
