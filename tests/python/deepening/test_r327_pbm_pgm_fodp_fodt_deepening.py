"""Sprint 97 — PBM/PGM/FODP/FODT cycle 7: 8 new analytics functions."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import pbm_white_row_count, pbm_diagonal_black_count
from src.python.pgm.pgm_parser import pgm_pixel_sum_normalized, pgm_midtone_pixel_count
from src.python.fodp.fodp_codec import fodp_slide_title_count, fodp_max_shape_count
from src.python.fodt.neutral_model import fodt_table_cell_count, fodt_section_depth_max

_PBM = _REPO / "samples" / "by-format" / "pbm" / "valid"
_PGM = _REPO / "samples" / "by-format" / "pgm" / "valid"
_FODP = _REPO / "samples" / "by-format" / "fodp"
_FODT = _REPO / "samples" / "by-format" / "fodt"


@pytest.fixture
def pbm_sample():
    return next(_PBM.glob("*.pbm"))


@pytest.fixture
def pgm_sample():
    return next(_PGM.glob("*.pgm"))


@pytest.fixture
def fodp_sample():
    return next(_FODP.glob("*.fodp"))


@pytest.fixture
def fodt_sample():
    return next(_FODT.glob("*.fodt"))


# --- PBM ---

class TestPbmWhiteRowCount:
    def test_returns_int(self, pbm_sample):
        assert isinstance(pbm_white_row_count(pbm_sample), int)

    def test_non_negative(self, pbm_sample):
        assert pbm_white_row_count(pbm_sample) >= 0


class TestPbmDiagonalBlackCount:
    def test_returns_int(self, pbm_sample):
        assert isinstance(pbm_diagonal_black_count(pbm_sample), int)

    def test_non_negative(self, pbm_sample):
        assert pbm_diagonal_black_count(pbm_sample) >= 0


# --- PGM ---

class TestPgmPixelSumNormalized:
    def test_returns_float(self, pgm_sample):
        assert isinstance(pgm_pixel_sum_normalized(pgm_sample), (int, float))

    def test_bounded(self, pgm_sample):
        val = pgm_pixel_sum_normalized(pgm_sample)
        assert 0.0 <= val <= 1.0


class TestPgmMidtonePixelCount:
    def test_returns_int(self, pgm_sample):
        assert isinstance(pgm_midtone_pixel_count(pgm_sample), int)

    def test_non_negative(self, pgm_sample):
        assert pgm_midtone_pixel_count(pgm_sample) >= 0


# --- FODP ---

class TestFodpSlideTitleCount:
    def test_returns_int(self, fodp_sample):
        assert isinstance(fodp_slide_title_count(fodp_sample), int)

    def test_non_negative(self, fodp_sample):
        assert fodp_slide_title_count(fodp_sample) >= 0


class TestFodpMaxShapeCount:
    def test_returns_int(self, fodp_sample):
        assert isinstance(fodp_max_shape_count(fodp_sample), int)

    def test_non_negative(self, fodp_sample):
        assert fodp_max_shape_count(fodp_sample) >= 0


# --- FODT ---

class TestFodtTableCellCount:
    def test_returns_int(self, fodt_sample):
        assert isinstance(fodt_table_cell_count(fodt_sample), int)

    def test_non_negative(self, fodt_sample):
        assert fodt_table_cell_count(fodt_sample) >= 0


class TestFodtSectionDepthMax:
    def test_returns_int(self, fodt_sample):
        assert isinstance(fodt_section_depth_max(fodt_sample), int)

    def test_non_negative(self, fodt_sample):
        assert fodt_section_depth_max(fodt_sample) >= 0
