"""Sprint R477 — FODS/FODT/ODS/ODT/FODP _times_eight composite analytics tests."""
import pathlib, sys

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

SAMPLES = _REPO / "samples" / "by-format"

from src.python.fods.neutral_model import fods_sheet_count_times_eight, fods_total_cell_count_times_eight
from src.python.fodt.neutral_model import fodt_paragraph_count_times_eight, fodt_word_count_times_eight
from src.python.ods.ods_parser import ods_sheet_count_times_eight, ods_total_cell_count_times_eight
from src.python.odt.odt_parser import odt_word_count_times_eight, odt_paragraph_count_times_eight
from src.python.fodp.fodp_codec import fodp_slide_count_times_eight, fodp_word_count_times_eight
from src.python.fods import parse_fods_strict

class TestFodsSheetCountTimesEight:
    def test_returns_int(self):
        wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
        assert isinstance(fods_sheet_count_times_eight(wb), int)
    def test_non_negative(self):
        wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
        assert fods_sheet_count_times_eight(wb) >= 0
    def test_divisible(self):
        wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
        assert fods_sheet_count_times_eight(wb) % 8 == 0

class TestFodsTotalCellCountTimesEight:
    def test_returns_int(self):
        wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
        assert isinstance(fods_total_cell_count_times_eight(wb), int)
    def test_non_negative(self):
        wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
        assert fods_total_cell_count_times_eight(wb) >= 0
    def test_divisible(self):
        wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
        assert fods_total_cell_count_times_eight(wb) % 8 == 0

class TestFodtParagraphCountTimesEight:
    def test_returns_int(self):
        p = str(SAMPLES / "fodt" / "minimal-document.fodt")
        assert isinstance(fodt_paragraph_count_times_eight(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "fodt" / "minimal-document.fodt")
        assert fodt_paragraph_count_times_eight(p) >= 0
    def test_divisible(self):
        p = str(SAMPLES / "fodt" / "minimal-document.fodt")
        assert fodt_paragraph_count_times_eight(p) % 8 == 0

class TestFodtWordCountTimesEight:
    def test_returns_int(self):
        p = str(SAMPLES / "fodt" / "minimal-document.fodt")
        assert isinstance(fodt_word_count_times_eight(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "fodt" / "minimal-document.fodt")
        assert fodt_word_count_times_eight(p) >= 0
    def test_divisible(self):
        p = str(SAMPLES / "fodt" / "minimal-document.fodt")
        assert fodt_word_count_times_eight(p) % 8 == 0

class TestOdsSheetCountTimesEight:
    def test_returns_int(self):
        p = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
        assert isinstance(ods_sheet_count_times_eight(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
        assert ods_sheet_count_times_eight(p) >= 0
    def test_divisible(self):
        p = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
        assert ods_sheet_count_times_eight(p) % 8 == 0

class TestOdsTotalCellCountTimesEight:
    def test_returns_int(self):
        p = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
        assert isinstance(ods_total_cell_count_times_eight(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
        assert ods_total_cell_count_times_eight(p) >= 0
    def test_divisible(self):
        p = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
        assert ods_total_cell_count_times_eight(p) % 8 == 0

class TestOdtWordCountTimesEight:
    def test_returns_int(self):
        p = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
        assert isinstance(odt_word_count_times_eight(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
        assert odt_word_count_times_eight(p) >= 0
    def test_divisible(self):
        p = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
        assert odt_word_count_times_eight(p) % 8 == 0

class TestOdtParagraphCountTimesEight:
    def test_returns_int(self):
        p = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
        assert isinstance(odt_paragraph_count_times_eight(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
        assert odt_paragraph_count_times_eight(p) >= 0
    def test_divisible(self):
        p = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
        assert odt_paragraph_count_times_eight(p) % 8 == 0

class TestFodpSlideCountTimesEight:
    def test_returns_int(self):
        p = str(SAMPLES / "fodp" / "title-only.fodp")
        assert isinstance(fodp_slide_count_times_eight(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "fodp" / "title-only.fodp")
        assert fodp_slide_count_times_eight(p) >= 0
    def test_divisible(self):
        p = str(SAMPLES / "fodp" / "title-only.fodp")
        assert fodp_slide_count_times_eight(p) % 8 == 0

class TestFodpWordCountTimesEight:
    def test_returns_int(self):
        p = str(SAMPLES / "fodp" / "title-only.fodp")
        assert isinstance(fodp_word_count_times_eight(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "fodp" / "title-only.fodp")
        assert fodp_word_count_times_eight(p) >= 0
    def test_divisible(self):
        p = str(SAMPLES / "fodp" / "title-only.fodp")
        assert fodp_word_count_times_eight(p) % 8 == 0
