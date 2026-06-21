"""Tests for ABW load capability.

Closes:
  GAP-ABW-FOSS-LOAD-001  (Abw Load)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.abw import load as abw_load

_DIR = _REPO / "samples" / "by-format" / "abw"
_MINIMAL = str(_DIR / "minimal-document.abw")
_TWO_PARA = str(_DIR / "two-paragraphs.abw")


class TestAbwLoad:
    def test_return_type(self):
        result = abw_load(_MINIMAL)
        assert isinstance(result, dict)

    def test_is_abw_true(self):
        result = abw_load(_MINIMAL)
        assert result["is_abw"] is True

    def test_paragraph_count_1_for_minimal(self):
        result = abw_load(_MINIMAL)
        assert result["paragraph_count"] == 1

    def test_paragraph_count_2_for_two_paragraphs(self):
        result = abw_load(_TWO_PARA)
        assert result["paragraph_count"] == 2

    def test_section_count_1_for_minimal(self):
        result = abw_load(_MINIMAL)
        assert result["section_count"] == 1

    def test_paragraphs_hello_for_minimal(self):
        result = abw_load(_MINIMAL)
        assert result["paragraphs"] == ["Hello"]

    def test_consistent_across_calls(self):
        r1 = abw_load(_MINIMAL)
        r2 = abw_load(_MINIMAL)
        assert r1["paragraph_count"] == r2["paragraph_count"]
