"""Tests for document_has_tables — rnext64 product deepening."""
from pathlib import Path

FODT_DIR = Path("samples/by-format/fodt")


def test_import():
    from src.python.fodt import document_has_tables
    assert callable(document_has_tables)


def test_minimal_document_has_no_tables():
    from src.python.fodt import document_has_tables, parse_fodt
    doc = parse_fodt(FODT_DIR / "minimal-document.fodt")
    assert document_has_tables(doc) is False


def test_table_basic_has_tables():
    from src.python.fodt import document_has_tables, parse_fodt
    doc = parse_fodt(FODT_DIR / "table-basic.fodt")
    assert document_has_tables(doc) is True


def test_headings_has_no_tables():
    from src.python.fodt import document_has_tables, parse_fodt
    doc = parse_fodt(FODT_DIR / "headings-and-paragraphs.fodt")
    assert document_has_tables(doc) is False


def test_returns_bool():
    from src.python.fodt import document_has_tables, parse_fodt
    doc = parse_fodt(FODT_DIR / "minimal-document.fodt")
    assert isinstance(document_has_tables(doc), bool)


def test_empty_document_returns_false():
    from src.python.fodt import document_has_tables
    assert document_has_tables({}) is False
