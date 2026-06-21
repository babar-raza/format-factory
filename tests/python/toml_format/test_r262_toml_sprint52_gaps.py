"""Tests for TOML Sprint 52 gap closure.

Closes:
  GAP-TOML-FOSS-TOML_MIN_KEY-001  (Toml Min Key Length)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.toml import toml_min_key_length

_DIR = _REPO / "samples" / "by-format" / "toml"
_MINIMAL = str(_DIR / "minimal.toml")


class TestTomlMinKeyLength:
    def test_return_type(self):
        assert isinstance(toml_min_key_length(_MINIMAL), int)

    def test_exact_5_for_minimal(self):
        assert toml_min_key_length(_MINIMAL) == 5

    def test_positive(self):
        assert toml_min_key_length(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert toml_min_key_length(_MINIMAL) == toml_min_key_length(_MINIMAL)
