"""Sprint R290H: ABW analytics deepening — vowel_count, consonant_ratio, numeric_char_count."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    abw_vowel_count,
    abw_consonant_ratio,
    abw_numeric_char_count,
)

SAMPLES = _REPO / "samples" / "by-format" / "abw"
MINIMAL = SAMPLES / "minimal-document.abw"
TWO_PARA = SAMPLES / "two-paragraphs.abw"


@pytest.fixture
def sample():
    if not MINIMAL.exists():
        pytest.skip("ABW sample not available")
    return MINIMAL


@pytest.fixture
def two_para_sample():
    if not TWO_PARA.exists():
        pytest.skip("ABW two-paragraph sample not available")
    return TWO_PARA


class TestAbwVowelCount:
    def test_returns_int(self, sample):
        assert isinstance(abw_vowel_count(sample), int)

    def test_nonnegative(self, sample):
        assert abw_vowel_count(sample) >= 0


class TestAbwConsonantRatio:
    def test_returns_float(self, sample):
        assert isinstance(abw_consonant_ratio(sample), float)

    def test_between_zero_and_one(self, sample):
        r = abw_consonant_ratio(sample)
        assert 0.0 <= r <= 1.0


class TestAbwNumericCharCount:
    def test_returns_int(self, sample):
        assert isinstance(abw_numeric_char_count(sample), int)

    def test_nonnegative(self, sample):
        assert abw_numeric_char_count(sample) >= 0
