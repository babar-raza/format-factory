"""
test_abw_roundtrip_pipeline.py -- ABW roundtrip pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-69
Tests write_abw creates file, probe_abw true, roundtrip paragraph count,
roundtrip text preserved, write then get_paragraph_count.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    create_abw,
    write_abw,
    probe_abw,
    load,
    get_paragraph_count,
    extract_text,
)

_PARAGRAPHS = ["First paragraph", "Second paragraph", "Third paragraph"]
_MODEL = create_abw(_PARAGRAPHS)


def test_write_abw_creates_file(tmp_path):
    dest = tmp_path / "doc.abw"
    write_abw(_MODEL, str(dest))
    assert dest.exists()


def test_probe_abw_true(tmp_path):
    dest = tmp_path / "doc.abw"
    write_abw(_MODEL, str(dest))
    assert probe_abw(str(dest)) is True


def test_roundtrip_paragraph_count(tmp_path):
    dest = tmp_path / "doc.abw"
    write_abw(_MODEL, str(dest))
    count = get_paragraph_count(str(dest))
    assert count == 3


def test_roundtrip_text_preserved(tmp_path):
    dest = tmp_path / "doc.abw"
    write_abw(_MODEL, str(dest))
    texts = extract_text(str(dest))
    assert "First paragraph" in texts


def test_write_then_load(tmp_path):
    dest = tmp_path / "doc.abw"
    write_abw(_MODEL, str(dest))
    loaded = load(str(dest))
    assert isinstance(loaded, dict)
    assert loaded["paragraph_count"] == 3
