"""Core tests for the xliff codec — probe, load, write, roundtrip."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from xliff.xliff_codec import (
    get_file_count,
    get_unit_count,
    load_xliff,
    probe_xliff,
    roundtrip,
    write_xliff,
    xliff_installed_workflow,
)
from xliff.exceptions import XliffParseError
from xliff.models import XliffDocument

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "xliff"
VALID_DIR = SAMPLES / "valid"
INVALID_DIR = SAMPLES / "invalid"


class TestProbe:
    def test_probe_valid_minimal(self):
        assert probe_xliff(VALID_DIR / "minimal.xliff") is True

    def test_probe_valid_multi_unit(self):
        assert probe_xliff(VALID_DIR / "multi-unit.xliff") is True

    def test_probe_valid_with_inline_codes(self):
        assert probe_xliff(VALID_DIR / "with-inline-codes.xliff") is True

    def test_probe_invalid_missing_namespace(self):
        assert probe_xliff(INVALID_DIR / "missing-namespace.xliff") is False

    def test_probe_nonexistent_file(self):
        assert probe_xliff("/nonexistent/file.xliff") is False

    def test_probe_random_bytes(self):
        assert probe_xliff(b"not xml at all") is False

    def test_probe_empty(self):
        assert probe_xliff(b"") is False

    def test_probe_xml_without_xliff_ns(self):
        assert probe_xliff(b'<?xml version="1.0"?><root/>') is False


class TestLoad:
    def test_load_minimal(self):
        model = load_xliff(VALID_DIR / "minimal.xliff")
        assert isinstance(model, dict)
        assert "version" in model
        assert "files" in model
        assert len(model["files"]) >= 1

    def test_load_multi_unit(self):
        model = load_xliff(VALID_DIR / "multi-unit.xliff")
        total_units = sum(len(f.get("units", [])) for f in model["files"])
        assert total_units >= 2

    def test_load_units_have_segments(self):
        model = load_xliff(VALID_DIR / "minimal.xliff")
        for f in model["files"]:
            for unit in f["units"]:
                assert "segments" in unit
                for seg in unit["segments"]:
                    assert "source" in seg

    def test_load_invalid_raises(self):
        with pytest.raises(XliffParseError):
            load_xliff(INVALID_DIR / "missing-namespace.xliff")

    def test_load_bad_xml_raises(self):
        with pytest.raises(XliffParseError, match="Invalid XML"):
            load_xliff(b"<not>closed xml")

    def test_load_from_bytes(self):
        xml = (
            b'<?xml version="1.0"?>'
            b'<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en">'
            b'<file id="f1"><unit id="u1"><segment><source>Hello</source>'
            b'<target>Hola</target></segment></unit></file></xliff>'
        )
        model = load_xliff(xml)
        assert model["version"] == "2.0"
        assert model["files"][0]["units"][0]["segments"][0]["source"] == "Hello"


class TestWrite:
    def test_write_returns_xml_string(self):
        model = {
            "version": "2.0",
            "source_language": "en",
            "target_language": "fr",
            "files": [{"id": "f1", "units": [
                {"id": "u1", "segments": [{"source": "Hello", "target": "Bonjour"}]}
            ]}],
        }
        result = write_xliff(model)
        assert "xliff" in result
        assert "Hello" in result
        assert "Bonjour" in result

    def test_write_to_file(self):
        model = {
            "version": "2.0",
            "source_language": "en",
            "files": [{"id": "f1", "units": [
                {"id": "u1", "segments": [{"source": "Test", "target": ""}]}
            ]}],
        }
        with tempfile.NamedTemporaryFile(suffix=".xliff", delete=False) as f:
            dest = f.name
        try:
            write_xliff(model, dest)
            content = Path(dest).read_text(encoding="utf-8")
            assert "Test" in content
        finally:
            Path(dest).unlink(missing_ok=True)


class TestRoundtrip:
    def test_roundtrip_minimal(self):
        with tempfile.NamedTemporaryFile(suffix=".xliff", delete=False) as f:
            dest = f.name
        try:
            original = load_xliff(VALID_DIR / "minimal.xliff")
            reloaded = roundtrip(VALID_DIR / "minimal.xliff", dest)
            assert len(original["files"]) == len(reloaded["files"])
        finally:
            Path(dest).unlink(missing_ok=True)


class TestHelpers:
    def test_get_unit_count(self):
        model = {"files": [{"units": [{"id": "1"}, {"id": "2"}]}, {"units": [{"id": "3"}]}]}
        assert get_unit_count(model) == 3

    def test_get_file_count(self):
        model = {"files": [{}, {}]}
        assert get_file_count(model) == 2


class TestModel:
    def test_xliff_document(self):
        data = {
            "version": "2.0",
            "source_language": "en",
            "target_language": "de",
            "files": [{"units": [
                {"segments": [{"source": "Hello", "target": "Hallo"}]},
                {"segments": [{"source": "World", "target": "Welt"}]},
            ]}],
        }
        doc = XliffDocument(data)
        assert doc.version == "2.0"
        assert doc.unit_count == 2
        assert doc.file_count == 1
        assert not doc.is_empty


class TestImport:
    def test_import_probe_load(self):
        from xliff import probe, load
        assert callable(probe)
        assert callable(load)

    def test_import_write(self):
        from xliff import write
        assert callable(write)

    def test_installed_workflow(self):
        xml = (
            b'<?xml version="1.0"?>'
            b'<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en">'
            b'<file id="f1"><unit id="u1"><segment><source>Hi</source>'
            b'<target></target></segment></unit></file></xliff>'
        )
        result = xliff_installed_workflow(xml)
        assert result["format"] == "xliff"
        assert result["loaded"] is True
