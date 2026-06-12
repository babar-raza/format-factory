"""
tests/evidence/test_r50_validator_hardening.py

R50 validator hardening tests.

Lane 1B: New proof-file placeholder patterns missed in R49.
  - "computed after pass 2 build", "pass 2 sha to follow",
    "entries: (computed", "size: (computed", "validation: (computed"
  - These are the exact strings present in the R49 stale bundle.

Lane 1C: check_artifact_inventory() parses lowercase YAML sha256: field.
  - R49 manifest uses "sha256: <hash>" (lowercase YAML), not "SHA-256: <hash>".
  - Without the fix the validator silently skips SHA validation for YAML manifests.

Sprint: FORMAT-FACTORY-R50-EVIDENCE-CLOSEOUT-REPAIR-AND-OBJECT-MODEL-HARDENING-001
"""

import hashlib
import io
import sys
import zipfile
from pathlib import Path


# ---------------------------------------------------------------------------
# Import the validator functions
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "evidence"))

from validate_evidence_bundle import (
    check_artifact_inventory,
    check_proof_file_finality,
    check_validation_command_log_freshness,
)


# ---------------------------------------------------------------------------
# Lane 1B: New placeholder patterns that R49 missed
# ---------------------------------------------------------------------------

class TestR50ProofFilePlaceholderPatterns:
    """R50 Lane 1B: Stale 'computed after pass 2 build' family of patterns."""

    def test_computed_after_pass2_build_triggers(self):
        """'computed after pass 2 build' triggers placeholder error."""
        content = {
            "final-bundle-validation-proof.txt": (
                "SHA-256: (computed after pass 2 build)\n"
                "Entries: (computed after pass 2 build)\n"
            )
        }
        hits = check_proof_file_finality(content)
        assert len(hits) == 1
        assert "PROOF_FILE_PLACEHOLDER" in hits[0]

    def test_entries_computed_triggers(self):
        """'entries: (computed' triggers placeholder error."""
        content = {
            "final-bundle-validation-proof.txt": (
                "Bundle: .local/evidence-bundles/r49-bundle.zip\n"
                "entries: (computed after pass 2 build)\n"
            )
        }
        hits = check_proof_file_finality(content)
        assert len(hits) == 1

    def test_size_computed_triggers(self):
        """'size: (computed' triggers placeholder error."""
        content = {
            "final-bundle-validation-proof.txt": (
                "size: (computed after pass 2 build)\n"
            )
        }
        hits = check_proof_file_finality(content)
        assert len(hits) == 1

    def test_validation_computed_triggers(self):
        """'validation: (computed' triggers placeholder error."""
        content = {
            "final-bundle-validation-proof.txt": (
                "validation: (computed after pass 2 build)\n"
            )
        }
        hits = check_proof_file_finality(content)
        assert len(hits) == 1

    def test_pass2_sha_to_follow_triggers(self):
        """'pass 2 sha to follow' triggers placeholder error."""
        content = {
            "final-bundle-validation-proof.txt": (
                "BUNDLE_VALIDATION: PASS (final verdict updated; pass 2 sha to follow)\n"
            )
        }
        hits = check_proof_file_finality(content)
        assert len(hits) == 1

    def test_r49_exact_stale_proof_content_triggers(self):
        """The exact stale text found in the R49 bundle triggers the guard."""
        r49_stale = (
            "Bundle path: .local/evidence-bundles/r49-bundle.zip\n"
            "SHA-256: (computed after pass 2 build)\n"
            "Entries: (computed after pass 2 build)\n"
            "Size: (computed after pass 2 build)\n"
            "Validation: (computed after pass 2 build)\n"
            "BUNDLE_VALIDATION: PASS (final verdict updated; pass 2 sha to follow)\n"
        )
        content = {"final-bundle-validation-proof.txt": r49_stale}
        hits = check_proof_file_finality(content)
        assert len(hits) == 1, f"Stale R49 proof should be caught; got: {hits}"

    def test_finalized_proof_still_passes(self):
        """A properly finalized proof file still passes all checks."""
        finalized = (
            "Bundle: .local/evidence-bundles/r50-bundle.zip\n"
            "SHA-256: a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2\n"
            "Entries: 2400\n"
            "Size: 4500000 bytes\n"
            "Metadata files: 38\n"
            "BUNDLE_VALIDATION: PASS\n"
        )
        content = {"final-bundle-validation-proof.txt": finalized}
        hits = check_proof_file_finality(content)
        assert hits == [], f"Finalized proof should pass; got: {hits}"


