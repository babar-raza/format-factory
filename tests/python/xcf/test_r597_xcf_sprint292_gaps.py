"""Sprint 292: XCF analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_XCF_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"

BLUE = _XCF_SAMPLES / "1x1-rgba-blue.xcf"
RED = _XCF_SAMPLES / "1x1-red-rgb.xcf"
GRAY = _XCF_SAMPLES / "2x2-gray.xcf"


class TestXcfFileSizeMod37Times200PlusImageTypeTimes900PlusLayerCountTimes1000:
    def _fn(self):
        from src.python.xcf import xcf_file_size_mod_37_times_200_plus_image_type_times_900_plus_layer_count_times_1000
        return xcf_file_size_mod_37_times_200_plus_image_type_times_900_plus_layer_count_times_1000

    def test_blue(self): assert self._fn()(BLUE) == 7000
    def test_red(self): assert self._fn()(RED) == 6800
    def test_gray(self): assert self._fn()(GRAY) == 7900
    def test_returns_int(self): assert isinstance(self._fn()(BLUE), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(BLUE), fn(RED), fn(GRAY)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [BLUE, RED, GRAY]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(BLUE)) == 7000
    def test_string_path_accepted(self): assert self._fn()(str(BLUE)) == 7000
    def test_gray_largest(self):
        fn = self._fn(); assert fn(GRAY) > fn(BLUE) > fn(RED)
    def test_red_smallest(self):
        fn = self._fn(); assert fn(RED) == min(fn(BLUE), fn(RED), fn(GRAY))


class TestXcfFileSizeMod47Times700PlusImageTypeTimes1000PlusWidthTimes90PlusHeightTimes60:
    def _fn(self):
        from src.python.xcf import xcf_file_size_mod_47_times_700_plus_image_type_times_1000_plus_width_times_90_plus_height_times_60
        return xcf_file_size_mod_47_times_700_plus_image_type_times_1000_plus_width_times_90_plus_height_times_60

    def test_blue(self): assert self._fn()(BLUE) == 26050
    def test_red(self): assert self._fn()(RED) == 25350
    def test_gray(self): assert self._fn()(GRAY) == 27200
    def test_returns_int(self): assert isinstance(self._fn()(BLUE), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(BLUE), fn(RED), fn(GRAY)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [BLUE, RED, GRAY]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(BLUE)) == 26050
    def test_string_path_accepted(self): assert self._fn()(str(BLUE)) == 26050
    def test_gray_largest(self):
        fn = self._fn(); assert fn(GRAY) > fn(BLUE) > fn(RED)
    def test_red_smallest(self):
        fn = self._fn(); assert fn(RED) == min(fn(BLUE), fn(RED), fn(GRAY))
