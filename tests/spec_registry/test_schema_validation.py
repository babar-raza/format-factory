"""Tests for shared/qname-registry/schema.yaml validity (TC-SRC-REVIEW-002)."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).parent.parent.parent
_SCHEMA = _REPO / "shared" / "qname-registry" / "schema.yaml"


class TestSchemaFile:
    def test_schema_yaml_exists(self):
        """shared/qname-registry/schema.yaml must exist."""
        assert _SCHEMA.exists(), f"schema.yaml not found at {_SCHEMA}"

    def test_schema_yaml_is_valid_yaml(self):
        """schema.yaml must be valid YAML (parseable without error)."""
        content = _SCHEMA.read_text(encoding="utf-8")
        try:
            import yaml
            data = yaml.safe_load(content)
        except ImportError:
            # Without yaml, at least verify it's non-empty text
            assert content.strip(), "schema.yaml is empty"
            return
        assert data is not None, "schema.yaml parsed to None"

    def test_schema_yaml_has_required_fields(self):
        """schema.yaml must define all required registry entry fields."""
        content = _SCHEMA.read_text(encoding="utf-8")
        required_fields = [
            "qname",
            "namespace_uri",
            "local_name",
            "canonical_class",
            "spec_fact_ref",
            "status",
            "source_layer",
        ]
        for field in required_fields:
            assert field in content, f"schema.yaml missing required field definition: '{field}'"

    def test_schema_yaml_has_status_enum(self):
        """schema.yaml must define the status enum values."""
        content = _SCHEMA.read_text(encoding="utf-8")
        status_values = ["seeded", "architecture_only", "implementing", "implemented", "stable", "deprecated"]
        for val in status_values:
            assert val in content, f"schema.yaml missing status enum value: '{val}'"

    def test_shared_directory_exists(self):
        """shared/ directory must exist at repo root (git-tracked)."""
        assert (_REPO / "shared").exists(), "shared/ directory missing at repo root"

    def test_qname_registry_directory_exists(self):
        """shared/qname-registry/ directory must exist."""
        assert (_REPO / "shared" / "qname-registry").exists(), "shared/qname-registry/ missing"
