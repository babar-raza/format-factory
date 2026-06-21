"""Sprint R685 — FODS/FODT/ODS/ODT/FODP _times_sixty composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fods.neutral_model import fods_sheet_count_times_sixty, fods_total_cell_count_times_sixty
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_sixty, fodt_word_count_times_sixty
from src.python.ods.ods_parser import ods_sheet_count_times_sixty, ods_total_cell_count_times_sixty
from src.python.odt.odt_parser import odt_word_count_times_sixty, odt_paragraph_count_times_sixty
from src.python.fodp.fodp_codec import fodp_slide_count_times_sixty, fodp_word_count_times_sixty
SAMPLES = _REPO / "samples" / "by-format"
_wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

class TestFodsSheetCountTimesSixty:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_sixty(_wb), int)
    def test_non_negative(self):
        assert fods_sheet_count_times_sixty(_wb) >= 0
    def test_divisible(self):
        assert fods_sheet_count_times_sixty(_wb) % 60 == 0
class TestFodsTotalCellCountTimesSixty:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_sixty(_wb), int)
    def test_non_negative(self):
        assert fods_total_cell_count_times_sixty(_wb) >= 0
    def test_divisible(self):
        assert fods_total_cell_count_times_sixty(_wb) % 60 == 0
class TestFodtParagraphCountTimesSixty:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_sixty(_FODT), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_sixty(_FODT) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_sixty(_FODT) % 60 == 0
class TestFodtWordCountTimesSixty:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_sixty(_FODT), int)
    def test_non_negative(self):
        assert fodt_word_count_times_sixty(_FODT) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_sixty(_FODT) % 60 == 0
class TestOdsSheetCountTimesSixty:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_sixty(_ODS), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_sixty(_ODS) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_sixty(_ODS) % 60 == 0
class TestOdsTotalCellCountTimesSixty:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_sixty(_ODS), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_sixty(_ODS) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_sixty(_ODS) % 60 == 0
class TestOdtWordCountTimesSixty:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_sixty(_ODT), int)
    def test_non_negative(self):
        assert odt_word_count_times_sixty(_ODT) >= 0
    def test_divisible(self):
        assert odt_word_count_times_sixty(_ODT) % 60 == 0
class TestOdtParagraphCountTimesSixty:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_sixty(_ODT), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_sixty(_ODT) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_sixty(_ODT) % 60 == 0
class TestFodpSlideCountTimesSixty:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_sixty(_FODP), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_sixty(_FODP) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_sixty(_FODP) % 60 == 0
class TestFodpWordCountTimesSixty:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_sixty(_FODP), int)
    def test_non_negative(self):
        assert fodp_word_count_times_sixty(_FODP) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_sixty(_FODP) % 60 == 0
