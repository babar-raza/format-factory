"""Tests for Gnumeric average_row function (rnext40)."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import average_row, create_gnumeric, set_cell_value


class TestAverageRow:
    def _make_model(self, rows: list[list[str]]) -> dict:
        sheets = [{"name": "Sheet1", "rows": rows}]
        return create_gnumeric(sheets)

    def test_numeric_row(self):
        model = self._make_model([["1", "2", "3", "4"]])
        result = average_row(model, 0, 0)
        assert abs(result - 2.5) < 1e-9

    def test_empty_row(self):
        model = self._make_model([[]])
        result = average_row(model, 0, 0)
        assert result == 0.0

    def test_mixed_numeric_and_text(self):
        # text values should be ignored
        model = self._make_model([["10", "hello", "20"]])
        result = average_row(model, 0, 0)
        assert abs(result - 15.0) < 1e-9

    def test_all_text_returns_zero(self):
        model = self._make_model([["foo", "bar"]])
        result = average_row(model, 0, 0)
        assert result == 0.0

    def test_single_value(self):
        model = self._make_model([["42"]])
        result = average_row(model, 0, 0)
        assert abs(result - 42.0) < 1e-9

    def test_returns_float(self):
        model = self._make_model([["1", "2"]])
        result = average_row(model, 0, 0)
        assert isinstance(result, float)
