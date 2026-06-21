"""Sprint R453 — FODS/FODT/ODS/ODT/FODP round 9 deepening tests."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods import fods_total_cell_count_times_three, fods_file_size_times_three, fods_total_cell_count, fods_file_size_bytes, parse_fods_strict
from src.python.fodt import fodt_block_count_times_three, fodt_file_size_times_three, fodt_file_size_bytes
from src.python.fodt.neutral_model import fodt_block_count
from src.python.ods import ods_total_row_count_times_three, ods_file_size_times_three, ods_total_row_count, ods_file_size_bytes
from src.python.odt import odt_word_count_times_three, odt_paragraph_count_times_three, odt_word_count, odt_paragraph_count
from src.python.fodp import fodp_word_count_times_three, fodp_file_size_times_three, fodp_word_count, fodp_file_size_bytes

SAMPLES = _REPO / "samples" / "by-format"
FODS_SAMPLE = SAMPLES / "fods" / "minimal-spreadsheet.fods"
FODT_SAMPLE = SAMPLES / "fodt" / "minimal-document.fodt"
ODS_SAMPLE = SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods"
ODT_SAMPLE = SAMPLES / "odt" / "valid" / "minimal-document.odt"
FODP_SAMPLE = SAMPLES / "fodp" / "title-only.fodp"


class TestFodsTotalCellCountTimesThree:
    def test_returns_int(self):
        wb = parse_fods_strict(FODS_SAMPLE)
        assert isinstance(fods_total_cell_count_times_three(wb), int)
    def test_is_triple(self):
        wb = parse_fods_strict(FODS_SAMPLE)
        assert fods_total_cell_count_times_three(wb) == fods_total_cell_count(wb) * 3
    def test_non_negative(self):
        wb = parse_fods_strict(FODS_SAMPLE)
        assert fods_total_cell_count_times_three(wb) >= 0


class TestFodsFileSizeTimesThree:
    def test_returns_int(self):
        assert isinstance(fods_file_size_times_three(FODS_SAMPLE), int)
    def test_is_triple(self):
        assert fods_file_size_times_three(FODS_SAMPLE) == fods_file_size_bytes(FODS_SAMPLE) * 3
    def test_non_negative(self):
        assert fods_file_size_times_three(FODS_SAMPLE) >= 0


class TestFodtBlockCountTimesThree:
    def test_returns_int(self):
        assert isinstance(fodt_block_count_times_three(FODT_SAMPLE), int)
    def test_is_triple(self):
        assert fodt_block_count_times_three(FODT_SAMPLE) == fodt_block_count(FODT_SAMPLE) * 3
    def test_non_negative(self):
        assert fodt_block_count_times_three(FODT_SAMPLE) >= 0


class TestFodtFileSizeTimesThree:
    def test_returns_int(self):
        assert isinstance(fodt_file_size_times_three(FODT_SAMPLE), int)
    def test_is_triple(self):
        assert fodt_file_size_times_three(FODT_SAMPLE) == fodt_file_size_bytes(FODT_SAMPLE) * 3
    def test_non_negative(self):
        assert fodt_file_size_times_three(FODT_SAMPLE) >= 0


class TestOdsTotalRowCountTimesThree:
    def test_returns_int(self):
        assert isinstance(ods_total_row_count_times_three(ODS_SAMPLE), int)
    def test_is_triple(self):
        assert ods_total_row_count_times_three(ODS_SAMPLE) == ods_total_row_count(ODS_SAMPLE) * 3
    def test_non_negative(self):
        assert ods_total_row_count_times_three(ODS_SAMPLE) >= 0


class TestOdsFileSizeTimesThree:
    def test_returns_int(self):
        assert isinstance(ods_file_size_times_three(ODS_SAMPLE), int)
    def test_is_triple(self):
        assert ods_file_size_times_three(ODS_SAMPLE) == ods_file_size_bytes(ODS_SAMPLE) * 3
    def test_non_negative(self):
        assert ods_file_size_times_three(ODS_SAMPLE) >= 0


class TestOdtWordCountTimesThree:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_three(ODT_SAMPLE), int)
    def test_is_triple(self):
        assert odt_word_count_times_three(ODT_SAMPLE) == odt_word_count(ODT_SAMPLE) * 3
    def test_non_negative(self):
        assert odt_word_count_times_three(ODT_SAMPLE) >= 0


class TestOdtParagraphCountTimesThree:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_three(ODT_SAMPLE), int)
    def test_is_triple(self):
        assert odt_paragraph_count_times_three(ODT_SAMPLE) == odt_paragraph_count(ODT_SAMPLE) * 3
    def test_non_negative(self):
        assert odt_paragraph_count_times_three(ODT_SAMPLE) >= 0


class TestFodpWordCountTimesThree:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_three(FODP_SAMPLE), int)
    def test_is_triple(self):
        assert fodp_word_count_times_three(FODP_SAMPLE) == fodp_word_count(FODP_SAMPLE) * 3
    def test_non_negative(self):
        assert fodp_word_count_times_three(FODP_SAMPLE) >= 0


class TestFodpFileSizeTimesThree:
    def test_returns_int(self):
        assert isinstance(fodp_file_size_times_three(FODP_SAMPLE), int)
    def test_is_triple(self):
        assert fodp_file_size_times_three(FODP_SAMPLE) == fodp_file_size_bytes(FODP_SAMPLE) * 3
    def test_non_negative(self):
        assert fodp_file_size_times_three(FODP_SAMPLE) >= 0
