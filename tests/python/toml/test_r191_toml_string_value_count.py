"""
tests/python/toml/test_r191_toml_string_value_count.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT60-001
Tests for toml_string_value_count() — count of top-level string values.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.toml import toml_string_value_count


class TestTomlStringValueCount:
    def test_all_string_values(self):
        """All values are strings → count equals number of keys."""
        toml_bytes = b'name = "Alice"\ncity = "Paris"\n'
        assert toml_string_value_count(toml_bytes) == 2

    def test_no_string_values(self):
        """No string values (only int/bool/list) → count is 0."""
        toml_bytes = b'count = 42\nflag = true\n'
        assert toml_string_value_count(toml_bytes) == 0

    def test_mixed_types(self):
        """Mixed types → only string values counted."""
        toml_bytes = b'name = "Bob"\nage = 30\ncity = "London"\n'
        assert toml_string_value_count(toml_bytes) == 2

    def test_section_values_not_counted(self):
        """Nested section dict values are not counted as strings."""
        toml_bytes = b'title = "Doc"\n[meta]\nauthor = "Alice"\n'
        # Only top-level 'title' is a string; 'meta' is a dict
        assert toml_string_value_count(toml_bytes) == 1

    def test_empty_toml_returns_zero(self):
        """Empty TOML document → 0."""
        assert toml_string_value_count(b"") == 0

    def test_result_is_int(self):
        """Result is always an integer."""
        result = toml_string_value_count(b'x = "hello"\n')
        assert isinstance(result, int)
