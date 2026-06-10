"""Tests for fodg.fodg_codec.page_names() — Sprint 11, R150."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from fodg.fodg_codec import create_fodg, page_names


def _model():
    model = create_fodg([])
    return {
        **model,
        "pages": [
            {"name": "Intro", "shape_count": 0, "shapes": [], "text_content": []},
            {"name": "Main", "shape_count": 0, "shapes": [], "text_content": []},
            {"name": "Outro", "shape_count": 0, "shapes": [], "text_content": []},
        ],
        "page_count": 3,
        "shapes_total": 0,
    }


def test_returns_three_names():
    assert page_names(_model()) == ["Intro", "Main", "Outro"]


def test_empty_pages():
    model = {**_model(), "pages": [], "page_count": 0}
    assert page_names(model) == []


def test_returns_list():
    assert isinstance(page_names(_model()), list)


def test_order_preserved():
    names = page_names(_model())
    assert names[0] == "Intro"
    assert names[2] == "Outro"


def test_does_not_mutate_model():
    m = _model()
    page_names(m)
    assert len(m["pages"]) == 3
