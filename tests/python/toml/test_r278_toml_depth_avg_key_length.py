"""
Tests for toml_depth and toml_avg_key_length.
Closes: GAP-TOML-FOSS-TOML_DEPTH-001, GAP-TOML-FOSS-TOML_AVG_KEY-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from toml import toml_depth, toml_avg_key_length

_FLAT = b"name = \"test\"\ncount = 42\n"
_ONE_LEVEL = b"[server]\nhost = \"localhost\"\n"
_TWO_LEVEL = b"[a]\n[a.b]\nkey = \"val\"\n"
_EMPTY = b""


class TestTomlDepth:
    def test_returns_int(self):
        assert isinstance(toml_depth(_FLAT), int)

    def test_flat_has_depth_one(self):
        assert toml_depth(_FLAT) == 1

    def test_one_level_table(self):
        assert toml_depth(_ONE_LEVEL) == 2

    def test_two_level_nested(self):
        # [a][a.b] gives depth 3
        assert toml_depth(_TWO_LEVEL) == 3

    def test_zero_or_one_for_empty(self):
        depth = toml_depth(_EMPTY)
        assert depth >= 0


class TestTomlAvgKeyLength:
    def test_returns_float(self):
        assert isinstance(toml_avg_key_length(_FLAT), float)

    def test_zero_for_empty(self):
        assert toml_avg_key_length(_EMPTY) == 0.0

    def test_positive_for_content(self):
        assert toml_avg_key_length(_FLAT) > 0.0

    def test_correct_avg(self):
        # "name" (4) + "count" (5) = avg 4.5
        assert toml_avg_key_length(_FLAT) == pytest.approx(4.5)

    def test_single_key(self):
        content = b"abcdef = 1\n"
        assert toml_avg_key_length(content) == pytest.approx(6.0)
