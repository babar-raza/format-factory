"""Tests for odt_writer.py — ODT write capability.

Gap closure: GAP-PROD-INV-WRITE-001 (ODT was read-only)
"""
from __future__ import annotations

import os
import tempfile
import zipfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]

import sys
if str(_REPO / "src" / "python") not in sys.path:
    sys.path.insert(0, str(_REPO / "src" / "python"))

from odt.odt_writer import odt_from_model, odt_from_text, write_odt
from odt.odt_parser import parse_odt_strict


class TestWriteOdt:
    def test_write_creates_file(self, tmp_path):
        dest = tmp_path / "out.odt"
        result = write_odt(["Hello", "World"], dest)
        assert dest.exists()
        assert result == dest

    def test_write_creates_valid_zip(self, tmp_path):
        dest = tmp_path / "out.odt"
        write_odt(["paragraph one"], dest)
        assert zipfile.is_zipfile(str(dest))

    def test_write_includes_mimetype(self, tmp_path):
        dest = tmp_path / "out.odt"
        write_odt(["test"], dest)
        with zipfile.ZipFile(str(dest)) as zf:
            assert "mimetype" in zf.namelist()
            assert zf.read("mimetype").decode() == "application/vnd.oasis.opendocument.text"

    def test_write_includes_content_xml(self, tmp_path):
        dest = tmp_path / "out.odt"
        write_odt(["test paragraph"], dest)
        with zipfile.ZipFile(str(dest)) as zf:
            assert "content.xml" in zf.namelist()

    def test_write_content_contains_paragraph_text(self, tmp_path):
        dest = tmp_path / "out.odt"
        write_odt(["Hello World"], dest)
        with zipfile.ZipFile(str(dest)) as zf:
            content = zf.read("content.xml").decode()
        assert "Hello World" in content

    def test_write_multiple_paragraphs(self, tmp_path):
        dest = tmp_path / "out.odt"
        write_odt(["First", "Second", "Third"], dest)
        with zipfile.ZipFile(str(dest)) as zf:
            content = zf.read("content.xml").decode()
        assert "First" in content
        assert "Second" in content
        assert "Third" in content

    def test_write_with_heading(self, tmp_path):
        dest = tmp_path / "out.odt"
        write_odt(["body text"], dest, heading="My Title")
        with zipfile.ZipFile(str(dest)) as zf:
            content = zf.read("content.xml").decode()
        assert "My Title" in content
        assert "body text" in content

    def test_write_empty_paragraphs(self, tmp_path):
        dest = tmp_path / "out.odt"
        write_odt([], dest)
        assert dest.exists()
        assert zipfile.is_zipfile(str(dest))

    def test_write_returns_path(self, tmp_path):
        dest = tmp_path / "out.odt"
        result = write_odt(["test"], dest)
        assert isinstance(result, Path)

    def test_write_string_path(self, tmp_path):
        dest = str(tmp_path / "out.odt")
        write_odt(["test"], dest)
        assert Path(dest).exists()

    def test_write_escapes_xml_special_chars(self, tmp_path):
        dest = tmp_path / "out.odt"
        write_odt(['a & b < c > d "e"'], dest)
        with zipfile.ZipFile(str(dest)) as zf:
            content = zf.read("content.xml").decode()
        assert "&amp;" in content
        assert "&lt;" in content


class TestOdtFromText:
    def test_from_text_creates_file(self, tmp_path):
        dest = tmp_path / "out.odt"
        result = odt_from_text("Hello\nWorld", dest)
        assert dest.exists()

    def test_from_text_splits_on_newlines(self, tmp_path):
        dest = tmp_path / "out.odt"
        odt_from_text("Line one\nLine two\nLine three", dest)
        doc = parse_odt_strict(str(dest))
        assert len(doc.paragraphs) == 3

    def test_from_text_skips_empty_lines(self, tmp_path):
        dest = tmp_path / "out.odt"
        odt_from_text("Line one\n\nLine two", dest)
        doc = parse_odt_strict(str(dest))
        assert len(doc.paragraphs) == 2

    def test_from_text_round_trip(self, tmp_path):
        dest = tmp_path / "out.odt"
        original = "Hello World\nSecond Paragraph"
        odt_from_text(original, dest)
        doc = parse_odt_strict(str(dest))
        texts = [p.text for p in doc.paragraphs]
        assert "Hello World" in texts
        assert "Second Paragraph" in texts


class TestOdtFromModel:
    def test_from_list(self, tmp_path):
        dest = tmp_path / "out.odt"
        odt_from_model(["para1", "para2"], dest)
        doc = parse_odt_strict(str(dest))
        assert len(doc.paragraphs) == 2

    def test_from_dict_with_paragraphs(self, tmp_path):
        dest = tmp_path / "out.odt"
        model = {"paragraphs": ["one", "two", "three"]}
        odt_from_model(model, dest)
        doc = parse_odt_strict(str(dest))
        assert len(doc.paragraphs) == 3

    def test_from_odt_document(self, tmp_path):
        # Write then read then write back
        src = tmp_path / "src.odt"
        write_odt(["original paragraph"], src)
        odt_doc = parse_odt_strict(str(src))
        dest = tmp_path / "dest.odt"
        odt_from_model(odt_doc, dest)
        doc2 = parse_odt_strict(str(dest))
        assert len(doc2.paragraphs) == 1
        assert doc2.paragraphs[0].text == "original paragraph"

    def test_from_empty_model(self, tmp_path):
        dest = tmp_path / "out.odt"
        odt_from_model([], dest)
        assert dest.exists()
