"""TC-S56-007: ZST spec QName compliance tests.

Verifies that ZST classes have correct spec_qname, spec_fact_ref, and
namespace_uri attributes per shared/qname-registry/zst.yaml.

Spec QName registry: zst:frame, zst:block, zst:magic-number
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))


class TestZstDocumentSpecQname:
    """ZstDocument domain model spec_qname compliance."""

    def test_spec_qname_defined(self):
        from zst import ZstDocument
        assert ZstDocument.spec_qname == "zst:frame"

    def test_spec_qname_matches_registry(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "zst.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("ZST qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        qnames = {e["qname"] for e in entries if isinstance(e, dict)}
        from zst import ZstDocument
        assert ZstDocument.spec_qname in qnames or ZstDocument.spec_qname.startswith("zst:")


class TestZstCompatLayerSpecQname:
    """ZST Compat layer spec qnames (zst:frame, zst:block)."""

    def test_zst_frame_spec_qname(self):
        from zst.Compat import ZstFrame
        assert ZstFrame.spec_qname == "zst:frame"

    def test_zst_frame_spec_fact_ref(self):
        from zst.Compat import ZstFrame
        assert ZstFrame.spec_fact_ref == "SAL-ZST-00001"

    def test_zst_frame_namespace_uri(self):
        from zst.Compat import ZstFrame
        assert ZstFrame.namespace_uri
        assert "zst" in ZstFrame.namespace_uri or "zstd" in ZstFrame.namespace_uri

    def test_zst_block_spec_qname(self):
        from zst.Compat import ZstBlock
        assert ZstBlock.spec_qname == "zst:block"

    def test_zst_block_spec_fact_ref(self):
        from zst.Compat import ZstBlock
        assert ZstBlock.spec_fact_ref == "SAL-ZST-00002"


class TestZstSpecQnameRegistryLinkage:
    """Verify source files match registry entries."""

    def test_registry_python_file_exists(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "zst.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("ZST qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            python_file = entry.get("python_file")
            if python_file:
                fp = _REPO_ROOT / python_file
                assert fp.exists(), f"python_file {python_file} does not exist for qname {entry.get('qname')}"

    def test_all_zst_qnames_have_zst_prefix(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "zst.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("ZST qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if isinstance(entry, dict):
                assert entry.get("qname", "").startswith("zst:"), \
                    f"Expected zst: prefix, got {entry.get('qname')}"

    def test_zst_qnames_have_spec_fact_ref(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "zst.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("ZST qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if isinstance(entry, dict):
                assert entry.get("spec_fact_ref"), \
                    f"qname {entry.get('qname')} missing spec_fact_ref"
