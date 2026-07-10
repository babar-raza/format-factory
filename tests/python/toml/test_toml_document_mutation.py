"""TomlDocument mutation API tests: set_key, delete_key, to_toml_string, save_to_file.

Sprint: FOSS-TOML-MUTATION-001
Adds model-based mutation API to TomlDocument (parallel to SYLK/NDJSON mutation pattern).
"""
from __future__ import annotations

from pathlib import Path

import pytest

SAMPLE = Path(__file__).parent.parent.parent.parent / "samples" / "by-format" / "toml" / "minimal.toml"


def _load() -> "object":
    """Load a fresh TomlDocument from the sample file."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src" / "python"))
    from toml.models import TomlDocument
    return TomlDocument.from_file(SAMPLE)


# ─────────────────────────────────────────────────────────────────────────────
# set_key
# ─────────────────────────────────────────────────────────────────────────────

class TestSetKey:
    def test_set_existing_top_level_key(self):
        doc = _load()
        doc.set_key("version", "9.9.9")
        assert doc.get("version") == "9.9.9"

    def test_set_creates_new_key(self):
        doc = _load()
        doc.set_key("new_field", "hello")
        assert doc.get("new_field") == "hello"

    def test_set_key_count_increases_for_new_key(self):
        doc = _load()
        before = doc.key_count
        doc.set_key("brand_new", 42)
        assert doc.key_count == before + 1

    def test_set_nested_key(self):
        doc = _load()
        doc.set_key("server.port", 9999)
        assert doc.get("server")["port"] == 9999

    def test_set_bool_value(self):
        doc = _load()
        doc.set_key("enabled", False)
        assert doc.get("enabled") is False


# ─────────────────────────────────────────────────────────────────────────────
# delete_key
# ─────────────────────────────────────────────────────────────────────────────

class TestDeleteKey:
    def test_delete_existing_key(self):
        doc = _load()
        assert doc.has_key("title")
        doc.delete_key("title")
        assert not doc.has_key("title")

    def test_delete_reduces_key_count(self):
        doc = _load()
        before = doc.key_count
        doc.delete_key("version")
        assert doc.key_count == before - 1


# ─────────────────────────────────────────────────────────────────────────────
# to_toml_string
# ─────────────────────────────────────────────────────────────────────────────

class TestToTomlString:
    def test_produces_string(self):
        doc = _load()
        s = doc.to_toml_string()
        assert isinstance(s, str)
        assert len(s) > 0

    def test_contains_key_values(self):
        doc = _load()
        doc.set_key("version", "5.0.0")
        s = doc.to_toml_string()
        assert "5.0.0" in s

    def test_is_lf_terminated(self):
        doc = _load()
        s = doc.to_toml_string()
        assert s.endswith("\n")


# ─────────────────────────────────────────────────────────────────────────────
# save_to_file
# ─────────────────────────────────────────────────────────────────────────────

class TestSaveToFile:
    def test_save_creates_file(self, tmp_path):
        doc = _load()
        path = tmp_path / "out.toml"
        doc.save_to_file(path)
        assert path.exists()

    def test_save_empty_path_raises(self):
        from toml.exceptions import TomlError
        doc = _load()
        with pytest.raises(TomlError):
            doc.save_to_file("")

    def test_save_creates_parent_dirs(self, tmp_path):
        doc = _load()
        nested = tmp_path / "a" / "b" / "out.toml"
        doc.save_to_file(nested)
        assert nested.exists()


# ─────────────────────────────────────────────────────────────────────────────
# Roundtrip: set_key → save_to_file → from_file → assert
# ─────────────────────────────────────────────────────────────────────────────

class TestMutationRoundtrip:
    def test_set_key_roundtrip(self, tmp_path):
        from toml.models import TomlDocument
        doc = _load()
        doc.set_key("version", "99.0.0")
        path = tmp_path / "roundtrip.toml"
        doc.save_to_file(path)
        doc2 = TomlDocument.from_file(path)
        assert doc2.get("version") == "99.0.0"

    def test_delete_key_roundtrip(self, tmp_path):
        from toml.models import TomlDocument
        doc = _load()
        assert doc.has_key("title")
        doc.delete_key("title")
        path = tmp_path / "del_roundtrip.toml"
        doc.save_to_file(path)
        doc2 = TomlDocument.from_file(path)
        assert not doc2.has_key("title")
