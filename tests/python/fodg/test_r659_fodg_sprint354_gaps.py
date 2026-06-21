"""Sprint 354: FODG analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_FODG_SAMPLES = _REPO / "samples" / "by-format" / "fodg"

EMPTY = _FODG_SAMPLES / "empty-page.fodg"
MINIMAL = _FODG_SAMPLES / "minimal-drawing.fodg"
SHAPES = _FODG_SAMPLES / "shapes-basic.fodg"


class TestFodgFileSizeMod241Times15PlusShapeCountTimes3200PlusTextCountTimes2900:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_241_times_15_plus_shape_count_times_3200_plus_text_count_times_2900
        return fodg_file_size_mod_241_times_15_plus_shape_count_times_3200_plus_text_count_times_2900

    def test_empty_page(self): assert self._fn()(EMPTY) == 1335
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 6505
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 15230
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 1335
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 1335
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))


class TestFodgFileSizeTimes25PlusShapeCountTimes60PlusTextCountTimes45PlusPageCountTimes21:
    def _fn(self):
        from src.python.fodg import fodg_file_size_times_25_plus_shape_count_times_60_plus_text_count_times_45_plus_page_count_times_21
        return fodg_file_size_times_25_plus_shape_count_times_60_plus_text_count_times_45_plus_page_count_times_21

    def test_empty_page(self): assert self._fn()(EMPTY) == 26346
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 36951
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 40946
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 26346
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 26346
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))
