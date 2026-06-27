"""
tests/python/ndjson/test_r288_ndjson_installed_workflow.py

Sprint: ff-sprint-s288-ndjson-installed-workflow-20260626
Authority: NDJSON / JSONL format spec

Tests for ndjson_installed_workflow() in ndjson_workflow.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_SAMPLE = _REPO / "samples" / "by-format" / "ndjson" / "valid" / "minimal.ndjson"


class TestNdjsonInstalledWorkflowImport:
    def test_importable_from_ndjson_workflow(self):
        from ndjson.ndjson_workflow import ndjson_installed_workflow
        assert callable(ndjson_installed_workflow)

    def test_importable_from_package(self):
        import ndjson
        assert hasattr(ndjson, "ndjson_installed_workflow")


class TestNdjsonInstalledWorkflowOutput:
    def test_returns_dict(self):
        from ndjson.ndjson_workflow import ndjson_installed_workflow
        assert isinstance(ndjson_installed_workflow(str(_SAMPLE)), dict)

    def test_format_field(self):
        from ndjson.ndjson_workflow import ndjson_installed_workflow
        assert ndjson_installed_workflow(str(_SAMPLE))["format"] == "ndjson"

    def test_loaded_true(self):
        from ndjson.ndjson_workflow import ndjson_installed_workflow
        assert ndjson_installed_workflow(str(_SAMPLE))["loaded"] is True

    def test_record_count_integer(self):
        from ndjson.ndjson_workflow import ndjson_installed_workflow
        assert isinstance(ndjson_installed_workflow(str(_SAMPLE))["record_count"], int)

    def test_has_required_keys(self):
        from ndjson.ndjson_workflow import ndjson_installed_workflow
        r = ndjson_installed_workflow(str(_SAMPLE))
        assert {"format", "loaded", "record_count"}.issubset(r.keys())

    def test_minimal_has_records(self):
        from ndjson.ndjson_workflow import ndjson_installed_workflow
        r = ndjson_installed_workflow(str(_SAMPLE))
        assert r["record_count"] >= 1

    def test_consistent(self):
        from ndjson.ndjson_workflow import ndjson_installed_workflow
        r1 = ndjson_installed_workflow(str(_SAMPLE))
        r2 = ndjson_installed_workflow(str(_SAMPLE))
        assert r1["record_count"] == r2["record_count"]
