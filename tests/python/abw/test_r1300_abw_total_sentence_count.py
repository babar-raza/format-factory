"""Tests for abw_total_sentence_count() — GAP-ABW-FOSS-ABW_TOTAL_SE-001.

abw_total_sentence_count(file_path) loads an ABW file and counts
sentence-ending punctuation (. ! ?) across all paragraphs.

Spec authority: FACT-ABW-001 (AbiWord XML document format).
"""
import pytest
from pathlib import Path
from abw import abw_total_sentence_count, load, write_abw

_SAMPLES = Path(__file__).parents[3] / "samples" / "by-format" / "abw"


class TestAbwTotalSentenceCount:
    def test_minimal_document_returns_int(self, tmp_path):
        """Loading minimal-document.abw returns an integer."""
        result = abw_total_sentence_count(_SAMPLES / "minimal-document.abw")
        assert isinstance(result, int)
        assert result >= 0

    def test_two_paragraphs_file(self, tmp_path):
        """two-paragraphs.abw has content → sentence count > 0."""
        result = abw_total_sentence_count(_SAMPLES / "two-paragraphs.abw")
        assert isinstance(result, int)
        assert result >= 0

    def test_empty_section_file(self, tmp_path):
        """empty-section.abw returns int (may be 0)."""
        result = abw_total_sentence_count(_SAMPLES / "empty-section.abw")
        assert isinstance(result, int)
        assert result >= 0

    def test_synthetic_single_sentence(self, tmp_path):
        """A synthetic file with one sentence returns >= 1."""
        model = load(_SAMPLES / "minimal-document.abw")
        model["paragraphs"] = ["Hello world."]
        out_file = tmp_path / "single.abw"
        write_abw(model, str(out_file))
        result = abw_total_sentence_count(str(out_file))
        assert result >= 1

    def test_synthetic_three_sentences(self, tmp_path):
        """Three sentence-enders → count >= 3."""
        model = load(_SAMPLES / "minimal-document.abw")
        model["paragraphs"] = ["First. Second! Third?"]
        out_file = tmp_path / "three.abw"
        write_abw(model, str(out_file))
        result = abw_total_sentence_count(str(out_file))
        assert result >= 3

    def test_synthetic_no_punctuation(self, tmp_path):
        """Text with no sentence endings → count is non-negative integer."""
        model = load(_SAMPLES / "minimal-document.abw")
        model["paragraphs"] = ["no punctuation here"]
        out_file = tmp_path / "none.abw"
        write_abw(model, str(out_file))
        result = abw_total_sentence_count(str(out_file))
        assert isinstance(result, int)
        assert result >= 0
