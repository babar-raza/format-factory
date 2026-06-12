"""
tests/python/fods/test_r191_fods_formula_policy.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT59-001
Tests for workbook_formula_edit_policy() — formula editing policy summary.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods.neutral_model import workbook_formula_edit_policy

SAMPLES = _REPO / "samples" / "by-format" / "fods"


class TestWorkbookFormulaEditPolicy:
    def test_empty_workbook_returns_no_formulas_policy(self):
        result = workbook_formula_edit_policy({})
        assert result["policy"] == "no_formulas"

    def test_returns_required_keys(self):
        result = workbook_formula_edit_policy({})
        assert "total_formulas" in result
        assert "editable_formulas" in result
        assert "locked_formulas" in result
        assert "policy" in result

    def test_total_formulas_non_negative(self):
        result = workbook_formula_edit_policy({})
        assert result["total_formulas"] >= 0

    def test_editable_plus_locked_le_total(self):
        result = workbook_formula_edit_policy({})
        assert result["editable_formulas"] + result["locked_formulas"] <= result["total_formulas"]

    def test_real_file_returns_valid_structure(self):
        from src.python.fods.parser import parse_fods
        model = parse_fods(str(SAMPLES / "minimal-spreadsheet.fods"))
        result = workbook_formula_edit_policy(model)
        assert isinstance(result["total_formulas"], int)
        assert isinstance(result["policy"], str)

    def test_policy_is_valid_string(self):
        from src.python.fods.parser import parse_fods
        model = parse_fods(str(SAMPLES / "minimal-spreadsheet.fods"))
        result = workbook_formula_edit_policy(model)
        valid_policies = {"no_formulas", "all_editable", "some_locked", "all_locked"}
        assert result["policy"] in valid_policies
