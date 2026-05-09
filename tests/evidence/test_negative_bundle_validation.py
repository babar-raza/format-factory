#!/usr/bin/env python3
"""
Negative tests for validate_evidence_bundle.py.

Tests that the validator correctly FAILS for:
1. Thin bundles (fewer metadata files than required minimum)
2. Bundles containing PENDING marker text in metadata files (--check-no-pending)

Run from repo root:
    python tests/evidence/test_negative_bundle_validation.py

Exits 0 if all tests PASS, 1 if any test FAILS.
"""

import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

# Add tools/evidence to path
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "evidence"))

from validate_evidence_bundle import validate_bundle  # noqa: E402

VALIDATE_SCRIPT = REPO_ROOT / "tools" / "evidence" / "validate_evidence_bundle.py"


def build_minimal_contract(tmp_dir: Path, min_meta: int = 5) -> Path:
    """Write a minimal contract YAML for tests."""
    contract = tmp_dir / "test-contract.yaml"
    contract.write_text(
        f"""\
contract_id: test-negative
require_clean_git: false
require_contract_in_bundle: false
require_manifest: false
min_metadata_count: {min_meta}
required_repo_files: []
required_metadata_files: []
forbidden_paths: []
""",
        encoding="utf-8",
    )
    return contract


def build_bundle_with_meta(tmp_dir: Path, meta_files: dict) -> Path:
    """Build a bundle zip with the given metadata files. No repo files."""
    bundle_path = tmp_dir / "test-bundle.zip"
    with zipfile.ZipFile(bundle_path, "w") as zf:
        # Add a minimal repo file so the repo/ folder exists
        zf.writestr("repo/placeholder.txt", "placeholder")
        # Add metadata files
        for name, content in meta_files.items():
            zf.writestr(f"bundle-metadata/{name}", content)
    return bundle_path


def build_sufficient_bundle(tmp_dir: Path, extra_meta: dict = None, bundle_name: str = "test-bundle.zip") -> Path:
    """Build a bundle with >= RUN_CONTRACT_METADATA_FLOOR metadata files.

    Used by tests that verify things other than metadata depth, so they pass the
    hardcoded floor check without interference.
    """
    # 32 dummy files comfortably exceeds RUN_CONTRACT_METADATA_FLOOR=30
    # (run047: restored from 5 to 32 after floor was restored from 4 to 30)
    meta = {f"_dummy_{i:02d}.txt": f"padding content {i}" for i in range(32)}
    if extra_meta:
        meta.update(extra_meta)
    bundle_path = tmp_dir / bundle_name
    with zipfile.ZipFile(bundle_path, "w") as zf:
        zf.writestr("repo/placeholder.txt", "placeholder")
        for name, content in meta.items():
            zf.writestr(f"bundle-metadata/{name}", content)
    return bundle_path


def test_thin_bundle_fails():
    """Validator must FAIL when metadata count is below min_metadata_count."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        # Contract requires at least 5 metadata files
        contract = build_minimal_contract(tmp_dir, min_meta=5)
        # Bundle has only 2 metadata files
        meta = {
            "file1.md": "content 1",
            "file2.md": "content 2",
        }
        bundle = build_bundle_with_meta(tmp_dir, meta)
        result = validate_bundle(str(contract), str(bundle), strict_git=False, no_pending=False)
        if result:
            print("FAIL: test_thin_bundle_fails — validator returned PASS but should have FAILed")
            return False
        print("PASS: test_thin_bundle_fails — validator correctly returned FAIL for thin bundle")
        return True


def test_pending_report_fails_with_flag():
    """Validator must FAIL when --check-no-pending is set and metadata contains PENDING marker."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        # Contract with low min_metadata so we don't fail on that
        contract = build_minimal_contract(tmp_dir, min_meta=1)
        # Bundle has a metadata file with PENDING marker
        meta = {
            "verdict.md": "**Validation status:** PENDING (bundle not yet built)\n",
        }
        bundle = build_bundle_with_meta(tmp_dir, meta)
        result = validate_bundle(str(contract), str(bundle), strict_git=False, no_pending=True)
        if result:
            print("FAIL: test_pending_report_fails_with_flag — validator returned PASS but should have FAILed")
            return False
        print("PASS: test_pending_report_fails_with_flag — validator correctly returned FAIL for PENDING marker")
        return True


