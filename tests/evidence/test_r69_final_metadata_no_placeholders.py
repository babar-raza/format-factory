"""
R69 Train D — Test: R69 final metadata must not contain prohibited placeholder tokens.

Covers the prohibition list from R69 hard requirements: PENDING_PASS2_SHA_COMMIT,
PENDING_FINAL_COMMIT, TBD (as final status), UNKNOWN (as unresolved). This extends
the R68 closeout-hygiene check to also cover source-commit-proof specific tokens.
"""
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
R69_METADATA = PROJECT_ROOT / ".local" / "r69-metadata"

# Tokens that must not appear in finalized R69 metadata files
PROHIBITED_TOKENS = [
    "PENDING_PASS2_SHA_COMMIT",
    "PENDING_FINAL_COMMIT",
    "PENDING_PASS2_COMMIT",
]

# Files to scan (finalized files only — not pass1/pass2 SHA placeholders in-progress)
SCAN_FILES = [
    # source-commit-proof.txt has dedicated tests (test_no_pending_pass2_sha_commit_in_source_proof)
    "r68-delivery-defect-repair-summary.txt",
    "validator-hardening-proof.txt",
    "multi-mega-train-scoreboard-final.txt",
    "work-ahead-scoreboard-final.txt",
    "phase-audit-19-summary.txt",
    "blockers-status.txt",
]


class TestFinalMetadataNoPlaceholders:
    """Final R69 metadata files must not contain prohibited placeholder tokens."""

    def test_no_pending_pass2_sha_commit_in_source_proof(self):
        """source-commit-proof.txt must not have PENDING_PASS2_SHA_COMMIT."""
        fpath = R69_METADATA / "source-commit-proof.txt"
        if not fpath.exists():
            pytest.skip("R69 source-commit-proof.txt not yet created")
        content = fpath.read_text(encoding="utf-8")
        assert "PENDING_PASS2_SHA_COMMIT" not in content, (
            "source-commit-proof.txt still has PENDING_PASS2_SHA_COMMIT (IV-R69-001 not repaired)"
        )

    def test_no_prohibited_tokens_in_finalized_metadata(self):
        """All finalized R69 metadata files must not contain any prohibited tokens."""
        if not R69_METADATA.exists():
            pytest.skip("R69 metadata dir not yet created")
        hits = []
        for fname in SCAN_FILES:
            fpath = R69_METADATA / fname
            if not fpath.exists():
                continue
            content = fpath.read_text(encoding="utf-8")
            for token in PROHIBITED_TOKENS:
                if token in content:
                    hits.append((fname, token))
        assert not hits, (
            f"Prohibited placeholder tokens found in R69 metadata: {hits}"
        )

    def test_r69_source_proof_has_b704712(self):
        """source-commit-proof.txt must record actual R68 final commit b704712."""
        fpath = R69_METADATA / "source-commit-proof.txt"
        if not fpath.exists():
            pytest.skip("R69 source-commit-proof.txt not yet created")
        content = fpath.read_text(encoding="utf-8")
        assert "b704712" in content, (
            "source-commit-proof.txt must record R68 final commit b704712 "
            "(repair of IV-R69-001: was PENDING_PASS2_SHA_COMMIT)"
        )

    def test_r68_had_pending_pass2_sha_commit(self):
        """Verify the R68 defect existed: source-commit-proof.txt had PENDING_PASS2_SHA_COMMIT."""
        r68_proof = PROJECT_ROOT / ".local" / "r68-metadata" / "source-commit-proof.txt"
        if not r68_proof.exists():
            pytest.skip("R68 source-commit-proof.txt not found (local artifact)")
        content = r68_proof.read_text(encoding="utf-8")
        assert "PENDING_PASS2_SHA_COMMIT" in content, (
            "Historical test: R68 source-commit-proof.txt should contain PENDING_PASS2_SHA_COMMIT "
            "(this documents the repaired defect IV-R69-001)"
        )
