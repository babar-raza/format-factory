"""Comprehensive gap-coverage tests for the FODP package public API.

Covers the ~58 `missing_test_coverage` gap-ledger entries for FODP
(reports/capability-layer/gap-ledger.json, format=FODP) by exercising every
name exported from ``fodp`` (see src/python/fodp/__init__.py __all__), plus a
handful of additional analytics helpers that are importable from the package
namespace via the ``from .module import *`` re-exports in __init__.py even
though they are not listed in __all__.

Fixtures used:
    - The three corpus samples in samples/by-format/fodp/ (minimal-presentation,
      two-slides-basic, title-only) for baseline / real-file coverage.
    - Two synthetic inline XML fixtures (XML_RICH, XML_FULL_META) that exercise
      code paths the corpus samples never touch: embedded images, presentation
      notes, multiple master pages, a slide with zero shapes, and a fully
      populated <office:meta> block.

Known-bug documentation:
    A handful of analytics functions in presentation_document.py /
    fodp_slide_analytics.py call ``dict.get("title", "")`` on a page dict that
    always has an explicit ``"title": None`` key. Because the key is *present*,
    ``dict.get`` returns the stored ``None`` rather than falling back to the
    default ``""``, so any downstream ``.strip()``/``.split()``/``len()`` call on
    an untitled slide raises. This module documents that behavior explicitly
    (see TestKnownTitleNoneBugs) rather than silently avoiding it, so the tests
    stay green today and turn into regression tests if the bug is ever fixed.

    Separately, fodp_max_text_length / fodp_text_length_variance /
    fodp_slide_text_lengths read ``doc.get("slides", [])`` but the neutral model
    dict never has a "slides" key (only "pages"), so these three functions
    always return their empty-input default (0 / 0.0 / []) regardless of input.
    This is documented in TestMaxTextLengthFamilyAlwaysDefault.

IMPORTANT: write_fodp no longer exists. It was a quarantined NotImplementedError
sentinel, removed by TC-PA-012 (2026-07-17); FODP is read-only at this parser
level. This file does not import or reference it — see test_fodp_write_stub.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import fodp  # noqa: E402
from fodp import exceptions as fodp_exceptions  # noqa: E402

SAMPLES_DIR = _REPO / "samples" / "by-format" / "fodp"
MINIMAL = SAMPLES_DIR / "minimal-presentation.fodp"   # 1 slide, title "Hello"
TWO = SAMPLES_DIR / "two-slides-basic.fodp"           # 2 slides, both titled
TITLE_ONLY = SAMPLES_DIR / "title-only.fodp"          # 0 slides, no <office:meta>

SOURCES = {"MINIMAL": MINIMAL, "TWO": TWO, "TITLE_ONLY": TITLE_ONLY}


# ---------------------------------------------------------------------------
# Synthetic fixtures — cover images / notes / master pages / rich metadata
# ---------------------------------------------------------------------------

XML_RICH = """<?xml version="1.0" encoding="UTF-8"?>
<office:document
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    office:mimetype="application/vnd.oasis.opendocument.presentation-flat-xml"
    office:version="1.3">
  <office:body>
    <office:presentation>
      <draw:page draw:name="Slide1" draw:style-name="s1" draw:master-page-name="Default">
        <draw:frame draw:name="title1" presentation:class="title">
          <draw:text-box><text:p>Slide One</text:p></draw:text-box>
        </draw:frame>
        <draw:frame draw:name="gfx1" presentation:class="graphic">
          <draw:image xlink:href="Pictures/a.png"/>
          <draw:image xlink:href="Pictures/b.png"/>
        </draw:frame>
        <presentation:notes>
          <text:p>Note one text</text:p>
        </presentation:notes>
      </draw:page>
      <draw:page draw:name="Slide2" draw:style-name="s1" draw:master-page-name="Default">
        <draw:frame draw:name="title2" presentation:class="title">
          <draw:text-box><text:p>Slide Two</text:p></draw:text-box>
        </draw:frame>
        <presentation:notes>
          <text:p>Note two</text:p>
        </presentation:notes>
      </draw:page>
      <draw:page draw:name="Slide3" draw:style-name="s1" draw:master-page-name="Alt">
      </draw:page>
    </office:presentation>
  </office:body>
</office:document>"""
# Slide1: title "Slide One", 1 title-frame + 1 graphic-frame (2 images) = 2 shapes,
#         notes "Note one text" (13 chars)
# Slide2: title "Slide Two", 1 shape, notes "Note two" (8 chars)
# Slide3: no title (title=None), 0 shapes, no notes -> "" ; master page "Alt"

XML_FULL_META = """<?xml version="1.0" encoding="UTF-8"?>
<office:document
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
    office:mimetype="application/vnd.oasis.opendocument.presentation-flat-xml"
    office:version="1.3">
  <office:meta>
    <dc:title>Sample Deck</dc:title>
    <dc:creator>Alice</dc:creator>
    <dc:description>A test deck</dc:description>
    <dc:subject>Testing</dc:subject>
    <dc:date>2026-01-01</dc:date>
    <dc:language>en-US</dc:language>
    <meta:creation-date>2025-12-01T00:00:00</meta:creation-date>
    <meta:generator>FormatFactory/1.0</meta:generator>
    <meta:editing-cycles>3</meta:editing-cycles>
    <meta:editing-duration>PT10M</meta:editing-duration>
    <meta:initial-creator>Bob</meta:initial-creator>
  </office:meta>
  <office:body>
    <office:presentation>
      <style:style style:name="s1"/>
      <style:style style:name="s2"/>
      <draw:page draw:name="MetaSlide" draw:style-name="s1">
        <draw:frame draw:name="title1" presentation:class="title">
          <draw:text-box><text:p>Meta Slide</text:p></draw:text-box>
        </draw:frame>
      </draw:page>
    </office:presentation>
  </office:body>
</office:document>"""

XML_WRONG_MIME = """<?xml version="1.0" encoding="UTF-8"?>
<office:document
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
    office:mimetype="application/vnd.oasis.opendocument.text-flat-xml"
    office:version="1.3">
  <office:body>
    <office:presentation>
      <draw:page draw:name="Slide1" draw:style-name=""/>
    </office:presentation>
  </office:body>
