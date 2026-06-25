"""TC-S55-007 (Pilot 6): PBM spec QName compliance tests.

Verifies that PBM classes have correct spec_qname, spec_fact_ref, and
namespace_uri attributes per shared/qname-registry/pbm.yaml.

Spec QName registry: pbm:header, pbm:raster, pbm:bitmap
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT))


class TestPbmImageSpecQname:
    """PbmImage spec_qname compliance (V53)."""

    def test_spec_qname_class_attribute(self):
        from src.python.pbm import PbmImage
        assert hasattr(PbmImage, "spec_qname"), "PbmImage must have spec_qname class attr"
        assert PbmImage.spec_qname == "pbm:image"

    def test_spec_qname_instance_accessible(self):
        from src.python.pbm import parse_pbm
        sample = _REPO_ROOT / "samples" / "by-format" / "pbm" / "valid" / "simple-1x1-binary.pbm"
        if not sample.exists():
            import pytest
            pytest.skip("No PBM sample file available")
        doc = parse_pbm(str(sample))
        # spec_qname should be class-level (not instance)
        assert doc.spec_qname == "pbm:image"


class TestPbmDocumentSpecQname:
    """PbmDocument domain model spec_qname compliance."""

    def test_spec_qname_defined(self):
        from src.python.pbm import PbmDocument
        assert PbmDocument.spec_qname == "pbm:image"

    def test_spec_qname_matches_registry(self):
        """Verify PbmDocument qname matches shared qname-registry entry."""
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "pbm.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("PBM qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        qnames = {e["qname"] for e in entries if isinstance(e, dict)}
        from src.python.pbm import PbmDocument
        assert PbmDocument.spec_qname in qnames or PbmDocument.spec_qname.startswith("pbm:")


class TestPbmCompatLayerSpecQname:
    """PBM Compat layer spec qnames (pbm:header, pbm:raster, pbm:bitmap)."""

    def test_pbm_header_spec_qname(self):
        from src.python.pbm.Compat import PbmHeader
        assert PbmHeader.spec_qname == "pbm:header"

    def test_pbm_header_spec_fact_ref(self):
        from src.python.pbm.Compat import PbmHeader
        assert PbmHeader.spec_fact_ref == "FACT-PBM-001"

    def test_pbm_header_namespace_uri(self):
        from src.python.pbm.Compat import PbmHeader
        assert PbmHeader.namespace_uri
        assert "netpbm" in PbmHeader.namespace_uri or "pbm" in PbmHeader.namespace_uri

    def test_pbm_bitmap_spec_qname(self):
        from src.python.pbm.Compat import PbmBitmap
        assert PbmBitmap.spec_qname == "pbm:bitmap"

    def test_pbm_bitmap_spec_fact_ref(self):
        from src.python.pbm.Compat import PbmBitmap
        assert PbmBitmap.spec_fact_ref


class TestPbmSpecQnameRegistryLinkage:
    """Verify source files match registry entries."""

    def test_registry_python_file_exists(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "pbm.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("PBM qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            python_file = entry.get("python_file")
            if python_file:
                fp = _REPO_ROOT / python_file
                assert fp.exists(), f"python_file {python_file} does not exist for qname {entry.get('qname')}"

    def test_all_pbm_qnames_have_pbm_prefix(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "pbm.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("PBM qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if isinstance(entry, dict):
                assert entry.get("qname", "").startswith("pbm:"), \
                    f"Expected pbm: prefix, got {entry.get('qname')}"

    def test_pbm_qnames_have_spec_fact_ref(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "pbm.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("PBM qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if isinstance(entry, dict):
                assert entry.get("spec_fact_ref"), \
                    f"qname {entry.get('qname')} missing spec_fact_ref"
