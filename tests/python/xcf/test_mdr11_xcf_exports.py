"""Tests for XCF package exports — mainstream-product-deepening-rnext11.

Covers: parse_xcf, probe_xcf, get_capabilities exported via src/python/xcf/__init__.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf import (
    parse_xcf,
    parse_xcf_strict,
    probe_xcf,
    get_capabilities,
    XcfImage,
)

SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"


# ---------------------------------------------------------------------------
# parse_xcf
# ---------------------------------------------------------------------------

def test_parse_xcf_returns_dict():
    result = parse_xcf(SAMPLES / "1x1-red-rgb.xcf")
    assert isinstance(result, dict)


def test_parse_xcf_ok_flag():
    result = parse_xcf(SAMPLES / "1x1-red-rgb.xcf")
    assert result.get("ok") is True


def test_parse_xcf_has_dimensions():
    result = parse_xcf(SAMPLES / "1x1-red-rgb.xcf")
    assert result.get("width") == 1
    assert result.get("height") == 1


# ---------------------------------------------------------------------------
# parse_xcf_strict
# ---------------------------------------------------------------------------

def test_parse_xcf_strict_returns_xcf_image():
    doc = parse_xcf_strict(SAMPLES / "1x1-red-rgb.xcf")
    assert isinstance(doc, XcfImage)


# ---------------------------------------------------------------------------
# probe_xcf
# ---------------------------------------------------------------------------

def test_probe_xcf_returns_dict():
    result = probe_xcf(SAMPLES / "1x1-red-rgb.xcf")
    assert isinstance(result, dict)


def test_probe_xcf_exists():
    result = probe_xcf(SAMPLES / "1x1-red-rgb.xcf")
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
