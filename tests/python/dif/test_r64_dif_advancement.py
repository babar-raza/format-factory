"""
test_r64_dif_advancement.py -- R64 Train I: DIF format track advancement.

New capability: dif_string_value_list(dif_doc)
  Returns flat list of all string cell values found in the DIF document.

R64 Sprint: Train I -- DIF format track advancement
"""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from src.python.dif.dif_stats import dif_string_value_list


def _doc(rows_data):
    """Build minimal DIF doc from list of cell dicts per row."""
    return {"rows": rows_data}


class TestDifStringValueList:
    def test_empty_doc(self):
        result = dif_string_value_list({"rows": []})
        assert result == []

    def test_all_string_cells(self):
        doc = _doc([
            [{"type": "string", "value": "hello"}, {"type": "string", "value": "world"}],
        ])
        result = dif_string_value_list(doc)
        assert result == ["hello", "world"]

    def test_numeric_cells_excluded(self):
        doc = _doc([
            [{"type": "numeric", "value": 42}, {"type": "string", "value": "abc"}],
        ])
        result = dif_string_value_list(doc)
        assert result == ["abc"]

    def test_empty_string_excluded(self):
        doc = _doc([
            [{"type": "string", "value": ""}, {"type": "string", "value": "ok"}],
        ])
        result = dif_string_value_list(doc)
        assert result == ["ok"]

    def test_none_value_excluded(self):
        doc = _doc([
            [{"type": "string", "value": None}],
        ])
        result = dif_string_value_list(doc)
        assert result == []

    def test_text_type_also_matched(self):
        doc = _doc([
            [{"type": "text", "value": "found"}],
        ])
        result = dif_string_value_list(doc)
        assert result == ["found"]

    def test_multiple_rows(self):
        doc = _doc([
            [{"type": "string", "value": "a"}],
            [{"type": "string", "value": "b"}],
            [{"type": "string", "value": "c"}],
        ])
        result = dif_string_value_list(doc)
        assert result == ["a", "b", "c"]

    def test_callable_from_module(self):
        from src.python.dif.dif_stats import dif_string_value_list as fn
        assert callable(fn)
