"""
tests/python/fodp/test_r177_fodp_total_text_length.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT45-001
Tests for fodp_total_text_length() — total char count across all slides.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodp.fodp_codec import fodp_total_text_length

SAMPLES = _REPO / "samples" / "by-format" / "fodp"


class TestFodpTotalTextLength:
    def test_minimal_presentation(self):
        # texts=['Hello'] -> total 5 chars
        result = fodp_total_text_length(SAMPLES / "minimal-presentation.fodp")
        assert result == 5

    def test_title_only_no_text(self):
        # No extracted text -> 0 chars
        result = fodp_total_text_length(SAMPLES / "title-only.fodp")
        assert result == 0

    def test_two_slides_basic(self):
        # 'Introduction' (12) + 'First slide content.' (20) + 'Conclusion' (10) = 42
        result = fodp_total_text_length(SAMPLES / "two-slides-basic.fodp")
        assert result == 42

    def test_returns_int(self):
        result = fodp_total_text_length(SAMPLES / "minimal-presentation.fodp")
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodp_total_text_length(SAMPLES / "title-only.fodp")
        assert result >= 0

    def test_exported_from_init(self):
        from src.python.fodp import fodp_total_text_length as fn
        result = fn(SAMPLES / "minimal-presentation.fodp")
        assert result == 5
