"""Tests closing FOSS gaps: dif_is_all_string, dif_nonempty_cell_ratio,
dif_avg_numeric_value, dif_row_length_variance."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.dif.dif_parser import (
    dif_is_all_string,
    dif_nonempty_cell_ratio,
    dif_avg_numeric_value,
    dif_row_length_variance,
)

SAMPLE_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"


@pytest.fixture
def numeric_dif():
    p = SAMPLE_DIR / "numeric-row.dif"
    if not p.exists():
        pytest.skip("numeric-row.dif sample not available")
    return p


@pytest.fixture
def minimal_dif():
    p = SAMPLE_DIR / "minimal-2x2.dif"
    if not p.exists():
        pytest.skip("minimal-2x2.dif sample not available")
    return p


def test_dif_is_all_string_returns_bool(minimal_dif):
    result = dif_is_all_string(minimal_dif)
    assert isinstance(result, bool)


def test_dif_nonempty_cell_ratio(minimal_dif):
    result = dif_nonempty_cell_ratio(minimal_dif)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0


def test_dif_avg_numeric_value(numeric_dif):
    result = dif_avg_numeric_value(numeric_dif)
    assert isinstance(result, (int, float))
    assert result > 0


def test_dif_row_length_variance(minimal_dif):
    result = dif_row_length_variance(minimal_dif)
    assert isinstance(result, (int, float))
    assert result >= 0.0
