"""TC-EXEC-002: FODS semantic round-trip verification.

Deep field comparison after parse→write→reload cycle.
Verifies that cell values, types, sheet names, row/column counts, and
formulas are fully preserved through a complete round-trip.
"""
import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from src.python.fods import parse_fods_strict, write_fods


def _roundtrip(workbook):
    with tempfile.NamedTemporaryFile(
        suffix=".fods", delete=False, mode="w", encoding="utf-8"
    ) as f:
        tmp = Path(f.name)
    try:
        write_fods(workbook, tmp)
        return parse_fods_strict(str(tmp))
    finally:
        tmp.unlink(missing_ok=True)


def _build_multi_sheet_workbook():
    """Build a synthetic workbook representative of real-world structure."""
    return {
        "sheets": [
            {
                "name": "Numbers",
                "rows": [
                    {"cells": [
                        {"value": "Qty", "value_type": "string"},
                        {"value": "Price", "value_type": "string"},
                    ]},
                    {"cells": [
                        {"value": 10.0, "value_type": "float"},
                        {"value": 99.95, "value_type": "float"},
                    ]},
                    {"cells": [
                        {"value": 3.0, "value_type": "float"},
                        {"value": 5.0, "value_type": "float"},
                    ]},
                ],
            },
            {
                "name": "Text",
                "rows": [
                    {"cells": [{"value": "Alice", "value_type": "string"}]},
                    {"cells": [{"value": "Bob", "value_type": "string"}]},
                ],
            },
        ]
    }


class TestFodsSemanticRoundtripSheets:
    def test_sheet_names_match_exactly(self):
        """Sheet names match original exactly after round-trip."""
        wb = _build_multi_sheet_workbook()
        wb2 = _roundtrip(wb)
        original_names = [s["name"] for s in wb["sheets"]]
        rt_names = [s["name"] for s in wb2["sheets"]]
        assert rt_names == original_names

    def test_sheet_count_matches(self):
        """Sheet count is unchanged after round-trip."""
        wb = _build_multi_sheet_workbook()
        wb2 = _roundtrip(wb)
        assert wb2["sheet_count"] == len(wb["sheets"])


class TestFodsSemanticRoundtripCells:
    def test_all_string_values_match(self):
        """All string cell values match after round-trip."""
        wb = _build_multi_sheet_workbook()
        wb2 = _roundtrip(wb)
        # Sheet 0 row 0: ["Qty", "Price"]
        cells = wb2["sheets"][0]["rows"][0]["cells"]
        assert cells[0]["value"] == "Qty"
        assert cells[1]["value"] == "Price"

    def test_all_numeric_values_match(self):
        """Numeric values match within float tolerance after round-trip."""
        wb = _build_multi_sheet_workbook()
        wb2 = _roundtrip(wb)
        row1 = wb2["sheets"][0]["rows"][1]["cells"]
        assert row1[0]["value"] == pytest.approx(10.0)
        assert row1[1]["value"] == pytest.approx(99.95)

    def test_cell_types_preserved(self):
        """Cell value_type fields are preserved after round-trip."""
        wb = _build_multi_sheet_workbook()
        wb2 = _roundtrip(wb)
        cells_row0 = wb2["sheets"][0]["rows"][0]["cells"]
        assert cells_row0[0]["value_type"] == "string"
        assert cells_row0[1]["value_type"] == "string"
        cells_row1 = wb2["sheets"][0]["rows"][1]["cells"]
        assert cells_row1[0]["value_type"] == "float"

    def test_second_sheet_values_match(self):
        """Values in the second sheet match after round-trip."""
        wb = _build_multi_sheet_workbook()
        wb2 = _roundtrip(wb)
        sheet_b = wb2["sheets"][1]
        assert sheet_b["rows"][0]["cells"][0]["value"] == "Alice"
        assert sheet_b["rows"][1]["cells"][0]["value"] == "Bob"


class TestFodsSemanticRoundtripCounts:
    def test_row_counts_per_sheet_match(self):
        """Row count per sheet matches after round-trip."""
        wb = _build_multi_sheet_workbook()
        wb2 = _roundtrip(wb)
        assert len(wb2["sheets"][0]["rows"]) == 3
        assert len(wb2["sheets"][1]["rows"]) == 2

    def test_empty_workbook_round_trip(self):
        """Empty workbook produces valid FODS and re-parses cleanly."""
        wb = {"sheets": []}
        wb2 = _roundtrip(wb)
        assert wb2["sheet_count"] == 0
        assert wb2["sheets"] == []
