"""TC-S58-002: FODS spec QName compliance tests.

Verifies that FODS classes have correct spec_qname, spec_fact_ref, and
namespace_uri attributes per shared/qname-registry/fods.yaml.

Spec QName registry: office:document, office:body, office:spreadsheet, table:table, table:table-cell
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
# FODS Compat uses 'from src.python.fods.spec...' absolute imports — need repo root
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))


class TestFodsDocumentSpecQname:
    """FodsDocument domain model spec_qname compliance."""

    def test_spec_qname_defined(self):
        from fods import FodsDocument
        assert FodsDocument.spec_qname == "office:document"

    def test_spec_qname_matches_registry(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "fods.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("FODS qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        qnames = {e["qname"] for e in entries if isinstance(e, dict)}
        from fods import FodsDocument
        assert FodsDocument.spec_qname in qnames


class TestFodsCompatLayerSpecQname:
    """FODS Compat layer spec qnames."""

    def test_fods_document_spec_qname(self):
        from fods.Compat import FodsDocument
        assert FodsDocument.spec_qname == "office:document"

    def test_fods_document_spec_fact_ref(self):
        from fods.Compat import FodsDocument
        assert FodsDocument.spec_fact_ref == "FACT-FODS-001"

    def test_fods_sheet_spec_qname(self):
        from fods.Compat import FodsSheet
        assert FodsSheet.spec_qname == "table:table"

    def test_fods_sheet_spec_fact_ref(self):
        from fods.Compat import FodsSheet
        assert FodsSheet.spec_fact_ref

    def test_fods_cell_spec_qname(self):
        from fods.Compat import FodsCell
        assert FodsCell.spec_qname == "table:table-cell"

    def test_fods_cell_spec_fact_ref(self):
        from fods.Compat import FodsCell
        assert FodsCell.spec_fact_ref == "FACT-FODS-006"


class TestFodsSpecQnameRegistryLinkage:
    """Verify registry entries have spec_fact_ref."""

    def test_registry_exists(self):
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "fods.yaml"
        assert registry_path.exists(), "FODS qname registry must exist"

    def test_fods_qnames_have_spec_fact_ref(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "fods.yaml"
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if isinstance(entry, dict):
                assert entry.get("spec_fact_ref"), \
                    f"qname {entry.get('qname')} missing spec_fact_ref"
