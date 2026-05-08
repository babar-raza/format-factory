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

import sys
import tempfile
import zipfile
from pathlib import Path

# Add tools/evidence to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "evidence"))

from validate_evidence_bundle import validate_bundle  # noqa: E402


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
