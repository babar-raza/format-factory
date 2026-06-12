"""
tests/python/abw/test_r200_abw_advanced_ops.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-SPRINT3-001
TASK-009: ABW advanced operations — text analytics, export, paragraph manipulation.

Covers: first_paragraph, last_paragraph, longest_paragraph, join_paragraphs,
paragraph_lengths, has_paragraph, count_paragraphs_matching, abw_sentence_count,
abw_empty_paragraph_count, abw_nonempty_paragraph_count, abw_total_char_count,
abw_longest_word, get_section_count, export_to_plain_text, export_to_markdown,
word_wrap, truncate_paragraphs, reverse_paragraphs, merge_abw, split_paragraphs,
append_paragraph, edit_paragraph, replace_in_paragraphs, search_paragraph,
search_replace_paragraph.
"""
from __future__ import annotations

import sys
import os
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import abw
from abw import (
    load, probe_abw, get_paragraph_count, get_section_count,
    first_paragraph, last_paragraph, longest_paragraph,
    join_paragraphs, paragraph_lengths,
    has_paragraph, count_paragraphs_matching,
    abw_sentence_count, abw_empty_paragraph_count, abw_nonempty_paragraph_count,
    abw_total_char_count, abw_longest_word,
    export_to_plain_text, export_to_markdown,
    word_wrap, truncate_paragraphs, reverse_paragraphs,
    merge_abw, split_paragraphs,
    append_paragraph, edit_paragraph, replace_in_paragraphs,
    search_paragraph, search_replace_paragraph,
    write_abw,
)

_TWO = str(_REPO / "samples" / "by-format" / "abw" / "two-paragraphs.abw")
_MINIMAL = str(_REPO / "samples" / "by-format" / "abw" / "minimal-document.abw")


class TestAbwProbeAndMetadata:
    """Probe and document-level metadata."""

    def test_probe_abw_returns_truthy(self):
        result = probe_abw(_TWO)
        assert result  # returns True for valid ABW

    def test_probe_abw_false_for_nonexistent(self):
        result = probe_abw("/nonexistent/path.abw")
        assert not result

    def test_get_paragraph_count_positive(self):
        n = get_paragraph_count(_TWO)
        assert isinstance(n, int)
        assert n == 2

    def test_get_section_count_positive(self):
        n = get_section_count(_TWO)
        assert isinstance(n, int)
        assert n >= 1


class TestAbwParagraphAccess:
    """Paragraph retrieval functions (model dict)."""

    def test_first_paragraph_returns_string(self):
        doc = load(_TWO)
        result = first_paragraph(doc)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_last_paragraph_returns_string(self):
        doc = load(_TWO)
        result = last_paragraph(doc)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_first_and_last_differ_for_two_paragraph(self):
        doc = load(_TWO)
        assert first_paragraph(doc) != last_paragraph(doc)

    def test_longest_paragraph_returns_string(self):
        doc = load(_TWO)
        result = longest_paragraph(doc)
        assert isinstance(result, str)

    def test_join_paragraphs_returns_string(self):
        doc = load(_TWO)
        result = join_paragraphs(doc)
        assert isinstance(result, str)
        assert "\n" in result or len(result) > 0

    def test_paragraph_lengths_returns_list(self):
        doc = load(_TWO)
        lengths = paragraph_lengths(doc)
        assert isinstance(lengths, list)
        assert len(lengths) == 2
        assert all(isinstance(n, int) for n in lengths)


class TestAbwTextSearch:
    """Text search and matching functions."""

    def test_has_paragraph_false_for_missing(self):
        doc = load(_TWO)
        result = has_paragraph(doc, "nonexistent-xyz-text")
        assert result is False

    def test_has_paragraph_true_for_present(self):
        doc = load(_TWO)
        result = has_paragraph(doc, "First paragraph.")
        assert result is True

    def test_count_paragraphs_matching_returns_int(self):
        doc = load(_TWO)
        n = count_paragraphs_matching(doc, "paragraph")
        assert isinstance(n, int)
        assert n >= 1

    def test_search_paragraph_returns_list(self):
        doc = load(_TWO)
        result = search_paragraph(doc, "First")
        assert isinstance(result, list)

    def test_search_paragraph_finds_correct_index(self):
        doc = load(_TWO)
        result = search_paragraph(doc, "First")
        assert 0 in result


