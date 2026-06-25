"""Tests for TOML R120 gap closure.

Closes:
  GAP-TOML-FOSS-HAS_ARRAYS-001     (toml_has_arrays)
  GAP-TOML-FOSS-HAS_NESTED_T-001   (toml_has_nested_tables)
  GAP-TOML-FOSS-SCALAR_KEY_C-001   (toml_scalar_key_count)
  GAP-TOML-FOSS-IS_EMPTY-001       (toml_is_empty — already implemented, verified here)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.toml import (
    toml_has_arrays,
    toml_has_nested_tables,
    toml_scalar_key_count,
    toml_is_empty,
)

_DIR = _REPO / "samples" / "by-format" / "toml"
_MINIMAL = str(_DIR / "minimal.toml")

# minimal.toml:
#   title = "Format Factory TOML Sample"   <- scalar (str)
#   version = "1.0"                         <- scalar (str)
#   enabled = true                          <- scalar (bool)
#   [server] host=..., port=...             <- table (dict)
#   [database] name=..., max_connections=.. <- table (dict)

_INLINE_WITH_ARRAYS = b'tags = ["python", "toml"]\ncount = 3\n'
_INLINE_NO_ARRAYS = b'name = "test"\nvalue = 42\n'
_INLINE_EMPTY = b''
_INLINE_ONLY_TABLES = b'[section]\nkey = "val"\n'
_INLINE_MIXED = b'tags = ["a", "b"]\n[meta]\nversion = 1\nflat_key = true\n'


class TestTomlHasArrays:
    """GAP-TOML-FOSS-HAS_ARRAYS-001: toml_has_arrays."""

    def test_returns_bool(self):
        assert isinstance(toml_has_arrays(_MINIMAL), bool)

    def test_false_for_minimal_no_arrays(self):
        # minimal.toml has no array values at top level
        assert toml_has_arrays(_MINIMAL) is False

    def test_true_for_inline_with_array(self):
        assert toml_has_arrays(_INLINE_WITH_ARRAYS) is True

    def test_false_for_inline_no_arrays(self):
        assert toml_has_arrays(_INLINE_NO_ARRAYS) is False

    def test_false_for_empty(self):
        assert toml_has_arrays(_INLINE_EMPTY) is False

    def test_false_for_only_tables(self):
        # [section] becomes a dict, not a list
        assert toml_has_arrays(_INLINE_ONLY_TABLES) is False

    def test_true_for_mixed(self):
        assert toml_has_arrays(_INLINE_MIXED) is True

    def test_consistent_across_calls(self):
        assert toml_has_arrays(_MINIMAL) == toml_has_arrays(_MINIMAL)

    def test_file_path_works(self):
        result = toml_has_arrays(Path(_MINIMAL))
        assert isinstance(result, bool)


class TestTomlHasNestedTables:
    """GAP-TOML-FOSS-HAS_NESTED_T-001: toml_has_nested_tables."""

    def test_returns_bool(self):
        assert isinstance(toml_has_nested_tables(_MINIMAL), bool)

    def test_true_for_minimal_has_tables(self):
        # minimal.toml has [server] and [database] sections
        assert toml_has_nested_tables(_MINIMAL) is True

    def test_false_for_flat_inline(self):
        assert toml_has_nested_tables(_INLINE_NO_ARRAYS) is False

    def test_false_for_empty(self):
        assert toml_has_nested_tables(_INLINE_EMPTY) is False

    def test_true_for_inline_with_section(self):
        assert toml_has_nested_tables(_INLINE_ONLY_TABLES) is True

    def test_true_for_mixed(self):
        assert toml_has_nested_tables(_INLINE_MIXED) is True

    def test_consistent_across_calls(self):
        assert toml_has_nested_tables(_MINIMAL) == toml_has_nested_tables(_MINIMAL)

    def test_file_path_works(self):
        result = toml_has_nested_tables(Path(_MINIMAL))
        assert isinstance(result, bool)


class TestTomlScalarKeyCount:
    """GAP-TOML-FOSS-SCALAR_KEY_C-001: toml_scalar_key_count."""

    def test_returns_int(self):
        assert isinstance(toml_scalar_key_count(_MINIMAL), int)

    def test_exact_3_for_minimal(self):
        # title, version, enabled are scalars; [server] and [database] are tables
        assert toml_scalar_key_count(_MINIMAL) == 3

    def test_zero_for_empty(self):
        assert toml_scalar_key_count(_INLINE_EMPTY) == 0

    def test_two_for_no_arrays(self):
        # name and value are scalars
        assert toml_scalar_key_count(_INLINE_NO_ARRAYS) == 2

    def test_one_for_arrays_plus_scalar(self):
        # tags is a list (not scalar), count is int (scalar) → 1 scalar
        assert toml_scalar_key_count(_INLINE_WITH_ARRAYS) == 1

    def test_zero_for_only_tables(self):
        # [section] becomes a nested table, not scalar
        assert toml_scalar_key_count(_INLINE_ONLY_TABLES) == 0

    def test_nonnegative(self):
        assert toml_scalar_key_count(_MINIMAL) >= 0

    def test_consistent(self):
        assert toml_scalar_key_count(_MINIMAL) == toml_scalar_key_count(_MINIMAL)

    def test_file_path_works(self):
        result = toml_scalar_key_count(Path(_MINIMAL))
        assert isinstance(result, int)


class TestTomlIsEmpty:
    """GAP-TOML-FOSS-IS_EMPTY-001: toml_is_empty (already implemented, verified)."""

    def test_returns_bool(self):
        assert isinstance(toml_is_empty(_MINIMAL), bool)

    def test_false_for_nonempty(self):
        assert toml_is_empty(_MINIMAL) is False

    def test_true_for_empty(self):
        assert toml_is_empty(_INLINE_EMPTY) is True

    def test_false_for_single_key(self):
        assert toml_is_empty(b'key = "val"') is False

    def test_consistent(self):
        assert toml_is_empty(_MINIMAL) == toml_is_empty(_MINIMAL)