</office:document>"""


# ---------------------------------------------------------------------------
# Part 1 — package export surface sanity
# ---------------------------------------------------------------------------

class TestPackageExports:
    def test_all_names_are_importable_attributes(self):
        for name in fodp.__all__:
            assert hasattr(fodp, name), f"{name} listed in __all__ but not an attribute of fodp"

    def test_write_fodp_absent_from_all(self):
        # TC-PA-012 removal (was: QF-1-004 quarantine) — the sentinel no longer
        # exists at all. This module intentionally never imports write_fodp.
        assert "write_fodp" not in fodp.__all__

    def test_fodp_document_in_all(self):
        assert "FodpDocument" in fodp.__all__
        assert fodp.FodpDocument is not None

    def test_analytics_functions_present_in_all(self):
        # Spot-check a representative slice of the analytics __all__ entries.
        for name in (
            "fodp_slide_count", "fodp_has_titles", "fodp_total_shape_count",
            "fodp_image_count", "fodp_notes_text", "fodp_master_page_count",
        ):
            assert name in fodp.__all__


# ---------------------------------------------------------------------------
# Part 2 — codec core: load / get_page_count / extract_text / get_page_metadata
# ---------------------------------------------------------------------------

class TestLoad:
    def test_load_minimal(self):
        model = fodp.load(MINIMAL)
        assert model["is_fodp"] is True
        assert model["page_count"] == 1

    def test_load_two_slides(self):
        model = fodp.load(TWO)
        assert model["page_count"] == 2

    def test_load_empty(self):
        model = fodp.load(TITLE_ONLY)
        assert model["page_count"] == 0
        assert model["pages"] == []

    def test_load_accepts_xml_string(self):
        model = fodp.load(XML_RICH)
        assert model["page_count"] == 3

    def test_load_accepts_bytes(self):
        data = MINIMAL.read_bytes()
        model = fodp.load(data)
        assert model["is_fodp"] is True

    def test_load_wrong_mimetype_sets_is_fodp_false(self):
        model = fodp.load(XML_WRONG_MIME)
        assert model["is_fodp"] is False
        assert model["page_count"] == 1

    def test_load_missing_file_raises_parse_error(self):
        with pytest.raises(fodp.FodpParseError):
            fodp.load(_REPO / "does" / "not" / "exist.fodp")

    def test_load_invalid_xml_raises_parse_error(self):
        with pytest.raises(fodp.FodpParseError):
            fodp.load(b"<not valid xml <<<")

    def test_load_wrong_root_raises_parse_error(self):
        with pytest.raises(fodp.FodpParseError):
            fodp.load(b"<?xml version='1.0'?><root/>")


class TestGetPageCount:
    def test_minimal(self):
        assert fodp.get_page_count(MINIMAL) == 1

    def test_two(self):
        assert fodp.get_page_count(TWO) == 2

    def test_empty(self):
        assert fodp.get_page_count(TITLE_ONLY) == 0

    def test_rich(self):
        assert fodp.get_page_count(XML_RICH) == 3


class TestExtractText:
    def test_minimal_contains_hello(self):
        texts = fodp.extract_text(MINIMAL)
        assert any("Hello" in t for t in texts)

    def test_two_returns_all_slide_texts(self):
        texts = fodp.extract_text(TWO)
        assert len(texts) == 3

    def test_empty_returns_empty_list(self):
        assert fodp.extract_text(TITLE_ONLY) == []

    def test_returns_list_of_str(self):
        texts = fodp.extract_text(TWO)
        assert isinstance(texts, list)
        assert all(isinstance(t, str) for t in texts)


class TestGetPageMetadata:
    def test_minimal_structure(self):
        pages = fodp.get_page_metadata(MINIMAL)
        assert len(pages) == 1
        page = pages[0]
        for key in ("name", "style", "master_page", "title", "text_content", "shape_count"):
            assert key in page

    def test_two_titles(self):
        pages = fodp.get_page_metadata(TWO)
        assert pages[0]["title"] == "Introduction"
        assert pages[1]["title"] == "Conclusion"

    def test_empty(self):
        assert fodp.get_page_metadata(TITLE_ONLY) == []

    def test_rich_master_pages(self):
        pages = fodp.get_page_metadata(XML_RICH)
        assert [p["master_page"] for p in pages] == ["Default", "Default", "Alt"]

    def test_rich_untitled_slide_has_none_title(self):
        pages = fodp.get_page_metadata(XML_RICH)
        assert pages[2]["title"] is None


# ---------------------------------------------------------------------------
# Part 3 — exceptions (fodp_codec.FodpError/FodpParseError, exported)
# ---------------------------------------------------------------------------

class TestExceptions:
    def test_fodp_error_is_exception(self):
        assert issubclass(fodp.FodpError, Exception)

    def test_fodp_parse_error_is_fodp_error(self):
        assert issubclass(fodp.FodpParseError, fodp.FodpError)

    def test_fodp_parse_error_raised_on_bad_xml(self):
        with pytest.raises(fodp.FodpError):
            fodp.load(b"<<<not xml")

    def test_fodp_error_message_preserved(self):
        try:
            fodp.load(b"<<<not xml")
        except fodp.FodpParseError as exc:
            assert "XML parse error" in str(exc)
        else:
            pytest.fail("expected FodpParseError")

    def test_exceptions_module_fodp_error_unified_with_codec(self):
        """Healed: fodp_codec.py imports FodpError from exceptions.py rather
        than redefining it -- both now resolve to the same class. See
        plans/.claude/quizzical-munching-gadget.md section 7."""
        assert fodp.FodpError is fodp_exceptions.FodpError
        assert fodp.FodpError.__module__ == "fodp.exceptions"

    def test_exceptions_module_parse_error_subclass(self):
        assert issubclass(fodp_exceptions.FodpParseError, fodp_exceptions.FodpError)

    def test_exceptions_module_write_error_subclass(self):
        assert issubclass(fodp_exceptions.FodpWriteError, fodp_exceptions.FodpError)
        err = fodp_exceptions.FodpWriteError("cannot write")
        assert isinstance(err, Exception)
        assert str(err) == "cannot write"


# ---------------------------------------------------------------------------
# Part 4 — get_document_metadata
# ---------------------------------------------------------------------------

class TestGetDocumentMetadata:
    def test_full_metadata_fields(self):
        meta = fodp.get_document_metadata(XML_FULL_META)
        assert meta == {
            "title": "Sample Deck",
            "description": "A test deck",
            "subject": "Testing",
            "creator": "Alice",
            "date": "2026-01-01",
            "language": "en-US",
            "creation_date": "2025-12-01T00:00:00",
            "generator": "FormatFactory/1.0",
            "editing_cycles": "3",
            "editing_duration": "PT10M",
            "initial_creator": "Bob",
        }

    def test_missing_meta_element_all_none(self):
        meta = fodp.get_document_metadata(TITLE_ONLY)
        assert set(meta.keys()) == {
            "title", "description", "subject", "creator", "date", "language",
            "creation_date", "generator", "editing_cycles", "editing_duration",
            "initial_creator",
        }
        assert all(v is None for v in meta.values())

    def test_minimal_has_no_meta_block(self):
        # minimal-presentation.fodp has no <office:meta> element at all.
        meta = fodp.get_document_metadata(MINIMAL)
        assert meta["title"] is None

    def test_wrong_root_raises(self):
        with pytest.raises(fodp.FodpParseError):
            fodp.get_document_metadata(b"<?xml version='1.0'?><root/>")

    def test_spec_qname_attribute(self):
        assert fodp.get_document_metadata.spec_qname == "office:meta"


# ---------------------------------------------------------------------------
# Part 5 — export_to_txt / export_to_csv / export_to_json
# ---------------------------------------------------------------------------

class TestExportToTxt:
    def test_minimal(self):
        assert fodp.export_to_txt(MINIMAL) == "Hello"

    def test_two_joins_with_newline(self):
        text = fodp.export_to_txt(TWO)
        assert text == "Introduction\nFirst slide content.\nConclusion"

    def test_empty_returns_empty_string(self):
        assert fodp.export_to_txt(TITLE_ONLY) == ""

    def test_returns_str(self):
        assert isinstance(fodp.export_to_txt(TWO), str)


class TestExportToCsv:
    def test_minimal_has_header_and_row(self):
        csv_text = fodp.export_to_csv(MINIMAL)
        lines = csv_text.strip().splitlines()
        assert lines[0] == "slide_index,slide_name,shape_count,text_snippet"
        assert lines[1] == "0,Slide1,1,Hello"

    def test_two_has_two_data_rows(self):
        csv_text = fodp.export_to_csv(TWO)
        lines = csv_text.strip().splitlines()
        assert len(lines) == 3  # header + 2 slides

    def test_empty_has_header_only(self):
        csv_text = fodp.export_to_csv(TITLE_ONLY)
        lines = csv_text.strip().splitlines()
        assert lines == ["slide_index,slide_name,shape_count,text_snippet"]

    def test_snippet_truncated_to_80_chars(self):
        long_text = "x" * 200
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
    office:mimetype="application/vnd.oasis.opendocument.presentation-flat-xml"
    office:version="1.3">
  <office:body>
    <office:presentation>
      <draw:page draw:name="Slide1" draw:style-name="">
        <draw:frame draw:name="b" presentation:class="body">
          <draw:text-box><text:p>{long_text}</text:p></draw:text-box>
        </draw:frame>
      </draw:page>
    </office:presentation>
  </office:body>
</office:document>"""
        csv_text = fodp.export_to_csv(xml)
        data_line = csv_text.strip().splitlines()[1]
        snippet = data_line.split(",", 3)[3]
        assert len(snippet) == 80


