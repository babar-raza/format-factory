#!/usr/bin/env python3
"""
Tests for final bundle closure rules.

Validates that the evidence bundle validator correctly rejects bundles that
violate final closure requirements:

1. Dirty git status (git-status-final.txt shows uncommitted changes) always FAIL
   unless emergency_blocker_bundle: true
2. emergency_blocker_bundle: true must NOT appear in final closure contracts
3. require_clean_git: false does NOT bypass dirty-git check
4. Stale IN_PROGRESS gate status causes --check-no-pending FAIL
5. Missing AUTHORITATIVE_TEST_RESULT causes --check-no-pending FAIL
6. PENDING bundle validation marker in metadata causes --check-no-pending FAIL
7. Closure contradiction (proof=PASS, verdict=FAIL) causes FAIL with --check-no-pending

These rules prevent R23-class defects from recurring in future sprints.

Run from repo root:
    PYTHONPATH=/c/Users/prora/AppData/Roaming/Python/Python313/site-packages:. \\
      python -m pytest tests/evidence/test_final_bundle_closure_rules.py -v

Exits 0 if all tests PASS, 1 if any test FAILS.
"""

import sys
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "evidence"))

from validate_evidence_bundle import validate_bundle  # noqa: E402

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_contract(tmp: Path, **overrides) -> Path:
    """Write a minimal valid contract YAML with optional overrides."""
    defaults = {
        "contract_id": "test-closure-rules",
        "require_clean_git": "false",
        "emergency_blocker_bundle": "false",
        "min_metadata_count": "30",
        "required_repo_files": "[]",
    }
    defaults.update(overrides)
    # Build YAML
    lines = [f"contract_id: {defaults['contract_id']}"]
    lines.append(f"require_clean_git: {defaults['require_clean_git']}")
    lines.append(f"emergency_blocker_bundle: {defaults['emergency_blocker_bundle']}")
    lines.append(f"min_metadata_count: {defaults['min_metadata_count']}")
    lines.append("required_repo_files: []")
    contract = tmp / "test-contract.yaml"
    contract.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return contract


def _make_bundle(tmp: Path, git_status: str = None, metadata_files: dict = None,
                 num_meta: int = 35) -> Path:
    """Build a minimal valid bundle zip.

    Args:
        git_status: Content of git-status-final.txt. None = omit the file.
        metadata_files: Additional metadata files {name: content}.
        num_meta: Total count of metadata files to generate (padded with empty ones).
    """
    bundle = tmp / "test-bundle.zip"
    all_meta = {}
    if git_status is not None:
        all_meta["git-status-final.txt"] = git_status
    if metadata_files:
        all_meta.update(metadata_files)
    # Pad to num_meta
    for i in range(num_meta - len(all_meta)):
        all_meta[f"metadata-pad-{i:03d}.md"] = f"# Pad {i}\nSprint: test\n"

    with zipfile.ZipFile(bundle, "w") as zf:
        zf.writestr("repo/dummy.txt", "placeholder repo file\n")
        for name, content in all_meta.items():
            zf.writestr(f"bundle-metadata/{name}", content)
    return bundle


_CLEAN_STATUS = (
    "On branch main\n"
    "Your branch is ahead of 'origin/main' by 246 commits.\n\n"
    "nothing to commit, working tree clean\n"
)

_DIRTY_STATUS = (
    "On branch main\n"
    "Your branch is ahead of 'origin/main' by 245 commits.\n\n"
    "Changes not staged for commit:\n"
    "\tmodified:   reports/memory/r19-memory-capture-20260517/git-status-final.txt\n\n"
    "no changes added to commit\n"
)

_UNTRACKED_STATUS = (
    "On branch main\n\n"
    "Untracked files:\n"
    "\treports/governance/r23-closure-*.md\n\n"
    "nothing added to commit but untracked files present\n"
)


# ---------------------------------------------------------------------------
# Rule 1: Dirty git-status always FAIL without emergency_blocker
# ---------------------------------------------------------------------------