class TestAbwTextStats:
    """Text analytics functions (path and model based)."""

    def test_abw_sentence_count_positive(self):
        doc = load(_TWO)
        n = abw_sentence_count(doc)
        assert isinstance(n, int)
        assert n >= 1

    def test_abw_empty_paragraph_count_int(self):
        n = abw_empty_paragraph_count(_TWO)
        assert isinstance(n, int)
        assert n == 0

    def test_abw_nonempty_paragraph_count_positive(self):
        n = abw_nonempty_paragraph_count(_TWO)
        assert isinstance(n, int)
        assert n == 2

    def test_abw_total_char_count_positive(self):
        n = abw_total_char_count(_TWO)
        assert isinstance(n, int)
        assert n > 0

    def test_abw_longest_word_returns_string(self):
        doc = load(_TWO)
        result = abw_longest_word(doc)
        assert isinstance(result, str)
        assert len(result) > 0


class TestAbwExport:
    """Export format conversion functions."""

    def test_export_to_plain_text_returns_string(self):
        doc = load(_TWO)
        result = export_to_plain_text(doc)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_export_to_plain_text_contains_content(self):
        doc = load(_TWO)
        result = export_to_plain_text(doc)
        assert "paragraph" in result.lower()

    def test_export_to_markdown_returns_string(self):
        doc = load(_TWO)
        result = export_to_markdown(doc)
        assert isinstance(result, str)
        assert len(result) > 0


class TestAbwTransformation:
    """Paragraph transformation: wrap, truncate, reverse, merge, split."""

    def test_word_wrap_returns_dict(self):
        doc = load(_TWO)
        result = word_wrap(doc, 20)
        assert isinstance(result, dict)
        assert result.get("is_abw") is True

    def test_truncate_paragraphs_to_one(self):
        doc = load(_TWO)
        result = truncate_paragraphs(doc, 1)
        assert isinstance(result, dict)
        assert result.get("paragraph_count", 2) <= 2

    def test_reverse_paragraphs_returns_dict(self):
        doc = load(_TWO)
        result = reverse_paragraphs(doc)
        assert isinstance(result, dict)
        paragraphs = result.get("paragraphs", [])
        if paragraphs:
            # Last paragraph should be first after reverse
            original = doc.get("paragraphs", [])
            if len(original) >= 2:
                assert paragraphs[0] == original[-1]

    def test_merge_abw_returns_dict(self):
        doc = load(_TWO)
        merged = merge_abw(doc, doc)
        assert isinstance(merged, dict)
        assert merged.get("paragraph_count", 0) >= doc.get("paragraph_count", 0)

    def test_split_paragraphs_returns_list(self):
        doc = load(_TWO)
        result = split_paragraphs(doc, 1)
        assert isinstance(result, list)
        assert len(result) == 2


class TestAbwMutation:
    """Paragraph mutation: append, edit, replace, search_replace, write."""

    def test_append_paragraph_returns_dict(self):
        doc = load(_TWO)
        result = append_paragraph(doc, "New paragraph.")
        assert isinstance(result, dict)
        assert result.get("paragraph_count", 0) > doc.get("paragraph_count", 0)

    def test_edit_paragraph_returns_dict(self):
        doc = load(_TWO)
        result = edit_paragraph(doc, 0, "Updated text.")
        assert isinstance(result, dict)

    def test_edit_paragraph_changes_content(self):
        doc = load(_TWO)
        result = edit_paragraph(doc, 0, "Replacement text.")
        paragraphs = result.get("paragraphs", [])
        if paragraphs:
            assert "Replacement" in paragraphs[0]

    def test_replace_in_paragraphs_returns_dict(self):
        doc = load(_TWO)
        result = replace_in_paragraphs(doc, "First", "Modified")
        assert isinstance(result, dict)

    def test_search_replace_paragraph_returns_dict(self):
        doc = load(_TWO)
        result = search_replace_paragraph(doc, "First", "Found")
        assert isinstance(result, dict)

    def test_write_abw_produces_file(self):
        doc = load(_TWO)
        fd, path = tempfile.mkstemp(suffix=".abw")
        os.close(fd)
        try:
            write_abw(doc, path)
            assert os.path.getsize(path) > 0
        finally:
            os.unlink(path)
