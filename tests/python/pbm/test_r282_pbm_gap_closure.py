"""Tests closing FOSS gaps: pbm_avg_row_density, pbm_border_black_count."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import pbm_avg_row_density, pbm_border_black_count


@pytest.fixture
def pbm_file(tmp_path):
    p = tmp_path / "test.pbm"
    # 4x3 P1 image: mix of black and white
    p.write_text("P1\n4 3\n1 0 1 0\n0 1 0 1\n1 1 0 0\n", encoding="utf-8")
    return p


def test_pbm_avg_row_density_returns_float(pbm_file):
    result = pbm_avg_row_density(pbm_file)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0


def test_pbm_avg_row_density_value(pbm_file):
    result = pbm_avg_row_density(pbm_file)
    # Row 1: 2/4=0.5, Row 2: 2/4=0.5, Row 3: 2/4=0.5 → avg 0.5
    assert 0.3 < result < 0.7


def test_pbm_border_black_count_returns_int(pbm_file):
    result = pbm_border_black_count(pbm_file)
    assert isinstance(result, int)
    assert result >= 0
