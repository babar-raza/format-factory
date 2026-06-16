"""Tests for product deepening: FODP, QOI, XCF new analytics functions.

Sprint: PRODUCT-DEEPENING-SPRINT8-20260616
Adds: fodp_nonempty_slide_count, fodp_text_to_slide_ratio,
      qoi_blue_dominant, qoi_green_dominant,
      xcf_perimeter, xcf_diagonal
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))


def _first_fodp():
    files = sorted((_REPO / "samples" / "by-format" / "fodp").glob("*.fodp"))
    assert files, "No FODP samples"
    return str(files[0])


def _first_qoi():
    files = sorted((_REPO / "samples" / "by-format" / "qoi" / "valid").glob("*.qoi"))
    assert files, "No QOI samples"
    return str(files[0])


def _first_xcf():
    files = sorted((_REPO / "samples" / "by-format" / "xcf" / "valid").glob("*.xcf"))
    assert files, "No XCF samples"
    return str(files[0])


# --- FODP ---

class TestFodpNonemptySlideCount:
    def test_returns_int(self):
        from fodp import fodp_nonempty_slide_count
        assert isinstance(fodp_nonempty_slide_count(_first_fodp()), int)

    def test_at_most_slide_count(self):
        from fodp import fodp_nonempty_slide_count, fodp_slide_count
        path = _first_fodp()
        assert fodp_nonempty_slide_count(path) <= fodp_slide_count(path)

    def test_nonnegative(self):
        from fodp import fodp_nonempty_slide_count
        assert fodp_nonempty_slide_count(_first_fodp()) >= 0


class TestFodpTextToSlideRatio:
    def test_returns_float(self):
        from fodp import fodp_text_to_slide_ratio
        assert isinstance(fodp_text_to_slide_ratio(_first_fodp()), float)

    def test_nonnegative(self):
        from fodp import fodp_text_to_slide_ratio
        assert fodp_text_to_slide_ratio(_first_fodp()) >= 0.0

    def test_consistent_with_density(self):
        from fodp import fodp_text_to_slide_ratio, fodp_slide_text_density
        path = _first_fodp()
        # Both compute text/slides, should be close
        ratio = fodp_text_to_slide_ratio(path)
        density = fodp_slide_text_density(path)
        assert abs(ratio - density) < 1.0  # Allow small float diff


# --- QOI ---

class TestQoiBlueDominant:
    def test_returns_bool(self):
        from qoi import qoi_blue_dominant
        assert isinstance(qoi_blue_dominant(_first_qoi()), bool)

    def test_consistent_with_avg_rgb(self):
        from qoi import qoi_blue_dominant, qoi_avg_rgb
        r, g, b = qoi_avg_rgb(_first_qoi())
        result = qoi_blue_dominant(_first_qoi())
        if b > r and b > g:
            assert result is True
        else:
            assert result is False


class TestQoiGreenDominant:
    def test_returns_bool(self):
        from qoi import qoi_green_dominant
        assert isinstance(qoi_green_dominant(_first_qoi()), bool)

    def test_at_most_one_dominant(self):
        from qoi import qoi_red_dominant, qoi_blue_dominant, qoi_green_dominant
        path = _first_qoi()
        dominants = [qoi_red_dominant(path), qoi_blue_dominant(path), qoi_green_dominant(path)]
        assert sum(dominants) <= 1  # At most one channel dominant


# --- XCF ---

class TestXcfPerimeter:
    def test_returns_int(self):
        from xcf import xcf_perimeter
        assert isinstance(xcf_perimeter(_first_xcf()), int)

    def test_positive(self):
        from xcf import xcf_perimeter
        assert xcf_perimeter(_first_xcf()) > 0

    def test_consistent_with_dimensions(self):
        from xcf import xcf_perimeter, xcf_width, xcf_height
        path = _first_xcf()
        assert xcf_perimeter(path) == 2 * (xcf_width(path) + xcf_height(path))


class TestXcfDiagonal:
    def test_returns_float(self):
        from xcf import xcf_diagonal
        assert isinstance(xcf_diagonal(_first_xcf()), float)

    def test_positive(self):
        from xcf import xcf_diagonal
        assert xcf_diagonal(_first_xcf()) > 0

    def test_pythagorean(self):
        import math
        from xcf import xcf_diagonal, xcf_width, xcf_height
        path = _first_xcf()
        expected = math.sqrt(xcf_width(path) ** 2 + xcf_height(path) ** 2)
        assert abs(xcf_diagonal(path) - expected) < 0.01
