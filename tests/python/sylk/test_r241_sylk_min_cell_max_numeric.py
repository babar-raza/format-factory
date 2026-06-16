"""Tests for sylk_min_cell_value_length and sylk_max_numeric_value (Sprint 31)."""
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk import sylk_min_cell_value_length, sylk_max_numeric_value, sylk_max_cell_value_length

_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"

# minimal-2x2.slk is first alphabetically:
#   Name/Value/"Alpha"/42 -> max_numeric=42, min_cell_len=2 ("42")
_FIRST_SLK = str(sorted(_SYLK_DIR.glob("*.slk"))[0])


def _write_sylk(tmp_path, content):
    p = tmp_path / "test.slk"
    p.write_text(content, encoding="ascii")
    return str(p)


_TEXT_ONLY = "ID;P\nC;X1;Y1;K\"hello\"\nC;X2;Y1;K\"world\"\nE\n"


class TestSylkMinCellValueLength:
    def test_return_type(self):
        result = sylk_min_cell_value_length(_FIRST_SLK)
        assert isinstance(result, int)

    def test_nonnegative(self):
        assert sylk_min_cell_value_length(_FIRST_SLK) >= 0

    def test_positive_for_nonempty(self):
        # minimal-2x2.slk has cells: Name(4), Value(5), Alpha(5), 42(2) -> min=2
        result = sylk_min_cell_value_length(_FIRST_SLK)
        assert result > 0

    def test_exact_min_value(self):
        # "42" -> len=2 is shortest non-empty cell string
        result = sylk_min_cell_value_length(_FIRST_SLK)
        assert result == 2

    def test_min_is_leq_max(self):
        min_len = sylk_min_cell_value_length(_FIRST_SLK)
        max_len = sylk_max_cell_value_length(_FIRST_SLK)
        assert min_len <= max_len


class TestSylkMaxNumericValue:
    def test_return_type_float_or_none(self):
        result = sylk_max_numeric_value(_FIRST_SLK)
        assert isinstance(result, (float, int, type(None)))

    def test_exact_42_for_sample(self):
        # minimal-2x2.slk has one numeric cell: K42 -> max=42.0
        result = sylk_max_numeric_value(_FIRST_SLK)
        assert result == 42.0

    def test_returns_none_for_text_only(self, tmp_path):
        p = _write_sylk(tmp_path, _TEXT_ONLY)
        result = sylk_max_numeric_value(p)
        assert result is None

    def test_max_is_largest(self, tmp_path):
        content = "ID;P\nC;X1;Y1;K10\nC;X2;Y1;K99\nC;X3;Y1;K5\nE\n"
        p = _write_sylk(tmp_path, content)
        assert sylk_max_numeric_value(p) == 99.0

    def test_consistent_across_calls(self):
        assert sylk_max_numeric_value(_FIRST_SLK) == sylk_max_numeric_value(_FIRST_SLK)
