"""Tests for odt_doc_analytics extension (ext2 batch)."""
from __future__ import annotations

from pathlib import Path

from odt.odt_doc_analytics import (
    odt_heading_texts,
    odt_is_empty,
    odt_min_paragraph_length,
    odt_last_paragraph_text,
    odt_total_heading_length,
    odt_has_content,
)

SAMPLES = Path("samples/by-format/odt/valid")
MINIMAL = SAMPLES / "minimal-document.odt"
TWO_PARA = SAMPLES / "two-paragraphs.odt"
UNICODE = SAMPLES / "unicode-text.odt"


# --- odt_heading_texts ---

def test_heading_texts_returns_list():
    result = odt_heading_texts(MINIMAL)
    assert isinstance(result, list)


def test_heading_texts_minimal():
    # minimal has no headings
    result = odt_heading_texts(MINIMAL)
    assert result == []


# --- odt_is_empty ---

def test_is_empty_minimal_false():
    assert odt_is_empty(MINIMAL) is False


def test_is_empty_returns_bool():
    assert isinstance(odt_is_empty(MINIMAL), bool)


# --- odt_min_paragraph_length ---

def test_min_paragraph_length_minimal():
    result = odt_min_paragraph_length(MINIMAL)
    assert isinstance(result, int)
    assert result >= 0


def test_min_paragraph_length_two_para():
    result = odt_min_paragraph_length(TWO_PARA)
    assert result >= 0


def test_min_paragraph_length_leq_max():
    from odt.odt_doc_analytics import odt_max_paragraph_length
    min_len = odt_min_paragraph_length(MINIMAL)
    max_len = odt_max_paragraph_length(MINIMAL)
    assert min_len <= max_len


# --- odt_last_paragraph_text ---

def test_last_paragraph_text_returns_str():
    result = odt_last_paragraph_text(MINIMAL)
    assert isinstance(result, str)


def test_last_paragraph_text_minimal_nonempty():
    result = odt_last_paragraph_text(MINIMAL)
    assert len(result) > 0


def test_last_paragraph_text_two_para():
    result = odt_last_paragraph_text(TWO_PARA)
    assert isinstance(result, str)
    assert len(result) > 0


# --- odt_total_heading_length ---

def test_total_heading_length_minimal_zero():
    # minimal has no headings
    result = odt_total_heading_length(MINIMAL)
    assert result == 0


def test_total_heading_length_returns_int():
    result = odt_total_heading_length(MINIMAL)
    assert isinstance(result, int)


# --- odt_has_content ---

def test_has_content_minimal_true():
    assert odt_has_content(MINIMAL) is True


def test_has_content_two_para_true():
    assert odt_has_content(TWO_PARA) is True


def test_has_content_returns_bool():
    assert isinstance(odt_has_content(MINIMAL), bool)
