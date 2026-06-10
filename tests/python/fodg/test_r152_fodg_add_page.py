"""Tests for fodg.fodg_codec.add_page() — Sprint 12, R152."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from fodg.fodg_codec import add_page, create_fodg


def _model():
    model = create_fodg([])
    return {
        **model,
        "pages": [
            {"name": "Existing", "shape_count": 0, "shapes": [], "text_content": []},
        ],
        "page_count": 1,
        "shapes_total": 0,
    }


def test_adds_page():
    result = add_page(_model(), "New")
    assert len(result["pages"]) == 2


def test_new_page_name():
    result = add_page(_model(), "New")
    assert result["pages"][-1]["name"] == "New"


def test_page_count_updated():
    result = add_page(_model(), "New")
    assert result["page_count"] == 2


def test_new_page_is_blank():
    result = add_page(_model(), "New")
    new_page = result["pages"][-1]
    assert new_page["shape_count"] == 0
    assert new_page["shapes"] == []


def test_does_not_mutate_original():
    m = _model()
    add_page(m, "New")
    assert len(m["pages"]) == 1


def test_returns_dict():
    assert isinstance(add_page(_model(), "X"), dict)
