"""Sprint 330: FODG analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_FODG_SAMPLES = _REPO / "samples" / "by-format" / "fodg"

EMPTY = _FODG_SAMPLES / "empty-page.fodg"
MINIMAL = _FODG_SAMPLES / "minimal-drawing.fodg"
SHAPES = _FODG_SAMPLES / "shapes-basic.fodg"


class TestFodgFileSizeMod223Times1100PlusShapeCountTimes1800PlusTextCountTimes1400:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_223_times_1100_plus_shape_count_times_1800_plus_text_count_times_1400
        return fodg_file_size_mod_223_times_1100_plus_shape_count_times_1800_plus_text_count_times_1400

    def test_empty_page(self): assert self._fn()(EMPTY) == 177100
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 151700
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 81900
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 177100
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 177100
    def test_empty_largest(self):
        fn = self._fn(); assert fn(EMPTY) > fn(MINIMAL) > fn(SHAPES)
    def test_shapes_smallest(self):
        fn = self._fn(); assert fn(SHAPES) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))


class TestFodgFileSizeMod67Times22PlusShapeCountTimes2000PlusTextCountTimes1400:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_67_times_22_plus_shape_count_times_2000_plus_text_count_times_1400
        return fodg_file_size_mod_67_times_22_plus_shape_count_times_2000_plus_text_count_times_1400

    def test_empty_page(self): assert self._fn()(EMPTY) == 1056
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 4852
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 9240
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 1056
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 1056
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))
