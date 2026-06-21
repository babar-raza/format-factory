"""Tests for TOML Sprint 56 gap closure.

Closes:
  GAP-TOML-FOSS-TOML_LIST_IT-001  (Toml List Item Count)
  GAP-TOML-FOSS-TOML_IS_SING-001  (Toml Is Single Table)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.toml import toml_list_item_count, toml_is_single_table

_DIR = _REPO / "samples" / "by-format" / "toml"
_MINIMAL = str(_DIR / "minimal.toml")


class TestTomlListItemCount:
    def test_return_type(self):
        assert isinstance(toml_list_item_count(_MINIMAL), int)

    def test_zero_for_minimal(self):
        assert toml_list_item_count(_MINIMAL) == 0

    def test_nonnegative(self):
        assert toml_list_item_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert toml_list_item_count(_MINIMAL) == toml_list_item_count(_MINIMAL)


class TestTomlIsSingleTable:
    def test_return_type(self):
        assert isinstance(toml_is_single_table(_MINIMAL), bool)

    def test_false_for_minimal(self):
        assert toml_is_single_table(_MINIMAL) is False

    def test_consistent_across_calls(self):
        assert toml_is_single_table(_MINIMAL) == toml_is_single_table(_MINIMAL)
