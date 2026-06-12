"""
tests/python/fodp/test_r202_fodp_advanced_ops.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-SPRINT9-001
TASK-001: FODP advanced operations — load, get_page_count, extract_text,
get_page_metadata, fodp_total_text_length, fodp_slide_shape_counts.
"""
from __future__ import annotations

import sys
import os
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodp import (
    load, get_page_count, extract_text, get_page_metadata,
    fodp_total_text_length, fodp_slide_shape_counts,
    FodpError, FodpParseError,
)

# Minimal FODP XML with 2 slides
_FODP_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<office:document
  xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
  xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
  xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
  xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
  office:mimetype="application/vnd.oasis.opendocument.presentation-flat-xml">
  <office:body>
    <office:presentation>
      <draw:page draw:name="Slide1">
        <draw:frame presentation:class="title">
          <draw:text-box>
            <text:p>Hello World</text:p>
          </draw:text-box>
        </draw:frame>
        <draw:frame>
          <draw:text-box>
            <text:p>Body Text</text:p>
          </draw:text-box>
        </draw:frame>
      </draw:page>
      <draw:page draw:name="Slide2">
        <draw:frame>
          <draw:text-box>
            <text:p>Slide Two Content</text:p>
          </draw:text-box>
        </draw:frame>
      </draw:page>
    </office:presentation>
  </office:body>
</office:document>"""

_FODP_SINGLE_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<office:document
  xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
  xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
  xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
  xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
  office:mimetype="application/vnd.oasis.opendocument.presentation-flat-xml">
  <office:body>
    <office:presentation>
      <draw:page draw:name="OnlySlide">
        <draw:frame presentation:class="title">
          <draw:text-box>
            <text:p>Single Slide Title</text:p>
          </draw:text-box>
        </draw:frame>
      </draw:page>
    </office:presentation>
  </office:body>
</office:document>"""

_FODP_EMPTY_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<office:document
  xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
  xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
  xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
  xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
  office:mimetype="application/vnd.oasis.opendocument.presentation-flat-xml">
  <office:body>
    <office:presentation>
    </office:presentation>
  </office:body>
