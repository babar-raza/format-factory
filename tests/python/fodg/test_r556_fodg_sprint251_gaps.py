"""Sprint 251: FODG analytics — two new composite functions."""
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_FODG_SAMPLES = _REPO / "samples" / "by-format" / "fodg"

EMPTY = _FODG_SAMPLES / "empty-page.fodg"
MINIMAL = _FODG_SAMPLES / "minimal-drawing.fodg"
SHAPES = _FODG_SAMPLES / "shapes-basic.fodg"


class TestFodgFileSizeMod37Times600PlusShapeCountTimes1200PlusTextCountTimes900:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_37_times_600_plus_shape_count_times_1200_plus_text_count_times_900
        return fodg_file_size_mod_37_times_600_plus_shape_count_times_1200_plus_text_count_times_900

    def test_empty_page(self):
        assert self._fn()(EMPTY) == 10200

    def test_minimal_drawing(self):
        assert self._fn()(MINIMAL) == 20100

    def test_shapes_basic(self):
        assert self._fn()(SHAPES) == 5400

    def test_returns_int(self):
        assert isinstance(self._fn()(EMPTY), int)

    def test_distinct_values(self):
        fn = self._fn()
        vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}
        assert len(vals) == 3

    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]:
            assert fn(p) >= 0

    def test_path_object_accepted(self):
        fn = self._fn()
        assert fn(Path(EMPTY)) == 10200

    def test_string_path_accepted(self):
        fn = self._fn()
        assert fn(str(EMPTY)) == 10200

    def test_minimal_largest(self):
        fn = self._fn()
        assert fn(MINIMAL) > fn(EMPTY) > fn(SHAPES)

    def test_shapes_smallest(self):
        fn = self._fn()
        assert fn(SHAPES) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))


class TestFodgFileSizeMod43Times800PlusShapeCountTimes850PlusTextCountTimes650:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_43_times_800_plus_shape_count_times_850_plus_text_count_times_650
        return fodg_file_size_mod_43_times_800_plus_shape_count_times_850_plus_text_count_times_650

    def test_empty_page(self):
        assert self._fn()(EMPTY) == 16800

    def test_minimal_drawing(self):
        assert self._fn()(MINIMAL) == 10300

    def test_shapes_basic(self):
        assert self._fn()(SHAPES) == 33450

    def test_returns_int(self):
        assert isinstance(self._fn()(EMPTY), int)

    def test_distinct_values(self):
        fn = self._fn()
        vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}
        assert len(vals) == 3

    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]:
            assert fn(p) >= 0

    def test_path_object_accepted(self):
        fn = self._fn()
        assert fn(Path(EMPTY)) == 16800

    def test_string_path_accepted(self):
        fn = self._fn()
        assert fn(str(EMPTY)) == 16800

    def test_shapes_largest(self):
        fn = self._fn()
        assert fn(SHAPES) > fn(EMPTY) > fn(MINIMAL)

    def test_minimal_smallest(self):
        fn = self._fn()
        assert fn(MINIMAL) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))
