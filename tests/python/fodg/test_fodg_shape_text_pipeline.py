"""
test_fodg_shape_text_pipeline.py -- FODG shape text extraction pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-46
Tests get_shapes returns list, get_text_shapes list, extract_text list,
get_all_text from file, probe_fodg after write.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import (
    create_fodg,
    write_fodg,
    get_shapes,
    get_text_shapes,
    extract_text,
    get_all_text,
    probe_fodg,
)

_PAGES = [
    {"name": "Page1", "shapes": [{"type": "text", "text": "First shape"}, {"type": "text", "text": "Second shape"}]},
    {"name": "Page2", "shapes": [{"type": "text", "text": "Third shape"}]},
]
_MODEL = create_fodg(_PAGES)


def _write_fodg(tmp_path):
    dest = tmp_path / "shapes.fodg"
    write_fodg(_MODEL, str(dest))
    return dest


def test_get_shapes_returns_list():
    shapes = get_shapes(_MODEL)
    assert isinstance(shapes, list)


def test_get_text_shapes_returns_list():
    text_shapes = get_text_shapes(_MODEL)
    assert isinstance(text_shapes, list)


def test_extract_text_returns_list(tmp_path):
    dest = _write_fodg(tmp_path)
    texts = extract_text(str(dest))
    assert isinstance(texts, list)


def test_get_all_text_model():
    texts = get_all_text(_MODEL)
    assert isinstance(texts, list)


def test_probe_fodg_after_write(tmp_path):
    dest = _write_fodg(tmp_path)
    assert probe_fodg(str(dest)) is True
