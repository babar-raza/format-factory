"""
test_toml_getvalue_hassection_w117_pipeline.py -- TOML get_value + has_section pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-117
Tests get_value returns expected string, get_value numeric, has_section returns bool,
has_section finds existing section, has_section returns False for missing section.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.toml.toml_codec import (
    get_value,
    has_section,
)

_TOML_BYTES = b"[server]\nhost = 'localhost'\nport = 8080\n\n[database]\nname = 'mydb'\nmax_conn = 10\n"


def test_get_value_returns_string():
    result = get_value(_TOML_BYTES, "server.host")
    assert result == "localhost"


def test_get_value_numeric():
    result = get_value(_TOML_BYTES, "server.port")
    assert result == 8080


def test_has_section_returns_bool():
    result = has_section(_TOML_BYTES, "server")
    assert isinstance(result, bool)


def test_has_section_existing():
    result = has_section(_TOML_BYTES, "database")
    assert result is True


def test_has_section_missing():
    result = has_section(_TOML_BYTES, "nonexistent_section")
    assert result is False
