"""Sprint 310: XCF analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_XCF_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"

BLUE = _XCF_SAMPLES / "1x1-rgba-blue.xcf"
RED = _XCF_SAMPLES / "1x1-red-rgb.xcf"
GRAY = _XCF_SAMPLES / "2x2-gray.xcf"


class TestXcfFileSizeMod149Times350PlusImageTypeTimes2200PlusWidthTimesHeightTimes1500:
    def _fn(self):
        from src.python.xcf import xcf_file_size_mod_149_times_350_plus_image_type_times_2200_plus_width_times_height_times_1500
        return xcf_file_size_mod_149_times_350_plus_image_type_times_2200_plus_width_times_height_times_1500

    def test_blue(self): assert self._fn()(BLUE) == 11650
    def test_red(self): assert self._fn()(RED) == 11300
    def test_gray(self): assert self._fn()(GRAY) == 18350
    def test_returns_int(self): assert isinstance(self._fn()(BLUE), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(BLUE), fn(RED), fn(GRAY)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [BLUE, RED, GRAY]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(BLUE)) == 11650
    def test_string_path_accepted(self): assert self._fn()(str(BLUE)) == 11650
    def test_gray_largest(self):
        fn = self._fn(); assert fn(GRAY) > fn(BLUE) > fn(RED)
    def test_red_smallest(self):
        fn = self._fn(); assert fn(RED) == min(fn(BLUE), fn(RED), fn(GRAY))


class TestXcfFileSizeMod151Times175PlusImageTypeTimes600PlusLayerCountTimes2200:
    def _fn(self):
        from src.python.xcf import xcf_file_size_mod_151_times_175_plus_image_type_times_600_plus_layer_count_times_2200
        return xcf_file_size_mod_151_times_175_plus_image_type_times_600_plus_layer_count_times_2200

    def test_blue(self): assert self._fn()(BLUE) == 6925
    def test_red(self): assert self._fn()(RED) == 6750
    def test_gray(self): assert self._fn()(GRAY) == 7525
    def test_returns_int(self): assert isinstance(self._fn()(BLUE), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(BLUE), fn(RED), fn(GRAY)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [BLUE, RED, GRAY]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(BLUE)) == 6925
    def test_string_path_accepted(self): assert self._fn()(str(BLUE)) == 6925
    def test_gray_largest(self):
        fn = self._fn(); assert fn(GRAY) > fn(BLUE) > fn(RED)
    def test_red_smallest(self):
        fn = self._fn(); assert fn(RED) == min(fn(BLUE), fn(RED), fn(GRAY))
