"""Tests for odt_table_count function."""
import sys
import zipfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from odt.odt_parser import odt_table_count

_SAMPLES = _REPO / "samples" / "by-format" / "odt"


def _make_odt(tmp_path, tables=0, paragraphs=1, name="test.odt"):
    """Create a minimal ODT file with specified number of tables."""
    content_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<office:document-content'
        ' xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
        ' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
        ' xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0">',
        '<office:body><office:text>',
    ]
    for i in range(paragraphs):
        content_parts.append(f'<text:p>Paragraph {i}</text:p>')
    for i in range(tables):
        content_parts.append(
            f'<table:table table:name="Table{i}">'
            '<table:table-row><table:table-cell>'
            '<text:p>cell</text:p>'
            '</table:table-cell></table:table-row>'
            '</table:table>'
        )
    content_parts.append('</office:text></office:body></office:document-content>')
    content_xml = "".join(content_parts)

    p = tmp_path / name
    with zipfile.ZipFile(p, "w") as zf:
        zf.writestr("mimetype", "application/vnd.oasis.opendocument.text")
        zf.writestr("content.xml", content_xml)
        zf.writestr("META-INF/manifest.xml",
            '<?xml version="1.0"?>'
            '<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">'
            '<manifest:file-entry manifest:full-path="/" manifest:media-type="application/vnd.oasis.opendocument.text"/>'
            '</manifest:manifest>')
    return str(p)


class TestOdtTableCount:
    def test_no_tables(self, tmp_path):
        path = _make_odt(tmp_path, tables=0)
        assert odt_table_count(path) == 0

    def test_one_table(self, tmp_path):
        path = _make_odt(tmp_path, tables=1)
        assert odt_table_count(path) == 1

    def test_multiple_tables(self, tmp_path):
        path = _make_odt(tmp_path, tables=3)
        assert odt_table_count(path) == 3

    def test_return_type(self, tmp_path):
        path = _make_odt(tmp_path, tables=0)
        assert isinstance(odt_table_count(path), int)

    def test_non_negative(self, tmp_path):
        path = _make_odt(tmp_path, tables=0)
        assert odt_table_count(path) >= 0

    def test_real_sample_no_crash(self):
        sample = _SAMPLES / "minimal-text.odt"
        if sample.exists():
            count = odt_table_count(str(sample))
            assert isinstance(count, int)
            assert count >= 0

    def test_tables_with_paragraphs(self, tmp_path):
        path = _make_odt(tmp_path, tables=2, paragraphs=3)
        assert odt_table_count(path) == 2

    def test_importable_from_package(self):
        from odt import odt_table_count as fn
        assert callable(fn)
