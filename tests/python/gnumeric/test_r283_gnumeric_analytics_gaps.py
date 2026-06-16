"""
Tests for Gnumeric analytics gap closure (2 FOSS gaps).
Closes: GAP-GNUMERIC-FOSS-GNUMERIC_ROW-001, GAP-GNUMERIC-FOSS-GNUMERIC_SHE-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import (
    gnumeric_row_count_variance,
    gnumeric_sheet_name_lengths,
)

_GNUMERIC_MINIMAL = _REPO / "samples/by-format/gnumeric/minimal-spreadsheet.gnumeric"
_GNUMERIC_MULTI = _REPO / "samples/by-format/gnumeric/multi-cell-basic.gnumeric"
_GNUMERIC_EMPTY = _REPO / "samples/by-format/gnumeric/empty-sheet.gnumeric"


class TestGnumericRowCountVariance:
    def test_returns_float(self):
        assert isinstance(gnumeric_row_count_variance(_GNUMERIC_MINIMAL), float)

    def test_nonnegative(self):
        assert gnumeric_row_count_variance(_GNUMERIC_MINIMAL) >= 0.0

    def test_zero_for_single_sheet(self):
        # A single-sheet file has no variance across sheets
        assert gnumeric_row_count_variance(_GNUMERIC_MINIMAL) == 0.0

    def test_multi_cell_nonnegative(self):
        assert gnumeric_row_count_variance(_GNUMERIC_MULTI) >= 0.0


class TestGnumericSheetNameLengths:
    def test_returns_list(self):
        assert isinstance(gnumeric_sheet_name_lengths(_GNUMERIC_MINIMAL), list)

    def test_list_of_ints(self):
        result = gnumeric_sheet_name_lengths(_GNUMERIC_MINIMAL)
        for v in result:
            assert isinstance(v, int)

    def test_nonnegative_values(self):
        result = gnumeric_sheet_name_lengths(_GNUMERIC_MINIMAL)
        for v in result:
            assert v >= 0

    def test_nonempty_for_file_with_sheet(self):
        result = gnumeric_sheet_name_lengths(_GNUMERIC_MULTI)
        assert len(result) >= 1
