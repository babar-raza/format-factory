#!/usr/bin/env python3
"""
Tests for check_current_state_consistency.py — run-state authority model (run041+).

Checks performed:
1. FAIL when master-plan Current Status contains "Latest commit: PENDING"
2. FAIL when master-plan contains "changes pending commit"
3. FAIL when memory/09 contains "changes pending commit"
4. FAIL when registry FODS gate_6 approved_by is not null
5. FAIL when FODT in registry but scoring package says gate_1_approved: false
6. FAIL when master-plan is missing
7. PASS on live repo after run041 fixes

Run from repo root:
    python tests/evidence/test_current_state_consistency.py

Exits 0 if all tests PASS, 1 if any test FAILS.
"""

import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent.parent


def run_checker(repo_root: Path) -> tuple[int, str]:
    """Run the checker script and return (exit_code, stdout+stderr)."""
    result = subprocess.run(
        [sys.executable, "tools/evidence/check_current_state_consistency.py",
         "--repo-root", str(repo_root)],
        capture_output=True, text=True,
        cwd=REPO_ROOT
    )
    return result.returncode, result.stdout + result.stderr


def make_minimal_repo(tmp_path: Path,
                      master_plan_content: str | None,
                      registry_content: str | None = None,
                      mem09_content: str | None = None,
                      scoring_pkg_content: str | None = None,
                      pack_yaml_content: str | None = None) -> None:
    """Set up a minimal fake repo structure for testing."""
    (tmp_path / "plans").mkdir(parents=True, exist_ok=True)
    (tmp_path / "registry" / "candidates").mkdir(parents=True, exist_ok=True)
    (tmp_path / "memory").mkdir(parents=True, exist_ok=True)
    (tmp_path / "acquisition-packs" / "fods").mkdir(parents=True, exist_ok=True)

    if master_plan_content is not None:
        (tmp_path / "plans" / "master-plan.md").write_text(master_plan_content, encoding="utf-8")

    if registry_content is not None:
        (tmp_path / "registry" / "format-registry.yaml").write_text(registry_content, encoding="utf-8")
    else:
        # Default: FODS with gate_6 not approved, no FODT entry
        (tmp_path / "registry" / "format-registry.yaml").write_text(
            _default_registry(), encoding="utf-8"
        )

    if mem09_content is not None:
        (tmp_path / "memory" / "09-current-state-before-phase1.md").write_text(
            mem09_content, encoding="utf-8"
        )

    if scoring_pkg_content is not None:
        (tmp_path / "registry" / "candidates" / "fodt-gate1-scoring-package.yaml").write_text(
            scoring_pkg_content, encoding="utf-8"
        )
    else:
        # Default: gate_1_approved: false (candidate-only)
        (tmp_path / "registry" / "candidates" / "fodt-gate1-scoring-package.yaml").write_text(
            "gate_1_approved: false\n", encoding="utf-8"
        )

    if pack_yaml_content is not None:
        (tmp_path / "acquisition-packs" / "fods" / "pack.yaml").write_text(
            pack_yaml_content, encoding="utf-8"
        )
    else:
        # Default: gate_6 not approved
        (tmp_path / "acquisition-packs" / "fods" / "pack.yaml").write_text(
            _default_pack_yaml(), encoding="utf-8"
        )


def _default_master_plan() -> str:
    return """# Master Plan

**Current status:** last_completed_run: run041. Gate 5 pending human review.

## Section 33 — Run Commit Ledger

| Run | Commits |
|-----|---------|
| run041 | abc1234 |
"""


def _default_registry() -> str:
    return """formats:
  - format_id: fods
    gates:
      gate_6:
        status: oracle_blocked_missing_tool
        approved_by: null
        approved_date: null
"""


def _default_pack_yaml() -> str:
    return """format_id: fods
gates:
  gate_6:
    status: oracle_blocked_missing_tool
    approved: false
"""


def test_fail_latest_commit_pending() -> bool:
    """FAIL when master-plan Current Status contains 'Latest commit: PENDING'."""
    content = _default_master_plan().replace(
        "**Current status:** last_completed_run: run041. Gate 5 pending human review.",
        "**Current status:** Latest commit: PENDING (run041 in progress)."
    )
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        make_minimal_repo(tmp_path, content)
        rc, out = run_checker(tmp_path)
        if rc == 0:
            print("FAIL: test_fail_latest_commit_pending — expected FAIL exit code, got PASS")
            print(f"  Output: {out[:300]}")
            return False
        if "CURRENT_STATE_CONSISTENCY: FAIL" not in out:
            print("FAIL: test_fail_latest_commit_pending — expected FAIL message in output")
            print(f"  Output: {out[:300]}")
            return False
        print("PASS: test_fail_latest_commit_pending — correctly rejected 'Latest commit: PENDING'")
        return True


