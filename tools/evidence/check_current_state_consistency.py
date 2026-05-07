#!/usr/bin/env python3
"""
check_current_state_consistency.py — Validate current-state consistency in master-plan.

PURPOSE:
    Verify that the "Latest commit" recorded in plans/master-plan.md matches the actual
    git HEAD commit. Prevents stale commit references from persisting after a final commit
    that updates only the plan file (a common pattern where the final commit hash is
    recorded before the commit itself is made, creating a one-commit lag).

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
    3. Both match actual git HEAD

NOTES:
    - Does NOT auto-fix stale references (fixing is the agent's job per DEC-034)
    - Safe to run at any time (read-only)
    - If master-plan does not exist, reports FAIL with explanation
    - Tolerates "run039 commits: PENDING" pattern (uncommitted sprint in progress)
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


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Check master-plan current-state consistency")
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

    # 5. Report
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
