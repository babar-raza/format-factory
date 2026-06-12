"""
R52 validator hardening tests.

Lane 1B: Verdict parser code-block format (state_snapshot)
Lane 2A: Proof SHA consistency warning
Lane 2B: Validation-command-log finality (new stale patterns)
Lane 1C: State/verdict agreement with INV-003 false-blocker detection
"""
import io
import sys
import zipfile
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "evidence"))

from validate_evidence_bundle import (
    check_validation_command_log_freshness,
    check_proof_sha_consistency,
    check_state_verdict_agreement,
    _parse_verdict_from_text,
)


# ============================================================
# Lane 1B — Verdict parser: code-block format
# ============================================================

class TestVerdictParserCodeBlock:
    """R52: _parse_verdict_from_text must handle R51 ## Verdict + code-block format."""

    def test_code_block_format_parsed(self):
        text = "## Verdict\n\n`R51_INSTALLED_ARTIFACT_BASELINE_AND_AI_ACCELERATION_COMPLETE`\n"
        assert _parse_verdict_from_text(text) == "R51_INSTALLED_ARTIFACT_BASELINE_AND_AI_ACCELERATION_COMPLETE"

    def test_inline_verdict_still_parsed(self):
        assert _parse_verdict_from_text("**VERDICT: R50_COMPLETE**") == "R50_COMPLETE"

    def test_bold_verdict_still_parsed(self):
        assert _parse_verdict_from_text("**Verdict:** **R43_AUTHORITY_PROOF_COMPLETE**") == "R43_AUTHORITY_PROOF_COMPLETE"

    def test_no_verdict_returns_none(self):
        assert _parse_verdict_from_text("## Verdict\n\nsome prose") is None

    def test_code_block_with_extra_newlines(self):
        text = "## Verdict\n\n\n\n`R52_STATE_CONSISTENT_INSTALLED_ARTIFACT_BASELINE_CLEAN`\n"
        assert _parse_verdict_from_text(text) == "R52_STATE_CONSISTENT_INSTALLED_ARTIFACT_BASELINE_CLEAN"


# ============================================================
# Lane 2A — Proof SHA consistency
# ============================================================

class TestProofSHAConsistency:
    """R52: check_proof_sha_consistency warns when proof SHA != actual bundle SHA."""

    def _make_bundle_with_proof(self, proof_content):
        """Return a path to a temp ZIP containing the given proof content."""
        import tempfile
        tmp = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
        with zipfile.ZipFile(tmp, "w") as zf:
            zf.writestr("bundle-metadata/dummy.txt", "x")
        tmp.close()
        return tmp.name

    def test_no_sha_in_proof_no_warning(self, tmp_path):
        bundle_path = tmp_path / "test.zip"
        with zipfile.ZipFile(bundle_path, "w") as zf:
            zf.writestr("x", "y")
        meta = {"final-bundle-validation-proof.txt": "PASS result — no SHA claimed"}
        warnings = check_proof_sha_consistency(meta, bundle_path)
        assert warnings == []

    def test_matching_sha_no_warning(self, tmp_path):
        import hashlib
        bundle_path = tmp_path / "test.zip"
        with zipfile.ZipFile(bundle_path, "w") as zf:
            zf.writestr("x", "y")
        actual_sha = hashlib.sha256(bundle_path.read_bytes()).hexdigest()
        meta = {"final-bundle-validation-proof.txt": f"SHA-256: {actual_sha}"}
        warnings = check_proof_sha_consistency(meta, bundle_path)
        assert warnings == [], f"Expected no warnings for matching SHA, got: {warnings}"

    def test_mismatched_sha_warns(self, tmp_path):
        bundle_path = tmp_path / "test.zip"
        with zipfile.ZipFile(bundle_path, "w") as zf:
            zf.writestr("x", "y")
        stale_sha = "a" * 64
        meta = {"final-bundle-validation-proof.txt": f"SHA-256: {stale_sha}"}
        warnings = check_proof_sha_consistency(meta, bundle_path)
        assert len(warnings) == 1
        assert "PROOF_SHA_SIDECAR_RECOMMENDED" in warnings[0]
        assert stale_sha in warnings[0]

    def test_empty_proof_no_warning(self, tmp_path):
        bundle_path = tmp_path / "test.zip"
        with zipfile.ZipFile(bundle_path, "w") as zf:
            zf.writestr("x", "y")
        warnings = check_proof_sha_consistency({}, bundle_path)
        assert warnings == []


