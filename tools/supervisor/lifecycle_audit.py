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

# Coordination plane integration (TC-SWB-004)
try:
    import sys as _sys_cw
    _sys_cw.path.insert(0, str(Path(__file__).resolve().parent))
    from coordination.coordinated_io import coordinated_write as _coordinated_write
except ImportError:
    from contextlib import contextmanager as _cm_fallback
    @_cm_fallback
    def _coordinated_write(path, **kw):
        yield

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DEFAULT_REPO_ROOT = Path(__file__).parent.parent.parent
_SIGNAL_PATH_REL = ".local/supervisor/continuation-signal.json"
_EVIDENCE_REVIEW_REL = "reports/supervisor/evidence-review.md"
_PRODUCT_MISSION_LEDGER_REL = ".local/supervisor/product-mission-ledger.json"
_OUTPUT_PATH_REL = ".local/supervisor/lifecycle-audit-results.json"

_MACHINERY_SIGNAL_PATH_REL = ".local/supervisor/machinery/continuation-signal.json"
_PRODUCT_SIGNAL_PATH_REL = ".local/supervisor/product/continuation-signal.json"

# TC-VWR-003 (velvet-swinging-wreath): machinery mission ledger path constant
_MACHINERY_LEDGER_PATH_REL = ".local/supervisor/machinery/mission-ledger.json"

_EXTERNAL_GATE_KEYWORDS = [
    "push_credentials",
    "gate_11",
    "g11",
    "publication_credentials",
    "external_gate",
]


def _resolve_signal_path(repo_root: Path, track: str | None = None) -> Path:
    """Resolve continuation signal path based on --track parameter.

    TC-RJO-NEW-002: Prevents cross-track signal contamination when running
    lifecycle audit for machinery missions while product track is blocked.
    """
    if track == "machinery":
        p = repo_root / _MACHINERY_SIGNAL_PATH_REL
        if p.exists():
            return p
        return repo_root / _SIGNAL_PATH_REL
    elif track == "product":
        p = repo_root / _PRODUCT_SIGNAL_PATH_REL
        if p.exists():
            return p
        return repo_root / _SIGNAL_PATH_REL
    return repo_root / _SIGNAL_PATH_REL


# ---------------------------------------------------------------------------
# TC-VWR-003/004 (velvet-swinging-wreath): Machinery mission ledger helpers
# ---------------------------------------------------------------------------


def _read_machinery_mission_ledger(mission_id: str, repo_root: Path | None = None) -> dict:
    """Read mission ledger for a given mission_id.

    Returns sentinel dict (0 iterations, _sentinel=True) on missing/invalid data
    or when the ledger's mission_id differs (stale entry from different mission).
    RC-001 fix: enables Check B1 to query behavioral iteration state.
    """
    _root = repo_root if repo_root is not None else _DEFAULT_REPO_ROOT
    ledger_path = _root / _MACHINERY_LEDGER_PATH_REL
    _default: dict = {
        "current_behavioral_iterations": 0,
        "behavioral_iterations_required": 2,
        "_sentinel": True,
    }
    if not ledger_path.exists():
        return _default
    try:
        data = json.loads(ledger_path.read_text(encoding="utf-8"))
        if data.get("mission_id") != mission_id:
            return _default  # Stale entry — treat as 0 iterations
        return data
    except Exception:
        return _default


