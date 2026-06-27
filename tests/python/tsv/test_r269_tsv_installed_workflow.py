"""
tests/python/tsv/test_r269_tsv_installed_workflow.py

Sprint: ff-sprint-s269-tsv-ndjson-installed-workflow-20260626
Authority: IANA text/tab-separated-values

Tests for tsv_installed_workflow() in tsv_workflow.py.
"""
from __future__ import annotations

import pytest

_TSV_BYTES = b"name\tage\tcity\nAlice\t30\tLondon\nBob\t25\tParis\n"
_TSV_EMPTY = b""
_TSV_HEADER_ONLY = b"col1\tcol2\tcol3\n"


class TestTsvInstalledWorkflowImport:
    """tsv_installed_workflow is importable and callable."""

    def test_importable_from_tsv_workflow(self):
        from tsv.tsv_workflow import tsv_installed_workflow
        assert callable(tsv_installed_workflow)

    def test_importable_from_package(self):
        import tsv
        assert hasattr(tsv, "tsv_installed_workflow")


class TestTsvInstalledWorkflowOutput:
    """tsv_installed_workflow returns correct output structure."""

    def test_returns_dict(self):
        from tsv.tsv_workflow import tsv_installed_workflow
        result = tsv_installed_workflow(_TSV_BYTES)
        assert isinstance(result, dict)

    def test_format_field_is_tsv(self):
        from tsv.tsv_workflow import tsv_installed_workflow
        result = tsv_installed_workflow(_TSV_BYTES)
        assert result["format"] == "tsv"

    def test_loaded_field_is_true(self):
        from tsv.tsv_workflow import tsv_installed_workflow
        result = tsv_installed_workflow(_TSV_BYTES)
        assert result["loaded"] is True

    def test_row_count_is_integer(self):
        from tsv.tsv_workflow import tsv_installed_workflow
        result = tsv_installed_workflow(_TSV_BYTES)
        assert isinstance(result["row_count"], int)

    def test_row_count_correct(self):
        from tsv.tsv_workflow import tsv_installed_workflow
        result = tsv_installed_workflow(_TSV_BYTES)
        assert result["row_count"] == 2

    def test_column_count_correct(self):
        from tsv.tsv_workflow import tsv_installed_workflow
        result = tsv_installed_workflow(_TSV_BYTES)
        assert result["column_count"] == 3

    def test_has_all_required_keys(self):
        from tsv.tsv_workflow import tsv_installed_workflow
        result = tsv_installed_workflow(_TSV_BYTES)
        assert {"format", "loaded", "row_count", "column_count"}.issubset(result.keys())

    def test_consistent_across_calls(self):
        from tsv.tsv_workflow import tsv_installed_workflow
        r1 = tsv_installed_workflow(_TSV_BYTES)
        r2 = tsv_installed_workflow(_TSV_BYTES)
        assert r1["row_count"] == r2["row_count"]
        assert r1["column_count"] == r2["column_count"]
