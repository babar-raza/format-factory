"""Sprint 327: FODG analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_FODG_SAMPLES = _REPO / "samples" / "by-format" / "fodg"

EMPTY = _FODG_SAMPLES / "empty-page.fodg"
MINIMAL = _FODG_SAMPLES / "minimal-drawing.fodg"
SHAPES = _FODG_SAMPLES / "shapes-basic.fodg"


class TestFodgFileSizeMod197Times7PlusShapeCountTimes2800PlusTextCountTimes2500:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_197_times_7_plus_shape_count_times_2800_plus_text_count_times_2500
        return fodg_file_size_mod_197_times_7_plus_shape_count_times_2800_plus_text_count_times_2500

    def test_empty_page(self): assert self._fn()(EMPTY) == 476
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 5958
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 11264
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 476
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 476
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))


class TestFodgFileSizeMod211Times1050PlusShapeCountTimes2100PlusTextCountTimes1600:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_211_times_1050_plus_shape_count_times_2100_plus_text_count_times_1600
        return fodg_file_size_mod_211_times_1050_plus_shape_count_times_2100_plus_text_count_times_1600

    def test_empty_page(self): assert self._fn()(EMPTY) == 219450
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 221050
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 168050
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 219450
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 219450
    def test_minimal_largest(self):
        fn = self._fn(); assert fn(MINIMAL) > fn(EMPTY) > fn(SHAPES)
    def test_shapes_smallest(self):
        fn = self._fn(); assert fn(SHAPES) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))
