"""Tests for xcf_compression_ratio and xcf_layers_per_dimension.

Product deepening: XCF analytics — R238.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf import xcf_compression_ratio, xcf_layers_per_dimension

_XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"


def _first_xcf():
    files = sorted(_XCF_DIR.glob("*.xcf"))
    assert files is not None, f"No XCF samples in {_XCF_DIR}"
    return str(files[0])


class TestXcfCompressionRatio:
    def test_returns_float(self):
        result = xcf_compression_ratio(_first_xcf())
        assert isinstance(result, float)

    def test_positive(self):
        result = xcf_compression_ratio(_first_xcf())
        assert result > 0

    def test_reasonable(self):
        result = xcf_compression_ratio(_first_xcf())
        assert 0.01 < result < 1000


class TestXcfLayersPerDimension:
    def test_returns_float(self):
        result = xcf_layers_per_dimension(_first_xcf())
        assert isinstance(result, float)

    def test_nonnegative(self):
        result = xcf_layers_per_dimension(_first_xcf())
        assert result >= 0

    def test_small_ratio(self):
        result = xcf_layers_per_dimension(_first_xcf())
        assert result < 100
