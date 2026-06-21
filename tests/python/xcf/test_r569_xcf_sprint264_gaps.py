"""Sprint 264: XCF analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_XCF_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"

RGBA_BLUE = _XCF_SAMPLES / "1x1-rgba-blue.xcf"
RED_RGB = _XCF_SAMPLES / "1x1-red-rgb.xcf"
GRAY_2X2 = _XCF_SAMPLES / "2x2-gray.xcf"


class TestXcfFileSizeMod31Times400PlusImageTypeTimes700PlusWidthTimes60PlusHeightTimes30:
    def _fn(self):
        from src.python.xcf import xcf_file_size_mod_31_times_400_plus_image_type_times_700_plus_width_times_60_plus_height_times_30
        return xcf_file_size_mod_31_times_400_plus_image_type_times_700_plus_width_times_60_plus_height_times_30

    def test_rgba_blue(self): assert self._fn()(RGBA_BLUE) == 9290
    def test_red_rgb(self): assert self._fn()(RED_RGB) == 8890
    def test_gray_2x2(self): assert self._fn()(GRAY_2X2) == 10080
    def test_returns_int(self): assert isinstance(self._fn()(RGBA_BLUE), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(RGBA_BLUE), fn(RED_RGB), fn(GRAY_2X2)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [RGBA_BLUE, RED_RGB, GRAY_2X2]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(RGBA_BLUE)) == 9290
    def test_string_path_accepted(self): assert self._fn()(str(RGBA_BLUE)) == 9290
    def test_gray_largest(self):
        fn = self._fn(); assert fn(GRAY_2X2) > fn(RGBA_BLUE) > fn(RED_RGB)
    def test_red_smallest(self):
        fn = self._fn(); assert fn(RED_RGB) == min(fn(RGBA_BLUE), fn(RED_RGB), fn(GRAY_2X2))


class TestXcfFileSizeTimes9PlusImageTypeTimes1000PlusWidthPlusHeightTimes80:
    def _fn(self):
        from src.python.xcf import xcf_file_size_times_9_plus_image_type_times_1000_plus_width_plus_height_times_80
        return xcf_file_size_times_9_plus_image_type_times_1000_plus_width_plus_height_times_80

    def test_rgba_blue(self): assert self._fn()(RGBA_BLUE) == 1762
    def test_red_rgb(self): assert self._fn()(RED_RGB) == 1753
    def test_gray_2x2(self): assert self._fn()(GRAY_2X2) == 2922
    def test_returns_int(self): assert isinstance(self._fn()(RGBA_BLUE), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(RGBA_BLUE), fn(RED_RGB), fn(GRAY_2X2)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [RGBA_BLUE, RED_RGB, GRAY_2X2]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(RGBA_BLUE)) == 1762
    def test_string_path_accepted(self): assert self._fn()(str(RGBA_BLUE)) == 1762
    def test_gray_largest(self):
        fn = self._fn(); assert fn(GRAY_2X2) > fn(RGBA_BLUE) > fn(RED_RGB)
    def test_red_smallest(self):
        fn = self._fn(); assert fn(RED_RGB) == min(fn(RGBA_BLUE), fn(RED_RGB), fn(GRAY_2X2))
