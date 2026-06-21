"""Tests for FODG load capability.

Closes:
  GAP-FODG-FOSS-LOAD-001  (Fodg Load)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodg import load as fodg_load

_DIR = _REPO / "samples" / "by-format" / "fodg"
_EMPTY_PAGE = str(_DIR / "empty-page.fodg")
_MINIMAL_DRAWING = str(_DIR / "minimal-drawing.fodg")
_SHAPES_BASIC = str(_DIR / "shapes-basic.fodg")


class TestFodgLoad:
    def test_return_type(self):
        result = fodg_load(_EMPTY_PAGE)
        assert isinstance(result, dict)

    def test_is_fodg_true(self):
        result = fodg_load(_EMPTY_PAGE)
        assert result["is_fodg"] is True

    def test_page_count_1_for_empty(self):
        result = fodg_load(_EMPTY_PAGE)
        assert result["page_count"] == 1

    def test_shapes_total_0_for_empty(self):
        result = fodg_load(_EMPTY_PAGE)
        assert result["shapes_total"] == 0

    def test_shapes_total_3_for_shapes_basic(self):
        result = fodg_load(_SHAPES_BASIC)
        assert result["shapes_total"] == 3

    def test_mime_type_correct(self):
        result = fodg_load(_EMPTY_PAGE)
        assert result["mime_type"] == "application/vnd.oasis.opendocument.graphics-flat-xml"

    def test_consistent_across_calls(self):
        r1 = fodg_load(_SHAPES_BASIC)
        r2 = fodg_load(_SHAPES_BASIC)
        assert r1["shapes_total"] == r2["shapes_total"]
