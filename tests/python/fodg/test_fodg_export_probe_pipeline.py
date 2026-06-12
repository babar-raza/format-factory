"""
test_fodg_export_probe_pipeline.py -- FODG export + probe pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-58
Tests export_to_json parseable, export_to_json page_count, probe_fodg file,
export_to_txt string, export_to_csv string.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import (
    create_fodg,
    write_fodg,
    export_to_json,
    probe_fodg,
    export_to_txt,
    export_to_csv,
)

_PAGES = [{"name": "Slide1"}, {"name": "Slide2"}]


def _write(tmp_path):
    model = create_fodg(_PAGES)
    dest = tmp_path / "doc.fodg"
    write_fodg(model, str(dest))
    return model, dest


def test_export_to_json_parseable(tmp_path):
    model, _ = _write(tmp_path)
    json_str = export_to_json(model)
    data = json.loads(json_str)
    assert isinstance(data, dict)


def test_export_to_json_page_count(tmp_path):
    model, _ = _write(tmp_path)
    data = json.loads(export_to_json(model))
    assert data["page_count"] == 2


def test_probe_fodg_file(tmp_path):
    _, dest = _write(tmp_path)
    result = probe_fodg(str(dest))
    assert result is True


def test_export_to_txt_string(tmp_path):
    _, dest = _write(tmp_path)
    txt = export_to_txt(str(dest))
    assert isinstance(txt, str)


def test_export_to_csv_string(tmp_path):
    _, dest = _write(tmp_path)
    csv_str = export_to_csv(str(dest))
    assert isinstance(csv_str, str)
