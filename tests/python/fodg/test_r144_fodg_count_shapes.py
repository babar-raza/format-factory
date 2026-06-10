"""Tests for fodg.fodg_codec.count_shapes() — Sprint 8, R144."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from fodg.fodg_codec import count_shapes, create_fodg


def _model_with_shapes():
    model = create_fodg([])
    # Inject pages with shape_count manually
    model = {
        **model,
        "pages": [
            {"name": "P1", "shape_count": 3, "shapes": [], "text_content": []},
            {"name": "P2", "shape_count": 2, "shapes": [], "text_content": []},
        ],
        "page_count": 2,
        "shapes_total": 5,
    }
    return model


def test_total_shape_count():
    model = _model_with_shapes()
    assert count_shapes(model) == 5


def test_empty_model():
    model = create_fodg([])
    assert count_shapes(model) == 0


def test_single_page():
    model = create_fodg([])
    model = {**model, "pages": [{"name": "P1", "shape_count": 7, "shapes": [], "text_content": []}], "page_count": 1, "shapes_total": 7}
    assert count_shapes(model) == 7


def test_returns_int():
    model = _model_with_shapes()
    assert isinstance(count_shapes(model), int)


def test_zero_shapes_page():
    model = create_fodg([])
    model = {**model, "pages": [{"name": "P1", "shape_count": 0, "shapes": [], "text_content": []}], "page_count": 1, "shapes_total": 0}
    assert count_shapes(model) == 0
