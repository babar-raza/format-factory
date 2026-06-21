"""Tests for DIF probe_dif product deepening.

Product deepening: GAP-DIF-FOSS-PROBE_DIF-001
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.dif import probe_dif

_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
_MINIMAL = str(_DIR / "minimal-2x2.dif")
_NUMERIC = str(_DIR / "numeric-row.dif")
_SINGLE = str(_DIR / "single-cell.dif")


class TestProbeDif:
    def test_return_type_is_dict(self):
        result = probe_dif(_MINIMAL)
        assert isinstance(result, dict)

    def test_has_exists_key(self):
        result = probe_dif(_MINIMAL)
        assert "exists" in result

    def test_exists_true_for_valid_file(self):
        result = probe_dif(_MINIMAL)
        assert result["exists"] is True

    def test_has_valid_header_key(self):
        result = probe_dif(_MINIMAL)
        assert "valid_header" in result

    def test_valid_header_true_for_minimal(self):
        result = probe_dif(_MINIMAL)
        assert result["valid_header"] is True

    def test_has_title_key(self):
        result = probe_dif(_MINIMAL)
        assert "title" in result

    def test_exact_title_minimal(self):
        result = probe_dif(_MINIMAL)
        assert result["title"] == "minimal"

    def test_exact_title_numeric_row(self):
        result = probe_dif(_NUMERIC)
        assert result["title"] == "numeric-row"

    def test_has_vectors_key(self):
        result = probe_dif(_MINIMAL)
        assert "vectors" in result

    def test_exact_2_vectors_for_minimal(self):
        result = probe_dif(_MINIMAL)
        assert result["vectors"] == 2

    def test_exact_1_vector_for_single_cell(self):
        result = probe_dif(_SINGLE)
        assert result["vectors"] == 1

    def test_exact_3_vectors_for_numeric_row(self):
        result = probe_dif(_NUMERIC)
        assert result["vectors"] == 3
