"""Sprint 137 — FODS is_single_sheet/nonempty_ratio, FODP is_single_slide/chars_per_slide."""
import sys, pathlib, pytest
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fods.neutral_model import fods_is_single_sheet, fods_nonempty_ratio
from src.python.fodp.fodp_codec import fodp_is_single_slide, fodp_chars_per_slide

F1 = str(_REPO / "samples/by-format/fods/minimal-spreadsheet.fods")
F2 = str(_REPO / "samples/by-format/fods/multi-sheet-basic.fods")
F3 = str(_REPO / "samples/by-format/fods/typed-values-basic.fods")
P1 = str(_REPO / "samples/by-format/fodp/minimal-presentation.fodp")
P2 = str(_REPO / "samples/by-format/fodp/two-slides-basic.fodp")
P3 = str(_REPO / "samples/by-format/fodp/title-only.fodp")

class TestFodsIsSingleSheet:
    def test_minimal(self):
        assert fods_is_single_sheet(F1) is True
    def test_multi(self):
        assert fods_is_single_sheet(F2) is False
    def test_typed(self):
        assert fods_is_single_sheet(F3) is True
    def test_return_type(self):
        assert isinstance(fods_is_single_sheet(F1), bool)
    def test_consistency(self):
        assert fods_is_single_sheet(F2) is False

class TestFodsNonemptyRatio:
    def test_minimal(self):
        assert fods_nonempty_ratio(F1) == 1.0
    def test_multi(self):
        assert fods_nonempty_ratio(F2) == 1.0
    def test_typed(self):
        assert fods_nonempty_ratio(F3) == 1.0
    def test_return_type(self):
        assert isinstance(fods_nonempty_ratio(F1), float)
    def test_bounded(self):
        assert 0.0 <= fods_nonempty_ratio(F1) <= 1.0

class TestFodpIsSingleSlide:
    def test_minimal(self):
        assert fodp_is_single_slide(P1) is True
    def test_two(self):
        assert fodp_is_single_slide(P2) is False
    def test_title(self):
        assert fodp_is_single_slide(P3) is False
    def test_return_type(self):
        assert isinstance(fodp_is_single_slide(P1), bool)
    def test_consistency(self):
        assert fodp_is_single_slide(P1) is True

class TestFodpCharsPerSlide:
    def test_minimal(self):
        assert fodp_chars_per_slide(P1) == 5.0
    def test_two(self):
        assert fodp_chars_per_slide(P2) == 21.5
    def test_title(self):
        assert fodp_chars_per_slide(P3) == 0.0
    def test_return_type(self):
        assert isinstance(fodp_chars_per_slide(P1), float)
    def test_non_negative(self):
        assert fodp_chars_per_slide(P1) >= 0.0
