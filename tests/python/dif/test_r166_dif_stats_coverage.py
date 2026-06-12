"""
test_r166_dif_stats_coverage.py

Sprint: FORMAT-FACTORY-HARDENED-AUDIT-REMEDIATION-SPRINT7-001
Added: 2026-06-11

Tests for DIF stats functions: dif_stats, dif_numeric_range,
dif_string_value_list, dif_empty_row_count, dif_string_cell_count,
dif_vector_density.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif.dif_stats import (
    dif_stats,
    dif_numeric_range,
    dif_string_value_list,
    dif_empty_row_count,
    dif_string_cell_count,
    dif_vector_density,
)
from src.python.dif.dif_parser import parse_dif

_SAMPLES = _REPO / "samples" / "by-format" / "dif" / "valid"
_MINIMAL = _SAMPLES / "minimal-2x2.dif"


def _make_doc(rows, title="test", vectors=2, tuples=2):
    """Build a synthetic DIF doc dict as returned by parse_dif."""
    return {
        "ok": True,
        "title": title,
        "vectors": vectors,
        "tuples": tuples,
        "row_count": len(rows),
        "rows": rows,
    }


def _numeric_row(*values):
    return [{"type": "numeric", "value": v} for v in values]


def _string_row(*values):
    return [{"type": "string", "value": v} for v in values]


def _empty_row(n=2):
    return [{"type": "string", "value": ""} for _ in range(n)]


# ── dif_stats ─────────────────────────────────────────────────────────────

class TestDifStats:

    def test_returns_dict(self):
        doc = _make_doc([_numeric_row(1.0, 2.0)])
        result = dif_stats(doc)
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        doc = _make_doc([_numeric_row(1.0)])
        result = dif_stats(doc)
        for key in ("row_count", "total_cells", "numeric_cells", "string_cells", "empty_cells", "title"):
            assert key in result, f"missing key: {key}"

    def test_numeric_cell_count(self):
        doc = _make_doc([_numeric_row(1.0, 2.0, 3.0)])
        result = dif_stats(doc)
        assert result["numeric_cells"] == 3

    def test_string_cell_count(self):
        doc = _make_doc([_string_row("a", "b")])
        result = dif_stats(doc)
        assert result["string_cells"] == 2

    def test_empty_cell_count(self):
        doc = _make_doc([_empty_row(3)])
        result = dif_stats(doc)
        assert result["empty_cells"] == 3

    def test_from_sample_file(self):
        doc = parse_dif(_MINIMAL)
        result = dif_stats(doc)
        assert result["total_cells"] > 0

    def test_title_preserved(self):
        doc = _make_doc([_numeric_row(1.0)], title="MySheet")
        result = dif_stats(doc)
        assert result["title"] == "MySheet"


# ── dif_numeric_range ─────────────────────────────────────────────────────

class TestDifNumericRange:

    def test_returns_dict(self):
        doc = _make_doc([_numeric_row(1.0, 5.0)])
        result = dif_numeric_range(doc)
        assert isinstance(result, dict)

    def test_has_min_max_count(self):
        doc = _make_doc([_numeric_row(3.0, 7.0)])
        result = dif_numeric_range(doc)
        assert "min_value" in result
        assert "max_value" in result
        assert "numeric_count" in result

    def test_correct_min_max(self):
        doc = _make_doc([_numeric_row(10.0, 2.0, 7.0)])
        result = dif_numeric_range(doc)
        assert result["min_value"] == 2.0
        assert result["max_value"] == 10.0

    def test_count_matches(self):
        doc = _make_doc([_numeric_row(1.0, 2.0, 3.0)])
        result = dif_numeric_range(doc)
        assert result["numeric_count"] == 3

    def test_from_sample_file(self):
        doc = parse_dif(_MINIMAL)
        result = dif_numeric_range(doc)
        assert result["numeric_count"] >= 0


# ── dif_string_value_list ─────────────────────────────────────────────────

class TestDifStringValueList:

    def test_returns_list(self):
        doc = _make_doc([_string_row("hello", "world")])
        result = dif_string_value_list(doc)
        assert isinstance(result, list)

    def test_contains_string_values(self):
        doc = _make_doc([_string_row("foo", "bar")])
        result = dif_string_value_list(doc)
        assert "foo" in result
        assert "bar" in result

    def test_excludes_numeric(self):
        doc = _make_doc([_numeric_row(42.0), _string_row("text")])
        result = dif_string_value_list(doc)
        assert "text" in result
        assert 42.0 not in result

    def test_from_sample_file(self):
        doc = parse_dif(_MINIMAL)
        result = dif_string_value_list(doc)
        assert isinstance(result, list)


# ── dif_empty_row_count ───────────────────────────────────────────────────

class TestDifEmptyRowCount:

    def test_returns_int(self):
        doc = _make_doc([])
        result = dif_empty_row_count(doc)
        assert isinstance(result, int)

    def test_no_empty_rows(self):
        doc = _make_doc([_numeric_row(1.0, 2.0), _string_row("a", "b")])
        result = dif_empty_row_count(doc)
        assert result == 0

    def test_counts_empty_rows(self):
        doc = _make_doc([_numeric_row(1.0), _empty_row(2), _empty_row(2)])
        result = dif_empty_row_count(doc)
        assert result == 2

    def test_from_sample_file(self):
        doc = parse_dif(_MINIMAL)
        result = dif_empty_row_count(doc)
        assert result >= 0


# ── dif_string_cell_count ─────────────────────────────────────────────────

class TestDifStringCellCount:

    def test_returns_int(self):
        doc = _make_doc([_string_row("a")])
        result = dif_string_cell_count(doc)
        assert isinstance(result, int)

    def test_counts_string_cells(self):
        doc = _make_doc([_string_row("x", "y", "z")])
        result = dif_string_cell_count(doc)
        assert result == 3

    def test_ignores_numeric(self):
        doc = _make_doc([_numeric_row(1.0, 2.0), _string_row("only")])
        result = dif_string_cell_count(doc)
        assert result == 1


# ── dif_vector_density ────────────────────────────────────────────────────

class TestDifVectorDensity:

    def _make_density_doc(self, vectors_list):
        """Build a doc with vectors as list of dicts (as dif_vector_density expects)."""
        return {"vectors": vectors_list}

    def test_returns_dict(self):
        doc = self._make_density_doc([])
        result = dif_vector_density(doc)
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        doc = self._make_density_doc([])
        result = dif_vector_density(doc)
        for key in ("total_vectors", "total_tuples", "non_empty_tuples", "density"):
            assert key in result

    def test_empty_vectors(self):
        doc = self._make_density_doc([])
        result = dif_vector_density(doc)
        assert result["total_vectors"] == 0
        assert result["density"] == 0.0

    def test_density_calculation(self):
        # 1 vector with 2 non-empty + 1 empty tuple → density = 2/3
        doc = self._make_density_doc([
            {"tuples": [{"value": 1}, {"value": 2}, {"value": None}]}
        ])
        result = dif_vector_density(doc)
        assert result["total_vectors"] == 1
        assert result["non_empty_tuples"] == 2
        assert result["total_tuples"] == 3
