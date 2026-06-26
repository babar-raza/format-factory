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
# Plan file taskcard parser (TC-TCF-003)
# ---------------------------------------------------------------------------

import re as _re

_TC_TABLE_RE = _re.compile(
    r"\|\s*(TC-[A-Z0-9]+-[A-Z0-9-]+)\s*\|\s*"
    r"(CLOSED|OPEN|IN_PROGRESS|PENDING|SUPERSEDED|EXCLUDED)\s*\|",
    _re.IGNORECASE,
)
_TC_BLOCK_RE = _re.compile(
    r"^#{1,4}\s+(TC-[A-Z0-9]+-[A-Z0-9-]+)\b[^\n]*\n"
    r"(?:[^\n]*\n){0,4}?"
    r"[^\n]*\*{0,2}Status:?\*{0,2}\s*(CLOSED|OPEN|IN_PROGRESS|PENDING|SUPERSEDED|EXCLUDED)",
    _re.IGNORECASE | _re.MULTILINE,
)
_TC_INLINE_RE = _re.compile(
    "(TC-[A-Z0-9]+-[A-Z0-9-]+)\\s*(?:\u2014|:|-)\\s*\\*{0,2}"
    "(CLOSED|OPEN|IN_PROGRESS|PENDING|SUPERSEDED|EXCLUDED)\\*{0,2}",
    _re.IGNORECASE,
)
_TERMINAL_STATUSES = frozenset({"CLOSED", "SUPERSEDED", "EXCLUDED"})


def parse_plan_taskcards(plan_path: str | Path) -> list[dict]:
    """Parse a plan file and extract taskcard IDs with their statuses."""
    plan_path = Path(plan_path)
    if not plan_path.exists():
        return []
    try:
        text = plan_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []

    seen: dict[str, str] = {}
    for m in _TC_TABLE_RE.finditer(text):
        tc_id = m.group(1).upper()
        if tc_id not in seen:
            seen[tc_id] = m.group(2).upper()
    for m in _TC_BLOCK_RE.finditer(text):
        tc_id = m.group(1).upper()
        if tc_id not in seen:
            seen[tc_id] = m.group(2).upper()
    for m in _TC_INLINE_RE.finditer(text):
        tc_id = m.group(1).upper()
        if tc_id not in seen:
            seen[tc_id] = m.group(2).upper()

    return [{"tc_id": k, "status": v} for k, v in seen.items()]


def compute_plan_hash(plan_path: str | Path) -> str:
    """Return SHA-256 hex digest of plan file content, or empty string if unavailable."""
    import hashlib
    plan_path = Path(plan_path)
    if not plan_path.exists():
        return ""
    try:
        data = plan_path.read_bytes()
        return hashlib.sha256(data).hexdigest()
    except Exception:
        return ""


def build_closure_contract(
    audit_result: dict,
    plan_path: str | Path | None = None,
) -> dict:
    """Build a machine-readable closure contract from audit results."""
    import hashlib
    findings = audit_result.get("findings", [])
    rework = audit_result.get("rework_items", [])
    open_tcs = audit_result.get("open_taskcards", [])
    open_gaps = audit_result.get("open_gaps", [])

    all_tasks_closed = audit_result.get("all_taskcards_closed", True)
    no_govblock = not any(
        r.startswith("GOV_BLOCK:") for r in rework
        if isinstance(r, str)
    )
    all_findings_consumed = all(
        f.get("severity", "").upper() in ("LOW", "INFO", "ADVISORY")
        for f in findings
    )
    evidence_complete = audit_result.get("mission_complete", False) or (
        not open_gaps and all_tasks_closed
    )
    no_open_gaps = len(open_gaps) == 0

    plan_hash = ""
    pp = ""
    if plan_path:
        pp = str(plan_path)
        p = Path(plan_path)
        if p.exists():
            try:
                plan_hash = hashlib.sha256(p.read_bytes()).hexdigest()
            except Exception:
                pass

    authorized = (
        all_tasks_closed
        and all_findings_consumed
        and no_govblock
        and evidence_complete
        and no_open_gaps
    )
    return {
        "all_mandatory_tasks_closed": all_tasks_closed,
        "all_audit_findings_consumed": all_findings_consumed,
        "all_rework_closed": len(rework) == 0,
        "evidence_complete": evidence_complete,
        "no_govblock_unresolved": no_govblock,
        "no_open_gaps": no_open_gaps,
        "plan_path": pp,
        "plan_hash": plan_hash,
        "closure_authorized": authorized,
    }


