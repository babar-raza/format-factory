"""Tests for extended ODT text analytics functions."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.odt.text_document import (
    odt_has_headings,
    odt_avg_paragraph_length,
    odt_max_paragraph_length,
    odt_has_single_paragraph,
)

SAMPLES = Path("samples/by-format/odt/valid")
MINIMAL = SAMPLES / "minimal-document.odt"    # 1 paragraph: 'Hello, world.' (13 chars)
TWO = SAMPLES / "two-paragraphs.odt"           # 2 paragraphs: 16 and 17 chars


# --- odt_has_headings ---

def test_has_headings_minimal():
    assert odt_has_headings(MINIMAL) is False


def test_has_headings_two():
    assert odt_has_headings(TWO) is False


def test_has_headings_returns_bool():
    assert isinstance(odt_has_headings(MINIMAL), bool)


# --- odt_avg_paragraph_length ---

def test_avg_paragraph_length_minimal():
    # 'Hello, world.' = 13 chars, 1 paragraph → avg 13.0
    assert odt_avg_paragraph_length(MINIMAL) == pytest.approx(13.0)


def test_avg_paragraph_length_two():
    # 'First paragraph.' (16) + 'Second paragraph.' (17) → avg 16.5
    assert odt_avg_paragraph_length(TWO) == pytest.approx(16.5)


def test_avg_paragraph_length_returns_float():
    assert isinstance(odt_avg_paragraph_length(MINIMAL), float)


def test_avg_paragraph_length_positive():
    assert odt_avg_paragraph_length(MINIMAL) > 0.0


# --- odt_max_paragraph_length ---

def test_max_paragraph_length_minimal():
    assert odt_max_paragraph_length(MINIMAL) == 13


def test_max_paragraph_length_two():
    assert odt_max_paragraph_length(TWO) == 17


def test_max_paragraph_length_returns_int():
    assert isinstance(odt_max_paragraph_length(MINIMAL), int)


def test_max_paragraph_length_gte_avg():
    assert odt_max_paragraph_length(TWO) >= odt_avg_paragraph_length(TWO)


# --- odt_has_single_paragraph ---

def test_has_single_paragraph_minimal():
    assert odt_has_single_paragraph(MINIMAL) is True


def test_has_single_paragraph_two():
    assert odt_has_single_paragraph(TWO) is False


def test_has_single_paragraph_returns_bool():
    assert isinstance(odt_has_single_paragraph(MINIMAL), bool)
