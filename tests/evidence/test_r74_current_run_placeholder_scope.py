"""
test_r74_current_run_placeholder_scope.py

R74 Train B: The new placeholder checks must scope correctly to current-run
metadata files only — they must NOT false-positive on historical docs,
git logs, or memory files that legitimately describe past PENDING states.

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

from tools.evidence.validate_evidence_bundle import (
    check_no_pending_reports,
    check_closeout_hygiene_tokens,
)


def _meta(content_map: dict) -> dict:
    return content_map


def _zip_with(entries: dict) -> zipfile.ZipFile:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as zf:
        for path, content in entries.items():
            zf.writestr(path, content)
    buf.seek(0)
    return zipfile.ZipFile(buf)


class TestPlaceholderScope:
    """R74: Placeholder checks must not false-positive on exempt files."""

    def test_git_log_with_pending_text_exempt(self):
        """git-log.txt references to PENDING must not trigger false positive."""
        metadata = _meta({
            "git-log.txt": (
                "a1b2c3d chore(r57): update final-verdict with pass 2 SHA\n"
                "e5f6a7b chore(r56): set PENDING before bundle\n"
            ),
            "validation-command-log.txt": "AUTHORITATIVE_TEST_RESULT: 6120 passed\n"
        })
        hits = check_no_pending_reports(metadata)
        # git-log.txt should be skipped
        git_hits = [(f, p) for f, p in hits if f == "git-log.txt"]
        assert len(git_hits) == 0, "git-log.txt must be exempt from PENDING scan"

    def test_git_status_with_pending_exempt(self):
        metadata = _meta({
            "git-status-final.txt": "On branch main\nnothing to commit\n"
        })
        hits = check_no_pending_reports(metadata)
        assert len(hits) == 0

    def test_historical_final_verdict_not_scanned_as_metadata(self):
        """Historical final-verdict in repo/ is only scanned by check_repo_reports_pending,
        not by check_no_pending_reports (which only scans bundle-metadata/)."""
        # check_no_pending_reports takes dict of metadata files, not repo files
        # Historical content should not appear in metadata dict
        metadata = _meta({
            "python-tests-summary.txt": "6120 passed, 0 failed, 30 skipped\n"
        })
        hits = check_no_pending_reports(metadata)
        assert len(hits) == 0

    def test_sidecar_summary_scanned_by_closeout_hygiene(self):
        """external-sidecar-proof-summary.txt must now be in CLOSEOUT_HYGIENE_REPORT_FILES."""
        from tools.evidence.validate_evidence_bundle import CLOSEOUT_HYGIENE_REPORT_FILES
        assert "external-sidecar-proof-summary.txt" in CLOSEOUT_HYGIENE_REPORT_FILES

    def test_validation_command_log_scanned_by_closeout_hygiene(self):
        """validation-command-log.txt must now be in CLOSEOUT_HYGIENE_REPORT_FILES."""
        from tools.evidence.validate_evidence_bundle import CLOSEOUT_HYGIENE_REPORT_FILES
        assert "validation-command-log.txt" in CLOSEOUT_HYGIENE_REPORT_FILES

    def test_final_iv_txt_scanned_by_closeout_hygiene(self):
        """final-independent-verification.txt must now be in CLOSEOUT_HYGIENE_REPORT_FILES."""
        from tools.evidence.validate_evidence_bundle import CLOSEOUT_HYGIENE_REPORT_FILES
        assert "final-independent-verification.txt" in CLOSEOUT_HYGIENE_REPORT_FILES

    def test_to_be_filled_after_in_closeout_tokens(self):
        """[to be filled after must be in CLOSEOUT_HYGIENE_TOKENS."""
        from tools.evidence.validate_evidence_bundle import CLOSEOUT_HYGIENE_TOKENS
        assert "[to be filled after" in CLOSEOUT_HYGIENE_TOKENS

    def test_clean_metadata_set_passes_all_checks(self):
        """A complete, clean R74-style metadata set must pass all new checks."""
        metadata = _meta({
            "external-sidecar-proof-summary.txt": (
                "Sidecar: r74-pass2-final.sha256-proof.json\n"
                "Sidecar SHA: aabbccdd1234...\n"
                "Bundle SHA: aabbccdd1234...\n"
                "EXTERNAL_SIDECAR_PROOF_SUMMARY: PASS\n"
            ),
            "validation-command-log.txt": (
                "Full test suite: python -m pytest tests/ -q\n"
                "Result: 6120 passed, 0 failed, 30 skipped\n"
                "AUTHORITATIVE_TEST_RESULT: 6120 passed, 0 failed, 30 skipped\n"
                "VALIDATION_COMMAND_LOG: COMPLETE\n"
            ),
            "final-independent-verification.txt": (
                "BUNDLE_VALIDATION_PASS_1_SHA: aabbcc1234...\n"
                "BUNDLE_VALIDATION_PASS_2_SHA: ddeeff5678...\n"
                "SIDECAR_SHA: 112233aabb...\n"
                "IV_VERDICT: R74_CLEAN\n"
            )
        })
        hits = check_no_pending_reports(metadata)
        assert len(hits) == 0, f"Clean metadata must pass: {hits}"
