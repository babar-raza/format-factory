"""
Tests for 23 TOML analytics functions — gap closure batch.

Closes:
  GAP-TOML-FOSS-TOML_MAX_LIS-001   toml_max_list_length
  GAP-TOML-FOSS-TOML_ALL_KEY-001   toml_all_keys_lowercase
  GAP-TOML-FOSS-TOML_HAS_NUM-001   toml_has_numeric_values
  GAP-TOML-FOSS-TOML_AVG_LIS-001   toml_avg_list_length
  GAP-TOML-FOSS-TOML_MAX_NUM-001   toml_max_numeric_value
  GAP-TOML-FOSS-TOML_MIN_NUM-001   toml_min_numeric_value
  GAP-TOML-FOSS-TOML_BOOL_RA-001   toml_bool_ratio
  GAP-TOML-FOSS-TOML_UNIQUE_-001   toml_unique_value_count
  GAP-TOML-FOSS-TOML_FILE_SI-001   toml_file_size_bytes
  GAP-TOML-FOSS-TOML_MAX_KEY-001   toml_max_key_length
  GAP-TOML-FOSS-TOML_AVG_VAL-001   toml_avg_value_length
  GAP-TOML-FOSS-TOML_MIN_KEY-001   toml_min_key_length
  GAP-TOML-FOSS-TOML_LIST_IT-001   toml_list_item_count
  GAP-TOML-FOSS-TOML_IS_SING-001   toml_is_single_table
  GAP-TOML-FOSS-TOML_BOOL_CO-001   toml_bool_count
  GAP-TOML-FOSS-TOML_HAS_BOO-001   toml_has_boolean_value
  GAP-TOML-FOSS-TOML_KEY_COU-001   toml_key_count_squared
  GAP-TOML-FOSS-TOML_HAS_EXA-001   toml_has_exactly_two_keys
  GAP-TOML-FOSS-TOML_HAS_ONL-001   toml_has_only_booleans
  GAP-TOML-FOSS-TOML_HAS_MIX-001   toml_has_mixed_value_types
  GAP-TOML-FOSS-TOML_NON_BOO-001   toml_non_boolean_count
  GAP-TOML-FOSS-TOML_HAS_NO_-001   toml_has_no_booleans
  GAP-TOML-FOSS-TOML_HAS_AT_-001   toml_has_at_least_one_numeric
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from toml import (
    toml_max_list_length,
    toml_all_keys_lowercase,
    toml_has_numeric_values,
    toml_avg_list_length,
    toml_max_numeric_value,
    toml_min_numeric_value,
    toml_bool_ratio,
    toml_unique_value_count,
    toml_file_size_bytes,
    toml_max_key_length,
    toml_avg_value_length,
    toml_min_key_length,
    toml_list_item_count,
    toml_is_single_table,
    toml_bool_count,
    toml_has_boolean_value,
    toml_key_count_squared,
    toml_has_exactly_two_keys,
    toml_has_only_booleans,
    toml_has_mixed_value_types,
    toml_non_boolean_count,
    toml_has_no_booleans,
    toml_has_at_least_one_numeric,
)

# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

_EMPTY = b""
_FLAT_TWO = b"a = 1\nb = 2\n"
_THREE_KEYS = b'name = "test"\ncount = 42\nenabled = true\n'
_BOOLS_ONLY = b"x = true\ny = false\n"
_WITH_LISTS = b"tags = [\"alpha\", \"beta\", \"gamma\"]\nids = [1, 2]\n"
_MIXED = b'title = "hello"\nport = 8080\nflag = true\n'
_NESTED = b"a = 1\n\n[server]\nhost = \"localhost\"\n"
_NUMERIC_ONLY = b"x = 10\ny = -5\nz = 3.14\n"
_LONG_KEY = b'a_very_long_key_name = "value"\nshort = 1\n'
_TWO_EQUAL = b"a = 1\nb = 1\n"
_UPPERCASE = b"Title = \"hello\"\nPort = 8080\n"


# ---------------------------------------------------------------------------
# GAP-TOML-FOSS-TOML_MAX_LIS-001: toml_max_list_length
# ---------------------------------------------------------------------------

class TestTomlMaxListLength:
    def test_returns_int(self):
        assert isinstance(toml_max_list_length(_WITH_LISTS), int)

    def test_empty_doc_returns_zero(self):
        assert toml_max_list_length(_EMPTY) == 0

    def test_no_lists_returns_zero(self):
        assert toml_max_list_length(_THREE_KEYS) == 0

    def test_longest_list_counted(self):
        # tags has 3 items, ids has 2 — max is 3
        assert toml_max_list_length(_WITH_LISTS) == 3

    def test_single_list(self):
        src = b"items = [1, 2, 3, 4, 5]\n"
        assert toml_max_list_length(src) == 5


# ---------------------------------------------------------------------------
# GAP-TOML-FOSS-TOML_ALL_KEY-001: toml_all_keys_lowercase
# ---------------------------------------------------------------------------

class TestTomlAllKeysLowercase:
    def test_returns_bool(self):
        assert isinstance(toml_all_keys_lowercase(_FLAT_TWO), bool)

    def test_empty_doc_returns_true(self):
        assert toml_all_keys_lowercase(_EMPTY) is True

    def test_all_lowercase_returns_true(self):
        assert toml_all_keys_lowercase(_THREE_KEYS) is True

    def test_uppercase_key_returns_false(self):
        assert toml_all_keys_lowercase(_UPPERCASE) is False

    def test_mixed_case_returns_false(self):
        src = b"myKey = 1\n"
        assert toml_all_keys_lowercase(src) is False


# ---------------------------------------------------------------------------
# GAP-TOML-FOSS-TOML_HAS_NUM-001: toml_has_numeric_values
# ---------------------------------------------------------------------------

class TestTomlHasNumericValues:
    def test_returns_bool(self):
        assert isinstance(toml_has_numeric_values(_THREE_KEYS), bool)

    def test_numeric_present_returns_true(self):
        assert toml_has_numeric_values(_THREE_KEYS) is True

    def test_bools_only_returns_false(self):
        assert toml_has_numeric_values(_BOOLS_ONLY) is False

    def test_string_only_returns_false(self):
        src = b'key = "hello"\n'
        assert toml_has_numeric_values(src) is False

    def test_float_counts_as_numeric(self):
        src = b"pi = 3.14\n"
        assert toml_has_numeric_values(src) is True


# ---------------------------------------------------------------------------
# GAP-TOML-FOSS-TOML_AVG_LIS-001: toml_avg_list_length
# ---------------------------------------------------------------------------

class TestTomlAvgListLength:
    def test_returns_float(self):
        assert isinstance(toml_avg_list_length(_WITH_LISTS), float)

    def test_no_lists_returns_zero(self):
        assert toml_avg_list_length(_THREE_KEYS) == 0.0

    def test_empty_doc_returns_zero(self):
        assert toml_avg_list_length(_EMPTY) == 0.0

    def test_avg_of_two_lists(self):
        # tags=3, ids=2 -> avg = 2.5
        result = toml_avg_list_length(_WITH_LISTS)
        assert abs(result - 2.5) < 1e-9

    def test_single_list_avg_equals_length(self):
        src = b"items = [1, 2, 3]\n"
        assert toml_avg_list_length(src) == 3.0


# ---------------------------------------------------------------------------
# GAP-TOML-FOSS-TOML_MAX_NUM-001: toml_max_numeric_value
# ---------------------------------------------------------------------------

class TestTomlMaxNumericValue:
    def test_returns_float(self):
        assert isinstance(toml_max_numeric_value(_NUMERIC_ONLY), float)

    def test_no_numerics_returns_zero(self):
        assert toml_max_numeric_value(_BOOLS_ONLY) == 0.0

    def test_max_of_three(self):
        # x=10, y=-5, z=3.14 -> max=10
        assert toml_max_numeric_value(_NUMERIC_ONLY) == 10.0

    def test_negative_values(self):
        src = b"a = -1\nb = -5\nc = -2\n"
        assert toml_max_numeric_value(src) == -1.0

    def test_bool_excluded(self):
        src = b"flag = true\nval = 100\n"
        assert toml_max_numeric_value(src) == 100.0


# ---------------------------------------------------------------------------
# GAP-TOML-FOSS-TOML_MIN_NUM-001: toml_min_numeric_value
# ---------------------------------------------------------------------------

class TestTomlMinNumericValue:
    def test_returns_float(self):
        assert isinstance(toml_min_numeric_value(_NUMERIC_ONLY), float)

    def test_no_numerics_returns_zero(self):
        assert toml_min_numeric_value(_BOOLS_ONLY) == 0.0

    def test_min_of_three(self):
        # x=10, y=-5, z=3.14 -> min=-5
        assert toml_min_numeric_value(_NUMERIC_ONLY) == -5.0

    def test_positive_values(self):
        src = b"a = 10\nb = 5\nc = 20\n"
        assert toml_min_numeric_value(src) == 5.0

    def test_bool_excluded(self):
        src = b"flag = false\nval = -99\n"
        assert toml_min_numeric_value(src) == -99.0


# ---------------------------------------------------------------------------
# GAP-TOML-FOSS-TOML_BOOL_RA-001: toml_bool_ratio
# ---------------------------------------------------------------------------

class TestTomlBoolRatio:
    def test_returns_float(self):
        assert isinstance(toml_bool_ratio(_THREE_KEYS), float)

    def test_empty_doc_returns_zero(self):
        assert toml_bool_ratio(_EMPTY) == 0.0

    def test_all_bools_returns_one(self):
        assert toml_bool_ratio(_BOOLS_ONLY) == 1.0

    def test_no_bools_returns_zero(self):
        assert toml_bool_ratio(_FLAT_TWO) == 0.0

    def test_one_of_three(self):
        # name=str, count=int, enabled=bool -> 1/3
        result = toml_bool_ratio(_THREE_KEYS)
        assert abs(result - 1 / 3) < 1e-9


# ---------------------------------------------------------------------------
# GAP-TOML-FOSS-TOML_UNIQUE_-001: toml_unique_value_count
# ---------------------------------------------------------------------------

class TestTomlUniqueValueCount:
    def test_returns_int(self):
        assert isinstance(toml_unique_value_count(_THREE_KEYS), int)

    def test_empty_doc_returns_zero(self):
        assert toml_unique_value_count(_EMPTY) == 0

    def test_all_different_values(self):
        # name="test", count=42, enabled=true -> 3 unique
        assert toml_unique_value_count(_THREE_KEYS) == 3

    def test_duplicate_values(self):
        # a=1, b=1 -> 1 unique (both stringify to "1")
        assert toml_unique_value_count(_TWO_EQUAL) == 1

    def test_lists_excluded(self):
        # lists are not scalars, so excluded
        src = b"tags = [1, 2]\nname = \"hello\"\n"
        assert toml_unique_value_count(src) == 1


# ---------------------------------------------------------------------------
# GAP-TOML-FOSS-TOML_FILE_SI-001: toml_file_size_bytes
# ---------------------------------------------------------------------------

class TestTomlFileSizeBytes:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes(_FLAT_TWO), int)

    def test_bytes_source_returns_zero(self):
        assert toml_file_size_bytes(_FLAT_TWO) == 0

    def test_nonexistent_path_returns_zero(self):
        assert toml_file_size_bytes("/nonexistent/path.toml") == 0

    def test_real_file_returns_positive(self, tmp_path):
        f = tmp_path / "sample.toml"
        f.write_bytes(b"key = 1\n")
        result = toml_file_size_bytes(str(f))
        assert result > 0

    def test_real_file_matches_actual_size(self, tmp_path):
        content = b"title = \"hello\"\nport = 8080\n"
        f = tmp_path / "test.toml"
        f.write_bytes(content)
        assert toml_file_size_bytes(str(f)) == len(content)


# ---------------------------------------------------------------------------
# GAP-TOML-FOSS-TOML_MAX_KEY-001: toml_max_key_length
# ---------------------------------------------------------------------------

class TestTomlMaxKeyLength:
    def test_returns_int(self):
        assert isinstance(toml_max_key_length(_FLAT_TWO), int)

    def test_empty_doc_returns_zero(self):
        assert toml_max_key_length(_EMPTY) == 0

    def test_single_char_keys(self):
        assert toml_max_key_length(_FLAT_TWO) == 1

    def test_long_key_detected(self):
        # "a_very_long_key_name" = 20 chars, "short" = 5
        assert toml_max_key_length(_LONG_KEY) == 20

    def test_three_keys(self):
        # "name"=4, "count"=5, "enabled"=7 -> max=7
        assert toml_max_key_length(_THREE_KEYS) == 7


# ---------------------------------------------------------------------------
# GAP-TOML-FOSS-TOML_AVG_VAL-001: toml_avg_value_length
# ---------------------------------------------------------------------------

class TestTomlAvgValueLength:
    def test_returns_float(self):
        assert isinstance(toml_avg_value_length(_FLAT_TWO), float)

    def test_empty_doc_returns_zero(self):
        assert toml_avg_value_length(_EMPTY) == 0.0

    def test_positive_for_nonempty(self):
        assert toml_avg_value_length(_THREE_KEYS) > 0.0

    def test_two_keys_same_length(self):
        # a=1, b=2 -> str(1)="1" (len 1), str(2)="2" (len 1), avg=1.0
        assert toml_avg_value_length(_FLAT_TWO) == 1.0

    def test_non_negative(self):
        assert toml_avg_value_length(_MIXED) >= 0.0


# ---------------------------------------------------------------------------
# GAP-TOML-FOSS-TOML_MIN_KEY-001: toml_min_key_length
# ---------------------------------------------------------------------------

class TestTomlMinKeyLength:
    def test_returns_int(self):
        assert isinstance(toml_min_key_length(_FLAT_TWO), int)

    def test_empty_doc_returns_zero(self):
        assert toml_min_key_length(_EMPTY) == 0

    def test_single_char_keys(self):
        assert toml_min_key_length(_FLAT_TWO) == 1

    def test_short_key_detected(self):
        # "a_very_long_key_name" and "short" — min is 5
        assert toml_min_key_length(_LONG_KEY) == 5

    def test_three_keys(self):
        # "name"=4, "count"=5, "enabled"=7 -> min=4
        assert toml_min_key_length(_THREE_KEYS) == 4


# ---------------------------------------------------------------------------
# GAP-TOML-FOSS-TOML_LIST_IT-001: toml_list_item_count
# ---------------------------------------------------------------------------

class TestTomlListItemCount:
    def test_returns_int(self):
        assert isinstance(toml_list_item_count(_WITH_LISTS), int)

    def test_no_lists_returns_zero(self):
        assert toml_list_item_count(_THREE_KEYS) == 0

    def test_empty_doc_returns_zero(self):
        assert toml_list_item_count(_EMPTY) == 0

    def test_total_across_lists(self):
        # tags=3, ids=2 -> total=5
        assert toml_list_item_count(_WITH_LISTS) == 5

    def test_single_list(self):
        src = b"items = [10, 20, 30, 40]\n"
        assert toml_list_item_count(src) == 4


# ---------------------------------------------------------------------------
# GAP-TOML-FOSS-TOML_IS_SING-001: toml_is_single_table
# ---------------------------------------------------------------------------

class TestTomlIsSingleTable:
    def test_returns_bool(self):
        assert isinstance(toml_is_single_table(_FLAT_TWO), bool)

    def test_flat_doc_is_single_table(self):
        assert toml_is_single_table(_FLAT_TWO) is True

    def test_nested_table_is_not_single(self):
        assert toml_is_single_table(_NESTED) is False

    def test_empty_doc_is_single_table(self):
        assert toml_is_single_table(_EMPTY) is True

    def test_three_keys_flat_is_single(self):
        assert toml_is_single_table(_THREE_KEYS) is True


# ---------------------------------------------------------------------------
# GAP-TOML-FOSS-TOML_BOOL_CO-001: toml_bool_count
# ---------------------------------------------------------------------------

class TestTomlBoolCount:
    def test_returns_int(self):
        assert isinstance(toml_bool_count(_THREE_KEYS), int)

    def test_empty_doc_returns_zero(self):
        assert toml_bool_count(_EMPTY) == 0

    def test_no_bools_returns_zero(self):
        assert toml_bool_count(_FLAT_TWO) == 0

    def test_one_bool_in_three_keys(self):
        assert toml_bool_count(_THREE_KEYS) == 1

    def test_all_bools(self):
        assert toml_bool_count(_BOOLS_ONLY) == 2


# ---------------------------------------------------------------------------
# GAP-TOML-FOSS-TOML_HAS_BOO-001: toml_has_boolean_value
# ---------------------------------------------------------------------------

class TestTomlHasBooleanValue:
    def test_returns_bool(self):
        assert isinstance(toml_has_boolean_value(_THREE_KEYS), bool)

    def test_empty_doc_returns_false(self):
        assert toml_has_boolean_value(_EMPTY) is False

    def test_with_bool_returns_true(self):
        assert toml_has_boolean_value(_THREE_KEYS) is True

    def test_without_bool_returns_false(self):
        assert toml_has_boolean_value(_FLAT_TWO) is False

    def test_all_bools_returns_true(self):
        assert toml_has_boolean_value(_BOOLS_ONLY) is True


# ---------------------------------------------------------------------------
# GAP-TOML-FOSS-TOML_KEY_COU-001: toml_key_count_squared
# ---------------------------------------------------------------------------

class TestTomlKeyCountSquared:
    def test_returns_int(self):
        assert isinstance(toml_key_count_squared(_FLAT_TWO), int)

    def test_empty_doc_returns_zero(self):
        assert toml_key_count_squared(_EMPTY) == 0

    def test_two_keys_squared(self):
        assert toml_key_count_squared(_FLAT_TWO) == 4

    def test_three_keys_squared(self):
        assert toml_key_count_squared(_THREE_KEYS) == 9

    def test_one_key_squared(self):
        src = b"x = 1\n"
        assert toml_key_count_squared(src) == 1


# ---------------------------------------------------------------------------
# GAP-TOML-FOSS-TOML_HAS_EXA-001: toml_has_exactly_two_keys
# ---------------------------------------------------------------------------

class TestTomlHasExactlyTwoKeys:
    def test_returns_bool(self):
        assert isinstance(toml_has_exactly_two_keys(_FLAT_TWO), bool)

    def test_two_keys_returns_true(self):
        assert toml_has_exactly_two_keys(_FLAT_TWO) is True

    def test_three_keys_returns_false(self):
        assert toml_has_exactly_two_keys(_THREE_KEYS) is False

    def test_empty_returns_false(self):
        assert toml_has_exactly_two_keys(_EMPTY) is False

    def test_one_key_returns_false(self):
        src = b"x = 1\n"
        assert toml_has_exactly_two_keys(src) is False


# ---------------------------------------------------------------------------
# GAP-TOML-FOSS-TOML_HAS_ONL-001: toml_has_only_booleans
# ---------------------------------------------------------------------------

class TestTomlHasOnlyBooleans:
    def test_returns_bool(self):
        assert isinstance(toml_has_only_booleans(_BOOLS_ONLY), bool)

    def test_all_bools_returns_true(self):
        assert toml_has_only_booleans(_BOOLS_ONLY) is True

    def test_mixed_returns_false(self):
        assert toml_has_only_booleans(_THREE_KEYS) is False

    def test_empty_returns_false(self):
        assert toml_has_only_booleans(_EMPTY) is False

    def test_numerics_returns_false(self):
        assert toml_has_only_booleans(_FLAT_TWO) is False


# ---------------------------------------------------------------------------
# GAP-TOML-FOSS-TOML_HAS_MIX-001: toml_has_mixed_value_types
# ---------------------------------------------------------------------------

class TestTomlHasMixedValueTypes:
    def test_returns_bool(self):
        assert isinstance(toml_has_mixed_value_types(_THREE_KEYS), bool)

    def test_mixed_returns_true(self):
        assert toml_has_mixed_value_types(_THREE_KEYS) is True

    def test_single_type_returns_false(self):
        assert toml_has_mixed_value_types(_FLAT_TWO) is False

    def test_empty_returns_false(self):
        assert toml_has_mixed_value_types(_EMPTY) is False

    def test_all_bools_not_mixed(self):
        assert toml_has_mixed_value_types(_BOOLS_ONLY) is False


# ---------------------------------------------------------------------------
# GAP-TOML-FOSS-TOML_NON_BOO-001: toml_non_boolean_count
# ---------------------------------------------------------------------------

class TestTomlNonBooleanCount:
    def test_returns_int(self):
        assert isinstance(toml_non_boolean_count(_THREE_KEYS), int)

    def test_empty_doc_returns_zero(self):
        assert toml_non_boolean_count(_EMPTY) == 0

    def test_all_bools_returns_zero(self):
        assert toml_non_boolean_count(_BOOLS_ONLY) == 0

    def test_two_non_bools_in_three_keys(self):
        # name(str) + count(int) = 2 non-bool
        assert toml_non_boolean_count(_THREE_KEYS) == 2

    def test_all_numeric_returns_all(self):
        assert toml_non_boolean_count(_FLAT_TWO) == 2


# ---------------------------------------------------------------------------
# GAP-TOML-FOSS-TOML_HAS_NO_-001: toml_has_no_booleans
# ---------------------------------------------------------------------------

class TestTomlHasNoBooleans:
    def test_returns_bool(self):
        assert isinstance(toml_has_no_booleans(_FLAT_TWO), bool)

    def test_no_bools_returns_true(self):
        assert toml_has_no_booleans(_FLAT_TWO) is True

    def test_with_bool_returns_false(self):
        assert toml_has_no_booleans(_THREE_KEYS) is False

    def test_empty_returns_true(self):
        assert toml_has_no_booleans(_EMPTY) is True

    def test_all_bools_returns_false(self):
        assert toml_has_no_booleans(_BOOLS_ONLY) is False


# ---------------------------------------------------------------------------
# GAP-TOML-FOSS-TOML_HAS_AT_-001: toml_has_at_least_one_numeric
# ---------------------------------------------------------------------------

class TestTomlHasAtLeastOneNumeric:
    def test_returns_bool(self):
        assert isinstance(toml_has_at_least_one_numeric(_THREE_KEYS), bool)

    def test_numeric_present_returns_true(self):
        assert toml_has_at_least_one_numeric(_THREE_KEYS) is True

    def test_bools_only_returns_false(self):
        assert toml_has_at_least_one_numeric(_BOOLS_ONLY) is False

    def test_string_only_returns_false(self):
        src = b'key = "hello"\n'
        assert toml_has_at_least_one_numeric(src) is False

    def test_float_counts_as_numeric(self):
        src = b"pi = 3.14\n"
        assert toml_has_at_least_one_numeric(src) is True
