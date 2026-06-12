"""
Tests for TOML update_section() — merges key/value pairs into a specific section.

Sprint: FORMAT-FACTORY-SELF-HEALING-PRODUCT-DEEPENING-RNEXT
Taskcard: PD-Q-001
Queue item: pdrnext-q-001
Execution method: QUEUE_DISPATCHED_EXECUTION
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.toml.toml_codec import update_section  # noqa: E402


def test_update_section_returns_dict():
    data = {"section": {"a": 1}}
    result = update_section(data, "section", {"b": 2})
    assert isinstance(result, dict)


def test_update_section_merges_new_key():
    data = {"section": {"a": 1}}
    result = update_section(data, "section", {"b": 2})
    assert result["section"]["a"] == 1
    assert result["section"]["b"] == 2


def test_update_section_overwrites_existing_key():
    data = {"section": {"a": 1, "b": 2}}
    result = update_section(data, "section", {"a": 99})
    assert result["section"]["a"] == 99
    assert result["section"]["b"] == 2


def test_update_section_does_not_mutate_original():
    data = {"section": {"a": 1}}
    update_section(data, "section", {"b": 2})
    assert "b" not in data["section"]


def test_update_section_creates_missing_section():
    data = {"other": {"x": 1}}
    result = update_section(data, "new_section", {"k": "v"})
    assert result["new_section"] == {"k": "v"}
    assert result["other"] == {"x": 1}


def test_update_section_other_sections_unchanged():
    data = {"a": {"x": 1}, "b": {"y": 2}}
    result = update_section(data, "a", {"z": 3})
    assert result["b"] == {"y": 2}


def test_update_section_empty_updates():
    data = {"section": {"a": 1}}
    result = update_section(data, "section", {})
    assert result["section"] == {"a": 1}


def test_update_section_non_dict_section_raises():
    data = {"section": "not-a-dict"}
    with pytest.raises(TypeError):
        update_section(data, "section", {"k": "v"})


def test_update_section_multiple_keys():
    data = {"cfg": {"host": "localhost"}}
    result = update_section(data, "cfg", {"port": 8080, "debug": True})
    assert result["cfg"]["host"] == "localhost"
    assert result["cfg"]["port"] == 8080
    assert result["cfg"]["debug"] is True


def test_update_section_importable_from_package():
    from src.python.toml import update_section as fn
    assert callable(fn)
