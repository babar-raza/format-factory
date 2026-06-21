"""Tests for FODT analytics deepening (R290L): consonant_ratio, avg_run_count, empty_block_count."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt.neutral_model import fodt_consonant_ratio, fodt_avg_run_count, fodt_empty_block_count

SAMPLES = _REPO / "samples" / "by-format" / "fodt"


def test_consonant_ratio_returns_float():
    result = fodt_consonant_ratio(SAMPLES / "minimal-document.fodt")
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


def test_consonant_ratio_with_headings():
    result = fodt_consonant_ratio(SAMPLES / "headings-and-paragraphs.fodt")
    assert isinstance(result, float)
    assert result > 0.0  # text content has consonants


def test_avg_run_count_returns_float():
    result = fodt_avg_run_count(SAMPLES / "minimal-document.fodt")
    assert isinstance(result, float)
    assert result >= 0.0


def test_avg_run_count_headings():
    result = fodt_avg_run_count(SAMPLES / "headings-and-paragraphs.fodt")
    assert isinstance(result, float)


def test_empty_block_count_returns_int():
    result = fodt_empty_block_count(SAMPLES / "minimal-document.fodt")
    assert isinstance(result, int)
    assert result >= 0


def test_empty_block_count_table():
    result = fodt_empty_block_count(SAMPLES / "table-basic.fodt")
    assert isinstance(result, int)