class TestExportToJson:
    def test_returns_valid_json(self):
        import json
        raw = fodp.export_to_json(MINIMAL)
        parsed = json.loads(raw)
        assert parsed["page_count"] == 1
        assert parsed["is_fodp"] is True

    def test_two_json_roundtrip(self):
        import json
        raw = fodp.export_to_json(TWO)
        parsed = json.loads(raw)
        assert parsed["page_count"] == 2
        assert len(parsed["pages"]) == 2

    def test_empty_json(self):
        import json
        raw = fodp.export_to_json(TITLE_ONLY)
        parsed = json.loads(raw)
        assert parsed["page_count"] == 0

    def test_returns_str(self):
        assert isinstance(fodp.export_to_json(MINIMAL), str)


# ---------------------------------------------------------------------------
# Part 6 — fodp_installed_workflow
# ---------------------------------------------------------------------------

class TestInstalledWorkflow:
    def test_minimal(self):
        result = fodp.fodp_installed_workflow(MINIMAL)
        assert result == {
            "format": "fodp",
            "loaded": True,
            "page_count": 1,
            "slide_count": 1,
        }

    def test_two_slides(self):
        result = fodp.fodp_installed_workflow(TWO)
        assert result["page_count"] == 2
        assert result["slide_count"] == 2

    def test_empty(self):
        result = fodp.fodp_installed_workflow(TITLE_ONLY)
        assert result["page_count"] == 0
        assert result["loaded"] is True

    def test_accepts_string_path(self):
        result = fodp.fodp_installed_workflow(str(MINIMAL))
        assert result["format"] == "fodp"

    def test_rich_via_tmp_file(self, tmp_path):
        p = tmp_path / "rich.fodp"
        p.write_text(XML_RICH, encoding="utf-8")
        result = fodp.fodp_installed_workflow(p)
        assert result["page_count"] == 3
        assert result["slide_count"] == 3


# ---------------------------------------------------------------------------
# Part 7 — fodp_iter_slides / Page
# ---------------------------------------------------------------------------

