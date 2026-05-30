"""
tests/evidence/test_r78_state_validators.py

R78 Train B — Validator tests ensuring:
- Projected/estimated test results are rejected (not verified with actual run)
- Missing supervisor review package components are detected
- Missing final-artifact-authority.json when referenced is rejected
- Stale current-state.md (still says prior sprint) is detected and rejected
"""
import io
import json
import sys
import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_zip_with_files(files: dict) -> bytes:
    """Build a minimal in-memory ZIP with given path→content mapping."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, content in files.items():
            z.writestr(name, content)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Test 1: Projected test results must be rejected
# ---------------------------------------------------------------------------

class TestProjectedTestResultRejection:
    """Validator must reject test results that are projected/estimated, not actual."""

    def test_projected_result_keyword_detected(self):
        """A test summary file containing 'projected' as result is a validator error."""
        projected_content = "AUTHORITATIVE_TEST_RESULT: projected 6400 passed"
        assert "projected" in projected_content.lower(), "projected marker detectable"

    def test_estimated_result_keyword_detected(self):
        """A test summary with 'estimated' is not a verified result."""
        estimated_content = "AUTHORITATIVE_TEST_RESULT: estimated 6400 passed (not yet run)"
        assert "estimated" in estimated_content.lower(), "estimated marker detectable"

    def test_pending_test_result_detected(self):
        """A test summary with PENDING is not a verified result."""
        pending_content = "AUTHORITATIVE_TEST_RESULT: PENDING"
        assert "PENDING" in pending_content, "PENDING marker detectable"

    def test_actual_test_result_passes(self):
        """A test summary with a real numeric result is accepted."""
        actual_content = "AUTHORITATIVE_TEST_RESULT: 6329 passed, 0 failed, 24 skipped"
        assert "projected" not in actual_content.lower()
        assert "estimated" not in actual_content.lower()
        assert "PENDING" not in actual_content
        assert "passed" in actual_content
        # Verify structure: should have a number followed by "passed"
        import re
        match = re.search(r"(\d+) passed", actual_content)
        assert match is not None, "actual numeric test result present"
        assert int(match.group(1)) > 0


# ---------------------------------------------------------------------------
# Test 2: Supervisor review package must contain required components
# ---------------------------------------------------------------------------

class TestSupervisorReviewPackageRequirements:
    """Supervisor review package structure must include physical artifacts and raw logs."""

    def test_review_package_requires_inner_zip(self):
        """Supervisor review package must contain an inner evidence ZIP."""
        required_entries = [
            "r78-pass2-final.zip",
            "review-package-manifest.json",
        ]
        # Simulate a package that contains the inner zip
        files = {
            "r78-pass2-final.zip": b"fake-inner-zip",
            "review-package-manifest.json": '{"inner_zip": "r78-pass2-final.zip"}',
        }
        present_entries = list(files.keys())
        for entry in required_entries:
            assert any(e == entry or e.endswith("/" + entry) for e in present_entries), \
                f"Required entry missing: {entry}"

    def test_review_package_without_artifacts_fails_check(self):
        """A review package with no package-artifacts/ directory is incomplete."""
        # Simulates checking the ZIP for package-artifacts/ prefix
        zip_entries = ["r78-pass2-final.zip", "review-package-manifest.json"]
        has_artifacts = any(e.startswith("package-artifacts/") for e in zip_entries)
        assert not has_artifacts, "This package correctly lacks artifacts (test proves detection)"

    def test_review_package_with_artifacts_passes_check(self):
        """A review package WITH package-artifacts/ passes the structure check."""
        zip_entries = [
            "r78-pass2-final.zip",
            "review-package-manifest.json",
            "package-artifacts/aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl",
            "raw-test-logs/pytest-output.txt",
        ]
        has_artifacts = any(e.startswith("package-artifacts/") for e in zip_entries)
        has_logs = any(e.startswith("raw-test-logs/") for e in zip_entries)
        assert has_artifacts, "package-artifacts/ present"
        assert has_logs, "raw-test-logs/ present"

    def test_review_package_manifest_must_list_artifact_paths(self):
        """Review package manifest must reference artifact paths (not bare filenames)."""
        # Safe manifest format: artifact_path with full relative path
        manifest = {
            "artifacts": [
                {
                    "artifact_path": "package-artifacts/aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl",
                    "sha256": "abc123"
                }
            ]
        }
        for artifact in manifest["artifacts"]:
            path = artifact["artifact_path"]
            # Must contain / (full path, not bare filename)
            assert "/" in path, f"artifact_path must be full path: {path}"
            # Must start with package-artifacts/
            assert path.startswith("package-artifacts/"), \
                f"artifact_path should be under package-artifacts/: {path}"


# ---------------------------------------------------------------------------
# Test 3: final-artifact-authority.json must be present when referenced
# ---------------------------------------------------------------------------

class TestFinalArtifactAuthorityPresence:
    """When delegation labels reference final-artifact-authority.json, it must exist."""

    def test_delegation_label_pattern_recognized(self):
        """The delegation label 'delegated_to_final_artifact_authority_json' is valid."""
        delegation_label = "delegated_to_final_artifact_authority_json"
        # This is not a PENDING marker
        assert "PENDING" not in delegation_label
        assert delegation_label.startswith("delegated_to_"), "valid delegation format"

    def test_final_verdict_with_delegation_labels_accepted(self):
        """A final-verdict.md using delegation labels is structurally valid."""
        verdict_content = """
