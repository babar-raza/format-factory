"""Tests for TOML Sprint 138 gap closure.

Closes:
  GAP-TOML-FOSS-TOML_HAS_MOR-001  (Toml Has More Strings Than Bools)
"""
import sys
import tempfile
import os
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.toml import toml_has_more_strings_than_bools

_MINIMAL = str(_REPO / "samples" / "by-format" / "toml" / "minimal.toml")

_ALL_STRINGS = 'name = "Alice"\ncity = "Paris"\ntag = "active"\n'
_ALL_BOOLS = "a = true\nb = false\n"


def _write_temp(content: str) -> str:
    f = tempfile.NamedTemporaryFile(suffix=".toml", mode="w", delete=False)
    f.write(content)
    f.close()
    return f.name


class TestTomlHasMoreStringsThanBools:
    def test_return_type(self):
        assert isinstance(toml_has_more_strings_than_bools(_MINIMAL), bool)

    def test_true_for_minimal(self):
        # minimal.toml has 6+ string values vs 1 bool (enabled=true)
        assert toml_has_more_strings_than_bools(_MINIMAL) is True

    def test_true_for_all_strings(self):
        tmp = _write_temp(_ALL_STRINGS)
        try:
            assert toml_has_more_strings_than_bools(tmp) is True
        finally:
            os.unlink(tmp)

    def test_false_for_all_bools(self):
        tmp = _write_temp(_ALL_BOOLS)
        try:
            assert toml_has_more_strings_than_bools(tmp) is False
        finally:
            os.unlink(tmp)

    def test_consistent(self):
        assert toml_has_more_strings_than_bools(_MINIMAL) == toml_has_more_strings_than_bools(_MINIMAL)