class TestIterSlides:
    def test_minimal_yields_one_page(self):
        pages = list(fodp.fodp_iter_slides(MINIMAL))
        assert len(pages) == 1
        assert pages[0].name == "Slide1"
        assert pages[0].shape_count == 1

    def test_two_yields_two_pages_in_order(self):
        pages = list(fodp.fodp_iter_slides(TWO))
        assert [p.name for p in pages] == ["Slide1", "Slide2"]
        assert [p.shape_count for p in pages] == [2, 1]

    def test_empty_yields_nothing(self):
        pages = list(fodp.fodp_iter_slides(TITLE_ONLY))
        assert pages == []

    def test_is_iterator(self):
        result = fodp.fodp_iter_slides(MINIMAL)
        assert hasattr(result, "__next__") or hasattr(result, "__iter__")

    def test_page_to_dict(self):
        pages = list(fodp.fodp_iter_slides(TWO))
        d = pages[0].to_dict()
        assert d["name"] == "Slide1"
        assert d["title"] == "Introduction"
        assert d["shape_count"] == 2

    def test_page_repr(self):
        pages = list(fodp.fodp_iter_slides(MINIMAL))
        assert repr(pages[0]) == "Page(name='Slide1', shape_count=1)"

    def test_page_shapes_property_default_empty(self):
        pages = list(fodp.fodp_iter_slides(MINIMAL))
        # Page dict from the neutral model has no "shapes" key; property defaults to [].
        assert pages[0].shapes == []

    def test_page_layout_defaults_empty_string(self):
        pages = list(fodp.fodp_iter_slides(MINIMAL))
        # Page dict from the neutral model has no "layout" key; property defaults to "".
        assert pages[0].layout == ""

    def test_page_spec_metadata(self):
        pages = list(fodp.fodp_iter_slides(MINIMAL))
        page = pages[0]
        assert page.spec_qname == "presentation:page"
        assert page.spec_fact_ref == "SAL-FODP-00414"
        assert page.local_name == "page"
        assert page.facade_names == ["FodpPage"]

    def test_rich_via_tmp_file_zero_shape_slide(self, tmp_path):
        p = tmp_path / "rich.fodp"
        p.write_text(XML_RICH, encoding="utf-8")
        pages = list(fodp.fodp_iter_slides(p))
        assert len(pages) == 3
        assert pages[2].name == "Slide3"
        assert pages[2].shape_count == 0
        assert pages[2].to_dict()["title"] is None


# ---------------------------------------------------------------------------
# Part 8 — FodpDocument domain model
# ---------------------------------------------------------------------------

class TestFodpDocument:
    def test_from_file_minimal(self):
        doc = fodp.FodpDocument.from_file(MINIMAL)
        assert doc.page_count == 1
        assert doc.is_fodp is True

    def test_from_file_accepts_string_path(self):
        doc = fodp.FodpDocument.from_file(str(MINIMAL))
        assert doc.page_count == 1

    def test_direct_construction_from_dict(self):
        model = fodp.load(TWO)
        doc = fodp.FodpDocument(model)
        assert doc.page_count == 2

    def test_page_count_and_styles_count(self):
        doc = fodp.FodpDocument.from_file(TWO)
        assert doc.page_count == 2
        assert doc.styles_count == 0

    def test_pages_property_returns_list_of_dicts(self):
        doc = fodp.FodpDocument.from_file(TWO)
        pages = doc.pages
        assert isinstance(pages, list)
        assert len(pages) == 2
        assert pages[0]["title"] == "Introduction"

    def test_is_empty_true_for_zero_slides(self):
        doc = fodp.FodpDocument.from_file(TITLE_ONLY)
        assert doc.is_empty is True
        assert doc.is_single_page is False
        assert doc.is_multi_page is False

    def test_is_single_page_true_for_one_slide(self):
        doc = fodp.FodpDocument.from_file(MINIMAL)
        assert doc.is_empty is False
        assert doc.is_single_page is True
        assert doc.is_multi_page is False

    def test_is_multi_page_true_for_two_slides(self):
        doc = fodp.FodpDocument.from_file(TWO)
        assert doc.is_empty is False
        assert doc.is_single_page is False
        assert doc.is_multi_page is True

    def test_has_styles_false_when_no_styles(self):
        doc = fodp.FodpDocument.from_file(TWO)
        assert doc.has_styles is False

    def test_has_styles_true_when_styles_present(self):
        doc = fodp.FodpDocument(fodp.load(XML_FULL_META))
        assert doc.styles_count == 2
        assert doc.has_styles is True

    def test_total_shape_count_and_avg(self):
        doc = fodp.FodpDocument.from_file(TWO)
        assert doc.total_shape_count == 3
        assert doc.avg_shapes_per_slide == pytest.approx(1.5)

    def test_avg_shapes_per_slide_zero_for_empty(self):
        doc = fodp.FodpDocument.from_file(TITLE_ONLY)
        assert doc.avg_shapes_per_slide == 0.0

    def test_has_shapes(self):
        assert fodp.FodpDocument.from_file(TWO).has_shapes is True
        assert fodp.FodpDocument.from_file(TITLE_ONLY).has_shapes is False

    def test_is_shape_heavy_false_for_small_decks(self):
        assert fodp.FodpDocument.from_file(TWO).is_shape_heavy is False
        assert fodp.FodpDocument.from_file(MINIMAL).is_shape_heavy is False

    def test_is_single_slide_with_shapes(self):
        assert fodp.FodpDocument.from_file(MINIMAL).is_single_slide_with_shapes is True
        assert fodp.FodpDocument.from_file(TWO).is_single_slide_with_shapes is False
        assert fodp.FodpDocument.from_file(TITLE_ONLY).is_single_slide_with_shapes is False

    def test_is_large_false_for_small_decks(self):
        assert fodp.FodpDocument.from_file(TWO).is_large is False

    def test_has_titles(self):
        assert fodp.FodpDocument.from_file(TWO).has_titles is True
        assert fodp.FodpDocument.from_file(TITLE_ONLY).has_titles is False

    def test_max_and_min_shapes_on_slide(self):
        doc = fodp.FodpDocument.from_file(TWO)
        assert doc.max_shapes_on_slide == 2
        assert doc.min_shapes_on_slide == 1

    def test_max_and_min_shapes_on_slide_empty(self):
        doc = fodp.FodpDocument.from_file(TITLE_ONLY)
        assert doc.max_shapes_on_slide == 0
        assert doc.min_shapes_on_slide == 0

    def test_slide_shape_range(self):
        doc = fodp.FodpDocument.from_file(TWO)
        assert doc.slide_shape_range == 1
        assert fodp.FodpDocument.from_file(TITLE_ONLY).slide_shape_range == 0

    def test_has_uniform_slides(self):
        assert fodp.FodpDocument.from_file(TWO).has_uniform_slides is False
        # Vacuously uniform when there are no slides.
        assert fodp.FodpDocument.from_file(TITLE_ONLY).has_uniform_slides is True

    def test_rich_document_properties(self):
        doc = fodp.FodpDocument(fodp.load(XML_RICH))
        assert doc.page_count == 3
        assert doc.total_shape_count == 3
        assert doc.max_shapes_on_slide == 2
        assert doc.min_shapes_on_slide == 0
        assert doc.slide_shape_range == 2
        assert doc.has_uniform_slides is False
        assert doc.is_shape_heavy is False
        assert doc.is_large is False

    def test_to_dict(self):
        doc = fodp.FodpDocument.from_file(TWO)
        assert doc.to_dict() == {
            "is_fodp": True,
            "page_count": 2,
            "styles_count": 0,
        }

    def test_repr(self):
        doc = fodp.FodpDocument.from_file(TWO)
        assert repr(doc) == "FodpDocument(page_count=2, styles_count=0)"

    def test_class_spec_metadata(self):
        assert fodp.FodpDocument.spec_qname == "office:document"
        assert fodp.FodpDocument.spec_fact_ref == "SAL-FODP-00001"
        assert fodp.FodpDocument.local_name == "document"
        assert fodp.FodpDocument.facade_names == []


