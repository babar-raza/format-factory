"""Tests for pbm_row_count and pbm_has_any_black (Sprint 33)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pbm import write_pbm, pbm_row_count, pbm_has_any_black


def _make_pbm(tmp_path, name, w, h, pixels):
    p = tmp_path / f"{name}.pbm"
    write_pbm(pixels, w, h, str(p))
    return p


class TestPbmRowCount:
    def test_return_type(self, tmp_path):
        p = _make_pbm(tmp_path, "rt", 2, 3, [0] * 6)
        assert isinstance(pbm_row_count(p), int)

    def test_exact_height(self, tmp_path):
        p = _make_pbm(tmp_path, "eh", 4, 3, [0] * 12)
        assert pbm_row_count(p) == 3

    def test_single_row(self, tmp_path):
        p = _make_pbm(tmp_path, "sr", 5, 1, [0] * 5)
        assert pbm_row_count(p) == 1

    def test_square_image(self, tmp_path):
        p = _make_pbm(tmp_path, "sq", 4, 4, [0] * 16)
        assert pbm_row_count(p) == 4

    def test_nonnegative(self, tmp_path):
        p = _make_pbm(tmp_path, "nn", 2, 2, [1, 0, 1, 0])
        assert pbm_row_count(p) >= 0


class TestPbmHasAnyBlack:
    def test_return_type(self, tmp_path):
        p = _make_pbm(tmp_path, "rt2", 2, 2, [1, 0, 0, 0])
        assert isinstance(pbm_has_any_black(p), bool)

    def test_true_one_black(self, tmp_path):
        p = _make_pbm(tmp_path, "ob", 2, 2, [0, 0, 0, 1])
        assert pbm_has_any_black(p) is True

    def test_true_all_black(self, tmp_path):
        p = _make_pbm(tmp_path, "ab", 2, 2, [1, 1, 1, 1])
        assert pbm_has_any_black(p) is True

    def test_false_all_white(self, tmp_path):
        p = _make_pbm(tmp_path, "aw", 2, 2, [0, 0, 0, 0])
        assert pbm_has_any_black(p) is False

    def test_mixed_has_black(self, tmp_path):
        p = _make_pbm(tmp_path, "mx", 3, 1, [0, 1, 0])
        assert pbm_has_any_black(p) is True
