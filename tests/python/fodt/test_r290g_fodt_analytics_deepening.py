"""Sprint R290G: FODT analytics deepening — total_character_count, avg_block_length, max_block_text_length."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt.neutral_model import (
    fodt_total_character_count,
    fodt_avg_block_length,
    fodt_max_block_text_length,
)

SAMPLES = _REPO / "samples" / "by-format" / "fodt"
MINIMAL = SAMPLES / "minimal-document.fodt"
HEADINGS = SAMPLES / "headings-and-paragraphs.fodt"


@pytest.fixture
def sample():
    if not MINIMAL.exists():
        pytest.skip("FODT sample not available")
    return MINIMAL


@pytest.fixture
def headings_sample():
    if not HEADINGS.exists():
        pytest.skip("FODT headings sample not available")
    return HEADINGS


class TestFodtTotalCharacterCount:
    def test_returns_int(self, sample):
        assert isinstance(fodt_total_character_count(sample), int)

    def test_nonnegative(self, sample):
        assert fodt_total_character_count(sample) >= 0


class TestFodtAvgBlockLength:
    def test_returns_float(self, sample):
        assert isinstance(fodt_avg_block_length(sample), float)

    def test_nonnegative(self, sample):
        assert fodt_avg_block_length(sample) >= 0.0


class TestFodtMaxBlockTextLength:
    def test_returns_int(self, sample):
        assert isinstance(fodt_max_block_text_length(sample), int)

    def test_nonnegative(self, headings_sample):
        assert fodt_max_block_text_length(headings_sample) >= 0
