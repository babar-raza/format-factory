"""Tests for odt_has_unicode and odt_max_words_per_paragraph (Sprint 44)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.odt import odt_has_unicode, odt_max_words_per_paragraph

_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"
_MINIMAL = str(_DIR / "minimal-document.odt")   # 1 para, ASCII: has_unicode=False, max_words=2
_TWO = str(_DIR / "two-paragraphs.odt")         # 2 paras, ASCII: has_unicode=False, max_words=2
_UNICODE = str(_DIR / "unicode-text.odt")        # 1 para, unicode: has_unicode=True, max_words=3


class TestOdtHasUnicode:
    def test_return_type(self):
        assert isinstance(odt_has_unicode(_MINIMAL), bool)

    def test_false_for_ascii_minimal(self):
        # minimal-document.odt: ASCII only
        assert odt_has_unicode(_MINIMAL) is False

    def test_false_for_ascii_two_paragraphs(self):
        # two-paragraphs.odt: ASCII only
        assert odt_has_unicode(_TWO) is False

    def test_true_for_unicode(self):
        # unicode-text.odt: contains non-ASCII characters
        assert odt_has_unicode(_UNICODE) is True

    def test_consistent_across_calls(self):
        assert odt_has_unicode(_UNICODE) == odt_has_unicode(_UNICODE)

    def test_false_is_not_none(self):
        result = odt_has_unicode(_MINIMAL)
        assert result is False
        assert result is not None


class TestOdtMaxWordsPerParagraph:
    def test_return_type(self):
        assert isinstance(odt_max_words_per_paragraph(_MINIMAL), int)

    def test_exact_2_for_minimal(self):
        # minimal-document.odt: 1 paragraph with 2 words
        assert odt_max_words_per_paragraph(_MINIMAL) == 2

    def test_exact_2_for_two_paragraphs(self):
        # two-paragraphs.odt: 2 paragraphs each with 2 words
        assert odt_max_words_per_paragraph(_TWO) == 2

    def test_exact_3_for_unicode(self):
        # unicode-text.odt: 1 paragraph with 3 words
        assert odt_max_words_per_paragraph(_UNICODE) == 3

    def test_nonnegative(self):
        assert odt_max_words_per_paragraph(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert odt_max_words_per_paragraph(_MINIMAL) == odt_max_words_per_paragraph(_MINIMAL)
