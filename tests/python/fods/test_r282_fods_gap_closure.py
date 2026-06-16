"""Tests closing FOSS gaps: fods_has_string_cells, fods_row_count_variance."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fods.neutral_model import fods_has_string_cells, fods_row_count_variance
from src.python.fods import parse_fods

SAMPLE_DIR = _REPO / "samples" / "by-format" / "fods"


@pytest.fixture
def fods_workbook():
    candidates = list(SAMPLE_DIR.glob("*.fods"))
    if not candidates:
        pytest.skip("No FODS sample files available")
    return parse_fods(candidates[0])


def test_fods_has_string_cells_returns_bool(fods_workbook):
    result = fods_has_string_cells(fods_workbook)
    assert isinstance(result, bool)


def test_fods_row_count_variance_returns_number(fods_workbook):
    result = fods_row_count_variance(fods_workbook)
    assert isinstance(result, (int, float))
    assert result >= 0.0
