#!/usr/bin/env python3
"""
check_current_state_consistency.py — Validate current-state consistency across the project.

PURPOSE:
    Verify that the "Latest commit" recorded in plans/master-plan.md matches the actual
    git HEAD commit. Also validates memory/09, registry gate_6 approval status, FODT
    candidate-only status, and forbidden-path invariants.

USAGE:
    python tools/evidence/check_current_state_consistency.py [--repo-root PATH]

OUTPUT:
    CURRENT_STATE_CONSISTENCY: PASS
    CURRENT_STATE_CONSISTENCY: FAIL

EXIT CODE:
    0 on PASS, 1 on FAIL

CHECKS PERFORMED:
    1. plans/master-plan.md "Current status" header has a "Latest commit: <hash>" entry
    2. Section 33 "Latest commit: <hash>" entry
    3. Both match actual git HEAD (or have PENDING marker if sprint in progress)
    4. memory/09-current-state-before-phase1.md latest commit matches HEAD (or PENDING)
    5. registry/format-registry.yaml gate_6 is NOT approved (approved_by: null)
    6. registry/format-registry.yaml gate_6 approved_date is null
    7. registry/format-registry.yaml has NO official fodt entry (FODT is candidate-only)
    8. registry/candidates/fodt-gate1-scoring-package.yaml gate_1_approved: false
    9. acquisition-packs/fodt/ does NOT exist (FODT has no acquisition pack)
    10. acquisition-packs/fods/pack.yaml gate_6 not marked approved

NOTES:
    - Does NOT auto-fix stale references (fixing is the agent's job per DEC-034)
    - Safe to run at any time (read-only)
    - If master-plan does not exist, reports FAIL with explanation
    - Tolerates "PENDING" pattern (uncommitted sprint in progress)
"""

import re
import subprocess
import sys
from pathlib import Path


