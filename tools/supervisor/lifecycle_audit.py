"""
lifecycle_audit.py — Product-track post-execution lifecycle audit module.

Reads current system state and produces a structured audit verdict: does another
plan iteration need to happen?

Reference pattern: tools/supervisor/machinery_audit.py (Track M equivalent).

Output: .local/supervisor/lifecycle-audit-results.json

CLI:
    python tools/supervisor/lifecycle_audit.py \
      --mission-id MACH-LIF-FORENSICS-20260623 \
      --sprint-id TC-LIF-001 \
      [--check-mission-complete]

Exit codes:
    0 — AUDIT_PASS or MISSION_COMPLETE
    1 — AUDIT_REQUIRES_ITERATION
    2 — AUDIT_BLOCKED_EXTERNAL
    3 — error

Created: 2026-06-23
Task: TC-UNIFIED-010 (agile-munching-quasar TC-LIF-002)
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DEFAULT_REPO_ROOT = Path(__file__).parent.parent.parent
_SIGNAL_PATH_REL = ".local/supervisor/continuation-signal.json"
_EVIDENCE_REVIEW_REL = "reports/supervisor/evidence-review.md"
_PRODUCT_MISSION_LEDGER_REL = ".local/supervisor/product-mission-ledger.json"
_OUTPUT_PATH_REL = ".local/supervisor/lifecycle-audit-results.json"

_EXTERNAL_GATE_KEYWORDS = [
    "push_credentials",
    "gate_11",
    "g11",
    "publication_credentials",
    "external_gate",
]


# ---------------------------------------------------------------------------
# Core audit function
# ---------------------------------------------------------------------------


def run_lifecycle_audit(
    repo_root: Path | None = None,
    mission_id: str | None = None,
    sprint_id: str | None = None,
) -> dict:
    """Read current system state and produce a structured audit verdict.

    Returns a dict conforming to the lifecycle-audit-results.json schema.
    Always writes output to .local/supervisor/lifecycle-audit-results.json.
    """
    if repo_root is None:
        repo_root = _DEFAULT_REPO_ROOT
    repo_root = Path(repo_root)

    findings: list[dict] = []
    rework_items: list[str] = []
    open_gaps: list[str] = []

    # ------------------------------------------------------------------
    # 1. Read continuation signal
    # ------------------------------------------------------------------
    signal_path = repo_root / _SIGNAL_PATH_REL
    signal: dict = {}
    if signal_path.exists():
        try:
            signal = json.loads(signal_path.read_text(encoding="utf-8"))
        except Exception as exc:
            findings.append({
                "finding_id": "FIND-SIG-001",
                "type": "SIGNAL_UNREADABLE",
                "severity": "HIGH",
                "description": f"continuation-signal.json unreadable: {exc}",
                "source_file": str(signal_path),
                "recommended_action": "Investigate signal file integrity",
            })

    raw_rework: list[str] = signal.get("rework_items", [])
    rework_items = list(raw_rework)
    govblock_resolved_by = signal.get("govblock_resolved_by")
    autonomous_continue = signal.get("autonomous_continue", True)

    # ------------------------------------------------------------------
    # 2. Check for structural GOV_BLOCK
    # ------------------------------------------------------------------
    govblock_items = [
        item for item in raw_rework
        if "monolith_detection_validator" in item or "GOV_BLOCK" in item
    ]
    if govblock_items and not govblock_resolved_by:
        findings.append({
            "finding_id": "FIND-GOV-001",
            "type": "GOVBLOCK_PRESENT",
            "severity": "CRITICAL",
            "description": (
                f"GOV_BLOCK item(s) in rework_items with no govblock_resolved_by: {govblock_items}"
            ),
            "source_file": str(signal_path),
            "recommended_action": "Run analytics separation or LOC reduction, then set govblock_resolved_by",
        })

    # ------------------------------------------------------------------
    # 3. Check autonomous_continue flag
    # ------------------------------------------------------------------
    if not autonomous_continue:
        # Distinguish external gate vs regular block
        stop_reason = signal.get("stop_reason", "")
        if any(kw in stop_reason.lower() for kw in _EXTERNAL_GATE_KEYWORDS):
            findings.append({
                "finding_id": "FIND-EXT-001",
                "type": "EXTERNAL_GATE_BLOCKING",
                "severity": "CRITICAL",
                "description": f"Continuation blocked by external gate: {stop_reason}",
                "source_file": str(signal_path),
                "recommended_action": "Requires human intervention for external gate",
            })
        else:
            findings.append({
                "finding_id": "FIND-CONT-001",
                "type": "CONTINUATION_BLOCKED",
                "severity": "HIGH",
                "description": f"autonomous_continue=false, stop_reason={stop_reason!r}",
                "source_file": str(signal_path),
                "recommended_action": "Resolve rework_items and re-run autonomous cycle",
            })

    # ------------------------------------------------------------------
    # 4. Check evidence-review.md for ACCEPTED_WITH_REWORK
    # ------------------------------------------------------------------
    evidence_review_path = repo_root / _EVIDENCE_REVIEW_REL
    if evidence_review_path.exists():
        try:
            review_text = evidence_review_path.read_text(encoding="utf-8")
            if "ACCEPTED_WITH_REWORK" in review_text:
                findings.append({
                    "finding_id": "FIND-REV-001",
                    "type": "REWORK_PENDING",
                    "severity": "MEDIUM",
                    "description": "evidence-review.md contains ACCEPTED_WITH_REWORK status",
                    "source_file": str(evidence_review_path),
                    "recommended_action": "Address rework items from last autonomous cycle",
                })
        except Exception:
            pass

    # ------------------------------------------------------------------
    # 5. Check product mission ledger (optional — may not exist yet)
    # ------------------------------------------------------------------
    mission_ledger_path = repo_root / _PRODUCT_MISSION_LEDGER_REL
    if mission_ledger_path.exists():
        try:
            ledger = json.loads(mission_ledger_path.read_text(encoding="utf-8"))
            open_gaps = [
                g["gap_id"] for g in ledger.get("gaps", [])
                if g.get("status") not in ("closed", "CLOSED", "resolved", "RESOLVED")
            ]
            if open_gaps:
                findings.append({
                    "finding_id": "FIND-GAP-001",
                    "type": "OPEN_GAPS",
                    "severity": "MEDIUM",
                    "description": f"{len(open_gaps)} open gap(s) in product mission ledger",
                    "source_file": str(mission_ledger_path),
                    "recommended_action": "Close open gaps before marking mission complete",
                })
        except Exception:
            pass

    # ------------------------------------------------------------------
    # 6. Compute overall verdict
    # ------------------------------------------------------------------
    has_external_gate = any(f["type"] == "EXTERNAL_GATE_BLOCKING" for f in findings)
    has_govblock = any(f["type"] == "GOVBLOCK_PRESENT" for f in findings)
    has_continuation_blocked = any(f["type"] == "CONTINUATION_BLOCKED" for f in findings)
    has_rework_pending = any(f["type"] == "REWORK_PENDING" for f in findings)
    has_open_gaps = bool(open_gaps)

    if has_external_gate:
        verdict = "AUDIT_BLOCKED_EXTERNAL"
    elif has_govblock or has_continuation_blocked or has_rework_pending or has_open_gaps:
        verdict = "AUDIT_REQUIRES_ITERATION"
    else:
        verdict = "AUDIT_PASS"

    next_iteration_required = verdict == "AUDIT_REQUIRES_ITERATION"
    mission_complete = verdict == "AUDIT_PASS" and not open_gaps

    if verdict == "AUDIT_PASS" and not open_gaps:
        recommended_action = "MISSION_COMPLETE"
    elif has_external_gate:
        recommended_action = "GOVBLOCK_REPAIR" if has_govblock else "REPLAN"
    elif has_govblock:
        recommended_action = "GOVBLOCK_REPAIR"
    else:
        recommended_action = "NEXT_ITERATION"

    result = {
        "mission_id": mission_id,
        "sprint_id": sprint_id,
        "audited_at": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict,
        "findings": findings,
        "rework_items": rework_items,
        "open_gaps": open_gaps,
        "mission_complete": mission_complete,
        "next_iteration_required": next_iteration_required,
        "recommended_action": recommended_action,
        "signal_snapshot": {
            "autonomous_continue": autonomous_continue,
            "govblock_resolved_by": govblock_resolved_by,
            "stop_reason": signal.get("stop_reason"),
            "iteration": signal.get("iteration"),
        },
    }

    # ------------------------------------------------------------------
    # 7. Write output
    # ------------------------------------------------------------------
    output_path = repo_root / _OUTPUT_PATH_REL
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    return result


# ---------------------------------------------------------------------------
# Mission complete helper
# ---------------------------------------------------------------------------


def check_mission_complete(repo_root: Path | None = None, mission_id: str | None = None) -> bool:
    """Return True only if lifecycle audit passes with no open gaps."""
    result = run_lifecycle_audit(repo_root=repo_root, mission_id=mission_id)
    return bool(result.get("mission_complete"))


# ---------------------------------------------------------------------------
# Taskcard generator (returned to agent for plan amendment via Edit tool)
# ---------------------------------------------------------------------------


def generate_audit_taskcard(finding: dict, mission_id: str) -> dict:
    """Generate a taskcard dict from an audit finding.

    This is returned to the agent — the agent writes it to the plan via Edit tool.
    This function does NOT write to the plan file.
    """
    finding_type = finding.get("type", "UNKNOWN")
    description = finding.get("description", "")
    recommended = finding.get("recommended_action", "")
    finding_id = finding.get("finding_id", "FIND-000")

    task_id = f"TC-AUD-{finding_id.replace('FIND-', '')}"

    return {
        "task_id": task_id,
        "stable_key": f"{finding_type.lower()}-{mission_id or 'unknown'}-{datetime.now(timezone.utc).strftime('%Y%m%d')}",
        "mission_id": mission_id,
        "status": "READY",
        "objective": f"Resolve audit finding: {description[:120]}",
        "why_it_matters": f"Finding type {finding_type} blocks lifecycle completion",
        "finding_ref": finding_id,
        "recommended_action": recommended,
        "severity": finding.get("severity", "MEDIUM"),
        "source_file": finding.get("source_file", ""),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Product-track post-execution lifecycle audit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--mission-id", default=None, help="Mission identifier (e.g. MACH-LIF-FORENSICS-20260623)")
    p.add_argument("--sprint-id", default=None, help="Sprint identifier (e.g. TC-LIF-001)")
    p.add_argument("--repo-root", default=None, help="Repository root path (default: auto-detected)")
    p.add_argument("--check-mission-complete", action="store_true", help="Exit 0 if mission complete, 1 otherwise")
    p.add_argument("--json", dest="output_json", action="store_true", help="Print result JSON to stdout")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root) if args.repo_root else None

    try:
        result = run_lifecycle_audit(
            repo_root=repo_root,
            mission_id=args.mission_id,
            sprint_id=args.sprint_id,
        )
    except Exception as exc:
        print(f"ERROR: lifecycle_audit failed: {exc}", file=sys.stderr)
        return 3

    if args.output_json or not args.check_mission_complete:
        print(json.dumps(result, indent=2))

    if args.check_mission_complete:
        return 0 if result.get("mission_complete") else 1

    verdict = result.get("verdict", "UNKNOWN")
    if verdict == "AUDIT_PASS":
        return 0
    elif verdict == "AUDIT_REQUIRES_ITERATION":
        return 1
    elif verdict == "AUDIT_BLOCKED_EXTERNAL":
        return 2
    else:
        return 3


if __name__ == "__main__":
    sys.exit(main())
