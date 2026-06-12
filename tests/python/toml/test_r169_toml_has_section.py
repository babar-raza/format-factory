"""R169 — TOML has_section function tests."""
from __future__ import annotations

import pytest
from pathlib import Path

from src.python.toml.toml_codec import has_section

PYPROJECT = Path("pyproject.toml")


class TestHasSection:
    def test_existing_section_returns_true(self):
        toml_bytes = b"[tool]\nname = \"x\"\n"
        assert has_section(toml_bytes, "tool") is True

    def test_missing_section_returns_false(self):
        toml_bytes = b"[tool]\nname = \"x\"\n"
        assert has_section(toml_bytes, "nonexistent") is False

    def test_returns_bool(self):
        toml_bytes = b"[db]\nhost = \"localhost\"\n"
        assert isinstance(has_section(toml_bytes, "db"), bool)

    def test_non_section_key_returns_false(self):
        # Scalar keys are not sections (not dicts)
        toml_bytes = b"version = \"1.0\"\n"
        assert has_section(toml_bytes, "version") is False

    def test_multiple_sections(self):
        toml_bytes = b"[dev]\nfoo = 1\n[prod]\nfoo = 2\n"
        assert has_section(toml_bytes, "dev") is True
        assert has_section(toml_bytes, "prod") is True
        assert has_section(toml_bytes, "staging") is False

    def test_string_source(self):
        # load_toml treats str as file path; use bytes for raw content
        toml_bytes = b"[server]\nport = 8080\n"
        assert has_section(toml_bytes, "server") is True

    def test_pyproject_has_project(self):
        if not PYPROJECT.exists():
            pytest.skip("pyproject.toml not found")
        result = has_section(PYPROJECT, "project")
        assert isinstance(result, bool)

    def test_empty_toml_returns_false(self):
        assert has_section(b"", "section") is False
