"""Sprint 270: XCF analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_XCF_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"

RGBA_BLUE = _XCF_SAMPLES / "1x1-rgba-blue.xcf"
RED_RGB = _XCF_SAMPLES / "1x1-red-rgb.xcf"
GRAY_2X2 = _XCF_SAMPLES / "2x2-gray.xcf"


class TestXcfFileSizeMod29Times200PlusImageTypeTimes1500PlusWidthTimesHeightTimes500:
    def _fn(self):
        from src.python.xcf import xcf_file_size_mod_29_times_200_plus_image_type_times_1500_plus_width_times_height_times_500
        return xcf_file_size_mod_29_times_200_plus_image_type_times_1500_plus_width_times_height_times_500

    def test_rgba_blue(self): assert self._fn()(RGBA_BLUE) == 1300
    def test_red_rgb(self): assert self._fn()(RED_RGB) == 1100
    def test_gray_2x2(self): assert self._fn()(GRAY_2X2) == 4300
    def test_returns_int(self): assert isinstance(self._fn()(RGBA_BLUE), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(RGBA_BLUE), fn(RED_RGB), fn(GRAY_2X2)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [RGBA_BLUE, RED_RGB, GRAY_2X2]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(RGBA_BLUE)) == 1300
    def test_string_path_accepted(self): assert self._fn()(str(RGBA_BLUE)) == 1300
    def test_gray_largest(self):
        fn = self._fn(); assert fn(GRAY_2X2) > fn(RGBA_BLUE) > fn(RED_RGB)
    def test_red_smallest(self):
        fn = self._fn(); assert fn(RED_RGB) == min(fn(RGBA_BLUE), fn(RED_RGB), fn(GRAY_2X2))


class TestXcfFileSizeMod23Times150PlusImageTypeTimes1000PlusLayerCountTimes600:
    def _fn(self):
        from src.python.xcf import xcf_file_size_mod_23_times_150_plus_image_type_times_1000_plus_layer_count_times_600
        return xcf_file_size_mod_23_times_150_plus_image_type_times_1000_plus_layer_count_times_600

    def test_rgba_blue(self): assert self._fn()(RGBA_BLUE) == 3150
    def test_red_rgb(self): assert self._fn()(RED_RGB) == 3000
    def test_gray_2x2(self): assert self._fn()(GRAY_2X2) == 4150
    def test_returns_int(self): assert isinstance(self._fn()(RGBA_BLUE), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(RGBA_BLUE), fn(RED_RGB), fn(GRAY_2X2)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [RGBA_BLUE, RED_RGB, GRAY_2X2]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(RGBA_BLUE)) == 3150
    def test_string_path_accepted(self): assert self._fn()(str(RGBA_BLUE)) == 3150
    def test_gray_largest(self):
        fn = self._fn(); assert fn(GRAY_2X2) > fn(RGBA_BLUE) > fn(RED_RGB)
    def test_red_smallest(self):
        fn = self._fn(); assert fn(RED_RGB) == min(fn(RGBA_BLUE), fn(RED_RGB), fn(GRAY_2X2))
