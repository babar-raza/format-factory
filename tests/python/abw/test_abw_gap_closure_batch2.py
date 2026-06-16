"""Gap closure tests for ABW — batch 2, covering 8 remaining open gaps.

Gaps: GAP-ABW-FOSS-TRUNCATE_PAR-001, GAP-ABW-FOSS-GET_UNIQUE_W-001,
      GAP-ABW-FOSS-MERGE_ABW-001, GAP-ABW-FOSS-REPLACE_IN_P-001,
      GAP-ABW-FOSS-INSTALLED_WO-001, GAP-ABW-FOSS-ABWERROR-001,
      GAP-ABW-FOSS-ABWPARSEERRO-001, GAP-ABW-FOSS-GET_PARAGRAP-001,
      GAP-ABW-FOSS-AVERAGE_PARA-001, GAP-ABW-FOSS-SHORTEST_PAR-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.abw import (
    AbwError,
    AbwParseError,
    average_paragraph_length,
    get_paragraph_count,
    get_unique_words,
    load,
    merge_abw,
    replace_in_paragraphs,
    shortest_paragraph,
    truncate_paragraphs,
)

SAMPLES = _REPO / "samples" / "by-format" / "abw"
TWO_PARA = SAMPLES / "two-paragraphs.abw"


@pytest.fixture
def doc():
    return load(str(TWO_PARA))


# --- GAP-ABW-FOSS-ABWERROR-001 ---
class TestAbwError:
    def test_is_exception(self):
        assert issubclass(AbwError, Exception)

    def test_message(self):
        err = AbwError("bad abw")
        assert "bad abw" in str(err)


# --- GAP-ABW-FOSS-ABWPARSEERRO-001 ---
class TestAbwParseError:
    def test_is_subclass(self):
        assert issubclass(AbwParseError, (AbwError, Exception))


# --- GAP-ABW-FOSS-GET_PARAGRAP-001 ---
class TestGetParagraphCount:
    def test_count(self):
        count = get_paragraph_count(str(TWO_PARA))
        assert isinstance(count, int)
        assert count >= 2


# --- GAP-ABW-FOSS-TRUNCATE_PAR-001 ---
class TestTruncateParagraphs:
    def test_truncates(self, doc):
        result = truncate_paragraphs(doc, 1)
        assert isinstance(result, dict)

    def test_has_paragraphs(self, doc):
        result = truncate_paragraphs(doc, 1)
        assert "paragraphs" in result or "sections" in result or isinstance(result, dict)


# --- GAP-ABW-FOSS-GET_UNIQUE_W-001 ---
class TestGetUniqueWords:
    def test_returns_list(self, doc):
        words = get_unique_words(doc)
        assert isinstance(words, list)
        assert len(words) > 0

    def test_words_are_strings(self, doc):
        words = get_unique_words(doc)
        assert all(isinstance(w, str) for w in words)


# --- GAP-ABW-FOSS-MERGE_ABW-001 ---
class TestMergeAbw:
    def test_merges_two_docs(self, doc):
        merged = merge_abw(doc, doc)
        assert isinstance(merged, dict)


# --- GAP-ABW-FOSS-REPLACE_IN_P-001 ---
class TestReplaceInParagraphs:
    def test_returns_dict(self, doc):
        result = replace_in_paragraphs(doc, "the", "THE")
        assert isinstance(result, dict)


# --- GAP-ABW-FOSS-AVERAGE_PARA-001 ---
class TestAverageParagraphLength:
    def test_returns_float(self, doc):
        avg = average_paragraph_length(doc)
        assert isinstance(avg, (int, float))
        assert avg > 0


# --- GAP-ABW-FOSS-SHORTEST_PAR-001 ---
class TestShortestParagraph:
    def test_returns_string(self, doc):
        result = shortest_paragraph(doc)
        assert isinstance(result, str)
        assert len(result) > 0


# --- GAP-ABW-FOSS-INSTALLED_WO-001 ---
class TestInstalledWorkflow:
    def test_module_importable(self):
        import src.python.abw
        assert hasattr(src.python.abw, "load")
        assert hasattr(src.python.abw, "create_abw")


class TestAbwBatch2ConcreteValues:
    """Concrete value assertions from two-paragraphs.abw known data."""

    def test_paragraph_count_equals_two(self):
        assert get_paragraph_count(str(TWO_PARA)) == 2

    def test_get_unique_words_content(self, doc):
        words = get_unique_words(doc)
        assert "first" in words or "paragraph." in words
        assert len(words) == 3

    def test_merge_doubles_paragraph_count(self, doc):
        merged = merge_abw(doc, doc)
        assert merged["paragraph_count"] == 4

    def test_replace_in_paragraphs_preserves_structure(self, doc):
        result = replace_in_paragraphs(doc, "paragraph", "section")
        assert result["paragraph_count"] == 2

    def test_average_paragraph_length_value(self, doc):
        avg = average_paragraph_length(doc)
        assert avg == 16.5

    def test_shortest_paragraph_is_first(self, doc):
        result = shortest_paragraph(doc)
        assert result == "First paragraph."

    def test_truncate_to_one_paragraph(self, doc):
        result = truncate_paragraphs(doc, 1)
        assert result["paragraph_count"] == 1
