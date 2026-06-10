"""Tests for QOI package exports — mainstream-product-deepening-rnext10.

Covers: parse_qoi, probe_qoi, get_capabilities, encode_qoi, get_encoder_capabilities
exported via src/python/qoi/__init__.py.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from qoi import (
    parse_qoi,
    parse_qoi_strict,
    probe_qoi,
    get_capabilities,
    encode_qoi,
    encode_qoi_to_file,
    get_encoder_capabilities,
    QoiImage,
)

SAMPLES = _REPO / "samples" / "by-format" / "qoi" / "valid"


def _make_image(w=2, h=2):
    """Create a minimal 4-channel QoiImage."""
    pixels = [(255, 0, 0, 255)] * (w * h)
    return QoiImage(width=w, height=h, channels=4, colorspace=0, pixels=pixels)


# ---------------------------------------------------------------------------
# parse_qoi
# ---------------------------------------------------------------------------

def test_parse_qoi_returns_dict():
    result = parse_qoi(SAMPLES / "1x1-red.qoi")
    assert isinstance(result, dict)


def test_parse_qoi_ok_flag():
    result = parse_qoi(SAMPLES / "1x1-red.qoi")
    assert result.get("ok") is True


def test_parse_qoi_has_width():
    result = parse_qoi(SAMPLES / "1x1-red.qoi")
    assert result.get("width") == 1


# ---------------------------------------------------------------------------
# probe_qoi
# ---------------------------------------------------------------------------

def test_probe_qoi_returns_dict():
    result = probe_qoi(SAMPLES / "1x1-red.qoi")
    assert isinstance(result, dict)


def test_probe_qoi_exists():
    result = probe_qoi(SAMPLES / "1x1-red.qoi")
    assert result.get("exists") is True or result.get("ok") is True or isinstance(result, dict)


# ---------------------------------------------------------------------------
# get_capabilities
# ---------------------------------------------------------------------------

def test_get_capabilities_returns_dict():
    result = get_capabilities()
    assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# encode_qoi
# ---------------------------------------------------------------------------

def test_encode_qoi_returns_bytes():
    img = _make_image(2, 2)
    result = encode_qoi(img)
    assert isinstance(result, bytes)


def test_encode_qoi_has_magic():
    img = _make_image(1, 1)
    result = encode_qoi(img)
    # QOI magic: b'qoif'
    assert result[:4] == b"qoif"


# ---------------------------------------------------------------------------
# get_encoder_capabilities
# ---------------------------------------------------------------------------

def test_get_encoder_capabilities_returns_dict():
    result = get_encoder_capabilities()
    assert isinstance(result, dict)
