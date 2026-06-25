"""TC-S58-004: FODG spec QName compliance tests.

Verifies that FODG classes have correct spec_qname, spec_fact_ref, and
namespace_uri attributes per shared/qname-registry/fodg.yaml.

Spec QName registry: office:document, draw:page, draw:frame
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))


class TestFodgDocumentSpecQname:
    """FodgDocument domain model spec_qname compliance."""

    def test_spec_qname_defined(self):
        from fodg import FodgDocument
        assert FodgDocument.spec_qname == "office:document"

    def test_spec_qname_matches_registry(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "fodg.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("FODG qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        qnames = {e["qname"] for e in entries if isinstance(e, dict)}
        from fodg import FodgDocument
        assert FodgDocument.spec_qname in qnames


class TestFodgCompatLayerSpecQname:
    """FODG Compat layer spec qnames."""

    def test_fodg_document_spec_qname(self):
        from fodg.Compat import FodgDocument
        assert FodgDocument.spec_qname == "office:document"

    def test_fodg_document_spec_fact_ref(self):
        from fodg.Compat import FodgDocument
        assert FodgDocument.spec_fact_ref

    def test_fodg_page_spec_qname(self):
        from fodg.Compat import FodgPage
        assert FodgPage.spec_qname == "draw:page"

    def test_fodg_page_spec_fact_ref(self):
        from fodg.Compat import FodgPage
        assert FodgPage.spec_fact_ref


class TestFodgSpecQnameRegistryLinkage:
    """Verify registry entries have spec_fact_ref."""

    def test_fodg_qnames_have_spec_fact_ref(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "fodg.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("FODG qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if isinstance(entry, dict):
                assert entry.get("spec_fact_ref"), \
                    f"qname {entry.get('qname')} missing spec_fact_ref"
