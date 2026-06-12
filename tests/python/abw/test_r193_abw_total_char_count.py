"""Tests for abw_total_char_count — rnext62 product deepening."""
from pathlib import Path

ABW_DIR = Path("samples/by-format/abw")


def test_import():
    from src.python.abw import abw_total_char_count
    assert callable(abw_total_char_count)


def test_minimal_document_count():
    from src.python.abw import abw_total_char_count
    result = abw_total_char_count(ABW_DIR / "minimal-document.abw")
    assert result == 5  # "Hello"


def test_two_paragraphs_count():
    from src.python.abw import abw_total_char_count
    result = abw_total_char_count(ABW_DIR / "two-paragraphs.abw")
    assert result == 33  # "First paragraph." + "Second paragraph."


def test_empty_section_returns_zero():
    from src.python.abw import abw_total_char_count
    result = abw_total_char_count(ABW_DIR / "empty-section.abw")
    assert result == 0


def test_returns_int():
    from src.python.abw import abw_total_char_count
    result = abw_total_char_count(ABW_DIR / "minimal-document.abw")
    assert isinstance(result, int)


def test_all_samples_nonnegative():
    from src.python.abw import abw_total_char_count
    for fname in ["minimal-document.abw", "two-paragraphs.abw", "empty-section.abw"]:
        result = abw_total_char_count(ABW_DIR / fname)
        assert result >= 0
