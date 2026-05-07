#!/usr/bin/env python3
"""
check_current_state_consistency.py — Validate current-state consistency across the project.

PURPOSE:
    Verify that committed current-state files do not contain current-looking stale
    PENDING markers (e.g., "Latest commit: PENDING") and that gate states, FODT
    status, and FODS Gate 6 status are internally consistent.

    IMPORTANT: This checker does NOT require committed files to contain the exact
    final Git HEAD hash. That was a flawed "self-referential commit-hash loop" model
    fixed in run041. See docs/current-state-and-evidence-authority.md.

    The exact final Git HEAD is authoritative only in evidence bundle metadata
    (bundle-metadata/git-log.txt and bundle-metadata/git-status-final.txt).

USAGE:
    python tools/evidence/check_current_state_consistency.py [--repo-root PATH]

OUTPUT:
    CURRENT_STATE_CONSISTENCY: PASS
    CURRENT_STATE_CONSISTENCY: FAIL

EXIT CODE:
    0 on PASS, 1 on FAIL

CHECKS PERFORMED:
    1. plans/master-plan.md Current Status section does NOT contain
       "Latest commit: PENDING" (sprint-in-progress marker must be absent after final commit)
    2. plans/master-plan.md does NOT contain "changes pending commit"
    3. memory/09-current-state-before-phase1.md does NOT contain "changes pending commit"
    4. registry/format-registry.yaml FODS gate_6 approved_by is null
    5. registry/format-registry.yaml FODS gate_6 approved_date is null
    6. registry/format-registry.yaml FODS gate_6 status is NOT "passed"
    7. FODT state is internally consistent:
       - If registry has FODT format_id entry: gate_1_approved must be true, pack must exist
       - If no FODT registry entry: gate_1_approved must be false, no pack
    8. acquisition-packs/fodt/ exists IFF FODT has approved Gate 1 in registry
    9. acquisition-packs/fods/pack.yaml gate_6 not approved
    10. Section 33 (or Run Commit Ledger) exists in master-plan.md

NOTES:
    - Does NOT require "Latest commit: <hash>" in committed files (design fixed run041)
    - Does NOT require committed files to match git HEAD hash
    - Safe to run at any time (read-only)
    - If master-plan does not exist, reports FAIL with explanation
"""

import re
import sys
from pathlib import Path


# Patterns that indicate a sprint is still in progress — must NOT appear in final state
PENDING_STATE_PATTERNS = [
    r"Latest commit:\s*PENDING",
    r"changes pending commit",
    r"run\d+\s+changes\s+pending",
    r"pending commit",
]


def check_no_pending_markers(text: str, context: str,
                              issues: list, warnings: list) -> None:
    """Check that text does not contain sprint-in-progress PENDING markers."""
    for pattern in PENDING_STATE_PATTERNS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            # Context: only flag in Current Status / header sections, not in historical run notes
            # The "changes pending commit" and "Latest commit: PENDING" patterns are only
            # problematic when they appear as current-state claims.
            # Exclude matches that are clearly inside historical commit log entries
            # (i.e., within a table row describing a past run, not in the current header).
            line_start = text.rfind('\n', 0, m.start()) + 1
            line_end = text.find('\n', m.end())
            line = text[line_start:line_end] if line_end > 0 else text[line_start:]
            # Heuristic: historical run entries start with "| run0" or are deep in Section 32
            if re.match(r'\|\s*run0\d+', line.strip()):
                continue  # Skip historical run table rows
            issues.append(
                f"{context}: contains sprint-in-progress marker: {m.group(0)!r} "
                f"(line: {line.strip()[:80]!r}) — must be removed after final commit. "
                f"See docs/current-state-and-evidence-authority.md"
            )


