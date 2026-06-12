"""
test_abw_export_html_csv_pipeline.py -- ABW export_to_html + csv pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-78
Tests export_to_html returns string, export_to_csv string, export_to_txt string,
export_to_json parseable, export_to_plain_text string.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import (
    create_abw,
    write_abw,
    export_to_html,
    export_to_csv,
    export_to_txt,
    export_to_json,
    export_to_plain_text,
)


def _make_file(tmp_path):
    model = create_abw(["Hello world", "Second paragraph", "Third item"])
    dest = tmp_path / "doc.abw"
    write_abw(model, str(dest))
    return dest, model


def test_export_to_html_returns_string(tmp_path):
    dest, _ = _make_file(tmp_path)
    result = export_to_html(str(dest))
    assert isinstance(result, str)


def test_export_to_csv_string(tmp_path):
    dest, _ = _make_file(tmp_path)
    result = export_to_csv(str(dest))
    assert isinstance(result, str)


def test_export_to_txt_string(tmp_path):
    dest, _ = _make_file(tmp_path)
    result = export_to_txt(str(dest))
    assert isinstance(result, str)
    assert "Hello world" in result


def test_export_to_json_parseable(tmp_path):
    dest, _ = _make_file(tmp_path)
    result = export_to_json(str(dest))
    parsed = json.loads(result)
    assert isinstance(parsed, dict)


def test_export_to_plain_text_string(tmp_path):
    _, model = _make_file(tmp_path)
    result = export_to_plain_text(model)
    assert isinstance(result, str)
    assert len(result) > 0
