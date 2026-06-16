"""Sprint 52: ODT odt_max_paragraph_length + odt_avg_chars_per_paragraph (R262)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from odt.odt_parser import odt_max_paragraph_length, odt_avg_chars_per_paragraph

ODT_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"

MINIMAL = ODT_DIR / "minimal-document.odt"
TWO_PARA = ODT_DIR / "two-paragraphs.odt"
UNICODE = ODT_DIR / "unicode-text.odt"


# --- odt_max_paragraph_length ---

def test_max_para_len_minimal_is_13():
    assert odt_max_paragraph_length(MINIMAL) == 13


def test_max_para_len_two_paragraphs_is_17():
    # "Second paragraph." is 17 chars
    assert odt_max_paragraph_length(TWO_PARA) == 17


def test_max_para_len_unicode_nonnegative():
    result = odt_max_paragraph_length(UNICODE)
    assert result >= 0


def test_max_para_len_returns_int():
    assert isinstance(odt_max_paragraph_length(MINIMAL), int)


def test_max_para_len_ge_shortest():
    from odt.odt_parser import odt_shortest_paragraph_length
    assert odt_max_paragraph_length(TWO_PARA) >= odt_shortest_paragraph_length(TWO_PARA)


# --- odt_avg_chars_per_paragraph ---

def test_avg_chars_minimal_is_13():
    assert odt_avg_chars_per_paragraph(MINIMAL) == 13.0


def test_avg_chars_two_paragraphs_is_16_5():
    # (16 + 17) / 2 = 16.5
    result = odt_avg_chars_per_paragraph(TWO_PARA)
    assert abs(result - 16.5) < 0.01


def test_avg_chars_unicode_nonnegative():
    result = odt_avg_chars_per_paragraph(UNICODE)
    assert result >= 0.0


def test_avg_chars_returns_float():
    assert isinstance(odt_avg_chars_per_paragraph(MINIMAL), float)


def test_avg_chars_consistent_with_max():
    avg = odt_avg_chars_per_paragraph(TWO_PARA)
    max_len = odt_max_paragraph_length(TWO_PARA)
    assert avg <= max_len
