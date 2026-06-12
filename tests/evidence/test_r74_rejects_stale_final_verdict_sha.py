"""
test_r74_rejects_stale_final_verdict_sha.py

R74 Train B: Document and test the stale-SHA-in-final-verdict defect class.
The inner evidence ZIP must contain a final-verdict where BUNDLE_VALIDATION_PASS_2_SHA
is either the real SHA or delegated (not a stale value from a prior build iteration).

Note: The validator cannot detect SHA staleness directly (it cannot know which SHA is
"current"). This test validates the build-order protocol used in R74 ensures the bundled
final-verdict has the correct SHA structure.

Sprint: FORMAT-FACTORY-R74-R73-CLEAN-CLOSURE-VALIDATOR-HARDENING-PRODUCT-READINESS-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
import zipfile
import io
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.evidence.validate_evidence_bundle import (
    check_repo_reports_pending,
    PENDING_MARKER_PATTERNS,
)


def _make_zip_with_verdict(content: str, run: str = "r74") -> io.BytesIO:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as zf:
        zf.writestr("bundle-metadata/sprint-id.txt",
                    "FORMAT-FACTORY-R74-TEST\n")
        zf.writestr(f"repo/reports/{run}/final-verdict.md", content)
    buf.seek(0)
    return buf


class TestFinalVerdictSHAStructure:
    """R74: final-verdict inside bundle must not have PENDING SHA fields."""

    def test_pending_pass2_sha_rejected(self):
        buf = _make_zip_with_verdict(
            "BUNDLE_VALIDATION_PASS_2_SHA: PENDING\n"
            "SIDECAR_SHA: abc123\n"
        )
        with zipfile.ZipFile(buf) as zf:
            hits = check_repo_reports_pending(zf)
        assert len(hits) > 0, "BUNDLE_VALIDATION_PASS_2_SHA: PENDING must be rejected"

    def test_pending_pass1_sha_rejected(self):
        buf = _make_zip_with_verdict(
            "BUNDLE_VALIDATION_PASS_1_SHA: PENDING\n"
        )
        with zipfile.ZipFile(buf) as zf:
            hits = check_repo_reports_pending(zf)
        assert len(hits) > 0, "BUNDLE_VALIDATION_PASS_1_SHA: PENDING must be rejected"

    def test_real_sha_passes(self):
        buf = _make_zip_with_verdict(
            "BUNDLE_VALIDATION_PASS_1_SHA: fe21c886272675dc3711ba2ff8a819e8c81e18dd393af131f3ec6a911bc8250f\n"
            "BUNDLE_VALIDATION_PASS_2_SHA: ffa23117339ec309161305cf91de8af3bece848db301f919c6b09051a45111a5\n"
            "SIDECAR_SHA: 12ecae49ff66109f32605d7883e331b01b93712f90613aa4365728533b688e5d\n"
            "DELIVERY_PACKAGE_SHA: external_delivery_manifest_authoritative\n"
        )
        with zipfile.ZipFile(buf) as zf:
            hits = check_repo_reports_pending(zf)
        assert len(hits) == 0, f"Real SHA values must pass check_repo_reports_pending: {hits}"

    def test_pending_marker_patterns_contains_required_sha_patterns(self):
        """Verify PENDING_MARKER_PATTERNS includes SHA-keyed PENDING patterns."""
        assert "BUNDLE_VALIDATION_PASS_2_SHA: PENDING" in PENDING_MARKER_PATTERNS
        assert "BUNDLE_VALIDATION_PASS_1_SHA: PENDING" in PENDING_MARKER_PATTERNS
        assert "PENDING_BUNDLE_BUILD" in PENDING_MARKER_PATTERNS
        assert "-> PENDING" in PENDING_MARKER_PATTERNS

    def test_pending_bundle_build_in_patterns(self):
        """PENDING_BUNDLE_BUILD must be in PENDING_MARKER_PATTERNS (R74 addition)."""
        assert "PENDING_BUNDLE_BUILD" in PENDING_MARKER_PATTERNS

    def test_arrow_pending_in_patterns(self):
        """'-> PENDING' must be in PENDING_MARKER_PATTERNS (R74 addition)."""
        assert "-> PENDING" in PENDING_MARKER_PATTERNS