# ---------------------------------------------------------------------------
# Lane 1C: check_artifact_inventory parses lowercase YAML sha256:
# ---------------------------------------------------------------------------

def _make_test_bundle(manifest_content: str, artifacts: dict) -> "zipfile.ZipFile":
    """Create an in-memory ZIP suitable for passing to check_artifact_inventory.

    manifest_content: text for bundle-metadata/package-artifact-manifest.yaml
    artifacts: dict mapping filename -> bytes content
                Files are added under bundle-metadata/package-artifacts/
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_STORED) as zf:
        zf.writestr("bundle-metadata/package-artifact-manifest.yaml", manifest_content)
        for name, content in artifacts.items():
            zf.writestr(f"bundle-metadata/package-artifacts/{name}", content)
    buf.seek(0)
    return zipfile.ZipFile(buf, mode="r")


class TestArtifactInventoryYamlParsing:
    """R50 Lane 1C: check_artifact_inventory parses lowercase YAML sha256: fields."""

    def test_yaml_sha256_correct_hash_passes(self):
        """YAML manifest with correct sha256: value passes."""
        artifact_bytes = b"fake wheel content for r50 test"
        expected_sha = hashlib.sha256(artifact_bytes).hexdigest()
        manifest = (
            "sprint: FORMAT-FACTORY-R50-TEST\n"
            "artifacts:\n"
            "  - file: test_package-0.1.0-py3-none-any.whl\n"
            "    format: test\n"
            f"    sha256: {expected_sha}\n"
            "    publication_authorized: false\n"
        )
        zf = _make_test_bundle(manifest, {"test_package-0.1.0-py3-none-any.whl": artifact_bytes})
        errors = check_artifact_inventory(zf)
        zf.close()
        assert errors == [], f"Correct YAML sha256 should pass; got: {errors}"

    def test_yaml_sha256_wrong_hash_fails(self):
        """YAML manifest with wrong sha256: value triggers ARTIFACT_SHA_MISMATCH."""
        artifact_bytes = b"real wheel bytes"
        wrong_sha = "a" * 64  # clearly wrong
        manifest = (
            "sprint: FORMAT-FACTORY-R50-TEST\n"
            "artifacts:\n"
            "  - file: bad_hash-0.1.0-py3-none-any.whl\n"
            "    format: test\n"
            f"    sha256: {wrong_sha}\n"
            "    publication_authorized: false\n"
        )
        zf = _make_test_bundle(manifest, {"bad_hash-0.1.0-py3-none-any.whl": artifact_bytes})
        errors = check_artifact_inventory(zf)
        zf.close()
        assert len(errors) == 1
        assert "ARTIFACT_SHA_MISMATCH" in errors[0]
        assert wrong_sha in errors[0]

    def test_yaml_sha256_missing_artifact_fails(self):
        """YAML manifest claiming an artifact not in the ZIP triggers ARTIFACT_INVENTORY error."""
        manifest = (
            "sprint: FORMAT-FACTORY-R50-TEST\n"
            "artifacts:\n"
            "  - file: missing-0.1.0-py3-none-any.whl\n"
            "    format: test\n"
            "    sha256: " + ("b" * 64) + "\n"
            "    publication_authorized: false\n"
        )
        zf = _make_test_bundle(manifest, {})  # artifact not added
        errors = check_artifact_inventory(zf)
        zf.close()
        assert len(errors) == 1
        assert "ARTIFACT_INVENTORY" in errors[0]
        assert "missing-0.1.0-py3-none-any.whl" in errors[0]

    def test_yaml_multi_artifact_one_wrong_hash(self):
        """Multi-artifact YAML manifest: only the artifact with wrong hash fails."""
        good_bytes = b"good artifact content"
        good_sha = hashlib.sha256(good_bytes).hexdigest()
        bad_bytes = b"bad artifact content"
        wrong_sha = "c" * 64

        manifest = (
            "sprint: FORMAT-FACTORY-R50-TEST\n"
            "artifacts:\n"
            "  - file: good_pkg-0.1.0-py3-none-any.whl\n"
            f"    sha256: {good_sha}\n"
            "  - file: bad_pkg-0.1.0-py3-none-any.whl\n"
            f"    sha256: {wrong_sha}\n"
        )
        zf = _make_test_bundle(
            manifest,
            {
                "good_pkg-0.1.0-py3-none-any.whl": good_bytes,
                "bad_pkg-0.1.0-py3-none-any.whl": bad_bytes,
            }
        )
        errors = check_artifact_inventory(zf)
        zf.close()
        # Only the bad one fails
        assert len(errors) == 1
        assert "bad_pkg" in errors[0]
        assert "ARTIFACT_SHA_MISMATCH" in errors[0]

    def test_yaml_nupkg_sha256_correct_passes(self):
        """YAML manifest for .nupkg artifact with correct sha256: passes."""
        nupkg_bytes = b"NuGet package fake content"
        expected_sha = hashlib.sha256(nupkg_bytes).hexdigest()
        manifest = (
            "artifacts:\n"
            "  - file: FormatFactory.Fods.0.1.0-tier0.nupkg\n"
            "    format: fods\n"
            "    track: dotnet-commercial\n"
            f"    sha256: {expected_sha}\n"
            "    publication_authorized: false\n"
        )
        zf = _make_test_bundle(
            manifest,
            {"FormatFactory.Fods.0.1.0-tier0.nupkg": nupkg_bytes}
        )
        errors = check_artifact_inventory(zf)
        zf.close()
        assert errors == [], f"Correct nupkg sha256 should pass; got: {errors}"

    def test_uppercase_sha_still_works(self):
        """Legacy uppercase SHA-256: format still parses correctly (no regression)."""
        artifact_bytes = b"old style artifact"
        expected_sha = hashlib.sha256(artifact_bytes).hexdigest()
        # Use legacy text format (not YAML)
        manifest = (
            "Package artifacts for R46 bundle:\n"
            "  - aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl\n"
            f"  SHA-256: {expected_sha}\n"
        )
        zf = _make_test_bundle(
            manifest,
            {"aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl": artifact_bytes}
        )
        errors = check_artifact_inventory(zf)
        zf.close()
        assert errors == [], f"Uppercase SHA-256 format should still work; got: {errors}"


# ---------------------------------------------------------------------------
# Lane 1D: check_validation_command_log_freshness
# ---------------------------------------------------------------------------

class TestCommandLogFreshness:
    """R50 Lane 1D: check_validation_command_log_freshness detects pre-final snapshot tokens."""

    def test_no_final_verdict_token_triggers(self):
        """'no_final_verdict' in validation command log triggers stale result error."""
        content = {
            "validation-command-log.txt": (
                "8. State snapshot:\n"
                "   python tools/state/state_snapshot.py\n"
                "   Result: STATE_SNAPSHOT: PASS (R49 no_final_verdict)\n"
            )
        }
        hits = check_validation_command_log_freshness(content)
        assert len(hits) == 1
        assert "COMMAND_LOG_STALE_RESULT" in hits[0]

    def test_r49_exact_stale_command_log_triggers(self):
        """The exact stale state snapshot line from R49's command log triggers the guard."""
        content = {
            "validation-command-log.txt": (
                "R49 Validation Command Log\n"
                "===========================\n"
                "8. State snapshot:\n"
                "   python tools/state/state_snapshot.py\n"
                "   Result: STATE_SNAPSHOT: PASS (R49 no_final_verdict)\n"
            )
        }
        hits = check_validation_command_log_freshness(content)
        assert len(hits) == 1, f"R49 stale snapshot line should be caught; got: {hits}"

    def test_final_command_log_passes(self):
        """Command log with post-verdict state snapshot token passes."""
        content = {
            "validation-command-log.txt": (
                "8. State snapshot:\n"
                "   python tools/state/state_snapshot.py\n"
                "   Result: STATE_SNAPSHOT: PASS (R50 sprint_closed)\n"
            )
        }
        hits = check_validation_command_log_freshness(content)
        assert hits == [], f"Post-verdict snapshot should pass; got: {hits}"

    def test_absent_command_log_returns_empty(self):
        """Missing command log file returns empty list (not flagged here)."""
        hits = check_validation_command_log_freshness({})
        assert hits == []

    def test_clean_command_log_no_false_positive(self):
        """Command log with no stale tokens passes cleanly."""
        content = {
            "validation-command-log.txt": (
                "1. Python FODS tests: 383 passed, 4 skipped\n"
                "2. Full suite: 1305 passed, 4 skipped, 2 pre-existing fail\n"
                "8. State snapshot: STATE_SNAPSHOT: PASS (R50 sprint_closed_verified)\n"
            )
        }
        hits = check_validation_command_log_freshness(content)
        assert hits == []
