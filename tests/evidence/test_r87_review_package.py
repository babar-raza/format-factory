"""
test_r87_review_package.py — Evidence tests for R87 review package enforcement.

Trains B + C: Final artifact selector, sidecar, AUTHORITATIVE_TEST_RESULT.
Sprint: FORMAT-FACTORY-R87-CLEAN-SUPERVISOR-CLOSEOUT-REVIEW-PACKAGE-POC-PRODUCT-FACTORY-DEEPENING-MEGA-TRAIN-001
"""

import sys
import zipfile
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "evidence"))


class TestPrimaryArtifactNotInnerBundle:
    """Train B: The primary upload artifact must NOT be the inner evidence bundle."""

    def test_review_package_has_inner_bundle_inside(self):
        """A valid review package contains the inner ZIP, not IS the inner ZIP."""
        review_pkg = REPO_ROOT / ".local" / "r87-supervisor-review-package.zip"
        if not review_pkg.exists():
            pytest.skip("R87 review package not yet built")
        with zipfile.ZipFile(review_pkg) as z:
            names = z.namelist()
            # Must contain an inner evidence ZIP
            inner_zips = [n for n in names if n.endswith(".zip") and "pass" in n.lower()]
            assert len(inner_zips) >= 1, "Review package must contain inner evidence ZIP"
            # Must NOT have repo/ or bundle-metadata/ at top level (that's inner bundle structure)
            top_level = {n.split("/")[0] for n in names}
            assert "repo" not in top_level, "Review package must not have repo/ at top level"
            assert "bundle-metadata" not in top_level, "Review package must not have bundle-metadata/ at top level"

    def test_review_package_contains_sidecar(self):
        """Review package must include sidecar proof file."""
        review_pkg = REPO_ROOT / ".local" / "r87-supervisor-review-package.zip"
        if not review_pkg.exists():
            pytest.skip("R87 review package not yet built")
        with zipfile.ZipFile(review_pkg) as z:
            sidecar_files = [n for n in z.namelist() if "sha256-proof" in n]
            assert len(sidecar_files) >= 1, "Review package must contain sidecar proof"

    def test_review_package_contains_authority_json(self):
        """Review package must include final-artifact-authority.json."""
        review_pkg = REPO_ROOT / ".local" / "r87-supervisor-review-package.zip"
        if not review_pkg.exists():
            pytest.skip("R87 review package not yet built")
        with zipfile.ZipFile(review_pkg) as z:
            authority_files = [n for n in z.namelist() if "authority" in n and n.endswith(".json")]
            assert len(authority_files) >= 1, "Review package must contain authority JSON"


class TestAuthoritativeTestResult:
    """Train C: Exact AUTHORITATIVE_TEST_RESULT token must exist in metadata."""

    def test_metadata_contains_exact_token(self):
        """At least one metadata file must contain 'AUTHORITATIVE_TEST_RESULT:' token."""
        metadata_dir = REPO_ROOT / ".local" / "r87-metadata"
        if not metadata_dir.exists():
            pytest.skip("R87 metadata not yet generated")
        found = False
        for f in metadata_dir.iterdir():
            if f.is_file():
                content = f.read_text(encoding="utf-8", errors="replace")
                if "AUTHORITATIVE_TEST_RESULT:" in content:
                    found = True
                    break
        assert found, "P-EVID-003: No metadata file contains exact AUTHORITATIVE_TEST_RESULT token"

    def test_authoritative_test_result_format(self):
        """The AUTHORITATIVE_TEST_RESULT line must include 'passed' count."""
        metadata_dir = REPO_ROOT / ".local" / "r87-metadata"
        if not metadata_dir.exists():
            pytest.skip("R87 metadata not yet generated")
        for f in metadata_dir.iterdir():
            if f.is_file():
                content = f.read_text(encoding="utf-8", errors="replace")
                for line in content.splitlines():
                    if "AUTHORITATIVE_TEST_RESULT:" in line:
                        assert "passed" in line.lower(), f"AUTHORITATIVE_TEST_RESULT line must include 'passed': {line}"
                        return
        pytest.skip("Token not found yet")


class TestSidecarValidation:
    """Train C: Sidecar proof must exist for sidecar-required contracts."""

    def test_sidecar_file_exists(self):
        """Sidecar proof JSON must exist alongside the evidence bundle."""
        sidecar = list((REPO_ROOT / ".local").glob("r87-pass*.sha256-proof.json"))
        if not sidecar:
            pytest.skip("R87 sidecar not yet generated")
        assert len(sidecar) >= 1
        data = json.loads(sidecar[0].read_text(encoding="utf-8"))
        assert "sha256" in data
        assert "validation_result" in data
        assert data["validation_result"] == "PASS"

    def test_no_metadata_below_minimum_size(self):
        """D87-R86-04: No metadata file should be below 50 bytes."""
        metadata_dir = REPO_ROOT / ".local" / "r87-metadata"
        if not metadata_dir.exists():
            pytest.skip("R87 metadata not yet generated")
        small_files = []
        for f in metadata_dir.iterdir():
            if f.is_file() and f.stat().st_size < 50:
                small_files.append(f.name)
        assert len(small_files) == 0, f"Metadata files below 50 bytes: {small_files}"