# ---------------------------------------------------------------------------
# Part 9 — data-driven analytics coverage across the 3 corpus samples
#
# This block exercises every analytics function reachable as `fodp.<name>`
# (the full __all__ analytics surface plus the extra names re-exported from
# fodp_slide_analytics.py / presentation_document.py via `import *`) against
# all three corpus samples. Expected values were captured empirically from
# the live functions and are asserted verbatim below, so any regression in
# the underlying computation will be caught.
# ---------------------------------------------------------------------------

FUNC_VALUES = {
    'fodp_all_slides_have_text': {'MINIMAL': True, 'TWO': True, 'TITLE_ONLY': False},
    'fodp_average_shapes_per_slide': {'MINIMAL': 1.0, 'TWO': 1.5, 'TITLE_ONLY': 0.0},
    'fodp_average_text_per_slide': {'MINIMAL': 5.0, 'TWO': 21.5, 'TITLE_ONLY': 0.0},
    'fodp_avg_notes_length': {'MINIMAL': 0.0, 'TWO': 0.0, 'TITLE_ONLY': 0.0},
    'fodp_avg_sentence_length': {'MINIMAL': 5.0, 'TWO': 21.0, 'TITLE_ONLY': 0.0},
    'fodp_avg_shapes_per_slide': {'MINIMAL': 1.0, 'TWO': 1.5, 'TITLE_ONLY': 0.0},
    'fodp_avg_text_length': {'MINIMAL': 5.0, 'TWO': 21.0, 'TITLE_ONLY': 0.0},
    'fodp_avg_title_length': {'MINIMAL': 5.0, 'TWO': 11.0, 'TITLE_ONLY': 0.0},
    'fodp_empty_slide_count': {'MINIMAL': 0, 'TWO': 0, 'TITLE_ONLY': 0},
    'fodp_has_empty_slides': {'MINIMAL': False, 'TWO': False, 'TITLE_ONLY': False},
    'fodp_has_images': {'MINIMAL': False, 'TWO': False, 'TITLE_ONLY': False},
    'fodp_has_multi_slide': {'MINIMAL': False, 'TWO': True, 'TITLE_ONLY': False},
    'fodp_has_notes': {'MINIMAL': False, 'TWO': False, 'TITLE_ONLY': False},
    'fodp_has_numeric_content': {'MINIMAL': False, 'TWO': False, 'TITLE_ONLY': False},
    'fodp_has_titles': {'MINIMAL': True, 'TWO': True, 'TITLE_ONLY': False},
    'fodp_has_zero_shapes': {'MINIMAL': False, 'TWO': False, 'TITLE_ONLY': True},
    'fodp_image_count': {'MINIMAL': 0, 'TWO': 0, 'TITLE_ONLY': 0},
    'fodp_image_density': {'MINIMAL': 0.0, 'TWO': 0.0, 'TITLE_ONLY': 0.0},
    'fodp_image_to_slide_ratio': {'MINIMAL': 0.0, 'TWO': 0.0, 'TITLE_ONLY': 0.0},
    'fodp_is_shape_heavy': {'MINIMAL': False, 'TWO': True, 'TITLE_ONLY': False},
    'fodp_is_single_slide': {'MINIMAL': True, 'TWO': False, 'TITLE_ONLY': False},
    'fodp_is_text_heavy': {'MINIMAL': False, 'TWO': False, 'TITLE_ONLY': False},
    'fodp_longest_slide_index': {'MINIMAL': 0, 'TWO': 0, 'TITLE_ONLY': -1},
    'fodp_master_page_count': {'MINIMAL': 0, 'TWO': 0, 'TITLE_ONLY': 0},
    'fodp_max_notes_length': {'MINIMAL': 0, 'TWO': 0, 'TITLE_ONLY': 0},
    'fodp_max_shapes_per_slide': {'MINIMAL': 1, 'TWO': 2, 'TITLE_ONLY': 0},
    'fodp_max_text_length': {'MINIMAL': 0, 'TWO': 0, 'TITLE_ONLY': 0},
    'fodp_max_text_per_slide': {'MINIMAL': 5, 'TWO': 33, 'TITLE_ONLY': 0},
    'fodp_min_shapes_per_slide': {'MINIMAL': 1, 'TWO': 1, 'TITLE_ONLY': 0},
    'fodp_min_text_per_slide': {'MINIMAL': 5, 'TWO': 10, 'TITLE_ONLY': 0},
    'fodp_nonempty_slide_count': {'MINIMAL': 1, 'TWO': 2, 'TITLE_ONLY': 0},
    'fodp_nonempty_slide_ratio': {'MINIMAL': 1.0, 'TWO': 1.0, 'TITLE_ONLY': 0.0},
    'fodp_notes_density': {'MINIMAL': 0.0, 'TWO': 0.0, 'TITLE_ONLY': 0.0},
    'fodp_notes_text': {'MINIMAL': [''], 'TWO': ['', ''], 'TITLE_ONLY': []},
    'fodp_notes_to_slide_ratio': {'MINIMAL': 0.0, 'TWO': 0.0, 'TITLE_ONLY': 0.0},
    'fodp_shape_count_variance': {'MINIMAL': 0.0, 'TWO': 0.25, 'TITLE_ONLY': 0.0},
    'fodp_shape_to_slide_ratio': {'MINIMAL': 1.0, 'TWO': 1.5, 'TITLE_ONLY': 0.0},
    'fodp_shape_variance': {'MINIMAL': 0, 'TWO': 1, 'TITLE_ONLY': 0},
    'fodp_shortest_slide_index': {'MINIMAL': 0, 'TWO': 1, 'TITLE_ONLY': -1},
    'fodp_slide_count': {'MINIMAL': 1, 'TWO': 2, 'TITLE_ONLY': 0},
    'fodp_slide_count_is_one': {'MINIMAL': True, 'TWO': False, 'TITLE_ONLY': False},
    'fodp_slide_shape_counts': {'MINIMAL': [1], 'TWO': [2, 1], 'TITLE_ONLY': []},
    'fodp_slide_text_density': {'MINIMAL': 5.0, 'TWO': 21.5, 'TITLE_ONLY': 0.0},
    'fodp_slide_text_lengths': {'MINIMAL': [], 'TWO': [], 'TITLE_ONLY': []},
    'fodp_slide_text_variance': {'MINIMAL': 0.0, 'TWO': 132.25, 'TITLE_ONLY': 0.0},
    'fodp_slide_titles': {'MINIMAL': ['Hello'], 'TWO': ['Introduction', 'Conclusion'], 'TITLE_ONLY': []},
    'fodp_text_length_variance': {'MINIMAL': 0.0, 'TWO': 0.0, 'TITLE_ONLY': 0.0},
    'fodp_text_per_slide': {
        'MINIMAL': ['Hello'],
        'TWO': ['Introduction\nFirst slide content.', 'Conclusion'],
        'TITLE_ONLY': [],
    },
    'fodp_text_to_slide_ratio': {'MINIMAL': 5.0, 'TWO': 21.0, 'TITLE_ONLY': 0.0},
    'fodp_title_coverage': {'MINIMAL': 1.0, 'TWO': 1.0, 'TITLE_ONLY': 0.0},
    'fodp_total_images': {'MINIMAL': 0, 'TWO': 0, 'TITLE_ONLY': 0},
    'fodp_total_notes_length': {'MINIMAL': 0, 'TWO': 0, 'TITLE_ONLY': 0},
    'fodp_total_shape_count': {'MINIMAL': 1, 'TWO': 3, 'TITLE_ONLY': 0},
    'fodp_total_text_chars': {'MINIMAL': 5, 'TWO': 43, 'TITLE_ONLY': 0},
    'fodp_min_shape_count': {'MINIMAL': 1, 'TWO': 1, 'TITLE_ONLY': 0},
    'fodp_text_to_shape_ratio': {'MINIMAL': 0.0, 'TWO': 0.0, 'TITLE_ONLY': 0.0},
    'fodp_slide_count_squared': {'MINIMAL': 1, 'TWO': 4, 'TITLE_ONLY': 0},
    'fodp_slide_name_list': {'MINIMAL': ['Slide1'], 'TWO': ['Slide1', 'Slide2'], 'TITLE_ONLY': []},
    'fodp_total_text_items': {'MINIMAL': 1, 'TWO': 3, 'TITLE_ONLY': 0},
    'fodp_slides_with_text_count': {'MINIMAL': 1, 'TWO': 2, 'TITLE_ONLY': 0},
    'fodp_max_slide_text_items': {'MINIMAL': 1, 'TWO': 2, 'TITLE_ONLY': 0},
    'fodp_min_slide_text_items': {'MINIMAL': 1, 'TWO': 1, 'TITLE_ONLY': 0},
    'fodp_is_fodp': {'MINIMAL': True, 'TWO': True, 'TITLE_ONLY': True},
    'fodp_first_slide_title': {'MINIMAL': 'Hello', 'TWO': 'Introduction', 'TITLE_ONLY': ''},
    'fodp_has_text': {'MINIMAL': True, 'TWO': True, 'TITLE_ONLY': False},
    'fodp_has_multiple_slides': {'MINIMAL': False, 'TWO': True, 'TITLE_ONLY': False},
    'fodp_slides_with_shapes_count': {'MINIMAL': 1, 'TWO': 2, 'TITLE_ONLY': 0},
    'fodp_all_text_items': {
        'MINIMAL': ['Hello'],
        'TWO': ['Introduction', 'First slide content.', 'Conclusion'],
        'TITLE_ONLY': [],
    },
    'fodp_slide_names_are_unique': {'MINIMAL': True, 'TWO': True, 'TITLE_ONLY': True},
    'fodp_last_slide_title': {'MINIMAL': 'Hello', 'TWO': 'Conclusion', 'TITLE_ONLY': ''},
    'fodp_slide_text_counts': {'MINIMAL': [1], 'TWO': [2, 1], 'TITLE_ONLY': []},
    'fodp_max_shape_count': {'MINIMAL': 1, 'TWO': 2, 'TITLE_ONLY': 0},
    'fodp_all_text_items_flat': {
        'MINIMAL': ['Hello'],
        'TWO': ['Introduction', 'First slide content.', 'Conclusion'],
        'TITLE_ONLY': [],
    },
    'fodp_slides_without_text_count': {'MINIMAL': 0, 'TWO': 0, 'TITLE_ONLY': 0},
    'fodp_avg_title_words': {'MINIMAL': 1.0, 'TWO': 1.0, 'TITLE_ONLY': 0.0},
    'fodp_max_title_length': {'MINIMAL': 5, 'TWO': 12, 'TITLE_ONLY': 0},
    'fodp_min_title_length': {'MINIMAL': 5, 'TWO': 10, 'TITLE_ONLY': 0},
    'fodp_all_slides_have_titles': {'MINIMAL': True, 'TWO': True, 'TITLE_ONLY': True},
    'fodp_note_count': {'MINIMAL': 1, 'TWO': 2, 'TITLE_ONLY': 0},
}

