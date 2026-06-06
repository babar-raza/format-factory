"""
Tests for Gnumeric export_to_csv() — R117 pilot.

Sprint: FORMAT-FACTORY-HOST-PROOFED-AUTONOMOUS-FORMAT-PILOT-001
Track: python-foss

Verifies:
- export_to_csv() produces valid CSV from Gnumeric samples
- Positional (Row/Col) grid is respected
- Empty sheets produce empty CSV
- Sheet index out of range raises GnumericError
"""

from __future__ import annotations

from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "src" / "python"))

from gnumeric.gnumeric_codec import (
    GnumericError,
    export_to_csv,
    load,
)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SAMPLES_DIR = REPO_ROOT / "samples" / "by-format" / "gnumeric"


# ---------------------------------------------------------------------------
# Basic export
# ---------------------------------------------------------------------------

class TestExportToCsv:
    def test_minimal_produces_nonempty_csv(self):
        csv_str = export_to_csv(SAMPLES_DIR / "minimal-spreadsheet.gnumeric")
        assert isinstance(csv_str, str)
        assert len(csv_str) > 0

    def test_minimal_contains_hello(self):
        csv_str = export_to_csv(SAMPLES_DIR / "minimal-spreadsheet.gnumeric")
        assert "Hello" in csv_str

    def test_multi_cell_headers_present(self):
        csv_str = export_to_csv(SAMPLES_DIR / "multi-cell-basic.gnumeric")
        assert "Name" in csv_str
        assert "Score" in csv_str

    def test_multi_cell_values_present(self):
        csv_str = export_to_csv(SAMPLES_DIR / "multi-cell-basic.gnumeric")
        assert "Alice" in csv_str
        assert "42" in csv_str

    def test_multi_cell_row_count(self):
        csv_str = export_to_csv(SAMPLES_DIR / "multi-cell-basic.gnumeric")
        lines = [l for l in csv_str.splitlines() if l.strip()]
        assert len(lines) == 2  # header row + data row

    def test_empty_sheet_returns_empty_string(self):
        csv_str = export_to_csv(SAMPLES_DIR / "empty-sheet.gnumeric")
        assert csv_str == ""

    def test_csv_uses_comma_delimiter(self):
        csv_str = export_to_csv(SAMPLES_DIR / "multi-cell-basic.gnumeric")
        first_line = csv_str.splitlines()[0]
        assert "," in first_line

    def test_custom_delimiter(self):
        csv_str = export_to_csv(SAMPLES_DIR / "multi-cell-basic.gnumeric", delimiter="\t")
        first_line = csv_str.splitlines()[0]
        assert "\t" in first_line

    def test_out_of_range_sheet_index_raises(self):
        with pytest.raises(GnumericError):
            export_to_csv(SAMPLES_DIR / "minimal-spreadsheet.gnumeric", sheet_index=99)

    def test_negative_sheet_index_raises(self):
        with pytest.raises(GnumericError):
            export_to_csv(SAMPLES_DIR / "minimal-spreadsheet.gnumeric", sheet_index=-1)


# ---------------------------------------------------------------------------
# Grid correctness
# ---------------------------------------------------------------------------

class TestGridCorrectness:
    def test_multi_cell_grid_column_alignment(self):
        csv_str = export_to_csv(SAMPLES_DIR / "multi-cell-basic.gnumeric")
        lines = csv_str.splitlines()
        header_cols = lines[0].split(",")
        data_cols = lines[1].split(",")
        assert len(header_cols) == len(data_cols)

    def test_multi_cell_first_row_is_name_score(self):
        csv_str = export_to_csv(SAMPLES_DIR / "multi-cell-basic.gnumeric")
        first_row = csv_str.splitlines()[0]
        assert first_row.startswith("Name")
        assert "Score" in first_row

    def test_multi_cell_second_row_is_alice_42(self):
        csv_str = export_to_csv(SAMPLES_DIR / "multi-cell-basic.gnumeric")
        second_row = csv_str.splitlines()[1]
        assert "Alice" in second_row
        assert "42" in second_row
