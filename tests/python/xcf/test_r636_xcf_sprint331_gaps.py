"""Sprint 331: XCF analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_XCF_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"

BLUE = _XCF_SAMPLES / "1x1-rgba-blue.xcf"
RED = _XCF_SAMPLES / "1x1-red-rgb.xcf"
GRAY = _XCF_SAMPLES / "2x2-gray.xcf"


class TestXcfFileSizeMod61Times1000PlusImageTypeTimes1300PlusWidthTimes120PlusHeightTimes90:
    def _fn(self):
        from src.python.xcf import xcf_file_size_mod_61_times_1000_plus_image_type_times_1300_plus_width_times_120_plus_height_times_90
        return xcf_file_size_mod_61_times_1000_plus_image_type_times_1300_plus_width_times_120_plus_height_times_90

    def test_blue(self): assert self._fn()(BLUE) == 56210
    def test_red(self): assert self._fn()(RED) == 55210
    def test_gray(self): assert self._fn()(GRAY) == 57720
    def test_returns_int(self): assert isinstance(self._fn()(BLUE), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(BLUE), fn(RED), fn(GRAY)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [BLUE, RED, GRAY]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(BLUE)) == 56210
    def test_string_path_accepted(self): assert self._fn()(str(BLUE)) == 56210
    def test_gray_largest(self):
        fn = self._fn(); assert fn(GRAY) > fn(BLUE) > fn(RED)
    def test_red_smallest(self):
        fn = self._fn(); assert fn(RED) == min(fn(BLUE), fn(RED), fn(GRAY))


class TestXcfFileSizeMod67Times1100PlusImageTypeTimes1400PlusWidthTimes130PlusHeightTimes100:
    def _fn(self):
        from src.python.xcf import xcf_file_size_mod_67_times_1100_plus_image_type_times_1400_plus_width_times_130_plus_height_times_100
        return xcf_file_size_mod_67_times_1100_plus_image_type_times_1400_plus_width_times_130_plus_height_times_100

    def test_blue(self): assert self._fn()(BLUE) == 48630
    def test_red(self): assert self._fn()(RED) == 47530
    def test_gray(self): assert self._fn()(GRAY) == 50260
    def test_returns_int(self): assert isinstance(self._fn()(BLUE), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(BLUE), fn(RED), fn(GRAY)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [BLUE, RED, GRAY]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(BLUE)) == 48630
    def test_string_path_accepted(self): assert self._fn()(str(BLUE)) == 48630
    def test_gray_largest(self):
        fn = self._fn(); assert fn(GRAY) > fn(BLUE) > fn(RED)
    def test_red_smallest(self):
        fn = self._fn(); assert fn(RED) == min(fn(BLUE), fn(RED), fn(GRAY))
