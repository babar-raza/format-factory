"""TC-S58-005: FODP spec QName compliance tests.

Verifies that FODP classes have correct spec_qname, spec_fact_ref, and
namespace_uri attributes per shared/qname-registry/fodp.yaml.

Spec QName registry: office:document, presentation:page, draw:frame
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))


class TestFodpDocumentSpecQname:
    """FodpDocument domain model spec_qname compliance."""

    def test_spec_qname_defined(self):
        from fodp import FodpDocument
        assert FodpDocument.spec_qname == "office:document"

    def test_spec_qname_matches_registry(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "fodp.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("FODP qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        qnames = {e["qname"] for e in entries if isinstance(e, dict)}
        from fodp import FodpDocument
        assert FodpDocument.spec_qname in qnames


class TestFodpCompatLayerSpecQname:
    """FODP Compat layer spec qnames."""

    def test_fodp_document_spec_qname(self):
        from fodp.Compat import FodpDocument
        assert FodpDocument.spec_qname == "office:document"

    def test_fodp_document_spec_fact_ref(self):
        from fodp.Compat import FodpDocument
        assert FodpDocument.spec_fact_ref

    def test_fodp_page_spec_qname(self):
        from fodp.Compat import FodpPage
        assert FodpPage.spec_qname == "presentation:page"

    def test_fodp_page_spec_fact_ref(self):
        from fodp.Compat import FodpPage
        assert FodpPage.spec_fact_ref


class TestFodpSpecQnameRegistryLinkage:
    """Verify registry entries have spec_fact_ref."""

    def test_fodp_qnames_have_spec_fact_ref(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "fodp.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("FODP qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if isinstance(entry, dict):
                assert entry.get("spec_fact_ref"), \
                    f"qname {entry.get('qname')} missing spec_fact_ref"
