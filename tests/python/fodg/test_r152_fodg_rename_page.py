"""Tests for fodg.fodg_codec.rename_page() — Sprint 12, R152."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from fodg.fodg_codec import FodgError, create_fodg, rename_page


def _model():
    model = create_fodg([])
    return {
        **model,
        "pages": [
            {"name": "Old", "shape_count": 0, "shapes": [], "text_content": []},
            {"name": "Keep", "shape_count": 0, "shapes": [], "text_content": []},
        ],
        "page_count": 2,
        "shapes_total": 0,
    }


def test_renames_first_page():
    result = rename_page(_model(), 0, "New")
    assert result["pages"][0]["name"] == "New"


def test_other_page_unchanged():
    result = rename_page(_model(), 0, "New")
    assert result["pages"][1]["name"] == "Keep"


def test_out_of_range_raises():
    try:
        rename_page(_model(), 99, "X")
        assert False, "Expected FodgError"
    except FodgError:
        pass


def test_does_not_mutate_original():
    m = _model()
    rename_page(m, 0, "New")
    assert m["pages"][0]["name"] == "Old"


def test_returns_dict():
    assert isinstance(rename_page(_model(), 0, "X"), dict)
