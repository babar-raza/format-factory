"""Sprint 451 — ZST deepening: compound analytics (primes 389, 139)."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

SAMPLE = _REPO / "samples" / "by-format" / "zst" / "valid" / "text-compressed.zst"

FN1 = "zst_compressed_mod_389_times_4150_plus_decompressed_times_169_plus_file_size_times_176"
FN2 = "zst_compressed_times_139_plus_decompressed_mod_850_times_740_plus_file_size_times_170"

FN1_EXPECTED = 1242582
FN2_EXPECTED = 372648


@pytest.fixture(scope="module")
def fn1():
    from src.python.zst import zst_compressed_mod_389_times_4150_plus_decompressed_times_169_plus_file_size_times_176 as f
    return f


@pytest.fixture(scope="module")
def fn2():
    from src.python.zst import zst_compressed_times_139_plus_decompressed_mod_850_times_740_plus_file_size_times_170 as f
    return f


class TestZstFn1:
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


class TestZstFn2:
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
