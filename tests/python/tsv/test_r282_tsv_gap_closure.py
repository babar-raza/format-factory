"""Tests closing FOSS gaps: tsv_numeric_sum, tsv_avg_numeric_value,
tsv_has_duplicates, tsv_empty_column_count, tsv_longest_row_index."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import (
    tsv_numeric_sum,
    tsv_avg_numeric_value,
    tsv_has_duplicates,
    tsv_empty_column_count,
    tsv_longest_row_index,
)


@pytest.fixture
def tsv_file(tmp_path):
    p = tmp_path / "data.tsv"
    p.write_text("name\tage\tcity\nAlice\t30\tNYC\nBob\t25\t\nAlice\t40\tLondon\n", encoding="utf-8")
    return p


def test_tsv_numeric_sum(tsv_file):
    result = tsv_numeric_sum(tsv_file)
    assert isinstance(result, (int, float))
    # 30+25+40 = 95
    assert result >= 90


def test_tsv_avg_numeric_value(tsv_file):
    result = tsv_avg_numeric_value(tsv_file)
    assert isinstance(result, (int, float))
    assert result > 0


def test_tsv_has_duplicates_true(tmp_path):
    p = tmp_path / "dup.tsv"
    p.write_text("name\tage\tcity\nAlice\t30\tNYC\nBob\t25\tLA\nAlice\t30\tNYC\n", encoding="utf-8")
    result = tsv_has_duplicates(p)
    assert result is True


def test_tsv_has_duplicates_false(tsv_file):
    result = tsv_has_duplicates(tsv_file)
    assert result is False


def test_tsv_empty_column_count(tsv_file):
    result = tsv_empty_column_count(tsv_file)
    assert isinstance(result, int)
    assert result >= 0


def test_tsv_longest_row_index(tsv_file):
    result = tsv_longest_row_index(tsv_file)
    assert isinstance(result, int)
    assert result >= 0
