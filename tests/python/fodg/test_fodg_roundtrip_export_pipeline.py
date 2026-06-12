"""
test_fodg_roundtrip_export_pipeline.py -- FODG roundtrip + export pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-76
Tests roundtrip returns dict, roundtrip page_count, probe_fodg true,
export_to_json string, export_to_csv string.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg import (
    create_fodg,
    write_fodg,
    export_to_csv,
    roundtrip,
    probe_fodg,
    export_to_json,
)


def _make_file(tmp_path):
    model = create_fodg([
        {"name": "Page1"},
        {"name": "Page2"},
    ])
    dest = tmp_path / "doc.fodg"
    write_fodg(model, str(dest))
    return dest


def test_roundtrip_returns_dict(tmp_path):
    dest = _make_file(tmp_path)
    out = tmp_path / "out.fodg"
    result = roundtrip(str(dest), str(out))
    assert isinstance(result, dict)


def test_roundtrip_page_count(tmp_path):
    dest = _make_file(tmp_path)
    out = tmp_path / "out.fodg"
    result = roundtrip(str(dest), str(out))
    assert result.get("page_count") == 2


def test_probe_fodg_true(tmp_path):
    dest = _make_file(tmp_path)
    result = probe_fodg(str(dest))
    assert result is True


def test_export_to_json_string():
    model = create_fodg([{"name": "Slide1"}])
    result = export_to_json(model)
    assert isinstance(result, str)
    parsed = json.loads(result)
    assert isinstance(parsed, dict)


def test_export_to_csv_returns_string(tmp_path):
    dest = _make_file(tmp_path)
    result = export_to_csv(str(dest))
    assert isinstance(result, str)
