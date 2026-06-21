"""Sprint 101 — PBM/PGM/FODP/FODT cycle 8: 8 new analytics functions."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

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


# ── PBM ──

def test_pbm_corner_pixel_sum_importable():
    from src.python.pbm import pbm_corner_pixel_sum
    assert callable(pbm_corner_pixel_sum)


def test_pbm_corner_pixel_sum_returns_int(pbm_sample):
    from src.python.pbm import pbm_corner_pixel_sum
    result = pbm_corner_pixel_sum(pbm_sample)
    assert isinstance(result, int)
    assert 0 <= result <= 4


def test_pbm_checkerboard_score_importable():
    from src.python.pbm import pbm_checkerboard_score
    assert callable(pbm_checkerboard_score)


def test_pbm_checkerboard_score_returns_float(pbm_sample):
    from src.python.pbm import pbm_checkerboard_score
    result = pbm_checkerboard_score(pbm_sample)
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


# ── PGM ──

def test_pgm_pixel_range_importable():
    from src.python.pgm import pgm_pixel_range
    assert callable(pgm_pixel_range)


def test_pgm_pixel_range_returns_int(pgm_sample):
    from src.python.pgm import pgm_pixel_range
    result = pgm_pixel_range(pgm_sample)
    assert isinstance(result, int)
    assert result >= 0


def test_pgm_shadow_pixel_count_importable():
    from src.python.pgm import pgm_shadow_pixel_count
    assert callable(pgm_shadow_pixel_count)


def test_pgm_shadow_pixel_count_returns_int(pgm_sample):
    from src.python.pgm import pgm_shadow_pixel_count
    result = pgm_shadow_pixel_count(pgm_sample)
    assert isinstance(result, int)
    assert result >= 0


# ── FODP ──

def test_fodp_min_shape_count_importable():
    from src.python.fodp import fodp_min_shape_count
    assert callable(fodp_min_shape_count)


def test_fodp_min_shape_count_returns_int(fodp_sample):
    from src.python.fodp import fodp_min_shape_count
    result = fodp_min_shape_count(fodp_sample)
    assert isinstance(result, int)
    assert result >= 0


def test_fodp_note_count_importable():
    from src.python.fodp import fodp_note_count
    assert callable(fodp_note_count)


def test_fodp_note_count_returns_int(fodp_sample):
    from src.python.fodp import fodp_note_count
    result = fodp_note_count(fodp_sample)
    assert isinstance(result, int)
    assert result >= 0


# ── FODT ──

def test_fodt_list_block_count_importable():
    from src.python.fodt import fodt_list_block_count
    assert callable(fodt_list_block_count)


def test_fodt_list_block_count_returns_int(fodt_sample):
    from src.python.fodt import fodt_list_block_count
    result = fodt_list_block_count(fodt_sample)
    assert isinstance(result, int)
    assert result >= 0


def test_fodt_text_block_ratio_importable():
    from src.python.fodt import fodt_text_block_ratio
    assert callable(fodt_text_block_ratio)


def test_fodt_text_block_ratio_returns_float(fodt_sample):
    from src.python.fodt import fodt_text_block_ratio
    result = fodt_text_block_ratio(fodt_sample)
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


# ── Cross-format ──

def test_all_eight_functions_callable():
    """Verify all 8 Sprint 101 functions are importable."""
    from src.python.pbm import pbm_corner_pixel_sum, pbm_checkerboard_score
    from src.python.pgm import pgm_pixel_range, pgm_shadow_pixel_count
    from src.python.fodp import fodp_min_shape_count, fodp_note_count
    from src.python.fodt import fodt_list_block_count, fodt_text_block_ratio
    for fn in [
        pbm_corner_pixel_sum, pbm_checkerboard_score,
        pgm_pixel_range, pgm_shadow_pixel_count,
        fodp_min_shape_count, fodp_note_count,
        fodt_list_block_count, fodt_text_block_ratio,
    ]:
        assert callable(fn)
