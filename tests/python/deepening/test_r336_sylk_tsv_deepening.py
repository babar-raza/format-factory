"""Sprint 126 deepening – SYLK bytes_per_cell/bytes_per_row, TSV bytes_per_field/bytes_per_row."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.sylk.sylk_parser import sylk_bytes_per_cell, sylk_bytes_per_row
from src.python.tsv.tsv_parser import tsv_bytes_per_field, tsv_bytes_per_row

SYLK = _REPO / "samples" / "by-format" / "sylk" / "valid"
TSV = _REPO / "samples" / "by-format" / "tsv"


# --- sylk_bytes_per_cell ---

class TestSylkBytesPerCell:
    def test_minimal(self):
        assert abs(sylk_bytes_per_cell(SYLK / "minimal-2x2.slk") - 18.75) < 0.01

    def test_numeric(self):
        assert abs(sylk_bytes_per_cell(SYLK / "numeric-row.slk") - 15.0) < 0.01

    def test_single(self):
        assert abs(sylk_bytes_per_cell(SYLK / "single-cell.slk") - 22.0) < 0.01

    def test_returns_float(self):
        assert isinstance(sylk_bytes_per_cell(SYLK / "minimal-2x2.slk"), float)

    def test_positive(self):
        assert sylk_bytes_per_cell(SYLK / "minimal-2x2.slk") > 0


# --- sylk_bytes_per_row ---

class TestSylkBytesPerRow:
    def test_minimal(self):
        assert abs(sylk_bytes_per_row(SYLK / "minimal-2x2.slk") - 37.5) < 0.01

    def test_numeric(self):
        assert abs(sylk_bytes_per_row(SYLK / "numeric-row.slk") - 45.0) < 0.01

    def test_single(self):
        assert abs(sylk_bytes_per_row(SYLK / "single-cell.slk") - 22.0) < 0.01

    def test_returns_float(self):
        assert isinstance(sylk_bytes_per_row(SYLK / "minimal-2x2.slk"), float)

    def test_positive(self):
        assert sylk_bytes_per_row(SYLK / "minimal-2x2.slk") > 0


# --- tsv_bytes_per_field ---

class TestTsvBytesPerField:
    def test_minimal(self):
        assert abs(tsv_bytes_per_field(TSV / "minimal-2x2.tsv") - 7.0) < 0.01

    def test_multi(self):
        assert abs(tsv_bytes_per_field(TSV / "multi-column.tsv") - 7.125) < 0.01

    def test_single(self):
        assert abs(tsv_bytes_per_field(TSV / "single-cell.tsv") - 11.0) < 0.01

    def test_returns_float(self):
        assert isinstance(tsv_bytes_per_field(TSV / "minimal-2x2.tsv"), float)

    def test_positive(self):
        assert tsv_bytes_per_field(TSV / "minimal-2x2.tsv") > 0


# --- tsv_bytes_per_row ---

class TestTsvBytesPerRow:
    def test_minimal(self):
        assert abs(tsv_bytes_per_row(TSV / "minimal-2x2.tsv") - 14.0) < 0.01

    def test_multi(self):
        assert abs(tsv_bytes_per_row(TSV / "multi-column.tsv") - 28.5) < 0.01

    def test_single(self):
        assert abs(tsv_bytes_per_row(TSV / "single-cell.tsv") - 11.0) < 0.01

    def test_returns_float(self):
        assert isinstance(tsv_bytes_per_row(TSV / "minimal-2x2.tsv"), float)

    def test_positive(self):
        assert tsv_bytes_per_row(TSV / "minimal-2x2.tsv") > 0
