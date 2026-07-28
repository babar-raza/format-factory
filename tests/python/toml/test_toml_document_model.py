"""Tests for TomlDocument domain model (HO-RC002-MODELS, PQ-T2-005).

Verifies TomlDocument wraps load_toml() results with typed accessors
and correct spec_qname for V53 compliance.

Gap closure: HO-RC002-MODELS (missing domain models)
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from toml.models import TomlDocument


def _make_model(data: dict):
    """Simulate load_toml() result."""
    return {"data": data}


# ---------------------------------------------------------------------------
# spec_qname / class-level attributes
# ---------------------------------------------------------------------------

class TestTomlDocumentSpec:
    def test_spec_qname_is_class_attr(self):
        assert TomlDocument.spec_qname == "toml:table"

    def test_spec_qname_accessible_without_instance(self):
        assert TomlDocument.spec_qname == "toml:table"

    def test_spec_fact_ref(self):
        assert TomlDocument.spec_fact_ref == "SAL-TOML-00001"

    def test_namespace_uri(self):
        assert "toml" in TomlDocument.namespace_uri.lower()

    def test_local_name(self):
        assert TomlDocument.local_name == "table"


# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------

class TestTomlDocumentProperties:
    def test_key_count(self):
        doc = TomlDocument(_make_model({"a": 1, "b": 2}))
        assert doc.key_count == 2

    def test_key_count_empty(self):
        doc = TomlDocument(_make_model({}))
        assert doc.key_count == 0

    def test_keys_list(self):
        doc = TomlDocument(_make_model({"x": 10, "y": 20}))
        assert set(doc.keys) == {"x", "y"}

    def test_get_existing_key(self):
        doc = TomlDocument(_make_model({"name": "format-factory"}))
        assert doc.get("name") == "format-factory"

    def test_get_missing_key_default(self):
        doc = TomlDocument(_make_model({}))
        assert doc.get("missing") is None

    def test_get_custom_default(self):
        doc = TomlDocument(_make_model({}))
        assert doc.get("key", "default") == "default"

    def test_has_key_true(self):
        doc = TomlDocument(_make_model({"present": True}))
        assert doc.has_key("present") is True

    def test_has_key_false(self):
        doc = TomlDocument(_make_model({}))
        assert doc.has_key("absent") is False

    def test_data_returns_inner_dict(self):
        doc = TomlDocument(_make_model({"k": "v"}))
        assert doc.data() == {"k": "v"}

    def test_data_returns_copy(self):
        doc = TomlDocument(_make_model({"k": "v"}))
        d = doc.data()
        d["injected"] = True
        assert "injected" not in doc.data()

    def test_to_dict_returns_wrapper(self):
        model = _make_model({"a": 1})
        doc = TomlDocument(model)
        assert "data" in doc.to_dict()

    def test_repr(self):
        doc = TomlDocument(_make_model({"a": 1, "b": 2}))
        r = repr(doc)
        assert "TomlDocument" in r
        assert "2" in r


# ---------------------------------------------------------------------------
# from_file
# ---------------------------------------------------------------------------

class TestTomlDocumentFromFile:
    def test_from_file_loads_keys(self):
        content = b'[meta]\nformat = "toml"\nversion = 1\n'
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as f:
            f.write(content)
            path = Path(f.name)
        try:
            doc = TomlDocument.from_file(path)
            assert doc.has_key("meta")
        finally:
            path.unlink(missing_ok=True)

    def test_from_file_flat_keys(self):
        content = b'name = "factory"\nversion = "1.0"\n'
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as f:
            f.write(content)
            path = Path(f.name)
        try:
            doc = TomlDocument.from_file(path)
            assert doc.key_count == 2
            assert doc.get("name") == "factory"
        finally:
            path.unlink(missing_ok=True)
