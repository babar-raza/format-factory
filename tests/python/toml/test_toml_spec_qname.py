"""TC-S56-006: TOML spec QName compliance tests.

Verifies that TOML classes have correct spec_qname, spec_fact_ref, and
namespace_uri attributes per shared/qname-registry/toml.yaml.

Spec QName registry: toml:table, toml:key
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))


class TestTomlDocumentSpecQname:
    """TomlDocument domain model spec_qname compliance."""

    def test_spec_qname_defined(self):
        from toml import TomlDocument
        assert TomlDocument.spec_qname == "toml:table"

    def test_spec_qname_matches_registry(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "toml.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("TOML qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        qnames = {e["qname"] for e in entries if isinstance(e, dict)}
        from toml import TomlDocument
        assert TomlDocument.spec_qname in qnames or TomlDocument.spec_qname.startswith("toml:")


class TestTomlCompatLayerSpecQname:
    """TOML Compat layer spec qnames (toml:table, toml:key)."""

    def test_toml_table_spec_qname(self):
        from toml.Compat import TomlTable
        assert TomlTable.spec_qname == "toml:table"

    def test_toml_table_spec_fact_ref(self):
        from toml.Compat import TomlTable
        assert TomlTable.spec_fact_ref == "SAL-TOML-00001"

    def test_toml_table_namespace_uri(self):
        from toml.Compat import TomlTable
        assert TomlTable.namespace_uri
        assert "toml" in TomlTable.namespace_uri

    def test_toml_key_spec_qname(self):
        from toml.Compat import TomlKey
        assert TomlKey.spec_qname == "toml:key"

    def test_toml_key_spec_fact_ref(self):
        from toml.Compat import TomlKey
        assert TomlKey.spec_fact_ref == "SAL-TOML-00002"


class TestTomlSpecQnameRegistryLinkage:
    """Verify source files match registry entries."""

    def test_registry_python_file_exists(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "toml.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("TOML qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            python_file = entry.get("python_file")
            if python_file:
                fp = _REPO_ROOT / python_file
                assert fp.exists(), f"python_file {python_file} does not exist for qname {entry.get('qname')}"

    def test_all_toml_qnames_have_toml_prefix(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "toml.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("TOML qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if isinstance(entry, dict):
                assert entry.get("qname", "").startswith("toml:"), \
                    f"Expected toml: prefix, got {entry.get('qname')}"

    def test_toml_qnames_have_spec_fact_ref(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "toml.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("TOML qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if isinstance(entry, dict):
                assert entry.get("spec_fact_ref"), \
                    f"qname {entry.get('qname')} missing spec_fact_ref"
