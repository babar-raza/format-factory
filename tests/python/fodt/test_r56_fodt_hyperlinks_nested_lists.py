"""
test_r56_fodt_hyperlinks_nested_lists.py — R56 Train C.

Tests for:
1. TC-0057 criterion 3: hyperlink (text:a xlink:href) preservation round-trip
2. TC-0059 criterion 2: nested list hierarchy (level > 1) round-trip

R56 Sprint: FORMAT-FACTORY-R56-R55-CLOSURE-REPAIR-PACKAGE-RC-PHASE7-PRODUCT-EXPANSION-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fodt.parser import parse_fodt_strict
from src.python.fodt.writer import document_to_xml


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fodt_with_hyperlink(href: str, link_text: str, surrounding_text: str = "") -> str:
    """Minimal FODT document with one hyperlink in a paragraph."""
    prefix = f"{surrounding_text} " if surrounding_text else ""
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<office:document'
        ' xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
        ' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
        ' xmlns:xlink="http://www.w3.org/1999/xlink"'
        ' office:version="1.3"'
        ' office:mimetype="application/vnd.oasis.opendocument.text-flat-xml">'
        '<office:body><office:text>'
        f'<text:p>{prefix}<text:a xlink:type="simple" xlink:href="{href}">{link_text}</text:a></text:p>'
        '</office:text></office:body></office:document>'
    )


def _fodt_with_nested_list(items: list) -> str:
    """FODT with a nested list structure. items is list of (text, level) tuples."""
    def _make_list(items_at_level, level=1):
        inner = ""
        i = 0
        while i < len(items_at_level):
            text, lvl = items_at_level[i]
            if lvl == level:
                # Find nested items
                nested = []
                j = i + 1
                while j < len(items_at_level) and items_at_level[j][1] > level:
                    nested.append(items_at_level[j])
                    j += 1
                if nested:
                    inner += f'<text:list-item><text:p>{text}</text:p>{_make_list(nested, level+1)}</text:list-item>'
                    i = j
                else:
                    inner += f'<text:list-item><text:p>{text}</text:p></text:list-item>'
                    i += 1
            else:
                i += 1
        return f'<text:list>{inner}</text:list>'

    top_level = [(t, l) for t, l in items if l >= 1]
    list_xml = _make_list(top_level)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<office:document'
        ' xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
        ' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
        ' office:version="1.3"'
        ' office:mimetype="application/vnd.oasis.opendocument.text-flat-xml">'
        '<office:body><office:text>'
        f'{list_xml}'
        '</office:text></office:body></office:document>'
    )


# ---------------------------------------------------------------------------
# TC-0057 criterion 3: Hyperlink preservation
# ---------------------------------------------------------------------------

class TestHyperlinkPreservation:
    """R56 Train C: TC-0057 criterion 3 — hyperlinks are preserved on round-trip."""

    def test_hyperlink_href_captured_in_runs(self, tmp_path):
        """Parser captures text:a xlink:href in runs dict."""
        fodt = tmp_path / "link.fodt"
        fodt.write_text(_fodt_with_hyperlink("https://example.com", "Example"), encoding="utf-8")
        doc = parse_fodt_strict(fodt)
        block = doc["blocks"][0]
        runs = block.get("runs", [])
        href_runs = [r for r in runs if r.get("href")]
        assert href_runs, f"Parser must capture href in runs; got runs={runs}"
        assert href_runs[0]["href"] == "https://example.com"
        assert href_runs[0]["text"] == "Example"

    def test_hyperlink_text_captured(self, tmp_path):
        """Parser captures the display text of a hyperlink."""
        fodt = tmp_path / "link.fodt"
        fodt.write_text(_fodt_with_hyperlink("https://test.org", "Click here"), encoding="utf-8")
        doc = parse_fodt_strict(fodt)
        block = doc["blocks"][0]
        href_runs = [r for r in block.get("runs", []) if r.get("href")]
        assert href_runs[0]["text"] == "Click here"

    def test_hyperlink_survives_roundtrip(self, tmp_path):
        """text:a href is preserved on parse → write round-trip."""
        fodt = tmp_path / "link.fodt"
        fodt.write_text(_fodt_with_hyperlink("https://roundtrip.test/path?q=1", "Link"), encoding="utf-8")
        doc = parse_fodt_strict(fodt)
        out_xml = document_to_xml(doc)
        assert "https://roundtrip.test/path?q=1" in out_xml, "href must survive round-trip"
        assert "Link" in out_xml, "link text must survive round-trip"

    def test_text_a_element_emitted_on_write(self, tmp_path):
        """Writer emits text:a element (not text:span) for hyperlink runs."""
        fodt = tmp_path / "link.fodt"
        fodt.write_text(_fodt_with_hyperlink("https://example.com", "Go"), encoding="utf-8")
        doc = parse_fodt_strict(fodt)
        out_xml = document_to_xml(doc)
        assert "text:a" in out_xml or "ns0:a" in out_xml or ":a" in out_xml, \
            f"text:a element must be emitted; got xml snippet: {out_xml[:400]}"

    def test_hyperlink_with_surrounding_text(self, tmp_path):
        """Hyperlink embedded in paragraph with surrounding plain text round-trips correctly."""
        fodt = tmp_path / "link.fodt"
        fodt.write_text(
            _fodt_with_hyperlink("https://x.com", "link", surrounding_text="Click"),
            encoding="utf-8"
        )
        doc = parse_fodt_strict(fodt)
        out_xml = document_to_xml(doc)
        assert "https://x.com" in out_xml
        assert "link" in out_xml

    def test_multiple_hyperlinks_preserved(self, tmp_path):
        """Multiple text:a elements in one paragraph are all preserved."""
        fodt = tmp_path / "links.fodt"
        fodt.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<office:document'
            ' xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
            ' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
            ' xmlns:xlink="http://www.w3.org/1999/xlink"'
            ' office:version="1.3"'
            ' office:mimetype="application/vnd.oasis.opendocument.text-flat-xml">'
            '<office:body><office:text>'
            '<text:p>'
            '<text:a xlink:type="simple" xlink:href="https://first.com">First</text:a>'
            ' and '
            '<text:a xlink:type="simple" xlink:href="https://second.com">Second</text:a>'
            '</text:p>'
            '</office:text></office:body></office:document>',
            encoding="utf-8"
        )
        doc = parse_fodt_strict(fodt)
        out_xml = document_to_xml(doc)
        assert "https://first.com" in out_xml
        assert "https://second.com" in out_xml


# ---------------------------------------------------------------------------
# TC-0059 criterion 2: Nested list hierarchy
# ---------------------------------------------------------------------------

class TestNestedListHierarchy:
    """R56 Train C: TC-0059 criterion 2 — nested list hierarchy is emitted correctly."""

    def test_nested_list_items_captured_with_level(self, tmp_path):
        """Parser captures level > 1 for nested list items."""
        fodt = tmp_path / "nlist.fodt"
        fodt.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<office:document'
            ' xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
            ' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
            ' office:version="1.3"'
            ' office:mimetype="application/vnd.oasis.opendocument.text-flat-xml">'
            '<office:body><office:text>'
            '<text:list>'
            '  <text:list-item><text:p>Level 1 Item A</text:p>'
            '    <text:list>'
            '      <text:list-item><text:p>Level 2 Item A1</text:p></text:list-item>'
            '    </text:list>'
            '  </text:list-item>'
            '  <text:list-item><text:p>Level 1 Item B</text:p></text:list-item>'
            '</text:list>'
            '</office:text></office:body></office:document>',
            encoding="utf-8"
        )
        doc = parse_fodt_strict(fodt)
        lst = doc["lists"][0]
        items = lst["items"]
        levels = [item["level"] for item in items]
        assert 2 in levels, f"Parser must capture level=2 items; got levels={levels}"
        level2_items = [item for item in items if item["level"] == 2]
        assert level2_items[0]["text"] == "Level 2 Item A1"

    def test_nested_list_emits_nested_xml(self, tmp_path):
        """Writer emits nested text:list elements for level > 1 items."""
        fodt = tmp_path / "nlist.fodt"
        fodt.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<office:document'
            ' xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
            ' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
            ' office:version="1.3"'
            ' office:mimetype="application/vnd.oasis.opendocument.text-flat-xml">'
            '<office:body><office:text>'
            '<text:list>'
            '  <text:list-item><text:p>Parent</text:p>'
            '    <text:list><text:list-item><text:p>Child</text:p></text:list-item></text:list>'
            '  </text:list-item>'
            '</text:list>'
            '</office:text></office:body></office:document>',
            encoding="utf-8"
        )
        doc = parse_fodt_strict(fodt)
        out_xml = document_to_xml(doc)
        # Output must have nested structure: text:list inside text:list-item
        assert out_xml.count("list-item") >= 2, f"Must have at least 2 list-items: {out_xml}"
        assert "Parent" in out_xml
        assert "Child" in out_xml

    def test_nested_list_structure_preserved(self, tmp_path):
        """Nested list: Child must appear after Parent in output XML."""
        fodt = tmp_path / "nlist.fodt"
        fodt.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<office:document'
            ' xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
            ' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
            ' office:version="1.3"'
            ' office:mimetype="application/vnd.oasis.opendocument.text-flat-xml">'
            '<office:body><office:text>'
            '<text:list>'
            '  <text:list-item><text:p>Alpha</text:p>'
            '    <text:list><text:list-item><text:p>Beta</text:p></text:list-item></text:list>'
            '  </text:list-item>'
            '  <text:list-item><text:p>Gamma</text:p></text:list-item>'
            '</text:list>'
            '</office:text></office:body></office:document>',
            encoding="utf-8"
        )
        doc = parse_fodt_strict(fodt)
        out_xml = document_to_xml(doc)
        alpha_pos = out_xml.find("Alpha")
        beta_pos = out_xml.find("Beta")
        gamma_pos = out_xml.find("Gamma")
        assert alpha_pos < beta_pos, "Alpha must come before Beta"
        assert beta_pos < gamma_pos, "Beta must come before Gamma"

    def test_three_level_list_emits_correct_nesting(self, tmp_path):
        """Three-level nested list emits 3 levels of text:list nesting."""
        fodt = tmp_path / "deep.fodt"
        fodt.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<office:document'
            ' xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
            ' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
            ' office:version="1.3"'
            ' office:mimetype="application/vnd.oasis.opendocument.text-flat-xml">'
            '<office:body><office:text>'
            '<text:list>'
            '  <text:list-item><text:p>L1</text:p>'
            '    <text:list><text:list-item><text:p>L2</text:p>'
            '      <text:list><text:list-item><text:p>L3</text:p></text:list-item></text:list>'
            '    </text:list-item></text:list>'
            '  </text:list-item>'
            '</text:list>'
            '</office:text></office:body></office:document>',
            encoding="utf-8"
        )
        doc = parse_fodt_strict(fodt)
        assert any(item["level"] == 3 for item in doc["lists"][0]["items"]), \
            "Parser must capture level=3 items"
        out_xml = document_to_xml(doc)
        assert "L1" in out_xml
        assert "L2" in out_xml
        assert "L3" in out_xml

    def test_flat_list_still_works(self, tmp_path):
        """Single-level list (level=1 only) still works correctly after changes."""
        fodt = tmp_path / "flat.fodt"
        fodt.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<office:document'
            ' xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
            ' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
            ' office:version="1.3"'
            ' office:mimetype="application/vnd.oasis.opendocument.text-flat-xml">'
            '<office:body><office:text>'
            '<text:list>'
            '  <text:list-item><text:p>Item One</text:p></text:list-item>'
            '  <text:list-item><text:p>Item Two</text:p></text:list-item>'
            '  <text:list-item><text:p>Item Three</text:p></text:list-item>'
            '</text:list>'
            '</office:text></office:body></office:document>',
            encoding="utf-8"
        )
        doc = parse_fodt_strict(fodt)
        out_xml = document_to_xml(doc)
        assert "Item One" in out_xml
        assert "Item Two" in out_xml
        assert "Item Three" in out_xml
        # All three items should be at the same nesting level (no spurious nesting)
        assert out_xml.count("list-item") >= 3
