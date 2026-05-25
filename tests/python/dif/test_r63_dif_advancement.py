"""
test_r63_dif_advancement.py — R63 Train I: DIF format track advancement.

New capability: dif_vector_density(dif_doc)
  Returns density statistics for DIF vectors (rows) and their tuples (cells).

R63 Sprint: FORMAT-FACTORY-R63-AI-ASSISTED-RC-CLOSURE-AND-WORKAHEAD-MULTI-SPRINT-MEGA-TRAIN-001
Train I — DIF format track advancement
"""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from src.python.dif.dif_stats import dif_vector_density


def _doc(vectors_data):
    """Build minimal DIF doc from list of (value,) per tuple per vector."""
    vectors = []
    for row in vectors_data:
        tuples = [{"value": v} for v in row]
        vectors.append({"tuples": tuples})
    return {"vectors": vectors}


class TestDifVectorDensity:
    def test_empty_doc(self):
        result = dif_vector_density({"vectors": []})
        assert result["total_vectors"] == 0
        assert result["total_tuples"] == 0
        assert result["density"] == 0.0

    def test_all_non_empty(self):
        doc = _doc([[1, 2, 3], [4, 5, 6]])
        result = dif_vector_density(doc)
        assert result["total_vectors"] == 2
        assert result["total_tuples"] == 6
        assert result["non_empty_tuples"] == 6
        assert result["density"] == 1.0

    def test_with_empty_values(self):
        doc = _doc([[1, None, 3], [None, None]])
        result = dif_vector_density(doc)
        assert result["total_tuples"] == 5
        assert result["non_empty_tuples"] == 2

    def test_single_vector(self):
        doc = _doc([[42]])
        result = dif_vector_density(doc)
        assert result["total_vectors"] == 1
        assert result["avg_tuples_per_vector"] == 1.0

    def test_density_fraction(self):
        doc = _doc([[1, None, 1, None]])  # 2 of 4 non-empty
        result = dif_vector_density(doc)
        assert result["density"] == 0.5

    def test_returns_correct_keys(self):
        result = dif_vector_density({"vectors": []})
        for key in ["total_vectors", "total_tuples", "non_empty_tuples", "density", "avg_tuples_per_vector"]:
            assert key in result

    def test_callable_from_module(self):
        from src.python.dif import dif_stats
        assert callable(dif_stats.dif_vector_density)
