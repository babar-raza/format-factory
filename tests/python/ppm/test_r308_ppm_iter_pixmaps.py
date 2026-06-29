"""
tests/python/ppm/test_r308_ppm_iter_pixmaps.py

Sprint: ff-sprint-s308-ppm-pixmap-iterator-20260626
Authority: Netpbm format — PPM (Portable Pixmap) RGB pixel data

Tests for ppm_iter_pixmaps() in ppm_pixmap_iterator.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_VALID_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_MINIMAL = _VALID_DIR / "1x1-red.ppm"
_COLOR = _VALID_DIR / "2x2-rgbw.ppm"


class TestPpmIterPixmapsImport:
    def test_importable_from_ppm_pixmap_iterator(self):
        from ppm.ppm_pixmap_iterator import ppm_iter_pixmaps
        assert callable(ppm_iter_pixmaps)

    def test_importable_from_package(self):
        import ppm
        assert hasattr(ppm, "ppm_iter_pixmaps")


class TestPpmIterPixmapsOutput:
    def test_returns_iterator(self):
        from ppm.ppm_pixmap_iterator import ppm_iter_pixmaps
        result = ppm_iter_pixmaps(str(_MINIMAL))
        assert hasattr(result, "__iter__") and hasattr(result, "__next__")

    def test_minimal_yields_one_pixmap(self):
        from ppm.ppm_pixmap_iterator import ppm_iter_pixmaps
        pms = list(ppm_iter_pixmaps(str(_MINIMAL)))
        assert len(pms) == 1

    def test_pixmap_type_is_spec_pixmap(self):
        from ppm.ppm_pixmap_iterator import ppm_iter_pixmaps
        from ppm.spec.pixmap.pixmap import Pixmap
        pms = list(ppm_iter_pixmaps(str(_MINIMAL)))
        assert all(isinstance(p, Pixmap) for p in pms)

    def test_pixmap_has_spec_qname(self):
        from ppm.ppm_pixmap_iterator import ppm_iter_pixmaps
        pms = list(ppm_iter_pixmaps(str(_MINIMAL)))
        assert all(hasattr(p, "spec_qname") for p in pms)

    def test_pixmap_qname_value(self):
        from ppm.ppm_pixmap_iterator import ppm_iter_pixmaps
        pms = list(ppm_iter_pixmaps(str(_MINIMAL)))
        assert all(p.spec_qname == "ppm:pixmap" for p in pms)

    def test_pixmap_dimensions(self):
        from ppm.ppm_pixmap_iterator import ppm_iter_pixmaps
        pms = list(ppm_iter_pixmaps(str(_MINIMAL)))
        p = pms[0]
        assert p.width == 1 and p.height == 1

    def test_color_image_dimensions(self):
        from ppm.ppm_pixmap_iterator import ppm_iter_pixmaps
        pms = list(ppm_iter_pixmaps(str(_COLOR)))
        p = pms[0]
        assert p.width == 2 and p.height == 2

    def test_pixel_count(self):
        from ppm.ppm_pixmap_iterator import ppm_iter_pixmaps
        pms = list(ppm_iter_pixmaps(str(_MINIMAL)))
        p = pms[0]
        assert p.pixel_count == 1

    def test_consistent(self):
        from ppm.ppm_pixmap_iterator import ppm_iter_pixmaps
        r1 = [(p.width, p.height) for p in ppm_iter_pixmaps(str(_MINIMAL))]
        r2 = [(p.width, p.height) for p in ppm_iter_pixmaps(str(_MINIMAL))]
        assert r1 == r2
