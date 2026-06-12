"""
test_r66_dif_advancement.py -- R66 Train I: DIF format track advancement.

New capability: dif_string_cell_count(dif_doc) -> int

R66 Sprint: FORMAT-FACTORY-R66 product advancement
Train I -- DIF format track advancement
"""
from __future__ import annotations

import sys
from pathlib import Path


_src = Path(__file__).resolve().parents[3] / "src" / "python"
sys.path.insert(0, str(_src))

from dif.dif_stats import dif_string_cell_count


# ---------------------------------------------------------------------------
# dif_string_cell_count tests
# ---------------------------------------------------------------------------

class TestDifStringCellCount:
    """Tests for dif_string_cell_count()."""

    def test_empty_doc_returns_zero(self):
        result = dif_string_cell_count({"rows": []})
        assert result == 0

    def test_returns_int(self):
        result = dif_string_cell_count({})
        assert isinstance(result, int)

    def test_counts_string_cells(self):
        doc = {"rows": [
            [{"type": "string", "value": "hello"}, {"type": "numeric", "value": 42}],
            [{"type": "text", "value": "world"}, {"type": "string", "value": "!"}],
        ]}
        result = dif_string_cell_count(doc)
        assert result == 3

    def test_empty_string_not_counted(self):
        doc = {"rows": [
            [{"type": "string", "value": ""}, {"type": "string", "value": "x"}],
        ]}
        result = dif_string_cell_count(doc)
        assert result == 1

    def test_none_value_not_counted(self):
        doc = {"rows": [
            [{"type": "string", "value": None}],
        ]}
        result = dif_string_cell_count(doc)
        assert result == 0

    def test_numeric_cells_excluded(self):
        doc = {"rows": [
            [{"type": "numeric", "value": 1}, {"type": "number", "value": 2}],
        ]}
        result = dif_string_cell_count(doc)
        assert result == 0
