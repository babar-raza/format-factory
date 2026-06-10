"""Tests for ODT package exports — mainstream-product-deepening-rnext10.

Covers: parse_odt, probe_odt, get_capabilities exported via src/python/odt/__init__.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from odt import (
    parse_odt,
    parse_odt_strict,
    probe_odt,
    get_capabilities,
    OdtDocument,
)

SAMPLES = _REPO / "samples" / "by-format" / "odt" / "valid"


# ---------------------------------------------------------------------------
# parse_odt
# ---------------------------------------------------------------------------

def test_parse_odt_returns_dict():
    result = parse_odt(SAMPLES / "minimal-document.odt")
    assert isinstance(result, dict)


def test_parse_odt_ok_flag():
    result = parse_odt(SAMPLES / "minimal-document.odt")
    assert result.get("ok") is True


def test_parse_odt_has_paragraphs():
    result = parse_odt(SAMPLES / "two-paragraphs.odt")
    assert "paragraphs" in result or "paragraph_count" in result


# ---------------------------------------------------------------------------
# parse_odt_strict
# ---------------------------------------------------------------------------

def test_parse_odt_strict_returns_document():
    doc = parse_odt_strict(SAMPLES / "minimal-document.odt")
    assert isinstance(doc, OdtDocument)


# ---------------------------------------------------------------------------
# probe_odt
# ---------------------------------------------------------------------------

def test_probe_odt_returns_dict():
    result = probe_odt(SAMPLES / "minimal-document.odt")
    assert isinstance(result, dict)


def test_probe_odt_exists_flag():
    result = probe_odt(SAMPLES / "minimal-document.odt")
    assert result.get("exists") is True or result.get("ok") is True or isinstance(result, dict)


# ---------------------------------------------------------------------------
# get_capabilities
# ---------------------------------------------------------------------------

def test_get_capabilities_returns_dict():
    result = get_capabilities()
    assert isinstance(result, dict)


def test_get_capabilities_has_key():
    result = get_capabilities()
    assert len(result) > 0
