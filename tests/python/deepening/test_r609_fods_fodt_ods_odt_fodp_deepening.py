"""Sprint R609 — FODS/FODT/ODS/ODT/FODP _times_forty_one composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fods.neutral_model import fods_sheet_count_times_forty_one, fods_total_cell_count_times_forty_one
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_forty_one, fodt_word_count_times_forty_one
from src.python.ods.ods_parser import ods_sheet_count_times_forty_one, ods_total_cell_count_times_forty_one
from src.python.odt.odt_parser import odt_word_count_times_forty_one, odt_paragraph_count_times_forty_one
from src.python.fodp.fodp_codec import fodp_slide_count_times_forty_one, fodp_word_count_times_forty_one
SAMPLES = _REPO / "samples" / "by-format"
_wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

class TestFodsSheetCountTimesFortyOne:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_forty_one(_wb), int)
    def test_non_negative(self):
        assert fods_sheet_count_times_forty_one(_wb) >= 0
    def test_divisible(self):
        assert fods_sheet_count_times_forty_one(_wb) % 41 == 0
class TestFodsTotalCellCountTimesFortyOne:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_forty_one(_wb), int)
    def test_non_negative(self):
        assert fods_total_cell_count_times_forty_one(_wb) >= 0
    def test_divisible(self):
        assert fods_total_cell_count_times_forty_one(_wb) % 41 == 0
class TestFodtParagraphCountTimesFortyOne:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_forty_one(_FODT), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_forty_one(_FODT) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_forty_one(_FODT) % 41 == 0
class TestFodtWordCountTimesFortyOne:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_forty_one(_FODT), int)
    def test_non_negative(self):
        assert fodt_word_count_times_forty_one(_FODT) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_forty_one(_FODT) % 41 == 0
class TestOdsSheetCountTimesFortyOne:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_forty_one(_ODS), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_forty_one(_ODS) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_forty_one(_ODS) % 41 == 0
class TestOdsTotalCellCountTimesFortyOne:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_forty_one(_ODS), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_forty_one(_ODS) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_forty_one(_ODS) % 41 == 0
class TestOdtWordCountTimesFortyOne:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_forty_one(_ODT), int)
    def test_non_negative(self):
        assert odt_word_count_times_forty_one(_ODT) >= 0
    def test_divisible(self):
        assert odt_word_count_times_forty_one(_ODT) % 41 == 0
class TestOdtParagraphCountTimesFortyOne:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_forty_one(_ODT), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_forty_one(_ODT) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_forty_one(_ODT) % 41 == 0
class TestFodpSlideCountTimesFortyOne:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_forty_one(_FODP), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_forty_one(_FODP) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_forty_one(_FODP) % 41 == 0
class TestFodpWordCountTimesFortyOne:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_forty_one(_FODP), int)
    def test_non_negative(self):
        assert fodp_word_count_times_forty_one(_FODP) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_forty_one(_FODP) % 41 == 0
