"""
test_gnumeric_export_content.py -- Gnumeric export_to_csv and export_to_json content verification.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-14
Tests export_to_csv and export_to_json with exact content assertions
from real sample files.
"""
from __future__ import annotations

import sys
import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_SAMPLES = _REPO / "samples" / "by-format" / "gnumeric"

from gnumeric.gnumeric_codec import export_to_csv, export_to_json


def test_export_to_csv_contains_header():
    csv = export_to_csv(str(_SAMPLES / "multi-cell-basic.gnumeric"))
    assert "Name" in csv
    assert "Score" in csv


def test_export_to_csv_contains_data():
    csv = export_to_csv(str(_SAMPLES / "multi-cell-basic.gnumeric"))
    assert "Alice" in csv
    assert "42" in csv


def test_export_to_csv_has_two_rows():
    csv = export_to_csv(str(_SAMPLES / "multi-cell-basic.gnumeric"))
    rows = [r for r in csv.strip().splitlines() if r.strip()]
    assert len(rows) == 2


def test_export_to_csv_comma_separated():
    csv = export_to_csv(str(_SAMPLES / "multi-cell-basic.gnumeric"))
    first_line = csv.strip().splitlines()[0]
    assert "," in first_line


def test_export_to_json_is_valid():
    j = export_to_json(str(_SAMPLES / "multi-cell-basic.gnumeric"))
    data = json.loads(j)
    assert isinstance(data, list)


def test_export_to_json_has_sheet():
    j = export_to_json(str(_SAMPLES / "multi-cell-basic.gnumeric"))
    data = json.loads(j)
    assert len(data) >= 1
    assert data[0]["name"] == "Sheet1"


def test_export_to_json_rows_content():
    j = export_to_json(str(_SAMPLES / "multi-cell-basic.gnumeric"))
    data = json.loads(j)
    rows = data[0]["rows"]
    assert rows[0] == ["Name", "Score"]
    assert rows[1] == ["Alice", "42"]


def test_export_to_csv_minimal():
    csv = export_to_csv(str(_SAMPLES / "minimal-spreadsheet.gnumeric"))
    assert "Hello" in csv