def test_pending_report_passes_without_flag():
    """Validator must PASS when --check-no-pending is NOT set, even if PENDING marker present."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        contract = build_minimal_contract(tmp_dir, min_meta=30)
        # Same PENDING marker, but no_pending=False — use sufficient bundle to clear floor
        bundle = build_sufficient_bundle(tmp_dir, extra_meta={
            "verdict.md": "**Validation status:** PENDING (bundle not yet built)\n",
        })
        result = validate_bundle(str(contract), str(bundle), strict_git=False, no_pending=False)
        if not result:
            print("FAIL: test_pending_report_passes_without_flag — validator returned FAIL but should have PASSed")
            return False
        print("PASS: test_pending_report_passes_without_flag — validator correctly PASSED when flag not set")
        return True


def test_clean_bundle_passes_no_pending():
    """Validator must PASS when --check-no-pending is set and no PENDING markers present."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        contract = build_minimal_contract(tmp_dir, min_meta=30)
        # Use sufficient bundle to clear the floor check (32 files >= floor 30)
        bundle = build_sufficient_bundle(tmp_dir, extra_meta={
            "verdict.md": "**Validation status:** BUNDLE_VALIDATION: PASS\n",
        })
        result = validate_bundle(str(contract), str(bundle), strict_git=False, no_pending=True)
        if not result:
            print("FAIL: test_clean_bundle_passes_no_pending — validator returned FAIL but should have PASSed")
            return False
        print("PASS: test_clean_bundle_passes_no_pending — validator correctly PASSED for clean bundle")
        return True


def test_dirty_git_fails_even_with_require_clean_git_false():
    """Validator must FAIL when git-status-final.txt shows dirty even if require_clean_git: false.

    This is the Section D loophole fix (run040): dirty git always fails unless
    emergency_blocker_bundle: true is set.
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        contract = tmp_dir / "test-dirty-git-contract.yaml"
        contract.write_text(
            """\
contract_id: test-dirty-git
require_clean_git: false
emergency_blocker_bundle: false
require_contract_in_bundle: false
require_manifest: false
min_metadata_count: 1
required_repo_files: []
required_metadata_files: []
forbidden_paths: []
""",
            encoding="utf-8",
        )
        bundle_path = tmp_dir / "test-dirty-bundle.zip"
        with zipfile.ZipFile(bundle_path, "w") as zf:
            zf.writestr("repo/placeholder.txt", "placeholder")
            zf.writestr(
                "bundle-metadata/git-status-final.txt",
                "On branch main\nChanges not staged for commit:\n  modified: plans/master-plan.md\n",
            )
            zf.writestr("bundle-metadata/verdict.md", "Git clean: no")
        result = validate_bundle(str(contract), str(bundle_path), strict_git=False, no_pending=False)
        if result:
            print(
                "FAIL: test_dirty_git_fails_even_with_require_clean_git_false "
                "— validator returned PASS but should have FAILed (loophole still open)"
            )
            return False
        print(
            "PASS: test_dirty_git_fails_even_with_require_clean_git_false "
            "— correctly FAILed for dirty git even when require_clean_git: false"
        )
        return True


def test_dirty_git_passes_with_emergency_blocker_bundle_true():
    """Validator must PASS (warn only) when emergency_blocker_bundle: true and git is dirty.

    This is the intentional escape hatch for documented blocker/failed bundles.
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        contract = tmp_dir / "test-emergency-contract.yaml"
        contract.write_text(
            """\
contract_id: test-emergency-blocker
require_clean_git: false
emergency_blocker_bundle: true
require_contract_in_bundle: false
require_manifest: false
min_metadata_count: 1
required_repo_files: []
required_metadata_files: []
forbidden_paths: []
""",
            encoding="utf-8",
        )
        bundle_path = tmp_dir / "test-blocker-bundle.zip"
        with zipfile.ZipFile(bundle_path, "w") as zf:
            zf.writestr("repo/placeholder.txt", "placeholder")
            zf.writestr(
                "bundle-metadata/git-status-final.txt",
                "On branch main\nChanges not staged for commit:\n  modified: plans/master-plan.md\n",
            )
            zf.writestr("bundle-metadata/verdict.md", "BUNDLE_VALIDATION: FAIL — blocked bundle")
        result = validate_bundle(str(contract), str(bundle_path), strict_git=False, no_pending=False)
        if not result:
            print(
                "FAIL: test_dirty_git_passes_with_emergency_blocker_bundle_true "
                "— validator returned FAIL but should have PASSed with emergency_blocker_bundle: true"
            )
            return False
        print(
            "PASS: test_dirty_git_passes_with_emergency_blocker_bundle_true "
            "— correctly PASSed with emergency_blocker_bundle: true exception"
        )
        return True


