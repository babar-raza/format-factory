"""
test_r74_rejects_pending_bundle_build_in_sidecar_summary.py

R74 Train B: Validator must reject bundles where external-sidecar-proof-summary.txt
contains PENDING_BUNDLE_BUILD placeholder.

Sprint: FORMAT-FACTORY-R74-R73-CLEAN-CLOSURE-VALIDATOR-HARDENING-PRODUCT-READINESS-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
import zipfile
import io
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.evidence.validate_evidence_bundle import check_no_pending_reports


def _make_metadata(content: str) -> dict:
    return {"external-sidecar-proof-summary.txt": content}


class TestRejectsPendingBundleBuild:
    """R74: PENDING_BUNDLE_BUILD in sidecar summary must be rejected."""

    def test_pending_bundle_build_detected(self):
        metadata = _make_metadata(
            "R73 External Sidecar Proof Summary\n"
            "Sidecar file: .local/r73-pass2-final.sha256-proof.json\n"
            "EXTERNAL_SIDECAR_PROOF_SUMMARY: PENDING_BUNDLE_BUILD\n"
        )
        hits = check_no_pending_reports(metadata)
        assert len(hits) > 0, "PENDING_BUNDLE_BUILD must be detected as a PENDING marker"
        assert any("external-sidecar-proof-summary.txt" in f for f, _ in hits)

    def test_clean_sidecar_summary_passes(self):
        metadata = _make_metadata(
            "R74 External Sidecar Proof Summary\n"
            "Sidecar: r74-pass2-final.sha256-proof.json\n"
            "Sidecar SHA: abcdef1234...\n"
            "Bundle SHA: abcdef1234...\n"
            "EXTERNAL_SIDECAR_PROOF_SUMMARY: PASS\n"
        )
        hits = check_no_pending_reports(metadata)
        assert len(hits) == 0, f"Clean sidecar summary must pass but got: {hits}"

    def test_pending_bundle_build_uppercase_detected(self):
        metadata = _make_metadata(
            "EXTERNAL_SIDECAR_PROOF_SUMMARY: PENDING_BUNDLE_BUILD\n"
        )
        hits = check_no_pending_reports(metadata)
        # PENDING_BUNDLE_BUILD is the canonical uppercase form
        
        assert len(hits) > 0, "PENDING_BUNDLE_BUILD (uppercase) must be caught by PENDING_MARKER_PATTERNS"

    def test_r73_style_stale_bundle_would_fail(self):
        """Prove the exact R73 stale sidecar summary would now fail validation."""
        r73_stale_content = (
            "R73 External Sidecar Proof Summary\n"
            "Date: 2026-05-29\n"
            "Sidecar proof policy: external_sidecar (sidecar_required: true)\n"
            "Sidecar file: .local/r73-pass2-final.sha256-proof.json "
            "(to be generated after Pass 2 bundle build)\n"
            "EXTERNAL_SIDECAR_PROOF_SUMMARY: PENDING_BUNDLE_BUILD\n"
        )
        metadata = _make_metadata(r73_stale_content)
        hits = check_no_pending_reports(metadata)
        assert len(hits) > 0, "R73-style stale sidecar summary must now be rejected by validator"
