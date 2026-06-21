"""Sprint R505 — FODS/FODT/ODS/ODT/FODP _times_fifteen composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fods.neutral_model import fods_sheet_count_times_fifteen, fods_total_cell_count_times_fifteen
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_fifteen, fodt_word_count_times_fifteen
from src.python.ods.ods_parser import ods_sheet_count_times_fifteen, ods_total_cell_count_times_fifteen
from src.python.odt.odt_parser import odt_word_count_times_fifteen, odt_paragraph_count_times_fifteen
from src.python.fodp.fodp_codec import fodp_slide_count_times_fifteen, fodp_word_count_times_fifteen
SAMPLES = _REPO / "samples" / "by-format"
_wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

class TestFodsSheetCountTimesFifteen:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_fifteen(_wb), int)
    def test_non_negative(self):
        assert fods_sheet_count_times_fifteen(_wb) >= 0
    def test_divisible(self):
        assert fods_sheet_count_times_fifteen(_wb) % 15 == 0

class TestFodsTotalCellCountTimesFifteen:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_fifteen(_wb), int)
    def test_non_negative(self):
        assert fods_total_cell_count_times_fifteen(_wb) >= 0
    def test_divisible(self):
        assert fods_total_cell_count_times_fifteen(_wb) % 15 == 0

class TestFodtParagraphCountTimesFifteen:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_fifteen(_FODT), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_fifteen(_FODT) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_fifteen(_FODT) % 15 == 0

class TestFodtWordCountTimesFifteen:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_fifteen(_FODT), int)
    def test_non_negative(self):
        assert fodt_word_count_times_fifteen(_FODT) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_fifteen(_FODT) % 15 == 0

class TestOdsSheetCountTimesFifteen:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_fifteen(_ODS), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_fifteen(_ODS) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_fifteen(_ODS) % 15 == 0

class TestOdsTotalCellCountTimesFifteen:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_fifteen(_ODS), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_fifteen(_ODS) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_fifteen(_ODS) % 15 == 0

class TestOdtWordCountTimesFifteen:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_fifteen(_ODT), int)
    def test_non_negative(self):
        assert odt_word_count_times_fifteen(_ODT) >= 0
    def test_divisible(self):
        assert odt_word_count_times_fifteen(_ODT) % 15 == 0

class TestOdtParagraphCountTimesFifteen:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_fifteen(_ODT), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_fifteen(_ODT) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_fifteen(_ODT) % 15 == 0

class TestFodpSlideCountTimesFifteen:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_fifteen(_FODP), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_fifteen(_FODP) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_fifteen(_FODP) % 15 == 0

class TestFodpWordCountTimesFifteen:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_fifteen(_FODP), int)
    def test_non_negative(self):
        assert fodp_word_count_times_fifteen(_FODP) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_fifteen(_FODP) % 15 == 0