def _check_behavioral_iteration_guard(
    mission_id: str,
    plan_type: str,
    repo_root: Path | None = None,
) -> dict | None:
    """Check B1 (RC-001 fix): Behavioral iteration minimum for machinery_hardening plans.

    For plans with plan_type == "machinery_hardening" only: require
    current_behavioral_iterations >= behavioral_iterations_required before AUDIT_PASS.
    Returns a CRITICAL guard finding if not met, or None if passed / not applicable.
    """
    if plan_type != "machinery_hardening":
        return None
    ledger = _read_machinery_mission_ledger(mission_id, repo_root)
    current = ledger.get("current_behavioral_iterations", 0)
    required = ledger.get("behavioral_iterations_required", 2)
    if current < required:
        return {
            "guard_id": "GB1",
            "finding_id": "FIND-GB1-001",
            "severity": "CRITICAL",
            "check": "behavioral_iteration_minimum",
            "type": "BEHAVIORAL_ITERATION_INSUFFICIENT",
            "current_behavioral_iterations": current,
            "behavioral_iterations_required": required,
            "mission_id": mission_id,
            "sentinel": ledger.get("_sentinel", False),
            "description": (
                f"Behavioral iteration minimum not met: {current}/{required} iterations completed. "
                "Mission-ledger may be absent or stale (treating as 0 iterations). "
                "Returning AUDIT_REQUIRES_ITERATION to prevent premature TERMINAL_CLOSED."
            ),
            "recommended_action": (
                "Complete one full audit-execute-reaudit cycle, then re-run lifecycle_audit."
            ),
        }
    return None


def _increment_behavioral_iteration(mission_id: str, repo_root: Path | None = None) -> int:
    """Increment current_behavioral_iterations in mission-ledger.json for mission_id.

    Called on AUDIT_PASS for machinery_hardening plans to record a completed cycle.
    Returns the new iteration count; returns 0 if ledger absent or mission_id mismatch.
    RC-002 fix: ensures each successful audit cycle is tracked.
    """
    _root = repo_root if repo_root is not None else _DEFAULT_REPO_ROOT
    ledger_path = _root / _MACHINERY_LEDGER_PATH_REL
    if not ledger_path.exists():
        return 0
    try:
        data = json.loads(ledger_path.read_text(encoding="utf-8"))
    except Exception:
        return 0
    if data.get("mission_id") != mission_id:
        return 0
    data["current_behavioral_iterations"] = data.get("current_behavioral_iterations", 0) + 1
    data["audit_pending"] = False
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    data["state_digest"] = (
        f"{mission_id}:iteration={data['current_behavioral_iterations']}:stage=POST_EXECUTION_AUDIT"
    )
    ledger_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data["current_behavioral_iterations"]


# ---------------------------------------------------------------------------
# Plan file taskcard parser (TC-TCF-003)
# ---------------------------------------------------------------------------

import re as _re

