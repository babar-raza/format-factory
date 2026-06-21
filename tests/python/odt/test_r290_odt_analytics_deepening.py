"""Sprint R290: ODT analytics deepening — empty_paragraph_ratio, longest_word, distinct_word_count."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from odt.odt_parser import (
    odt_empty_paragraph_ratio,
    odt_longest_word,
    odt_distinct_word_count,
)

SAMPLES = _REPO / "samples" / "by-format" / "odt" / "valid"
MINIMAL = SAMPLES / "minimal-document.odt"


@pytest.fixture
def sample():
    if not MINIMAL.exists():
        pytest.skip("ODT sample not available")
    return MINIMAL


class TestOdtEmptyParagraphRatio:
    def test_returns_float(self, sample):
        assert isinstance(odt_empty_paragraph_ratio(sample), float)

    def test_between_zero_and_one(self, sample):
        r = odt_empty_paragraph_ratio(sample)
        assert 0.0 <= r <= 1.0


class TestOdtLongestWord:
    def test_returns_int(self, sample):
        # odt_longest_word returns the CHARACTER LENGTH of the longest word (int)
        assert isinstance(odt_longest_word(sample), int)

    def test_nonnegative_length(self, sample):
        assert odt_longest_word(sample) >= 0


class TestOdtDistinctWordCount:
    def test_returns_int(self, sample):
        assert isinstance(odt_distinct_word_count(sample), int)

    def test_nonnegative(self, sample):
        assert odt_distinct_word_count(sample) >= 0
