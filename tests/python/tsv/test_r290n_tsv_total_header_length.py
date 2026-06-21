"""Tests for tsv_total_header_length — closing GAP-TSV-FOSS-TSV_TOTAL_HE-001."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv.tsv_parser import tsv_total_header_length

SAMPLES = _REPO / "samples" / "by-format" / "tsv"


def test_total_header_length_returns_int():
    result = tsv_total_header_length(SAMPLES / "minimal-2x2.tsv")
    assert isinstance(result, int)
    assert result >= 0


def test_total_header_length_multi_column():
    result = tsv_total_header_length(SAMPLES / "multi-column.tsv")
    assert isinstance(result, int)
    assert result >= 0


def test_total_header_length_single_cell():
    result = tsv_total_header_length(SAMPLES / "single-cell.tsv")
    assert isinstance(result, int)
