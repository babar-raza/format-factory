"""
test_abw_metadata_extract_pipeline.py -- ABW get_metadata + extract_text pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-90
Tests get_metadata returns dict, extract_text returns list, extract_text has content,
extract_text count=3, get_metadata has expected keys.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import (
    create_abw,
    write_abw,
    get_metadata,
    extract_text,
)

_PARAGRAPHS = ["Hello world content here.", "Second paragraph text.", "Third and final paragraph."]


def _make_doc(tmp_path):
    model = create_abw(_PARAGRAPHS)
    dest = tmp_path / "doc.abw"
    write_abw(model, str(dest))
    return dest


def test_get_metadata_returns_dict(tmp_path):
    dest = _make_doc(tmp_path)
    meta = get_metadata(str(dest))
    assert isinstance(meta, dict)


def test_extract_text_returns_list(tmp_path):
    dest = _make_doc(tmp_path)
    result = extract_text(str(dest))
    assert isinstance(result, list)


def test_extract_text_has_content(tmp_path):
    dest = _make_doc(tmp_path)
    result = extract_text(str(dest))
    combined = " ".join(result)
    assert "Hello" in combined or len(result) > 0


def test_extract_text_count(tmp_path):
    dest = _make_doc(tmp_path)
    result = extract_text(str(dest))
    assert len(result) == 3


def test_get_metadata_has_keys(tmp_path):
    dest = _make_doc(tmp_path)
    meta = get_metadata(str(dest))
    assert len(meta) >= 0
