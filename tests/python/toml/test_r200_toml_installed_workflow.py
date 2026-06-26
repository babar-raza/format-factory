"""
Installed workflow proof for aspose-format-factory-toml wheel.

Closes: GAP-TOML-FOSS-INSTALLED_WO-001
Capability: Installed Workflow
Authority: FACT-TOML-001, FACT-TOML-002, FACT-TOML-003

Tests that the installed TOML package (aspose-format-factory-toml wheel)
supports all core operations: load, parse, write, roundtrip, and domain model.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
_SAMPLE = _REPO / "samples" / "by-format" / "toml" / "minimal.toml"

# Ensure the installed package (not editable source) is importable
try:
    import toml as _toml_pkg  # noqa: F401
    _PACKAGE_AVAILABLE = True
except ImportError:
    _PACKAGE_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _PACKAGE_AVAILABLE,
    reason="aspose-format-factory-toml wheel not installed",
)


class TestTomlInstalledWorkflow:
    """Installed workflow proof: core TOML operations via installed wheel."""

    def test_load_returns_model_with_key_count(self):
        """load_toml returns a model dict with correct key_count."""
        from toml.toml_codec import load_toml
        model = load_toml(str(_SAMPLE))
        assert isinstance(model, dict), "load_toml must return dict"
        assert model["key_count"] == 5, f"Expected 5 top-level keys, got {model['key_count']}"

    def test_load_returns_data_dict(self):
        """load_toml model['data'] contains the parsed TOML data."""
        from toml.toml_codec import load_toml
        model = load_toml(str(_SAMPLE))
        data = model.get("data", {})
        assert "title" in data, "Expected 'title' key in TOML data"
        assert "server" in data, "Expected 'server' table in TOML data"
        assert isinstance(data["server"], dict), "server must be a dict (TOML table)"

    def test_domain_model_spec_qname(self):
        """TomlDocument.from_file() returns spec_qname='toml:table'."""
        from toml.models import TomlDocument
        doc = TomlDocument.from_file(str(_SAMPLE))
        assert doc.spec_qname == "toml:table", (
            f"Expected spec_qname='toml:table', got '{doc.spec_qname}'"
        )

    def test_domain_model_key_count(self):
        """TomlDocument.key_count matches Python stdlib tomllib."""
        import tomllib
        from toml.models import TomlDocument
        doc = TomlDocument.from_file(str(_SAMPLE))
        with open(_SAMPLE, "rb") as f:
            ref = tomllib.load(f)
        assert doc.key_count == len(ref), (
            f"key_count mismatch: product={doc.key_count}, stdlib={len(ref)}"
        )

    def test_write_roundtrip_preserves_key_count(self):
        """write_toml + load_toml roundtrip preserves key_count."""
        from toml.toml_codec import load_toml, write_toml
        model = load_toml(str(_SAMPLE))
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            write_toml(model["data"], tmp_path)
            reloaded = load_toml(tmp_path)
            assert reloaded["key_count"] == model["key_count"], (
                f"Roundtrip key_count mismatch: {reloaded['key_count']} != {model['key_count']}"
            )
        finally:
            os.unlink(tmp_path)

    def test_write_roundtrip_preserves_values(self):
        """write_toml + load_toml roundtrip preserves string values."""
        from toml.toml_codec import load_toml, write_toml
        model = load_toml(str(_SAMPLE))
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            write_toml(model["data"], tmp_path)
            reloaded = load_toml(tmp_path)
            orig_title = model["data"].get("title")
            rt_title = reloaded["data"].get("title")
            assert orig_title == rt_title, (
                f"title value mismatch after roundtrip: {rt_title!r} != {orig_title!r}"
            )
        finally:
            os.unlink(tmp_path)

    def test_domain_model_to_dict(self):
        """TomlDocument.to_dict() includes format, path, data, and key_count."""
        from toml.models import TomlDocument
        doc = TomlDocument.from_file(str(_SAMPLE))
        d = doc.to_dict()
        assert d.get("format") == "toml"
        assert "data" in d
        assert d.get("key_count") == 5
