"""
tests/python/tsv/test_tsv_append_rows.py
Tests for append_rows() added via QUEUE_DISPATCHED_EXECUTION.

Sprint: FORMAT-FACTORY-SELF-HEALING-QUEUE-PROFESSIONALIZE-RNEXT-001
Queue item: shq-q-001
"""

from __future__ import annotations

import sys
from pathlib import Path


_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import append_rows


TSV_BYTES = b"name\tage\nAlice\t30\nBob\t25\n"


class TestAppendRows:
    def test_returns_dict(self) -> None:
        result = append_rows(TSV_BYTES, [["Carol", "35"]])
        assert isinstance(result, dict)

    def test_rows_appended(self) -> None:
        result = append_rows(TSV_BYTES, [["Carol", "35"]])
        assert ["Carol", "35"] in result["rows"]

    def test_original_rows_preserved(self) -> None:
        result = append_rows(TSV_BYTES, [["Carol", "35"]])
        rows = result["rows"]
        assert any("Alice" in r for r in rows)
        assert any("Bob" in r for r in rows)

    def test_multiple_rows_appended(self) -> None:
        new_rows = [["Carol", "35"], ["Dave", "28"]]
        result = append_rows(TSV_BYTES, new_rows)
        assert len(result["rows"]) == 4  # 2 original + 2 new

    def test_empty_rows_list_unchanged(self) -> None:
        result = append_rows(TSV_BYTES, [])
        assert len(result["rows"]) == 2

    def test_row_count_updated(self) -> None:
        result = append_rows(TSV_BYTES, [["Carol", "35"]])
        assert result["row_count"] == 3

    def test_tab_sanitized_in_values(self) -> None:
        result = append_rows(TSV_BYTES, [["Col\tA", "Value"]])
        rows = result["rows"]
        last = rows[-1]
        assert "\t" not in last[0]
        assert "Col A" == last[0]

    def test_newline_sanitized_in_values(self) -> None:
        result = append_rows(TSV_BYTES, [["Line\nBreak", "v"]])
        rows = result["rows"]
        assert "\n" not in rows[-1][0]

    def test_model_dict_input(self) -> None:
        model = {"rows": [["a", "1"], ["b", "2"]], "headers": ["col1", "col2"], "row_count": 2}
        result = append_rows(model, [["c", "3"]])
        assert len(result["rows"]) == 3
        assert result["row_count"] == 3

    def test_does_not_mutate_original_model(self) -> None:
        model = {"rows": [["a", "1"]], "row_count": 1}
        original_rows = list(model["rows"])
        append_rows(model, [["b", "2"]])
        assert model["rows"] == original_rows

    def test_numeric_values_converted_to_str(self) -> None:
        result = append_rows(TSV_BYTES, [[1, 2]])
        rows = result["rows"]
        assert rows[-1] == ["1", "2"]
