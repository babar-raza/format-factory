"""Sprint 453 — XCF deepening: compound analytics (primes 397, 157)."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

SAMPLE = _REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-rgba-blue.xcf"

FN1 = "xcf_file_size_mod_397_times_6600_plus_image_type_times_8600_plus_width_times_850_plus_height_times_820"
FN2 = "xcf_file_size_times_157_plus_image_type_times_10600_plus_width_times_height_times_5700"

FN1_EXPECTED = 1176470
FN2_EXPECTED = 33646


@pytest.fixture(scope="module")
def fn1():
    from src.python.xcf import xcf_file_size_mod_397_times_6600_plus_image_type_times_8600_plus_width_times_850_plus_height_times_820 as f
    return f


@pytest.fixture(scope="module")
def fn2():
    from src.python.xcf import xcf_file_size_times_157_plus_image_type_times_10600_plus_width_times_height_times_5700 as f
    return f


class TestXcfFn1:
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


class TestXcfFn2:
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
