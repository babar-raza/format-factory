"""Tests for sylk_cell_type_distribution."""
import tempfile
from pathlib import Path

import pytest

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk.sylk_analytics import sylk_cell_type_distribution


def _make_sylk(records: list[str]) -> Path:
    """Create a minimal SYLK file from record lines."""
    lines = ["ID;P"] + records + ["E"]
    content = "\r\n".join(lines) + "\r\n"
    tmp = tempfile.NamedTemporaryFile(
        suffix=".slk", delete=False, mode="w", encoding="utf-8"
    )
    tmp.write(content)
    tmp.close()
    return Path(tmp.name)


class TestBasicDistribution:
    def test_all_numeric(self):
        path = _make_sylk([
            "C;Y1;X1;K42",
            "C;Y1;X2;K3.14",
            "C;Y2;X1;K0",
        ])
        result = sylk_cell_type_distribution(path)
        assert result["numeric"] == 3
        assert result["string"] == 0
        assert result["empty"] == 0

    def test_all_string(self):
        path = _make_sylk([
            'C;Y1;X1;K"hello"',
            'C;Y1;X2;K"world"',
        ])
        result = sylk_cell_type_distribution(path)
        assert result["string"] == 2
        assert result["numeric"] == 0
        assert result["empty"] == 0

    def test_mixed_types(self):
        path = _make_sylk([
            "C;Y1;X1;K42",
            'C;Y1;X2;K"text"',
            "C;Y2;X1;K99",
        ])
        result = sylk_cell_type_distribution(path)
        assert result["numeric"] == 2
        assert result["string"] == 1
        assert result["empty"] == 0


class TestEmptyCells:
    def test_no_cells_all_zero(self):
        path = _make_sylk([])
        result = sylk_cell_type_distribution(path)
        assert result == {"numeric": 0, "string": 0, "empty": 0}


class TestReturnShape:
    def test_returns_dict_with_three_keys(self):
        path = _make_sylk(["C;Y1;X1;K1"])
        result = sylk_cell_type_distribution(path)
        assert set(result.keys()) == {"numeric", "string", "empty"}

    def test_values_are_integers(self):
        path = _make_sylk(["C;Y1;X1;K1"])
        result = sylk_cell_type_distribution(path)
        for v in result.values():
            assert isinstance(v, int)

    def test_total_equals_cell_count(self):
        path = _make_sylk([
            "C;Y1;X1;K10",
            'C;Y1;X2;K"abc"',
            "C;Y2;X1;K20",
        ])
        result = sylk_cell_type_distribution(path)
        total = result["numeric"] + result["string"] + result["empty"]
        assert total == 3


class TestEdgeCases:
    def test_integer_zero_is_numeric(self):
        path = _make_sylk(["C;Y1;X1;K0"])
        result = sylk_cell_type_distribution(path)
        assert result["numeric"] >= 1

    def test_negative_number_is_numeric(self):
        path = _make_sylk(["C;Y1;X1;K-5"])
        result = sylk_cell_type_distribution(path)
        assert result["numeric"] >= 1
