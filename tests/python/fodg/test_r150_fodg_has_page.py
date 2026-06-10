"""Tests for fodg.fodg_codec.has_page() — Sprint 11, R150."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from fodg.fodg_codec import create_fodg, has_page


def _model():
    model = create_fodg([])
    return {
        **model,
        "pages": [
            {"name": "Intro", "shape_count": 0, "shapes": [], "text_content": []},
            {"name": "Main", "shape_count": 0, "shapes": [], "text_content": []},
        ],
        "page_count": 2,
        "shapes_total": 0,
    }


def test_existing_page_returns_true():
    assert has_page(_model(), "Intro") is True


def test_another_existing_page():
    assert has_page(_model(), "Main") is True


def test_missing_page_returns_false():
    assert has_page(_model(), "NotHere") is False


def test_case_sensitive():
    assert has_page(_model(), "intro") is False


def test_empty_pages_returns_false():
    model = {**_model(), "pages": [], "page_count": 0}
    assert has_page(model, "Intro") is False
