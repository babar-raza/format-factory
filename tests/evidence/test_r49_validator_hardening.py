"""
tests/evidence/test_r49_validator_hardening.py

R49 validator hardening tests: proof-file placeholder guard.

Verifies that check_proof_file_finality():
  - Returns errors for stale placeholder patterns
  - Passes for clean, finalized proof files
  - Does not false-positive on auto-proof transient placeholder content

Sprint: FORMAT-FACTORY-R49-EDITABLE-OBJECT-MODEL-POC-BASELINE-AND-STRATEGY-SYNC-001
"""

import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Import the validator
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "evidence"))

from validate_evidence_bundle import check_proof_file_finality


# ---------------------------------------------------------------------------
# Tests: stale placeholder patterns
# ---------------------------------------------------------------------------

class TestProofFileFinality:
    """R49: check_proof_file_finality guard tests."""

    def test_stale_updated_after_pattern(self):
        """'(updated after' triggers placeholder error."""
        content = {
            "final-bundle-validation-proof.txt": (
                "Bundle path: .local/evidence-bundles/r49-bundle.zip\n"
                "SHA-256: (updated after pass 2 build)\n"
                "Entries: 2300\n"
            )
        }
        hits = check_proof_file_finality(content)
        assert len(hits) == 1
        assert "PROOF_FILE_PLACEHOLDER" in hits[0]

    def test_stale_to_be_recorded_pattern(self):
        """'to be recorded' triggers placeholder error."""
        content = {
            "final-bundle-validation-proof.txt": (
                "SHA-256: to be recorded after bundle completes\n"
            )
        }
        hits = check_proof_file_finality(content)
        assert len(hits) == 1
        assert "PROOF_FILE_PLACEHOLDER" in hits[0]

    def test_stale_pass2_in_progress_pattern(self):
        """'STATUS: PASS 2 IN PROGRESS' triggers placeholder error."""
        content = {
            "final-bundle-validation-proof.txt": (
                "STATUS: PASS 2 IN PROGRESS — final SHA to be recorded\n"
            )
        }
        hits = check_proof_file_finality(content)
        assert len(hits) == 1
        assert "PROOF_FILE_PLACEHOLDER" in hits[0]

    def test_stale_final_sha_to_be_recorded(self):
        """'final SHA to be recorded' triggers placeholder error (R48 caveat)."""
        content = {
            "final-bundle-validation-proof.txt": (
                "STATUS: PASS 2 IN PROGRESS — final SHA to be recorded\n"
            )
        }
        hits = check_proof_file_finality(content)
        assert len(hits) == 1

    def test_clean_proof_passes(self):
        """Finalized proof file with no placeholder patterns passes."""
        content = {
            "final-bundle-validation-proof.txt": (
                "Bundle: .local/evidence-bundles/r49-bundle.zip\n"
                "SHA-256: abc123def456abc123def456abc123def456abc123def456abc123def456abc1\n"
                "Entries: 2300\n"
                "Size: 4200000 bytes\n"
                "Metadata files: 32\n"
                "BUNDLE_VALIDATION: PASS\n"
            )
        }
        hits = check_proof_file_finality(content)
        assert hits == [], f"Clean proof should pass; got: {hits}"

    def test_absent_proof_file_returns_empty(self):
        """Missing proof file returns empty list (caught by required_metadata_files check)."""
        hits = check_proof_file_finality({})
        assert hits == []

    def test_auto_proof_transient_placeholder_does_not_trigger(self):
        """Auto-proof's transient 'will be replaced' text does NOT trigger the guard.

        The auto_proof system writes 'PLACEHOLDER — will be replaced after candidate
        validation' during pass 1. This must NOT be flagged by the finality check
        (the check only fires when --check-no-pending is active, by which time the
        proof file should be fully written by auto_proof).
        """
        content = {
            "final-bundle-validation-proof.txt": (
                "PLACEHOLDER — will be replaced after candidate validation\n"
            )
        }
        hits = check_proof_file_finality(content)
        assert hits == [], (
            f"Auto-proof transient placeholder must not trigger finality check; got: {hits}"
        )

    def test_only_one_hit_per_file(self):
        """Multiple matching patterns in one file produce only one error (early exit)."""
        content = {
            "final-bundle-validation-proof.txt": (
                "(updated after build)\nto be recorded\nSTATUS: PASS 2 IN PROGRESS\n"
            )
        }
        hits = check_proof_file_finality(content)
        assert len(hits) == 1, "Should short-circuit after first match"
