"""Tests for AbwDocument domain model.

Verifies spec_qname class attribute, construction, typed properties,
from_file factory, and to_dict round-trip.
"""
from __future__ import annotations

import sys
import tempfile
import os
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO / "src" / "python") not in sys.path:
    sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.models import AbwDocument


_SAMPLE_DATA = {
    "is_abw": True,
    "section_count": 2,
    "paragraph_count": 3,
    "paragraphs": ["Hello world", "Second paragraph", "Third paragraph"],
}

_ABW_XML = """\
<abiword mimetype="application/x-abiword">
  <section>
    <p>Hello</p>
    <p>World</p>
  </section>
  <section>
    <p>Section two</p>
  </section>
</abiword>
"""


class TestAbwDocumentClassAttributes:
    def test_spec_qname_is_class_attribute(self):
        assert AbwDocument.spec_qname == "abiword:document"

    def test_spec_qname_accessible_without_instance(self):
        assert AbwDocument.spec_qname == "abiword:document"

    def test_spec_fact_ref(self):
        assert AbwDocument.spec_fact_ref == "FACT-ABW-001"

    def test_namespace_uri(self):
        assert AbwDocument.namespace_uri == "http://www.abisource.com/awml/"

    def test_local_name(self):
        assert AbwDocument.local_name == "document"

    def test_facade_names_is_list(self):
        assert isinstance(AbwDocument.facade_names, list)


class TestAbwDocumentConstruction:
    def test_construct_from_dict(self):
        doc = AbwDocument(_SAMPLE_DATA)
        assert isinstance(doc, AbwDocument)

    def test_section_count(self):
        doc = AbwDocument(_SAMPLE_DATA)
        assert doc.section_count == 2

    def test_paragraph_count(self):
        doc = AbwDocument(_SAMPLE_DATA)
        assert doc.paragraph_count == 3

    def test_paragraphs(self):
        doc = AbwDocument(_SAMPLE_DATA)
        assert doc.paragraphs == ["Hello world", "Second paragraph", "Third paragraph"]

    def test_is_abw(self):
        doc = AbwDocument(_SAMPLE_DATA)
        assert doc.is_abw is True

    def test_empty_doc(self):
        doc = AbwDocument({})
        assert doc.section_count == 0
        assert doc.paragraph_count == 0
        assert doc.paragraphs == []
        assert doc.is_abw is False


class TestAbwDocumentGetParagraph:
    def test_get_first_paragraph(self):
        doc = AbwDocument(_SAMPLE_DATA)
        assert doc.get_paragraph(0) == "Hello world"

    def test_get_last_paragraph(self):
        doc = AbwDocument(_SAMPLE_DATA)
        assert doc.get_paragraph(2) == "Third paragraph"

    def test_out_of_bounds_returns_empty(self):
        doc = AbwDocument(_SAMPLE_DATA)
        assert doc.get_paragraph(99) == ""

    def test_negative_index_returns_empty(self):
        doc = AbwDocument(_SAMPLE_DATA)
        assert doc.get_paragraph(-1) == ""


class TestAbwDocumentToDict:
    def test_to_dict_returns_dict(self):
        doc = AbwDocument(_SAMPLE_DATA)
        result = doc.to_dict()
        assert isinstance(result, dict)

    def test_to_dict_has_expected_keys(self):
        doc = AbwDocument(_SAMPLE_DATA)
        result = doc.to_dict()
        assert "section_count" in result
        assert "paragraph_count" in result

    def test_to_dict_is_copy(self):
        doc = AbwDocument(_SAMPLE_DATA)
        result = doc.to_dict()
        result["extra"] = "should not affect original"
        assert "extra" not in doc.to_dict()


class TestAbwDocumentFromFile:
    def test_from_file_xml_string_path(self):
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".abw", delete=False, encoding="utf-8"
        )
        tmp.write(_ABW_XML)
        tmp.close()
        try:
            doc = AbwDocument.from_file(tmp.name)
            assert isinstance(doc, AbwDocument)
            assert doc.section_count == 2
            assert doc.paragraph_count == 3
        finally:
            os.unlink(tmp.name)

    def test_from_file_paragraphs(self):
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".abw", delete=False, encoding="utf-8"
        )
        tmp.write(_ABW_XML)
        tmp.close()
        try:
            doc = AbwDocument.from_file(tmp.name)
            assert "Hello" in doc.paragraphs[0]
        finally:
            os.unlink(tmp.name)

    def test_from_file_path_object(self):
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".abw", delete=False, encoding="utf-8"
        )
        tmp.write(_ABW_XML)
        tmp.close()
        try:
            doc = AbwDocument.from_file(Path(tmp.name))
            assert doc.is_abw is True
        finally:
            os.unlink(tmp.name)


class TestAbwDocumentRepr:
    def test_repr_includes_counts(self):
        doc = AbwDocument(_SAMPLE_DATA)
        r = repr(doc)
        assert "section_count=2" in r
        assert "paragraph_count=3" in r
