"""Tests for TOML Sprint 137 gap closure.

Closes:
  GAP-TOML-FOSS-TOML_IS_ALL_-001  (Toml Is All Strings)
"""
import sys
import tempfile
import os
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.toml import toml_is_all_strings

_MINIMAL = str(_REPO / "samples" / "by-format" / "toml" / "minimal.toml")

# Temp TOML with only string values
_ALL_STRINGS_CONTENT = 'name = "Alice"\ncity = "Paris"\ntag = "active"\n'


def _write_temp(content: str) -> str:
    f = tempfile.NamedTemporaryFile(suffix=".toml", mode="w", delete=False)
    f.write(content)
    f.close()
    return f.name


class TestTomlIsAllStrings:
    def test_return_type(self):
        assert isinstance(toml_is_all_strings(_MINIMAL), bool)

    def test_false_for_mixed_types(self):
        # minimal.toml has booleans (enabled=true) and integers (port=8080, max_connections=10)
        assert toml_is_all_strings(_MINIMAL) is False

    def test_true_for_all_string_values(self):
        tmp = _write_temp(_ALL_STRINGS_CONTENT)
        try:
            assert toml_is_all_strings(tmp) is True
        finally:
            os.unlink(tmp)

    def test_consistent(self):
        assert toml_is_all_strings(_MINIMAL) == toml_is_all_strings(_MINIMAL)

    def test_nonnull(self):
        result = toml_is_all_strings(_MINIMAL)
        assert result is not None
