"""
diff_playbook_outputs.py — Compare two dry-run replay reports (read-only diff).

Sprint: S-F2F-03 (Dry-Run Replay and Review Queue Export)
Status: ACTIVE — read-only comparison; no file writes unless --output is specified.

AUTHORITY BOUNDARY:
  Diff output is INFORMATIONAL ONLY. It does not approve any gate, replace DEC-034,
  or replace human approval.

CLI:
  python tools/playbook/diff_playbook_outputs.py
    --baseline REPORT_A.yaml
    --current REPORT_B.yaml
    [--output DIFF_REPORT.yaml]   # optional; must target .local/ or external path
    [--format-id FORMAT_ID]       # optional filter
"""

import argparse
import datetime
import os
import sys

import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_UTC = datetime.timezone.utc


def _now_iso() -> str:
    return datetime.datetime.now(_UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _now_str() -> str:
    return datetime.datetime.now(_UTC).strftime("%Y%m%d-%H%M%S")

_COMMITTED_REPO_PREFIXES = (
    "src/", "tools/", "schemas/", "plans/", "taskcards/", "docs/",
    "tests/", "samples/", "acquisition-packs/", "registry/", "reports/", "prototypes/",
)


def _guard_output_path(output_path: str) -> None:
    abs_out = os.path.abspath(output_path)
    repo_abs = os.path.abspath(REPO_ROOT)
    if abs_out.startswith(repo_abs):
        rel = os.path.relpath(abs_out, repo_abs).replace("\\", "/")
        for prefix in _COMMITTED_REPO_PREFIXES:
            if rel.startswith(prefix):
                print(
                    f"DIFF_ERROR: --output path '{output_path}' targets a committed repo "
                    f"directory. Output must go to .local/ or an external path.",
                    file=sys.stderr,
                )
                sys.exit(2)


def _load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _index_by_op(report: dict) -> dict:
    """Return dict keyed by operation_id from operation_results."""
    results = report.get("operation_results", [])
    return {r["operation_id"]: r for r in results}


def _index_conflicts(report: dict) -> dict:
    """Return dict keyed by (operation_id, target_path) from conflicts."""
    idx = {}
    for c in report.get("conflicts", []):
        key = (c.get("operation_id"), c.get("target_path"))
        idx[key] = c
    return idx


def diff_reports(baseline: dict, current: dict) -> dict:
    """
    Compare two dry-run replay reports.
    Returns a diff summary dict.
    """
    baseline_ops = _index_by_op(baseline)
    current_ops = _index_by_op(current)
    baseline_conflicts = _index_conflicts(baseline)
    current_conflicts = _index_conflicts(current)

    all_op_ids = sorted(set(baseline_ops) | set(current_ops))
    op_diffs = []

    for op_id in all_op_ids:
        b = baseline_ops.get(op_id)
        c = current_ops.get(op_id)
        if b is None:
            op_diffs.append({"operation_id": op_id, "change": "added_in_current"})
        elif c is None:
            op_diffs.append({"operation_id": op_id, "change": "removed_in_current"})
        elif b["status"] != c["status"]:
            op_diffs.append({
                "operation_id": op_id,
                "change": "status_changed",
                "baseline_status": b["status"],
                "current_status": c["status"],
            })
        elif b.get("conflict_count", 0) != c.get("conflict_count", 0):
            op_diffs.append({
                "operation_id": op_id,
                "change": "conflict_count_changed",
                "baseline_conflict_count": b.get("conflict_count", 0),
                "current_conflict_count": c.get("conflict_count", 0),
            })
        else:
            op_diffs.append({"operation_id": op_id, "change": "unchanged"})

    all_conflict_keys = sorted(set(baseline_conflicts) | set(current_conflicts))
    conflict_diffs = []
    for key in all_conflict_keys:
        op_id, target = key
        b_c = baseline_conflicts.get(key)
        c_c = current_conflicts.get(key)
        if b_c is None:
            conflict_diffs.append({
                "operation_id": op_id, "target_path": target,
                "change": "new_conflict_in_current",
                "severity": c_c.get("severity"),
            })
        elif c_c is None:
            conflict_diffs.append({
                "operation_id": op_id, "target_path": target,
                "change": "conflict_resolved_in_current",
                "baseline_severity": b_c.get("severity"),
            })
        elif b_c.get("severity") != c_c.get("severity"):
            conflict_diffs.append({
                "operation_id": op_id, "target_path": target,
                "change": "severity_changed",
                "baseline_severity": b_c.get("severity"),
                "current_severity": c_c.get("severity"),
            })
        else:
            conflict_diffs.append({
                "operation_id": op_id, "target_path": target,
                "change": "unchanged",
            })

    regressions = [d for d in op_diffs if d["change"] in ("status_changed",) and
                   d.get("current_status") == "CONFLICT" and d.get("baseline_status") == "PASS"]
    improvements = [d for d in op_diffs if d["change"] in ("status_changed",) and
                    d.get("current_status") == "PASS" and d.get("baseline_status") == "CONFLICT"]
    new_conflicts = [d for d in conflict_diffs if d["change"] == "new_conflict_in_current"]
    resolved_conflicts = [d for d in conflict_diffs if d["change"] == "conflict_resolved_in_current"]

    overall = "UNCHANGED"
    if regressions or new_conflicts:
        overall = "REGRESSION"
    elif improvements or resolved_conflicts:
        overall = "IMPROVEMENT"

    return {
        "diff_generated_at": _now_iso(),
        "baseline_playbook_id": baseline.get("playbook_id"),
        "current_playbook_id": current.get("playbook_id"),
        "overall_diff": overall,
        "regression_count": len(regressions),
        "improvement_count": len(improvements),
        "new_conflict_count": len(new_conflicts),
        "resolved_conflict_count": len(resolved_conflicts),
        "operation_diffs": op_diffs,
        "conflict_diffs": conflict_diffs,
        "authority": "INFORMATIONAL ONLY — diff does not approve gates or replace DEC-034.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare two dry-run replay reports (read-only diff). S-F2F-03.",
    )
    parser.add_argument("--baseline", required=True, help="Baseline replay report YAML.")
    parser.add_argument("--current", required=True, help="Current replay report YAML.")
    parser.add_argument(
        "--output", default=None,
        help="Optional output path for diff report YAML. Must target .local/ or external path.",
    )
    parser.add_argument("--format-id", default=None, help="Optional format_id filter.")

    args = parser.parse_args()

    if args.output:
        _guard_output_path(args.output)

    try:
        baseline = _load_yaml(args.baseline)
    except Exception as e:
        print(f"DIFF_ERROR: cannot load baseline: {e}", file=sys.stderr)
        return 1

    try:
        current = _load_yaml(args.current)
    except Exception as e:
        print(f"DIFF_ERROR: cannot load current: {e}", file=sys.stderr)
        return 1

    result = diff_reports(baseline, current)

    # Print summary to stdout
    print(f"DIFF_OVERALL: {result['overall_diff']}")
    print(f"  Regressions:        {result['regression_count']}")
    print(f"  Improvements:       {result['improvement_count']}")
    print(f"  New conflicts:      {result['new_conflict_count']}")
    print(f"  Resolved conflicts: {result['resolved_conflict_count']}")

    changed = [d for d in result["operation_diffs"] if d["change"] != "unchanged"]
    if changed:
        print(f"\nChanged operations ({len(changed)}):")
        for d in changed:
            print(f"  {d['operation_id']}: {d['change']}")

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            yaml.dump(result, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print(f"\nDIFF_OUTPUT: {os.path.abspath(args.output)}")

    return 0 if result["overall_diff"] != "REGRESSION" else 1


if __name__ == "__main__":
    sys.exit(main())
