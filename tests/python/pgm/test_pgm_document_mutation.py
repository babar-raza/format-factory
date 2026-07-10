"""Tests for PgmDocument mutation API: set_pixel() and save_to_file().

Sprint: PGM-PYTHON-MUTATION-001
"""
import tempfile
from pathlib import Path

import pytest

from pgm.models import PgmDocument
from pgm.pgm_parser import PgmError


SAMPLE_PGM = Path("samples/by-format/pgm/valid/2x2-gradient.pgm")


class TestSetPixel:
    def test_set_pixel_value(self):
        doc = PgmDocument.from_file(SAMPLE_PGM)
        doc.set_pixel(0, 128)
        assert doc._parsed.pixels[0] == 128

    def test_set_pixel_out_of_range_raises(self):
        doc = PgmDocument.from_file(SAMPLE_PGM)
        with pytest.raises(PgmError):
            doc.set_pixel(999, 0)

    def test_set_pixel_negative_raises(self):
        doc = PgmDocument.from_file(SAMPLE_PGM)
        with pytest.raises(PgmError):
            doc.set_pixel(-1, 0)

    def test_set_pixel_preserves_others(self):
        doc = PgmDocument.from_file(SAMPLE_PGM)
        original = list(doc._parsed.pixels)
        doc.set_pixel(0, 99)
        assert doc._parsed.pixels[1:] == original[1:]

    def test_set_pixel_to_zero(self):
        doc = PgmDocument.from_file(SAMPLE_PGM)
        doc.set_pixel(0, 0)
        assert doc._parsed.pixels[0] == 0


class TestSaveToFile:
    def test_save_creates_file(self):
        doc = PgmDocument.from_file(SAMPLE_PGM)
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.pgm"
            doc.save_to_file(dest)
            assert dest.exists()

    def test_save_empty_path_raises(self):
        doc = PgmDocument.from_file(SAMPLE_PGM)
        with pytest.raises(PgmError):
            doc.save_to_file("")

    def test_save_creates_parent_dirs(self):
        doc = PgmDocument.from_file(SAMPLE_PGM)
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "sub" / "out.pgm"
            doc.save_to_file(dest)
            assert dest.exists()

    def test_save_file_is_nonzero(self):
        doc = PgmDocument.from_file(SAMPLE_PGM)
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.pgm"
            doc.save_to_file(dest)
            assert dest.stat().st_size > 0


class TestMutationRoundtrip:
    def test_set_pixel_roundtrip(self):
        """set_pixel → save_to_file → from_file: mutated pixel visible."""
        doc = PgmDocument.from_file(SAMPLE_PGM)
        doc.set_pixel(0, 77)
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt.pgm"
            doc.save_to_file(dest)
            reloaded = PgmDocument.from_file(dest)
            assert reloaded._parsed.pixels[0] == 77

    def test_roundtrip_dimensions_preserved(self):
        doc = PgmDocument.from_file(SAMPLE_PGM)
        original_w, original_h = doc.width, doc.height
        doc.set_pixel(0, 50)
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt2.pgm"
            doc.save_to_file(dest)
            reloaded = PgmDocument.from_file(dest)
            assert reloaded.width == original_w
            assert reloaded.height == original_h

    def test_roundtrip_maxval_preserved(self):
        doc = PgmDocument.from_file(SAMPLE_PGM)
        original_maxval = doc.maxval
        doc.set_pixel(0, 0)
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt3.pgm"
            doc.save_to_file(dest)
            reloaded = PgmDocument.from_file(dest)
            assert reloaded.maxval == original_maxval
