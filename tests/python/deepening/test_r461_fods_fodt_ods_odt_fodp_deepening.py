"""Sprint R461 — FODS/FODT/ODS/ODT/FODP round 12 deepening (_times_four continued)."""
import os, sys, pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

SAMPLES = _REPO / "samples" / "by-format"

from src.python.fods import parse_fods_strict, fods_file_size_times_four, fods_total_row_count_times_four
from src.python.fodt import fodt_file_size_times_four
from src.python.fodt.neutral_model import fodt_block_count_times_four
from src.python.ods import ods_file_size_times_four, ods_total_row_count_times_four
from src.python.odt import odt_file_size_times_four, odt_heading_count_times_four
from src.python.fodp import fodp_file_size_times_four, fodp_total_text_chars_times_four


# --- FODS ---
class TestFodsFileSizeTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "fods" / "minimal-spreadsheet.fods")
        assert isinstance(fods_file_size_times_four(p), int)

    def test_equals_four_times_size(self):
        p = str(SAMPLES / "fods" / "minimal-spreadsheet.fods")
        assert fods_file_size_times_four(p) == os.path.getsize(p) * 4

    def test_positive(self):
        p = str(SAMPLES / "fods" / "minimal-spreadsheet.fods")
        assert fods_file_size_times_four(p) > 0


class TestFodsTotalRowCountTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "fods" / "minimal-spreadsheet.fods")
        wb = parse_fods_strict(p)
        assert isinstance(fods_total_row_count_times_four(wb), int)

    def test_non_negative(self):
        p = str(SAMPLES / "fods" / "minimal-spreadsheet.fods")
        wb = parse_fods_strict(p)
        assert fods_total_row_count_times_four(wb) >= 0

    def test_divisible_by_four(self):
        p = str(SAMPLES / "fods" / "minimal-spreadsheet.fods")
        wb = parse_fods_strict(p)
        assert fods_total_row_count_times_four(wb) % 4 == 0


# --- FODT ---
class TestFodtFileSizeTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "fodt" / "minimal-document.fodt")
        assert isinstance(fodt_file_size_times_four(p), int)

    def test_equals_four_times_size(self):
        p = str(SAMPLES / "fodt" / "minimal-document.fodt")
        assert fodt_file_size_times_four(p) == os.path.getsize(p) * 4

    def test_positive(self):
        p = str(SAMPLES / "fodt" / "minimal-document.fodt")
        assert fodt_file_size_times_four(p) > 0


class TestFodtBlockCountTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "fodt" / "minimal-document.fodt")
        assert isinstance(fodt_block_count_times_four(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "fodt" / "minimal-document.fodt")
        assert fodt_block_count_times_four(p) >= 0

    def test_divisible_by_four(self):
        p = str(SAMPLES / "fodt" / "minimal-document.fodt")
        assert fodt_block_count_times_four(p) % 4 == 0


# --- ODS ---
class TestOdsFileSizeTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
        assert isinstance(ods_file_size_times_four(p), int)

    def test_equals_four_times_size(self):
        p = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
        assert ods_file_size_times_four(p) == os.path.getsize(p) * 4

    def test_positive(self):
        p = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
        assert ods_file_size_times_four(p) > 0


class TestOdsTotalRowCountTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
        assert isinstance(ods_total_row_count_times_four(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
        assert ods_total_row_count_times_four(p) >= 0

    def test_divisible_by_four(self):
        p = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
        assert ods_total_row_count_times_four(p) % 4 == 0


# --- ODT ---
class TestOdtFileSizeTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
        assert isinstance(odt_file_size_times_four(p), int)

    def test_equals_four_times_size(self):
        p = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
        assert odt_file_size_times_four(p) == os.path.getsize(p) * 4

    def test_positive(self):
        p = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
        assert odt_file_size_times_four(p) > 0


class TestOdtHeadingCountTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
        assert isinstance(odt_heading_count_times_four(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
        assert odt_heading_count_times_four(p) >= 0

    def test_divisible_by_four(self):
        p = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
        assert odt_heading_count_times_four(p) % 4 == 0


# --- FODP ---
class TestFodpFileSizeTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "fodp" / "title-only.fodp")
        assert isinstance(fodp_file_size_times_four(p), int)

    def test_equals_four_times_size(self):
        p = str(SAMPLES / "fodp" / "title-only.fodp")
        assert fodp_file_size_times_four(p) == os.path.getsize(p) * 4

    def test_positive(self):
        p = str(SAMPLES / "fodp" / "title-only.fodp")
        assert fodp_file_size_times_four(p) > 0


class TestFodpTotalTextCharsTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "fodp" / "title-only.fodp")
        assert isinstance(fodp_total_text_chars_times_four(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "fodp" / "title-only.fodp")
        assert fodp_total_text_chars_times_four(p) >= 0

    def test_divisible_by_four(self):
        p = str(SAMPLES / "fodp" / "title-only.fodp")
        assert fodp_total_text_chars_times_four(p) % 4 == 0