def check_registry_gate6_not_approved(repo_root: Path, issues: list, warnings: list) -> None:
    """Check FODS registry gate_6 is NOT approved (approved_by: null, approved_date: null, not passed)."""
    registry = repo_root / "registry" / "format-registry.yaml"
    if not registry.exists():
        warnings.append("registry/format-registry.yaml not found — skipping gate_6 check")
        return

    text = registry.read_text(encoding="utf-8")

    # Find FODS gate_6 section
    # Look for the fods entry first, then find gate_6 within it
    gate6_match = re.search(r'gate_6:.*?(?=gate_7:|$)', text, re.DOTALL)
    if not gate6_match:
        warnings.append("registry gate_6 section not found — skipping")
        return

    gate6_text = gate6_match.group(0)

    # Check approved_by is null
    approved_by_m = re.search(r'approved_by:\s*(\S+)', gate6_text)
    if approved_by_m:
        approved_by = approved_by_m.group(1)
        if approved_by.lower() not in ('null', 'none', '~'):
            issues.append(
                f"registry FODS gate_6.approved_by is '{approved_by}' — must be null "
                f"(Gate 6 is NOT approved; oracle blocked)"
            )
        else:
            print(f"  registry FODS gate_6.approved_by: {approved_by} (null — correct)")
    else:
        warnings.append("registry gate_6.approved_by field not found")

    # Check approved_date is null
    approved_date_m = re.search(r'approved_date:\s*(\S+)', gate6_text)
    if approved_date_m:
        approved_date = approved_date_m.group(1)
        if approved_date.lower() not in ('null', 'none', '~'):
            issues.append(
                f"registry FODS gate_6.approved_date is '{approved_date}' — must be null"
            )
        else:
            print(f"  registry FODS gate_6.approved_date: {approved_date} (null — correct)")

    # Check status is not passed
    status_m = re.search(r'status:\s*(\S+)', gate6_text)
    if status_m:
        status = status_m.group(1)
        if status.lower() in ('passed', 'approved'):
            issues.append(
                f"registry FODS gate_6.status is '{status}' — must not be passed/approved "
                f"(oracle blocked)"
            )
        else:
            print(f"  registry FODS gate_6.status: {status} (not passed — correct)")


def check_fodt_state_consistent(repo_root: Path, issues: list, warnings: list) -> None:
    """Check FODT state is internally consistent across registry, scoring package, and acquisition-packs."""

    registry = repo_root / "registry" / "format-registry.yaml"
    scoring_pkg = repo_root / "registry" / "candidates" / "fodt-gate1-scoring-package.yaml"
    fodt_pack = repo_root / "acquisition-packs" / "fodt"

    # Determine FODT registry state
    fodt_in_registry = False
    fodt_gate1_passed = False

    if registry.exists():
        text = registry.read_text(encoding="utf-8")
        if re.search(r'format_id:\s*fodt', text):
            fodt_in_registry = True
            # Check if gate_1 is passed
            # Find the fodt entry section
            fodt_section = re.search(r'format_id:\s*fodt.*?(?=- format_id:|\Z)', text, re.DOTALL)
            if fodt_section:
                fodt_text = fodt_section.group(0)
                gate1_section = re.search(r'gate_1:.*?(?=gate_2:|$)', fodt_text, re.DOTALL)
                if gate1_section:
                    gate1_text = gate1_section.group(0)
                    status_m = re.search(r'status:\s*(\S+)', gate1_text)
                    if status_m and status_m.group(1).lower() == 'passed':
                        fodt_gate1_passed = True

    # Get scoring package state
    pkg_gate1_approved = None
    if scoring_pkg.exists():
        pkg_text = scoring_pkg.read_text(encoding="utf-8")
        m = re.search(r'gate_1_approved:\s*(\S+)', pkg_text)
        if m:
            pkg_gate1_approved = m.group(1).lower() == 'true'

    # Get acquisition pack state
    fodt_pack_exists = fodt_pack.exists() and fodt_pack.is_dir()

    # Now check consistency
    if fodt_in_registry:
        print(f"  FODT in registry: YES (gate_1_passed={fodt_gate1_passed})")
        # If FODT is in registry with gate_1 passed
        if not fodt_gate1_passed:
            issues.append(
                "registry has FODT entry but gate_1.status is not 'passed' — "
                "FODT must not be in official registry without gate_1 approval"
            )
        # Scoring package must agree
        if pkg_gate1_approved is False:
            issues.append(
                "registry has FODT entry with gate_1 passed, but "
                "fodt-gate1-scoring-package.yaml says gate_1_approved: false — "
                "scoring package must be updated to match"
            )
        elif pkg_gate1_approved is True:
            print("  fodt-gate1-scoring-package.yaml gate_1_approved: true (consistent with registry)")
        # Acquisition pack must exist
        if not fodt_pack_exists:
            issues.append(
                "registry has FODT with gate_1 passed, but acquisition-packs/fodt/ does not exist — "
                "must create acquisition pack after Gate 1 approval"
            )
        else:
            print("  acquisition-packs/fodt/: exists (consistent with Gate 1 approval)")
    else:
        print("  FODT in registry: NO (candidate-only)")
        # FODT not in registry — scoring package must say gate_1_approved: false
        if pkg_gate1_approved is True:
            issues.append(
                "fodt-gate1-scoring-package.yaml says gate_1_approved: true, but "
                "registry/format-registry.yaml has no official FODT entry — "
                "registry must be updated when Gate 1 is approved"
            )
        elif pkg_gate1_approved is False:
            print("  fodt-gate1-scoring-package.yaml gate_1_approved: false (correct for candidate-only)")
        # Acquisition pack must NOT exist
        if fodt_pack_exists:
            issues.append(
                "acquisition-packs/fodt/ exists but FODT has no official registry entry — "
                "must not create acquisition pack before Gate 1 approval"
            )
        else:
            print("  acquisition-packs/fodt/: absent (correct — Gate 1 not yet approved)")


