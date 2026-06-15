"""Product deepening tests for TOML section analytics.

Tests count_values_in_section, has_any_section, toml_list_count,
toml_string_value_count, count_sections_with_key.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.toml import (
    has_any_section,
    count_values_in_section,
    toml_list_count,
    toml_string_value_count,
    count_sections_with_key,
)

_TOML_WITH_SECTIONS = b"""\
title = "Test Config"
tags = ["alpha", "beta"]

[database]
host = "localhost"
port = 5432
enabled = true

[logging]
level = "debug"
file = "/var/log/app.log"
"""

_TOML_FLAT = b"""\
name = "flat"
version = "1.0"
count = 42
"""


class TestHasAnySection:
    def test_with_sections(self):
        assert has_any_section(_TOML_WITH_SECTIONS) is True

    def test_without_sections(self):
        assert has_any_section(_TOML_FLAT) is False


class TestCountValuesInSection:
    def test_database_section(self):
        count = count_values_in_section(_TOML_WITH_SECTIONS, "database")
        assert count == 3  # host, port, enabled

    def test_logging_section(self):
        count = count_values_in_section(_TOML_WITH_SECTIONS, "logging")
        assert count == 2  # level, file

    def test_missing_section(self):
        count = count_values_in_section(_TOML_WITH_SECTIONS, "nonexistent")
        assert count == 0


class TestTomlListCount:
    def test_has_lists(self):
        count = toml_list_count(_TOML_WITH_SECTIONS)
        assert count == 1  # tags = [...]

    def test_no_lists(self):
        count = toml_list_count(_TOML_FLAT)
        assert count == 0


class TestTomlStringValueCount:
    def test_string_values(self):
        count = toml_string_value_count(_TOML_FLAT)
        assert count >= 2  # "flat", "1.0"

    def test_mixed_values(self):
        count = toml_string_value_count(_TOML_WITH_SECTIONS)
        assert count >= 1  # "Test Config"


class TestCountSectionsWithKey:
    def test_key_in_multiple_sections(self):
        toml_data = b"""\
[a]
name = "first"

[b]
name = "second"

[c]
other = "value"
"""
        count = count_sections_with_key(toml_data, "name")
        assert count == 2  # sections a and b

    def test_key_in_no_sections(self):
        count = count_sections_with_key(_TOML_WITH_SECTIONS, "nonexistent_key")
        assert count == 0
