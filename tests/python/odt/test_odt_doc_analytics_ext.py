"""Tests for ODT doc analytics extension functions in odt_doc_analytics.py."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.odt.odt_doc_analytics import (
    odt_has_paragraphs,
    odt_has_headings,
    odt_avg_paragraph_length,
    odt_max_paragraph_length,
    odt_paragraph_texts,
    odt_is_single_paragraph,
)

SAMPLES = Path("samples/by-format/odt/valid")
MINIMAL = SAMPLES / "minimal-document.odt"       # 1 para "Hello, world." (13 chars)
TWO_PARA = SAMPLES / "two-paragraphs.odt"         # 2 paras "First paragraph." / "Second paragraph."
UNICODE = SAMPLES / "unicode-text.odt"            # 1 para (unicode)


# odt_has_paragraphs
def test_has_paragraphs_minimal():
    assert odt_has_paragraphs(MINIMAL) is True

def test_has_paragraphs_two_para():
    assert odt_has_paragraphs(TWO_PARA) is True

def test_has_paragraphs_returns_bool():
    assert isinstance(odt_has_paragraphs(MINIMAL), bool)


# odt_has_headings
def test_has_headings_minimal_false():
    assert odt_has_headings(MINIMAL) is False

def test_has_headings_two_para_false():
    assert odt_has_headings(TWO_PARA) is False

def test_has_headings_returns_bool():
    assert isinstance(odt_has_headings(MINIMAL), bool)


# odt_avg_paragraph_length
def test_avg_paragraph_length_minimal():
    # "Hello, world." = 13 chars, 1 para
    avg = odt_avg_paragraph_length(MINIMAL)
    assert avg == pytest.approx(13.0)

def test_avg_paragraph_length_two_para():
    # "First paragraph." = 16, "Second paragraph." = 17 → avg = 16.5
    avg = odt_avg_paragraph_length(TWO_PARA)
    assert avg == pytest.approx(16.5)

def test_avg_paragraph_length_returns_float():
    assert isinstance(odt_avg_paragraph_length(MINIMAL), float)


# odt_max_paragraph_length
def test_max_paragraph_length_minimal():
    assert odt_max_paragraph_length(MINIMAL) == 13

def test_max_paragraph_length_two_para():
    # max("First paragraph."=16, "Second paragraph."=17) = 17
    assert odt_max_paragraph_length(TWO_PARA) == 17

def test_max_paragraph_length_returns_int():
    assert isinstance(odt_max_paragraph_length(MINIMAL), int)


# odt_paragraph_texts
def test_paragraph_texts_minimal():
    texts = odt_paragraph_texts(MINIMAL)
    assert texts == ["Hello, world."]

def test_paragraph_texts_two_para():
    texts = odt_paragraph_texts(TWO_PARA)
    assert len(texts) == 2
    assert texts[0] == "First paragraph."
    assert texts[1] == "Second paragraph."

def test_paragraph_texts_returns_list():
    assert isinstance(odt_paragraph_texts(MINIMAL), list)


# odt_is_single_paragraph
def test_is_single_paragraph_minimal():
    assert odt_is_single_paragraph(MINIMAL) is True

def test_is_single_paragraph_two_para():
    assert odt_is_single_paragraph(TWO_PARA) is False

def test_is_single_paragraph_returns_bool():
    assert isinstance(odt_is_single_paragraph(MINIMAL), bool)
