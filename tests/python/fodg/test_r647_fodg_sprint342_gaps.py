"""Sprint 342: FODG analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_FODG_SAMPLES = _REPO / "samples" / "by-format" / "fodg"

EMPTY = _FODG_SAMPLES / "empty-page.fodg"
MINIMAL = _FODG_SAMPLES / "minimal-drawing.fodg"
SHAPES = _FODG_SAMPLES / "shapes-basic.fodg"


class TestFodgFileSizeMod227Times1150PlusShapeCountTimes2200PlusTextCountTimes1700:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_227_times_1150_plus_shape_count_times_2200_plus_text_count_times_1700
        return fodg_file_size_mod_227_times_1150_plus_shape_count_times_2200_plus_text_count_times_1700

    def test_empty_page(self): assert self._fn()(EMPTY) == 166750
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 131550
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 54850
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 166750
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 166750
    def test_empty_largest(self):
        fn = self._fn(); assert fn(EMPTY) > fn(MINIMAL) > fn(SHAPES)
    def test_shapes_smallest(self):
        fn = self._fn(); assert fn(SHAPES) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))


class TestFodgFileSizeMod229Times1200PlusShapeCountTimes1900PlusTextCountTimes1500:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_229_times_1200_plus_shape_count_times_1900_plus_text_count_times_1500
        return fodg_file_size_mod_229_times_1200_plus_shape_count_times_1900_plus_text_count_times_1500

    def test_empty_page(self): assert self._fn()(EMPTY) == 164400
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 122200
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 38700
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 164400
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 164400
    def test_empty_largest(self):
        fn = self._fn(); assert fn(EMPTY) > fn(MINIMAL) > fn(SHAPES)
    def test_shapes_smallest(self):
        fn = self._fn(); assert fn(SHAPES) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))
