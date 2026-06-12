"""
R69 Train D — Test: source-commit-proof.txt must not contain PENDING_PASS2_SHA_COMMIT.

Covers IV-R69-001: R68's source-commit-proof.txt had PENDING_PASS2_SHA_COMMIT which
was never replaced with the actual final commit SHA. This test ensures R69 repairs
that defect and prevents it from recurring.
"""
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
R69_METADATA = PROJECT_ROOT / ".local" / "r69-metadata"


class TestSourceCommitProofNoPending:
    """source-commit-proof.txt must not have PENDING_PASS2_SHA_COMMIT or PENDING_FINAL_COMMIT."""

    def test_r68_metadata_had_pending_pass2_sha_commit(self):
        """Confirm the R68 defect: source-commit-proof.txt had PENDING_PASS2_SHA_COMMIT."""
        r68_proof = PROJECT_ROOT / ".local" / "r68-metadata" / "source-commit-proof.txt"
        if not r68_proof.exists():
            pytest.skip("R68 source-commit-proof.txt not found (local artifact)")
        content = r68_proof.read_text(encoding="utf-8")
        assert "PENDING_PASS2_SHA_COMMIT" in content, (
            "R68 source-commit-proof.txt should have had PENDING_PASS2_SHA_COMMIT "
            "(this test documents the historical defect IV-R69-001)"
        )

    def test_r69_source_commit_proof_no_pending_pass2_sha_commit(self):
        """R69 source-commit-proof.txt must not contain PENDING_PASS2_SHA_COMMIT."""
        r69_proof = R69_METADATA / "source-commit-proof.txt"
        if not r69_proof.exists():
            pytest.skip("R69 source-commit-proof.txt not yet created")
        content = r69_proof.read_text(encoding="utf-8")
        assert "PENDING_PASS2_SHA_COMMIT" not in content, (
            "R69 source-commit-proof.txt must not contain PENDING_PASS2_SHA_COMMIT. "
            "Replace with actual final commit SHA (IV-R69-001 repair)."
        )

    def test_r69_source_commit_proof_no_pending_final_commit(self):
        """R69 source-commit-proof.txt must not contain PENDING_FINAL_COMMIT."""
        r69_proof = R69_METADATA / "source-commit-proof.txt"
        if not r69_proof.exists():
            pytest.skip("R69 source-commit-proof.txt not yet created")
        content = r69_proof.read_text(encoding="utf-8")
        assert "PENDING_FINAL_COMMIT" not in content, (
            "R69 source-commit-proof.txt must not contain PENDING_FINAL_COMMIT. "
            "Replace with actual final commit SHA."
        )

    def test_r69_source_commit_proof_has_real_r68_commit(self):
        """R69 source-commit-proof.txt must record actual R68 final commit b704712."""
        r69_proof = R69_METADATA / "source-commit-proof.txt"
        if not r69_proof.exists():
            pytest.skip("R69 source-commit-proof.txt not yet created")
        content = r69_proof.read_text(encoding="utf-8")
        assert "b704712" in content, (
            "R69 source-commit-proof.txt must record R68 final commit b704712 "
            "(repaired from PENDING_PASS2_SHA_COMMIT, IV-R69-001)."
        )