def get_git_head(repo_root: Path) -> str | None:
    """Return the current git HEAD short hash (7 chars)."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short=7", "HEAD"],
            capture_output=True, text=True, cwd=repo_root, timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def extract_latest_commit(text: str, context: str) -> tuple[str | None, str]:
    """
    Extract the first 'Latest commit: <hash>' reference from text.
    Returns (hash_or_None, description_of_where_found).
    """
    # Match pattern: Latest commit: <7+ hex chars>
    # Handles both "Latest commit: abc1234" and "**Latest commit:** abc1234" (markdown bold)
    m = re.search(r'Latest commit:[*\s]*([0-9a-f]{7,40})', text, re.IGNORECASE)
    if m:
        return m.group(1)[:7], context
    return None, context


def check_no_pending_run(master_plan_text: str) -> bool:
    """
    Return True if Section 33 contains a PENDING run marker (expected during active sprint).
    This is informational only, not a failure condition.
    """
    s33_match = re.search(r'## Section 33.*?(?=## Section|\Z)', master_plan_text, re.DOTALL)
    if s33_match:
        return 'PENDING' in s33_match.group(0)
    return False


def check_memory_09_commit(repo_root: Path, actual_head: str,
                            issues: list, warnings: list) -> None:
    """Check memory/09 latest commit matches git HEAD or has PENDING marker."""
    mem09 = repo_root / "memory" / "09-current-state-before-phase1.md"
    if not mem09.exists():
        warnings.append("memory/09-current-state-before-phase1.md not found — skipping commit check")
        return

    text = mem09.read_text(encoding="utf-8")

    # Table row pattern: "| Latest commit | <hash> ... |"
    m = re.search(r'\|\s*Latest commit\s*\|\s*([0-9a-f]{7,40})', text, re.IGNORECASE)
    if m:
        mem_commit = m.group(1)[:7]
        print(f"memory/09 latest commit: {mem_commit}")
        # Check for PENDING in the same line or nearby context
        line_start = text.rfind('\n', 0, m.start()) + 1
        line_end = text.find('\n', m.end())
        line_ctx = text[line_start:line_end] if line_end > 0 else text[line_start:]
        if 'PENDING' in line_ctx or 'pending' in line_ctx.lower():
            warnings.append(
                f"memory/09 latest commit ({mem_commit}) has 'pending' marker — "
                f"sprint in progress (expected)"
            )
        elif mem_commit != actual_head:
            issues.append(
                f"memory/09 says '{mem_commit}' but git HEAD is '{actual_head}'"
            )
    else:
        # Check for any PENDING mention
        if 'PENDING' in text or 'pending commit' in text.lower():
            warnings.append(
                "memory/09 latest commit entry not found but 'pending' marker present "
                "— sprint in progress (expected)"
            )
        else:
            warnings.append("memory/09 does not contain a 'Latest commit' table row")


def check_registry_gate6_not_approved(repo_root: Path, issues: list, warnings: list) -> None:
    """Check registry gate_6 is NOT approved (approved_by: null, approved_date: null)."""
    registry = repo_root / "registry" / "format-registry.yaml"
    if not registry.exists():
        warnings.append("registry/format-registry.yaml not found — skipping gate_6 approval check")
        return

    text = registry.read_text(encoding="utf-8")

    # Find gate_6 section and check for non-null approved_by
    gate6_match = re.search(r'gate_6:.*?(?=gate_7:|$)', text, re.DOTALL)
    if not gate6_match:
        warnings.append("registry gate_6 section not found")
        return

    gate6_text = gate6_match.group(0)

    # Check approved_by is null
    approved_by_m = re.search(r'approved_by:\s*(\S+)', gate6_text)
    if approved_by_m:
        approved_by = approved_by_m.group(1)
        if approved_by.lower() not in ('null', 'none', '~'):
            issues.append(
                f"registry gate_6.approved_by is '{approved_by}' but should be null "
                f"(Gate 6 is NOT approved — oracle blocked)"
            )
        else:
            print(f"registry gate_6.approved_by: {approved_by} (null — correct)")
    else:
        warnings.append("registry gate_6.approved_by field not found")

    # Check approved_date is null
    approved_date_m = re.search(r'approved_date:\s*(\S+)', gate6_text)
    if approved_date_m:
        approved_date = approved_date_m.group(1)
        if approved_date.lower() not in ('null', 'none', '~'):
            issues.append(
                f"registry gate_6.approved_date is '{approved_date}' but should be null"
            )
        else:
            print(f"registry gate_6.approved_date: {approved_date} (null — correct)")


def check_fodt_candidate_only(repo_root: Path, issues: list, warnings: list) -> None:
    """Check FODT is candidate-only: no official registry entry, gate_1_approved: false,
    no acquisition-packs/fodt/ directory."""

    # 1. No official FODT entry in format-registry.yaml
    registry = repo_root / "registry" / "format-registry.yaml"
    if registry.exists():
        text = registry.read_text(encoding="utf-8")
        # Look for format_id: fodt as an official entry (not in candidates/ or comments)
        if re.search(r'^\s*format_id:\s*fodt', text, re.MULTILINE):
            issues.append(
                "registry/format-registry.yaml contains an official 'format_id: fodt' entry "
                "— FODT must remain candidate-only until Gate 1 is human-approved"
            )
        else:
            print("registry/format-registry.yaml: no official fodt entry (candidate-only — correct)")

    # 2. fodt-gate1-scoring-package.yaml gate_1_approved: false
    scoring_pkg = repo_root / "registry" / "candidates" / "fodt-gate1-scoring-package.yaml"
    if scoring_pkg.exists():
        pkg_text = scoring_pkg.read_text(encoding="utf-8")
        m = re.search(r'gate_1_approved:\s*(\S+)', pkg_text)
        if m:
            val = m.group(1)
            if val.lower() != 'false':
                issues.append(
                    f"fodt-gate1-scoring-package.yaml gate_1_approved: {val} "
                    f"(should be false — no human approval yet)"
                )
            else:
                print(f"fodt-gate1-scoring-package.yaml gate_1_approved: false (correct)")
        else:
            warnings.append("fodt-gate1-scoring-package.yaml: gate_1_approved field not found")
    else:
        warnings.append(
            "registry/candidates/fodt-gate1-scoring-package.yaml not found "
            "— skipping gate_1_approved check"
        )

    # 3. No acquisition-packs/fodt/ directory
    fodt_pack = repo_root / "acquisition-packs" / "fodt"
    if fodt_pack.exists() and fodt_pack.is_dir():
        issues.append(
            "acquisition-packs/fodt/ directory exists — FODT must not have an acquisition pack "
            "until Gate 1 is human-approved"
        )
    else:
        print("acquisition-packs/fodt/: absent (correct — FODT is candidate-only)")


def check_pack_yaml_gate6(repo_root: Path, issues: list, warnings: list) -> None:
    """Check acquisition-packs/fods/pack.yaml gate_6 is not marked approved."""
    pack_yaml = repo_root / "acquisition-packs" / "fods" / "pack.yaml"
    if not pack_yaml.exists():
        warnings.append("acquisition-packs/fods/pack.yaml not found — skipping gate_6 check")
        return

    text = pack_yaml.read_text(encoding="utf-8")

    # Find gate_6 section
    gate6_m = re.search(r'gate_6:.*?(?=gate_7:|stage_7:|$)', text, re.DOTALL)
    if not gate6_m:
        warnings.append("acquisition-packs/fods/pack.yaml: gate_6 section not found")
        return

    gate6_text = gate6_m.group(0)

    # Check it doesn't say "approved: true" or "status: passed"
    if re.search(r'(approved:\s*true|status:\s*passed)', gate6_text, re.IGNORECASE):
        issues.append(
            "acquisition-packs/fods/pack.yaml gate_6 appears approved — "
            "should still be blocked (oracle not installed)"
        )
    else:
        print("acquisition-packs/fods/pack.yaml gate_6: not approved (correct)")


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Check project current-state consistency")
    parser.add_argument("--repo-root", default=".", help="Repository root directory")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    master_plan = repo_root / "plans" / "master-plan.md"

    issues = []
    warnings = []

    # 1. Get actual git HEAD
    actual_head = get_git_head(repo_root)
    if actual_head is None:
        print("CURRENT_STATE_CONSISTENCY: FAIL")
        print("  Cannot determine git HEAD — not a git repository or git not available")
        return 1

    print(f"Git HEAD: {actual_head}")

    # 2. Read master-plan
    if not master_plan.exists():
        print("CURRENT_STATE_CONSISTENCY: FAIL")
        print(f"  plans/master-plan.md not found at {master_plan}")
        return 1

    text = master_plan.read_text(encoding="utf-8")

    # 3. Check "Current status" header line
    header_match = re.search(r'\*\*Current status:\*\*.*?Latest commit:\s*([0-9a-f]{7,40})', text)
    if header_match:
        header_commit = header_match.group(1)[:7]
        print(f"Current status header commit: {header_commit}")
        if header_commit != actual_head:
            issues.append(
                f"Current status header says '{header_commit}' but git HEAD is '{actual_head}'"
            )
    else:
        warnings.append("Current status header does not contain a 'Latest commit: <hash>' entry")

    # 4. Check Section 33
    s33_match = re.search(r'## Section 33.*?(?=## Section \d|\Z)', text, re.DOTALL)
    if s33_match:
        s33_text = s33_match.group(0)
        s33_commit, _ = extract_latest_commit(s33_text, "Section 33")
        if s33_commit:
            print(f"Section 33 latest commit: {s33_commit}")
            # Section 33 may legitimately say PENDING during an active sprint
            pending_in_s33 = 'PENDING' in s33_text
            if s33_commit != actual_head and not pending_in_s33:
                issues.append(
                    f"Section 33 says '{s33_commit}' but git HEAD is '{actual_head}' "
                    f"(no PENDING marker found — stale reference)"
                )
            elif s33_commit != actual_head and pending_in_s33:
                warnings.append(
                    f"Section 33 latest commit ({s33_commit}) is not HEAD ({actual_head}) "
                    f"but PENDING sprint marker is present — this is expected during active sprint"
                )
        else:
            warnings.append("Section 33 does not contain a 'Latest commit: <hash>' entry")
    else:
        warnings.append("Section 33 not found in master-plan.md")

    # 5. Check memory/09
    print()
    print("--- memory/09 check ---")
    check_memory_09_commit(repo_root, actual_head, issues, warnings)

    # 6. Check registry gate_6 not approved
    print()
    print("--- registry gate_6 approval check ---")
    check_registry_gate6_not_approved(repo_root, issues, warnings)

    # 7. Check FODT candidate-only invariants
    print()
    print("--- FODT candidate-only check ---")
    check_fodt_candidate_only(repo_root, issues, warnings)

    # 8. Check pack.yaml gate_6
    print()
    print("--- pack.yaml gate_6 check ---")
    check_pack_yaml_gate6(repo_root, issues, warnings)

    # Report
    print()
    for w in warnings:
        print(f"  WARN: {w}")

    if issues:
        print("CURRENT_STATE_CONSISTENCY: FAIL")
        for issue in issues:
            print(f"  FAIL: {issue}")
        return 1
    else:
        print("CURRENT_STATE_CONSISTENCY: PASS")
        return 0


if __name__ == "__main__":
    sys.exit(main())
