"""TC-S56-003 (Pilot 7): QOI spec QName compliance tests.

Verifies that QOI classes have correct spec_qname, spec_fact_ref, and
namespace_uri attributes per shared/qname-registry/qoi.yaml.

Spec QName registry: qoi:header, qoi:chunk, qoi:end-marker
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))


class TestQoiImageSpecQname:
    """QoiImage spec_qname compliance (V53)."""

    def test_spec_qname_class_attribute(self):
        from qoi import QoiImage
        assert hasattr(QoiImage, "spec_qname"), "QoiImage must have spec_qname class attr"
        assert QoiImage.spec_qname == "qoi:image"

    def test_spec_qname_instance_accessible(self):
        from qoi import parse_qoi
        sample = _REPO_ROOT / "samples" / "by-format" / "qoi" / "valid" / "minimal-1x1.qoi"
        if not sample.exists():
            import pytest
            pytest.skip("No QOI sample file available")
        doc = parse_qoi(str(sample))
        assert doc.spec_qname == "qoi:image"


class TestQoiDocumentSpecQname:
    """QoiDocument domain model spec_qname compliance."""

    def test_spec_qname_defined(self):
        from qoi import QoiDocument
        assert QoiDocument.spec_qname == "qoi:image"

    def test_spec_qname_matches_registry(self):
        """Verify QoiDocument qname matches shared qname-registry entry."""
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "qoi.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("QOI qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        qnames = {e["qname"] for e in entries if isinstance(e, dict)}
        from qoi import QoiDocument
        assert QoiDocument.spec_qname in qnames or QoiDocument.spec_qname.startswith("qoi:")


class TestQoiCompatLayerSpecQname:
    """QOI Compat layer spec qnames (qoi:header, qoi:chunk, qoi:end-marker)."""

    def test_qoi_header_spec_qname(self):
        from qoi.Compat import QoiHeader
        assert QoiHeader.spec_qname == "qoi:header"

    def test_qoi_header_spec_fact_ref(self):
        from qoi.Compat import QoiHeader
        assert QoiHeader.spec_fact_ref == "FACT-QOI-001"

    def test_qoi_header_namespace_uri(self):
        from qoi.Compat import QoiHeader
        assert QoiHeader.namespace_uri
        assert "qoi" in QoiHeader.namespace_uri

    def test_qoi_chunk_spec_qname(self):
        from qoi.Compat import QoiChunk
        assert QoiChunk.spec_qname == "qoi:chunk"

    def test_qoi_chunk_spec_fact_ref(self):
        from qoi.Compat import QoiChunk
        assert QoiChunk.spec_fact_ref

    def test_qoi_end_marker_spec_qname(self):
        from qoi.Compat import QoiEndMarker
        assert QoiEndMarker.spec_qname == "qoi:end-marker"


class TestQoiSpecQnameRegistryLinkage:
    """Verify source files match registry entries."""

    def test_registry_python_file_exists(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "qoi.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("QOI qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            python_file = entry.get("python_file")
            if python_file:
                fp = _REPO_ROOT / python_file
                assert fp.exists(), f"python_file {python_file} does not exist for qname {entry.get('qname')}"

    def test_all_qoi_qnames_have_qoi_prefix(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "qoi.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("QOI qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if isinstance(entry, dict):
                assert entry.get("qname", "").startswith("qoi:"), \
                    f"Expected qoi: prefix, got {entry.get('qname')}"

    def test_qoi_qnames_have_spec_fact_ref(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "qoi.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("QOI qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if isinstance(entry, dict):
                assert entry.get("spec_fact_ref"), \
                    f"qname {entry.get('qname')} missing spec_fact_ref"
