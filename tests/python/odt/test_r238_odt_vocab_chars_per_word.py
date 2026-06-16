"""Tests for odt_vocabulary_richness and odt_chars_per_word.

Product deepening: ODT analytics — R238.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO / "src" / "python"))

from odt import odt_vocabulary_richness, odt_chars_per_word

_ODT_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"


def _first_odt():
    files = sorted(_ODT_DIR.glob("*.odt"))
    assert files, f"No ODT samples in {_ODT_DIR}"
    return str(files[0])


class TestOdtVocabularyRichness:
    def test_returns_float(self):
        result = odt_vocabulary_richness(_first_odt())
        assert isinstance(result, float)

    def test_range(self):
        result = odt_vocabulary_richness(_first_odt())
        assert 0.0 <= result <= 1.0

    def test_positive_for_document(self):
        result = odt_vocabulary_richness(_first_odt())
        assert result > 0.0


class TestOdtCharsPerWord:
    def test_returns_float(self):
        result = odt_chars_per_word(_first_odt())
        assert isinstance(result, float)

    def test_positive(self):
        result = odt_chars_per_word(_first_odt())
        assert result > 0.0

    def test_reasonable_range(self):
        result = odt_chars_per_word(_first_odt())
        assert 1.0 < result < 50.0
