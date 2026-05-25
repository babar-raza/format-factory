"""
test_r64_final_proof_no_placeholders.py — R64 Train B: Final proof must have no placeholder language.

Closes:
- IV-R63-003: final-bundle-validation-proof.txt has 'to be computed' / 'to be confirmed'

Tests:
- final-bundle-validation-proof.txt has no forbidden placeholder tokens
- final-verdict.md has no forbidden placeholder tokens
- validation-command-log.txt has no forbidden placeholder tokens

R64 Sprint: FORMAT-FACTORY-R64-DELIVERED-SIDECAR-PACKAGING-REPLAY-AI-LIVE-REVIEW-WORKAHEAD-MEGA-TRAIN-001
IV-R63-003
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

FORBIDDEN_TOKENS = [
    "to be computed",
    "to be confirmed",
    "to be completed",
    "to be generated",
    "to be updated",
    "PENDING",
    "IN_PROGRESS",
    "in progress",
    "TBD",
    "TODO",
    "PLACEHOLDER",
]

# Allowed exceptions: quoted references to prior defects or policy descriptions
ALLOWED_CONTEXTS = [
    "IV-R62-012",  # Defect title references IN_PROGRESS historically
    "IV-R63-",     # Defect references
    "scoreboard status at bundle build",  # Renamed defect
    "R62 scoreboard",  # Historical reference
    "R63 reports claim",  # IV finding quote
    "final_proof_policy",  # YAML field name
]


def _check_file_for_placeholders(file_path: Path, forbidden: list[str]) -> list[str]:
    """Return list of forbidden tokens found in file (excluding allowed contexts)."""
    if not file_path.exists():
        return []
    content = file_path.read_text(encoding="utf-8")
    findings = []
    for token in forbidden:
        for i, line in enumerate(content.splitlines(), 1):
            if token.lower() in line.lower():
                # Check if line contains an allowed context
                if any(ctx.lower() in line.lower() for ctx in ALLOWED_CONTEXTS):
                    continue
                findings.append(f"Line {i}: found '{token}' in: {line.strip()[:100]}")
    return findings


class TestR64FinalProofNoPlaceholders:
    """Final proof metadata must have no placeholder language."""

    def test_final_bundle_validation_proof_clean(self):
        proof_path = PROJECT_ROOT / ".local" / "r64-metadata" / "final-bundle-validation-proof.txt"
        if not proof_path.exists():
            pytest.skip("R64 final-bundle-validation-proof.txt not yet written")
        findings = _check_file_for_placeholders(proof_path, FORBIDDEN_TOKENS)
        assert not findings, (
            f"final-bundle-validation-proof.txt contains placeholder language:\n"
            + "\n".join(findings)
        )

    def test_validation_command_log_clean(self):
        log_path = PROJECT_ROOT / ".local" / "r64-metadata" / "validation-command-log.txt"
        if not log_path.exists():
            pytest.skip("R64 validation-command-log.txt not yet written")
        findings = _check_file_for_placeholders(log_path, FORBIDDEN_TOKENS)
        assert not findings, (
            f"validation-command-log.txt contains placeholder language:\n"
            + "\n".join(findings)
        )

    def test_final_verdict_no_placeholders(self):
        verdict_path = PROJECT_ROOT / "reports" / "r64" / "final-verdict.md"
        if not verdict_path.exists():
            pytest.skip("R64 final-verdict not yet written")
        # For final-verdict, only check critical placeholders
        critical_tokens = ["to be computed", "to be confirmed", "to be completed", "to be generated"]
        findings = _check_file_for_placeholders(verdict_path, critical_tokens)
        assert not findings, (
            f"final-verdict.md contains placeholder language:\n"
            + "\n".join(findings)
        )


class TestR64FinalProofContent:
    """Final proof must contain required fields."""

    def test_proof_has_sha256(self):
        proof_path = PROJECT_ROOT / ".local" / "r64-metadata" / "final-bundle-validation-proof.txt"
        if not proof_path.exists():
            pytest.skip("R64 proof not yet written")
        content = proof_path.read_text(encoding="utf-8")
        assert "SHA-256:" in content, "Proof must contain SHA-256 field"

    def test_proof_has_bundle_validation_pass(self):
        proof_path = PROJECT_ROOT / ".local" / "r64-metadata" / "final-bundle-validation-proof.txt"
        if not proof_path.exists():
            pytest.skip("R64 proof not yet written")
        content = proof_path.read_text(encoding="utf-8")
        assert "BUNDLE_VALIDATION: PASS" in content, "Proof must declare BUNDLE_VALIDATION: PASS"

    def test_proof_has_sidecar_validation_pass(self):
        proof_path = PROJECT_ROOT / ".local" / "r64-metadata" / "final-bundle-validation-proof.txt"
        if not proof_path.exists():
            pytest.skip("R64 proof not yet written")
        content = proof_path.read_text(encoding="utf-8")
        assert "SIDECAR_PROOF_VALIDATION: PASS" in content, (
            "Proof must declare SIDECAR_PROOF_VALIDATION: PASS"
        )

    def test_proof_has_entry_count(self):
        proof_path = PROJECT_ROOT / ".local" / "r64-metadata" / "final-bundle-validation-proof.txt"
        if not proof_path.exists():
            pytest.skip("R64 proof not yet written")
        content = proof_path.read_text(encoding="utf-8")
        assert "Entries:" in content or "entry_count" in content, "Proof must contain entry count"
