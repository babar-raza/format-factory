"""
Tests for FODG analytics gap closure (1 FOSS gap).
Closes: GAP-FODG-FOSS-FODG_MIN_TE-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import fodg_min_text_per_page

_FODG_MINIMAL = _REPO / "samples/by-format/fodg/minimal-drawing.fodg"
_FODG_SHAPES = _REPO / "samples/by-format/fodg/shapes-basic.fodg"
_FODG_EMPTY = _REPO / "samples/by-format/fodg/empty-page.fodg"


class TestFodgMinTextPerPage:
    def test_returns_int(self):
        assert isinstance(fodg_min_text_per_page(_FODG_MINIMAL), int)

    def test_nonnegative(self):
        assert fodg_min_text_per_page(_FODG_MINIMAL) >= 0

    def test_empty_page_returns_zero(self):
        # empty-page.fodg has no shapes/text on its page
        assert fodg_min_text_per_page(_FODG_EMPTY) == 0

    def test_shapes_doc_nonnegative(self):
        assert fodg_min_text_per_page(_FODG_SHAPES) >= 0