# ============================================================
# Lane 2B — Command log stale patterns
# ============================================================

class TestCommandLogStalePatternsR52:
    """R52: New stale patterns for validation-command-log freshness check."""

    def _check(self, content):
        meta = {"validation-command-log.txt": content}
        return check_validation_command_log_freshness(meta)

    def test_pass1_pending_caught(self):
        result = self._check("--- BUNDLE VALIDATION ---\nPass 1: PENDING\nPass 2: PENDING")
        assert len(result) == 1
        assert "COMMAND_LOG_STALE_RESULT" in result[0]

    def test_pass2_pending_caught(self):
        result = self._check("Some log content\nPass 2: PENDING\nmore content")
        assert len(result) == 1

    def test_to_be_completed_in_mt_caught(self):
        result = self._check("--- BUNDLE VALIDATION (to be completed in MT9) ---")
        assert len(result) == 1

    def test_to_be_completed_generic_caught(self):
        result = self._check("Validation to be completed")
        assert len(result) == 1

    def test_clean_log_passes(self):
        result = self._check(
            "BUNDLE_VALIDATION: PASS\nEntries: 2374\nAUTHORITATIVE_TEST_RESULT: 4140 passed"
        )
        assert result == []

    def test_no_final_verdict_still_caught(self):
        """Original pattern must still work."""
        result = self._check("STATE_SNAPSHOT: PASS (R49 no_final_verdict)")
        assert len(result) == 1


# ============================================================
# Lane 1C — State/verdict agreement + INV-003 false-blocker
# ============================================================

class TestStateVerdictAgreementR52:
    """R52: check_state_verdict_agreement handles code-block verdict and INV-003 false blockers."""

    def _make_zip_with_state(self, state_content, final_verdict_content=None):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("repo/state/current-state.md", state_content)
            if final_verdict_content:
                zf.writestr("repo/reports/r52/final-verdict.md", final_verdict_content)
        buf.seek(0)
        return zipfile.ZipFile(buf, "r")

    def test_code_block_verdict_with_stale_state_fails(self):
        state = "**Latest sprint:** R51 - unknown\n"
        meta = {"final-verdict.md": "## Verdict\n\n`R51_SOMETHING_COMPLETE`\n"}
        zf = self._make_zip_with_state(state)
        hits = check_state_verdict_agreement(meta, zf)
        assert any("STATE_VERDICT_MISMATCH" in h for h in hits)

    def test_inline_verdict_with_clean_state_passes(self):
        state = "**Latest sprint:** R51 - R51_COMPLETE\n"
        meta = {"final-verdict.md": "**VERDICT: R51_COMPLETE**"}
        zf = self._make_zip_with_state(state)
        hits = check_state_verdict_agreement(meta, zf)
        assert hits == []

    def test_inv003_false_blocker_detected(self):
        state = "**Latest sprint:** R52 - unknown\nINV-003: MISSING: reports/r52/final-verdict.md\n"
        meta = {}
        zf = self._make_zip_with_state(state, final_verdict_content="**VERDICT: R52_COMPLETE**")
        hits = check_state_verdict_agreement(meta, zf)
        assert any("STATE_FALSE_INV003_BLOCKER" in h for h in hits)

    def test_no_false_inv003_when_file_absent_in_bundle(self):
        state = "**Latest sprint:** R52 - unknown\nINV-003: MISSING: reports/r52/final-verdict.md\n"
        meta = {}
        zf = self._make_zip_with_state(state)  # no final-verdict in bundle
        hits = check_state_verdict_agreement(meta, zf)
        # Should not trigger INV-003 false-blocker since file genuinely absent
        assert not any("STATE_FALSE_INV003_BLOCKER" in h for h in hits)