</office:document>"""


def _make_fodp_file(xml_bytes: bytes = _FODP_XML) -> str:
    fd, path = tempfile.mkstemp(suffix=".fodp")
    os.close(fd)
    Path(path).write_bytes(xml_bytes)
    return path


class TestFodpLoad:
    """load() model structure and field validation."""

    def test_load_bytes_returns_dict(self):
        model = load(_FODP_XML)
        assert isinstance(model, dict)

    def test_load_is_fodp_true(self):
        model = load(_FODP_XML)
        assert model["is_fodp"] is True

    def test_load_page_count_two(self):
        model = load(_FODP_XML)
        assert model["page_count"] == 2

    def test_load_pages_list(self):
        model = load(_FODP_XML)
        assert isinstance(model["pages"], list)
        assert len(model["pages"]) == 2

    def test_load_mime_type_fodp(self):
        model = load(_FODP_XML)
        assert "presentation-flat-xml" in model["mime_type"]

    def test_load_page_names(self):
        model = load(_FODP_XML)
        names = [p["name"] for p in model["pages"]]
        assert "Slide1" in names
        assert "Slide2" in names

    def test_load_title_extracted(self):
        model = load(_FODP_XML)
        slide1 = model["pages"][0]
        assert slide1["title"] == "Hello World"

    def test_load_text_content_slide1(self):
        model = load(_FODP_XML)
        slide1 = model["pages"][0]
        assert "Hello World" in slide1["text_content"]
        assert "Body Text" in slide1["text_content"]

    def test_load_shape_count_slide1(self):
        model = load(_FODP_XML)
        # Slide1 has 2 frames
        assert model["pages"][0]["shape_count"] == 2

    def test_load_file_path(self):
        path = _make_fodp_file()
        try:
            model = load(path)
            assert model["page_count"] == 2
        finally:
            os.unlink(path)

    def test_load_empty_presentation(self):
        model = load(_FODP_EMPTY_XML)
        assert model["page_count"] == 0
        assert model["pages"] == []

    def test_load_single_slide(self):
        model = load(_FODP_SINGLE_XML)
        assert model["page_count"] == 1
        assert model["pages"][0]["title"] == "Single Slide Title"

    def test_load_invalid_xml_raises(self):
        import pytest
        with pytest.raises(FodpParseError):
            load(b"<not valid xml><<>>")


class TestFodpGetPageCount:
    """get_page_count() taking source."""

    def test_get_page_count_two(self):
        assert get_page_count(_FODP_XML) == 2

    def test_get_page_count_single(self):
        assert get_page_count(_FODP_SINGLE_XML) == 1

    def test_get_page_count_empty(self):
        assert get_page_count(_FODP_EMPTY_XML) == 0

    def test_get_page_count_from_file(self):
        path = _make_fodp_file()
        try:
            assert get_page_count(path) == 2
        finally:
            os.unlink(path)


class TestFodpExtractText:
    """extract_text() returns flat list of non-empty strings."""

    def test_extract_text_returns_list(self):
        texts = extract_text(_FODP_XML)
        assert isinstance(texts, list)

    def test_extract_text_contains_hello(self):
        texts = extract_text(_FODP_XML)
        assert "Hello World" in texts

    def test_extract_text_contains_body(self):
        texts = extract_text(_FODP_XML)
        assert "Body Text" in texts

    def test_extract_text_slide2(self):
        texts = extract_text(_FODP_XML)
        assert "Slide Two Content" in texts

    def test_extract_text_total_count(self):
        texts = extract_text(_FODP_XML)
        assert len(texts) == 3  # Hello World, Body Text, Slide Two Content

    def test_extract_text_empty(self):
        texts = extract_text(_FODP_EMPTY_XML)
        assert texts == []

    def test_extract_text_from_file(self):
        path = _make_fodp_file()
        try:
            texts = extract_text(path)
            assert "Hello World" in texts
        finally:
            os.unlink(path)


class TestFodpGetPageMetadata:
    """get_page_metadata() returns per-slide dicts."""

    def test_get_page_metadata_list(self):
        meta = get_page_metadata(_FODP_XML)
        assert isinstance(meta, list)
        assert len(meta) == 2

    def test_get_page_metadata_keys(self):
        meta = get_page_metadata(_FODP_XML)
        slide = meta[0]
        assert "name" in slide
        assert "text_content" in slide
        assert "shape_count" in slide
        assert "title" in slide

    def test_get_page_metadata_slide1_name(self):
        meta = get_page_metadata(_FODP_XML)
        assert meta[0]["name"] == "Slide1"

    def test_get_page_metadata_slide2_name(self):
        meta = get_page_metadata(_FODP_XML)
        assert meta[1]["name"] == "Slide2"

    def test_get_page_metadata_empty(self):
        meta = get_page_metadata(_FODP_EMPTY_XML)
        assert meta == []


class TestFodpAnalytics:
    """fodp_total_text_length and fodp_slide_shape_counts."""

    def test_fodp_total_text_length_positive(self):
        length = fodp_total_text_length(_FODP_XML)
        assert isinstance(length, int)
        # "Hello World" + "Body Text" + "Slide Two Content" = 11+9+17=37
        assert length == 37

    def test_fodp_total_text_length_empty(self):
        assert fodp_total_text_length(_FODP_EMPTY_XML) == 0

    def test_fodp_total_text_length_from_file(self):
        path = _make_fodp_file()
        try:
            length = fodp_total_text_length(path)
            assert length > 0
        finally:
            os.unlink(path)

    def test_fodp_slide_shape_counts_list(self):
        counts = fodp_slide_shape_counts(_FODP_XML)
        assert isinstance(counts, list)
        assert len(counts) == 2

    def test_fodp_slide_shape_counts_values(self):
        counts = fodp_slide_shape_counts(_FODP_XML)
        # Slide1 has 2 frames, Slide2 has 1 frame
        assert counts[0] == 2
        assert counts[1] == 1

    def test_fodp_slide_shape_counts_empty(self):
        counts = fodp_slide_shape_counts(_FODP_EMPTY_XML)
        assert counts == []

    def test_fodp_slide_shape_counts_single(self):
        counts = fodp_slide_shape_counts(_FODP_SINGLE_XML)
        assert counts == [1]
