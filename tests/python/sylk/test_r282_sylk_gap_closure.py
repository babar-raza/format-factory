"""Tests closing FOSS gaps: sylk_is_all_numeric, sylk_row_span, sylk_is_square."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.sylk.sylk_parser import sylk_is_all_numeric, sylk_row_span, sylk_is_square


@pytest.fixture
def numeric_sylk(tmp_path):
    p = tmp_path / "numeric.sylk"
    p.write_text(
        "ID;P\nC;X1;Y1;K10\nC;X2;Y1;K20\n"
        "C;X1;Y2;K30\nC;X2;Y2;K40\nE\n",
        encoding="utf-8",
    )
    return p


@pytest.fixture
def mixed_sylk(tmp_path):
    p = tmp_path / "mixed.sylk"
    p.write_text(
        'ID;P\nC;X1;Y1;K10\nC;X2;Y1;"hello"\n'
        "C;X1;Y2;K30\nC;X2;Y2;K40\nE\n",
        encoding="utf-8",
    )
    return p


def test_sylk_is_all_numeric_true(numeric_sylk):
    result = sylk_is_all_numeric(numeric_sylk)
    assert result is True


def test_sylk_is_all_numeric_false(mixed_sylk):
    result = sylk_is_all_numeric(mixed_sylk)
    assert result is False


def test_sylk_row_span_returns_int(numeric_sylk):
    result = sylk_row_span(numeric_sylk)
    assert isinstance(result, int)
    assert result >= 1


def test_sylk_is_square_true(numeric_sylk):
    # 2x2 grid → square
    result = sylk_is_square(numeric_sylk)
    assert isinstance(result, bool)


def test_sylk_is_square_nonsquare(tmp_path):
    p = tmp_path / "rect.sylk"
    p.write_text(
        "ID;P\nC;X1;Y1;K1\nC;X2;Y1;K2\nC;X3;Y1;K3\n"
        "C;X1;Y2;K4\nC;X2;Y2;K5\nC;X3;Y2;K6\nE\n",
        encoding="utf-8",
    )
    result = sylk_is_square(p)
    assert result is False  # 3 cols x 2 rows
