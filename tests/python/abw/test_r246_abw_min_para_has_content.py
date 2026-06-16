"""Tests for abw_min_paragraph_length and abw_has_content (Sprint 36)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.abw import abw_min_paragraph_length, abw_has_content

_SAMPLES = _REPO / "samples" / "by-format" / "abw"
_MINIMAL = str(_SAMPLES / "minimal-document.abw")    # min_para=5, has_content=True
_EMPTY = str(_SAMPLES / "empty-section.abw")          # min_para=0, has_content=False
_TWO_PARA = str(_SAMPLES / "two-paragraphs.abw")     # min_para=16, has_content=True


class TestAbwMinParagraphLength:
    def test_return_type(self):
        result = abw_min_paragraph_length(_MINIMAL)
        assert isinstance(result, int)

    def test_exact_min_for_minimal(self):
        # minimal-document.abw has paragraph of length 5
        assert abw_min_paragraph_length(_MINIMAL) == 5

    def test_zero_for_empty(self):
        assert abw_min_paragraph_length(_EMPTY) == 0

    def test_exact_min_for_two_para(self):
        # two-paragraphs.abw min paragraph length is 16
        assert abw_min_paragraph_length(_TWO_PARA) == 16

    def test_nonnegative(self):
        assert abw_min_paragraph_length(_MINIMAL) >= 0


class TestAbwHasContent:
    def test_return_type(self):
        result = abw_has_content(_MINIMAL)
        assert isinstance(result, bool)

    def test_true_for_minimal(self):
        assert abw_has_content(_MINIMAL) is True

    def test_false_for_empty(self):
        assert abw_has_content(_EMPTY) is False

    def test_true_for_two_paragraphs(self):
        assert abw_has_content(_TWO_PARA) is True

    def test_consistent_across_calls(self):
        assert abw_has_content(_MINIMAL) == abw_has_content(_MINIMAL)
