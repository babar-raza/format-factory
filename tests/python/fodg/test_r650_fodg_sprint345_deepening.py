"""Sprint 345 FODG deepening."""
from __future__ import annotations
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
_S = _REPO / "samples" / "by-format" / "fodg"
_E = _S / "empty-page.fodg"
_M = _S / "minimal-drawing.fodg"
_SH = _S / "shapes-basic.fodg"

def _skip(p):
    if not p.exists(): pytest.skip(f"Missing: {p}")

class TestFodgFileSizeMod521Times3450PlusShapeCount4500PlusTextCount4000:
    def test_empty(self):
        _skip(_E)
        from src.python.fodg import fodg_file_size_mod_521_times_3450_plus_shape_count_times_4500_plus_text_count_times_4000 as f
        assert f(_E) == 37950
    def test_minimal(self):
        _skip(_M)
        from src.python.fodg import fodg_file_size_mod_521_times_3450_plus_shape_count_times_4500_plus_text_count_times_4000 as f
        assert f(_M) == 1495450
    def test_shapes(self):
        _skip(_SH)
        from src.python.fodg import fodg_file_size_mod_521_times_3450_plus_shape_count_times_4500_plus_text_count_times_4000 as f
        assert f(_SH) == 245750
    def test_int(self):
        _skip(_E)
        from src.python.fodg import fodg_file_size_mod_521_times_3450_plus_shape_count_times_4500_plus_text_count_times_4000 as f
        assert isinstance(f(_E), int)
    def test_nonneg(self):
        _skip(_E)
        from src.python.fodg import fodg_file_size_mod_521_times_3450_plus_shape_count_times_4500_plus_text_count_times_4000 as f
        assert f(_E) >= 0
    def test_minimal_gt_empty(self):
        _skip(_E); _skip(_M)
        from src.python.fodg import fodg_file_size_mod_521_times_3450_plus_shape_count_times_4500_plus_text_count_times_4000 as f
        assert f(_M) > f(_E)
    def test_str_path(self):
        _skip(_E)
        from src.python.fodg import fodg_file_size_mod_521_times_3450_plus_shape_count_times_4500_plus_text_count_times_4000 as f
        assert isinstance(f(str(_E)), int)
    def test_missing_raises(self):
        from src.python.fodg import fodg_file_size_mod_521_times_3450_plus_shape_count_times_4500_plus_text_count_times_4000 as f
        with pytest.raises(Exception): f("/nonexistent/file.fodg")
    def test_shapes_gt_empty(self):
        _skip(_E); _skip(_SH)
        from src.python.fodg import fodg_file_size_mod_521_times_3450_plus_shape_count_times_4500_plus_text_count_times_4000 as f
        assert f(_SH) > f(_E)
    def test_exported(self):
        import src.python.fodg as m
        assert hasattr(m, "fodg_file_size_mod_521_times_3450_plus_shape_count_times_4500_plus_text_count_times_4000")

class TestFodgFileSizeTimes165PlusShape71PlusText70PlusPage71:
    def test_empty(self):
        _skip(_E)
        from src.python.fodg import fodg_file_size_times_165_plus_shape_times_71_plus_text_times_70_plus_page_times_71 as f
        assert f(_E) == 173816
    def test_minimal(self):
        _skip(_M)
        from src.python.fodg import fodg_file_size_times_165_plus_shape_times_71_plus_text_times_70_plus_page_times_71 as f
        assert f(_M) == 243257
    def test_shapes(self):
        _skip(_SH)
        from src.python.fodg import fodg_file_size_times_165_plus_shape_times_71_plus_text_times_70_plus_page_times_71 as f
        assert f(_SH) == 269044
    def test_int(self):
        _skip(_E)
        from src.python.fodg import fodg_file_size_times_165_plus_shape_times_71_plus_text_times_70_plus_page_times_71 as f
        assert isinstance(f(_E), int)
    def test_nonneg(self):
        _skip(_E)
        from src.python.fodg import fodg_file_size_times_165_plus_shape_times_71_plus_text_times_70_plus_page_times_71 as f
        assert f(_E) >= 0
    def test_minimal_gt_empty(self):
        _skip(_E); _skip(_M)
        from src.python.fodg import fodg_file_size_times_165_plus_shape_times_71_plus_text_times_70_plus_page_times_71 as f
        assert f(_M) > f(_E)
    def test_str_path(self):
        _skip(_E)
        from src.python.fodg import fodg_file_size_times_165_plus_shape_times_71_plus_text_times_70_plus_page_times_71 as f
        assert isinstance(f(str(_E)), int)
    def test_missing_raises(self):
        from src.python.fodg import fodg_file_size_times_165_plus_shape_times_71_plus_text_times_70_plus_page_times_71 as f
        with pytest.raises(Exception): f("/nonexistent/file.fodg")
    def test_shapes_gt_empty(self):
        _skip(_E); _skip(_SH)
        from src.python.fodg import fodg_file_size_times_165_plus_shape_times_71_plus_text_times_70_plus_page_times_71 as f
        assert f(_SH) > f(_E)
    def test_exported(self):
        import src.python.fodg as m
        assert hasattr(m, "fodg_file_size_times_165_plus_shape_times_71_plus_text_times_70_plus_page_times_71")
