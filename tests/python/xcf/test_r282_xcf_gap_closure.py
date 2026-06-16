"""Tests closing FOSS gaps: xcf_is_multi_pixel, xcf_file_bytes_per_layer."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf.xcf_parser import xcf_is_multi_pixel, xcf_file_bytes_per_layer

SAMPLE_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"


@pytest.fixture
def xcf_path():
    candidates = list(SAMPLE_DIR.glob("*.xcf"))
    if not candidates:
        pytest.skip("No XCF sample files available")
    return candidates[0]


def test_xcf_is_multi_pixel_returns_bool(xcf_path):
    result = xcf_is_multi_pixel(xcf_path)
    assert isinstance(result, bool)


def test_xcf_file_bytes_per_layer_returns_number(xcf_path):
    result = xcf_file_bytes_per_layer(xcf_path)
    assert isinstance(result, (int, float))
    assert result > 0
