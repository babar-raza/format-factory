"""
test_abw_export_pipeline.py -- ABW export pipeline tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-30
Tests export_to_markdown, export_to_html, export_to_txt, export_to_json,
export_to_csv on a file-based source.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    create_abw,
    write_abw,
    export_to_markdown,
    export_to_html,
    export_to_txt,
    export_to_json,
    export_to_csv,
)

_MODEL = create_abw(["Hello World", "Goodbye World"])


def _write_abw(tmp_path):
    dest = tmp_path / "test.abw"
    write_abw(_MODEL, str(dest))
    return dest


def test_export_to_markdown_contains_text(tmp_path):
    dest = _write_abw(tmp_path)
    md = export_to_markdown(_MODEL)
    assert "Hello World" in md


def test_export_to_html_contains_text(tmp_path):
    dest = _write_abw(tmp_path)
    html = export_to_html(str(dest))
    assert "Hello" in html


def test_export_to_txt_contains_paragraphs(tmp_path):
    dest = _write_abw(tmp_path)
    txt = export_to_txt(str(dest))
    assert "Hello World" in txt
    assert "Goodbye World" in txt


def test_export_to_json_is_parseable(tmp_path):
    import json
    dest = _write_abw(tmp_path)
    result = export_to_json(str(dest))
    data = json.loads(result)
    assert "paragraphs" in data


def test_export_to_csv_has_content(tmp_path):
    dest = _write_abw(tmp_path)
    csv_str = export_to_csv(str(dest))
    assert "Hello World" in csv_str