def test_env_example_not_blocked_by_env_pattern():
    """.env.example in repo/ must NOT be blocked by the '.env' forbidden pattern (run042 fix).

    The forbidden pattern '.env' should only match the exact file '.env', not '.env.example'.
    This ensures .env.example (which is explicitly git-tracked) is included in bundles.
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        contract = tmp_dir / "test-env-contract.yaml"
        contract.write_text(
            """\
contract_id: test-env-example
require_clean_git: false
require_contract_in_bundle: false
require_manifest: false
min_metadata_count: 30
required_repo_files:
  - .env.example
required_metadata_files: []
forbidden_paths:
  - .env
  - .local/
  - .git/
""",
            encoding="utf-8",
        )
        bundle_path = tmp_dir / "test-env-bundle.zip"
        with zipfile.ZipFile(bundle_path, "w") as zf:
            zf.writestr("repo/.env.example", "ANTHROPIC_API_KEY=your-key-here\n")
            zf.writestr("bundle-metadata/git-log.txt", "abc1234 initial commit\n")
            # Add dummy metadata to clear the RUN_CONTRACT_METADATA_FLOOR
            for i in range(32):
                zf.writestr(f"bundle-metadata/_dummy_{i:02d}.txt", f"padding {i}")
        result = validate_bundle(str(contract), str(bundle_path), strict_git=False, no_pending=False)
        if not result:
            print(
                "FAIL: test_env_example_not_blocked_by_env_pattern "
                "— validator FAILed but .env.example should be allowed (not blocked by .env pattern)"
            )
            return False
        print(
            "PASS: test_env_example_not_blocked_by_env_pattern "
            "— .env.example correctly allowed despite .env forbidden pattern"
        )
        return True


def test_normal_pass_metadata_depth_fail():
    """Validator must FAIL when metadata count is below normal_pass_min_metadata (run042 fix).

    A bundle with only 5 metadata files must FAIL when base-run contract has
    normal_pass_min_metadata: 30. This enforces evidence depth for normal PASS bundles.
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        contract = tmp_dir / "test-depth-contract.yaml"
        contract.write_text(
            """\
contract_id: test-metadata-depth
require_clean_git: false
require_contract_in_bundle: false
require_manifest: false
min_metadata_count: 5
normal_pass_min_metadata: 30
required_repo_files: []
required_metadata_files: []
forbidden_paths: []
""",
            encoding="utf-8",
        )
        # Bundle with exactly 5 metadata files — passes min_metadata_count but fails depth
        meta = {f"file{i}.md": f"content {i}" for i in range(5)}
        bundle = build_bundle_with_meta(tmp_dir, meta)
        result = validate_bundle(str(contract), str(bundle), strict_git=False, no_pending=False)
        if result:
            print(
                "FAIL: test_normal_pass_metadata_depth_fail "
                "— validator returned PASS but should have FAILed (5 < normal_pass_min_metadata 30)"
            )
            return False
        print(
            "PASS: test_normal_pass_metadata_depth_fail "
            "— validator correctly FAILed when metadata depth < normal_pass_min_metadata"
        )
        return True


