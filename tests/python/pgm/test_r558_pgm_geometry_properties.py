"""R558: PGM geometry properties — aspect_ratio, is_square, is_landscape, is_portrait.

Tests for PgmDocument geometry properties added in R558.
Spec refs: SAL-PGM-00001 (P2 magic), SAL-PGM-00002 (P5 magic).
"""

import pytest
from pathlib import Path
from pgm.models import PgmDocument

SAMPLES = Path("samples/by-format/pgm/valid")


class TestAspectRatio:
    def test_landscape_3x1_ratio(self):
        doc = PgmDocument.from_file(SAMPLES / "3x1-ramp.pgm")
        assert doc.aspect_ratio == pytest.approx(3.0)

    def test_square_2x2_ratio(self):
        doc = PgmDocument.from_file(SAMPLES / "2x2-gradient.pgm")
        assert doc.aspect_ratio == pytest.approx(1.0)

    def test_square_1x1_ratio(self):
        doc = PgmDocument.from_file(SAMPLES / "1x1-white.pgm")
        assert doc.aspect_ratio == pytest.approx(1.0)

    def test_aspect_ratio_type(self):
        doc = PgmDocument.from_file(SAMPLES / "3x1-ramp.pgm")
        assert isinstance(doc.aspect_ratio, float)

    def test_aspect_ratio_positive(self):
        doc = PgmDocument.from_file(SAMPLES / "2x2-gradient.pgm")
        assert doc.aspect_ratio > 0


class TestIsSquare:
    def test_square_2x2(self):
        doc = PgmDocument.from_file(SAMPLES / "2x2-gradient.pgm")
        assert doc.is_square is True

    def test_square_1x1(self):
        doc = PgmDocument.from_file(SAMPLES / "1x1-white.pgm")
        assert doc.is_square is True

    def test_landscape_not_square(self):
        doc = PgmDocument.from_file(SAMPLES / "3x1-ramp.pgm")
        assert doc.is_square is False

    def test_is_square_type(self):
        doc = PgmDocument.from_file(SAMPLES / "2x2-gradient.pgm")
        assert isinstance(doc.is_square, bool)


class TestIsLandscape:
    def test_landscape_3x1(self):
        doc = PgmDocument.from_file(SAMPLES / "3x1-ramp.pgm")
        assert doc.is_landscape is True

    def test_square_not_landscape(self):
        doc = PgmDocument.from_file(SAMPLES / "2x2-gradient.pgm")
        assert doc.is_landscape is False

    def test_square_1x1_not_landscape(self):
        doc = PgmDocument.from_file(SAMPLES / "1x1-white.pgm")
        assert doc.is_landscape is False

    def test_is_landscape_type(self):
        doc = PgmDocument.from_file(SAMPLES / "3x1-ramp.pgm")
        assert isinstance(doc.is_landscape, bool)


class TestIsPortrait:
    def test_landscape_not_portrait(self):
        doc = PgmDocument.from_file(SAMPLES / "3x1-ramp.pgm")
        assert doc.is_portrait is False

    def test_square_not_portrait(self):
        doc = PgmDocument.from_file(SAMPLES / "2x2-gradient.pgm")
        assert doc.is_portrait is False

    def test_1x1_not_portrait(self):
        doc = PgmDocument.from_file(SAMPLES / "1x1-white.pgm")
        assert doc.is_portrait is False

    def test_is_portrait_type(self):
        doc = PgmDocument.from_file(SAMPLES / "3x1-ramp.pgm")
        assert isinstance(doc.is_portrait, bool)


class TestGeometryConsistency:
    def test_landscape_mutual_exclusion(self):
        doc = PgmDocument.from_file(SAMPLES / "3x1-ramp.pgm")
        assert doc.is_landscape
        assert not doc.is_portrait
        assert not doc.is_square

    def test_square_mutual_exclusion(self):
        doc = PgmDocument.from_file(SAMPLES / "2x2-gradient.pgm")
        assert doc.is_square
        assert not doc.is_landscape
        assert not doc.is_portrait

    def test_aspect_ratio_consistent_with_orientation(self):
        doc = PgmDocument.from_file(SAMPLES / "3x1-ramp.pgm")
        assert doc.is_landscape == (doc.aspect_ratio > 1.0)
