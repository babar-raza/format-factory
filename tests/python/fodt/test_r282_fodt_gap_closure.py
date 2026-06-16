"""Tests closing FOSS gaps: fodt_whitespace_ratio, fodt_longest_word,
fodt_avg_heading_length, fodt_table_density."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodt.neutral_model import (
    fodt_whitespace_ratio,
    fodt_longest_word,
    fodt_avg_heading_length,
    fodt_table_density,
)

SAMPLE_DIR = _REPO / "samples" / "by-format" / "fodt"


@pytest.fixture
def fodt_path():
    candidates = list(SAMPLE_DIR.glob("*.fodt"))
    if not candidates:
        pytest.skip("No FODT sample files available")
    return candidates[0]


def test_fodt_whitespace_ratio_returns_float(fodt_path):
    result = fodt_whitespace_ratio(fodt_path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0


def test_fodt_longest_word_returns_string(fodt_path):
    result = fodt_longest_word(fodt_path)
    assert isinstance(result, str)


def test_fodt_avg_heading_length_returns_number(fodt_path):
    result = fodt_avg_heading_length(fodt_path)
    assert isinstance(result, (int, float))
    assert result >= 0.0


def test_fodt_table_density_returns_number(fodt_path):
    result = fodt_table_density(fodt_path)
    assert isinstance(result, (int, float))
    assert result >= 0.0
