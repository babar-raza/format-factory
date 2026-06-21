"""Tests for toml_list_item_count and toml_is_single_table (Sprint r304)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.toml.toml_codec import toml_list_item_count, toml_is_single_table

_WITH_LISTS = b'items = [1, 2, 3]\ntags = ["a", "b"]\n'
_NO_LISTS = b'x = 1\ny = "hello"\n'
_SINGLE_LIST = b'vals = [42]\n'

_FLAT = b'x = 1\ny = 2\n'
_ONE_TABLE = b'x = 1\n[server]\nhost = "localhost"\n'
_TWO_TABLES = b'[db]\nname = "foo"\n[server]\nport = 80\n'


class TestTomlListItemCount:
    """Tests for toml_list_item_count."""

    def test_two_lists_sum(self):
        """3-element list + 2-element list = 5 total items."""
        assert toml_list_item_count(_WITH_LISTS) == 5

    def test_no_lists_returns_zero(self):
        """No list values → 0."""
        assert toml_list_item_count(_NO_LISTS) == 0

    def test_single_element_list(self):
        """One list with one element → 1."""
        assert toml_list_item_count(_SINGLE_LIST) == 1

    def test_returns_int(self):
        assert isinstance(toml_list_item_count(_WITH_LISTS), int)

    def test_no_lists_is_zero(self):
        assert toml_list_item_count(_NO_LISTS) == 0

    def test_with_lists_greater_than_single(self):
        assert toml_list_item_count(_WITH_LISTS) > toml_list_item_count(_SINGLE_LIST)


class TestTomlIsSingleTable:
    """Tests for toml_is_single_table."""

    def test_flat_is_single_table(self):
        """No nested tables → True."""
        assert toml_is_single_table(_FLAT) is True

    def test_one_nested_table_is_false(self):
        """One nested table section → False."""
        assert toml_is_single_table(_ONE_TABLE) is False

    def test_two_nested_tables_is_false(self):
        """Two nested table sections → False."""
        assert toml_is_single_table(_TWO_TABLES) is False

    def test_returns_bool(self):
        assert isinstance(toml_is_single_table(_FLAT), bool)

    def test_nested_returns_false(self):
        assert toml_is_single_table(_ONE_TABLE) is False

    def test_flat_true_nested_false(self):
        r1 = toml_is_single_table(_FLAT)
        r2 = toml_is_single_table(_TWO_TABLES)
        assert r1 is True and r2 is False
