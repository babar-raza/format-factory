"""
R45 MT3 Lane 3C: Validator hardening guard tests.

Verifies:
1. check_package_proof_present triggers for LOCAL_RC verdicts (not just POC_READY).
2. check_package_proof_present triggers for BASELINE_READY verdicts.
3. check_package_proof_present triggers for TWO_PRODUCT verdicts.
4. check_package_proof_present triggers for RELEASE_CANDIDATE verdicts.
5. check_package_proof_present does NOT trigger for COMPLETE-only verdicts.
6. check_package_proof_present passes when package-artifact-manifest.yaml is present.
7. check_package_proof_present error message names the matched keyword.

Sprint: FORMAT-FACTORY-R45-TWO-PRODUCT-LOCAL-RC-REPLAYABLE-001
"""
import io
import pathlib
import sys
import zipfile


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "evidence"))

from validate_evidence_bundle import check_package_proof_present  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_zf_with_manifest(has_manifest: bool = False):
    """Build a minimal in-memory zip optionally including package-artifact-manifest."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("repo/state/current-state.md", "# state\n")
        if has_manifest:
            zf.writestr("bundle-metadata/package-artifact-manifest.yaml",
                        "sprint_id: test\nPYTHON_BUILD_PROOF: PASS\n")
    buf.seek(0)
    return zipfile.ZipFile(buf, "r")


def _make_content(verdict_text):
    return {"final-verdict.md": verdict_text}


# ---------------------------------------------------------------------------
# Tests for verdict types that require package proof
# ---------------------------------------------------------------------------

class TestPackageProofPresentExtended:
    def test_poc_ready_without_proof_fails(self):
        """POC_READY verdict without package proof must fail (existing behavior)."""
        content = _make_content("**Verdict:** **R44_HIGH_THROUGHPUT_POC_READY**")
        zf = _make_zf_with_manifest(has_manifest=False)
        hits = check_package_proof_present(content, zf)
        assert len(hits) == 1
        assert "PACKAGE_PROOF_MISSING" in hits[0]

    def test_local_rc_without_proof_fails(self):
        """LOCAL_RC verdict without package proof must fail (R45 new rule)."""
        content = _make_content("**Verdict:** **R45_TWO_PRODUCT_LOCAL_RC_REPLAYABLE**")
        zf = _make_zf_with_manifest(has_manifest=False)
        hits = check_package_proof_present(content, zf)
        assert len(hits) == 1, f"Expected 1 hit, got: {hits}"
        assert "PACKAGE_PROOF_MISSING" in hits[0]
        assert "LOCAL_RC" in hits[0]

    def test_baseline_ready_without_proof_fails(self):
        """BASELINE_READY verdict without package proof must fail (R45 new rule)."""
        content = _make_content("**Verdict:** **R44_TWO_PRODUCT_LOCAL_RC_BASELINE_READY**")
        zf = _make_zf_with_manifest(has_manifest=False)
        hits = check_package_proof_present(content, zf)
        assert len(hits) == 1, f"Expected 1 hit, got: {hits}"
        assert "PACKAGE_PROOF_MISSING" in hits[0]

    def test_two_product_without_proof_fails(self):
        """TWO_PRODUCT verdict without package proof must fail (R45 new rule)."""
        content = _make_content("**Verdict:** **R45_TWO_PRODUCT_RC_COMPLETE**")
        zf = _make_zf_with_manifest(has_manifest=False)
        hits = check_package_proof_present(content, zf)
        assert len(hits) == 1, f"Expected 1 hit, got: {hits}"
        assert "PACKAGE_PROOF_MISSING" in hits[0]

    def test_release_candidate_without_proof_fails(self):
        """RELEASE_CANDIDATE verdict without package proof must fail (R45 new rule)."""
        content = _make_content("**Verdict:** **R45_RELEASE_CANDIDATE_ACCEPTED**")
        zf = _make_zf_with_manifest(has_manifest=False)
        hits = check_package_proof_present(content, zf)
        assert len(hits) == 1, f"Expected 1 hit, got: {hits}"
        assert "PACKAGE_PROOF_MISSING" in hits[0]

    def test_complete_only_verdict_does_not_require_proof(self):
        """A plain *_COMPLETE verdict without product materialization does NOT require proof."""
        content = _make_content("**Verdict:** **R45_SPRINT_COMPLETE**")
        zf = _make_zf_with_manifest(has_manifest=False)
        hits = check_package_proof_present(content, zf)
        assert len(hits) == 0, f"COMPLETE-only verdict should not require package proof. Got: {hits}"

    def test_local_rc_with_manifest_passes(self):
        """LOCAL_RC verdict WITH package-artifact-manifest.yaml must pass."""
        content = _make_content("**Verdict:** **R45_TWO_PRODUCT_LOCAL_RC_REPLAYABLE**")
        zf = _make_zf_with_manifest(has_manifest=True)
        hits = check_package_proof_present(content, zf)
        assert len(hits) == 0, f"Should pass when manifest present. Got: {hits}"

    def test_baseline_ready_with_manifest_passes(self):
        """BASELINE_READY verdict WITH package-artifact-manifest.yaml must pass."""
        content = _make_content("**Verdict:** **R44_TWO_PRODUCT_LOCAL_RC_BASELINE_READY**")
        zf = _make_zf_with_manifest(has_manifest=True)
        hits = check_package_proof_present(content, zf)
        assert len(hits) == 0, f"Should pass when manifest present. Got: {hits}"

    def test_no_verdict_returns_no_hits(self):
        """When no verdict file is present, check must return no hits."""
        content = {}  # no verdict file
        zf = _make_zf_with_manifest(has_manifest=False)
        hits = check_package_proof_present(content, zf)
        assert len(hits) == 0

    def test_error_message_names_matched_keyword(self):
        """Error message must name the matched keyword for diagnosis."""
        content = _make_content("**Verdict:** **R45_TWO_PRODUCT_LOCAL_RC_REPLAYABLE**")
        zf = _make_zf_with_manifest(has_manifest=False)
        hits = check_package_proof_present(content, zf)
        assert len(hits) == 1
        # Must name at least one of the keywords that matched
        keywords = ("LOCAL_RC", "TWO_PRODUCT")
        assert any(kw in hits[0] for kw in keywords), (
            f"Error message must name the matched keyword. Got: {hits[0]}"
        )
