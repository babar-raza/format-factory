"""Tests for fodp_is_shape_heavy and fodp_has_zero_shapes (Sprint 57)."""
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from fodp.fodp_codec import fodp_is_shape_heavy, fodp_has_zero_shapes

FODP = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodp"


class TestFodpIsShapeHeavy:
    def test_minimal_not_heavy(self):
        assert fodp_is_shape_heavy(FODP / "minimal-presentation.fodp") is False

    def test_title_only_not_heavy(self):
        assert fodp_is_shape_heavy(FODP / "title-only.fodp") is False

    def test_two_slides_is_heavy(self):
        assert fodp_is_shape_heavy(FODP / "two-slides-basic.fodp") is True

    def test_returns_bool(self):
        result = fodp_is_shape_heavy(FODP / "minimal-presentation.fodp")
        assert isinstance(result, bool)

    def test_false_when_no_slides(self):
        assert fodp_is_shape_heavy(FODP / "title-only.fodp") is False


class TestFodpHasZeroShapes:
    def test_minimal_has_shapes(self):
        assert fodp_has_zero_shapes(FODP / "minimal-presentation.fodp") is False

    def test_title_only_has_zero(self):
        assert fodp_has_zero_shapes(FODP / "title-only.fodp") is True

    def test_two_slides_has_shapes(self):
        assert fodp_has_zero_shapes(FODP / "two-slides-basic.fodp") is False

    def test_returns_bool(self):
        result = fodp_has_zero_shapes(FODP / "title-only.fodp")
        assert isinstance(result, bool)

    def test_true_when_no_shapes(self):
        assert fodp_has_zero_shapes(FODP / "title-only.fodp") is True
