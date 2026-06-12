"""
test_r75_fodt_new_apis.py

R75 Train G: Tests for the two new FODT APIs:
- document_paragraph_style_distribution
- document_language_list

Sprint: FORMAT-FACTORY-R75-FINAL-ARTIFACT-AUTHORITY-REPAIR-RC-SEAL-PRODUCT-ADVANCEMENT-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fodt.neutral_model import (
    document_paragraph_style_distribution,
    document_language_list,
)


def _make_doc(blocks=None, meta=None, **kwargs):
    doc = {"blocks": blocks or []}
    if meta:
        doc["meta"] = meta
    doc.update(kwargs)
    return doc


def _make_block(style=None, runs=None, **kwargs):
    block = {}
    if style:
        block["style_name"] = style
    if runs is not None:
        block["runs"] = runs
    block.update(kwargs)
    return block


class TestDocumentParagraphStyleDistribution:
    """Tests for document_paragraph_style_distribution (R75)."""

    def test_empty_document_returns_zero(self):
        result = document_paragraph_style_distribution(_make_doc())
        assert result["style_count"] == 0
        assert result["distribution"] == {}
        assert result["heading_styles"] == []

    def test_single_paragraph_style(self):
        doc = _make_doc([_make_block("Body Text")])
        result = document_paragraph_style_distribution(doc)
        assert result["style_count"] == 1
        assert result["distribution"]["Body Text"] == 1

    def test_multiple_paragraphs_same_style(self):
        doc = _make_doc([
            _make_block("Body Text"),
            _make_block("Body Text"),
            _make_block("Body Text"),
        ])
        result = document_paragraph_style_distribution(doc)
        assert result["distribution"]["Body Text"] == 3

    def test_heading_style_detected(self):
        doc = _make_doc([
            _make_block("Heading 1"),
            _make_block("Heading 2"),
            _make_block("Body Text"),
        ])
        result = document_paragraph_style_distribution(doc)
        assert "Heading 1" in result["heading_styles"]
        assert "Heading 2" in result["heading_styles"]
        assert "Body Text" not in result["heading_styles"]

    def test_default_style_when_none(self):
        doc = _make_doc([{}])  # block without style
        result = document_paragraph_style_distribution(doc)
        assert result["distribution"].get("Default", 0) == 1

    def test_text_style_name_key(self):
        block = {"text:style-name": "Caption"}
        doc = _make_doc([block])
        result = document_paragraph_style_distribution(doc)
        assert result["distribution"].get("Caption", 0) == 1

    def test_mixed_styles(self):
        doc = _make_doc([
            _make_block("Heading 1"),
            _make_block("Body Text"),
            _make_block("Body Text"),
            _make_block("Code"),
        ])
        result = document_paragraph_style_distribution(doc)
        assert result["style_count"] == 3
        assert result["distribution"]["Body Text"] == 2
        assert result["distribution"]["Heading 1"] == 1


class TestDocumentLanguageList:
    """Tests for document_language_list (R75)."""

    def test_empty_document_returns_empty(self):
        result = document_language_list(_make_doc())
        assert result == []

    def test_language_in_block(self):
        doc = _make_doc([_make_block(language="en")])
        result = document_language_list(doc)
        assert "en" in result

    def test_deduplicates_languages(self):
        doc = _make_doc([
            _make_block(language="en"),
            _make_block(language="en"),
            _make_block(language="de"),
        ])
        result = document_language_list(doc)
        assert result.count("en") == 1
        assert "de" in result

    def test_returns_sorted(self):
        doc = _make_doc([
            _make_block(language="fr"),
            _make_block(language="de"),
            _make_block(language="en"),
        ])
        result = document_language_list(doc)
        assert result == sorted(result)

    def test_language_in_run(self):
        runs = [{"language": "ja"}]
        doc = _make_doc([_make_block(runs=runs)])
        result = document_language_list(doc)
        assert "ja" in result

    def test_meta_language(self):
        doc = _make_doc(meta={"language": "zh"})
        result = document_language_list(doc)
        assert "zh" in result

    def test_lowercase_normalization(self):
        doc = _make_doc([_make_block(language="EN")])
        result = document_language_list(doc)
        assert "en" in result
        assert "EN" not in result

    def test_fo_language_key(self):
        block = {"fo:language": "pt"}
        doc = _make_doc([block])
        result = document_language_list(doc)
        assert "pt" in result

    def test_document_language_field(self):
        doc = _make_doc(document_language="es")
        result = document_language_list(doc)
        assert "es" in result

    def test_no_empty_strings(self):
        doc = _make_doc([{"language": ""}])
        result = document_language_list(doc)
        assert "" not in result
