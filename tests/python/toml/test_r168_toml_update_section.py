"""
test_r168_toml_update_section.py -- Tests for update_section.

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT22
Closes: GAP-TOML-FOSS-UPDATE_SECTION-001
"""
from __future__ import annotations

from pathlib import Path
import sys

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest
from src.python.toml.toml_codec import update_section


class TestUpdateSection:
    def test_update_existing_section(self):
        data = {"server": {"host": "localhost", "port": 8080}, "db": {"name": "test"}}
        result = update_section(data, "server", {"port": 9090, "debug": True})
        assert result["server"]["port"] == 9090
        assert result["server"]["debug"] is True
        assert result["server"]["host"] == "localhost"

    def test_create_missing_section(self):
        data = {"existing": {"key": "val"}}
        result = update_section(data, "new_section", {"a": 1, "b": 2})
        assert result["new_section"] == {"a": 1, "b": 2}
        assert "existing" in result

    def test_original_not_mutated(self):
        data = {"section": {"key": "original"}}
        result = update_section(data, "section", {"key": "updated"})
        assert data["section"]["key"] == "original"
        assert result["section"]["key"] == "updated"

    def test_other_sections_unchanged(self):
        data = {"a": {"x": 1}, "b": {"y": 2}}
        result = update_section(data, "a", {"z": 3})
        assert result["b"] == {"y": 2}

    def test_empty_updates_returns_same_section(self):
        data = {"section": {"key": "val"}}
        result = update_section(data, "section", {})
        assert result["section"] == {"key": "val"}

    def test_type_error_on_non_dict_section(self):
        data = {"section": "not_a_dict"}
        with pytest.raises(TypeError):
            update_section(data, "section", {"key": "val"})

    def test_updates_override_existing_keys(self):
        data = {"cfg": {"a": 1, "b": 2, "c": 3}}
        result = update_section(data, "cfg", {"b": 99})
        assert result["cfg"]["a"] == 1
        assert result["cfg"]["b"] == 99
        assert result["cfg"]["c"] == 3

    def test_empty_data_creates_section(self):
        result = update_section({}, "new", {"key": "val"})
        assert result["new"] == {"key": "val"}
