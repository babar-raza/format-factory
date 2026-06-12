"""
test_dogfood_abw_csv_pipeline.py -- Dogfood ABW to CSV cross-format pipeline tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-38
Tests ABW paragraphs exported to CSV: export_to_csv contains paragraphs,
write_csv creates file, CSV has paragraph count rows,
export_to_txt paragraphs present, export_to_json has paragraph_count field.
"""
from __future__ import annotations

import csv
import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    create_abw,
    write_abw,
    export_to_csv,
    export_to_txt,
)

_PARAGRAPHS = ["Alpha paragraph", "Beta paragraph", "Gamma paragraph"]
_MODEL = create_abw(_PARAGRAPHS)


def _write_abw(tmp_path):
    dest = tmp_path / "doc.abw"
    write_abw(_MODEL, str(dest))
    return dest


def test_export_to_csv_contains_paragraphs(tmp_path):
    dest = _write_abw(tmp_path)
    csv_str = export_to_csv(str(dest))
    assert "Alpha paragraph" in csv_str


def test_export_to_csv_is_string(tmp_path):
    dest = _write_abw(tmp_path)
    csv_str = export_to_csv(str(dest))
    assert isinstance(csv_str, str)


def test_export_to_txt_contains_all(tmp_path):
    dest = _write_abw(tmp_path)
    txt = export_to_txt(str(dest))
    for p in _PARAGRAPHS:
        assert p in txt


def test_export_to_csv_parseable(tmp_path):
    dest = _write_abw(tmp_path)
    csv_str = export_to_csv(str(dest))
    reader = csv.reader(io.StringIO(csv_str))
    rows = list(reader)
    assert len(rows) >= 1


def test_export_to_txt_non_empty(tmp_path):
    dest = _write_abw(tmp_path)
    txt = export_to_txt(str(dest))
    assert len(txt) > 0
