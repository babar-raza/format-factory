"""Tests for fodg.fodg_codec.duplicate_page() — Sprint 9, R146."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from fodg.fodg_codec import FodgError, create_fodg, duplicate_page


def _model():
    model = create_fodg([])
    return {
        **model,
        "pages": [
            {"name": "PageA", "shape_count": 2, "shapes": [], "text_content": ["text"]},
            {"name": "PageB", "shape_count": 0, "shapes": [], "text_content": []},
        ],
        "page_count": 2,
        "shapes_total": 2,
    }


def test_page_count_increases():
    model = duplicate_page(_model(), 0)
    assert model["page_count"] == 3


def test_copy_appended_at_end():
    model = duplicate_page(_model(), 0)
    assert model["pages"][-1]["name"] == "PageA"


def test_copy_has_same_content():
    model = duplicate_page(_model(), 0)
    orig = _model()["pages"][0]
    copy = model["pages"][-1]
    assert copy["text_content"] == orig["text_content"]


def test_out_of_range_raises():
    try:
        duplicate_page(_model(), 99)
        assert False, "Expected FodgError"
    except FodgError:
        pass


def test_does_not_mutate_original():
    model = _model()
    duplicate_page(model, 0)
    assert model["page_count"] == 2


def test_returns_dict():
    result = duplicate_page(_model(), 0)
    assert isinstance(result, dict)
