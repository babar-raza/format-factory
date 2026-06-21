"""Sprint 333: FODG analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_FODG_SAMPLES = _REPO / "samples" / "by-format" / "fodg"

EMPTY = _FODG_SAMPLES / "empty-page.fodg"
MINIMAL = _FODG_SAMPLES / "minimal-drawing.fodg"
SHAPES = _FODG_SAMPLES / "shapes-basic.fodg"


class TestFodgFileSizeTimes19PlusShapeCountTimes45PlusTextCountTimes28PlusPageCountTimes14:
    def _fn(self):
        from src.python.fodg import fodg_file_size_times_19_plus_shape_count_times_45_plus_text_count_times_28_plus_page_count_times_14
        return fodg_file_size_times_19_plus_shape_count_times_45_plus_text_count_times_28_plus_page_count_times_14

    def test_empty_page(self): assert self._fn()(EMPTY) == 20021
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 28074
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 31137
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 20021
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 20021
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))


class TestFodgFileSizeTimes17PlusShapeCountTimes40PlusTextCountTimes25PlusPageCountTimes13:
    def _fn(self):
        from src.python.fodg import fodg_file_size_times_17_plus_shape_count_times_40_plus_text_count_times_25_plus_page_count_times_13
        return fodg_file_size_times_17_plus_shape_count_times_40_plus_text_count_times_25_plus_page_count_times_13

    def test_empty_page(self): assert self._fn()(EMPTY) == 17914
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 25119
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 27834
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 17914
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 17914
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))
