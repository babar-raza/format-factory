"""Sprint R605 — FODS/FODT/ODS/ODT/FODP _times_forty composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fods.neutral_model import fods_sheet_count_times_forty, fods_total_cell_count_times_forty
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_forty, fodt_word_count_times_forty
from src.python.ods.ods_parser import ods_sheet_count_times_forty, ods_total_cell_count_times_forty
from src.python.odt.odt_parser import odt_word_count_times_forty, odt_paragraph_count_times_forty
from src.python.fodp.fodp_codec import fodp_slide_count_times_forty, fodp_word_count_times_forty
SAMPLES = _REPO / "samples" / "by-format"
_wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

class TestFodsSheetCountTimesForty:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_forty(_wb), int)
    def test_non_negative(self):
        assert fods_sheet_count_times_forty(_wb) >= 0
    def test_divisible(self):
        assert fods_sheet_count_times_forty(_wb) % 40 == 0
class TestFodsTotalCellCountTimesForty:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_forty(_wb), int)
    def test_non_negative(self):
        assert fods_total_cell_count_times_forty(_wb) >= 0
    def test_divisible(self):
        assert fods_total_cell_count_times_forty(_wb) % 40 == 0
class TestFodtParagraphCountTimesForty:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_forty(_FODT), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_forty(_FODT) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_forty(_FODT) % 40 == 0
class TestFodtWordCountTimesForty:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_forty(_FODT), int)
    def test_non_negative(self):
        assert fodt_word_count_times_forty(_FODT) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_forty(_FODT) % 40 == 0
class TestOdsSheetCountTimesForty:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_forty(_ODS), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_forty(_ODS) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_forty(_ODS) % 40 == 0
class TestOdsTotalCellCountTimesForty:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_forty(_ODS), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_forty(_ODS) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_forty(_ODS) % 40 == 0
class TestOdtWordCountTimesForty:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_forty(_ODT), int)
    def test_non_negative(self):
        assert odt_word_count_times_forty(_ODT) >= 0
    def test_divisible(self):
        assert odt_word_count_times_forty(_ODT) % 40 == 0
class TestOdtParagraphCountTimesForty:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_forty(_ODT), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_forty(_ODT) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_forty(_ODT) % 40 == 0
class TestFodpSlideCountTimesForty:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_forty(_FODP), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_forty(_FODP) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_forty(_FODP) % 40 == 0
class TestFodpWordCountTimesForty:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_forty(_FODP), int)
    def test_non_negative(self):
        assert fodp_word_count_times_forty(_FODP) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_forty(_FODP) % 40 == 0
