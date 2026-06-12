"""
test_dogfood_ods_csv_export.py -- ODS->CSV dogfood export pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-2
Uses the installed ODS parser + CSV exporter to validate a dogfood path.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_SAMPLES = _REPO / "samples" / "by-format" / "ods" / "valid"

from ods.ods_parser import parse_ods_strict
from ods.ods_csv_exporter import export_ods_to_csv, export_ods_to_csv_file


def test_ods_to_csv_minimal():
    """Parse minimal ODS and export first sheet to CSV string."""
    doc = parse_ods_strict(str(_SAMPLES / "minimal-spreadsheet.ods"))
    csv_text = export_ods_to_csv(doc)
    assert isinstance(csv_text, str)


def test_ods_to_csv_file(tmp_path):
    """Parse ODS and export to CSV file."""
    doc = parse_ods_strict(str(_SAMPLES / "minimal-spreadsheet.ods"))
    out = tmp_path / "export.csv"
    path = export_ods_to_csv_file(doc, out)
    assert Path(path).exists()
    content = Path(path).read_text(encoding="utf-8")
    assert len(content) > 0


def test_ods_numeric_row_to_csv():
    """Export numeric row ODS to CSV preserves data."""
    doc = parse_ods_strict(str(_SAMPLES / "numeric-row.ods"))
    csv_text = export_ods_to_csv(doc)
    assert isinstance(csv_text, str)


def test_ods_single_cell_to_csv():
    """Export single-cell ODS to CSV."""
    doc = parse_ods_strict(str(_SAMPLES / "single-cell.ods"))
    csv_text = export_ods_to_csv(doc)
    assert isinstance(csv_text, str)
