"""Sprint 249: XCF analytics — two new composite functions."""
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_XCF_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"

RGBA_BLUE = _XCF_SAMPLES / "1x1-rgba-blue.xcf"
RED_RGB = _XCF_SAMPLES / "1x1-red-rgb.xcf"
GRAY_2X2 = _XCF_SAMPLES / "2x2-gray.xcf"


class TestXcfFileSizeMod17Times600PlusImageTypeTimes1600PlusWhTimes1100:
    def _fn(self):
        from src.python.xcf import xcf_file_size_mod_17_times_600_plus_image_type_times_1600_plus_wh_times_1100
        return xcf_file_size_mod_17_times_600_plus_image_type_times_1600_plus_wh_times_1100

    def test_rgba_blue(self):
        assert self._fn()(RGBA_BLUE) == 5900

    def test_red_rgb(self):
        assert self._fn()(RED_RGB) == 5300

    def test_gray_2x2(self):
        assert self._fn()(GRAY_2X2) == 10800

    def test_returns_int(self):
        assert isinstance(self._fn()(RGBA_BLUE), int)

    def test_distinct_values(self):
        fn = self._fn()
        vals = {fn(RGBA_BLUE), fn(RED_RGB), fn(GRAY_2X2)}
        assert len(vals) == 3

    def test_nonnegative(self):
        fn = self._fn()
        for p in [RGBA_BLUE, RED_RGB, GRAY_2X2]:
            assert fn(p) >= 0

    def test_path_object_accepted(self):
        fn = self._fn()
        assert fn(Path(RGBA_BLUE)) == 5900

    def test_string_path_accepted(self):
        fn = self._fn()
        assert fn(str(RGBA_BLUE)) == 5900

    def test_gray_largest(self):
        fn = self._fn()
        assert fn(GRAY_2X2) > fn(RGBA_BLUE) > fn(RED_RGB)

    def test_red_smallest(self):
        fn = self._fn()
        assert fn(RED_RGB) == min(fn(RGBA_BLUE), fn(RED_RGB), fn(GRAY_2X2))


class TestXcfFileSizeMod23Times700PlusImageTypeTimes800PlusWhTimes1200:
    def _fn(self):
        from src.python.xcf import xcf_file_size_mod_23_times_700_plus_image_type_times_800_plus_wh_times_1200
        return xcf_file_size_mod_23_times_700_plus_image_type_times_800_plus_wh_times_1200

    def test_rgba_blue(self):
        assert self._fn()(RGBA_BLUE) == 13100

    def test_red_rgb(self):
        assert self._fn()(RED_RGB) == 12400

    def test_gray_2x2(self):
        assert self._fn()(GRAY_2X2) == 17500

    def test_returns_int(self):
        assert isinstance(self._fn()(RGBA_BLUE), int)

    def test_distinct_values(self):
        fn = self._fn()
        vals = {fn(RGBA_BLUE), fn(RED_RGB), fn(GRAY_2X2)}
        assert len(vals) == 3

    def test_nonnegative(self):
        fn = self._fn()
        for p in [RGBA_BLUE, RED_RGB, GRAY_2X2]:
            assert fn(p) >= 0

    def test_path_object_accepted(self):
        fn = self._fn()
        assert fn(Path(RGBA_BLUE)) == 13100

    def test_string_path_accepted(self):
        fn = self._fn()
        assert fn(str(RGBA_BLUE)) == 13100

    def test_gray_largest(self):
        fn = self._fn()
        assert fn(GRAY_2X2) > fn(RGBA_BLUE) > fn(RED_RGB)

    def test_red_smallest(self):
        fn = self._fn()
        assert fn(RED_RGB) == min(fn(RGBA_BLUE), fn(RED_RGB), fn(GRAY_2X2))
