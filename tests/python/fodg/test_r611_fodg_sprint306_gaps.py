"""Sprint 306: FODG analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_FODG_SAMPLES = _REPO / "samples" / "by-format" / "fodg"

EMPTY = _FODG_SAMPLES / "empty-page.fodg"
MINIMAL = _FODG_SAMPLES / "minimal-drawing.fodg"
SHAPES = _FODG_SAMPLES / "shapes-basic.fodg"


class TestFodgFileSizeMod127Times400PlusShapeCountTimes1400PlusTextCountTimes900:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_127_times_400_plus_shape_count_times_1400_plus_text_count_times_900
        return fodg_file_size_mod_127_times_400_plus_shape_count_times_1400_plus_text_count_times_900

    def test_empty_page(self): assert self._fn()(EMPTY) == 14800
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 32700
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 47600
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 14800
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 14800
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))


class TestFodgFileSizeMod131Times500PlusShapeCountTimes1100PlusTextCountTimes700:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_131_times_500_plus_shape_count_times_1100_plus_text_count_times_700
        return fodg_file_size_mod_131_times_500_plus_shape_count_times_1100_plus_text_count_times_700

    def test_empty_page(self): assert self._fn()(EMPTY) == 2500
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 17800
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 32700
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 2500
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 2500
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))
