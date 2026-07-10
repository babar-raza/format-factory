"""Tests for QoiDocument mutation API: set_pixel() and save_to_file().

Sprint: QOI-PYTHON-MUTATION-001
"""
import tempfile
from pathlib import Path

import pytest

from qoi.models import QoiDocument
from qoi.qoi_parser import QoiError


SAMPLE_QOI = Path("samples/by-format/qoi/valid/2x2-black.qoi")


class TestSetPixel:
    def test_set_pixel_rgba(self):
        doc = QoiDocument.from_file(SAMPLE_QOI)
        doc.set_pixel(0, (10, 20, 30, 255))
        assert doc._parsed.pixels[0] == (10, 20, 30, 255)

    def test_set_pixel_rgb(self):
        doc = QoiDocument.from_file(SAMPLE_QOI)
        doc.set_pixel(0, (10, 20, 30))
        assert doc._parsed.pixels[0] == (10, 20, 30)

    def test_set_pixel_out_of_range_raises(self):
        doc = QoiDocument.from_file(SAMPLE_QOI)
        with pytest.raises(QoiError):
            doc.set_pixel(999, (0, 0, 0, 255))

    def test_set_pixel_negative_raises(self):
        doc = QoiDocument.from_file(SAMPLE_QOI)
        with pytest.raises(QoiError):
            doc.set_pixel(-1, (0, 0, 0, 255))

    def test_set_pixel_bad_value_raises(self):
        doc = QoiDocument.from_file(SAMPLE_QOI)
        with pytest.raises(QoiError):
            doc.set_pixel(0, (0, 0))  # only 2 channels

    def test_set_pixel_preserves_others(self):
        doc = QoiDocument.from_file(SAMPLE_QOI)
        original = list(doc._parsed.pixels)
        doc.set_pixel(0, (1, 2, 3, 4))
        assert doc._parsed.pixels[1:] == original[1:]


class TestSaveToFile:
    def test_save_creates_file(self):
        doc = QoiDocument.from_file(SAMPLE_QOI)
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.qoi"
            doc.save_to_file(dest)
            assert dest.exists()

    def test_save_empty_path_raises(self):
        doc = QoiDocument.from_file(SAMPLE_QOI)
        with pytest.raises(QoiError):
            doc.save_to_file("")

    def test_save_creates_parent_dirs(self):
        doc = QoiDocument.from_file(SAMPLE_QOI)
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "sub" / "out.qoi"
            doc.save_to_file(dest)
            assert dest.exists()

    def test_save_file_is_nonzero(self):
        doc = QoiDocument.from_file(SAMPLE_QOI)
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.qoi"
            doc.save_to_file(dest)
            assert dest.stat().st_size > 0


class TestMutationRoundtrip:
    def test_set_pixel_roundtrip(self):
        """set_pixel → save_to_file → from_file: mutated pixel visible."""
        doc = QoiDocument.from_file(SAMPLE_QOI)
        doc.set_pixel(0, (11, 22, 33, 255))
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt.qoi"
            doc.save_to_file(dest)
            reloaded = QoiDocument.from_file(dest)
            assert reloaded._parsed.pixels[0] == (11, 22, 33, 255)

    def test_roundtrip_dimensions_preserved(self):
        doc = QoiDocument.from_file(SAMPLE_QOI)
        original_w, original_h = doc.width, doc.height
        doc.set_pixel(0, (5, 5, 5, 255))
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt2.qoi"
            doc.save_to_file(dest)
            reloaded = QoiDocument.from_file(dest)
            assert reloaded.width == original_w
            assert reloaded.height == original_h

    def test_roundtrip_pixel_count_preserved(self):
        doc = QoiDocument.from_file(SAMPLE_QOI)
        original_count = doc.pixel_count
        doc.set_pixel(0, (0, 0, 0, 255))
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt3.qoi"
            doc.save_to_file(dest)
            reloaded = QoiDocument.from_file(dest)
            assert reloaded.pixel_count == original_count
