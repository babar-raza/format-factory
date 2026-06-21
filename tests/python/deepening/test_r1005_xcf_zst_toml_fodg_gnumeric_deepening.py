"""Sprint 452 — FODG deepening: compound analytics (primes 509, 163)."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

SAMPLE = _REPO / "samples" / "by-format" / "fodg" / "empty-page.fodg"

FN1 = "fodg_file_size_mod_509_times_295_plus_shape_times_17200_plus_text_times_16800_plus_page_times_15100"
FN2 = "fodg_file_size_times_163_plus_shape_times_68_plus_text_times_67_plus_page_times_68"

FN1_EXPECTED = 25425
FN2_EXPECTED = 171707


@pytest.fixture(scope="module")
def fn1():
    from src.python.fodg import fodg_file_size_mod_509_times_295_plus_shape_times_17200_plus_text_times_16800_plus_page_times_15100 as f
    return f


@pytest.fixture(scope="module")
def fn2():
    from src.python.fodg import fodg_file_size_times_163_plus_shape_times_68_plus_text_times_67_plus_page_times_68 as f
    return f


class TestFodgFn1:
    def test_returns_int(self, fn1):
        assert isinstance(fn1(SAMPLE), int)

    def test_expected_value(self, fn1):
        assert fn1(SAMPLE) == FN1_EXPECTED

    def test_positive(self, fn1):
        assert fn1(SAMPLE) >= 0

    def test_string_path(self, fn1):
        assert fn1(str(SAMPLE)) == FN1_EXPECTED

    def test_path_object(self, fn1):
        assert fn1(Path(SAMPLE)) == FN1_EXPECTED


class TestFodgFn2:
    def test_returns_int(self, fn2):
        assert isinstance(fn2(SAMPLE), int)

    def test_expected_value(self, fn2):
        assert fn2(SAMPLE) == FN2_EXPECTED

    def test_positive(self, fn2):
        assert fn2(SAMPLE) >= 0

    def test_string_path(self, fn2):
        assert fn2(str(SAMPLE)) == FN2_EXPECTED

    def test_path_object(self, fn2):
        assert fn2(Path(SAMPLE)) == FN2_EXPECTED
