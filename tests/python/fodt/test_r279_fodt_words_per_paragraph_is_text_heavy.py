"""Tests for fodt_words_per_paragraph and fodt_is_text_heavy (Sprint 69)."""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from fodt.neutral_model import fodt_words_per_paragraph, fodt_is_text_heavy

FODT = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodt"


class TestFodtWordsPerParagraph:
    def test_minimal(self):
        assert abs(fodt_words_per_paragraph(FODT / "minimal-document.fodt") - 2.0) < 0.01

    def test_headings(self):
        assert abs(fodt_words_per_paragraph(FODT / "headings-and-paragraphs.fodt") - 11.0) < 0.01

    def test_table(self):
        assert abs(fodt_words_per_paragraph(FODT / "table-basic.fodt") - 3.5) < 0.01

    def test_returns_float(self):
        assert isinstance(fodt_words_per_paragraph(FODT / "minimal-document.fodt"), float)

    def test_nonnegative(self):
        for f in ["minimal-document.fodt", "headings-and-paragraphs.fodt", "table-basic.fodt"]:
            assert fodt_words_per_paragraph(FODT / f) >= 0.0


class TestFodtIsTextHeavy:
    def test_minimal_not_heavy(self):
        assert fodt_is_text_heavy(FODT / "minimal-document.fodt") is False

    def test_headings_is_heavy(self):
        assert fodt_is_text_heavy(FODT / "headings-and-paragraphs.fodt") is True

    def test_table_not_heavy(self):
        assert fodt_is_text_heavy(FODT / "table-basic.fodt") is False

    def test_returns_bool(self):
        assert isinstance(fodt_is_text_heavy(FODT / "minimal-document.fodt"), bool)

    def test_all_files(self):
        results = [fodt_is_text_heavy(FODT / f) for f in ["minimal-document.fodt", "headings-and-paragraphs.fodt", "table-basic.fodt"]]
        assert any(r is True for r in results)
        assert any(r is False for r in results)