def test_fail_changes_pending_commit() -> bool:
    """FAIL when master-plan Current Status contains 'changes pending commit'."""
    content = _default_master_plan().replace(
        "**Current status:** last_completed_run: run041. Gate 5 pending human review.",
        "**Current status:** run041 changes pending commit."
    )
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        make_minimal_repo(tmp_path, content)
        rc, out = run_checker(tmp_path)
        if rc == 0:
            print("FAIL: test_fail_changes_pending_commit — expected FAIL exit code, got PASS")
            print(f"  Output: {out[:300]}")
            return False
        if "CURRENT_STATE_CONSISTENCY: FAIL" not in out:
            print("FAIL: test_fail_changes_pending_commit — expected FAIL message in output")
            return False
        print("PASS: test_fail_changes_pending_commit — correctly rejected 'changes pending commit'")
        return True


def test_fail_memory09_pending() -> bool:
    """FAIL when memory/09 contains 'changes pending commit'."""
    mem09 = "**Current status:** run041 changes pending commit.\n"
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        make_minimal_repo(tmp_path, _default_master_plan(), mem09_content=mem09)
        rc, out = run_checker(tmp_path)
        if rc == 0:
            print("FAIL: test_fail_memory09_pending — expected FAIL exit code, got PASS")
            print(f"  Output: {out[:300]}")
            return False
        if "CURRENT_STATE_CONSISTENCY: FAIL" not in out:
            print("FAIL: test_fail_memory09_pending — expected FAIL message in output")
            return False
        print("PASS: test_fail_memory09_pending — correctly rejected PENDING marker in memory/09")
        return True


def test_fail_gate6_approved() -> bool:
    """FAIL when FODS registry gate_6 approved_by is not null."""
    registry = """formats:
  - format_id: fods
    gates:
      gate_6:
        status: passed
        approved_by: "Babar Raza"
        approved_date: "2026-05-07"
"""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        make_minimal_repo(tmp_path, _default_master_plan(), registry_content=registry)
        rc, out = run_checker(tmp_path)
        if rc == 0:
            print("FAIL: test_fail_gate6_approved — expected FAIL exit code, got PASS")
            print(f"  Output: {out[:300]}")
            return False
        if "CURRENT_STATE_CONSISTENCY: FAIL" not in out:
            print("FAIL: test_fail_gate6_approved — expected FAIL message in output")
            return False
        print("PASS: test_fail_gate6_approved — correctly rejected gate_6 approved_by not null")
        return True


def test_fail_fodt_inconsistent() -> bool:
    """FAIL when FODT appears in official registry but scoring package says gate_1_approved: false."""
    registry = _default_registry() + """  - format_id: fodt
    gates:
      gate_1:
        status: passed
        approved_by: "Babar Raza"
"""
    scoring_pkg = "gate_1_approved: false\n"
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        make_minimal_repo(
            tmp_path, _default_master_plan(),
            registry_content=registry,
            scoring_pkg_content=scoring_pkg
        )
        rc, out = run_checker(tmp_path)
        if rc == 0:
            print("FAIL: test_fail_fodt_inconsistent — expected FAIL exit code, got PASS")
            print(f"  Output: {out[:300]}")
            return False
        if "CURRENT_STATE_CONSISTENCY: FAIL" not in out:
            print("FAIL: test_fail_fodt_inconsistent — expected FAIL message in output")
            return False
        print("PASS: test_fail_fodt_inconsistent — correctly detected FODT registry/scoring mismatch")
        return True


def test_fail_master_plan_missing() -> bool:
    """FAIL when master-plan.md does not exist."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        make_minimal_repo(tmp_path, None)  # No master-plan
        rc, out = run_checker(tmp_path)
        if rc == 0:
            print("FAIL: test_fail_master_plan_missing — expected FAIL exit code, got PASS")
            return False
        if "CURRENT_STATE_CONSISTENCY: FAIL" not in out:
            print("FAIL: test_fail_master_plan_missing — expected FAIL message in output")
            return False
        print("PASS: test_fail_master_plan_missing — correctly FAILed when master-plan missing")
        return True


def test_pass_on_live_repo() -> bool:
    """PASS on the actual project repo (after run041 state-authority fixes)."""
    rc, out = run_checker(REPO_ROOT)
    if rc != 0:
        print("FAIL: test_pass_on_live_repo — expected PASS, got FAIL")
        print(f"  Output: {out[:600]}")
        return False
    if "CURRENT_STATE_CONSISTENCY: PASS" not in out:
        print("FAIL: test_pass_on_live_repo — expected PASS message, got:")
        print(f"  {out[:300]}")
        return False
    print("PASS: test_pass_on_live_repo — live repo is consistent")
    return True


def main() -> int:
    print("=" * 60)
    print("Tests: check_current_state_consistency.py (run041+ model)")
    print("=" * 60)
    print()

    tests = [
        test_fail_latest_commit_pending,
        test_fail_changes_pending_commit,
        test_fail_memory09_pending,
        test_fail_gate6_approved,
        test_fail_fodt_inconsistent,
        test_fail_master_plan_missing,
        test_pass_on_live_repo,
    ]

    results = []
    for test_fn in tests:
        print(f"--- {test_fn.__name__} ---")
        results.append(test_fn())
        print()

    total = len(results)
    passed = sum(results)
    failed = total - passed

    print("=" * 60)
    print(f"Results: {passed}/{total} PASS")
    if failed:
        print(f"FAIL: {failed} test(s) failed")
        return 1
    print("ALL TESTS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
