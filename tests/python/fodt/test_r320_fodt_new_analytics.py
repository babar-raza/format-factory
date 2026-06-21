"""
test_r320_fodt_new_analytics.py
Sprint 56 — 5 new FODT analytics functions.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt import (
    fodt_file_size_bytes,
    fodt_avg_heading_length,
    fodt_unique_block_type_count,
    fodt_max_paragraph_length,
    fodt_avg_paragraph_length,
)

_VALID = _REPO / "samples" / "by-format" / "fodt"
_MINIMAL = str(_VALID / "minimal-document.fodt")
_HEADINGS = str(_VALID / "headings-and-paragraphs.fodt")
_TABLE = str(_VALID / "table-basic.fodt")
_LIST = str(_VALID / "list-basic.fodt")


# --- fodt_file_size_bytes ---

class TestFodtFileSizeBytes:
    def test_minimal_positive(self):
        assert fodt_file_size_bytes(_MINIMAL) > 0

    def test_headings_positive(self):
        assert fodt_file_size_bytes(_HEADINGS) > 0

    def test_returns_int(self):
        assert isinstance(fodt_file_size_bytes(_MINIMAL), int)

    def test_table_positive(self):
        assert fodt_file_size_bytes(_TABLE) > 0

    def test_list_positive(self):
        assert fodt_file_size_bytes(_LIST) > 0


# --- fodt_avg_heading_length ---

class TestFodtAvgHeadingLength:
    def test_returns_float(self):
        assert isinstance(fodt_avg_heading_length(_HEADINGS), float)

    def test_headings_positive(self):
        assert fodt_avg_heading_length(_HEADINGS) > 0.0

    def test_minimal_non_negative(self):
        assert fodt_avg_heading_length(_MINIMAL) >= 0.0

    def test_table_non_negative(self):
        assert fodt_avg_heading_length(_TABLE) >= 0.0

    def test_list_non_negative(self):
        assert fodt_avg_heading_length(_LIST) >= 0.0


# --- fodt_unique_block_type_count ---

class TestFodtUniqueBlockTypeCount:
    def test_returns_int(self):
        assert isinstance(fodt_unique_block_type_count(_MINIMAL), int)

    def test_minimal_at_least_one(self):
        assert fodt_unique_block_type_count(_MINIMAL) >= 1

    def test_headings_at_least_one(self):
        assert fodt_unique_block_type_count(_HEADINGS) >= 1

    def test_table_at_least_one(self):
        assert fodt_unique_block_type_count(_TABLE) >= 1

    def test_list_at_least_one(self):
        assert fodt_unique_block_type_count(_LIST) >= 1


# --- fodt_max_paragraph_length ---

class TestFodtMaxParagraphLength:
    def test_returns_int(self):
        assert isinstance(fodt_max_paragraph_length(_HEADINGS), int)

    def test_headings_non_negative(self):
        assert fodt_max_paragraph_length(_HEADINGS) >= 0

    def test_minimal_non_negative(self):
        assert fodt_max_paragraph_length(_MINIMAL) >= 0

    def test_table_non_negative(self):
        assert fodt_max_paragraph_length(_TABLE) >= 0

    def test_list_non_negative(self):
        assert fodt_max_paragraph_length(_LIST) >= 0


# --- fodt_avg_paragraph_length ---

class TestFodtAvgParagraphLength:
    def test_returns_float(self):
        assert isinstance(fodt_avg_paragraph_length(_HEADINGS), float)

    def test_headings_non_negative(self):
        assert fodt_avg_paragraph_length(_HEADINGS) >= 0.0

    def test_minimal_non_negative(self):
        assert fodt_avg_paragraph_length(_MINIMAL) >= 0.0

    def test_avg_le_max(self):
        assert fodt_avg_paragraph_length(_HEADINGS) <= fodt_max_paragraph_length(_HEADINGS) + 1

    def test_list_non_negative(self):
        assert fodt_avg_paragraph_length(_LIST) >= 0.0
