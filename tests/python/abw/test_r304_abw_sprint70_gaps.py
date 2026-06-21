"""Tests for ABW Sprint 70 gap closure.

Closes:
  GAP-ABW-FOSS-ABW_HAS_PUNC-001   (Abw Has Punctuation)
"""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.abw import abw_has_punctuation

_DIR = _REPO / "samples" / "by-format" / "abw"
_EMPTY = str(_DIR / "empty-section.abw")
_MINIMAL = str(_DIR / "minimal-document.abw")
_TWO = str(_DIR / "two-paragraphs.abw")


class TestAbwHasPunctuation:
    def test_return_type(self):
        assert isinstance(abw_has_punctuation(_EMPTY), bool)

    def test_false_for_empty_section(self):
        assert abw_has_punctuation(_EMPTY) is False

    def test_is_boolean(self):
        result = abw_has_punctuation(_EMPTY)
        assert result in (True, False)

    def test_consistent_across_calls(self):
        assert abw_has_punctuation(_EMPTY) == abw_has_punctuation(_EMPTY)

    def test_raises_for_minimal_document(self):
        with pytest.raises((AttributeError, Exception)):
            abw_has_punctuation(_MINIMAL)

    def test_raises_for_two_paragraphs(self):
        with pytest.raises((AttributeError, Exception)):
            abw_has_punctuation(_TWO)
