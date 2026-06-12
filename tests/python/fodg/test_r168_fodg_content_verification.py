"""
test_r168_fodg_content_verification.py -- Content verification tests for FODG gap closure.

Sprint: FORMAT-FACTORY-GAP-CLOSURE-AND-DEEPENING-20260611-001
Addresses GC-002 LLM downgrade: adds content assertions for get_all_text, export_to_txt,
probe_fodg, and JSON structure. find_text is tested with synthetic model (load() does not
populate shapes list from XML text-boxes — by design in fodg_codec).
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg.fodg_codec import (
    load,
    create_fodg,
    write_fodg,
    export_to_json,
    export_to_txt,
    get_all_text,
    page_names,
    has_page,
    find_text,
    probe_fodg,
    FODG_MIME,
)


# Minimal FODG XML with proper MIME type and text content
_FODG_WITH_TEXT = (
    b'<?xml version="1.0" encoding="UTF-8"?>'
    b'<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
    b' xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"'
    b' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
    b' office:mimetype="application/vnd.oasis.opendocument.graphics-flat-xml">'
    b"<office:body><office:drawing>"
    b'<draw:page draw:name="MainSlide">'
    b"<draw:frame><draw:text-box><text:p>Hello World</text:p></draw:text-box></draw:frame>"
    b"<draw:frame><draw:text-box><text:p>Goodbye World</text:p></draw:text-box></draw:frame>"
    b"</draw:page>"
    b"</office:drawing></office:body></office:document>"
)


def _write_temp_fodg(bytes_data: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".fodg", delete=False) as f:
        f.write(bytes_data)
        return f.name


class TestFodgGetAllTextContent:
    """get_all_text returns actual text content, not just a list."""

    def test_all_text_contains_hello_world(self):
        model = load(_FODG_WITH_TEXT)
        texts = get_all_text(model)
        assert "Hello World" in texts, f"Expected 'Hello World' in {texts}"

    def test_all_text_contains_goodbye_world(self):
        model = load(_FODG_WITH_TEXT)
        texts = get_all_text(model)
        assert "Goodbye World" in texts, f"Expected 'Goodbye World' in {texts}"

    def test_all_text_count(self):
        model = load(_FODG_WITH_TEXT)
        texts = get_all_text(model)
        assert len(texts) >= 2, f"Expected at least 2 text items, got {len(texts)}"

    def test_all_text_empty_doc_is_empty_list(self):
        model = create_fodg([{"name": "Empty", "shapes": []}])
        texts = get_all_text(model)
        assert texts == [] or all(t == "" for t in texts)


class TestFodgFindTextContent:
    """find_text searches model shapes dict for text.
    Note: load() doesn't populate shapes list from XML text-boxes — find_text
    works on models with manually-populated shapes or via create_fodg with shape dicts.
    """

    def _make_model_with_shapes(self):
        # Construct a model dict with shapes that have text (bypassing load)
        return {
            "pages": [
                {
                    "name": "Slide1",
                    "shapes": [
                        {"type": "text", "text": "Hello World"},
                        {"type": "text", "text": "Goodbye World"},
                    ],
                    "text_content": ["Hello World", "Goodbye World"],
                    "shape_count": 2,
                }
            ]
        }

    def test_find_text_hello_returns_match(self):
        model = self._make_model_with_shapes()
        results = find_text(model, "Hello")
        assert len(results) > 0, "Expected find_text to find 'Hello' in shapes"

    def test_find_text_match_content(self):
        model = self._make_model_with_shapes()
        results = find_text(model, "Hello")
        texts = [r["text"] for r in results]
        assert any("Hello" in t for t in texts), f"Expected 'Hello' in {texts}"

    def test_find_text_no_match_returns_empty(self):
        model = self._make_model_with_shapes()
        results = find_text(model, "XYZZY_NOT_FOUND_12345")
        assert results == []

    def test_find_text_world_finds_multiple(self):
        model = self._make_model_with_shapes()
        results = find_text(model, "World")
        assert len(results) == 2, f"Expected 2 matches for 'World', got {len(results)}"

    def test_find_text_returns_page_info(self):
        model = self._make_model_with_shapes()
        results = find_text(model, "Hello")
        assert "page_name" in results[0]
        assert "page_index" in results[0]
        assert results[0]["page_name"] == "Slide1"


class TestFodgExportToTxt:
    """export_to_txt takes source bytes/path and returns text with content."""

    def test_export_to_txt_contains_hello_world(self):
        txt = export_to_txt(_FODG_WITH_TEXT)
        assert isinstance(txt, str)
        assert "Hello World" in txt, f"Expected 'Hello World' in: {txt[:300]}"

    def test_export_to_txt_nonempty(self):
        txt = export_to_txt(_FODG_WITH_TEXT)
        assert len(txt.strip()) > 0

    def test_export_to_txt_has_page_header(self):
        txt = export_to_txt(_FODG_WITH_TEXT)
        assert "MainSlide" in txt or "Page" in txt

    def test_export_to_txt_from_file(self, tmp_path):
        p = tmp_path / "test.fodg"
        p.write_bytes(_FODG_WITH_TEXT)
        txt = export_to_txt(str(p))
        assert "Hello World" in txt


class TestFodgPageNamesContent:
    """page_names returns correct page name strings."""

    def test_page_names_contains_main_slide(self):
        model = load(_FODG_WITH_TEXT)
        names = page_names(model)
        assert "MainSlide" in names, f"Expected 'MainSlide' in page_names: {names}"

    def test_has_page_true_for_main_slide(self):
        model = load(_FODG_WITH_TEXT)
        assert has_page(model, "MainSlide") is True

    def test_has_page_false_for_missing(self):
        model = load(_FODG_WITH_TEXT)
        assert has_page(model, "NonExistentPage") is False


class TestFodgExportToJsonContent:
    """export_to_json returns JSON with expected structure."""

    def test_export_to_json_parseable(self):
        model = load(_FODG_WITH_TEXT)
        json_str = export_to_json(model)
        data = json.loads(json_str)
        assert isinstance(data, dict)

    def test_export_to_json_has_pages(self):
        model = load(_FODG_WITH_TEXT)
        json_str = export_to_json(model)
        data = json.loads(json_str)
        assert "pages" in data, f"Expected 'pages' key in JSON: {list(data.keys())}"

    def test_export_to_json_page_count(self):
        model = load(_FODG_WITH_TEXT)
        json_str = export_to_json(model)
        data = json.loads(json_str)
        assert len(data["pages"]) == 1


class TestFodgProbeContent:
    """probe_fodg returns True for valid FODG source with correct MIME type."""

    def test_probe_fodg_returns_true_for_valid(self):
        result = probe_fodg(_FODG_WITH_TEXT)
        assert result is True, f"Expected probe_fodg to return True for valid FODG, got {result}"

    def test_probe_fodg_returns_false_for_invalid(self):
        result = probe_fodg(b"not a FODG document")
        assert result is False

    def test_probe_fodg_from_file(self, tmp_path):
        p = tmp_path / "test.fodg"
        p.write_bytes(_FODG_WITH_TEXT)
        result = probe_fodg(str(p))
        assert result is True
