"""
tests/python/toml/test_r289_toml_workflow.py

Sprint: ff-sprint-s289-toml-installed-workflow-20260626
Authority: TOML v1.0.0 specification

Tests for toml_installed_workflow() in toml_workflow.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_SAMPLE = _REPO / "samples" / "by-format" / "toml" / "minimal.toml"


class TestTomlInstalledWorkflowImport:
    def test_importable_from_toml_workflow(self):
        from toml.toml_workflow import toml_installed_workflow
        assert callable(toml_installed_workflow)

    def test_importable_from_package(self):
        import toml as toml
        assert hasattr(toml, "toml_installed_workflow")


class TestTomlInstalledWorkflowOutput:
    def test_returns_dict(self):
        from toml.toml_workflow import toml_installed_workflow
        assert isinstance(toml_installed_workflow(str(_SAMPLE)), dict)

    def test_format_field(self):
        from toml.toml_workflow import toml_installed_workflow
        assert toml_installed_workflow(str(_SAMPLE))["format"] == "toml"

    def test_loaded_true(self):
        from toml.toml_workflow import toml_installed_workflow
        assert toml_installed_workflow(str(_SAMPLE))["loaded"] is True

    def test_key_count_integer(self):
        from toml.toml_workflow import toml_installed_workflow
        assert isinstance(toml_installed_workflow(str(_SAMPLE))["key_count"], int)

    def test_section_count_integer(self):
        from toml.toml_workflow import toml_installed_workflow
        assert isinstance(toml_installed_workflow(str(_SAMPLE))["section_count"], int)

    def test_has_required_keys(self):
        from toml.toml_workflow import toml_installed_workflow
        r = toml_installed_workflow(str(_SAMPLE))
        assert {"format", "loaded", "key_count", "section_count"}.issubset(r.keys())

    def test_consistent(self):
        from toml.toml_workflow import toml_installed_workflow
        r1 = toml_installed_workflow(str(_SAMPLE))
        r2 = toml_installed_workflow(str(_SAMPLE))
        assert r1["key_count"] == r2["key_count"]