def test_run_contract_metadata_floor_fails():
    """Validator must FAIL when bundle has fewer metadata files than the hardcoded floor.

    RUN_CONTRACT_METADATA_FLOOR=30 means every bundle must have at least 30 metadata files
    for a normal PASS bundle (run047: restored from 4 back to 30 after run046 regression).
    A bundle with only 3 metadata files must fail (3 < 30).
    Contract with min_metadata_count=3 also fails RUN_CONTRACT_MINIMUM_NOT_BELOW_BASE.
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        # Contract similar to run045's regressed contract (min_metadata_count: 3)
        contract = tmp_dir / "test-floor-contract.yaml"
        contract.write_text(
            """\
contract_id: test-run045-regression
require_clean_git: false
emergency_blocker_bundle: false
require_contract_in_bundle: false
require_manifest: false
min_metadata_count: 3
normal_pass_min_metadata: 3
required_repo_files: []
required_metadata_files: []
forbidden_paths: []
""",
            encoding="utf-8",
        )
        # Bundle with only 4 metadata files (as run045 produced)
        meta = {
            "git-log.txt": "ff47169 chore: fix run045 contract\n",
            "git-status-final.txt": "On branch main\nnothing to commit, working tree clean\n",
            "repo-tree.txt": ".\n./plans\n./plans/master-plan.md\n"

        }
        bundle = build_bundle_with_meta(tmp_dir, meta)
        result = validate_bundle(str(contract), str(bundle), strict_git=False, no_pending=False)
        if result:
            print(
                "FAIL: test_run_contract_metadata_floor_fails "
                "— validator returned PASS but should have FAILed "
                "(3 metadata files < RUN_CONTRACT_METADATA_FLOOR=30)"
            )
            return False
        print(
            "PASS: test_run_contract_metadata_floor_fails "
            "— validator correctly FAILed for 3-file bundle "
            "(RUN_CONTRACT_METADATA_FLOOR=30 enforced)"
        )
        return True




def test_run_contract_minimum_not_below_base():
    """Validator must FAIL when a run contract's min_metadata_count is below RUN_CONTRACT_METADATA_FLOOR.

    Even if the bundle has 35 metadata files (above floor=30), a contract with
    min_metadata_count=3 must FAIL with RUN_CONTRACT_MINIMUM_NOT_BELOW_BASE.
    This prevents run046-style regression where contract lowered the floor to 3.
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        # Contract with min_metadata_count: 3 (below floor of 30), no emergency bypass
        contract = tmp_dir / "test-contract-min-below-base.yaml"
        contract.write_text(
            """contract_id: test-contract-min-below-base
require_clean_git: false
emergency_blocker_bundle: false
require_contract_in_bundle: false
require_manifest: false
min_metadata_count: 3
normal_pass_min_metadata: 3
required_repo_files: []
required_metadata_files: []
forbidden_paths: []
""",
            encoding="utf-8",
        )
        # Bundle with 35 metadata files — well above the hardcoded floor of 30
        bundle_path = tmp_dir / "test-bundle-35-files.zip"
        with zipfile.ZipFile(bundle_path, "w") as zf:
            zf.writestr("repo/placeholder.txt", "placeholder")
            for i in range(35):
                zf.writestr(f"bundle-metadata/file_{i:02d}.txt", f"content {i}")
        result = validate_bundle(str(contract), str(bundle_path), strict_git=False, no_pending=False)
        if result:
            print(
                "FAIL: test_run_contract_minimum_not_below_base "
                "— validator returned PASS but should have FAILed "
                "(contract min_metadata_count=3 < RUN_CONTRACT_METADATA_FLOOR=30)"
            )
            return False
        print(
            "PASS: test_run_contract_minimum_not_below_base "
            "— validator correctly FAILed when contract min < base floor "
            "(RUN_CONTRACT_MINIMUM_NOT_BELOW_BASE enforced)"
        )
        return True

def test_run_contract_metadata_floor_bypassed_by_emergency():
    """Validator must PASS when emergency_blocker_bundle:true bypasses the floor.

    Emergency bundles (blocked/failed sprints) are explicitly exempt from the floor.
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        contract = tmp_dir / "test-emergency-floor-contract.yaml"
        contract.write_text(
            """\
