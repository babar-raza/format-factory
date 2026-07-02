"""Tests for fodg.fodg_codec.swap_pages() — Sprint 10, R148."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from fodg.fodg_codec import FodgError, create_fodg, swap_pages


def _model():
    model = create_fodg([])
    return {
        **model,
        "pages": [
            {"name": "First", "shape_count": 0, "shapes": [], "text_content": []},
            {"name": "Second", "shape_count": 0, "shapes": [], "text_content": []},
            {"name": "Third", "shape_count": 0, "shapes": [], "text_content": []},
        ],
        "page_count": 3,
        "shapes_total": 0,
    }


def test_swap_first_and_second():
    model = swap_pages(_model(), 0, 1)
    assert model["pages"][0]["name"] == "Second"
    assert model["pages"][1]["name"] == "First"


def test_swap_first_and_last():
    model = swap_pages(_model(), 0, 2)
    assert model["pages"][0]["name"] == "Third"
    assert model["pages"][2]["name"] == "First"


def test_out_of_range_raises():
    try:
        swap_pages(_model(), 0, 99)
        assert 1 == 0, "Expected FodgError"

    except FodgError:
        pass


def test_does_not_mutate_original():
    model = _model()
    swap_pages(model, 0, 1)
    assert model["pages"][0]["name"] == "First"


def test_returns_dict():
    assert isinstance(swap_pages(_model(), 0, 1), dict)
