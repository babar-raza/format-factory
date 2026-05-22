"""R51 Lane 1B/1C/1D: Validator hardening tests.

Tests for:
- Lane 1B: R51 extended proof-file placeholder patterns (PLACEHOLDER, will-be-replaced, etc.)
- Lane 1C: Final verdict unresolved-closeout text detection
- Lane 1D: Contract clean-git strictness warning
"""
import io
import zipfile
from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tools.evidence.validate_evidence_bundle import (
    PROOF_FILE_PLACEHOLDER_PATTERNS,
    check_proof_file_finality,
    check_verdict_unresolved_closeout,
    check_contract_clean_git_strictness,
)


# ─── Lane 1B: R51 proof-file placeholder patterns ────────────────────────────

class TestR51ProofFilePlaceholderPatterns:
    """R51 Lane 1B: New placeholder patterns must be present and detected."""

    def test_placeholder_word_in_patterns(self):
        """'PLACEHOLDER' must be in guard list — R50 bundle proof had this exact text."""
        assert any("PLACEHOLDER" in p for p in PROOF_FILE_PLACEHOLDER_PATTERNS)

    def test_will_be_replaced_in_patterns(self):
        """'will be replaced' must be in guard list — R50 bundle proof exact text."""
        assert any("will be replaced" in p for p in PROOF_FILE_PLACEHOLDER_PATTERNS)

    def test_candidate_validation_in_patterns(self):
        """'candidate validation' must be in guard list — R50 bundle proof exact text."""
        assert any("candidate validation" in p for p in PROOF_FILE_PLACEHOLDER_PATTERNS)

    def test_r50_bundle_exact_placeholder_caught(self):
        """Exact R50 bundle proof placeholder text must be caught."""
        content = {"final-bundle-validation-proof.txt":
                   "PLACEHOLDER \ufffd will be replaced after candidate validation"}
        hits = check_proof_file_finality(content)
        assert len(hits) == 1, f"Expected 1 hit, got {hits}"
        assert "PROOF_FILE_PLACEHOLDER" in hits[0]

    def test_in_progress_pattern_caught(self):
        """'IN PROGRESS' pattern must be caught."""
        content = {"final-bundle-validation-proof.txt": "STATUS: IN PROGRESS — build not done"}
        hits = check_proof_file_finality(content)
        assert len(hits) == 1

    def test_tbd_pattern_caught(self):
        """'TBD' must be caught."""
        content = {"final-bundle-validation-proof.txt": "SHA-256: TBD"}
        hits = check_proof_file_finality(content)
        assert len(hits) == 1

    def test_sha_to_follow_caught(self):
        """'sha to follow' must be caught."""
        content = {"final-bundle-validation-proof.txt": "Pass 2 SHA to follow"}
        hits = check_proof_file_finality(content)
        assert len(hits) == 1

    def test_real_proof_passes(self):
        """A fully-resolved proof file must not trigger any hits."""
        real_proof = (
            "R51 Final Bundle Validation Proof\n"
            "Bundle: r51-installed-artifact-baseline.zip\n"
            "SHA-256: abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890\n"
            "Entries: 2400\n"
            "Size: 4,500,000 bytes\n"
            "Validation: BUNDLE_VALIDATION: PASS\n"
        )
        content = {"final-bundle-validation-proof.txt": real_proof}
        hits = check_proof_file_finality(content)
        assert len(hits) == 0, f"Unexpected hits in clean proof: {hits}"


# ─── Lane 1C: Final verdict unresolved-closeout text ─────────────────────────

def _make_bundle_with_verdict(verdict_content: str) -> io.BytesIO:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("repo/reports/r51/final-verdict.md", verdict_content)
    buf.seek(0)
    return buf


