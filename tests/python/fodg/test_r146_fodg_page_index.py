"""Tests for fodg.fodg_codec.get_page_index() — Sprint 9, R146."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from fodg.fodg_codec import create_fodg, get_page_index


def _model():
    model = create_fodg([])
    model = {
        **model,
        "pages": [
            {"name": "Intro", "shape_count": 0, "shapes": [], "text_content": []},
            {"name": "Content", "shape_count": 0, "shapes": [], "text_content": []},
            {"name": "Summary", "shape_count": 0, "shapes": [], "text_content": []},
        ],
        "page_count": 3,
        "shapes_total": 0,
    }
    return model


def test_first_page():
    assert get_page_index(_model(), "Intro") == 0


def test_second_page():
    assert get_page_index(_model(), "Content") == 1


def test_third_page():
    assert get_page_index(_model(), "Summary") == 2


def test_not_found_raises():
    try:
        get_page_index(_model(), "Missing")
        assert False, "Expected KeyError"
    except KeyError:
        pass


def test_returns_int():
    assert isinstance(get_page_index(_model(), "Intro"), int)