contract_id: test-emergency-floor-bypass
require_clean_git: false
emergency_blocker_bundle: true
require_contract_in_bundle: false
require_manifest: false
min_metadata_count: 1
normal_pass_min_metadata: 0
required_repo_files: []
required_metadata_files: []
forbidden_paths: []
""",
            encoding="utf-8",
        )
        # Bundle with only 4 files — would fail floor, but emergency_blocker bypasses it
        meta = {
            "git-log.txt": "abc1234 blocker commit\n",
            "git-status-final.txt": "On branch main\nnothing to commit, working tree clean\n",
            "blocker-report.md": "ORACLE_ENV: BLOCKED\n",
            "bundle-manifest.yaml": "entries: []\n",
        }
        bundle = build_bundle_with_meta(tmp_dir, meta)
        result = validate_bundle(str(contract), str(bundle), strict_git=False, no_pending=False)
        if not result:
            print(
                "FAIL: test_run_contract_metadata_floor_bypassed_by_emergency "
                "— validator returned FAIL but emergency_blocker_bundle:true should bypass the floor"
            )
            return False
        print(
            "PASS: test_run_contract_metadata_floor_bypassed_by_emergency "
            "— floor correctly bypassed when emergency_blocker_bundle:true"
        )
        return True



def test_required_metadata_depth_fails():
    """REQUIRED_METADATA_DEPTH: FAIL when min_metadata_count>=80 but <10 named files."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        contract = tmp_dir / "test-depth-contract.yaml"
        contract.write_text(
            """contract_id: test-depth-fail
require_clean_git: false
require_contract_in_bundle: false
require_manifest: false
min_metadata_count: 90
normal_pass_min_metadata: 0
required_metadata_files:
  - git-log.txt
  - git-status-final.txt
  - repo-tree.txt
  - bundle-manifest.yaml
required_repo_files: []
forbidden_paths: []
""",
            encoding="utf-8",
        )
        bundle = build_sufficient_bundle(tmp_dir, extra_meta={
            f"_extra_{i:02d}.txt": f"extra {i}" for i in range(70)
        })
        result = validate_bundle(str(contract), str(bundle), strict_git=False, no_pending=False)
        if result:
            print(
                "FAIL: test_required_metadata_depth_fails "
                "-- validator returned PASS but should have FAILed "
                "(min_metadata_count=90 but only 4 required_metadata_files)"
            )
            return False
        print(
            "PASS: test_required_metadata_depth_fails "
            "-- REQUIRED_METADATA_DEPTH correctly rejected contract "
            "with min=90 but only 4 named files"
        )
        return True


def test_required_metadata_depth_passes_with_test_contract():
    """REQUIRED_METADATA_DEPTH: PASS when test_contract: true is set (bypass allowed)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        contract = tmp_dir / "test-depth-bypass-contract.yaml"
        contract.write_text(
            """contract_id: test-depth-bypass
test_contract: true
require_clean_git: false
require_contract_in_bundle: false
require_manifest: false
min_metadata_count: 90
normal_pass_min_metadata: 0
required_metadata_files:
  - git-log.txt
  - git-status-final.txt
  - repo-tree.txt
  - bundle-manifest.yaml
required_repo_files: []
forbidden_paths: []
""",
            encoding="utf-8",
        )
        bundle = build_sufficient_bundle(tmp_dir, extra_meta={
            **{f"_extra_{i:02d}.txt": f"extra {i}" for i in range(70)},
            "git-log.txt": "fake git log",
            "git-status-final.txt": "nothing to commit",
            "repo-tree.txt": "repo tree",
            "bundle-manifest.yaml": "manifest: {}",
        })
        result = validate_bundle(str(contract), str(bundle), strict_git=False, no_pending=False)
        if not result:
            print(
                "FAIL: test_required_metadata_depth_passes_with_test_contract "
                "-- validator returned FAIL but test_contract: true should bypass check"
            )
            return False
        print(
            "PASS: test_required_metadata_depth_passes_with_test_contract "
            "-- REQUIRED_METADATA_DEPTH correctly bypassed when test_contract: true"
        )
        return True


def test_bundle_validation_pending_fails_with_flag():
    """BUNDLE_VALIDATION: PENDING in final-bundle-validation-proof.txt must fail --check-no-pending.

    This is the S-F2F-01C fix: final-bundle-validation-proof.txt that still says
    BUNDLE_VALIDATION: PENDING must be caught by the validator. Previously this pattern
    was not in PENDING_MARKER_PATTERNS, allowing the defect to slip through.
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        contract = build_minimal_contract(tmp_dir, min_meta=1)
        meta = {
            "final-bundle-validation-proof.txt": (
                "Final Bundle Validation Proof\n"
                "BUNDLE_VALIDATION: PENDING\n"
            ),
        }
        bundle = build_bundle_with_meta(tmp_dir, meta)
        result = validate_bundle(str(contract), str(bundle), strict_git=False, no_pending=True)
        if result:
            print(
                "FAIL: test_bundle_validation_pending_fails_with_flag "
                "— validator returned PASS but should have FAILed "
                "(BUNDLE_VALIDATION: PENDING not caught)"
            )
            return False
        print(
            "PASS: test_bundle_validation_pending_fails_with_flag "
            "— BUNDLE_VALIDATION: PENDING correctly caught by --check-no-pending"
        )
        return True


