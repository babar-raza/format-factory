"""Tests for FODT Sprint 45 gap closure.

Closes:
  GAP-FODT-FOSS-FODT_FILE_SI-001  (Fodt File Size Bytes)
  GAP-FODT-FOSS-FODT_AVG_PAR-001  (Fodt Avg Paragraph Length)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodt import fodt_file_size_bytes, fodt_avg_paragraph_length

_DIR = _REPO / "samples" / "by-format" / "fodt"
_MINIMAL = str(_DIR / "minimal-document.fodt")
_HEADINGS = str(_DIR / "headings-and-paragraphs.fodt")
_LIST = str(_DIR / "list-basic.fodt")


class TestFodtFileSizeBytes:
    def test_return_type(self):
        assert isinstance(fodt_file_size_bytes(_MINIMAL), int)

    def test_exact_1030_for_minimal(self):
        assert fodt_file_size_bytes(_MINIMAL) == 1030

    def test_exact_2063_for_headings(self):
        assert fodt_file_size_bytes(_HEADINGS) == 2063

    def test_exact_2492_for_list(self):
        assert fodt_file_size_bytes(_LIST) == 2492

    def test_positive(self):
        assert fodt_file_size_bytes(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert fodt_file_size_bytes(_MINIMAL) == fodt_file_size_bytes(_MINIMAL)


class TestFodtAvgParagraphLength:
    def test_return_type(self):
        assert isinstance(fodt_avg_paragraph_length(_MINIMAL), (int, float))

    def test_exact_13_for_minimal(self):
        assert fodt_avg_paragraph_length(_MINIMAL) == 13.0

    def test_exact_21_for_list(self):
        assert fodt_avg_paragraph_length(_LIST) == 21.0

    def test_nonnegative(self):
        assert fodt_avg_paragraph_length(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert fodt_avg_paragraph_length(_MINIMAL) == fodt_avg_paragraph_length(_MINIMAL)
