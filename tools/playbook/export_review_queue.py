"""
export_review_queue.py — Export a review queue YAML from a dry-run replay report.

Sprint: S-F2F-03 (Dry-Run Replay and Review Queue Export)
Status: ACTIVE — read-only transformation; writes output only to --output path.

AUTHORITY BOUNDARY:
  Review queues CANNOT approve gates, CANNOT replace DEC-034, CANNOT replace
  evidence contracts, CANNOT replace human approval.
  Items with severity 'high' or 'blocker' MUST block apply mode.

CLI:
  python tools/playbook/export_review_queue.py
    --format-id FORMAT_ID
    --dry-run-report DRY_RUN_REPORT.yaml
    --output QUEUE_OUTPUT.yaml   # must target .local/ or external path

  Alternatively, run replay + export in one step via:
    python tools/playbook/replay_acquisition_playbook.py
      --mode export-review-queue ...
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
                    f"EXPORT_ERROR: --output path '{output_path}' targets a committed repo "
                    f"directory. Output must go to .local/ or an external path.",
                    file=sys.stderr,
                )
                sys.exit(2)


def _load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_review_queue(format_id: str, dry_run_report: dict) -> dict:
    """
    Build a review-queue YAML document from a dry-run report.
    Conforms to schemas/playbook/review-queue.schema.json.
    """
    conflicts = dry_run_report.get("conflicts", [])
    playbook_id = dry_run_report.get("playbook_id", "unknown")
    now_str = _now_str()
    queue_id = f"rq-{format_id}-{now_str}"
    run_id = f"s-f2f-03-export-{now_str}"

    items = []
    for i, c in enumerate(conflicts, 1):
        item_id = f"RQ-{i:03d}"
        severity = c.get("severity", "medium")
        blocks_apply = severity in ("high", "blocker")
        items.append({
            "item_id": item_id,
            "format_id": format_id,
            "gate": c.get("gate", 1),
            "operation_id": c.get("operation_id", "unknown"),
            "target_path": c.get("target_path", ""),
            "issue_type": c.get("issue_type", "other"),
            "severity": severity,
            "deterministic_failure_reason": c.get("deterministic_failure_reason", ""),
            "required_action": c.get("required_action", ""),
            "suggested_fix": None,
            "evidence_required": ["manual_inspection"],
            "status": "open",
            "resolution_notes": None,
            "owner_role": "secondary_sprint_owner",
            "blocks_apply_mode": blocks_apply,
            "blocks_gate_progress": blocks_apply,
            "provenance": {
                "created_at": _now_iso(),
                "created_by_sprint": "S-F2F-03",
                "resolved_at": None,
                "resolved_by_sprint": None,
            },
        })

    total = len(items)
    open_count = sum(1 for it in items if it["status"] == "open")
    blocker_count = sum(1 for it in items if it["severity"] == "blocker")
    high_count = sum(1 for it in items if it["severity"] == "high")
    medium_count = sum(1 for it in items if it["severity"] == "medium")
    low_count = sum(1 for it in items if it["severity"] == "low")
    blocks_apply = any(it["blocks_apply_mode"] for it in items if it["status"] == "open")
    blocks_gate = any(it["blocks_gate_progress"] for it in items if it["status"] == "open")

    return {
        "schema_version": "1.0",
        "queue_id": queue_id,
        "run_id": run_id,
        "generated_at": _now_iso(),
        "source_playbook_id": playbook_id,
        "source_format_id": format_id,
        "items": items,
        "summary": {
            "total_items": total,
            "open_items": open_count,
            "blocker_count": blocker_count,
            "high_count": high_count,
            "medium_count": medium_count,
            "low_count": low_count,
            "blocks_apply_mode": blocks_apply,
            "blocks_gate_progress": blocks_gate,
        },
        "governance": {
            "cannot_approve_gates": True,
            "cannot_replace_dec034": True,
            "cannot_replace_evidence_contracts": True,
            "cannot_replace_human_approval": True,
            "high_severity_blocks_apply": True,
            "gate_progress_requires_resolution": True,
            "policy_doc_reference": "docs/governance/playbook-layer.md",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Export a review queue YAML from a dry-run replay report (S-F2F-03). "
            "Output conforms to schemas/playbook/review-queue.schema.json."
        ),
    )
    parser.add_argument("--format-id", required=True, help="Format identifier, e.g. 'fods'.")
    parser.add_argument(
        "--dry-run-report", required=True,
        help="Path to a dry-run report YAML produced by replay_acquisition_playbook.py.",
    )
    parser.add_argument(
        "--output", required=True,
        help="Output path for review queue YAML. Must target .local/ or external path.",
    )

    args = parser.parse_args()
    _guard_output_path(args.output)

    try:
        report = _load_yaml(args.dry_run_report)
    except Exception as e:
        print(f"EXPORT_ERROR: cannot load dry-run report: {e}", file=sys.stderr)
        return 1

    queue = build_review_queue(args.format_id, report)
    total = queue["summary"]["total_items"]

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        yaml.dump(queue, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    if total == 0:
        print("EXPORT_REVIEW_QUEUE: PASS (0 items — clean queue written)")
    else:
        print(f"EXPORT_REVIEW_QUEUE: CONFLICTS ({total} items written)")
    print(f"REVIEW_QUEUE_OUTPUT: {os.path.abspath(args.output)}")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
