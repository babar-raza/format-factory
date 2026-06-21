"""Tests for fodt_inline_count (Sprint 40 batch 3).

Closes:
  GAP-FODT-FOSS-FODT_INLINE_-001  (Fodt Inline Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodt import fodt_inline_count

_DIR = _REPO / "samples" / "by-format" / "fodt"
_MINIMAL = str(_DIR / "minimal-document.fodt")
_HEADINGS = str(_DIR / "headings-and-paragraphs.fodt")
_TABLE = str(_DIR / "table-basic.fodt")


class TestFodtInlineCount:
    def test_return_type(self):
        assert isinstance(fodt_inline_count(_MINIMAL), int)

    def test_zero_for_minimal_document(self):
        assert fodt_inline_count(_MINIMAL) == 0

    def test_zero_for_headings_and_paragraphs(self):
        assert fodt_inline_count(_HEADINGS) == 0

    def test_zero_for_table_basic(self):
        assert fodt_inline_count(_TABLE) == 0

    def test_nonnegative(self):
        assert fodt_inline_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert fodt_inline_count(_MINIMAL) == fodt_inline_count(_MINIMAL)
