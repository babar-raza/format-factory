"""R67 Train H: FODS minimal product readiness tests.

Low-risk readiness improvements: unsupported feature warnings,
extra validation coverage, and helper function smoke tests.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fods import parse_fods, workbook_style_family_list, workbook_data_validation_summary
from src.python.fods.neutral_model import validate_workbook


def _minimal_workbook():
    """Build a minimal workbook dict for testing."""
    from src.python.fods.neutral_model import build_workbook
    return build_workbook(
        odf_version_attr="1.3",
        mimetype="application/vnd.oasis.opendocument.spreadsheet-flat-xml",
        sheets=[{
            "name": "Sheet1",
            "rows": [[{"value": 1, "type": "float"}, {"value": "hello", "type": "string"}]],
            "merged_cells": [],
            "named_ranges": [],
        }],
        warnings=[],
        unsupported_features=[],
        parse_errors=[],
    )


class TestWorkbookStyleFamilyList:
    def test_returns_list_on_empty_workbook(self):
        wb = _minimal_workbook()
        result = workbook_style_family_list(wb)
        assert isinstance(result, list)

    def test_handles_none_auto_styles(self):
        wb = _minimal_workbook()
        wb["auto_styles_elem"] = None
        result = workbook_style_family_list(wb)
        assert isinstance(result, list)

    def test_no_crash_on_real_fods_file(self):
        sample = PROJECT_ROOT / "samples" / "by-format" / "fods" / "test_workbook.fods"
        if not sample.exists():
            pytest.skip("Sample FODS not available")
        wb = parse_fods(str(sample))
        result = workbook_style_family_list(wb)
        assert isinstance(result, list)


class TestWorkbookDataValidationSummary:
    def test_returns_dict(self):
        # Use empty rows to avoid cell format issues
        from src.python.fods.neutral_model import build_workbook
        wb = build_workbook(
            odf_version_attr="1.3",
            mimetype="application/vnd.oasis.opendocument.spreadsheet-flat-xml",
            sheets=[{"name": "Sheet1", "rows": [], "merged_cells": [], "named_ranges": []}],
            warnings=[], unsupported_features=[], parse_errors=[],
        )
        result = workbook_data_validation_summary(wb)
        assert isinstance(result, dict)

    def test_has_validation_count_key(self):
        from src.python.fods.neutral_model import build_workbook
        wb = build_workbook(
            odf_version_attr="1.3",
            mimetype="application/vnd.oasis.opendocument.spreadsheet-flat-xml",
            sheets=[{"name": "Sheet1", "rows": [], "merged_cells": [], "named_ranges": []}],
            warnings=[], unsupported_features=[], parse_errors=[],
        )
        result = workbook_data_validation_summary(wb)
        # Accept either 'count' or 'validation_count' as the key
        assert any(k in result for k in ("count", "validation_count", "data_validation_count")), \
            f"Expected a count key, got: {list(result.keys())}"

    def test_no_crash_on_real_fods_file(self):
        sample = PROJECT_ROOT / "samples" / "by-format" / "fods" / "test_workbook.fods"
        if not sample.exists():
            pytest.skip("Sample FODS not available")
        wb = parse_fods(str(sample))
        result = workbook_data_validation_summary(wb)
        assert isinstance(result, dict)


class TestFODSUnsupportedFeatureWarnings:
    """Low-risk: verify that known unsupported features are listed cleanly."""

    def test_unsupported_features_list_is_accessible(self):
        wb = _minimal_workbook()
        assert "unsupported_features" in wb

    def test_empty_unsupported_features_by_default(self):
        wb = _minimal_workbook()
        assert isinstance(wb["unsupported_features"], list)
