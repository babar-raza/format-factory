"""
test_r75_rejects_to_be_filled_after_bundle_build.py

R75 Train C: Validator must reject bundles where final-independent-verification.txt
contains 'TO_BE_FILLED_AFTER_BUNDLE_BUILD' (without brackets — R74 defect D01).

The R74 defect used uppercase underscore-joined tokens (not bracket-wrapped).
The R74 validator only caught bracket-wrapped variants like '[to be filled after X]'.
R75 adds coverage for the bare uppercase form.

Sprint: FORMAT-FACTORY-R75-FINAL-ARTIFACT-AUTHORITY-REPAIR-RC-SEAL-PRODUCT-ADVANCEMENT-MEGA-TRAIN-001
"""
from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.evidence.validate_evidence_bundle import (
    check_closeout_hygiene_tokens,
    check_no_pending_reports,
)


def _make_zip_with_metadata(fname: str, content: str) -> io.BytesIO:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(f"bundle-metadata/{fname}", content)
    buf.seek(0)
    return buf


class TestRejectsToBeFilledAfterBundleBuild:
    """R75 D01: TO_BE_FILLED_AFTER_BUNDLE_BUILD in final-iv must be caught."""

    def test_to_be_filled_after_bundle_build_caught_by_pending_check(self):
        """check_no_pending_reports must catch TO_BE_FILLED_AFTER_BUNDLE_BUILD."""
        content = {
            "final-independent-verification.txt": (
                "R75 Final Independent Verification\n"
                "BUNDLE_VALIDATION_PASS_1_SHA: TO_BE_FILLED_AFTER_BUNDLE_BUILD\n"
                "BUNDLE_VALIDATION_PASS_2_SHA: TO_BE_FILLED_AFTER_BUNDLE_BUILD\n"
                "FINAL_IV: PASS_PENDING_BUNDLE_SHA\n"
            )
        }
        hits = check_no_pending_reports(content)
        assert len(hits) > 0, (
            "TO_BE_FILLED_AFTER_BUNDLE_BUILD must be caught by check_no_pending_reports"
        )
        assert any(
            "TO_BE_FILLED_AFTER_BUNDLE_BUILD" in pattern
            for _, pattern in hits
        ), f"Expected TO_BE_FILLED_AFTER_BUNDLE_BUILD in hits, got: {hits}"

    def test_to_be_filled_after_bundle_build_caught_by_closeout_hygiene(self):
        """check_closeout_hygiene_tokens must catch TO_BE_FILLED_AFTER_BUNDLE_BUILD."""
        buf = _make_zip_with_metadata(
            "final-independent-verification.txt",
            "BUNDLE_VALIDATION_PASS_1_SHA: TO_BE_FILLED_AFTER_BUNDLE_BUILD\n",
        )
        with zipfile.ZipFile(buf) as zf:
            hits = check_closeout_hygiene_tokens(zf)
        assert len(hits) > 0, (
            "TO_BE_FILLED_AFTER_BUNDLE_BUILD must be caught by closeout hygiene check"
        )

    def test_pass_pending_bundle_sha_caught_by_pending_check(self):
        """check_no_pending_reports must catch PASS_PENDING_BUNDLE_SHA."""
        # Use a file that doesn't have TO_BE_FILLED so we can test PASS_PENDING alone
        content = {
            "final-independent-verification.txt": (
                "BUNDLE_VALIDATION_PASS_2_SHA: delegated_to_final_artifact_authority_json\n"
                "FINAL_IV: PASS_PENDING_BUNDLE_SHA\n"
            )
        }
        hits = check_no_pending_reports(content)
        assert len(hits) > 0, (
            "PASS_PENDING_BUNDLE_SHA must be caught by check_no_pending_reports"
        )
        assert any(
            "PASS_PENDING_BUNDLE_SHA" in pattern
            for _, pattern in hits
        ), f"Expected PASS_PENDING_BUNDLE_SHA in hits, got: {hits}"

    def test_pass_pending_bundle_sha_caught_by_closeout_hygiene(self):
        """check_closeout_hygiene_tokens must catch PASS_PENDING_BUNDLE_SHA."""
        buf = _make_zip_with_metadata(
            "final-independent-verification.txt",
            "BUNDLE_VALIDATION_PASS_2_SHA: delegated_to_final_artifact_authority_json\n"
            "FINAL_IV: PASS_PENDING_BUNDLE_SHA\n",
        )
        with zipfile.ZipFile(buf) as zf:
            hits = check_closeout_hygiene_tokens(zf)
        assert len(hits) > 0, (
            "PASS_PENDING_BUNDLE_SHA must be caught by closeout hygiene check"
        )

    def test_delegation_label_is_accepted(self):
        """delegated_to_final_artifact_authority_json is a valid non-placeholder value."""
        content = {
            "final-independent-verification.txt": (
                "R75 Final Independent Verification\n"
                "AUTHORITATIVE_TEST_RESULT: 6200 passed, 0 failed, 24 skipped\n"
                "BUNDLE_VALIDATION_PASS_1_SHA: abc123def456" + "0" * 52 + "\n"
                "BUNDLE_VALIDATION_PASS_2_SHA: delegated_to_final_artifact_authority_json\n"
                "SIDECAR_SHA: delegated_to_final_artifact_authority_json\n"
                "FINAL_IV: PASS_SEE_FINAL_ARTIFACT_AUTHORITY\n"
            )
        }
        hits = check_no_pending_reports(content)
        assert len(hits) == 0, (
            f"Delegation labels must not be rejected as PENDING, got: {hits}"
        )

    def test_r74_exact_defect_pattern_now_caught(self):
        """Prove the exact R74 defect D01 pattern is caught by R75 validator."""
        r74_defect_content = {
            "final-independent-verification.txt": (
                "R74 Final Independent Verification\n"
                "sprint_id: FORMAT-FACTORY-R74-R73-CLEAN-CLOSURE-VALIDATOR-HARDENING-PRODUCT-READINESS-MEGA-TRAIN-001\n"
                "AUTHORITATIVE_TEST_RESULT: 6097 passed, 0 failed, 24 skipped\n"
                "BUNDLE_VALIDATION_PASS_1_SHA: TO_BE_FILLED_AFTER_BUNDLE_BUILD\n"
                "BUNDLE_VALIDATION_PASS_2_SHA: TO_BE_FILLED_AFTER_BUNDLE_BUILD\n"
                "SIDECAR_SHA: TO_BE_FILLED_AFTER_BUNDLE_BUILD\n"
                "FINAL_IV: PASS_PENDING_BUNDLE_SHA\n"
            )
        }
        hits = check_no_pending_reports(r74_defect_content)
        assert len(hits) > 0, (
            "Exact R74 D01 defect pattern must now be caught by the R75-hardened validator"
        )
