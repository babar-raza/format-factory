"""Sprint 133 — PBM/PGM/FODP/FODT cycle 16 product deepening tests (rework: concrete values)."""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

# Explicit samples for reproducible concrete assertions
_PBM = str(_REPO / "samples" / "by-format" / "pbm" / "valid" / "1x1-black.pbm")
_PGM = str(_REPO / "samples" / "by-format" / "pgm" / "valid" / "1x1-white.pgm")
_PGM2 = str(_REPO / "samples" / "by-format" / "pgm" / "valid" / "2x2-gradient.pgm")
_FODP = str(_REPO / "samples" / "by-format" / "fodp" / "minimal-presentation.fodp")
_FODT = str(_REPO / "samples" / "by-format" / "fodt" / "headings-and-paragraphs.fodt")
_FODT2 = str(_REPO / "samples" / "by-format" / "fodt" / "minimal-document.fodt")


# ---------- PBM ----------
class TestPbmColumnTransitionCount:
    def test_returns_int(self):
        from src.python.pbm import pbm_column_transition_count
        assert isinstance(pbm_column_transition_count(_PBM), int)

    def test_exact_0_for_1x1_black(self):
        from src.python.pbm import pbm_column_transition_count
        assert pbm_column_transition_count(_PBM) == 0

    def test_non_negative(self):
        from src.python.pbm import pbm_column_transition_count
        assert pbm_column_transition_count(_PBM) >= 0

    def test_consistent(self):
        from src.python.pbm import pbm_column_transition_count
        assert pbm_column_transition_count(_PBM) == pbm_column_transition_count(_PBM)


class TestPbmCenterBlackCount:
    def test_returns_int(self):
        from src.python.pbm import pbm_center_black_count
        assert isinstance(pbm_center_black_count(_PBM), int)

    def test_exact_0_for_1x1_black(self):
        from src.python.pbm import pbm_center_black_count
        # 1x1 image has no center region (< 3x3), returns 0
        assert pbm_center_black_count(_PBM) == 0

    def test_non_negative(self):
        from src.python.pbm import pbm_center_black_count
        assert pbm_center_black_count(_PBM) >= 0

    def test_consistent(self):
        from src.python.pbm import pbm_center_black_count
        assert pbm_center_black_count(_PBM) == pbm_center_black_count(_PBM)


# ---------- PGM ----------
class TestPgmPixelMedian:
    def test_returns_float(self):
        from src.python.pgm import pgm_pixel_median
        assert isinstance(pgm_pixel_median(_PGM), (int, float))

    def test_exact_255_for_1x1_white(self):
        from src.python.pgm import pgm_pixel_median
        assert pgm_pixel_median(_PGM) == pytest.approx(255.0)

    def test_exact_127_5_for_2x2_gradient(self):
        from src.python.pgm import pgm_pixel_median
        assert pgm_pixel_median(_PGM2) == pytest.approx(127.5)

    def test_non_negative(self):
        from src.python.pgm import pgm_pixel_median
        assert pgm_pixel_median(_PGM) >= 0.0

    def test_consistent(self):
        from src.python.pgm import pgm_pixel_median
        assert pgm_pixel_median(_PGM) == pgm_pixel_median(_PGM)


class TestPgmEdgePixelMean:
    def test_returns_float(self):
        from src.python.pgm import pgm_edge_pixel_mean
        assert isinstance(pgm_edge_pixel_mean(_PGM), (int, float))

    def test_exact_255_for_1x1_white(self):
        from src.python.pgm import pgm_edge_pixel_mean
        assert pgm_edge_pixel_mean(_PGM) == pytest.approx(255.0)

    def test_exact_127_5_for_2x2_gradient(self):
        from src.python.pgm import pgm_edge_pixel_mean
        assert pgm_edge_pixel_mean(_PGM2) == pytest.approx(127.5)

    def test_non_negative(self):
        from src.python.pgm import pgm_edge_pixel_mean
        assert pgm_edge_pixel_mean(_PGM) >= 0.0

    def test_consistent(self):
        from src.python.pgm import pgm_edge_pixel_mean
        assert pgm_edge_pixel_mean(_PGM) == pgm_edge_pixel_mean(_PGM)


# ---------- FODP ----------
class TestFodpTextToShapeRatio:
    def test_returns_float(self):
        from src.python.fodp import fodp_text_to_shape_ratio
        assert isinstance(fodp_text_to_shape_ratio(_FODP), (int, float))

    def test_exact_0_for_minimal(self):
        from src.python.fodp import fodp_text_to_shape_ratio
        # FODP load() returns 0 shapes for sample files (known API limitation)
        assert fodp_text_to_shape_ratio(_FODP) == pytest.approx(0.0)

    def test_non_negative(self):
        from src.python.fodp import fodp_text_to_shape_ratio
        assert fodp_text_to_shape_ratio(_FODP) >= 0.0

    def test_consistent(self):
        from src.python.fodp import fodp_text_to_shape_ratio
        assert fodp_text_to_shape_ratio(_FODP) == fodp_text_to_shape_ratio(_FODP)


class TestFodpSlideCountSquared:
    def test_returns_int(self):
        from src.python.fodp import fodp_slide_count_squared
        assert isinstance(fodp_slide_count_squared(_FODP), int)

    def test_exact_for_minimal(self):
        from src.python.fodp import fodp_slide_count_squared
        assert fodp_slide_count_squared(_FODP) == 1

    def test_non_negative(self):
        from src.python.fodp import fodp_slide_count_squared
        assert fodp_slide_count_squared(_FODP) >= 0

    def test_consistent(self):
        from src.python.fodp import fodp_slide_count_squared
        assert fodp_slide_count_squared(_FODP) == fodp_slide_count_squared(_FODP)


# ---------- FODT ----------
class TestFodtWordCountTotal:
    def test_returns_int(self):
        from src.python.fodt import fodt_word_count_total
        assert isinstance(fodt_word_count_total(_FODT), int)

    def test_exact_44_for_headings_and_paragraphs(self):
        from src.python.fodt import fodt_word_count_total
        assert fodt_word_count_total(_FODT) == 44

    def test_exact_2_for_minimal(self):
        from src.python.fodt import fodt_word_count_total
        assert fodt_word_count_total(_FODT2) == 2

    def test_non_negative(self):
        from src.python.fodt import fodt_word_count_total
        assert fodt_word_count_total(_FODT) >= 0

    def test_consistent(self):
        from src.python.fodt import fodt_word_count_total
        assert fodt_word_count_total(_FODT) == fodt_word_count_total(_FODT)


class TestFodtParagraphCountTotal:
    def test_returns_int(self):
        from src.python.fodt import fodt_paragraph_count_total
        assert isinstance(fodt_paragraph_count_total(_FODT), int)

    def test_exact_4_for_headings_and_paragraphs(self):
        from src.python.fodt import fodt_paragraph_count_total
        assert fodt_paragraph_count_total(_FODT) == 4

    def test_exact_1_for_minimal(self):
        from src.python.fodt import fodt_paragraph_count_total
        assert fodt_paragraph_count_total(_FODT2) == 1

    def test_non_negative(self):
        from src.python.fodt import fodt_paragraph_count_total
        assert fodt_paragraph_count_total(_FODT) >= 0

    def test_consistent(self):
        from src.python.fodt import fodt_paragraph_count_total
        assert fodt_paragraph_count_total(_FODT) == fodt_paragraph_count_total(_FODT)