# ---------------------------------------------------------------------------
# TC-TCF-003: Premature-closure guards
# ---------------------------------------------------------------------------


def check_queue_exhaustion_guard(repo_root: Path, signal: dict) -> dict | None:
    """TC-TCF-003-G1: Distinguish 'queue empty because done' vs 'queue empty because generator failed'.

    Returns a CRITICAL finding if zero-task-counter shows repeated empty queue
    without mission_complete being declared. GUARD_FAIL blocks TERMINAL_CLOSED.
    Returns None when no issue is detected or the guard cannot run (non-blocking).
    """
    counter_path = repo_root / ".local" / "supervisor" / "zero-task-counter.json"
    try:
        if not counter_path.exists():
            return None
        counter = json.loads(counter_path.read_text(encoding="utf-8", errors="replace"))
        count = int(counter.get("count", 0))
        mission_complete_declared = bool(counter.get("mission_complete_declared"))
        if count >= 3 and not mission_complete_declared:
            return {
                "finding_id": "FIND-GUARD-001",
                "type": "QUEUE_EXHAUSTION_PREMATURE_CLOSURE",
                "severity": "CRITICAL",
                "description": (
                    f"zero-task-counter.json count={count} (>=3) but mission_complete_declared=False. "
                    "Queue exhaustion may be due to task generation failure, not true completion. "
                    "TC-TCF-003-G1 GUARD_FAIL: cannot authorize TERMINAL_CLOSED."
                ),
                "source_file": str(counter_path),
                "recommended_action": (
                    "Verify task queue by checking next-work-items.json and gap-ledger. "
                    "If truly complete, set mission_complete_declared=true in zero-task-counter.json. "
                    "If tasks are missing, regenerate the task queue."
                ),
                "guard_id": "G1_QUEUE_EXHAUSTION",
            }
    except Exception:
        pass  # Non-blocking; guard failure does not prevent audit
    return None


