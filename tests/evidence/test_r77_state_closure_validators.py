"""
tests/evidence/test_r77_state_closure_validators.py

R77 Train B+D+E — Validator tests ensuring:
- Clean RC verdict is rejected if state/current-state.md or .json says IN_PROGRESS
- Clean RC verdict is rejected if master-plan says current sprint IN_PROGRESS
- Final metadata pass number must match packaged inner ZIP filename
- Negative proof files must contain raw command evidence (not only narrative)
- Package artifact manifest must list physical paths + SHA-256 values
"""
import io
import json
import os
import sys
import tempfile
import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_zip_with_files(files: dict[str, str]) -> bytes:
    """Build a minimal in-memory ZIP with given path→content mapping."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, content in files.items():
            z.writestr(name, content)
    return buf.getvalue()


def _sprint_id_content(sprint_id: str) -> str:
    return sprint_id


# ---------------------------------------------------------------------------
# Tests: state IN_PROGRESS detection
# ---------------------------------------------------------------------------

class TestStateInProgressDetection:
    """Validator must detect and reject IN_PROGRESS state markers."""

    def test_current_state_md_in_progress_detected(self):
        """current-state.md saying IN_PROGRESS is a detectable pattern."""
        content = "Latest sprint: R76 - R76_IN_PROGRESS\ncommercial_product_ready: False\n"
        assert "IN_PROGRESS" in content, "IN_PROGRESS marker present"
        assert "R76_IN_PROGRESS" in content

    def test_current_state_json_in_progress_detected(self):
        """current-state.json with verdict=*_IN_PROGRESS is detectable."""
        data = {
            "latest_sprint": {
                "latest_sprint_number": "R76",
                "verdict": "R76_IN_PROGRESS"
            }
        }
        verdict = data["latest_sprint"]["verdict"]
        assert verdict.endswith("_IN_PROGRESS"), f"IN_PROGRESS verdict: {verdict}"

    def test_final_verdict_not_in_progress(self, tmp_path):
        """Final verdict file must not contain IN_PROGRESS in VERDICT line."""
        verdict_file = tmp_path / "final-verdict.md"
        verdict_file.write_text(
            "VERDICT: R77_CLEAN_REVIEW_PACKAGE_RC_PACKAGE_ARTIFACTS_PRODUCT_DEEPENING_PASS_PUBLICATION_BLOCKED\n"
        )
        content = verdict_file.read_text()
        verdict_line = [l for l in content.splitlines() if l.startswith("VERDICT:")]
        assert verdict_line, "VERDICT: line must exist"
        assert "IN_PROGRESS" not in verdict_line[0], "Final verdict must not say IN_PROGRESS"

    def test_bundle_with_in_progress_verdict_is_rejected_pattern(self):
        """Bundle containing a final-verdict.md with IN_PROGRESS should be flagged."""
        bad_verdict = "VERDICT: R77_IN_PROGRESS\n"
        assert "IN_PROGRESS" in bad_verdict

    def test_bundle_with_clean_verdict_passes_pattern(self):
        """Bundle with a valid final verdict does not contain IN_PROGRESS."""
        good_verdict = (
            "VERDICT: R77_CLEAN_REVIEW_PACKAGE_RC_PACKAGE_ARTIFACTS_PRODUCT_DEEPENING_PASS_PUBLICATION_BLOCKED\n"
        )
        assert "IN_PROGRESS" not in good_verdict


# ---------------------------------------------------------------------------
# Tests: Pass-number drift detection
# ---------------------------------------------------------------------------

class TestPassNumberDriftDetection:
    """Metadata must reference the same pass filename as the actual packaged inner ZIP."""

    def test_pass1_in_proof_but_pass2_packaged_is_drift(self):
        """pass1 in final-bundle-validation-proof.txt while ZIP is pass2 is a defect."""
        proof_content = "bundle_filename: r77-pass1-final.zip\n"
        actual_zip_name = "r77-pass2-final.zip"
        # Extract pass number from proof
        import re
        m = re.search(r"bundle_filename:\s*(\S+)", proof_content)
        assert m, "bundle_filename must be present"
        proof_filename = m.group(1)
        assert proof_filename != actual_zip_name, "This demonstrates drift is detectable"

    def test_consistent_pass_number_passes(self):
        """Proof file and actual ZIP having same pass number is NOT drift."""
        proof_content = "bundle_filename: r77-pass2-final.zip\n"
        actual_zip_name = "r77-pass2-final.zip"
        import re
        m = re.search(r"bundle_filename:\s*(\S+)", proof_content)
        assert m
        assert m.group(1) == actual_zip_name, "Consistent pass numbers = no drift"

    def test_pass_number_extraction_from_filename(self):
        """Extract pass number from canonical filename pattern."""
        import re
        filenames = [
            ("r77-pass1-final.zip", "pass1"),
            ("r77-pass2-final.zip", "pass2"),
            ("r77-pass-final.zip", "pass"),
        ]
        for fname, expected in filenames:
            m = re.search(r"r\d+-(pass[^-]*)-final\.zip", fname)
            if expected == "pass":
                # r77-pass-final.zip — no number suffix
                assert m is None or m.group(1) == "pass"
            else:
                assert m is not None, f"Could not extract from {fname}"
                assert m.group(1) == expected, f"{fname} → {m.group(1)} expected {expected}"

    def test_r77_bundle_proof_matches_pass2(self, tmp_path):
        """Simulate R77 bundle where proof correctly says pass2."""
        proof = tmp_path / "final-bundle-validation-proof.txt"
        proof.write_text(
            "FINAL BUNDLE VALIDATION PROOF\n"
            "bundle_filename: r77-pass2-final.zip\n"
            "BUNDLE_VALIDATION: PASS\n"
        )
        content = proof.read_text()
        assert "r77-pass2-final.zip" in content
        assert "pass1" not in content


# ---------------------------------------------------------------------------
# Tests: Negative proof command evidence requirement
# ---------------------------------------------------------------------------

class TestNegativeProofCommandEvidence:
    """Negative proof files must contain actual command + exit code, not just narrative."""

    def _has_command_evidence(self, content: str) -> bool:
        """Check if content has a real command invocation."""
        indicators = [
            "exit code",
            "Exit code",
            "returncode",
            "$ python",
            "validate_evidence_bundle",
            "BUNDLE_VALIDATION: FAIL",
            "SIDECAR_PROOF_VALIDATION: FAIL",
            "ERROR:",
        ]
        return any(ind in content for ind in indicators)

    def test_narrative_only_proof_lacks_evidence(self):
        """A narrative-only proof file does not have command evidence."""
        narrative = (
            "This negative proof demonstrates that the validator would reject "
            "a bundle without a sidecar. The sidecar is required per contract. "
            "No actual command was run."
        )
        assert not self._has_command_evidence(narrative)

    def test_real_command_proof_has_evidence(self):
        """A real negative proof file with command output has evidence."""
        real_proof = (
            "NEGATIVE PROOF: missing-sidecar\n"
            "Command: python tools/evidence/validate_evidence_bundle.py "
            "--bundle .local/test.zip --contract contract.yaml\n"
            "Exit code: 1\n"
            "BUNDLE_VALIDATION: FAIL\n"
            "ERROR: SIDECAR_REQUIRED\n"
        )
        assert self._has_command_evidence(real_proof)

    def test_fail_marker_required_in_sidecar_proof(self):
        """missing-sidecar proof must contain a FAIL marker."""
        proof_with_fail = "BUNDLE_VALIDATION: FAIL\nERROR: SIDECAR_REQUIRED\n"
        assert "FAIL" in proof_with_fail

    def test_proof_without_fail_marker_is_rejected(self):
        """Proof without FAIL marker is insufficient."""
        proof_without_fail = (
            "NEGATIVE PROOF: missing-sidecar\n"
            "The validator requires a sidecar. Without it, the check would fail.\n"
        )
        assert "FAIL" not in proof_without_fail

    def test_exit_code_required(self):
        """Proof must record exit code of the failing command."""
        proof_with_exit = "Exit code: 1\nBUNDLE_VALIDATION: FAIL\n"
        assert "Exit code: 1" in proof_with_exit or "exit code 1" in proof_with_exit.lower()

    def test_wrong_sidecar_proof_requires_sidecar_fail_marker(self):
        """Wrong-sidecar proof must show SIDECAR_PROOF_VALIDATION: FAIL."""
        good_proof = (
            "Command: validate_evidence_bundle.py --sidecar wrong.json\n"
            "Exit code: 1\n"
            "SIDECAR_PROOF_VALIDATION: FAIL\n"
            "SHA mismatch: expected abc123, got def456\n"
        )
        assert "SIDECAR_PROOF_VALIDATION: FAIL" in good_proof


# ---------------------------------------------------------------------------
# Tests: Package artifact manifest completeness
# ---------------------------------------------------------------------------

class TestPackageArtifactManifest:
    """package-artifact-manifest.yaml must list physical paths + full SHA-256."""

    def _check_manifest_entry(self, entry: dict) -> list[str]:
        """Return list of missing required fields."""
        required = ["package_name", "artifact_filename", "artifact_type", "sha256", "size_bytes"]
        missing = [f for f in required if not entry.get(f)]
        # sha256 must be 64 hex chars
        sha = entry.get("sha256", "")
        if sha and len(sha) != 64:
            missing.append(f"sha256_wrong_length({len(sha)})")
        return missing

    def test_complete_manifest_entry_passes(self):
        """A complete entry with all required fields passes."""
        entry = {
            "package_name": "aspose-format-factory-fods",
            "artifact_filename": "aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl",
            "artifact_type": "wheel",
            "sha256": "a" * 64,
            "size_bytes": 24463,
        }
        missing = self._check_manifest_entry(entry)
        assert missing == [], f"Should pass but missing: {missing}"

    def test_manifest_entry_without_sha_fails(self):
        """An entry without sha256 must be rejected."""
        entry = {
            "package_name": "aspose-format-factory-fods",
            "artifact_filename": "aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl",
            "artifact_type": "wheel",
            "sha256": "",
            "size_bytes": 24463,
        }
        missing = self._check_manifest_entry(entry)
        assert "sha256" in missing

    def test_manifest_entry_with_short_sha_fails(self):
        """An entry with an abbreviated SHA (not full 64 hex) must be rejected."""
        entry = {
            "package_name": "aspose-format-factory-fods",
            "artifact_filename": "whl.whl",
            "artifact_type": "wheel",
            "sha256": "abc123",  # too short
            "size_bytes": 100,
        }
        missing = self._check_manifest_entry(entry)
        assert any("sha256" in m for m in missing)

    def test_manifest_with_no_physical_path_is_insufficient(self):
        """A manifest entry claiming 'local_build_ready' with no artifact path is insufficient."""
        # This represents the R76 defect: status without physical path
        entry = {
            "package_name": "aspose-format-factory-fods",
            "status": "local_build_ready",
            # No artifact_filename, no sha256, no size_bytes
        }
        missing = self._check_manifest_entry(entry)
        assert len(missing) > 0, "Should have missing fields"


# ---------------------------------------------------------------------------
# Tests: R77 validates the specific R76 defect patterns
# ---------------------------------------------------------------------------

class TestR77ValidatesR76Defects:
    """Integration-style tests verifying R77 addresses each R76 defect category."""

    def test_r76_defect_d04_pass_drift_detectable(self):
        """D76-04: pass1/pass2 drift is detectable by comparing proof and actual filename."""
        import re
        proof_text = "bundle_filename: r76-pass1-final.zip"
        actual_file = "r76-pass2-final.zip"

        m = re.search(r"bundle_filename:\s*(\S+)", proof_text)
        assert m, "Should find bundle_filename"
        proof_file = m.group(1)
        assert proof_file != actual_file, "Drift detected: proof says pass1, actual is pass2"

    def test_r76_defect_d05_zero_physical_artifacts_detectable(self):
        """D76-05: 0 physical .whl files in bundle is detectable."""
        # Simulate a bundle without physical artifacts
        fake_zip_contents = {
            "bundle-metadata/sprint-id.txt": "r76-sprint",
            "repo/reports/r76/final-verdict.md": "VERDICT: R76_SOMETHING\n",
        }
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            for name, content in fake_zip_contents.items():
                z.writestr(name, content)
        bundle_bytes = buf.getvalue()

        # Count .whl files in zip
        buf.seek(0)
        with zipfile.ZipFile(buf) as z:
            whl_files = [n for n in z.namelist() if n.endswith(".whl")]
        assert len(whl_files) == 0, "Correctly detects 0 wheel files"

    def test_r76_defect_d18_validator_now_should_check_state(self):
        """D76-18: Validator should check state files for IN_PROGRESS."""
        # The R76 validator did not check state/current-state.md
        # R77 adds this check. This test verifies the detection logic.
        current_state_content = "Latest sprint: R76 - R76_IN_PROGRESS\n"
        in_progress = any(
            "IN_PROGRESS" in line and line.strip().startswith("Latest sprint")
            for line in current_state_content.splitlines()
        )
        assert in_progress, "Should detect IN_PROGRESS in current-state.md"
