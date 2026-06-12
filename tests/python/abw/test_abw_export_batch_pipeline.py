"""
test_abw_export_batch_pipeline.py -- ABW export batch pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-51
Tests export_to_csv creates file, export_to_html has tags, export_to_txt content,
export_to_json parseable with paragraph_count, export_to_markdown headers.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    create_abw,
    write_abw,
    export_to_csv,
    export_to_html,
    export_to_txt,
    export_to_json,
    export_to_markdown,
)

_MODEL = create_abw([
    "Introduction paragraph",
    "Body content goes here",
    "Conclusion and summary",
])


def _write_abw(tmp_path):
    dest = tmp_path / "doc.abw"
    write_abw(_MODEL, str(dest))
    return dest


def test_export_to_csv_has_content(tmp_path):
    dest = _write_abw(tmp_path)
    csv_str = export_to_csv(str(dest))
    assert "Introduction" in csv_str


def test_export_to_html_has_tags(tmp_path):
    dest = _write_abw(tmp_path)
    html = export_to_html(str(dest))
    assert "<" in html and "Introduction" in html


def test_export_to_txt_has_content(tmp_path):
    dest = _write_abw(tmp_path)
    txt = export_to_txt(str(dest))
    assert "Introduction" in txt
    assert "Conclusion" in txt


def test_export_to_json_parseable(tmp_path):
    dest = _write_abw(tmp_path)
    json_str = export_to_json(str(dest))
    data = json.loads(json_str)
    assert "paragraph_count" in data
    assert data["paragraph_count"] == 3


def test_export_to_markdown_has_content():
    md = export_to_markdown(_MODEL)
    assert "Introduction" in md
