"""
tests/python/abw/test_r270_abw_workflow.py

Sprint: ff-sprint-s270-abw-installed-workflow-20260626
Authority: FACT-ABW-001 (AbiWord XML document format)

Tests for abw_installed_workflow() in abw_codec.py.
"""
from __future__ import annotations

from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_SAMPLE = _REPO / "samples" / "by-format" / "abw" / "minimal-document.abw"
_TWO_PARA = _REPO / "samples" / "by-format" / "abw" / "two-paragraphs.abw"


class TestAbwInstalledWorkflowImport:
    """abw_installed_workflow is importable and callable."""

    def test_importable_from_abw_codec(self):
        from abw.abw_codec import abw_installed_workflow
        assert callable(abw_installed_workflow)

    def test_importable_from_package(self):
        import abw
        assert hasattr(abw, "abw_installed_workflow")


class TestAbwInstalledWorkflowOutput:
    """abw_installed_workflow returns correct output structure."""

    def test_returns_dict(self):
        from abw.abw_codec import abw_installed_workflow
        result = abw_installed_workflow(str(_SAMPLE))
        assert isinstance(result, dict)

    def test_format_field_is_abw(self):
        from abw.abw_codec import abw_installed_workflow
        result = abw_installed_workflow(str(_SAMPLE))
        assert result["format"] == "abw"

    def test_loaded_field_is_true(self):
        from abw.abw_codec import abw_installed_workflow
        result = abw_installed_workflow(str(_SAMPLE))
        assert result["loaded"] is True

    def test_paragraph_count_is_integer(self):
        from abw.abw_codec import abw_installed_workflow
        result = abw_installed_workflow(str(_SAMPLE))
        assert isinstance(result["paragraph_count"], int)

    def test_section_count_is_integer(self):
        from abw.abw_codec import abw_installed_workflow
        result = abw_installed_workflow(str(_SAMPLE))
        assert isinstance(result["section_count"], int)

    def test_has_all_required_keys(self):
        from abw.abw_codec import abw_installed_workflow
        result = abw_installed_workflow(str(_SAMPLE))
        assert {"format", "loaded", "paragraph_count", "section_count"}.issubset(result.keys())

    def test_consistent_across_calls(self):
        from abw.abw_codec import abw_installed_workflow
        r1 = abw_installed_workflow(str(_SAMPLE))
        r2 = abw_installed_workflow(str(_SAMPLE))
        assert r1["paragraph_count"] == r2["paragraph_count"]
        assert r1["section_count"] == r2["section_count"]

    def test_two_paragraphs_doc(self):
        from abw.abw_codec import abw_installed_workflow
        result = abw_installed_workflow(str(_TWO_PARA))
        assert result["loaded"] is True
        assert result["paragraph_count"] >= 2

    def test_bytes_input_works(self):
        from abw.abw_codec import abw_installed_workflow
        content = _SAMPLE.read_bytes()
        result = abw_installed_workflow(content)
        assert result["loaded"] is True
        assert result["format"] == "abw"
