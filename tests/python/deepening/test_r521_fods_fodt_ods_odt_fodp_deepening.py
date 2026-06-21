"""Sprint R521 — FODS/FODT/ODS/ODT/FODP _times_nineteen composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fods.neutral_model import fods_sheet_count_times_nineteen, fods_total_cell_count_times_nineteen
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_nineteen, fodt_word_count_times_nineteen
from src.python.ods.ods_parser import ods_sheet_count_times_nineteen, ods_total_cell_count_times_nineteen
from src.python.odt.odt_parser import odt_word_count_times_nineteen, odt_paragraph_count_times_nineteen
from src.python.fodp.fodp_codec import fodp_slide_count_times_nineteen, fodp_word_count_times_nineteen
SAMPLES = _REPO / "samples" / "by-format"
_wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

class TestFodsSheetCountTimesNineteen:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_nineteen(_wb), int)
    def test_non_negative(self):
        assert fods_sheet_count_times_nineteen(_wb) >= 0
    def test_divisible(self):
        assert fods_sheet_count_times_nineteen(_wb) % 19 == 0
class TestFodsTotalCellCountTimesNineteen:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_nineteen(_wb), int)
    def test_non_negative(self):
        assert fods_total_cell_count_times_nineteen(_wb) >= 0
    def test_divisible(self):
        assert fods_total_cell_count_times_nineteen(_wb) % 19 == 0
class TestFodtParagraphCountTimesNineteen:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_nineteen(_FODT), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_nineteen(_FODT) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_nineteen(_FODT) % 19 == 0
class TestFodtWordCountTimesNineteen:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_nineteen(_FODT), int)
    def test_non_negative(self):
        assert fodt_word_count_times_nineteen(_FODT) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_nineteen(_FODT) % 19 == 0
class TestOdsSheetCountTimesNineteen:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_nineteen(_ODS), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_nineteen(_ODS) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_nineteen(_ODS) % 19 == 0
class TestOdsTotalCellCountTimesNineteen:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_nineteen(_ODS), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_nineteen(_ODS) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_nineteen(_ODS) % 19 == 0
class TestOdtWordCountTimesNineteen:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_nineteen(_ODT), int)
    def test_non_negative(self):
        assert odt_word_count_times_nineteen(_ODT) >= 0
    def test_divisible(self):
        assert odt_word_count_times_nineteen(_ODT) % 19 == 0
class TestOdtParagraphCountTimesNineteen:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_nineteen(_ODT), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_nineteen(_ODT) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_nineteen(_ODT) % 19 == 0
class TestFodpSlideCountTimesNineteen:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_nineteen(_FODP), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_nineteen(_FODP) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_nineteen(_FODP) % 19 == 0
class TestFodpWordCountTimesNineteen:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_nineteen(_FODP), int)
    def test_non_negative(self):
        assert fodp_word_count_times_nineteen(_FODP) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_nineteen(_FODP) % 19 == 0
