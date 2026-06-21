"""Sprint R525 — FODS/FODT/ODS/ODT/FODP _times_twenty composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fods.neutral_model import fods_sheet_count_times_twenty, fods_total_cell_count_times_twenty
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_twenty, fodt_word_count_times_twenty
from src.python.ods.ods_parser import ods_sheet_count_times_twenty, ods_total_cell_count_times_twenty
from src.python.odt.odt_parser import odt_word_count_times_twenty, odt_paragraph_count_times_twenty
from src.python.fodp.fodp_codec import fodp_slide_count_times_twenty, fodp_word_count_times_twenty
SAMPLES = _REPO / "samples" / "by-format"
_wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

class TestFodsSheetCountTimesTwenty:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_twenty(_wb), int)
    def test_non_negative(self):
        assert fods_sheet_count_times_twenty(_wb) >= 0
    def test_divisible(self):
        assert fods_sheet_count_times_twenty(_wb) % 20 == 0
class TestFodsTotalCellCountTimesTwenty:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_twenty(_wb), int)
    def test_non_negative(self):
        assert fods_total_cell_count_times_twenty(_wb) >= 0
    def test_divisible(self):
        assert fods_total_cell_count_times_twenty(_wb) % 20 == 0
class TestFodtParagraphCountTimesTwenty:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_twenty(_FODT), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_twenty(_FODT) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_twenty(_FODT) % 20 == 0
class TestFodtWordCountTimesTwenty:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_twenty(_FODT), int)
    def test_non_negative(self):
        assert fodt_word_count_times_twenty(_FODT) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_twenty(_FODT) % 20 == 0
class TestOdsSheetCountTimesTwenty:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_twenty(_ODS), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_twenty(_ODS) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_twenty(_ODS) % 20 == 0
class TestOdsTotalCellCountTimesTwenty:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_twenty(_ODS), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_twenty(_ODS) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_twenty(_ODS) % 20 == 0
class TestOdtWordCountTimesTwenty:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_twenty(_ODT), int)
    def test_non_negative(self):
        assert odt_word_count_times_twenty(_ODT) >= 0
    def test_divisible(self):
        assert odt_word_count_times_twenty(_ODT) % 20 == 0
class TestOdtParagraphCountTimesTwenty:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_twenty(_ODT), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_twenty(_ODT) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_twenty(_ODT) % 20 == 0
class TestFodpSlideCountTimesTwenty:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_twenty(_FODP), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_twenty(_FODP) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_twenty(_FODP) % 20 == 0
class TestFodpWordCountTimesTwenty:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_twenty(_FODP), int)
    def test_non_negative(self):
        assert fodp_word_count_times_twenty(_FODP) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_twenty(_FODP) % 20 == 0
