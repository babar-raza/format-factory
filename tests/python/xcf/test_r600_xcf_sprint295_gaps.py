"""Sprint 295: XCF analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_XCF_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"

BLUE = _XCF_SAMPLES / "1x1-rgba-blue.xcf"
RED = _XCF_SAMPLES / "1x1-red-rgb.xcf"
GRAY = _XCF_SAMPLES / "2x2-gray.xcf"


class TestXcfFileSizeMod41Times300PlusImageTypeTimes1500PlusWidthTimesHeightTimes800:
    def _fn(self):
        from src.python.xcf import xcf_file_size_mod_41_times_300_plus_image_type_times_1500_plus_width_times_height_times_800
        return xcf_file_size_mod_41_times_300_plus_image_type_times_1500_plus_width_times_height_times_800

    def test_blue(self): assert self._fn()(BLUE) == 5000
    def test_red(self): assert self._fn()(RED) == 4700
    def test_gray(self): assert self._fn()(GRAY) == 8900
    def test_returns_int(self): assert isinstance(self._fn()(BLUE), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(BLUE), fn(RED), fn(GRAY)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [BLUE, RED, GRAY]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(BLUE)) == 5000
    def test_string_path_accepted(self): assert self._fn()(str(BLUE)) == 5000
    def test_gray_largest(self):
        fn = self._fn(); assert fn(GRAY) > fn(BLUE) > fn(RED)
    def test_red_smallest(self):
        fn = self._fn(); assert fn(RED) == min(fn(BLUE), fn(RED), fn(GRAY))


class TestXcfFileSizeMod31Times150PlusImageTypeTimes700PlusLayerCountTimes1200:
    def _fn(self):
        from src.python.xcf import xcf_file_size_mod_31_times_150_plus_image_type_times_700_plus_layer_count_times_1200
        return xcf_file_size_mod_31_times_150_plus_image_type_times_700_plus_layer_count_times_1200

    def test_blue(self): assert self._fn()(BLUE) == 4650
    def test_red(self): assert self._fn()(RED) == 4500
    def test_gray(self): assert self._fn()(GRAY) == 5350
    def test_returns_int(self): assert isinstance(self._fn()(BLUE), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(BLUE), fn(RED), fn(GRAY)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [BLUE, RED, GRAY]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(BLUE)) == 4650
    def test_string_path_accepted(self): assert self._fn()(str(BLUE)) == 4650
    def test_gray_largest(self):
        fn = self._fn(); assert fn(GRAY) > fn(BLUE) > fn(RED)
    def test_red_smallest(self):
        fn = self._fn(); assert fn(RED) == min(fn(BLUE), fn(RED), fn(GRAY))
