"""R558: PPM geometry properties — aspect_ratio, is_square, is_landscape, is_portrait.

Tests for PpmDocument geometry properties added in R558.
Spec refs: SAL-PPM-00001 (P3 magic), SAL-PPM-00002 (P6 magic).
"""

import pytest
from pathlib import Path
from ppm.models import PpmDocument

SAMPLES = Path("samples/by-format/ppm/valid")


class TestAspectRatio:
    def test_landscape_3x1_ratio(self):
        doc = PpmDocument.from_file(SAMPLES / "3x1-gradient.ppm")
        assert doc.aspect_ratio == pytest.approx(3.0)

    def test_square_2x2_ratio(self):
        doc = PpmDocument.from_file(SAMPLES / "2x2-rgbw.ppm")
        assert doc.aspect_ratio == pytest.approx(1.0)

    def test_square_1x1_ratio(self):
        doc = PpmDocument.from_file(SAMPLES / "1x1-red.ppm")
        assert doc.aspect_ratio == pytest.approx(1.0)

    def test_aspect_ratio_type(self):
        doc = PpmDocument.from_file(SAMPLES / "3x1-gradient.ppm")
        assert isinstance(doc.aspect_ratio, float)

    def test_aspect_ratio_positive(self):
        doc = PpmDocument.from_file(SAMPLES / "2x2-rgbw.ppm")
        assert doc.aspect_ratio > 0


class TestIsSquare:
    def test_square_2x2(self):
        doc = PpmDocument.from_file(SAMPLES / "2x2-rgbw.ppm")
        assert doc.is_square is True

    def test_square_1x1(self):
        doc = PpmDocument.from_file(SAMPLES / "1x1-red.ppm")
        assert doc.is_square is True

    def test_landscape_not_square(self):
        doc = PpmDocument.from_file(SAMPLES / "3x1-gradient.ppm")
        assert doc.is_square is False

    def test_is_square_type(self):
        doc = PpmDocument.from_file(SAMPLES / "2x2-rgbw.ppm")
        assert isinstance(doc.is_square, bool)


class TestIsLandscape:
    def test_landscape_3x1(self):
        doc = PpmDocument.from_file(SAMPLES / "3x1-gradient.ppm")
        assert doc.is_landscape is True

    def test_square_not_landscape(self):
        doc = PpmDocument.from_file(SAMPLES / "2x2-rgbw.ppm")
        assert doc.is_landscape is False

    def test_square_1x1_not_landscape(self):
        doc = PpmDocument.from_file(SAMPLES / "1x1-red.ppm")
        assert doc.is_landscape is False

    def test_is_landscape_type(self):
        doc = PpmDocument.from_file(SAMPLES / "3x1-gradient.ppm")
        assert isinstance(doc.is_landscape, bool)


class TestIsPortrait:
    def test_landscape_not_portrait(self):
        doc = PpmDocument.from_file(SAMPLES / "3x1-gradient.ppm")
        assert doc.is_portrait is False

    def test_square_not_portrait(self):
        doc = PpmDocument.from_file(SAMPLES / "2x2-rgbw.ppm")
        assert doc.is_portrait is False

    def test_1x1_not_portrait(self):
        doc = PpmDocument.from_file(SAMPLES / "1x1-red.ppm")
        assert doc.is_portrait is False

    def test_is_portrait_type(self):
        doc = PpmDocument.from_file(SAMPLES / "3x1-gradient.ppm")
        assert isinstance(doc.is_portrait, bool)


class TestGeometryConsistency:
    def test_landscape_mutual_exclusion(self):
        doc = PpmDocument.from_file(SAMPLES / "3x1-gradient.ppm")
        assert doc.is_landscape
        assert not doc.is_portrait
        assert not doc.is_square

    def test_square_mutual_exclusion(self):
        doc = PpmDocument.from_file(SAMPLES / "2x2-rgbw.ppm")
        assert doc.is_square
        assert not doc.is_landscape
        assert not doc.is_portrait

    def test_aspect_ratio_consistent_with_orientation(self):
        doc = PpmDocument.from_file(SAMPLES / "3x1-gradient.ppm")
        assert doc.is_landscape == (doc.aspect_ratio > 1.0)
