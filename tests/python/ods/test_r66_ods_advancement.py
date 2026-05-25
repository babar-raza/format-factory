"""
test_r66_ods_advancement.py -- R66 Train I: ODS format track advancement.

New capability: ods_data_validation_count(ods_doc) -> int

R66 Sprint: FORMAT-FACTORY-R66 product advancement
Train I -- ODS format track advancement
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_src = Path(__file__).resolve().parents[3] / "src" / "python"
sys.path.insert(0, str(_src))

from ods.ods_stats import ods_data_validation_count


# ---------------------------------------------------------------------------
# ods_data_validation_count tests
# ---------------------------------------------------------------------------

class TestOdsDataValidationCount:
    """Tests for ods_data_validation_count()."""

    def test_empty_doc_returns_zero(self):
        result = ods_data_validation_count({"sheets": []})
        assert result == 0

    def test_returns_int(self):
        result = ods_data_validation_count({})
        assert isinstance(result, int)

    def test_explicit_data_validations_list(self):
        doc = {"sheets": [], "data_validations": [
            {"name": "v1"}, {"name": "v2"}, {"name": "v3"},
        ]}
        result = ods_data_validation_count(doc)
        assert result == 3

    def test_cell_level_validation_attributes(self):
        doc = {"sheets": [
            {"name": "Sheet1", "rows": [
                {"cells": [
                    {"value": 1, "validation": "val1"},
                    {"value": 2, "validation": "val2"},
                    {"value": 3},
                ]},
            ]},
        ]}
        result = ods_data_validation_count(doc)
        assert result == 2

    def test_none_doc_returns_zero(self):
        result = ods_data_validation_count({})
        assert result == 0

    def test_empty_validations_list(self):
        doc = {"sheets": [], "data_validations": []}
        result = ods_data_validation_count(doc)
        assert result == 0
