"""Tests for pbm_column_black_counts and pbm_white_density (Sprint 21)."""
import pytest
from src.python.pbm import write_pbm, pbm_column_black_counts, pbm_white_density


@pytest.fixture
def tmp_pbm(tmp_path):
    def _make(pixels, width, height):
        p = tmp_path / "test.pbm"
        write_pbm(pixels, width, height, str(p))
        return str(p)
    return _make


class TestPbmColumnBlackCounts:
    def test_all_black(self, tmp_pbm):
        path = tmp_pbm([1, 1, 1, 1], 2, 2)
        assert pbm_column_black_counts(path) == [2, 2]

    def test_all_white(self, tmp_pbm):
        path = tmp_pbm([0, 0, 0, 0], 2, 2)
        assert pbm_column_black_counts(path) == [0, 0]

    def test_mixed(self, tmp_pbm):
        path = tmp_pbm([1, 0, 0, 1], 2, 2)
        assert pbm_column_black_counts(path) == [1, 1]

    def test_single_column(self, tmp_pbm):
        path = tmp_pbm([1, 0, 1], 1, 3)
        assert pbm_column_black_counts(path) == [2]

    def test_return_type(self, tmp_pbm):
        path = tmp_pbm([0, 0], 2, 1)
        assert isinstance(pbm_column_black_counts(path), list)


class TestPbmWhiteDensity:
    def test_all_white(self, tmp_pbm):
        path = tmp_pbm([0, 0, 0, 0], 2, 2)
        assert pbm_white_density(path) == 1.0

    def test_all_black(self, tmp_pbm):
        path = tmp_pbm([1, 1, 1, 1], 2, 2)
        assert pbm_white_density(path) == 0.0

    def test_half_and_half(self, tmp_pbm):
        path = tmp_pbm([1, 0, 1, 0], 2, 2)
        assert pbm_white_density(path) == pytest.approx(0.5)

    def test_return_type(self, tmp_pbm):
        path = tmp_pbm([0], 1, 1)
        assert isinstance(pbm_white_density(path), float)

    def test_range(self, tmp_pbm):
        path = tmp_pbm([1, 0], 2, 1)
        d = pbm_white_density(path)
        assert 0.0 <= d <= 1.0
