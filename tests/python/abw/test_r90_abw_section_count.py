"""Tests for ABW section count capability.

Gap closure: GAP-ABW-FOSS-ABW_SECTION_-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.abw import load, get_section_count

SAMPLES = _REPO / "samples" / "by-format" / "abw"


class TestAbwSectionCount:
    def test_minimal_document_has_one_section(self):
        f = SAMPLES / "minimal-document.abw"
        assert get_section_count(f) == 1

    def test_two_paragraphs_has_one_section(self):
        f = SAMPLES / "two-paragraphs.abw"
        assert get_section_count(f) == 1

    def test_empty_section(self):
        f = SAMPLES / "empty-section.abw"
        sc = get_section_count(f)
        assert isinstance(sc, int)
        assert sc >= 0

    def test_section_count_matches_model(self):
        f = SAMPLES / "minimal-document.abw"
        model = load(f)
        assert model["section_count"] == get_section_count(f)

    def test_section_count_returns_int(self):
        f = SAMPLES / "minimal-document.abw"
        sc = get_section_count(f)
        assert isinstance(sc, int)
