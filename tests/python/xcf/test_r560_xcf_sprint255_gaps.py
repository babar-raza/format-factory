"""Sprint 255: XCF analytics — two new composite functions."""
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_XCF_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"

RGBA_BLUE = _XCF_SAMPLES / "1x1-rgba-blue.xcf"
RED_RGB = _XCF_SAMPLES / "1x1-red-rgb.xcf"
GRAY_2X2 = _XCF_SAMPLES / "2x2-gray.xcf"


class TestXcfFileSizeMod13Times200PlusImageTypeTimes900PlusWidthTimesHeightTimes300:
    def _fn(self):
        from src.python.xcf import xcf_file_size_mod_13_times_200_plus_image_type_times_900_plus_width_times_height_times_300
        return xcf_file_size_mod_13_times_200_plus_image_type_times_900_plus_width_times_height_times_300

    def test_rgba_blue(self):
        assert self._fn()(RGBA_BLUE) == 2100

    def test_red_rgb(self):
        assert self._fn()(RED_RGB) == 1900

    def test_gray_2x2(self):
        assert self._fn()(GRAY_2X2) == 3900

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
        assert fn(Path(RGBA_BLUE)) == 2100

    def test_string_path_accepted(self):
        fn = self._fn()
        assert fn(str(RGBA_BLUE)) == 2100

    def test_gray_largest(self):
        fn = self._fn()
        assert fn(GRAY_2X2) > fn(RGBA_BLUE) > fn(RED_RGB)

    def test_red_smallest(self):
        fn = self._fn()
        assert fn(RED_RGB) == min(fn(RGBA_BLUE), fn(RED_RGB), fn(GRAY_2X2))


class TestXcfFileSizeMod9Times300PlusImageTypeTimes600PlusLayerCountTimes400:
    def _fn(self):
        from src.python.xcf import xcf_file_size_mod_9_times_300_plus_image_type_times_600_plus_layer_count_times_400
        return xcf_file_size_mod_9_times_300_plus_image_type_times_600_plus_layer_count_times_400

    def test_rgba_blue(self):
        assert self._fn()(RGBA_BLUE) == 2500

    def test_red_rgb(self):
        assert self._fn()(RED_RGB) == 2200

    def test_gray_2x2(self):
        assert self._fn()(GRAY_2X2) == 3100

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
        assert fn(Path(RGBA_BLUE)) == 2500

    def test_string_path_accepted(self):
        fn = self._fn()
        assert fn(str(RGBA_BLUE)) == 2500

    def test_gray_largest(self):
        fn = self._fn()
        assert fn(GRAY_2X2) > fn(RGBA_BLUE) > fn(RED_RGB)

    def test_red_smallest(self):
        fn = self._fn()
        assert fn(RED_RGB) == min(fn(RGBA_BLUE), fn(RED_RGB), fn(GRAY_2X2))
