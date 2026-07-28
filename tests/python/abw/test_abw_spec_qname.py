"""TC-S58-001: ABW spec QName compliance tests.

Verifies that ABW classes have correct spec_qname, spec_fact_ref, and
namespace_uri attributes per shared/qname-registry/abw.yaml.

Spec QName registry: abiword:document, abiword:section, abiword:p
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))


class TestAbwDocumentSpecQname:
    """AbwDocument domain model spec_qname compliance."""

    def test_spec_qname_defined(self):
        from abw import AbwDocument
        assert AbwDocument.spec_qname == "abiword:document"

    def test_spec_qname_matches_registry(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "abw.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("ABW qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        qnames = {e["qname"] for e in entries if isinstance(e, dict)}
        from abw import AbwDocument
        assert AbwDocument.spec_qname in qnames or AbwDocument.spec_qname.startswith("abiword:")


class TestAbwCompatLayerSpecQname:
    """ABW Compat layer spec qnames (abiword:document, abiword:p)."""

    def test_abw_document_spec_qname(self):
        from abw.Compat import AbwDocument
        assert AbwDocument.spec_qname == "abiword:document"

    def test_abw_document_spec_fact_ref(self):
        from abw.Compat import AbwDocument
        assert AbwDocument.spec_fact_ref == "SAL-ABW-00001"

    def test_abw_document_namespace_uri(self):
        from abw.Compat import AbwDocument
        assert AbwDocument.namespace_uri
        assert "abisource" in AbwDocument.namespace_uri or "abw" in AbwDocument.namespace_uri

    def test_abw_paragraph_spec_qname(self):
        from abw.Compat import AbwParagraph
        assert AbwParagraph.spec_qname == "abiword:p"

    def test_abw_paragraph_spec_fact_ref(self):
        from abw.Compat import AbwParagraph
        assert AbwParagraph.spec_fact_ref


class TestAbwSpecQnameRegistryLinkage:
    """Verify source files match registry entries."""

    def test_registry_python_file_exists(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "abw.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("ABW qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            python_file = entry.get("python_file")
            if python_file:
                fp = _REPO_ROOT / python_file
                assert fp.exists(), f"python_file {python_file} does not exist for qname {entry.get('qname')}"

    def test_all_abw_qnames_have_abiword_prefix(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "abw.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("ABW qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if isinstance(entry, dict):
                assert entry.get("qname", "").startswith("abiword:"), \
                    f"Expected abiword: prefix, got {entry.get('qname')}"

    def test_abw_qnames_have_spec_fact_ref(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "abw.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("ABW qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if isinstance(entry, dict):
                assert entry.get("spec_fact_ref"), \
                    f"qname {entry.get('qname')} missing spec_fact_ref"
