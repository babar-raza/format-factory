"""Sprint 246: XCF analytics — two new composite functions."""
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_XCF_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"

RGBA_BLUE = _XCF_SAMPLES / "1x1-rgba-blue.xcf"
RED_RGB = _XCF_SAMPLES / "1x1-red-rgb.xcf"
GRAY_2X2 = _XCF_SAMPLES / "2x2-gray.xcf"


class TestXcfFileSizeMod11Times400PlusImageTypeTimes1400PlusWhTimes900:
    def _fn(self):
        from src.python.xcf import xcf_file_size_mod_11_times_400_plus_image_type_times_1400_plus_wh_times_900
        return xcf_file_size_mod_11_times_400_plus_image_type_times_1400_plus_wh_times_900

    def test_rgba_blue(self):
        assert self._fn()(RGBA_BLUE) == 1700

    def test_red_rgb(self):
        assert self._fn()(RED_RGB) == 1300

    def test_gray_2x2(self):
        assert self._fn()(GRAY_2X2) == 5800

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
        assert fn(Path(RGBA_BLUE)) == 1700

    def test_string_path_accepted(self):
        fn = self._fn()
        assert fn(str(RGBA_BLUE)) == 1700

    def test_gray_larger_than_red(self):
        fn = self._fn()
        assert fn(GRAY_2X2) > fn(RED_RGB)

    def test_gray_larger_than_blue(self):
        fn = self._fn()
        assert fn(GRAY_2X2) > fn(RGBA_BLUE)


class TestXcfFileSizeMod13Times500PlusImageTypeTimes600PlusFileSizeMod7Times200:
    def _fn(self):
        from src.python.xcf import xcf_file_size_mod_13_times_500_plus_image_type_times_600_plus_file_size_mod_7_times_200
        return xcf_file_size_mod_13_times_500_plus_image_type_times_600_plus_file_size_mod_7_times_200

    def test_rgba_blue(self):
        assert self._fn()(RGBA_BLUE) == 5100

    def test_red_rgb(self):
        assert self._fn()(RED_RGB) == 4400

    def test_gray_2x2(self):
        assert self._fn()(GRAY_2X2) == 5700

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
        assert fn(Path(RGBA_BLUE)) == 5100

    def test_string_path_accepted(self):
        fn = self._fn()
        assert fn(str(RGBA_BLUE)) == 5100

    def test_gray_larger_than_red(self):
        fn = self._fn()
        assert fn(GRAY_2X2) > fn(RED_RGB)

    def test_blue_larger_than_red(self):
        fn = self._fn()
        assert fn(RGBA_BLUE) > fn(RED_RGB)
