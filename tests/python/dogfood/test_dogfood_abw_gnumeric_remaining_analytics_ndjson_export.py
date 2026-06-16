"""
tests/python/dogfood/test_dogfood_abw_gnumeric_remaining_analytics_ndjson_export.py

Dogfood export: ABW remaining (char_density, longest_paragraph_length) +
Gnumeric remaining (cell_count_all_sheets, is_single_sheet, empty_sheet_count,
data_density, avg_row_count, nonempty_density, total_string_length) -> NDJSON -> verify.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import abw_char_density, abw_longest_paragraph_length
from gnumeric.gnumeric_codec import (
    gnumeric_cell_count_all_sheets,
    gnumeric_is_single_sheet,
    gnumeric_empty_sheet_count,
    gnumeric_data_density,
    gnumeric_avg_row_count,
    gnumeric_nonempty_density,
    gnumeric_total_string_length,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_ABW = _REPO / "samples" / "by-format" / "abw"
_GN = _REPO / "samples" / "by-format" / "gnumeric"


def test_abw_char_density(tmp_path):
    path = str(_ABW / "two-paragraphs.abw")
    density = abw_char_density(path)
    assert density == 16.5
    record = {"file": "two-paragraphs.abw", "abw_char_density": float(density)}
    out = tmp_path / "abw_char_density.ndjson"
    write_ndjson([record], str(out))
    rows = load_ndjson(str(out))
    assert rows[0]["abw_char_density"] == 16.5


def test_abw_longest_paragraph_length(tmp_path):
    path = str(_ABW / "two-paragraphs.abw")
    length = abw_longest_paragraph_length(path)
    assert length == 17
    record = {"file": "two-paragraphs.abw", "abw_longest_paragraph_length": int(length)}
    out = tmp_path / "abw_longest.ndjson"
    write_ndjson([record], str(out))
    rows = load_ndjson(str(out))
    assert rows[0]["abw_longest_paragraph_length"] == 17


def test_gnumeric_cell_count_all_sheets(tmp_path):
    path = str(_GN / "multi-cell-basic.gnumeric")
    count = gnumeric_cell_count_all_sheets(path)
    assert count == 4
    assert gnumeric_is_single_sheet(path) is True
    record = {"file": "multi-cell-basic.gnumeric", "cell_count_all_sheets": count,
              "is_single_sheet": True}
    out = tmp_path / "gn_cell_count.ndjson"
    write_ndjson([record], str(out))
    rows = load_ndjson(str(out))
    assert rows[0]["cell_count_all_sheets"] == 4


def test_gnumeric_empty_sheet_count(tmp_path):
    path_empty = str(_GN / "empty-sheet.gnumeric")
    path_multi = str(_GN / "multi-cell-basic.gnumeric")
    assert gnumeric_empty_sheet_count(path_empty) == 1
    assert gnumeric_empty_sheet_count(path_multi) == 0
    records = [
        {"file": "empty-sheet.gnumeric", "empty_sheet_count": 1},
        {"file": "multi-cell-basic.gnumeric", "empty_sheet_count": 0},
    ]
    out = tmp_path / "gn_empty_sheet.ndjson"
    write_ndjson(records, str(out))
    rows = load_ndjson(str(out))
    assert rows[0]["empty_sheet_count"] == 1
    assert rows[1]["empty_sheet_count"] == 0


def test_gnumeric_data_density_and_nonempty(tmp_path):
    path_empty = str(_GN / "empty-sheet.gnumeric")
    path_multi = str(_GN / "multi-cell-basic.gnumeric")
    assert gnumeric_data_density(path_multi) == 1.0
    assert gnumeric_nonempty_density(path_empty) == 0.0
    assert gnumeric_nonempty_density(path_multi) == 1.0
    records = [
        {"file": "empty-sheet.gnumeric", "nonempty_density": 0.0},
        {"file": "multi-cell-basic.gnumeric", "data_density": 1.0, "nonempty_density": 1.0},
    ]
    out = tmp_path / "gn_density.ndjson"
    write_ndjson(records, str(out))
    rows = load_ndjson(str(out))
    assert rows[0]["nonempty_density"] == 0.0
    assert rows[1]["data_density"] == 1.0


def test_gnumeric_total_string_length(tmp_path):
    path = str(_GN / "multi-cell-basic.gnumeric")
    length = gnumeric_total_string_length(path)
    assert length == 16
    record = {"file": "multi-cell-basic.gnumeric", "total_string_length": int(length)}
    out = tmp_path / "gn_string_len.ndjson"
    write_ndjson([record], str(out))
    rows = load_ndjson(str(out))
    assert rows[0]["total_string_length"] == 16


def test_gnumeric_avg_row_count(tmp_path):
    path = str(_GN / "multi-cell-basic.gnumeric")
    avg = gnumeric_avg_row_count(path)
    assert isinstance(avg, float)
    record = {"file": "multi-cell-basic.gnumeric", "avg_row_count": avg}
    out = tmp_path / "gn_avg_row.ndjson"
    write_ndjson([record], str(out))
    rows = load_ndjson(str(out))
    assert isinstance(rows[0]["avg_row_count"], float)