class TestDirtyGitStatusFails:

    def test_dirty_changes_not_staged_fails(self, tmp_path):
        contract = _make_contract(tmp_path)
        bundle = _make_bundle(tmp_path, git_status=_DIRTY_STATUS)
        result = validate_bundle(str(contract), str(bundle))
        assert result is False, "Dirty git status should cause FAIL"

    def test_untracked_files_fails(self, tmp_path):
        contract = _make_contract(tmp_path)
        bundle = _make_bundle(tmp_path, git_status=_UNTRACKED_STATUS)
        result = validate_bundle(str(contract), str(bundle))
        assert result is False, "Untracked files in git status should cause FAIL"

    def test_require_clean_git_false_does_not_bypass_dirty_check(self, tmp_path):
        """require_clean_git: false only suppresses 'no git status file found' warning.
        It does NOT bypass the check when git-status-final.txt is present and dirty.
        This is the key invariant violated in the R23 pre-commit emergency bundle."""
        contract = _make_contract(tmp_path, require_clean_git="false")
        bundle = _make_bundle(tmp_path, git_status=_DIRTY_STATUS)
        result = validate_bundle(str(contract), str(bundle))
        assert result is False, (
            "require_clean_git: false must NOT bypass dirty-git check "
            "when git-status-final.txt is present and dirty"
        )

    def test_clean_status_passes(self, tmp_path):
        contract = _make_contract(tmp_path)
        bundle = _make_bundle(tmp_path, git_status=_CLEAN_STATUS)
        result = validate_bundle(str(contract), str(bundle))
        assert result is True, "Clean git status should PASS"

    def test_no_git_status_file_with_require_false_passes(self, tmp_path):
        """When require_clean_git: false and no git status file, result should PASS
        (file missing is a warning, not an error)."""
        contract = _make_contract(tmp_path, require_clean_git="false")
        bundle = _make_bundle(tmp_path, git_status=None)
        result = validate_bundle(str(contract), str(bundle))
        assert result is True, "Missing git status file with require_clean_git: false should PASS"


# ---------------------------------------------------------------------------
# Rule 2: emergency_blocker_bundle=true allows dirty git (but is not for final closure)
# ---------------------------------------------------------------------------

class TestEmergencyBlockerBundle:

    def test_emergency_blocker_allows_dirty_git(self, tmp_path):
        """emergency_blocker_bundle: true allows dirty git (for emergency/blocked sprints).
        This MUST NOT be used for final closure contracts."""
        contract = _make_contract(tmp_path, emergency_blocker_bundle="true")
        bundle = _make_bundle(tmp_path, git_status=_DIRTY_STATUS)
        result = validate_bundle(str(contract), str(bundle))
        # emergency_blocker downgrades dirty git to a warning, so result is PASS
        assert result is True, "emergency_blocker_bundle: true should allow dirty git"

    def test_non_emergency_clean_passes(self, tmp_path):
        contract = _make_contract(tmp_path, emergency_blocker_bundle="false")
        bundle = _make_bundle(tmp_path, git_status=_CLEAN_STATUS)
        result = validate_bundle(str(contract), str(bundle))
        assert result is True


# ---------------------------------------------------------------------------
# Rule 3: Stale IN_PROGRESS status with --check-no-pending
# ---------------------------------------------------------------------------

class TestInProgressStaleStatus:

    def test_in_progress_marker_fails_with_check_pending(self, tmp_path):
        """Final bundles must not contain | IN_PROGRESS | table markers."""
        stale_metadata = {
            "sprint-overview.md": (
                "# Sprint R99\n"
                "| Gate 5 | Sample corpus | IN_PROGRESS |\n"
            )
        }
        contract = _make_contract(tmp_path)
        bundle = _make_bundle(tmp_path, git_status=_CLEAN_STATUS, metadata_files=stale_metadata)
        result = validate_bundle(str(contract), str(bundle), no_pending=True)
        assert result is False, "| IN_PROGRESS | in metadata should FAIL with --check-no-pending"

    def test_in_progress_marker_passes_without_check_pending(self, tmp_path):
        """Without --check-no-pending, IN_PROGRESS does not block."""
        stale_metadata = {
            "sprint-overview.md": (
                "# Sprint R99\n"
                "| Gate 5 | Sample corpus | IN_PROGRESS |\n"
            )
        }
        contract = _make_contract(tmp_path)
        bundle = _make_bundle(tmp_path, git_status=_CLEAN_STATUS, metadata_files=stale_metadata)
        result = validate_bundle(str(contract), str(bundle), no_pending=False)
        assert result is True


# ---------------------------------------------------------------------------
# Rule 4: Missing AUTHORITATIVE_TEST_RESULT with --check-no-pending
# ---------------------------------------------------------------------------

