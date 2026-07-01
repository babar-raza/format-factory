"""R559: QOI geometry properties — aspect_ratio, is_square, is_landscape, is_portrait.

Tests for QoiDocument geometry properties added in R559.
Spec refs: FACT-QOI-001 (header with width/height).
"""

import pytest
from pathlib import Path
from qoi.models import QoiDocument

SAMPLES = Path("samples/by-format/qoi/valid")


class TestAspectRatio:
    def test_landscape_4x1_ratio(self):
        doc = QoiDocument.from_file(SAMPLES / "4x1-gradient.qoi")
        assert doc.aspect_ratio == pytest.approx(4.0)

    def test_square_2x2_ratio(self):
        doc = QoiDocument.from_file(SAMPLES / "2x2-black.qoi")
        assert doc.aspect_ratio == pytest.approx(1.0)

    def test_square_1x1_ratio(self):
        doc = QoiDocument.from_file(SAMPLES / "1x1-red.qoi")
        assert doc.aspect_ratio == pytest.approx(1.0)

    def test_aspect_ratio_type(self):
        doc = QoiDocument.from_file(SAMPLES / "4x1-gradient.qoi")
        assert isinstance(doc.aspect_ratio, float)

    def test_aspect_ratio_positive(self):
        doc = QoiDocument.from_file(SAMPLES / "2x2-black.qoi")
        assert doc.aspect_ratio > 0


class TestIsSquare:
    def test_square_2x2(self):
        doc = QoiDocument.from_file(SAMPLES / "2x2-black.qoi")
        assert doc.is_square is True

    def test_square_1x1(self):
        doc = QoiDocument.from_file(SAMPLES / "1x1-red.qoi")
        assert doc.is_square is True

    def test_landscape_not_square(self):
        doc = QoiDocument.from_file(SAMPLES / "4x1-gradient.qoi")
        assert doc.is_square is False

    def test_is_square_type(self):
        doc = QoiDocument.from_file(SAMPLES / "2x2-black.qoi")
        assert isinstance(doc.is_square, bool)


class TestIsLandscape:
    def test_landscape_4x1(self):
        doc = QoiDocument.from_file(SAMPLES / "4x1-gradient.qoi")
        assert doc.is_landscape is True

    def test_square_not_landscape(self):
        doc = QoiDocument.from_file(SAMPLES / "2x2-black.qoi")
        assert doc.is_landscape is False

    def test_square_1x1_not_landscape(self):
        doc = QoiDocument.from_file(SAMPLES / "1x1-red.qoi")
        assert doc.is_landscape is False

    def test_is_landscape_type(self):
        doc = QoiDocument.from_file(SAMPLES / "4x1-gradient.qoi")
        assert isinstance(doc.is_landscape, bool)


class TestIsPortrait:
    def test_landscape_not_portrait(self):
        doc = QoiDocument.from_file(SAMPLES / "4x1-gradient.qoi")
        assert doc.is_portrait is False

    def test_square_not_portrait(self):
        doc = QoiDocument.from_file(SAMPLES / "2x2-black.qoi")
        assert doc.is_portrait is False

    def test_1x1_not_portrait(self):
        doc = QoiDocument.from_file(SAMPLES / "1x1-red.qoi")
        assert doc.is_portrait is False

    def test_is_portrait_type(self):
        doc = QoiDocument.from_file(SAMPLES / "4x1-gradient.qoi")
        assert isinstance(doc.is_portrait, bool)


class TestGeometryConsistency:
    def test_landscape_mutual_exclusion(self):
        doc = QoiDocument.from_file(SAMPLES / "4x1-gradient.qoi")
        assert doc.is_landscape
        assert not doc.is_portrait
        assert not doc.is_square

    def test_square_mutual_exclusion(self):
        doc = QoiDocument.from_file(SAMPLES / "2x2-black.qoi")
        assert doc.is_square
        assert not doc.is_landscape
        assert not doc.is_portrait

    def test_aspect_ratio_consistent_with_orientation(self):
        doc = QoiDocument.from_file(SAMPLES / "4x1-gradient.qoi")
        assert doc.is_landscape == (doc.aspect_ratio > 1.0)
