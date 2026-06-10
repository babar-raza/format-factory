"""Tests for fodg.fodg_codec.clear_page() — Sprint 10, R148."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from fodg.fodg_codec import FodgError, clear_page, create_fodg


def _model():
    model = create_fodg([])
    return {
        **model,
        "pages": [
            {"name": "P1", "shape_count": 3, "shapes": ["s1", "s2", "s3"], "text_content": ["text"]},
            {"name": "P2", "shape_count": 1, "shapes": ["s4"], "text_content": []},
        ],
        "page_count": 2,
        "shapes_total": 4,
    }


def test_shapes_cleared():
    model = clear_page(_model(), 0)
    assert model["pages"][0]["shapes"] == []
    assert model["pages"][0]["shape_count"] == 0


def test_text_content_cleared():
    model = clear_page(_model(), 0)
    assert model["pages"][0]["text_content"] == []


def test_other_page_unaffected():
    model = clear_page(_model(), 0)
    assert model["pages"][1]["shape_count"] == 1


def test_out_of_range_raises():
    try:
        clear_page(_model(), 99)
        assert False, "Expected FodgError"
    except FodgError:
        pass


def test_does_not_mutate_original():
    model = _model()
    clear_page(model, 0)
    assert model["pages"][0]["shape_count"] == 3


def test_returns_dict():
    assert isinstance(clear_page(_model(), 0), dict)
