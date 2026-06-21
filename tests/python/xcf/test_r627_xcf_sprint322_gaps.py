"""Sprint 322: XCF analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_XCF_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"

BLUE = _XCF_SAMPLES / "1x1-rgba-blue.xcf"
RED = _XCF_SAMPLES / "1x1-red-rgb.xcf"
GRAY = _XCF_SAMPLES / "2x2-gray.xcf"


class TestXcfFileSizeMod197Times300PlusImageTypeTimes2600PlusWidthTimesHeightTimes1900:
    def _fn(self):
        from src.python.xcf import xcf_file_size_mod_197_times_300_plus_image_type_times_2600_plus_width_times_height_times_1900
        return xcf_file_size_mod_197_times_300_plus_image_type_times_2600_plus_width_times_height_times_1900

    def test_blue(self): assert self._fn()(BLUE) == 55300
    def test_red(self): assert self._fn()(RED) == 55000
    def test_gray(self): assert self._fn()(GRAY) == 63600
    def test_returns_int(self): assert isinstance(self._fn()(BLUE), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(BLUE), fn(RED), fn(GRAY)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [BLUE, RED, GRAY]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(BLUE)) == 55300
    def test_string_path_accepted(self): assert self._fn()(str(BLUE)) == 55300
    def test_gray_largest(self):
        fn = self._fn(); assert fn(GRAY) > fn(BLUE) > fn(RED)
    def test_red_smallest(self):
        fn = self._fn(); assert fn(RED) == min(fn(BLUE), fn(RED), fn(GRAY))


class TestXcfFileSizeMod199Times250PlusImageTypeTimes800PlusLayerCountTimes2600:
    def _fn(self):
        from src.python.xcf import xcf_file_size_mod_199_times_250_plus_image_type_times_800_plus_layer_count_times_2600
        return xcf_file_size_mod_199_times_250_plus_image_type_times_800_plus_layer_count_times_2600

    def test_blue(self): assert self._fn()(BLUE) == 47100
    def test_red(self): assert self._fn()(RED) == 46850
    def test_gray(self): assert self._fn()(GRAY) == 47900
    def test_returns_int(self): assert isinstance(self._fn()(BLUE), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(BLUE), fn(RED), fn(GRAY)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [BLUE, RED, GRAY]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(BLUE)) == 47100
    def test_string_path_accepted(self): assert self._fn()(str(BLUE)) == 47100
    def test_gray_largest(self):
        fn = self._fn(); assert fn(GRAY) > fn(BLUE) > fn(RED)
    def test_red_smallest(self):
        fn = self._fn(); assert fn(RED) == min(fn(BLUE), fn(RED), fn(GRAY))
