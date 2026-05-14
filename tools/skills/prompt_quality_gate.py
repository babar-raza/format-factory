"""
prompt_quality_gate.py -- Phase R4 Deliverable (Lane B)

10-criterion validation of generated execution handoff prompts.

PURPOSE:
  Accept a prompt string (from swarm_prompt_generator.py) and validate it
  against 10 required criteria. Returns PASS, PASS_WITH_WARNINGS, or FAIL.

CRITERIA:
  1.  EXECUTION MODE header exists
  2.  Sprint ID exists
  3.  Authority context (READ FIRST) exists
  4.  Lane ownership model exists
  5.  Forbidden commands absent (stash/reset/clean/push/force)
  6.  No autonomous gate approval language
  7.  No commercial readiness overclaim
  8.  No implementation execution instructions (dry-run only)
  9.  Evidence requirements (contract path, BUNDLE_VALIDATION) present
  10. Deterministic final format (EVIDENCE_BUNDLE: line) present

SEVERITY:
  Criteria 1-10 are BLOCKER except criterion 9 which is WARNING.
  Any BLOCKER failure → FAIL.
  Only WARNING failures → PASS_WITH_WARNINGS.
  All pass → PASS.

Authority: AGENTS.md AF9-AF15 | GOVERNANCE.md 26.8-26.13
           templates/commercial-sprint/lane-library.yaml (prompt_quality_gate_criteria)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Forbidden command patterns that must NOT appear in generated prompts
FORBIDDEN_COMMAND_PATTERNS = [
    r"git\s+stash",
    r"git\s+reset\s+--hard",
    r"git\s+restore\s+\.",
    r"git\s+clean\s+",
    r"git\s+push\s+--force",
    r"git\s+push\s+-f\b",
    r"git\s+add\s+-A\b",
    r"git\s+add\s+\.\b",
]

# Forbidden content patterns (gate approval / commercial claim language)
FORBIDDEN_GATE_APPROVAL_PATTERNS = [
    r"gate\s*11\s+(?:is\s+)?(?:now\s+)?approved",
    r"gate_11.*approved.*true",
    r"gate.*self.?approv",
    r"human.*gate.*approv",
    r"gate.*status.*passed.*11",
]

FORBIDDEN_COMMERCIAL_CLAIM_PATTERNS = [
    r"commercial_product_ready.*true",
    r"commercial.*product.*ready.*=.*true",
    r"commercially.*ready",
    r"production.*ready.*true",
]

FORBIDDEN_IMPLEMENTATION_EXECUTION_PATTERNS = [
    r"execute.*implementation.*now",
    r"implement.*immediately.*without.*review",
    r"autonomous.*implementation.*authorized",
    r"proceed.*without.*human",
]

# Required patterns that MUST appear in a valid prompt
REQUIRED_EXECUTION_MODE_PATTERN = r"EXECUTION MODE"
REQUIRED_SPRINT_ID_PATTERN = r"sprint.{0,50}id|CONWAY-|SPRINT-\d{3}"
REQUIRED_AUTHORITY_CONTEXT_PATTERN = r"READ FIRST|AGENTS\.md|authority.*context"
REQUIRED_LANE_OWNERSHIP_PATTERN = r"LANE.*OWNERSHIP|Coordinator owns|lane ownership"
REQUIRED_EVIDENCE_PATTERN = r"EVIDENCE_BUNDLE|evidence.*contract|BUNDLE_VALIDATION"
REQUIRED_FINAL_FORMAT_PATTERN = r"EVIDENCE_BUNDLE:\s*<|EVIDENCE_BUNDLE: C:\\"


def _check_patterns(text: str, patterns: list[str]) -> list[str]:
    """
    Return list of patterns found in text in a POSITIVE (non-negated) context.
    Lines that start with negating prefixes (No, NOT, never, do not, avoid, forbid,
    must not, BLOCKED, - No) are excluded from matching to prevent false positives
    when prohibition text includes the forbidden pattern.
    """
    # Negation prefixes at start of line (strip leading whitespace/bullet)
    NEGATION_PREFIXES = re.compile(
        r"^\s*[-*#]?\s*"
        r"(no\b|no_\w|not\b|never\b|do\s+not\b|avoid\b|forbid|blocked|must\s+not|"
        r"without\b|absent\b|n/a\b|none\b)",
        re.IGNORECASE,
    )
    lines = text.splitlines()
    non_negated_text = "\n".join(
        line for line in lines
        if not NEGATION_PREFIXES.match(line)
    )

    found = []
    for pat in patterns:
        if re.search(pat, non_negated_text, re.IGNORECASE):
            found.append(pat)
    return found


def _has_pattern(text: str, pattern: str) -> bool:
    return bool(re.search(pattern, text, re.IGNORECASE))


def validate_prompt(prompt: str) -> dict:
    """
    Validate a generated execution handoff prompt against 10 quality criteria.

    Parameters
    ----------
    prompt : str
        The generated prompt text to validate.

    Returns
    -------
    dict with:
      status: "PASS" | "PASS_WITH_WARNINGS" | "FAIL"
      score: int (0-10)
      checks: list[dict]  -- per-criterion results
      blocker_count: int
      warning_count: int
      pass_count: int
    """
    if not prompt or not isinstance(prompt, str):
        return {
            "status": "FAIL",
            "score": 0,
            "checks": [{"id": 0, "name": "prompt_not_empty", "status": "FAIL",
                         "severity": "BLOCKER", "detail": "Prompt is None or empty"}],
            "blocker_count": 1,
            "warning_count": 0,
            "pass_count": 0,
        }

    checks = []

    def _add_check(check_id: int, name: str, passed: bool, severity: str, detail: str):
        checks.append({
            "id": check_id,
            "name": name,
            "status": "PASS" if passed else severity,
            "severity": severity,
            "detail": detail,
        })

    # Criterion 1: EXECUTION MODE header
    _add_check(
        1, "execution_mode_header",
        _has_pattern(prompt, REQUIRED_EXECUTION_MODE_PATTERN),
        "BLOCKER",
        "Prompt must contain 'EXECUTION MODE' header",
    )

    # Criterion 2: Sprint ID
    _add_check(
        2, "sprint_id_present",
        _has_pattern(prompt, REQUIRED_SPRINT_ID_PATTERN),
        "BLOCKER",
        "Prompt must contain a sprint ID (e.g. CONWAY-*, SPRINT-NNN)",
    )

    # Criterion 3: Authority context (READ FIRST)
    _add_check(
        3, "authority_context_present",
        _has_pattern(prompt, REQUIRED_AUTHORITY_CONTEXT_PATTERN),
        "BLOCKER",
        "Prompt must include READ FIRST / authority context section",
    )

    # Criterion 4: Lane ownership model
    _add_check(
        4, "lane_ownership_present",
        _has_pattern(prompt, REQUIRED_LANE_OWNERSHIP_PATTERN),
        "BLOCKER",
        "Prompt must include lane ownership model",
    )

    # Criterion 5: Forbidden commands absent
    forbidden_found = _check_patterns(prompt, FORBIDDEN_COMMAND_PATTERNS)
    _add_check(
        5, "no_forbidden_git_commands",
        len(forbidden_found) == 0,
        "BLOCKER",
        f"Forbidden git commands found: {forbidden_found}" if forbidden_found
        else "No forbidden git commands found",
    )

    # Criterion 6: No autonomous gate approval
    gate_approval_found = _check_patterns(prompt, FORBIDDEN_GATE_APPROVAL_PATTERNS)
    _add_check(
        6, "no_gate_approval_language",
        len(gate_approval_found) == 0,
        "BLOCKER",
        f"Gate approval language found: {gate_approval_found}" if gate_approval_found
        else "No gate approval language found",
    )

    # Criterion 7: No commercial readiness overclaim
    commercial_found = _check_patterns(prompt, FORBIDDEN_COMMERCIAL_CLAIM_PATTERNS)
    _add_check(
        7, "no_commercial_readiness_claim",
        len(commercial_found) == 0,
        "BLOCKER",
        f"Commercial readiness claim found: {commercial_found}" if commercial_found
        else "No commercial readiness claim found",
    )

    # Criterion 8: No autonomous implementation execution instructions
    impl_exec_found = _check_patterns(prompt, FORBIDDEN_IMPLEMENTATION_EXECUTION_PATTERNS)
    _add_check(
        8, "no_autonomous_implementation_execution",
        len(impl_exec_found) == 0,
        "BLOCKER",
        f"Autonomous implementation execution language: {impl_exec_found}" if impl_exec_found
        else "No autonomous implementation execution language",
    )

    # Criterion 9: Evidence requirements present (WARNING not BLOCKER)
    _add_check(
        9, "evidence_requirements_present",
        _has_pattern(prompt, REQUIRED_EVIDENCE_PATTERN),
        "WARNING",
        "Prompt should reference evidence contract path and BUNDLE_VALIDATION",
    )

    # Criterion 10: Deterministic final format (EVIDENCE_BUNDLE: line)
    _add_check(
        10, "deterministic_final_format",
        _has_pattern(prompt, REQUIRED_FINAL_FORMAT_PATTERN),
        "BLOCKER",
        "Prompt must include 'EVIDENCE_BUNDLE: <path>' as final format instruction",
    )

    # Tally results
    blocker_count = sum(1 for c in checks if c["status"] == "BLOCKER")
    warning_count = sum(1 for c in checks if c["status"] == "WARNING")
    pass_count = sum(1 for c in checks if c["status"] == "PASS")

    if blocker_count > 0:
        status = "FAIL"
    elif warning_count > 0:
        status = "PASS_WITH_WARNINGS"
    else:
        status = "PASS"

    return {
        "status": status,
        "score": pass_count,
        "checks": checks,
        "blocker_count": blocker_count,
        "warning_count": warning_count,
        "pass_count": pass_count,
    }


def main():
    import argparse
    import json
    parser = argparse.ArgumentParser(
        description="Prompt quality gate — validate generated execution prompts"
    )
    parser.add_argument("prompt_file", nargs="?", help="Path to prompt file to validate")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    if args.prompt_file:
        prompt_text = Path(args.prompt_file).read_text(encoding="utf-8")
    else:
        print("No prompt file provided. Running against a minimal test prompt.")
        prompt_text = "EXECUTION MODE — TEST-SPRINT-001\nREAD FIRST: AGENTS.md\n"

    result = validate_prompt(prompt_text)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print(f"\n=== Prompt Quality Gate ===")
    print(f"  STATUS:   {result['status']}")
    print(f"  SCORE:    {result['score']}/10")
    print(f"  BLOCKERS: {result['blocker_count']}")
    print(f"  WARNINGS: {result['warning_count']}")
    print(f"\n  Per-criterion results:")
    for check in result["checks"]:
        icon = "PASS" if check["status"] == "PASS" else check["status"]
        print(f"    [{icon}] #{check['id']} {check['name']}: {check['detail']}")


if __name__ == "__main__":
    main()
