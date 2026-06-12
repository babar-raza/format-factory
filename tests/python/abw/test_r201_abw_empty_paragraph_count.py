"""
Tests for abw_empty_paragraph_count — sprint product-deepening-rnext70.

Sprint: FORMAT-FACTORY-ABW-ZST-DEEPENING-001
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ABW_SAMPLES = REPO / "samples" / "by-format" / "abw"

sys.path.insert(0, str(REPO / "src" / "python"))

from abw.abw_codec import abw_empty_paragraph_count


def test_import():
    assert callable(abw_empty_paragraph_count)


def test_minimal_document_returns_zero():
    result = abw_empty_paragraph_count(ABW_SAMPLES / "minimal-document.abw")
    assert result == 0


def test_two_paragraphs_returns_zero():
    result = abw_empty_paragraph_count(ABW_SAMPLES / "two-paragraphs.abw")
    assert result == 0


def test_empty_section_returns_zero():
    result = abw_empty_paragraph_count(ABW_SAMPLES / "empty-section.abw")
    assert result == 0


def test_returns_int():
    result = abw_empty_paragraph_count(ABW_SAMPLES / "minimal-document.abw")
    assert isinstance(result, int)


def test_result_nonnegative():
    result = abw_empty_paragraph_count(ABW_SAMPLES / "two-paragraphs.abw")
    assert result >= 0
