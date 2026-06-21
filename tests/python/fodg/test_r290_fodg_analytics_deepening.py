"""Sprint R290: FODG analytics deepening — shape_density, has_text_content, max_shape_count."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import (
    fodg_shape_density,
    fodg_has_text_content,
    fodg_max_shape_count,
)

SAMPLES = _REPO / "samples" / "by-format" / "fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"


@pytest.fixture
def sample():
    if not MINIMAL.exists():
        pytest.skip("FODG sample not available")
    return MINIMAL


class TestFodgShapeDensity:
    def test_returns_float(self, sample):
        assert isinstance(fodg_shape_density(sample), float)

    def test_nonnegative(self, sample):
        assert fodg_shape_density(sample) >= 0.0


class TestFodgHasTextContent:
    def test_returns_bool(self, sample):
        assert isinstance(fodg_has_text_content(sample), bool)


class TestFodgMaxShapeCount:
    def test_returns_int(self, sample):
        assert isinstance(fodg_max_shape_count(sample), int)

    def test_nonnegative(self, sample):
        assert fodg_max_shape_count(sample) >= 0
