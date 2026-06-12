"""
test_odt_conveyor_deepening.py -- ODT product deepening tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-1
Tests parse, probe, capabilities for ODT parser.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_SAMPLES = _REPO / "samples" / "by-format" / "odt" / "valid"

from odt.odt_parser import (
    parse_odt,
    parse_odt_strict,
    probe_odt,
    get_capabilities,
    OdtDocument,
)


def test_parse_odt_minimal():
    result = parse_odt(str(_SAMPLES / "minimal-document.odt"))
    assert result["ok"] is True


def test_parse_odt_strict_returns_document():
    doc = parse_odt_strict(str(_SAMPLES / "minimal-document.odt"))
    assert isinstance(doc, OdtDocument)


def test_parse_odt_two_paragraphs():
    result = parse_odt(str(_SAMPLES / "two-paragraphs.odt"))
    assert result["ok"] is True
    assert result["paragraph_count"] >= 2


def test_parse_odt_unicode():
    result = parse_odt(str(_SAMPLES / "unicode-text.odt"))
    assert result["ok"] is True


def test_probe_odt_valid_container():
    info = probe_odt(str(_SAMPLES / "minimal-document.odt"))
    assert info["valid_container"] is True
    assert info["mimetype"] == "application/vnd.oasis.opendocument.text"


def test_probe_odt_nonexistent():
    info = probe_odt("/nonexistent/file.odt")
    assert info["exists"] is False


def test_capabilities():
    caps = get_capabilities()
    assert caps["format"] == "odt"
    assert "paragraph_extraction" in caps["supported"]


def test_parse_odt_bad_file(tmp_path):
    fp = tmp_path / "bad.odt"
    fp.write_bytes(b"not a zip")
    result = parse_odt(str(fp))
    assert result["ok"] is False


def test_strict_parse_has_elements():
    doc = parse_odt_strict(str(_SAMPLES / "two-paragraphs.odt"))
    assert len(doc.elements) >= 2


def test_headings_extraction():
    doc = parse_odt_strict(str(_SAMPLES / "minimal-document.odt"))
    assert isinstance(doc.headings, list)