def test_proposed_pending_human_approval_does_not_fail():
    """proposed_pending_human_approval in taskcard text must NOT fail --check-no-pending.

    Legitimate taskcard status strings like 'proposed_pending_human_approval' should
    not be flagged as PENDING markers. Only placeholder-style markers should fail.
    Uses a sufficient bundle (>=30 metadata files) to clear the metadata floor check.
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        contract = build_minimal_contract(tmp_dir, min_meta=30)
        bundle = build_sufficient_bundle(tmp_dir, extra_meta={
            "sf2f02-taskcard-check.md": (
                "# S-F2F-02 Taskcard Status Check\n"
                "Status: proposed_pending_human_approval\n"
                "TASKCARD_BOUNDARY: PASS\n"
            ),
        })
        result = validate_bundle(str(contract), str(bundle), strict_git=False, no_pending=True)
        if not result:
            print(
                "FAIL: test_proposed_pending_human_approval_does_not_fail "
                "— validator FAILed but proposed_pending_human_approval should be allowed"
            )
            return False
        print(
            "PASS: test_proposed_pending_human_approval_does_not_fail "
            "— proposed_pending_human_approval correctly NOT flagged as PENDING marker"
        )
        return True



def test_real_sprint_contract_with_test_contract_true_fails(tmp_path):
    """A real sprint contract (run\d+) with test_contract: true must fail."""
    contract = tmp_path / "run099-test.yaml"
    contract.write_text(
        "contract_id: run099-test\n"
        "version: \"1.0\"\n"
        "require_clean_git: false\n"
        "emergency_blocker_bundle: false\n"
        "test_contract: true\n"
        "min_metadata_count: 1\n"
        "normal_pass_min_metadata: 1\n"
        "required_repo_files: []\n"
        "required_metadata_files: []\n"
        "forbidden_patterns: []\n",
        encoding="utf-8"
    )
    bundle = tmp_path / "bundle.zip"
    import zipfile
    with zipfile.ZipFile(bundle, "w") as zf:
        zf.writestr("repo/README.md", "test")
        zf.writestr("bundle-metadata/bundle-manifest.yaml", "entries: 1")
        zf.writestr("bundle-metadata/git-log.txt", "abc123 test commit")
        zf.writestr("bundle-metadata/git-status-final.txt", "nothing to commit")
    result = subprocess.run(
        [sys.executable, str(VALIDATE_SCRIPT), "--contract", str(contract), "--bundle", str(bundle)],
        capture_output=True, text=True
    )
    assert "BUNDLE_VALIDATION: FAIL" in result.stdout or "TEST_CONTRACT_MISUSE" in result.stdout, (
        f"Expected FAIL for test_contract: true on real sprint contract, got:\n{result.stdout}"
    )


def test_historical_contract_bypasses_depth_check(tmp_path):
    """historical_contract: true should bypass REQUIRED_METADATA_DEPTH check."""
    contract = tmp_path / "run001-historical.yaml"
    # old contract with historical_contract: true and high min_metadata but few named files
    contract.write_text(
        "contract_id: run001-historical\n"
        "version: \"1.0\"\n"
        "require_clean_git: false\n"
        "emergency_blocker_bundle: false\n"
        "historical_contract: true\n"
        "min_metadata_count: 1\n"
        "normal_pass_min_metadata: 1\n"
        "required_repo_files: []\n"
        "required_metadata_files: [bundle-manifest.yaml, git-log.txt, git-status-final.txt]\n"
        "forbidden_patterns: []\n",
        encoding="utf-8"
    )
    bundle = tmp_path / "bundle.zip"
    import zipfile
    with zipfile.ZipFile(bundle, "w") as zf:
        zf.writestr("repo/README.md", "test")
        zf.writestr("bundle-metadata/bundle-manifest.yaml", "entries: 1")
        zf.writestr("bundle-metadata/git-log.txt", "abc123 test commit")
        zf.writestr("bundle-metadata/git-status-final.txt", "nothing to commit")
    result = subprocess.run(
        [sys.executable, str(VALIDATE_SCRIPT), "--contract", str(contract), "--bundle", str(bundle)],
        capture_output=True, text=True
    )
    # Should NOT fail due to REQUIRED_METADATA_DEPTH (historical_contract bypasses that check)
    assert "REQUIRED_METADATA_DEPTH: FAIL" not in result.stdout, (
        f"historical_contract should bypass depth check:\n{result.stdout}"
    )


def test_current_run_contract_missing_verdict_fails_with_named_requirement(tmp_path):
    """A current sprint contract that explicitly requires verdict.md must fail if it is absent."""
    contract = tmp_path / "run099-full.yaml"
    contract.write_text(
        "contract_id: run099-full\n"
        "version: \"1.0\"\n"
        "require_clean_git: false\n"
        "emergency_blocker_bundle: false\n"
        "min_metadata_count: 1\n"
        "normal_pass_min_metadata: 1\n"
        "required_repo_files: []\n"
        "required_metadata_files: [bundle-manifest.yaml, git-log.txt, git-status-final.txt, verdict.md]\n"
        "forbidden_patterns: []\n",
        encoding="utf-8"
    )
    bundle = tmp_path / "bundle.zip"
    import zipfile
    with zipfile.ZipFile(bundle, "w") as zf:
        zf.writestr("repo/README.md", "test")
        zf.writestr("bundle-metadata/bundle-manifest.yaml", "entries: 1")
        zf.writestr("bundle-metadata/git-log.txt", "abc123 test commit")
        zf.writestr("bundle-metadata/git-status-final.txt", "nothing to commit")
        # verdict.md is intentionally absent
    result = subprocess.run(
        [sys.executable, str(VALIDATE_SCRIPT), "--contract", str(contract), "--bundle", str(bundle)],
        capture_output=True, text=True
    )
    assert "BUNDLE_VALIDATION: FAIL" in result.stdout, (
        f"Expected FAIL for missing verdict.md:\n{result.stdout}"
    )


def test_closure_contradiction_fails_when_proof_pass_verdict_fail(tmp_path):
    """Bundle with final proof=PASS but verdict=FAIL must fail --check-no-pending."""
    contract = tmp_path / "run099-closure.yaml"
    contract.write_text(
        "contract_id: run099-closure\n"
        "version: \"1.0\"\n"
        "require_clean_git: false\n"
        "emergency_blocker_bundle: true\n"
        "min_metadata_count: 1\n"
        "normal_pass_min_metadata: 1\n"
        "required_repo_files: []\n"
        "required_metadata_files: [bundle-manifest.yaml, git-log.txt, git-status-final.txt]\n"
        "forbidden_patterns: []\n",
        encoding="utf-8"
    )
    bundle = tmp_path / "bundle.zip"
    with zipfile.ZipFile(bundle, "w") as zf:
        zf.writestr("repo/README.md", "test")
        zf.writestr("bundle-metadata/bundle-manifest.yaml", "entries: 1")
        zf.writestr("bundle-metadata/git-log.txt", "abc123 test commit")
        zf.writestr("bundle-metadata/git-status-final.txt", "nothing to commit")
        # Contradiction: proof says PASS, verdict says FAIL
        zf.writestr("bundle-metadata/final-bundle-validation-proof.txt",
                    "BUNDLE_VALIDATION: PASS\n")
        zf.writestr("bundle-metadata/verdict.md",
                    "# Sprint Verdict\nSPRINT_VERDICT: FAIL\n")
    result = subprocess.run(
        [sys.executable, str(VALIDATE_SCRIPT), "--contract", str(contract), "--bundle", str(bundle),
         "--check-no-pending"],
        capture_output=True, text=True
    )
    assert "BUNDLE_VALIDATION: FAIL" in result.stdout, (
        f"Expected FAIL for proof/verdict contradiction:\n{result.stdout}"
    )
    assert "CLOSURE_CONTRADICTION" in result.stdout, (
        f"Expected CLOSURE_CONTRADICTION in output:\n{result.stdout}"
    )


def test_closure_contradiction_passes_when_consistent(tmp_path):
    """Bundle with final proof=PASS and verdict=PASS must pass --check-no-pending."""
    contract = tmp_path / "run099-consistent.yaml"
    contract.write_text(
        "contract_id: run099-consistent\n"
        "version: \"1.0\"\n"
        "require_clean_git: false\n"
        "emergency_blocker_bundle: true\n"
        "min_metadata_count: 1\n"
        "normal_pass_min_metadata: 1\n"
        "required_repo_files: []\n"
        "required_metadata_files: [bundle-manifest.yaml, git-log.txt, git-status-final.txt]\n"
        "forbidden_patterns: []\n",
        encoding="utf-8"
    )
    bundle = tmp_path / "bundle.zip"
    with zipfile.ZipFile(bundle, "w") as zf:
        zf.writestr("repo/README.md", "test")
        zf.writestr("bundle-metadata/bundle-manifest.yaml", "entries: 1")
        zf.writestr("bundle-metadata/git-log.txt", "abc123 test commit")
        zf.writestr("bundle-metadata/git-status-final.txt", "nothing to commit")
        # Consistent: both say PASS
        zf.writestr("bundle-metadata/final-bundle-validation-proof.txt",
                    "BUNDLE_VALIDATION: PASS\n")
        zf.writestr("bundle-metadata/verdict.md",
                    "# Sprint Verdict\nSPRINT_VERDICT: COMPLETE_WITH_CLOSURE_HYGIENE_REPAIR\n")
    result = subprocess.run(
        [sys.executable, str(VALIDATE_SCRIPT), "--contract", str(contract), "--bundle", str(bundle),
         "--check-no-pending"],
        capture_output=True, text=True
    )
    assert "BUNDLE_VALIDATION: PASS" in result.stdout, (
        f"Expected PASS for consistent proof/verdict:\n{result.stdout}"
    )
    assert "CLOSURE_CONTRADICTION" not in result.stdout or "PASS" in result.stdout


def main():
    print("=" * 60)
    print("Negative Tests: validate_evidence_bundle.py")
    print("=" * 60)
    print()

    tests = [
        test_thin_bundle_fails,
        test_pending_report_fails_with_flag,
        test_pending_report_passes_without_flag,
        test_clean_bundle_passes_no_pending,
        test_dirty_git_fails_even_with_require_clean_git_false,
        test_dirty_git_passes_with_emergency_blocker_bundle_true,
        test_env_example_not_blocked_by_env_pattern,
        test_normal_pass_metadata_depth_fail,
        test_run_contract_metadata_floor_fails,
        test_run_contract_metadata_floor_bypassed_by_emergency,
        test_run_contract_minimum_not_below_base,
        test_required_metadata_depth_fails,
        test_required_metadata_depth_passes_with_test_contract,
        test_bundle_validation_pending_fails_with_flag,
        test_proposed_pending_human_approval_does_not_fail,
    ]

    results = []
    for test_fn in tests:
        print(f"--- {test_fn.__name__} ---")
        results.append(test_fn())
        print()

    passed = sum(1 for r in results if r)
    total = len(results)
    print("=" * 60)
    if passed == total:
        print(f"ALL TESTS PASS: {passed}/{total}")
        sys.exit(0)
    else:
        print(f"TESTS FAILED: {passed}/{total} passed")
        sys.exit(1)


if __name__ == "__main__":
    main()
