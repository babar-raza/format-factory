"""
tests/skills/test_xpm_gate4_prototype.py

Gate 4 prototype validation tests for XPM (X PixMap) format.
Tests the prototypes/by-format/xpm/xpm_parser.py prototype.
Evidence type: STANDALONE_PROTOTYPE
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROTO_DIR = REPO_ROOT / "prototypes" / "by-format" / "xpm"
SAMPLES_DIR = REPO_ROOT / "samples" / "by-format" / "xpm"

sys.path.insert(0, str(PROTO_DIR))
from xpm_parser import is_xpm3, parse_xpm3, XpmParseError


def test_valid_xpm3_loads():
    result = parse_xpm3(SAMPLES_DIR / "1x1-red.xpm")
    assert result["error"] is None, f"Unexpected error: {result['error']}"
    assert result["format_id"] == "xpm"


def test_dimensions_correct_1x1():
    result = parse_xpm3(SAMPLES_DIR / "1x1-red.xpm")
    assert result["width"] == 1
    assert result["height"] == 1


def test_dimensions_correct_2x2():
    result = parse_xpm3(SAMPLES_DIR / "2x2-checker.xpm")
    assert result["width"] == 2
    assert result["height"] == 2


def test_dimensions_correct_3x1():
    result = parse_xpm3(SAMPLES_DIR / "3x1-rgb.xpm")
    assert result["width"] == 3
    assert result["height"] == 1


def test_color_table_parsed():
    result = parse_xpm3(SAMPLES_DIR / "1x1-red.xpm")
    assert "colors" in result
    assert len(result["colors"]) == result["ncolors"]


def test_pixel_rows_present():
    result = parse_xpm3(SAMPLES_DIR / "1x1-red.xpm")
    assert "pixel_rows" in result
    assert len(result["pixel_rows"]) == result["height"]


def test_is_xpm3_positive():
    assert is_xpm3(SAMPLES_DIR / "1x1-red.xpm") is True


def test_is_xpm3_negative():
    assert is_xpm3(SAMPLES_DIR / "invalid-no-magic.xpm") is False


def test_invalid_magic_rejected():
    import pytest
    with pytest.raises(XpmParseError):
        parse_xpm3(SAMPLES_DIR / "invalid-no-magic.xpm")


def test_malformed_dimensions_rejected():
    import pytest
    with pytest.raises(XpmParseError):
        parse_xpm3(b'/* XPM */\nstatic char * t[] = {\n"BAD"\n};')


def test_parse_xpm3_bytes_input():
    data = (SAMPLES_DIR / "1x1-red.xpm").read_bytes()
    result = parse_xpm3(data)
    assert result["error"] is None
    assert result["width"] == 1


def test_parse_xpm3_file_not_found():
    import pytest
    with pytest.raises((XpmParseError, FileNotFoundError, OSError)):
        parse_xpm3(REPO_ROOT / "nonexistent.xpm")


def test_all_valid_corpus_samples_parse():
    """All valid XPM3 corpus samples parse without error."""
    valid_samples = [
        SAMPLES_DIR / "1x1-red.xpm",
        SAMPLES_DIR / "2x2-checker.xpm",
        SAMPLES_DIR / "3x1-rgb.xpm",
    ]
    for sample in valid_samples:
        result = parse_xpm3(sample)
        assert result["error"] is None, f"{sample.name}: {result['error']}"
        assert result["format_id"] == "xpm"
