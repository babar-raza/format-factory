"""
test_r75_detects_pass_number_drift.py

R75 Train C: Validator must detect pass-number drift in final-bundle-validation-proof.txt.

R74 defect D02: The inner ZIP's proof file claimed 'Bundle: r74-pass4-final.zip'
while the actual bundle being validated was r74-pass5-final.zip. The validator
issued a SHA mismatch WARNING but no ERROR for this condition.

R75 adds check_pass_number_drift() which errors when the pass number in the
proof file differs from the actual bundle's pass number.

Sprint: FORMAT-FACTORY-R75-FINAL-ARTIFACT-AUTHORITY-REPAIR-RC-SEAL-PRODUCT-ADVANCEMENT-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.evidence.validate_evidence_bundle import check_pass_number_drift


class TestDetectsPassNumberDrift:
    """R75 D02: Pass-number drift in proof file must be detected."""

    def test_r74_exact_defect_caught(self):
        """Exact R74 D02 defect: proof claims pass4, actual bundle is pass5."""
        metadata = {
            "final-bundle-validation-proof.txt": (
                "Final Bundle Validation Proof -- R74\n"
                "Bundle: r74-pass4-final.zip\n"
                "SHA-256: 4cfd346c81609d00b1a312b32eec2749eaef8cebcddb7ff78f9f08a500f1c703\n"
                "BUNDLE_VALIDATION: PASS\n"
            )
        }
        hits = check_pass_number_drift(metadata, "r74-pass5-final.zip")
        assert len(hits) == 1, f"Pass number drift (4 vs 5) must be caught, got: {hits}"
        assert "PASS_NUMBER_DRIFT" in hits[0]
        assert "pass 4" in hits[0]
        assert "pass 5" in hits[0]

    def test_matching_pass_number_passes(self):
        """Proof file and actual bundle have same pass number — no error."""
        metadata = {
            "final-bundle-validation-proof.txt": (
                "Bundle: r75-pass2-final.zip\n"
                "SHA-256: abc123\n"
                "BUNDLE_VALIDATION: PASS\n"
            )
        }
        hits = check_pass_number_drift(metadata, "r75-pass2-final.zip")
        assert len(hits) == 0, f"Matching pass numbers must pass, got: {hits}"

    def test_pass1_proof_vs_pass2_bundle_caught(self):
        """Pass1 proof vs pass2 bundle — should be caught."""
        metadata = {
            "final-bundle-validation-proof.txt": (
                "Bundle: r75-pass1-final.zip\n"
                "SHA-256: abc123\n"
                "BUNDLE_VALIDATION: PASS\n"
            )
        }
        hits = check_pass_number_drift(metadata, "r75-pass2-final.zip")
        assert len(hits) == 1, "Pass1 proof vs pass2 bundle must be caught"

    def test_no_proof_file_skips_check(self):
        """If no proof file present, drift check is skipped (file absence handled elsewhere)."""
        hits = check_pass_number_drift({}, "r75-pass2-final.zip")
        assert len(hits) == 0, "Missing proof file must skip drift check"

    def test_proof_without_bundle_line_skips_check(self):
        """Old-format proof files without 'Bundle:' line skip the check."""
        metadata = {
            "final-bundle-validation-proof.txt": (
                "BUNDLE_VALIDATION: PASS\n"
                "SHA-256: abc123\n"
            )
        }
        hits = check_pass_number_drift(metadata, "r75-pass2-final.zip")
        assert len(hits) == 0, "Proof without Bundle: line must skip drift check"

    def test_case_insensitive_bundle_line_parsed(self):
        """'bundle: ...' (lowercase) is also parsed correctly."""
        metadata = {
            "final-bundle-validation-proof.txt": (
                "bundle: r75-pass1-final.zip\n"
                "BUNDLE_VALIDATION: PASS\n"
            )
        }
        hits = check_pass_number_drift(metadata, "r75-pass2-final.zip")
        assert len(hits) == 1, "Lowercase 'bundle:' must also be parsed"

    def test_three_pass_gap_caught(self):
        """Proof claims pass1, actual is pass4 — large gap still caught."""
        metadata = {
            "final-bundle-validation-proof.txt": (
                "Bundle: r75-pass1-final.zip\n"
                "SHA-256: abc123\n"
                "BUNDLE_VALIDATION: PASS\n"
            )
        }
        hits = check_pass_number_drift(metadata, "r75-pass4-final.zip")
        assert len(hits) == 1, "Pass gap of 3 must also be caught"
        assert "pass 1" in hits[0]
        assert "pass 4" in hits[0]
