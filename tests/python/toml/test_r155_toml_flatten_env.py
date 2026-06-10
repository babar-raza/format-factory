"""
test_r155_toml_flatten_env.py

Sprint: FORMAT-FACTORY-MAINSTREAM-PRODUCT-DEEPENING-RNEXT13-001
Added: 2026-06-09

Tests for TOML flatten and to_env functions.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.toml.toml_codec import flatten, to_env


SAMPLE_TOML = b"""\
title = "Config"
debug = true

[server]
host = "localhost"
port = 8080

[database]
url = "postgres://db"

[database.pool]
size = 10
"""


class TestFlatten:
    """flatten: collapse nested TOML into flat dotted-key dict."""

    def test_top_level_keys(self):
        flat = flatten(SAMPLE_TOML)
        assert flat["title"] == "Config"
        assert flat["debug"] is True

    def test_nested_keys(self):
        flat = flatten(SAMPLE_TOML)
        assert flat["server.host"] == "localhost"
        assert flat["server.port"] == 8080

    def test_deeply_nested(self):
        flat = flatten(SAMPLE_TOML)
        assert flat["database.pool.size"] == 10

    def test_custom_separator(self):
        flat = flatten(SAMPLE_TOML, separator="/")
        assert "server/host" in flat
        assert flat["server/port"] == 8080

    def test_no_dict_values_in_output(self):
        flat = flatten(SAMPLE_TOML)
        for v in flat.values():
            assert not isinstance(v, dict)

    def test_empty_toml(self):
        flat = flatten(b"")
        assert flat == {}


class TestToEnv:
    """to_env: export TOML as environment variable assignments."""

    def test_basic_output(self):
        env = to_env(SAMPLE_TOML)
        assert "TITLE=Config" in env
        assert "DEBUG=true" in env

    def test_nested_keys_use_underscore(self):
        env = to_env(SAMPLE_TOML)
        assert "SERVER_HOST=localhost" in env
        assert "SERVER_PORT=8080" in env

    def test_prefix(self):
        env = to_env(SAMPLE_TOML, prefix="APP")
        assert "APP_TITLE=Config" in env
        assert "APP_SERVER_HOST=localhost" in env

    def test_no_uppercase(self):
        env = to_env(SAMPLE_TOML, uppercase=False)
        assert "title=Config" in env
        assert "server_host=localhost" in env

    def test_empty_toml(self):
        env = to_env(b"")
        assert env == ""

    def test_multiline_format(self):
        env = to_env(SAMPLE_TOML)
        lines = env.strip().split("\n")
        assert len(lines) >= 5
        for line in lines:
            assert "=" in line
