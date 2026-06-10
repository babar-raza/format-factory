"""
test_r165_xcf_probe_layer_dims.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT29-001
Added: 2026-06-10

Tests for XCF probe_xcf, xcf_layer_count, xcf_image_dimensions, get_capabilities.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf.xcf_parser import (
    probe_xcf,
    xcf_layer_count,
    xcf_image_dimensions,
    get_capabilities,
    XcfError,
)

_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"


# ── get_capabilities ─────────────────────────────────────────────────────

class TestGetCapabilities:

    def test_returns_dict(self):
        result = get_capabilities()
        assert isinstance(result, dict)

    def test_format_is_xcf(self):
        assert get_capabilities()["format"] == "xcf"

    def test_gate_number(self):
        assert get_capabilities()["gate"] == 5

    def test_commercial_not_ready(self):
        assert get_capabilities()["commercial_product_ready"] is False

    def test_has_supported_list(self):
        result = get_capabilities()
        assert isinstance(result["supported"], list)
        assert len(result["supported"]) > 0

    def test_has_unsupported_list(self):
        result = get_capabilities()
        assert isinstance(result["unsupported"], list)


# ── probe_xcf ────────────────────────────────────────────────────────────

class TestProbeXcf:

    def test_valid_rgb(self):
        result = probe_xcf(_SAMPLES / "1x1-red-rgb.xcf")
        assert result["valid_header"] is True
        assert result["width"] == 1
        assert result["height"] == 1

    def test_valid_gray(self):
        result = probe_xcf(_SAMPLES / "2x2-gray.xcf")
        assert result["valid_header"] is True
        assert result["width"] == 2
        assert result["height"] == 2

    def test_valid_rgba(self):
        result = probe_xcf(_SAMPLES / "1x1-rgba-blue.xcf")
        assert result["valid_header"] is True

    def test_nonexistent_file(self):
        result = probe_xcf(_SAMPLES / "ghost.xcf")
        assert result["exists"] is False

    def test_has_version(self):
        result = probe_xcf(_SAMPLES / "1x1-red-rgb.xcf")
        assert "version" in result

    def test_has_image_type(self):
        result = probe_xcf(_SAMPLES / "1x1-red-rgb.xcf")
        assert "image_type" in result
        assert "image_type_name" in result

    def test_has_file_size(self):
        result = probe_xcf(_SAMPLES / "1x1-red-rgb.xcf")
        assert result["file_size"] > 0

    def test_too_short_file(self, tmp_path):
        p = tmp_path / "tiny.xcf"
        p.write_bytes(b"gimp")
        result = probe_xcf(p)
        assert result.get("valid_header") is False


# ── xcf_layer_count ──────────────────────────────────────────────────────

class TestXcfLayerCount:

    def test_1x1_rgb(self):
        count = xcf_layer_count(_SAMPLES / "1x1-red-rgb.xcf")
        assert isinstance(count, int)
        assert count >= 1

    def test_2x2_gray(self):
        count = xcf_layer_count(_SAMPLES / "2x2-gray.xcf")
        assert count >= 1

    def test_nonexistent_raises(self):
        with pytest.raises(XcfError):
            xcf_layer_count(_SAMPLES / "ghost.xcf")


# ── xcf_image_dimensions ─────────────────────────────────────────────────

class TestXcfImageDimensions:

    def test_1x1_rgb(self):
        dims = xcf_image_dimensions(_SAMPLES / "1x1-red-rgb.xcf")
        assert dims == {"width": 1, "height": 1}

    def test_2x2_gray(self):
        dims = xcf_image_dimensions(_SAMPLES / "2x2-gray.xcf")
        assert dims == {"width": 2, "height": 2}

    def test_1x1_rgba(self):
        dims = xcf_image_dimensions(_SAMPLES / "1x1-rgba-blue.xcf")
        assert dims == {"width": 1, "height": 1}

    def test_nonexistent_raises(self):
        with pytest.raises(XcfError):
            xcf_image_dimensions(_SAMPLES / "ghost.xcf")
