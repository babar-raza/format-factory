"""
test_r65_dif_advancement.py -- R65 Train I: DIF format track advancement.

New capability: dif_empty_row_count(dif_doc) -- count of rows where all cells are empty.

R65 Sprint: Train I -- DIF stats module expansion
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.dif.dif_stats import dif_empty_row_count


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

def _make_dif(rows: list) -> dict:
    """Build a minimal DIF document dict."""
    return {"rows": rows, "vectors": len(rows), "tuples": 0, "title": "test"}


# ---------------------------------------------------------------------------
# dif_empty_row_count tests
# ---------------------------------------------------------------------------

class TestDifEmptyRowCount:
    """Tests for dif_empty_row_count()."""

    def test_no_rows(self):
        doc = _make_dif([])
        assert dif_empty_row_count(doc) == 0

    def test_all_rows_non_empty(self):
        doc = _make_dif([
            [{"value": 1, "type": "numeric"}, {"value": "hello", "type": "string"}],
            [{"value": 2, "type": "numeric"}, {"value": "world", "type": "string"}],
        ])
        assert dif_empty_row_count(doc) == 0

    def test_all_rows_empty(self):
        doc = _make_dif([
            [{"value": None, "type": ""}, {"value": "", "type": ""}],
            [{"value": None, "type": ""}],
        ])
        assert dif_empty_row_count(doc) == 2

    def test_mixed_empty_and_non_empty(self):
        doc = _make_dif([
            [{"value": 1, "type": "numeric"}],
            [{"value": None, "type": ""}, {"value": "", "type": ""}],
            [{"value": "x", "type": "string"}],
        ])
        assert dif_empty_row_count(doc) == 1

    def test_single_cell_empty_row(self):
        doc = _make_dif([
            [{"value": None, "type": ""}],
        ])
        assert dif_empty_row_count(doc) == 1

    def test_single_cell_non_empty_row(self):
        doc = _make_dif([
            [{"value": 42, "type": "numeric"}],
        ])
        assert dif_empty_row_count(doc) == 0

    def test_empty_list_row(self):
        """An empty row (no cells) counts as empty."""
        doc = _make_dif([[]])
        assert dif_empty_row_count(doc) == 1

    def test_returns_int(self):
        doc = _make_dif([
            [{"value": None, "type": ""}],
            [{"value": 1, "type": "numeric"}],
        ])
        result = dif_empty_row_count(doc)
        assert isinstance(result, int)
        assert result == 1
