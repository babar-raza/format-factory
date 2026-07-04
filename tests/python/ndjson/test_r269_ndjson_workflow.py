"""
tests/python/ndjson/test_r269_ndjson_installed_workflow.py

Sprint: ff-sprint-s269-tsv-ndjson-installed-workflow-20260626
Authority: ndjson.org NDJSON specification

Tests for ndjson_installed_workflow() in ndjson_codec.py.
"""
from __future__ import annotations

import pytest

_NDJSON_BYTES = (
    b'{"name": "Alice", "age": 30, "city": "London"}\n'
    b'{"name": "Bob", "age": 25, "city": "Paris"}\n'
    b'{"name": "Carol", "age": 35, "city": "Berlin"}\n'
)


class TestNdjsonInstalledWorkflowImport:
    """ndjson_installed_workflow is importable and callable."""

    def test_importable_from_ndjson_codec(self):
        from ndjson.ndjson_codec import ndjson_installed_workflow
        assert callable(ndjson_installed_workflow)

    def test_importable_from_package(self):
        import ndjson
        assert hasattr(ndjson, "ndjson_installed_workflow")


class TestNdjsonInstalledWorkflowOutput:
    """ndjson_installed_workflow returns correct output structure."""

    def test_returns_dict(self):
        from ndjson.ndjson_codec import ndjson_installed_workflow
        result = ndjson_installed_workflow(_NDJSON_BYTES)
        assert isinstance(result, dict)

    def test_format_field_is_ndjson(self):
        from ndjson.ndjson_codec import ndjson_installed_workflow
        result = ndjson_installed_workflow(_NDJSON_BYTES)
        assert result["format"] == "ndjson"

    def test_loaded_field_is_true(self):
        from ndjson.ndjson_codec import ndjson_installed_workflow
        result = ndjson_installed_workflow(_NDJSON_BYTES)
        assert result["loaded"] is True

    def test_record_count_correct(self):
        from ndjson.ndjson_codec import ndjson_installed_workflow
        result = ndjson_installed_workflow(_NDJSON_BYTES)
        assert result["record_count"] == 3

    def test_field_count_correct(self):
        from ndjson.ndjson_codec import ndjson_installed_workflow
        result = ndjson_installed_workflow(_NDJSON_BYTES)
        assert result["field_count"] == 3

    def test_has_all_required_keys(self):
        from ndjson.ndjson_codec import ndjson_installed_workflow
        result = ndjson_installed_workflow(_NDJSON_BYTES)
        assert {"format", "loaded", "record_count", "field_count"}.issubset(result.keys())

    def test_consistent_across_calls(self):
        from ndjson.ndjson_codec import ndjson_installed_workflow
        r1 = ndjson_installed_workflow(_NDJSON_BYTES)
        r2 = ndjson_installed_workflow(_NDJSON_BYTES)
        assert r1["record_count"] == r2["record_count"]
        assert r1["field_count"] == r2["field_count"]

    def test_record_count_and_field_count_are_integers(self):
        from ndjson.ndjson_codec import ndjson_installed_workflow
        result = ndjson_installed_workflow(_NDJSON_BYTES)
        assert isinstance(result["record_count"], int)
        assert isinstance(result["field_count"], int)
