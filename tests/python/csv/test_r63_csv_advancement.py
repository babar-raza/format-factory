"""
test_r63_csv_advancement.py — R63 Train I: CSV format track advancement.

New capability: csv_row_length_distribution(csv_doc)
  Returns distribution of row lengths (column counts) across the CSV.

R63 Sprint: FORMAT-FACTORY-R63-AI-ASSISTED-RC-CLOSURE-AND-WORKAHEAD-MULTI-SPRINT-MEGA-TRAIN-001
Train I — CSV format track advancement
"""
from __future__ import annotations
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from src.python.ff_csv.csv_stats import csv_row_length_distribution


class TestCsvRowLengthDistribution:
    def test_empty_doc(self):
        result = csv_row_length_distribution({"rows": []})
        assert result["total_rows"] == 0
        assert result["min_length"] is None
        assert result["max_length"] is None
        assert result["is_uniform"] is True

    def test_uniform_rows(self):
        doc = {"rows": [["a", "b"], ["c", "d"], ["e", "f"]]}
        result = csv_row_length_distribution(doc)
        assert result["total_rows"] == 3
        assert result["is_uniform"] is True
        assert result["by_length"] == {2: 3}

    def test_jagged_rows(self):
        doc = {"rows": [["a", "b"], ["c"], ["d", "e", "f"]]}
        result = csv_row_length_distribution(doc)
        assert result["is_uniform"] is False
        assert result["min_length"] == 1
        assert result["max_length"] == 3

    def test_single_row(self):
        doc = {"rows": [["x", "y", "z"]]}
        result = csv_row_length_distribution(doc)
        assert result["total_rows"] == 1
        assert result["by_length"] == {3: 1}

    def test_by_length_counts(self):
        doc = {"rows": [["a"], ["b"], ["c", "d"]]}
        result = csv_row_length_distribution(doc)
        assert result["by_length"][1] == 2
        assert result["by_length"][2] == 1

    def test_returns_correct_keys(self):
        result = csv_row_length_distribution({"rows": []})
        for key in ["by_length", "min_length", "max_length", "is_uniform", "total_rows"]:
            assert key in result

    def test_callable_from_module(self):
        from src.python.ff_csv import csv_stats
        assert callable(csv_stats.csv_row_length_distribution)
