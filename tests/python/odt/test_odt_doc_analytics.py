"""Tests for ODT document analytics functions."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.odt.odt_doc_analytics import (
    odt_paragraph_count,
    odt_heading_count,
    odt_element_count,
    odt_is_ok,
    odt_first_paragraph_text,
    odt_total_text_length,
)

SAMPLES = Path("samples/by-format/odt/valid")
MINIMAL = SAMPLES / "minimal-document.odt"
TWO_PARA = SAMPLES / "two-paragraphs.odt"
# minimal-document.odt: 1 paragraph ['Hello, world.'], 0 headings, element_count=1
# two-paragraphs.odt: 2 paragraphs ['First paragraph.', 'Second paragraph.'], 0 headings, element_count=2


# --- odt_paragraph_count ---

def test_paragraph_count_minimal():
    assert odt_paragraph_count(MINIMAL) == 1


def test_paragraph_count_two():
    assert odt_paragraph_count(TWO_PARA) == 2


def test_paragraph_count_returns_int():
    assert isinstance(odt_paragraph_count(MINIMAL), int)


# --- odt_heading_count ---

def test_heading_count_minimal():
    assert odt_heading_count(MINIMAL) == 0


def test_heading_count_two():
    assert odt_heading_count(TWO_PARA) == 0


def test_heading_count_returns_int():
    assert isinstance(odt_heading_count(MINIMAL), int)


# --- odt_element_count ---

def test_element_count_minimal():
    assert odt_element_count(MINIMAL) == 1


def test_element_count_two():
    assert odt_element_count(TWO_PARA) == 2


def test_element_count_returns_int():
    assert isinstance(odt_element_count(MINIMAL), int)


# --- odt_is_ok ---

def test_is_ok_minimal():
    assert odt_is_ok(MINIMAL) is True


def test_is_ok_two():
    assert odt_is_ok(TWO_PARA) is True


def test_is_ok_returns_bool():
    assert isinstance(odt_is_ok(MINIMAL), bool)


# --- odt_first_paragraph_text ---

def test_first_paragraph_text_minimal():
    assert odt_first_paragraph_text(MINIMAL) == "Hello, world."


def test_first_paragraph_text_two():
    assert odt_first_paragraph_text(TWO_PARA) == "First paragraph."


def test_first_paragraph_text_returns_str():
    assert isinstance(odt_first_paragraph_text(MINIMAL), str)


# --- odt_total_text_length ---

def test_total_text_length_minimal():
    # 'Hello, world.' = 13 chars
    assert odt_total_text_length(MINIMAL) == 13


def test_total_text_length_two():
    # 'First paragraph.' + 'Second paragraph.' = 16 + 17 = 33
    assert odt_total_text_length(TWO_PARA) == 33


def test_total_text_length_returns_int():
    assert isinstance(odt_total_text_length(MINIMAL), int)


def test_total_text_length_positive():
    assert odt_total_text_length(MINIMAL) > 0
