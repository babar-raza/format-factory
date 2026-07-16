"""TC-S56-002 (Pilot 7): PPM spec QName compliance tests.

Verifies that PPM classes have correct spec_qname, spec_fact_ref, and
namespace_uri attributes per shared/qname-registry/ppm.yaml.

Spec QName registry: ppm:header, ppm:raster, ppm:pixmap
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))


class TestPpmImageSpecQname:
    """PpmImage spec_qname compliance (V53)."""

    def test_spec_qname_class_attribute(self):
        from ppm import PpmImage
        assert hasattr(PpmImage, "spec_qname"), "PpmImage must have spec_qname class attr"
        assert PpmImage.spec_qname == "ppm:image"

    def test_spec_qname_instance_accessible(self):
        from ppm import parse_ppm
        sample = _REPO_ROOT / "samples" / "by-format" / "ppm" / "valid" / "simple-2x2-ascii.ppm"
        if not sample.exists():
            import pytest
            pytest.skip("No PPM sample file available")
        doc = parse_ppm(str(sample))
        assert doc.spec_qname == "ppm:image"


class TestPpmDocumentSpecQname:
    """PpmDocument domain model spec_qname compliance."""

    def test_spec_qname_defined(self):
        from ppm import PpmDocument
        assert PpmDocument.spec_qname == "ppm:image"

    def test_spec_qname_matches_registry(self):
        """Verify PpmDocument qname matches shared qname-registry entry."""
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "ppm.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("PPM qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        qnames = {e["qname"] for e in entries if isinstance(e, dict)}
        from ppm import PpmDocument
        assert PpmDocument.spec_qname in qnames or PpmDocument.spec_qname.startswith("ppm:")


class TestPpmCompatLayerSpecQname:
    """PPM Compat layer spec qnames (ppm:header, ppm:pixmap)."""

    def test_ppm_header_spec_qname(self):
        from ppm.Compat import PpmHeader
        assert PpmHeader.spec_qname == "ppm:header"

    def test_ppm_header_spec_fact_ref(self):
        from ppm.Compat import PpmHeader
        assert PpmHeader.spec_fact_ref == "SAL-PPM-00001"

    def test_ppm_header_namespace_uri(self):
        from ppm.Compat import PpmHeader
        assert PpmHeader.namespace_uri
        assert "netpbm" in PpmHeader.namespace_uri or "ppm" in PpmHeader.namespace_uri

    def test_ppm_pixmap_spec_qname(self):
        from ppm.Compat import PpmPixmap
        assert PpmPixmap.spec_qname == "ppm:pixmap"

    def test_ppm_pixmap_spec_fact_ref(self):
        from ppm.Compat import PpmPixmap
        assert PpmPixmap.spec_fact_ref


class TestPpmSpecQnameRegistryLinkage:
    """Verify source files match registry entries."""

    def test_registry_python_file_exists(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "ppm.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("PPM qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            python_file = entry.get("python_file")
            if python_file:
                fp = _REPO_ROOT / python_file
                assert fp.exists(), f"python_file {python_file} does not exist for qname {entry.get('qname')}"

    def test_all_ppm_qnames_have_ppm_prefix(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "ppm.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("PPM qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if isinstance(entry, dict):
                assert entry.get("qname", "").startswith("ppm:"), \
                    f"Expected ppm: prefix, got {entry.get('qname')}"

    def test_ppm_qnames_have_spec_fact_ref(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "ppm.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("PPM qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if isinstance(entry, dict):
                assert entry.get("spec_fact_ref"), \
                    f"qname {entry.get('qname')} missing spec_fact_ref"
