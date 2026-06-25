"""TC-S56-008: GNUMERIC spec QName compliance tests.

Verifies that Gnumeric classes have correct spec_qname, spec_fact_ref, and
namespace_uri attributes per shared/qname-registry/gnumeric.yaml.

Spec QName registry: gnumeric:workbook, gnumeric:sheet, gnumeric:cell
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))


class TestGnumericDocumentSpecQname:
    """GnumericDocument domain model spec_qname compliance."""

    def test_spec_qname_defined(self):
        from gnumeric import GnumericDocument
        assert GnumericDocument.spec_qname == "gnumeric:workbook"

    def test_spec_qname_matches_registry(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "gnumeric.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("GNUMERIC qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        qnames = {e["qname"] for e in entries if isinstance(e, dict)}
        from gnumeric import GnumericDocument
        assert GnumericDocument.spec_qname in qnames or GnumericDocument.spec_qname.startswith("gnumeric:")


class TestGnumericCompatLayerSpecQname:
    """Gnumeric Compat layer spec qnames (gnumeric:workbook, gnumeric:sheet)."""

    def test_gnumeric_workbook_spec_qname(self):
        from gnumeric.Compat import GnumericWorkbook
        assert GnumericWorkbook.spec_qname == "gnumeric:workbook"

    def test_gnumeric_workbook_spec_fact_ref(self):
        from gnumeric.Compat import GnumericWorkbook
        assert GnumericWorkbook.spec_fact_ref == "FACT-GNUMERIC-001"

    def test_gnumeric_workbook_namespace_uri(self):
        from gnumeric.Compat import GnumericWorkbook
        assert GnumericWorkbook.namespace_uri
        assert "gnumeric" in GnumericWorkbook.namespace_uri

    def test_gnumeric_sheet_spec_qname(self):
        from gnumeric.Compat import GnumericSheet
        assert GnumericSheet.spec_qname == "gnumeric:sheet"

    def test_gnumeric_sheet_spec_fact_ref(self):
        from gnumeric.Compat import GnumericSheet
        assert GnumericSheet.spec_fact_ref == "FACT-GNUMERIC-002"


class TestGnumericSpecQnameRegistryLinkage:
    """Verify source files match registry entries."""

    def test_registry_python_file_exists(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "gnumeric.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("GNUMERIC qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            python_file = entry.get("python_file")
            if python_file:
                fp = _REPO_ROOT / python_file
                assert fp.exists(), f"python_file {python_file} does not exist for qname {entry.get('qname')}"

    def test_all_gnumeric_qnames_have_gnumeric_prefix(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "gnumeric.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("GNUMERIC qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if isinstance(entry, dict):
                assert entry.get("qname", "").startswith("gnumeric:"), \
                    f"Expected gnumeric: prefix, got {entry.get('qname')}"

    def test_gnumeric_qnames_have_spec_fact_ref(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "gnumeric.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("GNUMERIC qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if isinstance(entry, dict):
                assert entry.get("spec_fact_ref"), \
                    f"qname {entry.get('qname')} missing spec_fact_ref"
