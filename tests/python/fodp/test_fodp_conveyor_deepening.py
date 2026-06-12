"""
test_fodp_conveyor_deepening.py -- FODP product deepening tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-1
Tests load, get_page_count, extract_text, get_page_metadata for FODP codec.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodp.fodp_codec import (
    load,
    get_page_count,
    extract_text,
    get_page_metadata,
    FODP_MIME,
    FodpParseError,
)

# Minimal valid FODP XML
_MINIMAL_FODP = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
    ' xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"'
    ' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
    ' xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"'
    ' xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"'
    f' office:mimetype="{FODP_MIME}">'
    '<office:body><office:presentation>'
    '<draw:page draw:name="Slide1">'
    '<draw:frame presentation:class="title">'
    '<draw:text-box><text:p>Hello World</text:p></draw:text-box>'
    '</draw:frame>'
    '<draw:frame presentation:class="subtitle">'
    '<draw:text-box><text:p>Subtitle text</text:p></draw:text-box>'
    '</draw:frame>'
    '</draw:page>'
    '<draw:page draw:name="Slide2">'
    '<draw:frame>'
    '<draw:text-box><text:p>Second slide content</text:p></draw:text-box>'
    '</draw:frame>'
    '</draw:page>'
    '</office:presentation></office:body>'
    '</office:document>'
)

_EMPTY_FODP = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
    ' xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"'
    ' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
    ' xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"'
    ' xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"'
    f' office:mimetype="{FODP_MIME}">'
    '<office:body><office:presentation>'
    '</office:presentation></office:body>'
    '</office:document>'
)


def test_load_from_bytes():
    model = load(_MINIMAL_FODP.encode("utf-8"))
    assert model["is_fodp"] is True
    assert model["mime_type"] == FODP_MIME


def test_load_page_count():
    model = load(_MINIMAL_FODP.encode("utf-8"))
    assert model["page_count"] == 2


def test_get_page_count_function():
    count = get_page_count(_MINIMAL_FODP.encode("utf-8"))
    assert count == 2


def test_extract_text_all_slides():
    texts = extract_text(_MINIMAL_FODP.encode("utf-8"))
    assert "Hello World" in texts
    assert "Subtitle text" in texts
    assert "Second slide content" in texts


def test_get_page_metadata_slide_names():
    pages = get_page_metadata(_MINIMAL_FODP.encode("utf-8"))
    assert len(pages) == 2
    assert pages[0]["name"] == "Slide1"
    assert pages[1]["name"] == "Slide2"


def test_page_title_extraction():
    pages = get_page_metadata(_MINIMAL_FODP.encode("utf-8"))
    assert pages[0]["title"] == "Hello World"


def test_page_shape_count():
    pages = get_page_metadata(_MINIMAL_FODP.encode("utf-8"))
    assert pages[0]["shape_count"] == 2  # title + subtitle frames
    assert pages[1]["shape_count"] == 1


def test_empty_presentation():
    model = load(_EMPTY_FODP.encode("utf-8"))
    assert model["page_count"] == 0
    assert model["pages"] == []


def test_load_from_xml_string():
    model = load(_MINIMAL_FODP)
    assert model["is_fodp"] is True


def test_styles_count():
    model = load(_MINIMAL_FODP.encode("utf-8"))
    assert model["styles_count"] == 0  # minimal doc has no styles


def test_load_invalid_xml_raises():
    import pytest
    with pytest.raises(FodpParseError):
        load(b"<not valid xml")


def test_load_wrong_root_raises():
    import pytest
    with pytest.raises(FodpParseError):
        load(b"<root/>")


def test_load_from_file(tmp_path):
    fp = tmp_path / "test.fodp"
    fp.write_text(_MINIMAL_FODP, encoding="utf-8")
    model = load(fp)
    assert model["is_fodp"] is True
    assert model["page_count"] == 2
