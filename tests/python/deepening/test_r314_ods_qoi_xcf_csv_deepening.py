"""Sprint 84 — ODS/QOI/XCF/CSV cycle 4 product deepening tests.

Functions under test:
  ODS:  ods_numeric_column_count, ods_row_cell_variance
  QOI:  qoi_channel_variance, qoi_red_blue_ratio
  XCF:  xcf_version_number, xcf_dimension_sum
  CSV:  csv_row_length_sum, csv_empty_field_ratio
"""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

# ODS -------------------------------------------------------------------------
from src.python.ods.ods_analytics import ods_numeric_column_count, ods_row_cell_variance

_ODS = _REPO / "samples" / "by-format" / "ods" / "valid"

def test_ods_numeric_column_count_type():
    samples = list(_ODS.glob("*.ods"))
    assert samples
    r = ods_numeric_column_count(samples[0])
    assert isinstance(r, int)

def test_ods_numeric_column_count_non_negative():
    for s in _ODS.glob("*.ods"):
        assert ods_numeric_column_count(s) >= 0

def test_ods_row_cell_variance_type():
    samples = list(_ODS.glob("*.ods"))
    assert samples
    r = ods_row_cell_variance(samples[0])
    assert isinstance(r, float)

def test_ods_row_cell_variance_non_negative():
    for s in _ODS.glob("*.ods"):
        assert ods_row_cell_variance(s) >= 0.0

# QOI -------------------------------------------------------------------------
from src.python.qoi.qoi_parser import qoi_channel_variance, qoi_red_blue_ratio

_QOI = _REPO / "samples" / "by-format" / "qoi" / "valid"

def test_qoi_channel_variance_type():
    samples = list(_QOI.glob("*.qoi"))
    assert samples
    r = qoi_channel_variance(samples[0])
    assert isinstance(r, float)

def test_qoi_channel_variance_non_negative():
    for s in _QOI.glob("*.qoi"):
        assert qoi_channel_variance(s) >= 0.0

def test_qoi_red_blue_ratio_type():
    samples = list(_QOI.glob("*.qoi"))
    assert samples
    r = qoi_red_blue_ratio(samples[0])
    assert isinstance(r, float)

def test_qoi_red_blue_ratio_non_negative():
    for s in _QOI.glob("*.qoi"):
        assert qoi_red_blue_ratio(s) >= 0.0

# XCF -------------------------------------------------------------------------
from src.python.xcf.xcf_parser import xcf_version_number, xcf_dimension_sum

_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"

def test_xcf_version_number_type():
    samples = list(_XCF.glob("*.xcf"))
    assert samples
    r = xcf_version_number(samples[0])
    assert isinstance(r, int)

def test_xcf_version_number_non_negative():
    for s in _XCF.glob("*.xcf"):
        assert xcf_version_number(s) >= 0

def test_xcf_dimension_sum_type():
    samples = list(_XCF.glob("*.xcf"))
    assert samples
    r = xcf_dimension_sum(samples[0])
    assert isinstance(r, int)

def test_xcf_dimension_sum_positive():
    for s in _XCF.glob("*.xcf"):
        assert xcf_dimension_sum(s) > 0

# CSV -------------------------------------------------------------------------
from src.python.ff_csv.csv_parser import csv_row_length_sum, csv_empty_field_ratio

_CSV = _REPO / "samples" / "by-format" / "csv"

def test_csv_row_length_sum_type():
    samples = list(_CSV.glob("*.csv"))
    assert samples
    r = csv_row_length_sum(samples[0])
    assert isinstance(r, int)

def test_csv_row_length_sum_non_negative():
    for s in _CSV.glob("*.csv"):
        assert csv_row_length_sum(s) >= 0

def test_csv_empty_field_ratio_type():
    samples = list(_CSV.glob("*.csv"))
    assert samples
    r = csv_empty_field_ratio(samples[0])
    assert isinstance(r, float)

def test_csv_empty_field_ratio_range():
    for s in _CSV.glob("*.csv"):
        r = csv_empty_field_ratio(s)
        assert 0.0 <= r <= 1.0, f"{s.name}: {r}"
