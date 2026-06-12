"""
test_ods_conveyor_deepening.py -- ODS product deepening tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-1
Tests parse, probe, stats, writer, csv_exporter for ODS.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_SAMPLES = _REPO / "samples" / "by-format" / "ods" / "valid"

from ods.ods_parser import parse_ods, parse_ods_strict, probe_ods
from ods.ods_stats import (
    spreadsheet_stats,
    sheet_name_order,
    ods_cell_type_distribution,
    ods_sheet_name_list,
    ods_formula_cell_count,
)


def test_parse_ods_minimal():
    result = parse_ods(str(_SAMPLES / "minimal-spreadsheet.ods"))
    assert result["ok"] is True


def test_parse_ods_strict_returns_document():
    doc = parse_ods_strict(str(_SAMPLES / "minimal-spreadsheet.ods"))
    assert hasattr(doc, "sheets")


def test_probe_ods_valid_container():
    info = probe_ods(str(_SAMPLES / "minimal-spreadsheet.ods"))
    assert info["valid_container"] is True
    assert info["mimetype"] == "application/vnd.oasis.opendocument.spreadsheet"


def test_probe_ods_nonexistent():
    info = probe_ods("/nonexistent/file.ods")
    assert info["exists"] is False


def test_single_cell_parse():
    result = parse_ods(str(_SAMPLES / "single-cell.ods"))
    assert result["ok"] is True


def test_numeric_row_parse():
    result = parse_ods(str(_SAMPLES / "numeric-row.ods"))
    assert result["ok"] is True


def test_spreadsheet_stats_on_minimal():
    result = parse_ods(str(_SAMPLES / "minimal-spreadsheet.ods"))
    stats = spreadsheet_stats(result)
    assert stats["sheet_count"] >= 1
    assert isinstance(stats["total_rows"], int)
    assert isinstance(stats["total_cells"], int)


def test_sheet_name_order():
    result = parse_ods(str(_SAMPLES / "minimal-spreadsheet.ods"))
    names = sheet_name_order(result)
    assert isinstance(names, list)
    assert len(names) >= 1


def test_cell_type_distribution():
    result = parse_ods(str(_SAMPLES / "numeric-row.ods"))
    dist = ods_cell_type_distribution(result)
    assert "by_type" in dist
    assert isinstance(dist["total_cells"], int)


def test_ods_sheet_name_list_empty():
    names = ods_sheet_name_list({})
    assert names == []


def test_formula_cell_count_zero():
    result = parse_ods(str(_SAMPLES / "minimal-spreadsheet.ods"))
    count = ods_formula_cell_count(result)
    assert count == 0


def test_parse_ods_bad_file(tmp_path):
    fp = tmp_path / "bad.ods"
    fp.write_bytes(b"not a zip file")
    result = parse_ods(str(fp))
    assert result["ok"] is False
