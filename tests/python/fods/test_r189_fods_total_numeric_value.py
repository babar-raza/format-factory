"""
tests/python/fods/test_r189_fods_total_numeric_value.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT58-001
Tests for workbook_total_numeric_value() — sum of all numeric cell values.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods.neutral_model import workbook_total_numeric_value

SAMPLES = _REPO / "samples" / "by-format" / "fods"


class TestFodsTotalNumericValue:
    def test_empty_workbook_returns_zero(self):
        """Empty workbook with no sheets returns 0.0."""
        result = workbook_total_numeric_value({})
        assert result == 0.0

    def test_no_numeric_cells_returns_zero(self):
        """Sheet with only text cells returns 0.0."""
        wb = {
            "sheets": [
                {
                    "rows": [
                        {"cells": [{"value": "alpha"}, {"value": "beta"}]},
                    ]
                }
            ]
        }
        result = workbook_total_numeric_value(wb)
        assert result == 0.0

    def test_sums_integer_values(self):
        """Sum of integer cells is correct."""
        wb = {
            "sheets": [
                {
                    "rows": [
                        {"cells": [{"value": 10}, {"value": 20}]},
                        {"cells": [{"value": 30}]},
                    ]
                }
            ]
        }
        result = workbook_total_numeric_value(wb)
        assert result == 60.0

    def test_sums_float_values(self):
        """Sum of float cells is correct."""
        wb = {
            "sheets": [
                {
                    "rows": [
                        {"cells": [{"value": 1.5}, {"value": 2.5}]},
                    ]
                }
            ]
        }
        result = workbook_total_numeric_value(wb)
        assert abs(result - 4.0) < 1e-9

    def test_booleans_not_counted(self):
        """Boolean values are not included in the sum."""
        wb = {
            "sheets": [
                {
                    "rows": [
                        {"cells": [{"value": True}, {"value": False}, {"value": 5}]},
                    ]
                }
            ]
        }
        result = workbook_total_numeric_value(wb)
        assert result == 5.0

    def test_result_is_float(self):
        """Result is always a float."""
        wb = {"sheets": [{"rows": [{"cells": [{"value": 7}]}]}]}
        result = workbook_total_numeric_value(wb)
        assert isinstance(result, float)
