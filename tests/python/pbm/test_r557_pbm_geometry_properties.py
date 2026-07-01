"""Tests for PBM PbmDocument geometry properties — R557 FOSS-NETPBM object model.

Spec refs:
  FACT-PBM-001: PBM ASCII format starts with magic 'P1' (structure implies width/height fields)
  FACT-PBM-002: PBM binary format starts with magic 'P4'

New properties tested:
  aspect_ratio: float — width / height
  is_square: bool — width == height
  is_landscape: bool — width > height
  is_portrait: bool — height > width
"""
from __future__ import annotations

from pathlib import Path

import pytest

SAMPLES = Path(__file__).parent.parent.parent.parent / "samples" / "by-format" / "pbm" / "valid"
PBM_3X2 = SAMPLES / "3x2-pattern.pbm"   # landscape
PBM_1X1 = SAMPLES / "1x1-black.pbm"    # square
PBM_2X2 = SAMPLES / "2x2-checker.pbm"  # square


def _doc(path: Path):
    from pbm.models import PbmDocument
    return PbmDocument.from_file(path)


# ---------------------------------------------------------------------------
# TestAspectRatio
# ---------------------------------------------------------------------------

class TestAspectRatio:
    def test_aspect_ratio_landscape(self):
        doc = _doc(PBM_3X2)
        assert doc.aspect_ratio == pytest.approx(1.5)

    def test_aspect_ratio_square(self):
        doc = _doc(PBM_1X1)
        assert doc.aspect_ratio == pytest.approx(1.0)

    def test_aspect_ratio_2x2_square(self):
        doc = _doc(PBM_2X2)
        assert doc.aspect_ratio == pytest.approx(1.0)

    def test_aspect_ratio_is_float(self):
        doc = _doc(PBM_3X2)
        assert isinstance(doc.aspect_ratio, float)

    def test_aspect_ratio_equals_width_over_height(self):
        doc = _doc(PBM_3X2)
        assert doc.aspect_ratio == doc.width / doc.height


# ---------------------------------------------------------------------------
# TestIsSquare
# ---------------------------------------------------------------------------

class TestIsSquare:
    def test_1x1_is_square(self):
        doc = _doc(PBM_1X1)
        assert doc.is_square is True

    def test_2x2_is_square(self):
        doc = _doc(PBM_2X2)
        assert doc.is_square is True

    def test_3x2_not_square(self):
        doc = _doc(PBM_3X2)
        assert doc.is_square is False

    def test_is_square_is_bool(self):
        doc = _doc(PBM_1X1)
        assert isinstance(doc.is_square, bool)


# ---------------------------------------------------------------------------
# TestIsLandscape
# ---------------------------------------------------------------------------

class TestIsLandscape:
    def test_3x2_is_landscape(self):
        doc = _doc(PBM_3X2)
        assert doc.is_landscape is True

    def test_1x1_not_landscape(self):
        doc = _doc(PBM_1X1)
        assert doc.is_landscape is False

    def test_2x2_not_landscape(self):
        doc = _doc(PBM_2X2)
        assert doc.is_landscape is False

    def test_is_landscape_is_bool(self):
        doc = _doc(PBM_3X2)
        assert isinstance(doc.is_landscape, bool)


# ---------------------------------------------------------------------------
# TestIsPortrait
# ---------------------------------------------------------------------------

class TestIsPortrait:
    def test_3x2_not_portrait(self):
        doc = _doc(PBM_3X2)
        assert doc.is_portrait is False

    def test_1x1_not_portrait(self):
        doc = _doc(PBM_1X1)
        assert doc.is_portrait is False

    def test_2x2_not_portrait(self):
        doc = _doc(PBM_2X2)
        assert doc.is_portrait is False

    def test_is_portrait_is_bool(self):
        doc = _doc(PBM_2X2)
        assert isinstance(doc.is_portrait, bool)


# ---------------------------------------------------------------------------
# TestGeometryConsistency
# ---------------------------------------------------------------------------

class TestGeometryConsistency:
    def test_landscape_and_portrait_mutually_exclusive_on_3x2(self):
        doc = _doc(PBM_3X2)
        assert doc.is_landscape != doc.is_portrait

    def test_square_is_neither_landscape_nor_portrait(self):
        doc = _doc(PBM_1X1)
        assert not doc.is_landscape
        assert not doc.is_portrait
        assert doc.is_square

    def test_exactly_one_shape_classification_per_image(self):
        for sample in [PBM_1X1, PBM_2X2, PBM_3X2]:
            doc = _doc(sample)
            classifications = [doc.is_square, doc.is_landscape, doc.is_portrait]
            assert sum(classifications) <= 1, f"{sample.name}: multiple shape classes"
