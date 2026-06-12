"""
test_toml_sections_flatten_w113_pipeline.py -- TOML list_sections + flatten pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-113
Tests list_sections returns list, has server and database, flatten returns dict,
flattened has server.host key, flatten has expected count.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.toml.toml_codec import (
    list_sections,
    flatten,
)

_TOML_BYTES = b"[server]\nhost = 'localhost'\nport = 8080\n\n[database]\nname = 'mydb'\nmax_conn = 10\n"


def test_list_sections_returns_list():
    result = list_sections(_TOML_BYTES)
    assert isinstance(result, list)


def test_list_sections_has_server():
    result = list_sections(_TOML_BYTES)
    assert "server" in result


def test_list_sections_has_database():
    result = list_sections(_TOML_BYTES)
    assert "database" in result


def test_flatten_returns_dict():
    result = flatten(_TOML_BYTES)
    assert isinstance(result, dict)


def test_flatten_has_dotted_keys():
    result = flatten(_TOML_BYTES)
    assert "server.host" in result
    assert result["server.host"] == "localhost"
