"""Tests for TOML Sprint 140 gap closure.

Closes:
  GAP-TOML-FOSS-TOML_IS_NUME-001  (Toml Is Numeric Only)
"""
import sys
import tempfile
import os
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.toml import toml_is_numeric_only

_MINIMAL = str(_REPO / "samples" / "by-format" / "toml" / "minimal.toml")

_ALL_NUMERIC = "a = 1\nb = 2\nc = 3\n"
_ALL_STRINGS = 'name = "Alice"\ncity = "Paris"\n'


def _write_temp(content: str) -> str:
    f = tempfile.NamedTemporaryFile(suffix=".toml", mode="w", delete=False)
    f.write(content)
    f.close()
    return f.name


class TestTomlIsNumericOnly:
    def test_return_type(self):
        assert isinstance(toml_is_numeric_only(_MINIMAL), bool)

    def test_false_for_minimal(self):
        # minimal.toml has strings, booleans — not numeric only
        assert toml_is_numeric_only(_MINIMAL) is False

    def test_true_for_all_numeric(self):
        tmp = _write_temp(_ALL_NUMERIC)
        try:
            assert toml_is_numeric_only(tmp) is True
        finally:
            os.unlink(tmp)

    def test_false_for_all_strings(self):
        tmp = _write_temp(_ALL_STRINGS)
        try:
            assert toml_is_numeric_only(tmp) is False
        finally:
            os.unlink(tmp)

    def test_consistent(self):
        assert toml_is_numeric_only(_MINIMAL) == toml_is_numeric_only(_MINIMAL)
