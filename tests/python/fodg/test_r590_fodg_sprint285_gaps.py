"""Sprint 285: FODG analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_FODG_SAMPLES = _REPO / "samples" / "by-format" / "fodg"

EMPTY = _FODG_SAMPLES / "empty-page.fodg"
MINIMAL = _FODG_SAMPLES / "minimal-drawing.fodg"
SHAPES = _FODG_SAMPLES / "shapes-basic.fodg"


class TestFodgFileSizeMod37Times200PlusShapeCountTimes700PlusTextCountTimes300:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_37_times_200_plus_shape_count_times_700_plus_text_count_times_300
        return fodg_file_size_mod_37_times_200_plus_shape_count_times_700_plus_text_count_times_300

    def test_empty_page(self): assert self._fn()(EMPTY) == 3400
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 7000
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 2700
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 3400
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 3400
    def test_minimal_largest(self):
        fn = self._fn(); assert fn(MINIMAL) > fn(EMPTY) > fn(SHAPES)
    def test_shapes_smallest(self):
        fn = self._fn(); assert fn(SHAPES) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))


class TestFodgFileSizeMod53Times100PlusShapeCountTimes1000PlusTextCountTimes600:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_53_times_100_plus_shape_count_times_1000_plus_text_count_times_600
        return fodg_file_size_mod_53_times_100_plus_shape_count_times_1000_plus_text_count_times_600

    def test_empty_page(self): assert self._fn()(EMPTY) == 4600
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 5800
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 8000
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 4600
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 4600
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))
