"""Sprint 307 XCF product deepening — 2 new analytics functions, 20 tests.

Skill: add-python-api
Spec fact refs: FACT-XCF-EX-0001, FACT-XCF-EX-0002
"""
from __future__ import annotations

from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
_XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"

XCF_BLUE = _XCF_DIR / "1x1-rgba-blue.xcf"
XCF_RED = _XCF_DIR / "1x1-red-rgb.xcf"
XCF_GRAY = _XCF_DIR / "2x2-gray.xcf"

import sys
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_times_19_plus_image_type_times_600_plus_width_times_130_plus_height_times_110_plus_layer_count_times_1200 as f1,
    xcf_file_size_mod_19_times_200_plus_image_type_times_800_plus_width_times_height_times_300_plus_layer_count_times_1500 as f2,
)


# ---------------------------------------------------------------------------
# xcf_file_size_times_19_plus_image_type_times_600_plus_width_times_130_plus_height_times_110_plus_layer_count_times_1200
# ---------------------------------------------------------------------------

class TestXcfFileSizeTimes19PlusImageType600PlusWidth130PlusHeight110PlusLayerCount1200:
    def test_blue_returns_int(self):
        result = f1(XCF_BLUE)
        assert isinstance(result, int)

    def test_blue_expected_value(self):
        assert f1(XCF_BLUE) == 4822

    def test_red_returns_int(self):
        result = f1(XCF_RED)
        assert isinstance(result, int)

    def test_red_expected_value(self):
        assert f1(XCF_RED) == 4803

    def test_gray_returns_int(self):
        result = f1(XCF_GRAY)
        assert isinstance(result, int)

    def test_gray_expected_value(self):
        assert f1(XCF_GRAY) == 5662

    def test_gray_greater_than_blue(self):
        assert f1(XCF_GRAY) > f1(XCF_BLUE)

    def test_blue_greater_than_red(self):
        assert f1(XCF_BLUE) > f1(XCF_RED)

    def test_path_string_accepted(self):
        result = f1(str(XCF_BLUE))
        assert isinstance(result, int)

    def test_invalid_path_raises(self):
        with pytest.raises(Exception):
            f1("/nonexistent/path/missing.xcf")


# ---------------------------------------------------------------------------
# xcf_file_size_mod_19_times_200_plus_image_type_times_800_plus_width_times_height_times_300_plus_layer_count_times_1500
# ---------------------------------------------------------------------------

class TestXcfFileSizeMod19Times200PlusImageType800PlusWidthHeight300PlusLayerCount1500:
    def test_blue_returns_int(self):
        result = f2(XCF_BLUE)
        assert isinstance(result, int)

    def test_blue_expected_value(self):
        assert f2(XCF_BLUE) == 3200

    def test_red_returns_int(self):
        result = f2(XCF_RED)
        assert isinstance(result, int)

    def test_red_expected_value(self):
        assert f2(XCF_RED) == 3000

    def test_gray_returns_int(self):
        result = f2(XCF_GRAY)
        assert isinstance(result, int)

    def test_gray_expected_value(self):
        assert f2(XCF_GRAY) == 4900

    def test_gray_greater_than_blue(self):
        assert f2(XCF_GRAY) > f2(XCF_BLUE)

    def test_blue_greater_than_red(self):
        assert f2(XCF_BLUE) > f2(XCF_RED)

    def test_path_string_accepted(self):
        result = f2(str(XCF_RED))
        assert isinstance(result, int)

    def test_invalid_path_raises(self):
        with pytest.raises(Exception):
            f2("/nonexistent/path/missing.xcf")