class TestVerdictUnresolvedCloseout:
    """R51 Lane 1C: Final verdict must not contain unresolved closeout text."""

    def test_to_follow_caught(self):
        """'to follow' in verdict triggers error."""
        buf = _make_bundle_with_verdict(
            "# R51 Final Verdict\n"
            "VERDICT: R51_COMPLETE\n"
            "Pass 2 SHA to follow\n"
        )
        with zipfile.ZipFile(buf) as zf:
            hits = check_verdict_unresolved_closeout(zf)
        assert len(hits) == 1
        assert "VERDICT_UNRESOLVED_CLOSEOUT" in hits[0]

    def test_candidate_validation_in_verdict_caught(self):
        """'candidate validation' in verdict triggers error."""
        buf = _make_bundle_with_verdict(
            "# R51 Final Verdict\n"
            "VERDICT: R51_COMPLETE\n"
            "SHA will be updated after candidate validation\n"
        )
        with zipfile.ZipFile(buf) as zf:
            hits = check_verdict_unresolved_closeout(zf)
        assert len(hits) == 1

    def test_computed_after_in_verdict_caught(self):
        """'computed after' in verdict triggers error."""
        buf = _make_bundle_with_verdict(
            "# R51 Final Verdict\n"
            "Entries: (computed after pass 2 build)\n"
        )
        with zipfile.ZipFile(buf) as zf:
            hits = check_verdict_unresolved_closeout(zf)
        assert len(hits) == 1

    def test_clean_verdict_passes(self):
        """A verdict with actual SHA/entries/size must pass."""
        buf = _make_bundle_with_verdict(
            "# R51 Final Verdict\n"
            "VERDICT: R51_INSTALLED_ARTIFACT_BASELINE_CLEAN_AND_AI_ACCELERATION_PROVEN\n"
            "Pass 2 SHA-256: abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890\n"
            "Entries: 2400\nSize: 4,500,000 bytes\n"
            "BUNDLE_VALIDATION: PASS\n"
        )
        with zipfile.ZipFile(buf) as zf:
            hits = check_verdict_unresolved_closeout(zf)
        assert len(hits) == 0, f"Unexpected hits: {hits}"

    def test_no_final_verdict_file_passes(self):
        """Bundle without final-verdict.md in reports must pass (no false positive)."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("bundle-metadata/sprint-id.txt", "R51")
        buf.seek(0)
        with zipfile.ZipFile(buf) as zf:
            hits = check_verdict_unresolved_closeout(zf)
        assert len(hits) == 0


# ─── Lane 1D: Contract clean-git strictness ──────────────────────────────────

class TestContractCleanGitStrictness:
    """R51 Lane 1D: Clean-closure contracts must use require_clean_git: true."""

    def _make_bundle_with_verdict_for_contract(self, verdict_text: str) -> io.BytesIO:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("repo/reports/r51/final-verdict.md", verdict_text)
        buf.seek(0)
        return buf

    def test_clean_verdict_with_require_false_warns(self):
        """require_clean_git: false + COMPLETE verdict triggers warning."""
        contract = {"require_clean_git": False}
        buf = self._make_bundle_with_verdict_for_contract(
            "VERDICT: R51_INSTALLED_ARTIFACT_BASELINE_COMPLETE\n"
        )
        with zipfile.ZipFile(buf) as zf:
            warnings = check_contract_clean_git_strictness(contract, zf)
        assert len(warnings) == 1
        assert "CONTRACT_CLEAN_GIT_WEAK" in warnings[0]

    def test_require_true_suppresses_warning(self):
        """require_clean_git: true must not trigger warning."""
        contract = {"require_clean_git": True}
        buf = self._make_bundle_with_verdict_for_contract(
            "VERDICT: R51_COMPLETE\n"
        )
        with zipfile.ZipFile(buf) as zf:
            warnings = check_contract_clean_git_strictness(contract, zf)
        assert len(warnings) == 0

    def test_dirty_tree_blocked_exempted(self):
        """DIRTY_TREE_BLOCKED verdict exempts the require_clean_git: false rule."""
        contract = {"require_clean_git": False}
        buf = self._make_bundle_with_verdict_for_contract(
            "VERDICT: R51_EVIDENCE_CLOSEOUT_DIRTY_TREE_BLOCKED\n"
        )
        with zipfile.ZipFile(buf) as zf:
            warnings = check_contract_clean_git_strictness(contract, zf)
        assert len(warnings) == 0
