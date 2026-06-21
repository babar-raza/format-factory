"""Sprint 134 — FODG bytes_per_shape/text_to_shape_ratio, SYLK numeric_ratio/is_all_numeric."""
import sys, pathlib, pytest
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fodg.fodg_codec import fodg_bytes_per_shape, fodg_text_to_shape_ratio
from src.python.sylk.sylk_parser import sylk_numeric_ratio, sylk_is_all_numeric

F1 = str(_REPO / "samples/by-format/fodg/empty-page.fodg")
F2 = str(_REPO / "samples/by-format/fodg/minimal-drawing.fodg")
F3 = str(_REPO / "samples/by-format/fodg/shapes-basic.fodg")
S1 = str(_REPO / "samples/by-format/sylk/valid/minimal-2x2.slk")
S2 = str(_REPO / "samples/by-format/sylk/valid/numeric-row.slk")
S3 = str(_REPO / "samples/by-format/sylk/valid/single-cell.slk")

class TestFodgBytesPerShape:
    def test_empty(self):
        assert fodg_bytes_per_shape(F1) == 0.0
    def test_minimal(self):
        assert fodg_bytes_per_shape(F2) == 1473.0
    def test_shapes_basic(self):
        assert abs(fodg_bytes_per_shape(F3) - 542.6667) < 0.01
    def test_return_type(self):
        assert isinstance(fodg_bytes_per_shape(F1), float)
    def test_non_negative(self):
        assert fodg_bytes_per_shape(F3) >= 0.0

class TestFodgTextToShapeRatio:
    def test_empty(self):
        assert fodg_text_to_shape_ratio(F1) == 0.0
    def test_minimal(self):
        assert fodg_text_to_shape_ratio(F2) == 1.0
    def test_shapes_basic(self):
        assert abs(fodg_text_to_shape_ratio(F3) - 0.6667) < 0.01
    def test_return_type(self):
        assert isinstance(fodg_text_to_shape_ratio(F1), float)
    def test_bounded(self):
        assert 0.0 <= fodg_text_to_shape_ratio(F2) <= 1.0

class TestSylkNumericRatio:
    def test_minimal(self):
        assert sylk_numeric_ratio(S1) == 0.25
    def test_numeric_row(self):
        assert sylk_numeric_ratio(S2) == 1.0
    def test_single_cell(self):
        assert sylk_numeric_ratio(S3) == 1.0
    def test_return_type(self):
        assert isinstance(sylk_numeric_ratio(S1), float)
    def test_bounded(self):
        assert 0.0 <= sylk_numeric_ratio(S1) <= 1.0

class TestSylkIsAllNumeric:
    def test_minimal(self):
        assert sylk_is_all_numeric(S1) is False
    def test_numeric_row(self):
        assert sylk_is_all_numeric(S2) is True
    def test_single_cell(self):
        assert sylk_is_all_numeric(S3) is True
    def test_return_type(self):
        assert isinstance(sylk_is_all_numeric(S1), bool)
    def test_consistency(self):
        assert sylk_is_all_numeric(S2) == (sylk_numeric_ratio(S2) == 1.0)
