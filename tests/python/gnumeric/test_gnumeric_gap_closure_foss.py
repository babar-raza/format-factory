"""
Gnumeric FOSS gap closure tests.

Closes:
  GAP-Gnumeric-FOSS-GNUMERIC_SHE-001  — gnumeric_sheet_name_lengths
  GAP-Gnumeric-FOSS-GNUMERIC_LON-001  — gnumeric_longest_row_index

Run from repo root:
    python -m pytest tests/python/gnumeric/test_gnumeric_gap_closure_foss.py -v
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

from gnumeric.gnumeric_codec import gnumeric_sheet_name_lengths, gnumeric_longest_row_index

SAMPLES = REPO_ROOT / "samples" / "by-format" / "gnumeric"
EMPTY = SAMPLES / "empty-sheet.gnumeric"
MINIMAL = SAMPLES / "minimal-spreadsheet.gnumeric"
MULTI = SAMPLES / "multi-cell-basic.gnumeric"


# ---------------------------------------------------------------------------
# GAP-Gnumeric-FOSS-GNUMERIC_SHE-001 — gnumeric_sheet_name_lengths
# ---------------------------------------------------------------------------

class TestGnumericSheetNameLengths:
    def test_empty_returns_list(self):
        result = gnumeric_sheet_name_lengths(EMPTY)
        assert isinstance(result, list)

    def test_empty_has_one_sheet(self):
        assert len(gnumeric_sheet_name_lengths(EMPTY)) == 1

    def test_empty_sheet_name_length(self):
        # empty-sheet.gnumeric has sheet named "Sheet" (5 chars)
        assert gnumeric_sheet_name_lengths(EMPTY) == [5]

    def test_minimal_sheet_name_length(self):
        # minimal-spreadsheet.gnumeric has sheet with 6-char name
        assert gnumeric_sheet_name_lengths(MINIMAL) == [6]

    def test_all_lengths_positive(self):
        for p in [EMPTY, MINIMAL, MULTI]:
            for length in gnumeric_sheet_name_lengths(p):
                assert length > 0


# ---------------------------------------------------------------------------
# GAP-Gnumeric-FOSS-GNUMERIC_LON-001 — gnumeric_longest_row_index
# ---------------------------------------------------------------------------

class TestGnumericLongestRowIndex:
    def test_empty_returns_minus_one(self):
        # empty sheet has no rows
        assert gnumeric_longest_row_index(EMPTY) == -1

    def test_minimal_returns_zero(self):
        # single-row sheet: longest row is at index 0
        assert gnumeric_longest_row_index(MINIMAL) == 0

    def test_multi_returns_non_negative(self):
        assert gnumeric_longest_row_index(MULTI) >= 0

    def test_returns_int(self):
        assert isinstance(gnumeric_longest_row_index(MINIMAL), int)
