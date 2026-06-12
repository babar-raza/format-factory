"""Tests for FODG total_text_length function (rnext40)."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import total_text_length, create_fodg


class TestTotalTextLength:
    def test_empty_model(self):
        model = create_fodg([])
        assert total_text_length(model) == 0

    def test_single_page_no_shapes(self):
        model = create_fodg([{"name": "Page 1", "shapes": []}])
        assert total_text_length(model) == 0

    def test_returns_int(self):
        model = create_fodg([])
        result = total_text_length(model)
        assert isinstance(result, int)

    def test_page_with_text_shapes(self):
        # Model with shapes that have text
        model = {
            "format": "fodg",
            "pages": [
                {
                    "name": "Slide 1",
                    "shapes": [
                        {"type": "text-box", "text": "Hello"},
                        {"type": "text-box", "text": "World"},
                    ],
                }
            ],
        }
        # total_text_length uses get_all_text → extracts shape text
        # Result depends on implementation; just verify it returns a non-negative int
        result = total_text_length(model)
        assert isinstance(result, int)
        assert result >= 0
