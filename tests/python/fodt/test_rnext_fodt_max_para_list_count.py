"""Tests for fodt_max_paragraph_length and fodt_list_count."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodt.neutral_model import fodt_max_paragraph_length, fodt_list_count

_SAMPLES = _REPO / "samples" / "by-format" / "fodt"

_MINIMAL = _SAMPLES / "minimal-document.fodt"
_HEADINGS = _SAMPLES / "headings-and-paragraphs.fodt"
_LIST = _SAMPLES / "list-basic.fodt"
_TABLE = _SAMPLES / "table-basic.fodt"


class TestFodtMaxParagraphLength:
    def test_import(self):
        assert callable(fodt_max_paragraph_length)

    def test_returns_int(self):
        assert isinstance(fodt_max_paragraph_length(_MINIMAL), int)

    def test_nonnegative(self):
        assert fodt_max_paragraph_length(_MINIMAL) >= 0

    def test_headings_file_positive(self):
        result = fodt_max_paragraph_length(_HEADINGS)
        assert result >= 1

    def test_geq_average_length(self):
        from src.python.fodt.neutral_model import fodt_average_paragraph_length
        result = fodt_max_paragraph_length(_HEADINGS)
        avg = fodt_average_paragraph_length(_HEADINGS)
        assert result >= avg

    def test_table_file_nonnegative(self):
        result = fodt_max_paragraph_length(_TABLE)
        assert result >= 0

    def test_minimal_doc(self):
        result = fodt_max_paragraph_length(_MINIMAL)
        assert isinstance(result, int)

    def test_list_file_nonnegative(self):
        result = fodt_max_paragraph_length(_LIST)
        assert result >= 0


class TestFodtListCount:
    def test_import(self):
        assert callable(fodt_list_count)

    def test_returns_int(self):
        assert isinstance(fodt_list_count(_MINIMAL), int)

    def test_nonnegative(self):
        assert fodt_list_count(_MINIMAL) >= 0

    def test_list_file_has_lists(self):
        result = fodt_list_count(_LIST)
        assert result >= 1

    def test_minimal_may_have_zero(self):
        result = fodt_list_count(_MINIMAL)
        assert isinstance(result, int)

    def test_headings_file_nonnegative(self):
        assert fodt_list_count(_HEADINGS) >= 0

    def test_table_file_nonnegative(self):
        assert fodt_list_count(_TABLE) >= 0

    def test_return_type_is_int(self):
        assert type(fodt_list_count(_LIST)) is int
