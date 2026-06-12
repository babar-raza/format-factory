"""R170 — TOML get_section_as_dict and has_any_section tests.

Sprint: FORMAT-FACTORY-PROOF-CLOSED-SELF-HEALING-PROFESSIONALIZE-PRODUCT-READINESS-RNEXT-001
"""
from __future__ import annotations

import pytest

from src.python.toml.toml_codec import get_section_as_dict, has_any_section

_TOML_WITH_SECTIONS = b"""
[server]
host = "localhost"
port = 8080

[database]
name = "mydb"
user = "admin"

top_key = "value"
"""

_TOML_NO_SECTIONS = b"""
name = "simple"
version = 1
flag = true
"""

_TOML_EMPTY = b""


class TestGetSectionAsDict:
    def test_returns_existing_section(self):
        result = get_section_as_dict(_TOML_WITH_SECTIONS, "server")
        assert result == {"host": "localhost", "port": 8080}

    def test_returns_second_section(self):
        result = get_section_as_dict(_TOML_WITH_SECTIONS, "database")
        assert result["name"] == "mydb"
        assert result["user"] == "admin"

    def test_missing_section_returns_empty_dict(self):
        result = get_section_as_dict(_TOML_WITH_SECTIONS, "nonexistent")
        assert result == {}

    def test_non_dict_key_returns_empty(self):
        """top_key is a string, not a dict → returns {}."""
        result = get_section_as_dict(_TOML_WITH_SECTIONS, "top_key")
        assert result == {}

    def test_empty_toml_returns_empty(self):
        result = get_section_as_dict(_TOML_EMPTY, "anything")
        assert result == {}

    def test_returns_dict_type(self):
        result = get_section_as_dict(_TOML_WITH_SECTIONS, "server")
        assert isinstance(result, dict)

    def test_function_in_all(self):
        from src.python.toml import __all__ as toml_all
        assert "get_section_as_dict" in toml_all


class TestHasAnySection:
    def test_true_when_sections_exist(self):
        assert has_any_section(_TOML_WITH_SECTIONS) is True

    def test_false_when_only_scalars(self):
        assert has_any_section(_TOML_NO_SECTIONS) is False

    def test_false_on_empty_toml(self):
        assert has_any_section(_TOML_EMPTY) is False

    def test_returns_bool(self):
        result = has_any_section(_TOML_WITH_SECTIONS)
        assert isinstance(result, bool)

    def test_function_in_all(self):
        from src.python.toml import __all__ as toml_all
        assert "has_any_section" in toml_all
