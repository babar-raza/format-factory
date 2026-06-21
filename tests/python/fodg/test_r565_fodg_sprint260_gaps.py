"""Sprint 260: FODG analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_FODG_SAMPLES = _REPO / "samples" / "by-format" / "fodg"

EMPTY = _FODG_SAMPLES / "empty-page.fodg"
MINIMAL = _FODG_SAMPLES / "minimal-drawing.fodg"
SHAPES = _FODG_SAMPLES / "shapes-basic.fodg"


class TestFodgFileSizeMod29Times5PlusShapeTimes1600PlusTextTimes1200PlusPageTimes700:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_29_times_5_plus_shape_times_1600_plus_text_times_1200_plus_page_times_700
        return fodg_file_size_mod_29_times_5_plus_shape_times_1600_plus_text_times_1200_plus_page_times_700

    def test_empty_page(self): assert self._fn()(EMPTY) == 745
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 3615
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 7920
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 745
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 745
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))


class TestFodgFileSizeTimes8PlusShapeTimes500PlusTextTimes250PlusPageTimes150:
    def _fn(self):
        from src.python.fodg import fodg_file_size_times_8_plus_shape_times_500_plus_text_times_250_plus_page_times_150
        return fodg_file_size_times_8_plus_shape_times_500_plus_text_times_250_plus_page_times_150

    def test_empty_page(self): assert self._fn()(EMPTY) == 8574
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 12684
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 15174
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 8574
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 8574
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))
