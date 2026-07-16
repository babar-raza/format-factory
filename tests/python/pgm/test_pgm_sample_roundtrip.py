"""Roundtrip test for PGM: load sample, check model, write modified image, reload, verify.

edit_operation: SetPixelGrayValue
Proves: parse/load, domain model, same-format save (write_pgm), reload verification.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pgm.models import PgmDocument
from pgm.pgm_parser import parse_pgm_strict, write_pgm

_SAMPLE = _REPO / "samples" / "by-format" / "pgm" / "valid" / "1x1-white.pgm"
_SAMPLE_2X2 = _REPO / "samples" / "by-format" / "pgm" / "valid" / "2x2-gradient.pgm"


class TestPgmSampleRoundtrip:
    """Roundtrip: load from sample → verify model → write modified → reload → verify."""

    @pytest.mark.roundtrip
    def test_from_file_loads_sample(self):
        doc = PgmDocument.from_file(_SAMPLE)
        assert doc.spec_qname == "pgm:image"
        assert doc.width == 1
        assert doc.height == 1

    @pytest.mark.roundtrip
    def test_spec_qname_matches_registry(self):
        assert PgmDocument.spec_qname == "pgm:image"
        assert PgmDocument.spec_fact_ref == "SAL-PGM-00001"

    @pytest.mark.roundtrip
    def test_sample_model_typed_properties(self):
        doc = PgmDocument.from_file(_SAMPLE_2X2)
        assert isinstance(doc.width, int)
        assert isinstance(doc.height, int)
        assert isinstance(doc.maxval, int)
        assert isinstance(doc.pixel_count, int)
        assert doc.pixel_count == doc.width * doc.height

    @pytest.mark.roundtrip
    def test_to_dict_keys(self):
        doc = PgmDocument.from_file(_SAMPLE)
        d = doc.to_dict()
        assert "width" in d
        assert "height" in d
        assert "maxval" in d
        assert "pixel_count" in d

    @pytest.mark.roundtrip
    def test_write_reload_preserves_dimensions(self, tmp_path):
        """Roundtrip: write 3x2 image → reload → verify width/height preserved."""
        dest = tmp_path / "roundtrip.pgm"
        pixels = [128, 64, 192, 32, 96, 160]  # 3x2
        write_pgm(pixels, width=3, height=2, maxval=255, file_path=dest)

        reloaded = PgmDocument.from_file(dest)
        assert reloaded.width == 3
        assert reloaded.height == 2
        assert reloaded.maxval == 255
        assert reloaded.pixel_count == 6

    @pytest.mark.roundtrip
    def test_edit_operation_set_pixel_gray_value(self, tmp_path):
        """Edit: load sample pixels, set first pixel to 0, save, reload, verify."""
        original = parse_pgm_strict(_SAMPLE_2X2)
        pixels = list(original.pixels)

        # Set first pixel to 0 (black)
        pixels[0] = 0
        dest = tmp_path / "edited.pgm"
        write_pgm(pixels, original.width, original.height, original.maxval, dest)

        reloaded_raw = parse_pgm_strict(dest)
        reloaded_doc = PgmDocument.from_file(dest)
        assert reloaded_doc.spec_qname == "pgm:image"
        assert reloaded_raw.pixels[0] == 0
        assert reloaded_doc.width == original.width
        assert reloaded_doc.height == original.height