_TC_TABLE_RE = _re.compile(
    r"\|\s*(TC-[A-Z0-9]+-[A-Z0-9-]+)\s*\|\s*"
    r"(CLOSED|OPEN|IN_PROGRESS|PENDING|SUPERSEDED|EXCLUDED"
    r"|READY|PARTIALLY_COMPLETED|COMPLETED_BUT_WEAKLY_VERIFIED|FOLLOW_UP)\s*\|",
    _re.IGNORECASE,
)
_TC_BLOCK_RE = _re.compile(
    r"^#{1,4}\s+(TC-[A-Z0-9]+-[A-Z0-9-]+)\b[^\n]*\n"
    r"(?:[^\n]*\n){0,4}?"
    r"[^\n]*\*{0,2}Status:?\*{0,2}\s*(CLOSED|OPEN|IN_PROGRESS|PENDING|SUPERSEDED|EXCLUDED"
    r"|READY|PARTIALLY_COMPLETED|COMPLETED_BUT_WEAKLY_VERIFIED|FOLLOW_UP)",
    _re.IGNORECASE | _re.MULTILINE,
)
_TC_INLINE_RE = _re.compile(
    "(TC-[A-Z0-9]+-[A-Z0-9-]+)\\s*(?:\u2014|:|-)\\s*\\*{0,2}"
    "(CLOSED|OPEN|IN_PROGRESS|PENDING|SUPERSEDED|EXCLUDED"
    "|READY|PARTIALLY_COMPLETED|COMPLETED_BUT_WEAKLY_VERIFIED|FOLLOW_UP)\\*{0,2}",
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


def _scope_rework_items(
    rework_items: list,
    mission_id: "str | None",
    plan_path: "str | Path | None" = None,
) -> list:
    """Filter rework_items to those plausibly belonging to `mission_id`.

    SFC-GAP-D (2026-07-17): ``continuation-signal.json``'s ``rework_items`` is a
    flat, global, unscoped list shared by every mission on a track. Feeding it
    unfiltered into :func:`build_closure_contract` makes one mission's closure
    block on a completely unrelated mission's rework — the exact non-determinism
    hit live (a plan with 0 rework of its own was blocked by
    ``LANE_ENFORCEMENT:1_violations`` belonging to a different mission).

    This is an interim, additive heuristic — no structured
    ``rework_items_by_mission`` producer exists yet (that would require editing
    ~21 call sites across the codebase, explicitly rejected as too large a blast
    radius for this change). An item is kept if it mentions the mission_id
    itself or one of the mission's own taskcard IDs (parsed from its plan file).
    GOV_BLOCK items are exempt from scoping — a structural governance block is
    never mission-private and must never be silently filtered out.

    When ``mission_id`` is falsy, returns the input unchanged (explicit opt-in
    to global/unscoped semantics, matching :func:`check_sprint_audit_guard`).
    """
    if not mission_id:
        return list(rework_items)
    own_ids: set[str] = {mission_id}
    if plan_path:
        for tc in parse_plan_taskcards(plan_path):
            own_ids.add(tc["tc_id"])
    scoped = []
    for item in rework_items:
        if not isinstance(item, str):
            continue
        if "GOV_BLOCK" in item or "monolith_detection_validator" in item:
            scoped.append(item)  # structural blocks are never mission-private
            continue
        if any(oid in item for oid in own_ids):
            scoped.append(item)
    return scoped


def build_closure_contract(
    audit_result: dict,
    plan_path: str | Path | None = None,
    ledger_lane_scope: str = "global",
) -> dict:
    """Build a machine-readable closure contract from audit results.

    ``ledger_lane_scope`` ("mission" | "global") records, visibly and
    auditably, whether the caller passed a mission-scoped ``rework_items`` list
    (SFC-GAP-D) or the raw global list — never a silent fallthrough.
    """
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
        "ledger_lane_scope": ledger_lane_scope,
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


def _read_json_mission_id(path: Path) -> "str | None":
    """Best-effort read of a JSON file's top-level mission_id field.

    Returns None on any read/parse failure or when the field is absent —
    callers must treat None as "no assertion possible", never as a match.
    """
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    mid = data.get("mission_id")
    return mid if isinstance(mid, str) and mid else None


def check_sprint_audit_guard(
    repo_root: Path,
    audit_log_path: "Path | None" = None,
    evidence_review_path: "Path | None" = None,
    mission_id: "str | None" = None,
) -> dict | None:
    """TC-TCF-003-G4: Guard for sprint audit log state.

    Mission-scoping (SFC-GAP-D, 2026-07-17): ``sprint-audit-log.json`` and
    ``evidence-review.json`` are GLOBAL singletons, not mission-scoped stores —
    a fresh write by ANY concurrent mission's sprint updates the same file every
    other mission's closure reads from. Comparing raw mtimes with no mission
    filter (the pre-fix behavior) makes closure verdicts non-deterministic under
    concurrency: re-running this guard against the SAME mission minutes apart can
    flip purely because an unrelated mission's sprint touched these files.

    When ``mission_id`` is None (default): preserve the exact pre-fix global-mtime
    behavior unchanged — this is the explicit opt-in path for a plan whose own
    scope legitimately IS general-ledger/cross-mission audit hygiene.

    When ``mission_id`` is provided: absence of the audit log entirely is still
    unambiguous (CRITICAL — no audit ran for anyone). But if the audit log EXISTS
    and its own recorded ``mission_id`` field does not match (or the field is
    absent — the current real-world case, since no code in this repo writes that
    field yet; only the `/post-sprint-audit` skill does, out of this fix's scope),
    this guard has NO reliable data about *this* mission's audit freshness — it
    returns an INFO-severity (non-blocking) note rather than asserting CRITICAL or
    MEDIUM on data that may belong to an entirely different mission. Only when the
    file's mission_id actually MATCHES does the original stale-comparison logic
    apply, at full strength, for the mission under audit.

    Four cases:
    - Absent audit log: CRITICAL — audit never ran (TC-VWR-006 fix, unchanged).
    - mission_id given, audit log's own mission_id present but does NOT match:
      INFO GUARD_INFO — no signal for this mission; never blocks closure.
    - mission_id given (or None) and audit log's mission matches (or scoping is
      not requested): stale comparison — MEDIUM GUARD_WARN if stale, else None.
    - OK or cannot determine: None (non-blocking).
    """
    try:
        _repo = repo_root
        _review_path = evidence_review_path or (_repo / "reports" / "supervisor" / "evidence-review.json")
        _audit_log = audit_log_path or (_repo / ".local" / "supervisor" / "sprint-audit-log.json")
        if not _review_path.exists():
            return None
        if not _audit_log.exists():
            # TC-VWR-006-01: ESCALATE — absent audit log means audit never ran
            # (unambiguous regardless of mission scope: no audit ran for anyone).
            return {
                "finding_id": "FIND-GUARD-004-ABSENT",
                "type": "SPRINT_AUDIT_NEVER_RAN",
                "severity": "CRITICAL",
                "description": (
                    f"sprint-audit-log.json does not exist at {_audit_log}. "
                    "Post-execution audit was never run. "
                    "Cannot authorize TERMINAL_CLOSED without behavioral audit evidence."
                ),
                "source_file": str(_audit_log),
                "recommended_action": (
                    "Run: python tools/supervisor/lifecycle_audit.py "
                    "--mission-id <MISSION_ID> --plan-path <PLAN_PATH>"
                ),
                "guard_id": "G4_SPRINT_AUDIT",
            }

        if mission_id:
            _log_mission = _read_json_mission_id(_audit_log)
            if _log_mission != mission_id:
                return {
                    "finding_id": "FIND-GUARD-004-SCOPE",
                    "type": "SPRINT_AUDIT_NO_SIGNAL_FOR_MISSION",
                    "severity": "INFO",
                    "description": (
                        f"sprint-audit-log.json's recorded mission "
                        f"({_log_mission!r}) does not match the mission under "
                        f"audit ({mission_id!r}) — this global singleton file was "
                        "last written by a different mission's sprint. No audit-"
                        "freshness signal is available for this mission from this "
                        "file; this does not assert staleness or absence for this "
                        "mission and never blocks closure."
                    ),
                    "source_file": str(_audit_log),
                    "recommended_action": (
                        "If this mission requires its own post-sprint audit "
                        "evidence, ensure /post-sprint-audit was run for it "
                        "specifically (its mission_id write-through is tracked "
                        "as a follow-up; this guard cannot verify it yet)."
                    ),
                    "guard_id": "G4_SPRINT_AUDIT",
                }

        review_mtime = _review_path.stat().st_mtime
        audit_mtime = _audit_log.stat().st_mtime
        if review_mtime > audit_mtime + 60:  # >1 min gap — stale but present
            return {
                "finding_id": "FIND-GUARD-004",
                "type": "SPRINT_AUDIT_UNCONSUMED",
                "severity": "MEDIUM",
                "description": (
                    "evidence-review.json is newer than sprint-audit-log.json by >60s. "
                    "The most recent sprint's audit findings may not have been consumed. "
                    "TC-TCF-003-G4 GUARD_WARN: confirm all sprint audit findings are addressed."
                ),
                "source_file": str(_review_path),
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
    track: str | None = None,
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
    signal_path = _resolve_signal_path(repo_root, track)
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
    # 1a. TC-VWR-003: Detect plan_type from plan file header (machinery check)
    # ------------------------------------------------------------------
    import re as _re_lifecycle  # noqa: PLC0415
    _plan_type = "unknown"
    if plan_path:
        try:
            _header_text = Path(plan_path).read_text(encoding="utf-8", errors="replace")[:2000]
            _pt_match = _re_lifecycle.search(r"\*\*plan_type:\*\*\s+(\S+)", _header_text)
            if _pt_match:
                _plan_type = _pt_match.group(1).strip().lower()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # 1b. TC-TCF-003: Premature-closure guards (run before GOV_BLOCK check)
    # ------------------------------------------------------------------
    _guard_results: list[str] = []
    for _guard_fn, _guard_args, _guard_kwargs in [
        (check_queue_exhaustion_guard, (repo_root, signal), {}),
        (check_closeout_task_guard, (repo_root,), {}),
        (check_iteration_limit_guard, (signal,), {}),
        # SFC-GAP-D fix: mission_id was previously never forwarded here, so G4
        # always ran in unscoped (global) mode regardless of caller intent.
        (check_sprint_audit_guard, (repo_root,), {"mission_id": mission_id}),
    ]:
        try:
            _gf = _guard_fn(*_guard_args, **_guard_kwargs)  # type: ignore[operator]
            if _gf:
                findings.append(_gf)
                _guard_results.append(f"{_gf['guard_id']}:{_gf['severity']}")
        except Exception:
            pass  # Non-blocking; individual guard failure does not stop audit

    # Check B1 (TC-VWR-003): Behavioral iteration minimum for machinery_hardening plans
    try:
        _b1_finding = _check_behavioral_iteration_guard(
            mission_id or "", _plan_type, repo_root
        )
        if _b1_finding:
            _guard_results.append(f"GB1:{_b1_finding['severity']}")
            findings.append(_b1_finding)
    except Exception:
        pass  # Non-blocking

    # G3X (TC-VWR-006): Iteration-limit + behavioral iteration cross-check
    # If G3 (MAX_ITERATIONS) fired AND behavioral iterations are still below minimum,
    # escalate to CRITICAL to prevent premature AUDIT_PASS via iteration exhaustion.
    if any("G3" in g for g in _guard_results) and _plan_type == "machinery_hardening":
        try:
            _g3x_ledger = _read_machinery_mission_ledger(mission_id or "", repo_root)
            _current_b = _g3x_ledger.get("current_behavioral_iterations", 0)
            _required_b = _g3x_ledger.get("behavioral_iterations_required", 2)
            if _current_b < _required_b:
                _g3x = {
                    "guard_id": "G3X",
                    "finding_id": "FIND-G3X-001",
                    "severity": "CRITICAL",
                    "type": "ITERATION_LIMIT_WITHOUT_BEHAVIORAL_PROOF",
                    "check": "iteration_limit_without_behavioral_proof",
                    "description": (
                        f"Iteration limit reached but behavioral iterations ({_current_b}) < "
                        f"required ({_required_b}). Blocking AUDIT_PASS to prevent false mission completion."
                    ),
                    "recommended_action": "Complete required behavioral cycles before terminal closure.",
                }
                _guard_results.append("G3X:CRITICAL")
                findings.append(_g3x)
        except Exception:
            pass  # Non-blocking

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
    # 5c. TC-AUDIT-FAIL-CLOSED: Reject AUDIT_PASS when plan state is unknowable
    # ------------------------------------------------------------------
    # Case 1: mission_id provided but no plan_path — cannot verify taskcard closure.
    if not plan_path and mission_id:
        findings.append({
            "finding_id": "FIND-PP-001",
            "type": "PLAN_PATH_MISSING",
            "severity": "CRITICAL",
            "description": (
                f"lifecycle_audit called with mission_id={mission_id!r} but no --plan-path. "
                "Cannot verify taskcard closure state. AUDIT_PASS requires a readable plan file."
            ),
            "source_file": "CLI",
            "recommended_action": "Re-run with --plan-path <plan-file-path>",
        })

    # Case 2: plan_path provided but could not be read (hash empty = file unreadable).
    if plan_path and not plan_hash_value:
        findings.append({
            "finding_id": "FIND-PP-002",
            "type": "PLAN_UNREADABLE",
            "severity": "CRITICAL",
            "description": (
                f"Plan file {plan_path!r} could not be read or hashed. "
                "Cannot verify taskcard closure state."
            ),
            "source_file": str(plan_path),
            "recommended_action": "Verify plan file exists and is readable.",
        })

    # Case 3: plan_path provided, file is readable (hash present), but 0 taskcards found.
    # This catches parse failures, wrong format, or missing Taskcard Status Summary table.
    if plan_path and plan_hash_value and total_taskcards_parsed == 0:
        findings.append({
            "finding_id": "FIND-PP-003",
            "type": "ZERO_TASKCARDS_PARSED",
            "severity": "CRITICAL",
            "description": (
                f"Plan file {plan_path!r} was readable (hash={plan_hash_value[:12]}...) "
                "but 0 taskcards were parsed. This is likely a format/parsing failure. "
                "AUDIT_PASS is rejected to prevent false completion evidence."
            ),
            "source_file": str(plan_path),
            "recommended_action": (
                "Add a '## Taskcard Status Summary' table with '| TC-ID | Status |' columns. "
                "lifecycle_audit.py requires this exact format to parse taskcards."
            ),
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
    # TC-AUDIT-FAIL-CLOSED: Plan path or parsing failures block AUDIT_PASS
    has_plan_path_issue = any(
        f["type"] in ("PLAN_PATH_MISSING", "PLAN_UNREADABLE", "ZERO_TASKCARDS_PARSED")
        for f in findings
    )

    if has_external_gate:
        verdict = "AUDIT_BLOCKED_EXTERNAL"
    elif has_govblock or has_continuation_blocked or has_rework_pending or has_open_gaps or has_open_taskcards or has_critical_guard or has_plan_path_issue:
        verdict = "AUDIT_REQUIRES_ITERATION"
    else:
        verdict = "AUDIT_PASS"

    next_iteration_required = verdict == "AUDIT_REQUIRES_ITERATION"
    mission_complete = verdict == "AUDIT_PASS" and not open_gaps

    # TC-VWR-004-02: Increment behavioral iteration counter on AUDIT_PASS for machinery plans
    if verdict == "AUDIT_PASS" and _plan_type == "machinery_hardening" and mission_id:
        try:
            _increment_behavioral_iteration(mission_id, repo_root)
        except Exception:
            pass  # Non-blocking

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
    # SFC-GAP-D: rework_items fed into the closure contract is mission-scoped
    # when mission_id is given (the raw global list is still reported in
    # result["rework_items"] below for transparency — nothing is hidden, only
    # the closure-blocking computation is scoped).
    closure_contract = {}
    if plan_path:
        _scoped_rework = _scope_rework_items(rework_items, mission_id, plan_path)
        closure_contract = build_closure_contract(
            {
                "findings": findings,
                "rework_items": _scoped_rework,
                "open_taskcards": open_taskcards,
                "all_taskcards_closed": all_taskcards_closed,
                "open_gaps": open_gaps,
                "mission_complete": mission_complete,
            },
            plan_path=plan_path,
            ledger_lane_scope="mission" if mission_id else "global",
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
    with _coordinated_write(output_path, op="lifecycle_audit", source="lifecycle_audit"):
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
    """Return True only if lifecycle audit passes with no open gaps.

    Reads from the cached lifecycle-audit-results.json if available, to avoid
    re-running the audit without plan_path context (which would produce false negatives).
    """
    if repo_root is None:
        repo_root = _DEFAULT_REPO_ROOT
    cached = Path(repo_root) / ".local" / "supervisor" / "lifecycle-audit-results.json"
    if cached.exists():
        try:
            data = json.loads(cached.read_text(encoding="utf-8"))
            # Only trust the cached result if it matches the requested mission_id (or no filter)
            if mission_id is None or data.get("mission_id") == mission_id:
                return bool(data.get("mission_complete"))
        except Exception:
            pass
    # Fallback: re-run (may return false negative without plan_path)
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
# RC-004 (velvet-swinging-wreath): Auto-generate gap taskcards on ITERATION_REQUIRED
# ---------------------------------------------------------------------------


def generate_behavioral_gap_taskcards(
    audit_result: dict,
    plan_path: "Path | str | None" = None,
) -> list[dict]:
    """Generate taskcard dicts from ITERATION_REQUIRED findings.

    When lifecycle_audit returns AUDIT_REQUIRES_ITERATION, this function
    produces ready-to-append taskcard entries for each CRITICAL/HIGH finding,
    breaking the manual-inspection loop.

    Returns a list of taskcard dicts (does NOT write to plan file — caller uses Edit tool).
    If plan_path is provided, also appends a machine-readable summary to
    .local/supervisor/gap-taskcards.json for agent pickup.
    """
    from datetime import datetime, timezone as _tz  # noqa: PLC0415

    findings = audit_result.get("findings", [])
    mission_id = audit_result.get("mission_id") or "UNKNOWN"
    verdict = audit_result.get("verdict", "")

    if verdict not in ("AUDIT_REQUIRES_ITERATION", "AUDIT_REQUIRES_ITERATION"):
        return []

    # Only generate taskcards for findings that caused the iteration requirement
    actionable_severities = {"CRITICAL", "HIGH"}
    gap_taskcards = []
    for finding in findings:
        if finding.get("severity") not in actionable_severities:
            continue
        if finding.get("finding_id", "").startswith("FIND-VAC"):
            continue  # Skip vacuous-call findings
        tc = generate_audit_taskcard(finding, mission_id)
        tc["generated_by"] = "generate_behavioral_gap_taskcards (RC-004)"
        tc["generated_at"] = datetime.now(_tz.utc).isoformat()
        gap_taskcards.append(tc)

    # Persist for agent pickup
    if plan_path is not None:
        _plan_path = Path(plan_path) if not isinstance(plan_path, Path) else plan_path
        repo_root = _plan_path.resolve().parent
        # Walk up to find repo root (contains .git or .local)
        candidate = _plan_path.resolve()
        for _ in range(10):
            candidate = candidate.parent
            if (candidate / ".git").exists() or (candidate / ".local").exists():
                repo_root = candidate
                break
        try:
            out_path = repo_root / ".local" / "supervisor" / "gap-taskcards.json"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(
                __import__("json").dumps(
                    {"mission_id": mission_id, "verdict": verdict, "gap_taskcards": gap_taskcards},
                    indent=2,
                ) + "\n",
                encoding="utf-8",
            )
        except Exception:
            pass  # Non-blocking

    return gap_taskcards


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
    p.add_argument("--track", default=None, choices=["machinery", "product"],
                   help="Track to read continuation signal from (default: legacy path)")
    p.add_argument("--write-gap-taskcards", action="store_true",
                   help="RC-004: On ITERATION_REQUIRED, generate gap taskcards and write to "
                        ".local/supervisor/gap-taskcards.json for agent pickup")
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
            track=args.track,
        )
    except Exception as exc:
        print(f"ERROR: lifecycle_audit failed: {exc}", file=sys.stderr)
        return 3

    # RC-004: Auto-generate gap taskcards when ITERATION_REQUIRED
    if getattr(args, "write_gap_taskcards", False) and result.get("verdict") == "AUDIT_REQUIRES_ITERATION":
        gap_tcs = generate_behavioral_gap_taskcards(result, plan_path=args.plan_path)
        if gap_tcs:
            print(f"[RC-004] Generated {len(gap_tcs)} gap taskcard(s) -> .local/supervisor/gap-taskcards.json")

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
