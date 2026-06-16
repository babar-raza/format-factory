"""Sprint 69 — TSV / ABW / ODT / ODS product deepening (R299).

Tests 8 new analytics functions:
  TSV: tsv_min_field_count, tsv_nonempty_row_ratio
  ABW: abw_whitespace_ratio, abw_avg_sentence_length
  ODT: odt_is_multi_paragraph, odt_whitespace_ratio
  ODS: ods_max_sheet_row_count, ods_is_rectangular
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv import tsv_min_field_count, tsv_nonempty_row_ratio
from src.python.abw import abw_whitespace_ratio, abw_avg_sentence_length
from src.python.odt import odt_is_multi_paragraph, odt_whitespace_ratio
from src.python.ods import ods_max_sheet_row_count, ods_is_rectangular

_TSV = _REPO / "samples" / "by-format" / "tsv" / "minimal-2x2.tsv"
_ABW = _REPO / "samples" / "by-format" / "abw" / "minimal-document.abw"
_ODT = _REPO / "samples" / "by-format" / "odt" / "valid" / "minimal-document.odt"
_ODS = _REPO / "samples" / "by-format" / "ods" / "valid" / "minimal-spreadsheet.ods"


class TestTsvMinFieldCount:
    def test_returns_int(self):
        assert isinstance(tsv_min_field_count(_TSV), int)

    def test_positive(self):
        assert tsv_min_field_count(_TSV) > 0


class TestTsvNonemptyRowRatio:
    def test_returns_float(self):
        assert isinstance(tsv_nonempty_row_ratio(_TSV), (int, float))

    def test_between_zero_and_one(self):
        ratio = tsv_nonempty_row_ratio(_TSV)
        assert 0.0 <= ratio <= 1.0


class TestAbwWhitespaceRatio:
    def test_returns_float(self):
        assert isinstance(abw_whitespace_ratio(_ABW), (int, float))

    def test_between_zero_and_one(self):
        ratio = abw_whitespace_ratio(_ABW)
        assert 0.0 <= ratio <= 1.0


class TestAbwAvgSentenceLength:
    def test_returns_float(self):
        assert isinstance(abw_avg_sentence_length(_ABW), (int, float))

    def test_nonnegative(self):
        assert abw_avg_sentence_length(_ABW) >= 0.0


class TestOdtIsMultiParagraph:
    def test_returns_bool(self):
        assert isinstance(odt_is_multi_paragraph(_ODT), bool)


class TestOdtWhitespaceRatio:
    def test_returns_float(self):
        assert isinstance(odt_whitespace_ratio(_ODT), (int, float))

    def test_between_zero_and_one(self):
        ratio = odt_whitespace_ratio(_ODT)
        assert 0.0 <= ratio <= 1.0


class TestOdsMaxSheetRowCount:
    def test_returns_int(self):
        assert isinstance(ods_max_sheet_row_count(_ODS), int)

    def test_nonnegative(self):
        assert ods_max_sheet_row_count(_ODS) >= 0


class TestOdsIsRectangular:
    def test_returns_bool(self):
        assert isinstance(ods_is_rectangular(_ODS), bool)
