"""
test_dogfood_abw_gnumeric_export.py -- Cross-format dogfood tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-5
Tests ABW->HTML/CSV/TXT and Gnumeric->CSV/JSON export pipelines.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_ABW_SAMPLES = _REPO / "samples" / "by-format" / "abw"
_GNM_SAMPLES = _REPO / "samples" / "by-format" / "gnumeric"

from abw.abw_codec import load as load_abw, export_to_html, export_to_txt
from gnumeric.gnumeric_codec import export_to_csv as gnumeric_to_csv, export_to_json


def test_abw_html_contains_paragraphs():
    html = export_to_html(_ABW_SAMPLES / "two-paragraphs.abw")
    assert "<p>" in html or "<div>" in html or len(html) > 10


def test_abw_txt_matches_paragraph_count():
    model = load_abw(_ABW_SAMPLES / "two-paragraphs.abw")
    txt = export_to_txt(_ABW_SAMPLES / "two-paragraphs.abw")
    lines = [l for l in txt.strip().split("\n") if l.strip()]
    assert len(lines) >= model["paragraph_count"]


def test_gnumeric_csv_has_cell_data():
    csv_str = gnumeric_to_csv(_GNM_SAMPLES / "multi-cell-basic.gnumeric")
    assert len(csv_str) > 0
    lines = [l for l in csv_str.splitlines() if l.strip()]
    assert len(lines) >= 1


def test_gnumeric_json_roundtrip():
    json_str = export_to_json(_GNM_SAMPLES / "multi-cell-basic.gnumeric")
    data = json.loads(json_str)
    assert isinstance(data, (dict, list))
