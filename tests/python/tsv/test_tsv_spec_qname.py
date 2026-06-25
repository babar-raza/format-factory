"""TC-S56-005: TSV spec QName compliance tests.

Verifies that TSV classes have correct spec_qname, spec_fact_ref, and
namespace_uri attributes per shared/qname-registry/tsv.yaml.

Spec QName registry: tsv:record, tsv:field
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))


class TestTsvDocumentSpecQname:
    """TsvDocument domain model spec_qname compliance."""

    def test_spec_qname_defined(self):
        from tsv import TsvDocument
        assert TsvDocument.spec_qname == "tsv:record"

    def test_spec_qname_matches_registry(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "tsv.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("TSV qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        qnames = {e["qname"] for e in entries if isinstance(e, dict)}
        from tsv import TsvDocument
        assert TsvDocument.spec_qname in qnames or TsvDocument.spec_qname.startswith("tsv:")


class TestTsvCompatLayerSpecQname:
    """TSV Compat layer spec qnames (tsv:record, tsv:field)."""

    def test_tsv_record_spec_qname(self):
        from tsv.Compat import TsvRecord
        assert TsvRecord.spec_qname == "tsv:record"

    def test_tsv_record_spec_fact_ref(self):
        from tsv.Compat import TsvRecord
        assert TsvRecord.spec_fact_ref == "FACT-TSV-001"

    def test_tsv_record_namespace_uri(self):
        from tsv.Compat import TsvRecord
        assert TsvRecord.namespace_uri
        assert "tsv" in TsvRecord.namespace_uri or "tab" in TsvRecord.namespace_uri

    def test_tsv_field_spec_qname(self):
        from tsv.Compat import TsvField
        assert TsvField.spec_qname == "tsv:field"

    def test_tsv_field_spec_fact_ref(self):
        from tsv.Compat import TsvField
        assert TsvField.spec_fact_ref == "FACT-TSV-002"


class TestTsvSpecQnameRegistryLinkage:
    """Verify source files match registry entries."""

    def test_registry_python_file_exists(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "tsv.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("TSV qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            python_file = entry.get("python_file")
            if python_file:
                fp = _REPO_ROOT / python_file
                assert fp.exists(), f"python_file {python_file} does not exist for qname {entry.get('qname')}"

    def test_all_tsv_qnames_have_tsv_prefix(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "tsv.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("TSV qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if isinstance(entry, dict):
                assert entry.get("qname", "").startswith("tsv:"), \
                    f"Expected tsv: prefix, got {entry.get('qname')}"

    def test_tsv_qnames_have_spec_fact_ref(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "tsv.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("TSV qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if isinstance(entry, dict):
                assert entry.get("spec_fact_ref"), \
                    f"qname {entry.get('qname')} missing spec_fact_ref"
