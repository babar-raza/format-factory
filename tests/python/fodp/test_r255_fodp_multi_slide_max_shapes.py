"""Tests for fodp_has_multi_slide and fodp_max_shapes_per_slide (Sprint 45)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodp import fodp_has_multi_slide, fodp_max_shapes_per_slide

_DIR = _REPO / "samples" / "by-format" / "fodp"
_MINIMAL = str(_DIR / "minimal-presentation.fodp") # 1 slide, 1 shape: multi=F, max=1
_TITLE = str(_DIR / "title-only.fodp")             # 0 slides: multi=F, max=0
_TWO = str(_DIR / "two-slides-basic.fodp")          # 2 slides, [2,1]: multi=T, max=2


class TestFodpHasMultiSlide:
    def test_return_type(self):
        assert isinstance(fodp_has_multi_slide(_MINIMAL), bool)

    def test_false_for_single_slide(self):
        # minimal-presentation: 1 slide -> not multi
        assert fodp_has_multi_slide(_MINIMAL) is False

    def test_false_for_no_slides(self):
        # title-only: 0 slides -> not multi
        assert fodp_has_multi_slide(_TITLE) is False

    def test_true_for_two_slides(self):
        # two-slides-basic: 2 slides -> multi
        assert fodp_has_multi_slide(_TWO) is True

    def test_consistent_across_calls(self):
        assert fodp_has_multi_slide(_TWO) == fodp_has_multi_slide(_TWO)

    def test_false_is_not_none(self):
        result = fodp_has_multi_slide(_MINIMAL)
        assert result is False
        assert result is not None


class TestFodpMaxShapesPerSlide:
    def test_return_type(self):
        assert isinstance(fodp_max_shapes_per_slide(_MINIMAL), int)

    def test_exact_1_for_minimal(self):
        # minimal-presentation: 1 slide with 1 shape -> max=1
        assert fodp_max_shapes_per_slide(_MINIMAL) == 1

    def test_exact_0_for_no_slides(self):
        # title-only: 0 slides -> max=0
        assert fodp_max_shapes_per_slide(_TITLE) == 0

    def test_exact_2_for_two_slides(self):
        # two-slides-basic: shapes=[2,1] -> max=2
        assert fodp_max_shapes_per_slide(_TWO) == 2

    def test_nonnegative(self):
        assert fodp_max_shapes_per_slide(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert fodp_max_shapes_per_slide(_TWO) == fodp_max_shapes_per_slide(_TWO)

    def test_max_ge_min(self):
        from src.python.fodp import fodp_min_shapes_per_slide
        assert fodp_max_shapes_per_slide(_TWO) >= fodp_min_shapes_per_slide(_TWO)
