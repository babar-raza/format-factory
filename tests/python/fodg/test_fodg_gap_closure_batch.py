"""Gap closure tests for FODG format — batch covering 15 open gaps.

Gaps covered:
  GAP-FODG-FOSS-EXPORT_TO_TX-001, GAP-FODG-FOSS-EXPORT_TO_CS-001,
  GAP-FODG-FOSS-EXPORT_TO_JS-001, GAP-FODG-FOSS-GET_TEXT_SHA-001,
  GAP-FODG-FOSS-GET_PAGE_IND-001, GAP-FODG-FOSS-FODGERROR-001,
  GAP-FODG-FOSS-FODGPARSEERR-001, GAP-FODG-FOSS-GET_SHAPE_CO-001,
  GAP-FODG-FOSS-EXTRACT_TEXT-001, GAP-FODG-FOSS-GET_PAGE_MET-001,
  GAP-FODG-FOSS-GET_PAGE_TEX-001, GAP-FODG-FOSS-FIND_SHAPES_-001,
  GAP-FODG-FOSS-EXPORT_PAGE_-001, GAP-FODG-FOSS-FODG_TOTAL_S-001,
  GAP-FODG-FOSS-FODG_TEXT_SH-001
"""
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg import (
    FodgError,
    FodgParseError,
    export_page_to_json,
    export_to_csv,
    export_to_json,
    export_to_txt,
    extract_text,
    find_shapes_by_text_pattern,
    fodg_text_shape_count,
    fodg_total_shape_count,
    get_page_index,
    get_page_metadata,
    get_page_text,
    get_shape_count,
    get_text_shapes,
    load,
)

MINIMAL_FODG = b"""<?xml version="1.0" encoding="UTF-8"?>
<office:document
  xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
  xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
  xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
  office:mimetype="application/vnd.oasis.opendocument.graphics-flat-xml">
  <office:body>
    <office:drawing>
      <draw:page draw:name="Page1">
        <draw:text-box svg:x="1cm" svg:y="1cm" svg:width="10cm" svg:height="2cm">
          <text:p>Hello World</text:p>
        </draw:text-box>
        <draw:rect svg:x="1cm" svg:y="4cm" svg:width="5cm" svg:height="3cm"/>
      </draw:page>
      <draw:page draw:name="Page2">
        <draw:ellipse svg:x="2cm" svg:y="2cm" svg:width="4cm" svg:height="4cm">
          <text:p>Circle Text</text:p>
        </draw:ellipse>
      </draw:page>
    </office:drawing>
  </office:body>
</office:document>
"""


@pytest.fixture
def fodg_file(tmp_path):
    p = tmp_path / "sample.fodg"
    p.write_bytes(MINIMAL_FODG)
    return p


@pytest.fixture
def fodg_model():
    return load(MINIMAL_FODG)


# --- GAP-FODG-FOSS-FODGERROR-001 ---
class TestFodgError:
    def test_is_exception(self):
        assert issubclass(FodgError, Exception)

    def test_can_raise(self):
        with pytest.raises(FodgError):
            raise FodgError("test error")


# --- GAP-FODG-FOSS-FODGPARSEERR-001 ---
class TestFodgParseError:
    def test_is_subclass(self):
        assert issubclass(FodgParseError, (FodgError, Exception))

    def test_can_raise(self):
        with pytest.raises(FodgParseError):
            raise FodgParseError("bad parse")


# --- GAP-FODG-FOSS-EXPORT_TO_TX-001 ---
class TestExportToTxt:
    def test_basic(self, fodg_file):
        result = export_to_txt(fodg_file)
        assert isinstance(result, str)
        assert "Hello World" in result

    def test_bytes(self):
        result = export_to_txt(MINIMAL_FODG)
        assert isinstance(result, str)
        assert len(result) > 0


# --- GAP-FODG-FOSS-EXPORT_TO_CS-001 ---
class TestExportToCsv:
    def test_basic(self, fodg_file):
        result = export_to_csv(fodg_file)
        assert isinstance(result, str)
        assert len(result) > 0


# --- GAP-FODG-FOSS-EXPORT_TO_JS-001 ---
class TestExportToJson:
    def test_basic(self, fodg_model):
        result = export_to_json(fodg_model)
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed is not None


# --- GAP-FODG-FOSS-GET_TEXT_SHA-001 ---
class TestGetTextShapes:
    def test_basic(self, fodg_model):
        shapes = get_text_shapes(fodg_model)
        assert isinstance(shapes, list)
        assert len(shapes) >= 1


# --- GAP-FODG-FOSS-GET_PAGE_IND-001 ---
class TestGetPageIndex:
    def test_page1(self, fodg_model):
        idx = get_page_index(fodg_model, "Page1")
        assert idx == 0

    def test_page2(self, fodg_model):
        idx = get_page_index(fodg_model, "Page2")
        assert idx == 1


# --- GAP-FODG-FOSS-GET_SHAPE_CO-001 ---
class TestGetShapeCount:
    def test_basic(self, fodg_file):
        count = get_shape_count(fodg_file)
        assert isinstance(count, int)
        assert count >= 2


# --- GAP-FODG-FOSS-EXTRACT_TEXT-001 ---
class TestExtractText:
    def test_basic(self, fodg_file):
        texts = extract_text(fodg_file)
        assert isinstance(texts, list)
        combined = " ".join(texts)
        assert "Hello" in combined or "World" in combined


# --- GAP-FODG-FOSS-GET_PAGE_MET-001 ---
class TestGetPageMetadata:
    def test_basic(self, fodg_file):
        meta = get_page_metadata(fodg_file)
        assert isinstance(meta, list)
        assert len(meta) >= 1


# --- GAP-FODG-FOSS-GET_PAGE_TEX-001 ---
class TestGetPageText:
    def test_page1(self, fodg_model):
        texts = get_page_text(fodg_model, 0)
        assert isinstance(texts, list)
        combined = " ".join(texts)
        assert "Hello" in combined


# --- GAP-FODG-FOSS-FIND_SHAPES_-001 ---
class TestFindShapesByTextPattern:
    def test_find(self, fodg_model):
        result = find_shapes_by_text_pattern(fodg_model, "Hello")
        assert isinstance(result, list)
        assert len(result) >= 1


# --- GAP-FODG-FOSS-EXPORT_PAGE_-001 ---
class TestExportPageToJson:
    def test_page0(self, fodg_model):
        result = export_page_to_json(fodg_model, 0)
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed is not None


# --- GAP-FODG-FOSS-FODG_TOTAL_S-001 ---
class TestFodgTotalShapeCount:
    def test_basic(self, fodg_file):
        count = fodg_total_shape_count(fodg_file)
        assert isinstance(count, int)
        assert count >= 2


# --- GAP-FODG-FOSS-FODG_TEXT_SH-001 ---
class TestFodgTextShapeCount:
    def test_basic(self, fodg_file):
        count = fodg_text_shape_count(fodg_file)
        assert isinstance(count, int)
        assert count >= 1
