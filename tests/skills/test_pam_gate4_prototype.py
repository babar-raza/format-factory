"""
tests/skills/test_pam_gate4_prototype.py

Gate 4 prototype validation tests for PAM (Portable Arbitrary Map / P7) format.
Tests the prototypes/by-format/pam/pam_parser.py prototype.
Evidence type: STANDALONE_PROTOTYPE
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROTO_DIR = REPO_ROOT / "prototypes" / "by-format" / "pam"
SAMPLES_DIR = REPO_ROOT / "samples" / "by-format" / "pam"

sys.path.insert(0, str(PROTO_DIR))
from pam_parser import is_pam, parse_pam, PamParseError


def test_valid_pam_loads():
    result = parse_pam(SAMPLES_DIR / "1x1-gray.pam")
    assert result["error"] is None, f"Unexpected error: {result['error']}"
    assert result["format_id"] == "pam"


def test_header_fields_parsed():
    result = parse_pam(SAMPLES_DIR / "1x1-gray.pam")
    assert result["width"] == 1
    assert result["height"] == 1
    assert result["depth"] >= 1
    assert result["maxval"] >= 1


def test_1x1_rgb_header():
    result = parse_pam(SAMPLES_DIR / "1x1-rgb.pam")
    assert result["error"] is None
    assert result["depth"] == 3


def test_2x2_bw_dimensions():
    result = parse_pam(SAMPLES_DIR / "2x2-bw.pam")
    assert result["error"] is None
    assert result["width"] == 2
    assert result["height"] == 2


def test_raster_length_validated():
    result = parse_pam(SAMPLES_DIR / "1x1-gray.pam")
    assert result["raster_length_valid"] is True


def test_is_pam_positive():
    assert is_pam(SAMPLES_DIR / "1x1-gray.pam") is True


def test_is_pam_negative():
    assert is_pam(SAMPLES_DIR / "invalid-wrong-magic.pam") is False


def test_invalid_magic_rejected():
    import pytest
    with pytest.raises(PamParseError):
        parse_pam(SAMPLES_DIR / "invalid-wrong-magic.pam")


def test_malformed_header_rejected():
    import pytest
    with pytest.raises(PamParseError):
        parse_pam(b"P7\nWIDTH 1\nENDHDR\n")  # Missing HEIGHT/DEPTH/MAXVAL


def test_parse_pam_bytes_input():
    data = (SAMPLES_DIR / "1x1-gray.pam").read_bytes()
    result = parse_pam(data)
    assert result["error"] is None
    assert result["format_id"] == "pam"


def test_parse_pam_file_not_found():
    import pytest
    with pytest.raises((PamParseError, FileNotFoundError, OSError)):
        parse_pam(REPO_ROOT / "nonexistent.pam")


def test_all_valid_corpus_samples_parse():
    """All valid PAM corpus samples parse without error."""
    valid_samples = [
        SAMPLES_DIR / "1x1-gray.pam",
        SAMPLES_DIR / "1x1-rgb.pam",
        SAMPLES_DIR / "2x2-bw.pam",
    ]
    for sample in valid_samples:
        result = parse_pam(sample)
        assert result["error"] is None, f"{sample.name}: {result['error']}"
        assert result["format_id"] == "pam"
