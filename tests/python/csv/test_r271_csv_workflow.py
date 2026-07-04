"""
tests/python/csv/test_r271_csv_workflow.py

Sprint: ff-sprint-s271-csv-installed-workflow-20260626
Authority: RFC 4180 (IETF) — Common Format and MIME Type for CSV Files

Tests for csv_installed_workflow() in csv_workflow.py.
Note: Uses src.python.csv path due to stdlib csv shadowing.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_workflow import csv_installed_workflow

_CSV_BYTES = b"name,age,city\nAlice,30,London\nBob,25,Paris\n"
_SAMPLE = _REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv"


class TestCsvInstalledWorkflowImport:
    """csv_installed_workflow is importable and callable."""

    def test_importable_from_csv_workflow(self):
        from src.python.csv.csv_workflow import csv_installed_workflow as fn
        assert callable(fn)

    def test_callable(self):
        assert callable(csv_installed_workflow)


class TestCsvInstalledWorkflowOutput:
    """csv_installed_workflow returns correct output structure."""

    def test_returns_dict(self):
        result = csv_installed_workflow(_CSV_BYTES)
        assert isinstance(result, dict)

    def test_format_field_is_csv(self):
        result = csv_installed_workflow(_CSV_BYTES)
        assert result["format"] == "csv"

    def test_loaded_field_is_true(self):
        result = csv_installed_workflow(_CSV_BYTES)
        assert result["loaded"] is True

    def test_row_count_is_integer(self):
        result = csv_installed_workflow(_CSV_BYTES)
        assert isinstance(result["row_count"], int)

    def test_row_count_correct(self):
        result = csv_installed_workflow(_CSV_BYTES)
        assert result["row_count"] == 2

    def test_column_count_correct(self):
        result = csv_installed_workflow(_CSV_BYTES)
        assert result["column_count"] == 3

    def test_has_all_required_keys(self):
        result = csv_installed_workflow(_CSV_BYTES)
        assert {"format", "loaded", "row_count", "column_count"}.issubset(result.keys())

    def test_consistent_across_calls(self):
        r1 = csv_installed_workflow(_CSV_BYTES)
        r2 = csv_installed_workflow(_CSV_BYTES)
        assert r1["row_count"] == r2["row_count"]
        assert r1["column_count"] == r2["column_count"]

    def test_sample_file(self):
        result = csv_installed_workflow(str(_SAMPLE))
        assert result["loaded"] is True
        assert result["format"] == "csv"
        assert result["row_count"] >= 1
