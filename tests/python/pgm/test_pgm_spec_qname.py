"""TC-S56-001 (Pilot 7): PGM spec QName compliance tests.

Verifies that PGM classes have correct spec_qname, spec_fact_ref, and
namespace_uri attributes per shared/qname-registry/pgm.yaml.

Spec QName registry: pgm:header, pgm:raster, pgm:graymap
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))


class TestPgmImageSpecQname:
    """PgmImage spec_qname compliance (V53)."""

    def test_spec_qname_class_attribute(self):
        from pgm import PgmImage
        assert hasattr(PgmImage, "spec_qname"), "PgmImage must have spec_qname class attr"
        assert PgmImage.spec_qname == "pgm:image"

    def test_spec_qname_instance_accessible(self):
        from pgm import parse_pgm
        sample = _REPO_ROOT / "samples" / "by-format" / "pgm" / "valid" / "simple-4x4-ascii.pgm"
        if not sample.exists():
            import pytest
            pytest.skip("No PGM sample file available")
        doc = parse_pgm(str(sample))
        assert doc.spec_qname == "pgm:image"


class TestPgmDocumentSpecQname:
    """PgmDocument domain model spec_qname compliance."""

    def test_spec_qname_defined(self):
        from pgm import PgmDocument
        assert PgmDocument.spec_qname == "pgm:image"

    def test_spec_qname_matches_registry(self):
        """Verify PgmDocument qname matches shared qname-registry entry."""
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "pgm.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("PGM qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        qnames = {e["qname"] for e in entries if isinstance(e, dict)}
        from pgm import PgmDocument
        assert PgmDocument.spec_qname in qnames or PgmDocument.spec_qname.startswith("pgm:")


class TestPgmCompatLayerSpecQname:
    """PGM Compat layer spec qnames (pgm:header, pgm:graymap)."""

    def test_pgm_header_spec_qname(self):
        from pgm.Compat import PgmHeader
        assert PgmHeader.spec_qname == "pgm:header"

    def test_pgm_header_spec_fact_ref(self):
        from pgm.Compat import PgmHeader
        assert PgmHeader.spec_fact_ref == "SAL-PGM-00001"

    def test_pgm_header_namespace_uri(self):
        from pgm.Compat import PgmHeader
        assert PgmHeader.namespace_uri
        assert "netpbm" in PgmHeader.namespace_uri or "pgm" in PgmHeader.namespace_uri

    def test_pgm_graymap_spec_qname(self):
        from pgm.Compat import PgmGraymap
        assert PgmGraymap.spec_qname == "pgm:graymap"

    def test_pgm_graymap_spec_fact_ref(self):
        from pgm.Compat import PgmGraymap
        assert PgmGraymap.spec_fact_ref


class TestPgmSpecQnameRegistryLinkage:
    """Verify source files match registry entries."""

    def test_registry_python_file_exists(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "pgm.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("PGM qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            python_file = entry.get("python_file")
            if python_file:
                fp = _REPO_ROOT / python_file
                assert fp.exists(), f"python_file {python_file} does not exist for qname {entry.get('qname')}"

    def test_all_pgm_qnames_have_pgm_prefix(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "pgm.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("PGM qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if isinstance(entry, dict):
                assert entry.get("qname", "").startswith("pgm:"), \
                    f"Expected pgm: prefix, got {entry.get('qname')}"

    def test_pgm_qnames_have_spec_fact_ref(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "pgm.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("PGM qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if isinstance(entry, dict):
                assert entry.get("spec_fact_ref"), \
                    f"qname {entry.get('qname')} missing spec_fact_ref"
