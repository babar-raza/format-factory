"""Roundtrip test for QOI: load sample, verify model, encode to file, reload, verify.

edit_operation: SetPixelColor
Proves: parse/load, domain model, same-format save (encode_qoi_to_file), reload.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from qoi.models import QoiDocument
from qoi.qoi_parser import parse_qoi_strict, QoiImage
from qoi.qoi_encoder import encode_qoi_to_file

_SAMPLE = _REPO / "samples" / "by-format" / "qoi" / "valid" / "1x1-red.qoi"
_SAMPLE_2X2 = _REPO / "samples" / "by-format" / "qoi" / "valid" / "2x2-black.qoi"


class TestQoiSampleRoundtrip:
    """Roundtrip: load from sample → verify model → encode to file → reload → verify."""

    @pytest.mark.roundtrip
    def test_from_file_loads_sample(self):
        doc = QoiDocument.from_file(_SAMPLE)
        assert doc.spec_qname == "qoi:image"
        assert doc.width == 1
        assert doc.height == 1

    @pytest.mark.roundtrip
    def test_spec_qname_matches_registry(self):
        assert QoiDocument.spec_qname == "qoi:image"
        assert QoiDocument.spec_fact_ref == "SAL-QOI-00001"

    @pytest.mark.roundtrip
    def test_sample_model_typed_properties(self):
        doc = QoiDocument.from_file(_SAMPLE)
        assert isinstance(doc.width, int)
        assert isinstance(doc.height, int)
        assert isinstance(doc.channels, int)
        assert isinstance(doc.pixel_count, int)
        assert doc.pixel_count == doc.width * doc.height

    @pytest.mark.roundtrip
    def test_to_dict_keys(self):
        doc = QoiDocument.from_file(_SAMPLE)
        d = doc.to_dict()
        assert "width" in d
        assert "height" in d
        assert "channels" in d
        assert "colorspace" in d

    @pytest.mark.roundtrip
    def test_encode_and_reload_preserves_dimensions(self, tmp_path):
        """Roundtrip: load → encode to file → reload via from_file → verify dimensions."""
        original = parse_qoi_strict(_SAMPLE_2X2)
        dest = tmp_path / "roundtrip.qoi"
        encode_qoi_to_file(original, dest)

        reloaded = QoiDocument.from_file(dest)
        assert reloaded.spec_qname == "qoi:image"
        assert reloaded.width == original.width
        assert reloaded.height == original.height
        assert reloaded.channels == original.channels

    @pytest.mark.roundtrip
    def test_edit_operation_set_pixel_color(self, tmp_path):
        """Edit: load sample, replace first pixel with green, encode, reload, verify."""
        original = parse_qoi_strict(_SAMPLE)
        pixels = list(original.pixels)

        # Replace first pixel with green (RGBA)
        if original.channels == 4:
            pixels[0] = (0, 255, 0, 255)
        else:
            pixels[0] = (0, 255, 0)

        modified = QoiImage(
            width=original.width,
            height=original.height,
            channels=original.channels,
            colorspace=original.colorspace,
            pixels=pixels,
            path=str(tmp_path / "edited.qoi"),
        )
        dest = tmp_path / "edited.qoi"
        encode_qoi_to_file(modified, dest)

        reloaded_raw = parse_qoi_strict(dest)
        reloaded_doc = QoiDocument.from_file(dest)
        assert reloaded_doc.spec_qname == "qoi:image"
        assert reloaded_raw.pixels[0][1] == 255  # green channel
        assert reloaded_doc.width == original.width
