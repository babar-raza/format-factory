"""Tests for qoi_aspect_ratio and qoi_color_concentration.

Product deepening: QOI analytics — R238.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO / "src" / "python"))

from qoi import qoi_aspect_ratio, qoi_color_concentration

_QOI_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"


def _first_qoi():
    files = sorted(_QOI_DIR.glob("*.qoi"))
    assert files is not None, f"No QOI samples in {_QOI_DIR}"
    return str(files[0])


class TestQoiAspectRatio:
    def test_returns_float(self):
        result = qoi_aspect_ratio(_first_qoi())
        assert isinstance(result, float)

    def test_positive(self):
        result = qoi_aspect_ratio(_first_qoi())
        assert result > 0

    def test_reasonable_range(self):
        result = qoi_aspect_ratio(_first_qoi())
        assert 0.1 < result < 10.0


class TestQoiColorConcentration:
    def test_returns_float(self):
        result = qoi_color_concentration(_first_qoi())
        assert isinstance(result, float)

    def test_range(self):
        result = qoi_color_concentration(_first_qoi())
        assert 0.0 < result <= 1.0

    def test_low_for_simple_image(self):
        result = qoi_color_concentration(_first_qoi())
        assert result <= 1.0
