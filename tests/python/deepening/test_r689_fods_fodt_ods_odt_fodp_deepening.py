"""Sprint R689 — FODS/FODT/ODS/ODT/FODP _times_sixty_one composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fods.neutral_model import fods_sheet_count_times_sixty_one, fods_total_cell_count_times_sixty_one
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_sixty_one, fodt_word_count_times_sixty_one
from src.python.ods.ods_parser import ods_sheet_count_times_sixty_one, ods_total_cell_count_times_sixty_one
from src.python.odt.odt_parser import odt_word_count_times_sixty_one, odt_paragraph_count_times_sixty_one
from src.python.fodp.fodp_codec import fodp_slide_count_times_sixty_one, fodp_word_count_times_sixty_one
SAMPLES = _REPO / "samples" / "by-format"
_wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

class TestFodsSheetCountTimesSixtyOne:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_sixty_one(_wb), int)
    def test_non_negative(self):
        assert fods_sheet_count_times_sixty_one(_wb) >= 0
    def test_divisible(self):
        assert fods_sheet_count_times_sixty_one(_wb) % 61 == 0
class TestFodsTotalCellCountTimesSixtyOne:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_sixty_one(_wb), int)
    def test_non_negative(self):
        assert fods_total_cell_count_times_sixty_one(_wb) >= 0
    def test_divisible(self):
        assert fods_total_cell_count_times_sixty_one(_wb) % 61 == 0
class TestFodtParagraphCountTimesSixtyOne:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_sixty_one(_FODT), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_sixty_one(_FODT) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_sixty_one(_FODT) % 61 == 0
class TestFodtWordCountTimesSixtyOne:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_sixty_one(_FODT), int)
    def test_non_negative(self):
        assert fodt_word_count_times_sixty_one(_FODT) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_sixty_one(_FODT) % 61 == 0
class TestOdsSheetCountTimesSixtyOne:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_sixty_one(_ODS), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_sixty_one(_ODS) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_sixty_one(_ODS) % 61 == 0
class TestOdsTotalCellCountTimesSixtyOne:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_sixty_one(_ODS), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_sixty_one(_ODS) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_sixty_one(_ODS) % 61 == 0
class TestOdtWordCountTimesSixtyOne:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_sixty_one(_ODT), int)
    def test_non_negative(self):
        assert odt_word_count_times_sixty_one(_ODT) >= 0
    def test_divisible(self):
        assert odt_word_count_times_sixty_one(_ODT) % 61 == 0
class TestOdtParagraphCountTimesSixtyOne:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_sixty_one(_ODT), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_sixty_one(_ODT) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_sixty_one(_ODT) % 61 == 0
class TestFodpSlideCountTimesSixtyOne:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_sixty_one(_FODP), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_sixty_one(_FODP) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_sixty_one(_FODP) % 61 == 0
class TestFodpWordCountTimesSixtyOne:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_sixty_one(_FODP), int)
    def test_non_negative(self):
        assert fodp_word_count_times_sixty_one(_FODP) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_sixty_one(_FODP) % 61 == 0
