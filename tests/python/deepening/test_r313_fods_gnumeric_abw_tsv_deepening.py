"""Sprint 83 — FODS/GNUMERIC/ABW/TSV cycle 3 product deepening tests.

Functions under test:
  FODS:     fods_formula_cell_count, fods_sheet_row_variance
  Gnumeric: gnumeric_cell_count_variance, gnumeric_max_row_length
  ABW:      abw_line_count, abw_uppercase_ratio
  TSV:      tsv_field_length_sum, tsv_numeric_field_ratio
"""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

# FODS -------------------------------------------------------------------------
from src.python.fods.neutral_model import fods_formula_cell_count, fods_sheet_row_variance
from src.python.fods.parser import parse_fods

_FODS = _REPO / "samples" / "by-format" / "fods"

def _load_fods():
    samples = list(_FODS.glob("*.fods"))
    assert samples, "no FODS samples"
    return parse_fods(samples[0]), samples

def test_fods_formula_cell_count_type():
    wb, _ = _load_fods()
    r = fods_formula_cell_count(wb)
    assert isinstance(r, int)

def test_fods_formula_cell_count_non_negative():
    wb, _ = _load_fods()
    assert fods_formula_cell_count(wb) >= 0

def test_fods_sheet_row_variance_type():
    wb, _ = _load_fods()
    r = fods_sheet_row_variance(wb)
    assert isinstance(r, float)

def test_fods_sheet_row_variance_non_negative():
    wb, _ = _load_fods()
    assert fods_sheet_row_variance(wb) >= 0.0

# GNUMERIC ---------------------------------------------------------------------
from src.python.gnumeric.gnumeric_codec import gnumeric_cell_count_variance, gnumeric_max_row_length

_GNUMERIC = _REPO / "samples" / "by-format" / "gnumeric"

def test_gnumeric_cell_count_variance_type():
    samples = list(_GNUMERIC.glob("*.gnumeric"))
    assert samples
    r = gnumeric_cell_count_variance(samples[0])
    assert isinstance(r, float)

def test_gnumeric_cell_count_variance_non_negative():
    for s in _GNUMERIC.glob("*.gnumeric"):
        assert gnumeric_cell_count_variance(s) >= 0.0

def test_gnumeric_max_row_length_type():
    samples = list(_GNUMERIC.glob("*.gnumeric"))
    assert samples
    r = gnumeric_max_row_length(samples[0])
    assert isinstance(r, int)

def test_gnumeric_max_row_length_non_negative():
    for s in _GNUMERIC.glob("*.gnumeric"):
        assert gnumeric_max_row_length(s) >= 0

# ABW --------------------------------------------------------------------------
from src.python.abw.abw_codec import abw_line_count, abw_uppercase_ratio

_ABW = _REPO / "samples" / "by-format" / "abw"

def test_abw_line_count_type():
    samples = list(_ABW.glob("*.abw"))
    assert samples
    r = abw_line_count(samples[0])
    assert isinstance(r, int)

def test_abw_line_count_positive():
    for s in _ABW.glob("*.abw"):
        assert abw_line_count(s) >= 0

def test_abw_uppercase_ratio_type():
    samples = list(_ABW.glob("*.abw"))
    assert samples
    r = abw_uppercase_ratio(samples[0])
    assert isinstance(r, float)

def test_abw_uppercase_ratio_range():
    for s in _ABW.glob("*.abw"):
        r = abw_uppercase_ratio(s)
        assert 0.0 <= r <= 1.0, f"{s.name}: {r}"

# TSV --------------------------------------------------------------------------
from src.python.tsv.tsv_parser import tsv_field_length_sum, tsv_numeric_field_ratio

_TSV = _REPO / "samples" / "by-format" / "tsv"

def test_tsv_field_length_sum_type():
    samples = list(_TSV.glob("*.tsv"))
    assert samples
    r = tsv_field_length_sum(samples[0])
    assert isinstance(r, int)

def test_tsv_field_length_sum_non_negative():
    for s in _TSV.glob("*.tsv"):
        assert tsv_field_length_sum(s) >= 0

def test_tsv_numeric_field_ratio_type():
    samples = list(_TSV.glob("*.tsv"))
    assert samples
    r = tsv_numeric_field_ratio(samples[0])
    assert isinstance(r, float)

def test_tsv_numeric_field_ratio_range():
    for s in _TSV.glob("*.tsv"):
        r = tsv_numeric_field_ratio(s)
        assert 0.0 <= r <= 1.0, f"{s.name}: {r}"
