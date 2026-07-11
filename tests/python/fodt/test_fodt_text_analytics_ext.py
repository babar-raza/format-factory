"""Tests for FODT text analytics extension functions."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodt.text_document_analytics import (
    fodt_has_content,
    fodt_first_block_type,
    fodt_first_block_text,
    fodt_heading_texts,
    fodt_paragraph_texts,
    fodt_all_blocks_have_text,
)

SAMPLES = Path("samples/by-format/fodt")
MINIMAL = SAMPLES / "minimal-document.fodt"        # 1 block, paragraph, 'Hello, world.'
HEADINGS = SAMPLES / "headings-and-paragraphs.fodt" # 7 blocks: 3 headings + 4 paragraphs
LIST = SAMPLES / "list-basic.fodt"                  # 2 paragraph blocks
TABLE = SAMPLES / "table-basic.fodt"                # 2 paragraph blocks


# --- fodt_has_content ---

def test_has_content_minimal():
    assert fodt_has_content(MINIMAL) is True


def test_has_content_headings():
    assert fodt_has_content(HEADINGS) is True


def test_has_content_returns_bool():
    assert isinstance(fodt_has_content(MINIMAL), bool)


# --- fodt_first_block_type ---

def test_first_block_type_minimal():
    assert fodt_first_block_type(MINIMAL) == "paragraph"


def test_first_block_type_headings():
    assert fodt_first_block_type(HEADINGS) == "heading"


def test_first_block_type_list():
    assert fodt_first_block_type(LIST) == "paragraph"


def test_first_block_type_returns_str():
    assert isinstance(fodt_first_block_type(MINIMAL), str)


# --- fodt_first_block_text ---

def test_first_block_text_minimal():
    assert fodt_first_block_text(MINIMAL) == "Hello, world."


def test_first_block_text_headings():
    assert fodt_first_block_text(HEADINGS) == "Section One"


def test_first_block_text_returns_str():
    assert isinstance(fodt_first_block_text(MINIMAL), str)


# --- fodt_heading_texts ---

def test_heading_texts_minimal():
    assert fodt_heading_texts(MINIMAL) == []


def test_heading_texts_headings():
    result = fodt_heading_texts(HEADINGS)
    assert result == ["Section One", "Subsection One A", "Section Two"]


def test_heading_texts_returns_list():
    assert isinstance(fodt_heading_texts(MINIMAL), list)


# --- fodt_paragraph_texts ---

def test_paragraph_texts_minimal():
    assert fodt_paragraph_texts(MINIMAL) == ["Hello, world."]


def test_paragraph_texts_headings_count():
    result = fodt_paragraph_texts(HEADINGS)
    assert len(result) == 4


def test_paragraph_texts_returns_list():
    assert isinstance(fodt_paragraph_texts(MINIMAL), list)


# --- fodt_all_blocks_have_text ---

def test_all_blocks_have_text_minimal():
    assert fodt_all_blocks_have_text(MINIMAL) is True


def test_all_blocks_have_text_headings():
    assert fodt_all_blocks_have_text(HEADINGS) is True


def test_all_blocks_have_text_returns_bool():
    assert isinstance(fodt_all_blocks_have_text(MINIMAL), bool)
