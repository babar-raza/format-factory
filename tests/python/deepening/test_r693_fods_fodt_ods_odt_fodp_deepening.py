"""Sprint R693 — FODS/FODT/ODS/ODT/FODP _times_sixty_two composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fods.neutral_model import fods_sheet_count_times_sixty_two, fods_total_cell_count_times_sixty_two
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_sixty_two, fodt_word_count_times_sixty_two
from src.python.ods.ods_parser import ods_sheet_count_times_sixty_two, ods_total_cell_count_times_sixty_two
from src.python.odt.odt_parser import odt_word_count_times_sixty_two, odt_paragraph_count_times_sixty_two
from src.python.fodp.fodp_codec import fodp_slide_count_times_sixty_two, fodp_word_count_times_sixty_two
SAMPLES = _REPO / "samples" / "by-format"
_wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

class TestFodsSheetCountTimesSixtyTwo:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_sixty_two(_wb), int)
    def test_non_negative(self):
        assert fods_sheet_count_times_sixty_two(_wb) >= 0
    def test_divisible(self):
        assert fods_sheet_count_times_sixty_two(_wb) % 62 == 0
class TestFodsTotalCellCountTimesSixtyTwo:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_sixty_two(_wb), int)
    def test_non_negative(self):
        assert fods_total_cell_count_times_sixty_two(_wb) >= 0
    def test_divisible(self):
        assert fods_total_cell_count_times_sixty_two(_wb) % 62 == 0
class TestFodtParagraphCountTimesSixtyTwo:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_sixty_two(_FODT), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_sixty_two(_FODT) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_sixty_two(_FODT) % 62 == 0
class TestFodtWordCountTimesSixtyTwo:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_sixty_two(_FODT), int)
    def test_non_negative(self):
        assert fodt_word_count_times_sixty_two(_FODT) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_sixty_two(_FODT) % 62 == 0
class TestOdsSheetCountTimesSixtyTwo:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_sixty_two(_ODS), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_sixty_two(_ODS) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_sixty_two(_ODS) % 62 == 0
class TestOdsTotalCellCountTimesSixtyTwo:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_sixty_two(_ODS), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_sixty_two(_ODS) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_sixty_two(_ODS) % 62 == 0
class TestOdtWordCountTimesSixtyTwo:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_sixty_two(_ODT), int)
    def test_non_negative(self):
        assert odt_word_count_times_sixty_two(_ODT) >= 0
    def test_divisible(self):
        assert odt_word_count_times_sixty_two(_ODT) % 62 == 0
class TestOdtParagraphCountTimesSixtyTwo:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_sixty_two(_ODT), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_sixty_two(_ODT) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_sixty_two(_ODT) % 62 == 0
class TestFodpSlideCountTimesSixtyTwo:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_sixty_two(_FODP), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_sixty_two(_FODP) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_sixty_two(_FODP) % 62 == 0
class TestFodpWordCountTimesSixtyTwo:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_sixty_two(_FODP), int)
    def test_non_negative(self):
        assert fodp_word_count_times_sixty_two(_FODP) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_sixty_two(_FODP) % 62 == 0
