"""
Tests for FODG gap closure (1 FOSS function).
Closes: GAP-FODG-FOSS-FODG_HAS_NO_-001

Known sample values:
  empty-page.fodg: has_no_shapes=True
  minimal-drawing.fodg: has_no_shapes=False
  shapes-basic.fodg: has_no_shapes=False
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg import fodg_has_no_shapes

_FODG = _REPO / "samples" / "by-format" / "fodg"
_EMPTY = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES = _FODG / "shapes-basic.fodg"


class TestFodgHasNoShapes:
    def test_returns_bool(self):
        assert isinstance(fodg_has_no_shapes(_EMPTY), bool)

    def test_empty_page_has_no_shapes(self):
        assert fodg_has_no_shapes(_EMPTY) is True

    def test_minimal_drawing_has_shapes(self):
        assert fodg_has_no_shapes(_MINIMAL) is False

    def test_shapes_basic_has_shapes(self):
        assert fodg_has_no_shapes(_SHAPES) is False

    def test_all_return_bool(self):
        for p in [_EMPTY, _MINIMAL, _SHAPES]:
            result = fodg_has_no_shapes(p)
            assert result is True or result is False

    def test_no_shapes_is_inverse_of_has_shapes(self):
        # empty page: no shapes → True
        # shapes-basic: has shapes → False
        assert fodg_has_no_shapes(_EMPTY) != fodg_has_no_shapes(_SHAPES)
