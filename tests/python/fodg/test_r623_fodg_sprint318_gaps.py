"""Sprint 318: FODG analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_FODG_SAMPLES = _REPO / "samples" / "by-format" / "fodg"

EMPTY = _FODG_SAMPLES / "empty-page.fodg"
MINIMAL = _FODG_SAMPLES / "minimal-drawing.fodg"
SHAPES = _FODG_SAMPLES / "shapes-basic.fodg"


class TestFodgFileSizeMod167Times750PlusShapeCountTimes1800PlusTextCountTimes1300:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_167_times_750_plus_shape_count_times_1800_plus_text_count_times_1300
        return fodg_file_size_mod_167_times_750_plus_shape_count_times_1800_plus_text_count_times_1300

    def test_empty_page(self): assert self._fn()(EMPTY) == 38250
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 105850
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 101750
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 38250
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 38250
    def test_minimal_largest(self):
        fn = self._fn(); assert fn(MINIMAL) > fn(SHAPES) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))


class TestFodgFileSizeMod173Times800PlusShapeCountTimes1500PlusTextCountTimes1100:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_173_times_800_plus_shape_count_times_1500_plus_text_count_times_1100
        return fodg_file_size_mod_173_times_800_plus_shape_count_times_1500_plus_text_count_times_1100

    def test_empty_page(self): assert self._fn()(EMPTY) == 12000
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 73800
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 63500
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 12000
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 12000
    def test_minimal_largest(self):
        fn = self._fn(); assert fn(MINIMAL) > fn(SHAPES) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))
