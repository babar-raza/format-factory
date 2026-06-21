"""Sprint 269: FODG analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_FODG_SAMPLES = _REPO / "samples" / "by-format" / "fodg"

EMPTY = _FODG_SAMPLES / "empty-page.fodg"
MINIMAL = _FODG_SAMPLES / "minimal-drawing.fodg"
SHAPES = _FODG_SAMPLES / "shapes-basic.fodg"


class TestFodgFileSizeMod37Times7PlusShapeTimes1700PlusTextTimes1300PlusPageTimes800:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_37_times_7_plus_shape_times_1700_plus_text_times_1300_plus_page_times_800
        return fodg_file_size_mod_37_times_7_plus_shape_times_1700_plus_text_times_1300_plus_page_times_800

    def test_empty_page(self): assert self._fn()(EMPTY) == 919
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 4010
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 8500
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 919
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 919
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))


class TestFodgFileSizeTimes9PlusShapeTimes400PlusTextTimes200PlusPageTimes100:
    def _fn(self):
        from src.python.fodg import fodg_file_size_times_9_plus_shape_times_400_plus_text_times_200_plus_page_times_100
        return fodg_file_size_times_9_plus_shape_times_400_plus_text_times_200_plus_page_times_100

    def test_empty_page(self): assert self._fn()(EMPTY) == 9577
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 13957
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 16352
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 9577
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 9577
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))
