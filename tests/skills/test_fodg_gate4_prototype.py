"""
tests/skills/test_fodg_gate4_prototype.py

Gate 4 prototype validation tests for FODG (.fodg) format.
Tests the prototypes/by-format/fodg/fodg_parser.py prototype.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROTO_DIR = REPO_ROOT / "prototypes" / "by-format" / "fodg"
SAMPLES_DIR = REPO_ROOT / "samples" / "by-format" / "fodg"

sys.path.insert(0, str(PROTO_DIR))
from fodg_parser import parse_fodg, count_pages, get_shape_count, extract_text, FODG_MIME


def test_parse_fodg_minimal_is_fodg():
    """minimal-drawing.fodg must be identified as FODG."""
    result = parse_fodg(SAMPLES_DIR / "minimal-drawing.fodg")
    assert result["error"] is None
    assert result["is_fodg"] is True
    assert result["mime_type"] == FODG_MIME


def test_page_count_minimal():
    """minimal-drawing.fodg has 1 page."""
    assert count_pages(SAMPLES_DIR / "minimal-drawing.fodg") == 1


def test_page_count_shapes_basic():
    """shapes-basic.fodg has 1 page."""
    assert count_pages(SAMPLES_DIR / "shapes-basic.fodg") == 1


def test_shape_count_minimal():
    """minimal-drawing.fodg has 1 shape."""
    assert get_shape_count(SAMPLES_DIR / "minimal-drawing.fodg") == 1


def test_shape_count_shapes_basic():
    """shapes-basic.fodg has 3 shapes (rect, ellipse, line)."""
    assert get_shape_count(SAMPLES_DIR / "shapes-basic.fodg") == 3


def test_shape_count_empty():
    """empty-page.fodg has 0 shapes."""
    assert get_shape_count(SAMPLES_DIR / "empty-page.fodg") == 0


def test_parse_fodg_bytes_input():
    """parse_fodg accepts bytes input."""
    data = (SAMPLES_DIR / "minimal-drawing.fodg").read_bytes()
    result = parse_fodg(data)
    assert result["is_fodg"] is True


def test_parse_fodg_file_not_found():
    result = parse_fodg(REPO_ROOT / "nonexistent.fodg")
    assert result["error"] is not None


def test_parse_fodg_invalid_xml():
    result = parse_fodg(b"not xml <<<<<")
    assert result["error"] is not None
    assert result["is_fodg"] is False


def test_parse_fodg_wrong_root():
    result = parse_fodg(b"<?xml version='1.0'?><root/>")
    assert result["error"] is not None


def test_all_corpus_samples_parse():
    """All FODG corpus samples parse without error."""
    samples = list(SAMPLES_DIR.glob("*.fodg"))
    assert len(samples) >= 3
    for sample in samples:
        result = parse_fodg(sample)
        assert result["error"] is None, f"{sample.name}: {result['error']}"
        assert result["is_fodg"] is True


def test_extract_text_empty():
    texts = extract_text(SAMPLES_DIR / "empty-page.fodg")
    assert texts == []