CASES = [
    (func_name, source_label, expected)
    for func_name, values in FUNC_VALUES.items()
    for source_label, expected in values.items()
]
CASE_IDS = [f"{func_name}::{source_label}" for func_name, source_label, _ in CASES]


@pytest.mark.parametrize("func_name,source_label,expected", CASES, ids=CASE_IDS)
def test_analytics_function_matches_expected(func_name, source_label, expected):
    assert hasattr(fodp, func_name), f"{func_name} not importable from fodp package"
    func = getattr(fodp, func_name)
    source = SOURCES[source_label]
    actual = func(source)
    if isinstance(expected, float):
        assert actual == pytest.approx(expected)
    else:
        assert actual == expected


def test_func_values_table_covers_expected_function_count():
    # Guard against silent shrinkage of the data-driven coverage table.
    assert len(FUNC_VALUES) >= 75


# ---------------------------------------------------------------------------
# Part 10 — XML_RICH supplementary coverage (images, notes, master pages,
# zero-shape slide) — code paths the 3 corpus samples never exercise.
# ---------------------------------------------------------------------------

class TestRichFixtureAnalytics:
    def test_image_count_and_related(self):
        assert fodp.fodp_image_count(XML_RICH) == 2
        assert fodp.fodp_total_images(XML_RICH) == 2
        assert fodp.fodp_has_images(XML_RICH) is True
        assert fodp.fodp_image_density(XML_RICH) == pytest.approx(2 / 3)
        assert fodp.fodp_image_to_slide_ratio(XML_RICH) == pytest.approx(2 / 3)

    def test_notes_extraction(self):
        assert fodp.fodp_notes_text(XML_RICH) == ["Note one text", "Note two", ""]
        assert fodp.fodp_has_notes(XML_RICH) is True
        assert fodp.fodp_total_notes_length(XML_RICH) == 21
        assert fodp.fodp_max_notes_length(XML_RICH) == 13
        assert fodp.fodp_avg_notes_length(XML_RICH) == pytest.approx(7.0)
        assert fodp.fodp_notes_density(XML_RICH) == pytest.approx(7.0)
        assert fodp.fodp_notes_to_slide_ratio(XML_RICH) == pytest.approx(7.0)

    def test_master_page_count(self):
        # 2 distinct master pages: "Default" (slides 1-2) and "Alt" (slide 3).
        assert fodp.fodp_master_page_count(XML_RICH) == 2

    def test_zero_shape_slide_detected(self):
        assert fodp.fodp_empty_slide_count(XML_RICH) == 1
        assert fodp.fodp_has_empty_slides(XML_RICH) is True
        assert fodp.fodp_has_zero_shapes(XML_RICH) is False  # total shapes = 3, not 0
        assert fodp.fodp_min_shapes_per_slide(XML_RICH) == 0
        assert fodp.fodp_max_shapes_per_slide(XML_RICH) == 2
        assert fodp.fodp_shape_variance(XML_RICH) == 2

    def test_shape_and_text_distribution(self):
        assert fodp.fodp_slide_shape_counts(XML_RICH) == [2, 1, 0]
        assert fodp.fodp_total_shape_count(XML_RICH) == 3
        assert fodp.fodp_shape_count_variance(XML_RICH) == pytest.approx(2 / 3)
        assert fodp.fodp_shape_to_slide_ratio(XML_RICH) == pytest.approx(1.0)
        assert fodp.fodp_is_shape_heavy(XML_RICH) is False

    def test_text_distribution(self):
        assert fodp.fodp_text_per_slide(XML_RICH) == ["Slide One", "Slide Two", ""]
        assert fodp.fodp_max_text_per_slide(XML_RICH) == 9
        assert fodp.fodp_min_text_per_slide(XML_RICH) == 0
        assert fodp.fodp_total_text_chars(XML_RICH) == 18
        assert fodp.fodp_slide_text_density(XML_RICH) == pytest.approx(6.0)
        assert fodp.fodp_slide_text_variance(XML_RICH) == pytest.approx(18.0)
        assert fodp.fodp_nonempty_slide_count(XML_RICH) == 2
        assert fodp.fodp_nonempty_slide_ratio(XML_RICH) == pytest.approx(2 / 3)
        assert fodp.fodp_all_slides_have_text(XML_RICH) is False

    def test_title_related_safe_functions(self):
        # These do NOT crash on the untitled slide because they filter falsy
        # entries (`if t`) before doing string ops, unlike the functions
        # documented in TestKnownTitleNoneBugs below.
        assert fodp.fodp_slide_titles(XML_RICH) == ["Slide One", "Slide Two", None]
        assert fodp.fodp_avg_title_length(XML_RICH) == pytest.approx(9.0)
        assert fodp.fodp_has_titles(XML_RICH) is True
        assert fodp.fodp_title_coverage(XML_RICH) == pytest.approx(2 / 3)

    def test_longest_and_shortest_slide_index(self):
        assert fodp.fodp_longest_slide_index(XML_RICH) == 0
        assert fodp.fodp_shortest_slide_index(XML_RICH) == 2

    def test_sentence_and_numeric_content(self):
        assert fodp.fodp_avg_sentence_length(XML_RICH) == pytest.approx(19.0)
        assert fodp.fodp_has_numeric_content(XML_RICH) is False

    def test_slide_count_and_flags(self):
        assert fodp.fodp_slide_count(XML_RICH) == 3
        assert fodp.fodp_slide_count_is_one(XML_RICH) is False
        assert fodp.fodp_is_single_slide(XML_RICH) is False
        assert fodp.fodp_has_multi_slide(XML_RICH) is True
        assert fodp.fodp_is_text_heavy(XML_RICH) is False

    def test_slide_name_list_and_uniqueness(self):
        assert fodp.fodp_slide_name_list(XML_RICH) == ["Slide1", "Slide2", "Slide3"]
        assert fodp.fodp_slide_names_are_unique(XML_RICH) is True

    def test_text_item_helpers(self):
        assert fodp.fodp_total_text_items(XML_RICH) == 2
        assert fodp.fodp_slides_with_text_count(XML_RICH) == 2
        assert fodp.fodp_max_slide_text_items(XML_RICH) == 1
        assert fodp.fodp_min_slide_text_items(XML_RICH) == 0
        assert fodp.fodp_all_text_items(XML_RICH) == ["Slide One", "Slide Two"]
        assert fodp.fodp_all_text_items_flat(XML_RICH) == ["Slide One", "Slide Two"]
        assert fodp.fodp_slides_without_text_count(XML_RICH) == 1
        assert fodp.fodp_slide_text_counts(XML_RICH) == [1, 1, 0]

    def test_last_slide_title_is_none_when_untitled(self):
        # Documents actual behavior: the last slide has no title frame, and the
        # "" default in `.get("title", "")` never triggers because the key is
        # present with value None (see module docstring).
        assert fodp.fodp_last_slide_title(XML_RICH) is None

    def test_first_slide_title_present(self):
        assert fodp.fodp_first_slide_title(XML_RICH) == "Slide One"

    def test_shapes_with_and_without(self):
        assert fodp.fodp_slides_with_shapes_count(XML_RICH) == 2
        assert fodp.fodp_max_shape_count(XML_RICH) == 2
        assert fodp.fodp_min_shape_count(XML_RICH) == 0

    def test_is_fodp_true(self):
        assert fodp.fodp_is_fodp(XML_RICH) is True

    def test_text_to_slide_and_shape_ratios(self):
        assert fodp.fodp_text_to_slide_ratio(XML_RICH) == pytest.approx(6.0)
        assert fodp.fodp_text_to_shape_ratio(XML_RICH) == pytest.approx(7.0)
        assert fodp.fodp_average_text_per_slide(XML_RICH) == pytest.approx(6.0)
        assert fodp.fodp_average_shapes_per_slide(XML_RICH) == pytest.approx(1.0)
        assert fodp.fodp_avg_shapes_per_slide(XML_RICH) == pytest.approx(1.0)
        assert fodp.fodp_avg_text_length(XML_RICH) == pytest.approx(6.0)

    def test_slide_count_squared(self):
        assert fodp.fodp_slide_count_squared(XML_RICH) == 9

    def test_max_text_length_family_still_default_on_rich(self):
        # Same "slides" vs "pages" key bug (see module docstring) — always
        # returns the empty-input default even on a 3-slide fixture.
        assert fodp.fodp_max_text_length(XML_RICH) == 0
        assert fodp.fodp_text_length_variance(XML_RICH) == 0.0
        assert fodp.fodp_slide_text_lengths(XML_RICH) == []

    def test_wrong_mime_is_fodp_false(self):
        assert fodp.fodp_is_fodp(XML_WRONG_MIME) is False
        assert fodp.fodp_slide_count(XML_WRONG_MIME) == 1