def check_closeout_task_guard(repo_root: Path) -> dict | None:
    """TC-TCF-003-G2: Verify the most recent sprint was not a closeout-only sprint.

    A closeout sprint (writing evidence, building review packages, updating reports)
    is NOT a valid basis for terminal closure. The mission must show real product
    or machinery work, not just administrative cleanup.
    Returns CRITICAL finding if last declaration changed only administrative files.
    Returns None when no issue is detected or guard cannot run (non-blocking).
    """
    _ADMIN_PREFIXES = (
        ".local/evidences/",
        "reports/supervisor/",
        "reports/terminal-closure",
        ".local/supervisor/",
    )
    _ADMIN_SUFFIXES = (".yaml", ".json", ".md")
    try:
        evidences_dir = repo_root / ".local" / "evidences"
        if not evidences_dir.exists():
            return None
        # Find most recent evidence-declaration.yaml
        declarations = sorted(
            evidences_dir.rglob("evidence-declaration.yaml"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if not declarations:
            return None
        latest = declarations[0]
        content = latest.read_text(encoding="utf-8", errors="replace")
        # Extract changed_files list via simple heuristic
        import re as _re_g2
        changed_match = _re_g2.findall(r"changed_files:\s*\n((?:\s+-[^\n]+\n)*)", content)
        if not changed_match:
            return None  # Cannot parse; non-blocking
        changed_block = changed_match[-1]
        files = [ln.strip().lstrip("- ").strip() for ln in changed_block.strip().splitlines() if ln.strip().startswith("-")]
        if not files:
            return None
        admin_files = [
            f for f in files
            if any(f.startswith(p) for p in _ADMIN_PREFIXES)
            or (all(f.endswith(s) for s in _ADMIN_SUFFIXES[:1]) and "evidence" in f)
        ]
        if files and len(admin_files) == len(files):
            return {
                "finding_id": "FIND-GUARD-002",
                "type": "CLOSEOUT_ONLY_SPRINT",
                "severity": "CRITICAL",
                "description": (
                    f"Most recent declaration ({latest.name}) changed only administrative files "
                    f"(evidence, reports, YAML). Closeout sprint ≠ mission completion. "
                    "TC-TCF-003-G2 GUARD_FAIL: cannot authorize TERMINAL_CLOSED from a closeout sprint."
                ),
                "source_file": str(latest),
                "recommended_action": (
                    "Verify that meaningful product or machinery work preceded this closeout sprint. "
                    "If closure is valid, the prior sprint's declaration should show real implementation."
                ),
                "guard_id": "G2_CLOSEOUT_TASK",
            }
    except Exception:
        pass  # Non-blocking
    return None


def check_iteration_limit_guard(signal: dict) -> dict | None:
    """TC-TCF-003-G3: Warn when closure was triggered at MAX_ITERATIONS boundary.

    An iteration limit is a checkpoint/rollover, not a completion signal.
    Returns MEDIUM finding when stop_reason indicates iteration limit.
    Returns None when not applicable (non-blocking GUARD_WARN only).
    """
    stop_reason = signal.get("stop_reason") or ""
    if "MAX_ITERATIONS" in stop_reason or "GOVERNED_ROLLOVER" in stop_reason:
        return {
            "finding_id": "FIND-GUARD-003",
            "type": "ITERATION_LIMIT_TRIGGERED",
            "severity": "MEDIUM",
            "description": (
                f"stop_reason='{stop_reason}' indicates an iteration limit was reached. "
                "MAX_ITERATIONS is a checkpoint/rollover signal, not a completion signal. "
                "TC-TCF-003-G3 GUARD_WARN: verify mission is truly complete before terminal closure."
            ),
            "source_file": ".local/supervisor/continuation-signal.json",
            "recommended_action": "Confirm all plan requirements are met; reset iteration counter and verify completion.",
            "guard_id": "G3_ITERATION_LIMIT",
        }
    return None


def check_sprint_audit_guard(repo_root: Path) -> dict | None:
    """TC-TCF-003-G4: Warn when evidence-review.json appears newer than last sprint audit log.

    An unconsumed sprint audit indicates the agent has not reviewed the most recent
    sprint's findings before attempting terminal closure.
    Returns MEDIUM finding when potential mismatch is detected (non-blocking GUARD_WARN).
    Returns None when guard cannot determine state (non-blocking).
    """
    try:
        review_path = repo_root / "reports" / "supervisor" / "evidence-review.json"
        audit_log_path = repo_root / ".local" / "supervisor" / "sprint-audit-log.json"
        if not review_path.exists():
            return None
        review_mtime = review_path.stat().st_mtime
        if audit_log_path.exists():
            audit_mtime = audit_log_path.stat().st_mtime
            if review_mtime > audit_mtime + 60:  # >1 min gap
                return {
                    "finding_id": "FIND-GUARD-004",
                    "type": "SPRINT_AUDIT_UNCONSUMED",
                    "severity": "MEDIUM",
                    "description": (
                        "evidence-review.json is newer than sprint-audit-log.json by >60s. "
                        "The most recent sprint's audit findings may not have been consumed. "
                        "TC-TCF-003-G4 GUARD_WARN: confirm all sprint audit findings are addressed."
                    ),
                    "source_file": str(review_path),
                    "recommended_action": "Review evidence-review.json findings and update sprint-audit-log.json.",
                    "guard_id": "G4_SPRINT_AUDIT",
                }
    except Exception:
        pass  # Non-blocking
    return None


# ---------------------------------------------------------------------------
# Core audit function
# ---------------------------------------------------------------------------


def run_lifecycle_audit(
    repo_root: Path | None = None,
    mission_id: str | None = None,
    sprint_id: str | None = None,
    plan_path: str | Path | None = None,
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
    # 0. Vacuous-call guard (TC-RJO-004)
    # ------------------------------------------------------------------
    # Track whether this is a vacuous call (no plan_path, no mission_id).
    # When vacuous, we still run signal-based checks (for GOVBLOCK, rework, etc.)
    # but we force mission_complete=False and mark the verdict as AUDIT_PASS_VACUOUS
    # when no other issue is detected — preventing false AUDIT_PASS with 0 taskcards.
    _vacuous_call = not plan_path and not mission_id

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
    # 1b. TC-TCF-003: Premature-closure guards (run before GOV_BLOCK check)
    # ------------------------------------------------------------------
    _guard_results: list[str] = []
    for _guard_fn, _guard_args in [
        (check_queue_exhaustion_guard, (repo_root, signal)),
        (check_closeout_task_guard, (repo_root,)),
        (check_iteration_limit_guard, (signal,)),
        (check_sprint_audit_guard, (repo_root,)),
    ]:
        try:
            _gf = _guard_fn(*_guard_args)  # type: ignore[operator]
            if _gf:
                findings.append(_gf)
                _guard_results.append(f"{_gf['guard_id']}:{_gf['severity']}")
        except Exception:
            pass  # Non-blocking; individual guard failure does not stop audit

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
    # 2b. Check for advisory (non-GOV_BLOCK) rework items
    # ------------------------------------------------------------------
    non_govblock_rework = [item for item in raw_rework if item not in govblock_items]
    if non_govblock_rework:
        findings.append({
            "finding_id": "FIND-REWORK-001",
            "type": "ADVISORY_REWORK_PENDING",
            "severity": "LOW",
            "description": (
                f"Non-blocking rework items present: {non_govblock_rework}. "
                "Mission may be complete, but advisory items should be noted."
            ),
            "source_file": str(signal_path),
            "recommended_action": (
                "Note advisory rework in evidence declaration incomplete_work_items. "
                "Does not block mission_complete if all other checks pass."
            ),
        })

    # ------------------------------------------------------------------
    # 3. Check autonomous_continue flag
    # ------------------------------------------------------------------
    if not autonomous_continue:
        # Distinguish external gate vs regular block
        stop_reason = signal.get("stop_reason") or ""
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
    # 5b. Plan file taskcard check (TC-TCF-003)
    # ------------------------------------------------------------------
    open_taskcards: list[dict] = []
    all_taskcards_closed = True
    total_taskcards_parsed = 0
    plan_hash_value = ""
    has_open_taskcards = False

    if plan_path:
        tcs = parse_plan_taskcards(plan_path)
        total_taskcards_parsed = len(tcs)
        open_taskcards = [
            tc for tc in tcs if tc["status"] not in _TERMINAL_STATUSES
        ]
        all_taskcards_closed = len(open_taskcards) == 0 and total_taskcards_parsed > 0
        has_open_taskcards = bool(open_taskcards)
        plan_hash_value = compute_plan_hash(plan_path)

        if has_open_taskcards:
            findings.append({
                "finding_id": "FIND-TC-001",
                "type": "OPEN_TASKCARDS",
                "severity": "CRITICAL",
                "description": (
                    f"{len(open_taskcards)} open taskcard(s) in plan: "
                    f"{', '.join(tc['tc_id'] for tc in open_taskcards[:5])}"
                ),
                "source_file": str(plan_path),
                "recommended_action": "Close all taskcards before allowing TERMINAL_CLOSED",
            })

    # ------------------------------------------------------------------
    # 6. Compute overall verdict
    # ------------------------------------------------------------------
    has_external_gate = any(f["type"] == "EXTERNAL_GATE_BLOCKING" for f in findings)
    has_govblock = any(f["type"] == "GOVBLOCK_PRESENT" for f in findings)
    has_continuation_blocked = any(f["type"] == "CONTINUATION_BLOCKED" for f in findings)
    has_rework_pending = any(f["type"] == "REWORK_PENDING" for f in findings)
    has_open_gaps = bool(open_gaps)
    # TC-TCF-003: CRITICAL guard findings (G1/G2) block closure same as open taskcards
    has_critical_guard = any(
        f.get("severity") == "CRITICAL" and f.get("guard_id", "").startswith("G")
        for f in findings
    )

    if has_external_gate:
        verdict = "AUDIT_BLOCKED_EXTERNAL"
    elif has_govblock or has_continuation_blocked or has_rework_pending or has_open_gaps or has_open_taskcards or has_critical_guard:
        verdict = "AUDIT_REQUIRES_ITERATION"
    else:
        verdict = "AUDIT_PASS"

    next_iteration_required = verdict == "AUDIT_REQUIRES_ITERATION"
    mission_complete = verdict == "AUDIT_PASS" and not open_gaps

    # TC-RJO-004: Vacuous-call guard — if called without plan_path or mission_id,
    # convert AUDIT_PASS to AUDIT_PASS_VACUOUS and force mission_complete=False.
    # Signal-based checks (GOVBLOCK, CONTINUATION_BLOCKED) still run and can produce
    # AUDIT_REQUIRES_ITERATION correctly — we only intercept the vacuous AUDIT_PASS case.
    if _vacuous_call and verdict == "AUDIT_PASS":
        verdict = "AUDIT_PASS_VACUOUS"
        mission_complete = False
        next_iteration_required = False
        findings.append({
            "finding_id": "FIND-VAC-001",
            "type": "VACUOUS_CALL",
            "severity": "HIGH",
            "description": (
                "lifecycle_audit called without --plan-path or --mission-id. "
                f"Taskcards parsed: {total_taskcards_parsed}. "
                "mission_complete is forced to False to prevent vacuous truth. "
                "Pass --plan-path to audit real taskcard state."
            ),
            "source_file": "CLI",
            "recommended_action": (
                "Re-run with --plan-path <plan-file> or --mission-id <mission-id>"
            ),
        })

    if verdict == "AUDIT_PASS" and not open_gaps:
        recommended_action = "MISSION_COMPLETE"
    elif has_external_gate:
        recommended_action = "GOVBLOCK_REPAIR" if has_govblock else "REPLAN"
    elif has_govblock:
        recommended_action = "GOVBLOCK_REPAIR"
    else:
        recommended_action = "NEXT_ITERATION"

    # Build closure contract if plan_path provided
    closure_contract = {}
    if plan_path:
        closure_contract = build_closure_contract(
            {
                "findings": findings,
                "rework_items": rework_items,
                "open_taskcards": open_taskcards,
                "all_taskcards_closed": all_taskcards_closed,
                "open_gaps": open_gaps,
                "mission_complete": mission_complete,
            },
            plan_path=plan_path,
        )
        # Override verdict if contract says not authorized
        if not closure_contract.get("closure_authorized") and verdict == "AUDIT_PASS":
            verdict = "AUDIT_REQUIRES_ITERATION"
            next_iteration_required = True
            mission_complete = False

    result = {
        "mission_id": mission_id,
        "sprint_id": sprint_id,
        "audited_at": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict,
        "findings": findings,
        "rework_items": rework_items,
        "open_gaps": open_gaps,
        "open_taskcards": open_taskcards,
        "all_taskcards_closed": all_taskcards_closed,
        "total_taskcards_parsed": total_taskcards_parsed,
        "plan_path": str(plan_path) if plan_path else None,
        "plan_hash": plan_hash_value,
        "mission_complete": mission_complete,
        "next_iteration_required": next_iteration_required,
        "recommended_action": recommended_action,
        "closure_contract": closure_contract,
        "guard_results": _guard_results,
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

    # TC-TCF-003: Persist closure_contract.json alongside output when authorized.
    # Allows V-TCF-002 to verify the contract exists before accepting terminal closure claims.
    if closure_contract and closure_contract.get("closure_authorized") and plan_path:
        import hashlib as _hl_c
        _phash = closure_contract.get("plan_hash") or _hl_c.sha256(str(plan_path).encode()).hexdigest()[:16]
        _cc_dir = repo_root / ".local" / "evidences" / "plan-closures" / _phash[:16]
        try:
            _cc_dir.mkdir(parents=True, exist_ok=True)
            (_cc_dir / "closure_contract.json").write_text(
                json.dumps(closure_contract, indent=2) + "\n", encoding="utf-8"
            )
        except Exception:
            pass  # Non-blocking

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
    p.add_argument("--plan-path", default=None, help="Path to plan file for taskcard verification")
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
            plan_path=args.plan_path,
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
