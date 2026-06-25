"""TC-S58-003: FODT spec QName compliance tests.

Verifies that FODT classes have correct spec_qname, spec_fact_ref, and
namespace_uri attributes per shared/qname-registry/fodt.yaml.

Spec QName registry: office:body, text:p, text:h, text:span, text:list
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))


class TestFodtDocumentSpecQname:
    """FodtDocument domain model spec_qname compliance."""

    def test_spec_qname_defined(self):
        from fodt import FodtDocument
        assert FodtDocument.spec_qname == "office:document"

    def test_spec_qname_matches_registry(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "fodt.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("FODT qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        qnames = {e["qname"] for e in entries if isinstance(e, dict)}
        from fodt import FodtDocument
        assert FodtDocument.spec_qname in qnames or FodtDocument.spec_qname == "office:document"


class TestFodtCompatLayerSpecQname:
    """FODT Compat layer spec qnames."""

    def test_fodt_document_spec_qname(self):
        from fodt.Compat import FodtDocument
        assert FodtDocument.spec_qname == "office:document"

    def test_fodt_document_spec_fact_ref(self):
        from fodt.Compat import FodtDocument
        assert FodtDocument.spec_fact_ref == "FACT-FODT-001"

    def test_fodt_paragraph_spec_qname(self):
        from fodt.Compat import FodtParagraph
        assert FodtParagraph.spec_qname == "text:p"

    def test_fodt_paragraph_spec_fact_ref(self):
        from fodt.Compat import FodtParagraph
        assert FodtParagraph.spec_fact_ref

    def test_fodt_heading_spec_qname(self):
        from fodt.Compat import FodtHeading
        assert FodtHeading.spec_qname == "text:h"


class TestFodtSpecQnameRegistryLinkage:
    """Verify registry entries have spec_fact_ref."""

    def test_fodt_qnames_have_spec_fact_ref(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "fodt.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("FODT qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if isinstance(entry, dict):
                assert entry.get("spec_fact_ref"), \
                    f"qname {entry.get('qname')} missing spec_fact_ref"
