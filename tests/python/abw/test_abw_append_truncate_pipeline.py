"""
test_abw_append_truncate_pipeline.py -- ABW append_paragraph + truncate_paragraphs pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-93
Tests append_paragraph increases count, append returns model, truncate_paragraphs returns model,
truncate reduces count, append then truncate restores count.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import (
    create_abw,
    append_paragraph,
    truncate_paragraphs,
)

_PARAGRAPHS = ["First paragraph.", "Second paragraph.", "Third paragraph.", "Fourth paragraph."]


def test_append_paragraph_increases_count(tmp_path):
    model = create_abw(_PARAGRAPHS)
    before = len(model["paragraphs"])
    model = append_paragraph(model, "New paragraph added.")
    assert len(model["paragraphs"]) == before + 1


def test_append_paragraph_returns_model(tmp_path):
    model = create_abw(_PARAGRAPHS)
    result = append_paragraph(model, "Extra.")
    assert isinstance(result, dict)
    assert "paragraphs" in result


def test_truncate_paragraphs_returns_model(tmp_path):
    model = create_abw(_PARAGRAPHS)
    result = truncate_paragraphs(model, 2)
    assert isinstance(result, dict)


def test_truncate_reduces_count(tmp_path):
    model = create_abw(_PARAGRAPHS)
    result = truncate_paragraphs(model, 2)
    assert len(result["paragraphs"]) == 2


def test_append_then_truncate_restores_count(tmp_path):
    model = create_abw(_PARAGRAPHS)
    original = len(model["paragraphs"])
    model = append_paragraph(model, "Extra paragraph.")
    model = truncate_paragraphs(model, original)
    assert len(model["paragraphs"]) == original
