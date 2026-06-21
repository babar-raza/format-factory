"""Sprint R290I: ODT analytics deepening — digit_count, uppercase_ratio, space_count."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from odt.odt_parser import (
    odt_digit_count,
    odt_uppercase_ratio,
    odt_space_count,
)

SAMPLES = _REPO / "samples" / "by-format" / "odt" / "valid"
MINIMAL = SAMPLES / "minimal-document.odt"
TWO_PARA = SAMPLES / "two-paragraphs.odt"


@pytest.fixture
def sample():
    if not MINIMAL.exists():
        pytest.skip("ODT minimal sample not available")
    return MINIMAL


@pytest.fixture
def two_para_sample():
    if not TWO_PARA.exists():
        pytest.skip("ODT two-paragraph sample not available")
    return TWO_PARA


class TestOdtDigitCount:
    def test_returns_int(self, sample):
        assert isinstance(odt_digit_count(sample), int)

    def test_nonnegative(self, sample):
        assert odt_digit_count(sample) >= 0


class TestOdtUppercaseRatio:
    def test_returns_float(self, sample):
        assert isinstance(odt_uppercase_ratio(sample), float)

    def test_between_zero_and_one(self, sample):
        r = odt_uppercase_ratio(sample)
        assert 0.0 <= r <= 1.0


class TestOdtSpaceCount:
    def test_returns_int(self, sample):
        assert isinstance(odt_space_count(sample), int)

    def test_nonnegative(self, sample):
        assert odt_space_count(sample) >= 0

    def test_two_paragraphs_has_spaces(self, two_para_sample):
        assert odt_space_count(two_para_sample) >= 0
