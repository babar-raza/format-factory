"""
test_r58_bundle_hygiene_no_pyc.py — R58 Train C: Bundle hygiene checks.

Verifies that __pycache__ and .pyc files cannot appear in evidence bundles.

R58 Sprint: FORMAT-FACTORY-R58-TRUE-SELF-VERIFYING-RC-REBUILD-PHASE9-EXPANSION-MEGA-TRAIN-001
IV-R57-012 (regression guard)
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


class TestNoPycacheInBundle:
    """check_pycache_in_bundle must detect any __pycache__ or .pyc entry."""

    def test_empty_bundle_passes(self, tmp_path):
        zp = tmp_path / "r58.zip"
        with zipfile.ZipFile(zp, "w") as zf:
            zf.writestr("repo/README.md", "test")
        from tools.evidence.validate_evidence_bundle import check_pycache_in_bundle
        with zipfile.ZipFile(zp) as zf:
            assert check_pycache_in_bundle(zf) == []

    def test_pycache_dir_fails(self, tmp_path):
        zp = tmp_path / "r58.zip"
        with zipfile.ZipFile(zp, "w") as zf:
            zf.writestr("repo/src/python/fods/__pycache__/parser.cpython-313.pyc", b"\x00")
        from tools.evidence.validate_evidence_bundle import check_pycache_in_bundle
        with zipfile.ZipFile(zp) as zf:
            errors = check_pycache_in_bundle(zf)
        assert errors and "BUNDLE_PYCACHE_PRESENT" in errors[0]

    def test_dot_pyc_file_fails(self, tmp_path):
        zp = tmp_path / "r58.zip"
        with zipfile.ZipFile(zp, "w") as zf:
            zf.writestr("repo/src/python/fods/parser.pyc", b"\x00")
        from tools.evidence.validate_evidence_bundle import check_pycache_in_bundle
        with zipfile.ZipFile(zp) as zf:
            errors = check_pycache_in_bundle(zf)
        assert errors and "BUNDLE_PYCACHE_PRESENT" in errors[0]

    def test_pycache_in_metadata_ignored(self, tmp_path):
        """__pycache__ in bundle-metadata/ is not checked (only repo/ is checked)."""
        zp = tmp_path / "r58.zip"
        with zipfile.ZipFile(zp, "w") as zf:
            zf.writestr("bundle-metadata/__pycache__/test.pyc", b"\x00")
            zf.writestr("repo/README.md", "clean")
        from tools.evidence.validate_evidence_bundle import check_pycache_in_bundle
        with zipfile.ZipFile(zp) as zf:
            errors = check_pycache_in_bundle(zf)
        assert errors == []

    def test_multiple_pycache_reported_as_one_error(self, tmp_path):
        zp = tmp_path / "r58.zip"
        with zipfile.ZipFile(zp, "w") as zf:
            for i in range(5):
                zf.writestr(f"repo/src/python/pkg{i}/__pycache__/mod.cpython-313.pyc", b"\x00")
        from tools.evidence.validate_evidence_bundle import check_pycache_in_bundle
        with zipfile.ZipFile(zp) as zf:
            errors = check_pycache_in_bundle(zf)
        assert len(errors) == 1
        assert "5" in errors[0]

    def test_real_bundle_has_no_pycache(self):
        """The actual R57 pass-2 bundle should have 0 pycache entries."""
        bundle = PROJECT_ROOT / ".local" / "r57-pass2-final.zip"
        if not bundle.exists():
            pytest.skip("R57 pass-2 bundle not available")
        from tools.evidence.validate_evidence_bundle import check_pycache_in_bundle
        with zipfile.ZipFile(bundle) as zf:
            errors = check_pycache_in_bundle(zf)
        assert errors == [], f"R57 bundle should have no pycache: {errors}"