# ---------------------------------------------------------------------------
# Part 11 — known-bug documentation: title=None crashes
#
# page_info["title"] is *always* set (to None by default in _extract_pages),
# so `dict.get("title", "")` on an untitled slide returns the stored None
# rather than the "" default. Any function that then calls .strip()/.split()/
# len() on that value raises. These tests pin the CURRENT (buggy) behavior so
# it is documented and any future fix shows up as a test that now needs
# updating rather than a silent behavior change.
# ---------------------------------------------------------------------------

class TestKnownTitleNoneBugs:
    def test_avg_title_words_raises_on_untitled_slide(self):
        with pytest.raises(AttributeError):
            fodp.fodp_avg_title_words(XML_RICH)

    def test_avg_title_words_safe_on_fully_titled_deck(self):
        assert fodp.fodp_avg_title_words(TWO) == pytest.approx(1.0)
        assert fodp.fodp_avg_title_words(TITLE_ONLY) == 0.0

    def test_max_title_length_raises_on_untitled_slide(self):
        with pytest.raises(TypeError):
            fodp.fodp_max_title_length(XML_RICH)

    def test_max_title_length_safe_on_fully_titled_deck(self):
        assert fodp.fodp_max_title_length(TWO) == 12
        assert fodp.fodp_max_title_length(TITLE_ONLY) == 0

    def test_min_title_length_raises_on_untitled_slide(self):
        with pytest.raises(TypeError):
            fodp.fodp_min_title_length(XML_RICH)

    def test_min_title_length_safe_on_fully_titled_deck(self):
        assert fodp.fodp_min_title_length(TWO) == 10

    def test_all_slides_have_titles_raises_on_untitled_slide(self):
        with pytest.raises(AttributeError):
            fodp.fodp_all_slides_have_titles(XML_RICH)

    def test_all_slides_have_titles_safe_on_fully_titled_deck(self):
        assert fodp.fodp_all_slides_have_titles(TWO) is True
        assert fodp.fodp_all_slides_have_titles(MINIMAL) is True
        # Vacuously true for zero slides.
        assert fodp.fodp_all_slides_have_titles(TITLE_ONLY) is True

    def test_note_count_raises_on_untitled_slide(self):
        with pytest.raises(AttributeError):
            fodp.fodp_note_count(XML_RICH)

    def test_note_count_safe_on_fully_titled_deck(self):
        assert fodp.fodp_note_count(TWO) == 2
        assert fodp.fodp_note_count(TITLE_ONLY) == 0


# ---------------------------------------------------------------------------
# Part 12 — corpus-wide smoke test (every function against every real sample)
# ---------------------------------------------------------------------------

def test_all_corpus_samples_load_without_error():
    for path in sorted(SAMPLES_DIR.glob("*.fodp")):
        model = fodp.load(path)
        assert "pages" in model
        assert isinstance(model["page_count"], int)


def test_all_corpus_samples_support_full_analytics_pass():
    # Every *_titled_ deck in the corpus is fully titled, so this exercises
    # the whole safe analytics surface (including the title-dependent
    # functions from TestKnownTitleNoneBugs) against every real sample file
    # without hitting the None-title bug.
    safe_titled_funcs = [
        "fodp_slide_count", "fodp_total_shape_count", "fodp_has_titles",
        "fodp_avg_title_words", "fodp_max_title_length", "fodp_min_title_length",
        "fodp_all_slides_have_titles", "fodp_note_count",
    ]
    for path in sorted(SAMPLES_DIR.glob("*.fodp")):
        for name in safe_titled_funcs:
            func = getattr(fodp, name)
            func(path)  # must not raise for any real corpus sample
