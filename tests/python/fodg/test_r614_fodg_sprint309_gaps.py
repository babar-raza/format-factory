"""Sprint 309: FODG analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_FODG_SAMPLES = _REPO / "samples" / "by-format" / "fodg"

EMPTY = _FODG_SAMPLES / "empty-page.fodg"
MINIMAL = _FODG_SAMPLES / "minimal-drawing.fodg"
SHAPES = _FODG_SAMPLES / "shapes-basic.fodg"


class TestFodgFileSizeMod137Times450PlusShapeCountTimes1500PlusTextCountTimes1000:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_137_times_450_plus_shape_count_times_1500_plus_text_count_times_1000
        return fodg_file_size_mod_137_times_450_plus_shape_count_times_1500_plus_text_count_times_1000

    def test_empty_page(self): assert self._fn()(EMPTY) == 42300
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 48850
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 60950
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 42300
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 42300
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))


class TestFodgFileSizeMod139Times550PlusShapeCountTimes1200PlusTextCountTimes800:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_139_times_550_plus_shape_count_times_1200_plus_text_count_times_800
        return fodg_file_size_mod_139_times_550_plus_shape_count_times_1200_plus_text_count_times_800

    def test_empty_page(self): assert self._fn()(EMPTY) == 44000
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 47650
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 59650
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 44000
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 44000
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))
