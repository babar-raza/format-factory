"""Sample roundtrip test for XCF: load sample files, verify domain model properties.

XCF is a read-only format (no write support) — roundtrip proves parse/load
and domain model correctness from real sample files.

edit_operation: N/A (read-only format)
Proves: parse/load, domain model typed properties, spec_qname registry match.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf.models import XcfDocument

_SAMPLE_RGB = _REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-red-rgb.xcf"
_SAMPLE_RGBA = _REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-rgba-blue.xcf"
_SAMPLE_2X2 = _REPO / "samples" / "by-format" / "xcf" / "valid" / "2x2-gray.xcf"


class TestXcfSampleRoundtrip:
    """Load real XCF samples and verify typed domain model properties."""

    @pytest.mark.roundtrip
    def test_from_file_loads_rgb_sample(self):
        doc = XcfDocument.from_file(_SAMPLE_RGB)
        assert doc.spec_qname == "xcf:image"
        assert doc.width == 1
        assert doc.height == 1

    @pytest.mark.roundtrip
    def test_spec_qname_matches_registry(self):
        assert XcfDocument.spec_qname == "xcf:image"
        assert XcfDocument.spec_fact_ref == "SAL-XCF-00001"

    @pytest.mark.roundtrip
    def test_sample_model_typed_properties_rgb(self):
        doc = XcfDocument.from_file(_SAMPLE_RGB)
        assert isinstance(doc.width, int)
        assert isinstance(doc.height, int)
        assert isinstance(doc.layer_count, int)
        assert isinstance(doc.version, str)
        assert isinstance(doc.image_type, int)

    @pytest.mark.roundtrip
    def test_sample_model_typed_properties_rgba(self):
        doc = XcfDocument.from_file(_SAMPLE_RGBA)
        assert doc.spec_qname == "xcf:image"
        assert doc.width >= 1
        assert doc.height >= 1

    @pytest.mark.roundtrip
    def test_sample_2x2_dimensions(self):
        doc = XcfDocument.from_file(_SAMPLE_2X2)
        assert doc.width == 2
        assert doc.height == 2

    @pytest.mark.roundtrip
    def test_to_dict_keys(self):
        doc = XcfDocument.from_file(_SAMPLE_RGB)
        d = doc.to_dict()
        assert "width" in d
        assert "height" in d
        assert "layer_count" in d
        assert "version" in d
        assert "image_type" in d

    @pytest.mark.roundtrip
    def test_layer_names_is_list(self):
        doc = XcfDocument.from_file(_SAMPLE_RGB)
        assert isinstance(doc.layer_names, list)

    @pytest.mark.roundtrip
    def test_all_three_samples_load(self):
        """Verify all available XCF samples load successfully with correct spec_qname."""
        for sample in [_SAMPLE_RGB, _SAMPLE_RGBA, _SAMPLE_2X2]:
            doc = XcfDocument.from_file(sample)
            assert doc.spec_qname == "xcf:image"
            assert doc.width >= 1
            assert doc.height >= 1
