"""
tests/python/abw/test_r120_abw_html_and_metadata.py

Sprint: FORMAT-FACTORY-PRODUCT-FIRST-AUTONOMOUS-ACQUISITION-TRAIN-001
TC-ABW-HTML: export_to_html()
TC-ABW-META: get_metadata()
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path


_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    create_abw,
    write_abw,
    export_to_html,
    get_metadata,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_abw_file(paragraphs: list[str]) -> Path:
    """Write a temp ABW file and return its path."""
    model = create_abw(paragraphs)
    with tempfile.NamedTemporaryFile(suffix=".abw", delete=False) as f:
        tmp = Path(f.name)
    write_abw(model, tmp)
    return tmp


# ---------------------------------------------------------------------------
# TC-ABW-HTML: export_to_html
# ---------------------------------------------------------------------------

class TestExportToHtml:
    """Tests for export_to_html()."""

    def test_returns_string(self):
        tmp = _make_abw_file(["Hello"])
        try:
            result = export_to_html(tmp)
            assert isinstance(result, str)
        finally:
            tmp.unlink()

    def test_contains_html_structure(self):
        tmp = _make_abw_file(["Hello"])
        try:
            result = export_to_html(tmp)
            assert "<!DOCTYPE html>" in result
            assert "<html>" in result
            assert "<body>" in result
            assert "</body>" in result
            assert "</html>" in result
        finally:
            tmp.unlink()

    def test_single_paragraph_wraps_in_p(self):
        tmp = _make_abw_file(["Hello world"])
        try:
            result = export_to_html(tmp)
            assert "<p>Hello world</p>" in result
        finally:
            tmp.unlink()

    def test_multiple_paragraphs(self):
        tmp = _make_abw_file(["First", "Second", "Third"])
        try:
            result = export_to_html(tmp)
            assert "<p>First</p>" in result
            assert "<p>Second</p>" in result
            assert "<p>Third</p>" in result
        finally:
            tmp.unlink()

    def test_paragraph_order_preserved(self):
        tmp = _make_abw_file(["Alpha", "Beta", "Gamma"])
        try:
            result = export_to_html(tmp)
            idx_a = result.index("<p>Alpha</p>")
            idx_b = result.index("<p>Beta</p>")
            idx_g = result.index("<p>Gamma</p>")
            assert idx_a < idx_b < idx_g
        finally:
            tmp.unlink()

    def test_empty_document(self):
        tmp = _make_abw_file([])
        try:
            result = export_to_html(tmp)
            assert "<html>" in result
            assert "<p>" not in result
        finally:
            tmp.unlink()

    def test_html_escape_lt_gt(self):
        tmp = _make_abw_file(["a < b > c"])
        try:
            result = export_to_html(tmp)
            assert "&lt;" in result
            assert "&gt;" in result
            assert "a < b" not in result
        finally:
            tmp.unlink()

    def test_html_escape_ampersand(self):
        tmp = _make_abw_file(["cats & dogs"])
        try:
            result = export_to_html(tmp)
            assert "&amp;" in result
        finally:
            tmp.unlink()

    def test_html_escape_quote(self):
        tmp = _make_abw_file(['say "hello"'])
        try:
            result = export_to_html(tmp)
            assert "&quot;" in result
        finally:
            tmp.unlink()

    def test_accepts_bytes(self):
        tmp = _make_abw_file(["From bytes"])
        try:
            raw = tmp.read_bytes()
            result = export_to_html(raw)
            assert "<p>From bytes</p>" in result
        finally:
            tmp.unlink()

    def test_accepts_string_path(self):
        tmp = _make_abw_file(["From string path"])
        try:
            result = export_to_html(str(tmp))
            assert "<p>From string path</p>" in result
        finally:
            tmp.unlink()

    def test_accepts_xml_bytes_directly(self):
        xml = b'<?xml version="1.0"?><abiword version="1.0" fileformat="1.0"><section><p>Direct</p></section></abiword>'
        result = export_to_html(xml)
        assert "<p>Direct</p>" in result

    def test_newline_between_elements(self):
        tmp = _make_abw_file(["One", "Two"])
        try:
            result = export_to_html(tmp)
            assert "\n" in result
        finally:
            tmp.unlink()

    def test_p_tags_inside_body(self):
        tmp = _make_abw_file(["Content"])
        try:
            result = export_to_html(tmp)
            body_start = result.index("<body>")
            body_end = result.index("</body>")
            p_pos = result.index("<p>Content</p>")
            assert body_start < p_pos < body_end
        finally:
            tmp.unlink()

    def test_roundtrip_create_write_export_html(self):
        model = create_abw(["Hello", "World"])
        tmp = Path(tempfile.mktemp(suffix=".abw"))
        try:
            write_abw(model, tmp)
            html = export_to_html(tmp)
            assert "<p>Hello</p>" in html
            assert "<p>World</p>" in html
        finally:
            if tmp.exists():
                tmp.unlink()


# ---------------------------------------------------------------------------
# TC-ABW-META: get_metadata
# ---------------------------------------------------------------------------

class TestGetMetadata:
    """Tests for get_metadata()."""

    def test_returns_dict(self):
        tmp = _make_abw_file(["Hello"])
        try:
            result = get_metadata(tmp)
            assert isinstance(result, dict)
        finally:
            tmp.unlink()

    def test_created_doc_has_empty_metadata(self):
        """Documents created by create_abw() have no metadata block."""
        tmp = _make_abw_file(["Hello"])
        try:
            result = get_metadata(tmp)
            assert result == {}
        finally:
            tmp.unlink()

    def test_metadata_from_real_abw_with_meta_element(self):
        """ABW with <metadata><m key='dc.title' value='My Title'/></metadata>."""
        xml = (
            b'<?xml version="1.0"?>'
            b'<abiword version="1.0" fileformat="1.0">'
            b'<metadata>'
            b'<m key="dc.title" value="My Title"/>'
            b'<m key="dc.creator" value="Alice"/>'
            b'</metadata>'
            b'<section><p>Body text</p></section>'
            b'</abiword>'
        )
        result = get_metadata(xml)
        assert result.get("dc.title") == "My Title"
        assert result.get("dc.creator") == "Alice"

    def test_metadata_keys_are_strings(self):
        xml = (
            b'<?xml version="1.0"?>'
            b'<abiword version="1.0" fileformat="1.0">'
            b'<metadata><m key="dc.title" value="Test"/></metadata>'
            b'<section><p>X</p></section>'
            b'</abiword>'
        )
        result = get_metadata(xml)
        for k, v in result.items():
            assert isinstance(k, str)
            assert isinstance(v, str)

    def test_accepts_bytes(self):
        tmp = _make_abw_file(["Para"])
        try:
            raw = tmp.read_bytes()
            result = get_metadata(raw)
            assert isinstance(result, dict)
        finally:
            tmp.unlink()

    def test_accepts_string_path(self):
        tmp = _make_abw_file(["Para"])
        try:
            result = get_metadata(str(tmp))
            assert isinstance(result, dict)
        finally:
            tmp.unlink()

    def test_no_metadata_element_returns_empty(self):
        xml = (
            b'<?xml version="1.0"?>'
            b'<abiword version="1.0" fileformat="1.0">'
            b'<section><p>No meta</p></section>'
            b'</abiword>'
        )
        result = get_metadata(xml)
        assert result == {}

    def test_multiple_meta_keys_all_extracted(self):
        xml = (
            b'<?xml version="1.0"?>'
            b'<abiword version="1.0" fileformat="1.0">'
            b'<metadata>'
            b'<m key="dc.title" value="T1"/>'
            b'<m key="dc.creator" value="C1"/>'
            b'<m key="dc.description" value="D1"/>'
            b'</metadata>'
            b'<section><p>Body</p></section>'
            b'</abiword>'
        )
        result = get_metadata(xml)
        assert len(result) == 3
        assert "dc.title" in result
        assert "dc.creator" in result
        assert "dc.description" in result
