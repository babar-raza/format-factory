"""Tests for odt_longest_paragraph and odt_has_tables.

Product deepening: ODT analytics — TC-H3-002-ODT / PDC-ODT-LONGEST-TABLES-001.
"""
import sys, zipfile
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.odt import odt_longest_paragraph, odt_has_tables


def _make_odt(tmp_path, name, paragraphs, has_table=False):
    ns_o = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    ns_t = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    ns_tab = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    paras = "".join(f'<text:p>{p}</text:p>' for p in paragraphs)
    table_xml = ""
    if has_table:
        table_xml = (
            f'<table:table table:name="T1">'
            f'<table:table-row><table:table-cell><text:p>cell</text:p></table:table-cell></table:table-row>'
            f'</table:table>'
        )
    content = (
        f'<?xml version="1.0"?>'
        f'<office:document-content xmlns:office="{ns_o}" xmlns:text="{ns_t}" xmlns:table="{ns_tab}">'
        f'<office:body><office:text>{paras}{table_xml}</office:text></office:body>'
        f'</office:document-content>'
    )
    p = tmp_path / f"{name}.odt"
    with zipfile.ZipFile(str(p), "w") as zf:
        zf.writestr("mimetype", "application/vnd.oasis.opendocument.text")
        zf.writestr("content.xml", content)
        zf.writestr("META-INF/manifest.xml",
            '<?xml version="1.0"?><manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">'
            '<manifest:file-entry manifest:full-path="/" manifest:media-type="application/vnd.oasis.opendocument.text"/>'
            '</manifest:manifest>')
    return p


class TestOdtLongestParagraph:
    def test_single(self, tmp_path):
        p = _make_odt(tmp_path, "one", ["hello world"])
        result = odt_longest_paragraph(p)
        assert isinstance(result, int)
        assert result >= 11

    def test_multiple(self, tmp_path):
        p = _make_odt(tmp_path, "multi", ["hi", "a much longer paragraph text"])
        result = odt_longest_paragraph(p)
        assert result >= 20

    def test_empty(self, tmp_path):
        p = _make_odt(tmp_path, "empty", [])
        result = odt_longest_paragraph(p)
        assert result == 0

    def test_returns_int(self, tmp_path):
        p = _make_odt(tmp_path, "type", ["test"])
        assert isinstance(odt_longest_paragraph(p), int)

    def test_non_negative(self, tmp_path):
        p = _make_odt(tmp_path, "nn", ["x"])
        assert odt_longest_paragraph(p) >= 0


class TestOdtHasTables:
    def test_no_tables(self, tmp_path):
        p = _make_odt(tmp_path, "no_tbl", ["text only"])
        assert odt_has_tables(p) is False

    def test_with_table(self, tmp_path):
        p = _make_odt(tmp_path, "tbl", ["text"], has_table=True)
        assert odt_has_tables(p) is True

    def test_returns_bool(self, tmp_path):
        p = _make_odt(tmp_path, "bool_type", ["x"])
        assert isinstance(odt_has_tables(p), bool)

    def test_empty(self, tmp_path):
        p = _make_odt(tmp_path, "empty_tbl", [])
        assert odt_has_tables(p) is False

    def test_consistent(self, tmp_path):
        p = _make_odt(tmp_path, "consist", ["text"])
        assert odt_has_tables(p) == odt_has_tables(p)
