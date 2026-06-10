"""
test_r154_toml_section_keys.py

Sprint: FORMAT-FACTORY-MAINSTREAM-PRODUCT-DEEPENING-RNEXT12-001
Added: 2026-06-09

Tests for TOML get_section_keys, has_key, and count_keys functions.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.toml.toml_codec import get_section_keys, has_key, count_keys


SAMPLE_TOML = b"""\
title = "Sample"
version = 1

[server]
host = "localhost"
port = 8080

[database]
url = "postgres://localhost/db"
pool_size = 5

[database.primary]
host = "primary.db"
"""


class TestGetSectionKeys:
    """get_section_keys: return keys within a TOML section."""

    def test_top_level_section(self):
        keys = get_section_keys(SAMPLE_TOML, "server")
        assert "host" in keys
        assert "port" in keys

    def test_nested_section(self):
        keys = get_section_keys(SAMPLE_TOML, "database.primary")
        assert keys == ["host"]

    def test_section_with_subsections(self):
        keys = get_section_keys(SAMPLE_TOML, "database")
        assert "url" in keys
        assert "pool_size" in keys

    def test_nonexistent_section_raises(self):
        with pytest.raises(KeyError):
            get_section_keys(SAMPLE_TOML, "nonexistent")

    def test_scalar_key_raises(self):
        with pytest.raises(KeyError):
            get_section_keys(SAMPLE_TOML, "title")


class TestHasKey:
    """has_key: check if a dotted key path exists in TOML."""

    def test_top_level_key_exists(self):
        assert has_key(SAMPLE_TOML, "title") is True

    def test_nested_key_exists(self):
        assert has_key(SAMPLE_TOML, "server.host") is True

    def test_deeply_nested_key_exists(self):
        assert has_key(SAMPLE_TOML, "database.primary.host") is True

    def test_nonexistent_key(self):
        assert has_key(SAMPLE_TOML, "missing") is False

    def test_nonexistent_nested_key(self):
        assert has_key(SAMPLE_TOML, "server.missing") is False

    def test_section_itself_is_a_key(self):
        assert has_key(SAMPLE_TOML, "server") is True


class TestCountKeys:
    """count_keys: count keys in a TOML document."""

    def test_top_level_count(self):
        count = count_keys(SAMPLE_TOML)
        assert count == 4  # title, version, server, database

    def test_recursive_count(self):
        count = count_keys(SAMPLE_TOML, recursive=True)
        # title(1) + version(1) + server(1) + server.host(1) + server.port(1)
        # + database(1) + database.url(1) + database.pool_size(1)
        # + database.primary(1) + database.primary.host(1) = 10
        assert count == 10

    def test_simple_toml(self):
        simple = b'a = 1\nb = 2\n'
        assert count_keys(simple) == 2

    def test_simple_toml_recursive_same_as_non_recursive(self):
        simple = b'a = 1\nb = 2\n'
        assert count_keys(simple, recursive=True) == 2

    def test_empty_toml(self):
        assert count_keys(b'') == 0
