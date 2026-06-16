"""Tests for fodt_empty_paragraph_count and fodt_table_count (Sprint 29)."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt import fodt_empty_paragraph_count, fodt_table_count

_FODT_SIMPLE = """\
<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
                 xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
                 office:mimetype="application/vnd.oasis.opendocument.text">
  <office:body><office:text>
    {content}
  </office:text></office:body>
</office:document>"""

_ONE_TABLE = (
    '<table:table><table:table-row>'
    '<table:table-cell><text:p>Cell</text:p></table:table-cell>'
    '</table:table-row></table:table>'
)


def _make_fodt(tmp_path, name, content):
    p = tmp_path / f"{name}.fodt"
    p.write_text(_FODT_SIMPLE.format(content=content), encoding="utf-8")
    return str(p)


class TestFodtEmptyParagraphCount:
    def test_return_type(self, tmp_path):
        p = _make_fodt(tmp_path, "rt", "<text:p>hello</text:p>")
        assert isinstance(fodt_empty_paragraph_count(p), int)

    def test_one_empty_among_nonempty(self, tmp_path):
        content = "<text:p>Hello world</text:p><text:p></text:p><text:p>Another</text:p>"
        p = _make_fodt(tmp_path, "oe", content)
        assert fodt_empty_paragraph_count(p) == 1

    def test_no_empty_paragraphs(self, tmp_path):
        p = _make_fodt(tmp_path, "ne", "<text:p>A</text:p><text:p>B</text:p>")
        assert fodt_empty_paragraph_count(p) == 0

    def test_all_empty(self, tmp_path):
        p = _make_fodt(tmp_path, "ae", "<text:p></text:p><text:p></text:p>")
        assert fodt_empty_paragraph_count(p) == 2

    def test_nonnegative(self, tmp_path):
        p = _make_fodt(tmp_path, "nn", "<text:p>text here</text:p>")
        assert fodt_empty_paragraph_count(p) >= 0


class TestFodtTableCount:
    def test_return_type(self, tmp_path):
        p = _make_fodt(tmp_path, "rt2", "<text:p>hello</text:p>")
        assert isinstance(fodt_table_count(p), int)

    def test_no_tables(self, tmp_path):
        p = _make_fodt(tmp_path, "nt", "<text:p>no tables here</text:p>")
        assert fodt_table_count(p) == 0

    def test_one_table_exact(self, tmp_path):
        # document with exactly 1 table -> 1
        p = _make_fodt(tmp_path, "ot", f"<text:p>Before</text:p>{_ONE_TABLE}")
        assert fodt_table_count(p) == 1

    def test_two_tables_exact(self, tmp_path):
        # document with 2 tables -> 2
        p = _make_fodt(tmp_path, "tt", f"{_ONE_TABLE}{_ONE_TABLE}")
        assert fodt_table_count(p) == 2

    def test_empty_document(self, tmp_path):
        p = _make_fodt(tmp_path, "ed", "")
        assert fodt_table_count(p) == 0