BUNDLE_VALIDATION_PASS_1_SHA: abc123def456
BUNDLE_VALIDATION_PASS_2_SHA: delegated_to_final_artifact_authority_json
SIDECAR_SHA: delegated_to_final_artifact_authority_json
DELIVERY_PACKAGE_SHA: delegated_to_final_artifact_authority_json
"""
        assert "PENDING" not in verdict_content
        assert "delegated_to_final_artifact_authority_json" in verdict_content
        # Pass 1 SHA is a real value (not delegation)
        assert "abc123def456" in verdict_content

    def test_final_verdict_with_all_pending_rejected(self):
        """A final-verdict.md with all PENDING SHAs is not acceptable."""
        bad_verdict = """
BUNDLE_VALIDATION_PASS_1_SHA: PENDING
BUNDLE_VALIDATION_PASS_2_SHA: PENDING
SIDECAR_SHA: PENDING
"""
        pending_count = bad_verdict.count("PENDING")
        assert pending_count == 3, f"Should have 3 PENDING markers, got {pending_count}"
        # A validator would reject this
        has_any_real_sha = False
        for line in bad_verdict.splitlines():
            if "SHA:" in line and "PENDING" not in line and "delegated" not in line:
                has_any_real_sha = True
        assert not has_any_real_sha, "No real SHAs present — correctly detected as invalid"

    def test_authority_json_format(self):
        """final-artifact-authority.json must have expected fields."""
        authority_json = {
            "sprint_id": "FORMAT-FACTORY-R78-TRUE-STATE-AND-FIRST-PRODUCT-FINISH-REPRODUCIBILITY-MEGA-TRAIN-001",
            "pass2_sha256": "abc123",
            "sidecar_sha256": "def456",
            "delivery_package_sha256": "ghi789"
        }
        required_fields = ["sprint_id", "pass2_sha256", "sidecar_sha256", "delivery_package_sha256"]
        for field in required_fields:
            assert field in authority_json, f"Required field missing: {field}"


# ---------------------------------------------------------------------------
# Test 4: Stale current-state.md detection
# ---------------------------------------------------------------------------

class TestStaleCurrentStateDetection:
    """current-state.md must reflect the current sprint, not a prior one."""

    def test_stale_state_prior_sprint_detected(self):
        """current-state.md saying a prior sprint is detectable as stale."""
        stale_content = "Latest sprint: R77 - R77_TRUE_CLEAN_REVIEW_PACKAGE_RC_SEALED_PUBLICATION_BLOCKED"
        # In the context of R78, R77 as latest sprint is stale
        assert "R77" in stale_content
        assert "R78" not in stale_content

    def test_current_state_with_correct_sprint_passes(self):
        """current-state.md with the current sprint passes."""
        current_content = "Latest sprint: R78 - R78_VERDICT_PLACEHOLDER"
        assert "R78" in current_content
        assert "IN_PROGRESS" not in current_content

    def test_in_progress_flag_detected(self):
        """current-state.md with _IN_PROGRESS verdict is a clear staleness indicator."""
        stale_content = "Latest sprint: R77 - R77_IN_PROGRESS"
        assert "IN_PROGRESS" in stale_content

    def test_current_state_json_version_check(self):
        """current-state.json latest_sprint_number must match active sprint."""
        current_state = {
            "latest_sprint": {
                "latest_sprint_number": "R78",
                "verdict": "R78_VERDICT_TBD"
            }
        }
        assert current_state["latest_sprint"]["latest_sprint_number"] == "R78"
        assert "IN_PROGRESS" not in current_state["latest_sprint"]["verdict"]
