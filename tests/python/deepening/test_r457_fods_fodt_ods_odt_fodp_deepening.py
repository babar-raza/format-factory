"""Sprint R457 — FODS/FODT/ODS/ODT/FODP round 10 deepening tests."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods import fods_sheet_count_times_four, fods_total_cell_count_times_four, fods_sheet_count, fods_total_cell_count, parse_fods_strict
from src.python.fodt import fodt_paragraph_count_times_four, fodt_word_count_times_four, fodt_paragraph_count, fodt_word_count
from src.python.ods import ods_sheet_count_times_four, ods_total_cell_count_times_four, ods_sheet_count, ods_total_cell_count
from src.python.odt import odt_word_count_times_four, odt_paragraph_count_times_four, odt_word_count, odt_paragraph_count
from src.python.fodp import fodp_slide_count_times_four, fodp_word_count_times_four, fodp_slide_count, fodp_word_count

SAMPLES = _REPO / "samples" / "by-format"
FODS_SAMPLE = SAMPLES / "fods" / "minimal-spreadsheet.fods"
FODT_SAMPLE = SAMPLES / "fodt" / "minimal-document.fodt"
ODS_SAMPLE = SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods"
ODT_SAMPLE = SAMPLES / "odt" / "valid" / "minimal-document.odt"
FODP_SAMPLE = SAMPLES / "fodp" / "title-only.fodp"


class TestFodsSheetCountTimesFour:
    def test_returns_int(self):
        wb = parse_fods_strict(FODS_SAMPLE)
        assert isinstance(fods_sheet_count_times_four(wb), int)
    def test_is_quadruple(self):
        wb = parse_fods_strict(FODS_SAMPLE)
        assert fods_sheet_count_times_four(wb) == fods_sheet_count(wb) * 4
    def test_non_negative(self):
        wb = parse_fods_strict(FODS_SAMPLE)
        assert fods_sheet_count_times_four(wb) >= 0


class TestFodsTotalCellCountTimesFour:
    def test_returns_int(self):
        wb = parse_fods_strict(FODS_SAMPLE)
        assert isinstance(fods_total_cell_count_times_four(wb), int)
    def test_is_quadruple(self):
        wb = parse_fods_strict(FODS_SAMPLE)
        assert fods_total_cell_count_times_four(wb) == fods_total_cell_count(wb) * 4
    def test_non_negative(self):
        wb = parse_fods_strict(FODS_SAMPLE)
        assert fods_total_cell_count_times_four(wb) >= 0


class TestFodtParagraphCountTimesFour:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_four(FODT_SAMPLE), int)
    def test_is_quadruple(self):
        assert fodt_paragraph_count_times_four(FODT_SAMPLE) == fodt_paragraph_count(FODT_SAMPLE) * 4
    def test_non_negative(self):
        assert fodt_paragraph_count_times_four(FODT_SAMPLE) >= 0


class TestFodtWordCountTimesFour:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_four(FODT_SAMPLE), int)
    def test_is_quadruple(self):
        assert fodt_word_count_times_four(FODT_SAMPLE) == fodt_word_count(FODT_SAMPLE) * 4
    def test_non_negative(self):
        assert fodt_word_count_times_four(FODT_SAMPLE) >= 0


class TestOdsSheetCountTimesFour:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_four(ODS_SAMPLE), int)
    def test_is_quadruple(self):
        assert ods_sheet_count_times_four(ODS_SAMPLE) == ods_sheet_count(ODS_SAMPLE) * 4
    def test_non_negative(self):
        assert ods_sheet_count_times_four(ODS_SAMPLE) >= 0


class TestOdsTotalCellCountTimesFour:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_four(ODS_SAMPLE), int)
    def test_is_quadruple(self):
        assert ods_total_cell_count_times_four(ODS_SAMPLE) == ods_total_cell_count(ODS_SAMPLE) * 4
    def test_non_negative(self):
        assert ods_total_cell_count_times_four(ODS_SAMPLE) >= 0


class TestOdtWordCountTimesFour:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_four(ODT_SAMPLE), int)
    def test_is_quadruple(self):
        assert odt_word_count_times_four(ODT_SAMPLE) == odt_word_count(ODT_SAMPLE) * 4
    def test_non_negative(self):
        assert odt_word_count_times_four(ODT_SAMPLE) >= 0


class TestOdtParagraphCountTimesFour:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_four(ODT_SAMPLE), int)
    def test_is_quadruple(self):
        assert odt_paragraph_count_times_four(ODT_SAMPLE) == odt_paragraph_count(ODT_SAMPLE) * 4
    def test_non_negative(self):
        assert odt_paragraph_count_times_four(ODT_SAMPLE) >= 0


class TestFodpSlideCountTimesFour:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_four(FODP_SAMPLE), int)
    def test_is_quadruple(self):
        assert fodp_slide_count_times_four(FODP_SAMPLE) == fodp_slide_count(FODP_SAMPLE) * 4
    def test_non_negative(self):
        assert fodp_slide_count_times_four(FODP_SAMPLE) >= 0


class TestFodpWordCountTimesFour:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_four(FODP_SAMPLE), int)
    def test_is_quadruple(self):
        assert fodp_word_count_times_four(FODP_SAMPLE) == fodp_word_count(FODP_SAMPLE) * 4
    def test_non_negative(self):
        assert fodp_word_count_times_four(FODP_SAMPLE) >= 0
