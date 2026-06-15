"""Tests for pbm_row_black_counts function."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm.pbm_parser import pbm_row_black_counts, write_pbm, PbmError


@pytest.fixture
def tmp_pbm(tmp_path):
    """Helper to write a PBM file from pixels."""
    def _make(pixels, width, height):
        p = tmp_path / "test.pbm"
        write_pbm(pixels, width, height, str(p))
        return str(p)
    return _make


class TestPbmRowBlackCounts:
    def test_all_white_image(self, tmp_pbm):
        path = tmp_pbm([0, 0, 0, 0], 2, 2)
        result = pbm_row_black_counts(path)
        assert result == [0, 0]

    def test_all_black_image(self, tmp_pbm):
        path = tmp_pbm([1, 1, 1, 1], 2, 2)
        result = pbm_row_black_counts(path)
        assert result == [2, 2]

    def test_checkerboard(self, tmp_pbm):
        pixels = [1, 0, 0, 1]
        path = tmp_pbm(pixels, 2, 2)
        result = pbm_row_black_counts(path)
        assert result == [1, 1]

    def test_single_row(self, tmp_pbm):
        path = tmp_pbm([1, 0, 1, 1, 0], 5, 1)
        result = pbm_row_black_counts(path)
        assert result == [3]

    def test_single_column(self, tmp_pbm):
        path = tmp_pbm([1, 0, 1], 1, 3)
        result = pbm_row_black_counts(path)
        assert result == [1, 0, 1]

    def test_first_row_all_black_rest_white(self, tmp_pbm):
        pixels = [1, 1, 1, 0, 0, 0, 0, 0, 0]
        path = tmp_pbm(pixels, 3, 3)
        result = pbm_row_black_counts(path)
        assert result == [3, 0, 0]

    def test_result_length_equals_height(self, tmp_pbm):
        path = tmp_pbm([0] * 20, 4, 5)
        result = pbm_row_black_counts(path)
        assert len(result) == 5

    def test_importable_from_package(self):
        from pbm import pbm_row_black_counts as fn
        assert callable(fn)
