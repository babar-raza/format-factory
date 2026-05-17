"""
tests/skills/test_abw_gate4_prototype.py

Gate 4 prototype validation tests for AbiWord (.abw) format.
Tests the prototypes/by-format/abw/abw_parser.py prototype.
"""

import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROTO_DIR = REPO_ROOT / "prototypes" / "by-format" / "abw"
SAMPLES_DIR = REPO_ROOT / "samples" / "by-format" / "abw"

sys.path.insert(0, str(PROTO_DIR))
from abw_parser import parse_abw, count_sections, get_paragraph_count, extract_text, ABW_MIME


def test_parse_abw_minimal_is_abw():
    """minimal-document.abw must be identified as ABW."""
    result = parse_abw(SAMPLES_DIR / "minimal-document.abw")
    assert result["error"] is None, f"Unexpected error: {result['error']}"
    assert result["is_abw"] is True


def test_section_count_minimal():
    """minimal-document.abw has 1 section."""
    assert count_sections(SAMPLES_DIR / "minimal-document.abw") == 1


def test_section_count_empty():
    """empty-section.abw has 1 section."""
    assert count_sections(SAMPLES_DIR / "empty-section.abw") == 1


def test_paragraph_count_minimal():
    """minimal-document.abw has 1 paragraph."""
    assert get_paragraph_count(SAMPLES_DIR / "minimal-document.abw") == 1


def test_paragraph_count_two():
    """two-paragraphs.abw has 2 paragraphs."""
    assert get_paragraph_count(SAMPLES_DIR / "two-paragraphs.abw") == 2


def test_paragraph_count_empty():
    """empty-section.abw has 0 paragraphs."""
    assert get_paragraph_count(SAMPLES_DIR / "empty-section.abw") == 0


def test_extract_text_minimal():
    """minimal-document.abw contains 'Hello' text."""
    texts = extract_text(SAMPLES_DIR / "minimal-document.abw")
    assert any("Hello" in t for t in texts)


def test_extract_text_two_paragraphs():
    """two-paragraphs.abw has text from both paragraphs."""
    texts = extract_text(SAMPLES_DIR / "two-paragraphs.abw")
    assert len(texts) >= 2


def test_extract_text_empty():
    """empty-section.abw has no text."""
    texts = extract_text(SAMPLES_DIR / "empty-section.abw")
    assert texts == []


def test_parse_abw_bytes_input():
    """parse_abw accepts bytes input."""
    data = (SAMPLES_DIR / "minimal-document.abw").read_bytes()
    result = parse_abw(data)
    assert result["is_abw"] is True


def test_parse_abw_file_not_found():
    result = parse_abw(REPO_ROOT / "nonexistent.abw")
    assert result["error"] is not None


def test_parse_abw_invalid_xml():
    result = parse_abw(b"not xml at all <<<")
    assert result["error"] is not None
    assert result["is_abw"] is False


def test_parse_abw_wrong_root():
    result = parse_abw(b"<?xml version='1.0'?><root/>")
    assert result["error"] is not None


def test_all_corpus_samples_parse():
    """All ABW corpus samples parse without error."""
    samples = list(SAMPLES_DIR.glob("*.abw"))
    assert len(samples) >= 3
    for sample in samples:
        result = parse_abw(sample)
        assert result["error"] is None, f"{sample.name}: {result['error']}"
        assert result["is_abw"] is True