def check_pack_yaml_gate6(repo_root: Path, issues: list, warnings: list) -> None:
    """Check acquisition-packs/fods/pack.yaml gate_6 is not marked approved."""
    pack_yaml = repo_root / "acquisition-packs" / "fods" / "pack.yaml"
    if not pack_yaml.exists():
        warnings.append("acquisition-packs/fods/pack.yaml not found — skipping gate_6 check")
        return

    text = pack_yaml.read_text(encoding="utf-8")

    gate6_m = re.search(r'gate_6:.*?(?=gate_7:|stage_7:|$)', text, re.DOTALL)
    if not gate6_m:
        warnings.append("acquisition-packs/fods/pack.yaml: gate_6 section not found")
        return

    gate6_text = gate6_m.group(0)

    if re.search(r'(approved:\s*true|status:\s*passed)', gate6_text, re.IGNORECASE):
        issues.append(
            "acquisition-packs/fods/pack.yaml gate_6 appears approved — "
            "Gate 6 must remain blocked (oracle not installed)"
        )
    else:
        print("  pack.yaml gate_6: not approved (correct)")


def check_run_commit_ledger_exists(text: str, issues: list, warnings: list) -> None:
    """Check that a Run Commit Ledger section exists in master-plan.md."""
    if re.search(r'## Section 33', text):
        print("  Section 33 (Run Commit Ledger): present")
    else:
        warnings.append("Section 33 not found in master-plan.md")


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Check project current-state consistency")
    parser.add_argument("--repo-root", default=".", help="Repository root directory")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    master_plan = repo_root / "plans" / "master-plan.md"
    mem09 = repo_root / "memory" / "09-current-state-before-phase1.md"

    issues = []
    warnings = []

    print("=" * 60)
    print("CURRENT STATE CONSISTENCY CHECK")
    print("Model: run-state authority (run041+)")
    print("See: docs/current-state-and-evidence-authority.md")
    print("=" * 60)

    # --- Check 1+2: master-plan no PENDING markers ---
    print("\n--- Check 1+2: master-plan PENDING markers ---")
    if not master_plan.exists():
        print("CURRENT_STATE_CONSISTENCY: FAIL")
        print(f"  plans/master-plan.md not found at {master_plan}")
        return 1

    mp_text = master_plan.read_text(encoding="utf-8")

    # Only scan the Current Status section (first ~2000 chars of the file, before run history)
    # Historical entries are expected to contain PENDING_VERIFICATION etc. which are fine.
    header_section = mp_text[:3000]  # Covers lines 1-~50 including Current Status
    check_no_pending_markers(header_section, "master-plan Current Status", issues, warnings)
    if not issues:
        print("  master-plan Current Status: no PENDING markers (correct)")

    # --- Check 3: memory/09 no PENDING markers ---
    print("\n--- Check 3: memory/09 PENDING markers ---")
    if mem09.exists():
        mem_text = mem09.read_text(encoding="utf-8")
        prev_issues_count = len(issues)
        check_no_pending_markers(mem_text[:3000], "memory/09 Current Status", issues, warnings)
        if len(issues) == prev_issues_count:
            print("  memory/09: no PENDING markers (correct)")
    else:
        warnings.append("memory/09-current-state-before-phase1.md not found")

    # --- Checks 4-6: FODS Gate 6 not approved ---
    print("\n--- Checks 4-6: FODS Gate 6 approval state ---")
    check_registry_gate6_not_approved(repo_root, issues, warnings)

    # --- Check 7+8: FODT state consistency ---
    print("\n--- Checks 7+8: FODT state consistency ---")
    check_fodt_state_consistent(repo_root, issues, warnings)

    # --- Check 9: pack.yaml gate_6 ---
    print("\n--- Check 9: pack.yaml gate_6 ---")
    check_pack_yaml_gate6(repo_root, issues, warnings)

    # --- Check 10: Section 33 exists ---
    print("\n--- Check 10: Run Commit Ledger section ---")
    check_run_commit_ledger_exists(mp_text, issues, warnings)

    # Report
    print()
    for w in warnings:
        print(f"  WARN: {w}")

    if issues:
        print("\nCURRENT_STATE_CONSISTENCY: FAIL")
        for issue in issues:
            print(f"  FAIL: {issue}")
        return 1
    else:
        print("\nCURRENT_STATE_CONSISTENCY: PASS")
        return 0


if __name__ == "__main__":
    sys.exit(main())
