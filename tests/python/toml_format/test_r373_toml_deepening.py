"""Tests for TOML product deepening sprint 145.

New functions:
  toml_key_length_range    — max key length minus min key length
  toml_bool_to_total_ratio — booleans / total top-level values
"""
import sys
import tempfile
import os
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.toml import toml_key_length_range, toml_bool_to_total_ratio

_MINIMAL = str(_REPO / "samples" / "by-format" / "toml" / "minimal.toml")

_EQUAL_KEYS = "a = 1\nb = 2\n"
_ALL_BOOLS = "x = true\ny = false\nz = true\n"


def _write_temp(content: str) -> str:
    f = tempfile.NamedTemporaryFile(suffix=".toml", mode="w", delete=False)
    f.write(content)
    f.close()
    return f.name


class TestTomlKeyLengthRange:
    def test_return_type(self):
        assert isinstance(toml_key_length_range(_MINIMAL), int)

    def test_exact_3_for_minimal(self):
        # minimal.toml: max key = "enabled" (7) or "version" (7) or "title" (5)... let's check
        # actually max=8 ("database"), min=5 ("title") → range=3
        assert toml_key_length_range(_MINIMAL) == 3

    def test_zero_for_equal_length_keys(self):
        # "a" and "b" are both length 1 → range=0
        tmp = _write_temp(_EQUAL_KEYS)
        try:
            assert toml_key_length_range(tmp) == 0
        finally:
            os.unlink(tmp)

    def test_nonnegative(self):
        assert toml_key_length_range(_MINIMAL) >= 0

    def test_consistent(self):
        assert toml_key_length_range(_MINIMAL) == toml_key_length_range(_MINIMAL)


class TestTomlBoolToTotalRatio:
    def test_return_type(self):
        assert isinstance(toml_bool_to_total_ratio(_MINIMAL), float)

    def test_exact_0_2_for_minimal(self):
        # minimal.toml has 5 top-level keys: title, version, enabled, server, database
        # enabled=true is 1 bool → 1/5 = 0.2
        assert toml_bool_to_total_ratio(_MINIMAL) == 0.2

    def test_exact_1_0_for_all_bools(self):
        tmp = _write_temp(_ALL_BOOLS)
        try:
            assert toml_bool_to_total_ratio(tmp) == 1.0
        finally:
            os.unlink(tmp)

    def test_zero_for_numeric_only(self):
        tmp = _write_temp(_EQUAL_KEYS)
        try:
            assert toml_bool_to_total_ratio(tmp) == 0.0
        finally:
            os.unlink(tmp)

    def test_bounded(self):
        r = toml_bool_to_total_ratio(_MINIMAL)
        assert 0.0 <= r <= 1.0

    def test_consistent(self):
        assert toml_bool_to_total_ratio(_MINIMAL) == toml_bool_to_total_ratio(_MINIMAL)
