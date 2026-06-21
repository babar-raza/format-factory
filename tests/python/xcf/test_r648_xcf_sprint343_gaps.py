"""Sprint 343: XCF analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_XCF_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"

BLUE = _XCF_SAMPLES / "1x1-rgba-blue.xcf"
RED = _XCF_SAMPLES / "1x1-red-rgb.xcf"
GRAY = _XCF_SAMPLES / "2x2-gray.xcf"


class TestXcfFileSizeMod71Times1200PlusImageTypeTimes1500PlusWidthTimes140PlusHeightTimes110:
    def _fn(self):
        from src.python.xcf import xcf_file_size_mod_71_times_1200_plus_image_type_times_1500_plus_width_times_140_plus_height_times_110
        return xcf_file_size_mod_71_times_1200_plus_image_type_times_1500_plus_width_times_140_plus_height_times_110

    def test_blue(self): assert self._fn()(BLUE) == 43450
    def test_red(self): assert self._fn()(RED) == 42250
    def test_gray(self): assert self._fn()(GRAY) == 45200
    def test_returns_int(self): assert isinstance(self._fn()(BLUE), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(BLUE), fn(RED), fn(GRAY)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [BLUE, RED, GRAY]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(BLUE)) == 43450
    def test_string_path_accepted(self): assert self._fn()(str(BLUE)) == 43450
    def test_gray_largest(self):
        fn = self._fn(); assert fn(GRAY) > fn(BLUE) > fn(RED)
    def test_red_smallest(self):
        fn = self._fn(); assert fn(RED) == min(fn(BLUE), fn(RED), fn(GRAY))


class TestXcfFileSizeTimes17PlusImageTypeTimes1800PlusWidthTimesHeightTimes500:
    def _fn(self):
        from src.python.xcf import xcf_file_size_times_17_plus_image_type_times_1800_plus_width_times_height_times_500
        return xcf_file_size_times_17_plus_image_type_times_1800_plus_width_times_height_times_500

    def test_blue(self): assert self._fn()(BLUE) == 3526
    def test_red(self): assert self._fn()(RED) == 3509
    def test_gray(self): assert self._fn()(GRAY) == 6826
    def test_returns_int(self): assert isinstance(self._fn()(BLUE), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(BLUE), fn(RED), fn(GRAY)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [BLUE, RED, GRAY]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(BLUE)) == 3526
    def test_string_path_accepted(self): assert self._fn()(str(BLUE)) == 3526
    def test_gray_largest(self):
        fn = self._fn(); assert fn(GRAY) > fn(BLUE) > fn(RED)
    def test_red_smallest(self):
        fn = self._fn(); assert fn(RED) == min(fn(BLUE), fn(RED), fn(GRAY))
