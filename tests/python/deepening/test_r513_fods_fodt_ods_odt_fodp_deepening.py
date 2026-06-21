"""Sprint R513 — FODS/FODT/ODS/ODT/FODP _times_seventeen composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fods.neutral_model import fods_sheet_count_times_seventeen, fods_total_cell_count_times_seventeen
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_seventeen, fodt_word_count_times_seventeen
from src.python.ods.ods_parser import ods_sheet_count_times_seventeen, ods_total_cell_count_times_seventeen
from src.python.odt.odt_parser import odt_word_count_times_seventeen, odt_paragraph_count_times_seventeen
from src.python.fodp.fodp_codec import fodp_slide_count_times_seventeen, fodp_word_count_times_seventeen
SAMPLES = _REPO / "samples" / "by-format"
_wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

class TestFodsSheetCountTimesSeventeen:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_seventeen(_wb), int)
    def test_non_negative(self):
        assert fods_sheet_count_times_seventeen(_wb) >= 0
    def test_divisible(self):
        assert fods_sheet_count_times_seventeen(_wb) % 17 == 0
class TestFodsTotalCellCountTimesSeventeen:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_seventeen(_wb), int)
    def test_non_negative(self):
        assert fods_total_cell_count_times_seventeen(_wb) >= 0
    def test_divisible(self):
        assert fods_total_cell_count_times_seventeen(_wb) % 17 == 0
class TestFodtParagraphCountTimesSeventeen:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_seventeen(_FODT), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_seventeen(_FODT) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_seventeen(_FODT) % 17 == 0
class TestFodtWordCountTimesSeventeen:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_seventeen(_FODT), int)
    def test_non_negative(self):
        assert fodt_word_count_times_seventeen(_FODT) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_seventeen(_FODT) % 17 == 0
class TestOdsSheetCountTimesSeventeen:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_seventeen(_ODS), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_seventeen(_ODS) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_seventeen(_ODS) % 17 == 0
class TestOdsTotalCellCountTimesSeventeen:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_seventeen(_ODS), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_seventeen(_ODS) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_seventeen(_ODS) % 17 == 0
class TestOdtWordCountTimesSeventeen:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_seventeen(_ODT), int)
    def test_non_negative(self):
        assert odt_word_count_times_seventeen(_ODT) >= 0
    def test_divisible(self):
        assert odt_word_count_times_seventeen(_ODT) % 17 == 0
class TestOdtParagraphCountTimesSeventeen:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_seventeen(_ODT), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_seventeen(_ODT) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_seventeen(_ODT) % 17 == 0
class TestFodpSlideCountTimesSeventeen:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_seventeen(_FODP), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_seventeen(_FODP) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_seventeen(_FODP) % 17 == 0
class TestFodpWordCountTimesSeventeen:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_seventeen(_FODP), int)
    def test_non_negative(self):
        assert fodp_word_count_times_seventeen(_FODP) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_seventeen(_FODP) % 17 == 0
