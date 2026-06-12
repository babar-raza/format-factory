"""Tests for pbm_aspect_ratio — rnext62 product deepening."""
from pathlib import Path

PBM_DIR = Path("samples/by-format/pbm/valid")


def test_import():
    from src.python.pbm import pbm_aspect_ratio
    assert callable(pbm_aspect_ratio)


def test_square_image_returns_one():
    from src.python.pbm import pbm_aspect_ratio
    result = pbm_aspect_ratio(PBM_DIR / "2x2-checker.pbm")
    assert result == 1.0


def test_1x1_returns_one():
    from src.python.pbm import pbm_aspect_ratio
    result = pbm_aspect_ratio(PBM_DIR / "1x1-black.pbm")
    assert result == 1.0


def test_wide_image_returns_greater_than_one():
    from src.python.pbm import pbm_aspect_ratio
    result = pbm_aspect_ratio(PBM_DIR / "3x2-pattern.pbm")
    assert result == 1.5


def test_returns_float():
    from src.python.pbm import pbm_aspect_ratio
    result = pbm_aspect_ratio(PBM_DIR / "3x2-pattern.pbm")
    assert isinstance(result, float)


def test_all_samples_nonnegative():
    from src.python.pbm import pbm_aspect_ratio
    for fname in ["1x1-black.pbm", "2x2-checker.pbm", "3x2-pattern.pbm"]:
        result = pbm_aspect_ratio(PBM_DIR / fname)
        assert result >= 0.0
