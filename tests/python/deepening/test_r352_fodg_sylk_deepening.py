"""Sprint 142 deepening tests: FODG text_per_page/is_text_heavy, SYLK min_value_length/cell_density."""
import sys, pathlib, pytest
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg.fodg_codec import fodg_text_per_page, fodg_is_text_heavy
from src.python.sylk.sylk_parser import sylk_min_value_length, sylk_cell_density

F1 = str(_REPO / "samples/by-format/fodg/empty-page.fodg")
F2 = str(_REPO / "samples/by-format/fodg/minimal-drawing.fodg")
F3 = str(_REPO / "samples/by-format/fodg/shapes-basic.fodg")
S1 = str(_REPO / "samples/by-format/sylk/valid/minimal-2x2.slk")
S2 = str(_REPO / "samples/by-format/sylk/valid/numeric-row.slk")
S3 = str(_REPO / "samples/by-format/sylk/valid/single-cell.slk")


class TestFodgTextPerPage:
    def test_empty(self):
        assert fodg_text_per_page(F1) == 0.0

    def test_minimal(self):
        assert fodg_text_per_page(F2) == 1.0

    def test_shapes(self):
        assert fodg_text_per_page(F3) == 2.0

    def test_return_type(self):
        assert isinstance(fodg_text_per_page(F1), float)

    def test_nonnegative(self):
        assert fodg_text_per_page(F3) >= 0.0


class TestFodgIsTextHeavy:
    def test_empty(self):
        assert fodg_is_text_heavy(F1) is False

    def test_minimal(self):
        assert fodg_is_text_heavy(F2) is True

    def test_shapes(self):
        assert fodg_is_text_heavy(F3) is True

    def test_return_type(self):
        assert isinstance(fodg_is_text_heavy(F1), bool)

    def test_empty_no_shapes(self):
        assert fodg_is_text_heavy(F1) is False


class TestSylkMinValueLength:
    def test_minimal(self):
        assert sylk_min_value_length(S1) == 2

    def test_numeric(self):
        assert sylk_min_value_length(S2) == 1

    def test_single(self):
        assert sylk_min_value_length(S3) == 2

    def test_return_type(self):
        assert isinstance(sylk_min_value_length(S1), int)

    def test_positive(self):
        assert sylk_min_value_length(S2) > 0


class TestSylkCellDensity:
    def test_minimal(self):
        assert abs(sylk_cell_density(S1) - 0.4444) < 0.01

    def test_numeric(self):
        assert abs(sylk_cell_density(S2) - 0.375) < 0.01

    def test_single(self):
        assert abs(sylk_cell_density(S3) - 0.25) < 0.01

    def test_return_type(self):
        assert isinstance(sylk_cell_density(S1), float)

    def test_bounded(self):
        assert 0.0 < sylk_cell_density(S1) <= 1.0
