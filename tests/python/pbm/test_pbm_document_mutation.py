"""Tests for PbmDocument mutation API: set_pixel() and save_to_file().

Sprint: PBM-PYTHON-MUTATION-001
"""
import tempfile
from pathlib import Path

import pytest

from pbm.models import PbmDocument
from pbm.pbm_parser import PbmError


SAMPLE_PBM = Path("samples/by-format/pbm/valid/2x2-checker.pbm")


class TestSetPixel:
    def test_set_pixel_value(self):
        doc = PbmDocument.from_file(SAMPLE_PBM)
        doc.set_pixel(0, 0)
        assert doc._parsed.pixels[0] == 0

    def test_set_pixel_out_of_range_raises(self):
        doc = PbmDocument.from_file(SAMPLE_PBM)
        with pytest.raises(PbmError):
            doc.set_pixel(999, 1)

    def test_set_pixel_negative_raises(self):
        doc = PbmDocument.from_file(SAMPLE_PBM)
        with pytest.raises(PbmError):
            doc.set_pixel(-1, 0)

    def test_set_pixel_preserves_others(self):
        doc = PbmDocument.from_file(SAMPLE_PBM)
        original = list(doc._parsed.pixels)
        doc.set_pixel(0, 0)
        assert doc._parsed.pixels[1:] == original[1:]

    def test_set_pixel_to_black(self):
        doc = PbmDocument.from_file(SAMPLE_PBM)
        doc.set_pixel(0, 1)
        assert doc._parsed.pixels[0] == 1


class TestSaveToFile:
    def test_save_creates_file(self):
        doc = PbmDocument.from_file(SAMPLE_PBM)
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.pbm"
            doc.save_to_file(dest)
            assert dest.exists()

    def test_save_empty_path_raises(self):
        doc = PbmDocument.from_file(SAMPLE_PBM)
        with pytest.raises(PbmError):
            doc.save_to_file("")

    def test_save_creates_parent_dirs(self):
        doc = PbmDocument.from_file(SAMPLE_PBM)
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "sub" / "out.pbm"
            doc.save_to_file(dest)
            assert dest.exists()

    def test_save_file_is_nonzero(self):
        doc = PbmDocument.from_file(SAMPLE_PBM)
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.pbm"
            doc.save_to_file(dest)
            assert dest.stat().st_size > 0


class TestMutationRoundtrip:
    def test_set_pixel_roundtrip(self):
        """set_pixel → save_to_file → from_file: mutated pixel visible."""
        doc = PbmDocument.from_file(SAMPLE_PBM)
        doc.set_pixel(0, 0)
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt.pbm"
            doc.save_to_file(dest)
            reloaded = PbmDocument.from_file(dest)
            assert reloaded._parsed.pixels[0] == 0

    def test_roundtrip_dimensions_preserved(self):
        doc = PbmDocument.from_file(SAMPLE_PBM)
        original_w, original_h = doc.width, doc.height
        doc.set_pixel(0, 1)
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt2.pbm"
            doc.save_to_file(dest)
            reloaded = PbmDocument.from_file(dest)
            assert reloaded.width == original_w
            assert reloaded.height == original_h

    def test_roundtrip_pixel_count_preserved(self):
        doc = PbmDocument.from_file(SAMPLE_PBM)
        original_count = doc.pixel_count
        doc.set_pixel(0, 0)
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt3.pbm"
            doc.save_to_file(dest)
            reloaded = PbmDocument.from_file(dest)
            assert reloaded.pixel_count == original_count