class TestAuthoritativeTestResult:

    def test_missing_authoritative_test_result_fails(self, tmp_path):
        """P-EVID-003: must have AUTHORITATIVE_TEST_RESULT in at least one metadata file."""
        contract = _make_contract(tmp_path)
        bundle = _make_bundle(tmp_path, git_status=_CLEAN_STATUS)
        result = validate_bundle(str(contract), str(bundle), no_pending=True)
        assert result is False, "Missing AUTHORITATIVE_TEST_RESULT should FAIL with --check-no-pending"

    def test_present_authoritative_test_result_passes(self, tmp_path):
        meta = {
            "validation-command-log.md": (
                "AUTHORITATIVE_TEST_RESULT: 1804 passed, 12 skipped, 0 failed\n"
                "PLAYBOOK_TEST_RESULT: 149 passed, 0 failed\n"
            )
        }
        contract = _make_contract(tmp_path)
        bundle = _make_bundle(tmp_path, git_status=_CLEAN_STATUS, metadata_files=meta)
        result = validate_bundle(str(contract), str(bundle), no_pending=True)
        assert result is True, "Present AUTHORITATIVE_TEST_RESULT should PASS"


# ---------------------------------------------------------------------------
# Rule 5: PENDING bundle validation marker
# ---------------------------------------------------------------------------

class TestPendingBundleValidation:

    def test_pending_bundle_validation_marker_fails(self, tmp_path):
        meta = {
            "verdict.md": (
                "# Sprint Verdict\n"
                "BUNDLE_VALIDATION: PENDING\n"
            )
        }
        contract = _make_contract(tmp_path)
        bundle = _make_bundle(tmp_path, git_status=_CLEAN_STATUS, metadata_files=meta)
        result = validate_bundle(str(contract), str(bundle), no_pending=True)
        assert result is False, "BUNDLE_VALIDATION: PENDING in metadata should FAIL"


# ---------------------------------------------------------------------------
# Rule 6: Closure contradiction detection
# ---------------------------------------------------------------------------

class TestClosureContradiction:

    def test_proof_pass_verdict_fail_fails(self, tmp_path):
        """If final-bundle-validation-proof.txt says PASS but verdict.md says FAIL,
        it must be detected as a contradiction."""
        meta = {
            "final-bundle-validation-proof.txt": "BUNDLE_VALIDATION: PASS\n",
            "verdict.md": "SPRINT_VERDICT: FAIL\n",
            "validation-command-log.md": (
                "AUTHORITATIVE_TEST_RESULT: 100 passed, 0 failed\n"
            )
        }
        contract = _make_contract(tmp_path)
        bundle = _make_bundle(tmp_path, git_status=_CLEAN_STATUS, metadata_files=meta)
        result = validate_bundle(str(contract), str(bundle), no_pending=True)
        assert result is False, "CLOSURE_CONTRADICTION (proof=PASS, verdict=FAIL) should FAIL"


# ---------------------------------------------------------------------------
# Rule 7: Minimum metadata count floor enforcement
# ---------------------------------------------------------------------------

class TestMetadataFloor:

    def test_below_floor_fails_without_emergency_blocker(self, tmp_path):
        """Non-emergency bundles must have >= 30 metadata files (RUN_CONTRACT_METADATA_FLOOR)."""
        contract = _make_contract(tmp_path, emergency_blocker_bundle="false")
        bundle = _make_bundle(tmp_path, git_status=_CLEAN_STATUS, num_meta=5)
        result = validate_bundle(str(contract), str(bundle))
        assert result is False, "Below metadata floor should FAIL"

    def test_above_floor_passes(self, tmp_path):
        contract = _make_contract(tmp_path, emergency_blocker_bundle="false")
        bundle = _make_bundle(tmp_path, git_status=_CLEAN_STATUS, num_meta=35)
        result = validate_bundle(str(contract), str(bundle))
        assert result is True, "Above metadata floor should PASS"

    def test_contract_min_below_floor_fails(self, tmp_path):
        """A contract itself cannot set min_metadata_count below 30."""
        contract = _make_contract(tmp_path, min_metadata_count="5",
                                  emergency_blocker_bundle="false")
        bundle = _make_bundle(tmp_path, git_status=_CLEAN_STATUS, num_meta=35)
        result = validate_bundle(str(contract), str(bundle))
        assert result is False, (
            "Contract with min_metadata_count < RUN_CONTRACT_METADATA_FLOOR should FAIL"
        )


if __name__ == "__main__":
    import pytest as _pytest
    sys.exit(_pytest.main([__file__, "-v"]))
