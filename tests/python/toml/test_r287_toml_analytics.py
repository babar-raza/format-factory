"""
Tests for TOML additional analytics (2 new FOSS functions).
Closes: GAP-TOML-FOSS-HAS_NUMERIC-001, GAP-TOML-FOSS-AVG_LIST-001

Known inline values:
  toml_has_numeric_values:
    b'' → False
    b'name="Alice"\n' → False (string only)
    b'name="Bob"\nage=42\n' → True
    b'flag=true\n' → False (bool excluded)
  toml_avg_list_length:
    b'' → 0.0
    b'items=[1,2,3]\n' → 3.0
    b'a=[1,2,3]\nb=[4,5]\n' → 2.5
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from toml.toml_codec import toml_has_numeric_values, toml_avg_list_length

_EMPTY = b""
_TEXT_ONLY = b'name="Alice"\n'
_WITH_INT = b'name="Bob"\nage=42\n'
_BOOL_ONLY = b'flag=true\n'
_WITH_FLOAT = b'pi=3.14\n'
_TWO_LISTS = b'a=[1,2,3]\nb=[4,5]\n'
_ONE_LIST = b'items=[1,2,3]\n'
_NO_LISTS = b'name="Dave"\n'


class TestTomlHasNumericValues:
    def test_returns_bool(self):
        assert isinstance(toml_has_numeric_values(_EMPTY), bool)

    def test_empty_doc_is_false(self):
        assert toml_has_numeric_values(_EMPTY) is False

    def test_text_only_is_false(self):
        assert toml_has_numeric_values(_TEXT_ONLY) is False

    def test_with_int_is_true(self):
        assert toml_has_numeric_values(_WITH_INT) is True

    def test_bool_only_is_false(self):
        # booleans excluded from numeric check
        assert toml_has_numeric_values(_BOOL_ONLY) is False

    def test_with_float_is_true(self):
        assert toml_has_numeric_values(_WITH_FLOAT) is True

    def test_all_return_bool(self):
        for src in [_EMPTY, _TEXT_ONLY, _WITH_INT, _BOOL_ONLY, _WITH_FLOAT]:
            result = toml_has_numeric_values(src)
            assert result is True or result is False

    def test_mixed_has_numeric(self):
        assert toml_has_numeric_values(b'name="Carol"\ncount=7\n') is True


class TestTomlAvgListLength:
    def test_returns_float(self):
        assert isinstance(toml_avg_list_length(_EMPTY), float)

    def test_empty_doc_is_zero(self):
        assert toml_avg_list_length(_EMPTY) == 0.0

    def test_no_lists_is_zero(self):
        assert toml_avg_list_length(_NO_LISTS) == 0.0

    def test_single_list_avg(self):
        # [1,2,3] → avg=3.0
        assert toml_avg_list_length(_ONE_LIST) == 3.0

    def test_two_lists_avg(self):
        # [1,2,3]=3 and [4,5]=2 → avg=2.5
        assert toml_avg_list_length(_TWO_LISTS) == 2.5

    def test_empty_list_avg_zero(self):
        assert toml_avg_list_length(b'items=[]\n') == 0.0

    def test_nonnegative(self):
        for src in [_EMPTY, _ONE_LIST, _TWO_LISTS, _NO_LISTS]:
            assert toml_avg_list_length(src) >= 0.0

    def test_all_return_float(self):
        for src in [_EMPTY, _ONE_LIST, _TWO_LISTS, _NO_LISTS]:
            assert isinstance(toml_avg_list_length(src), float)
