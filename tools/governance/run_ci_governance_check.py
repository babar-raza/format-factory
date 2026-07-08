#!/usr/bin/env python3
"""
run_ci_governance_check.py — CI governance validators wrapper.

Replaces inline python -c block in governance-check CI job.
Uses pathlib for robust path resolution (no fragile relative sys.path).

Exit codes:
    0 — governance validators pass (blocks_sprint=False)
    1 — one or more validators block the sprint (blocks_sprint=True)
    2 — import error or configuration error
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SUPERVISOR_PATH = REPO_ROOT / "tools" / "supervisor"
sys.path.insert(0, str(_SUPERVISOR_PATH))

try:
    from governance_validators import run_all_governance_validators
except ImportError as exc:
    print(
        f"ERROR: Cannot import governance_validators from {_SUPERVISOR_PATH}: {exc}",
        file=sys.stderr,
    )
    sys.exit(2)

_CI_DECLARATION = {
    "run_id": "ci-governance-check",
    "sprint_id": "ci",
    "declared_scope": "CI_CHECK",
    "planned_work_items": [],
    "evidence_root": ".local/evidences/",
    "worker_self_verdict": "PASS",
    "worker_self_grade": "PASS",
    "start_time": "1970-01-01T00:00:00",
    "end_time": "1970-01-01T00:00:01",
    "git_head_start": "HEAD",
    "git_head_end": "HEAD",
    "git_status_final": "clean",
    "declared_scope_items": [],
    "completed_work_items": [],
    "incomplete_work_items": [],
    "changed_files": [],
    "tests_run": [],
    "test_results": {},
    "reports_created": [],
    "next_recommended_work": "continue",
    "acceptance_criteria": "CI governance check passes",
}

result = run_all_governance_validators(_CI_DECLARATION)

# Print FAIL details for CI debugging
_fails = [v for v in result.get("validators", []) if v.get("result") == "FAIL"]
for _f in _fails:
    print(
        f"  FAIL: {_f.get('validator', '?')} — {_f.get('summary', '')[:200]}"
    )

print(
    f"Governance validators: fail={result['fail_count']} "
    f"warn={result['warn_count']} pass={result['pass_count']} "
    f"blocks={result['blocks_sprint']} total={result.get('ran_count', '?')}"
)
sys.exit(1 if result["blocks_sprint"] else 0)
