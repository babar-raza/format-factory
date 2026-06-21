"""Sprint 279: FODG analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_FODG_SAMPLES = _REPO / "samples" / "by-format" / "fodg"

EMPTY = _FODG_SAMPLES / "empty-page.fodg"
MINIMAL = _FODG_SAMPLES / "minimal-drawing.fodg"
SHAPES = _FODG_SAMPLES / "shapes-basic.fodg"


class TestFodgFileSizeMod41Times9PlusShapeTimes1800PlusTextTimes1400PlusPageTimes900:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_41_times_9_plus_shape_times_1800_plus_text_times_1400_plus_page_times_900
        return fodg_file_size_mod_41_times_9_plus_shape_times_1800_plus_text_times_1400_plus_page_times_900

    def test_empty_page(self): assert self._fn()(EMPTY) == 1152
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 4442
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 9361
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 1152
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 1152
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))


class TestFodgFileSizeTimes10PlusShapeTimes300PlusTextTimes150PlusPageTimes75:
    def _fn(self):
        from src.python.fodg import fodg_file_size_times_10_plus_shape_times_300_plus_text_times_150_plus_page_times_75
        return fodg_file_size_times_10_plus_shape_times_300_plus_text_times_150_plus_page_times_75

    def test_empty_page(self): assert self._fn()(EMPTY) == 10605
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 15255
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 17555
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 10605
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 10605
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))
