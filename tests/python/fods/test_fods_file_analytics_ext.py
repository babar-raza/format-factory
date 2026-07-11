"""Tests for fods_file_analytics extension functions (ext2 batch)."""
from __future__ import annotations

from pathlib import Path

import pytest

from fods.fods_file_analytics import (
    fods_file_has_parse_errors,
    fods_file_odf_version,
    fods_file_has_warnings,
    fods_file_last_sheet_name,
    fods_file_sheet_row_counts,
    fods_file_max_sheet_row_count,
)

SAMPLES = Path("samples/by-format/fods")
MINIMAL = SAMPLES / "minimal-spreadsheet.fods"
MULTI = SAMPLES / "multi-sheet-basic.fods"
FORMULA = SAMPLES / "formula-basic.fods"


# --- fods_file_has_parse_errors ---

def test_has_parse_errors_minimal_false():
    assert fods_file_has_parse_errors(MINIMAL) is False


def test_has_parse_errors_multi_false():
    assert fods_file_has_parse_errors(MULTI) is False


def test_has_parse_errors_returns_bool():
    result = fods_file_has_parse_errors(MINIMAL)
    assert isinstance(result, bool)


# --- fods_file_odf_version ---

def test_odf_version_minimal_nonempty():
    version = fods_file_odf_version(MINIMAL)
    assert isinstance(version, str)
    assert len(version) > 0


def test_odf_version_multi_nonempty():
    version = fods_file_odf_version(MULTI)
    assert isinstance(version, str)
    assert len(version) > 0


def test_odf_version_formula_nonempty():
    version = fods_file_odf_version(FORMULA)
    assert isinstance(version, str)


# --- fods_file_has_warnings ---

def test_has_warnings_minimal_bool():
    result = fods_file_has_warnings(MINIMAL)
    assert isinstance(result, bool)


def test_has_warnings_multi_bool():
    result = fods_file_has_warnings(MULTI)
    assert isinstance(result, bool)


# --- fods_file_last_sheet_name ---

def test_last_sheet_name_minimal():
    name = fods_file_last_sheet_name(MINIMAL)
    assert isinstance(name, str)
    assert len(name) > 0


def test_last_sheet_name_multi():
    name = fods_file_last_sheet_name(MULTI)
    assert isinstance(name, str)
    assert len(name) > 0


def test_last_sheet_name_single_matches_first():
    from fods.fods_file_analytics import fods_file_first_sheet_name
    # single-sheet file: last == first
    assert fods_file_last_sheet_name(MINIMAL) == fods_file_first_sheet_name(MINIMAL)


def test_last_sheet_name_multi_differs_from_first():
    from fods.fods_file_analytics import fods_file_first_sheet_name
    last = fods_file_last_sheet_name(MULTI)
    first = fods_file_first_sheet_name(MULTI)
    assert last != first


# --- fods_file_sheet_row_counts ---

def test_sheet_row_counts_minimal_is_list():
    result = fods_file_sheet_row_counts(MINIMAL)
    assert isinstance(result, list)


def test_sheet_row_counts_minimal_length():
    from fods.fods_file_analytics import fods_file_sheet_count
    result = fods_file_sheet_row_counts(MINIMAL)
    assert len(result) == fods_file_sheet_count(MINIMAL)


def test_sheet_row_counts_multi_length():
    from fods.fods_file_analytics import fods_file_sheet_count
    result = fods_file_sheet_row_counts(MULTI)
    assert len(result) == fods_file_sheet_count(MULTI)


def test_sheet_row_counts_values_are_ints():
    result = fods_file_sheet_row_counts(MINIMAL)
    assert all(isinstance(v, int) for v in result)


# --- fods_file_max_sheet_row_count ---

def test_max_sheet_row_count_minimal_positive():
    result = fods_file_max_sheet_row_count(MINIMAL)
    assert isinstance(result, int)
    assert result >= 0


def test_max_sheet_row_count_multi_positive():
    result = fods_file_max_sheet_row_count(MULTI)
    assert result > 0


def test_max_sheet_row_count_geq_any_sheet():
    counts = fods_file_sheet_row_counts(MULTI)
    max_val = fods_file_max_sheet_row_count(MULTI)
    assert all(max_val >= c for c in counts)
