"""
test_r165_abw_get_metadata.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT29-001
Added: 2026-06-10

Tests for ABW get_metadata function.
Authority: P1 (ABW format track)
"""
from __future__ import annotations

import sys
from pathlib import Path


_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import get_metadata, create_abw, write_abw


def _abw_with_metadata(meta_elements: str) -> bytes:
    """Build a minimal ABW XML with metadata block."""
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<abiword version="1.0">'
        f'<metadata>{meta_elements}</metadata>'
        '<section><p>Hello</p></section>'
        '</abiword>'
    ).encode("utf-8")


def _abw_no_metadata() -> bytes:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<abiword version="1.0">'
        '<section><p>Hello</p></section>'
        '</abiword>'
    ).encode("utf-8")


class TestGetMetadata:

    def test_no_metadata_block(self):
        result = get_metadata(_abw_no_metadata())
        assert result == {}

    def test_single_meta_key(self):
        xml = _abw_with_metadata(
            '<m key="dc.title" value="My Document"/>'
        )
        result = get_metadata(xml)
        assert result["dc.title"] == "My Document"

    def test_multiple_meta_keys(self):
        xml = _abw_with_metadata(
            '<m key="dc.title" value="Title"/>'
            '<m key="dc.creator" value="Alice"/>'
        )
        result = get_metadata(xml)
        assert result["dc.title"] == "Title"
        assert result["dc.creator"] == "Alice"

    def test_empty_metadata_block(self):
        xml = _abw_with_metadata("")
        result = get_metadata(xml)
        assert result == {}

    def test_created_abw_has_no_metadata(self, tmp_path):
        doc = create_abw(["paragraph one", "paragraph two"])
        p = tmp_path / "created.abw"
        write_abw(doc, p)
        result = get_metadata(p)
        assert result == {}

    def test_from_file(self, tmp_path):
        xml = _abw_with_metadata(
            '<m key="dc.description" value="A test file"/>'
        )
        p = tmp_path / "test.abw"
        p.write_bytes(xml)
        result = get_metadata(p)
        assert result["dc.description"] == "A test file"

    def test_meta_with_text_content(self):
        xml = _abw_with_metadata(
            '<m key="abiword.generator">AbiWord</m>'
        )
        result = get_metadata(xml)
        assert result["abiword.generator"] == "AbiWord"

    def test_returns_dict(self):
        result = get_metadata(_abw_no_metadata())
        assert isinstance(result, dict)
