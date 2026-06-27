"""
tests/python/toml/test_r266_toml_installed_workflow.py

Closes gap: GAP-TOML-FOSS-INSTALLED_WO-001
Sprint: ff-sprint-s266-toml-installed-workflow-20260626
Authority: FACT-TOML-001, FACT-TOML-002, FACT-TOML-003

Tests for toml_installed_workflow() in toml_codec.py.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
_SAMPLE = _REPO / "samples" / "by-format" / "toml" / "minimal.toml"


class TestTomlInstalledWorkflowImport:
    """toml_installed_workflow is importable and callable."""

    def test_importable_from_toml_codec(self):
        from toml.toml_codec import toml_installed_workflow
        assert callable(toml_installed_workflow)

    def test_importable_from_package(self):
        import toml
        assert hasattr(toml, "toml_installed_workflow")
        assert callable(toml.toml_installed_workflow)


class TestTomlInstalledWorkflowOutput:
    """toml_installed_workflow returns correct output structure."""

    def test_returns_dict(self):
        from toml.toml_codec import toml_installed_workflow
        result = toml_installed_workflow(str(_SAMPLE))
        assert isinstance(result, dict)

    def test_format_field_is_toml(self):
        from toml.toml_codec import toml_installed_workflow
        result = toml_installed_workflow(str(_SAMPLE))
        assert result["format"] == "toml"

    def test_loaded_field_is_true(self):
        from toml.toml_codec import toml_installed_workflow
        result = toml_installed_workflow(str(_SAMPLE))
        assert result["loaded"] is True

    def test_key_count_is_integer(self):
        from toml.toml_codec import toml_installed_workflow
        result = toml_installed_workflow(str(_SAMPLE))
        assert isinstance(result["key_count"], int)

    def test_key_count_is_positive(self):
        from toml.toml_codec import toml_installed_workflow
        result = toml_installed_workflow(str(_SAMPLE))
        assert result["key_count"] > 0

    def test_result_has_required_keys(self):
        from toml.toml_codec import toml_installed_workflow
        result = toml_installed_workflow(str(_SAMPLE))
        assert "format" in result
        assert "loaded" in result
        assert "key_count" in result


class TestTomlInstalledWorkflowWithBytes:
    """toml_installed_workflow works with bytes input."""

    def test_bytes_input_returns_dict(self):
        from toml.toml_codec import toml_installed_workflow
        content = _SAMPLE.read_bytes()
        result = toml_installed_workflow(content)
        assert isinstance(result, dict)
        assert result["loaded"] is True

    def test_bytes_key_count_matches_file(self):
        from toml.toml_codec import toml_installed_workflow
        file_result = toml_installed_workflow(str(_SAMPLE))
        bytes_result = toml_installed_workflow(_SAMPLE.read_bytes())
        assert file_result["key_count"] == bytes_result["key_count"]


class TestTomlInstalledWorkflowRoundtrip:
    """toml_installed_workflow works after write roundtrip."""

    def test_write_then_installed_workflow(self):
        from toml.toml_codec import load_toml, write_toml, toml_installed_workflow
        model = load_toml(str(_SAMPLE))
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            write_toml(model["data"], tmp_path)
            result = toml_installed_workflow(tmp_path)
            assert result["loaded"] is True
            assert result["format"] == "toml"
            assert result["key_count"] == model["key_count"]
        finally:
            os.unlink(tmp_path)

    def test_consistent_across_calls(self):
        from toml.toml_codec import toml_installed_workflow
        r1 = toml_installed_workflow(str(_SAMPLE))
        r2 = toml_installed_workflow(str(_SAMPLE))
        assert r1["key_count"] == r2["key_count"]
        assert r1["format"] == r2["format"]
        assert r1["loaded"] == r2["loaded"]
