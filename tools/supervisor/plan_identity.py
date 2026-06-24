"""
plan_identity.py — Plan Identity Infrastructure for Format Factory

Implements:
- extract_plan_identity()    : Parse machine-readable plan_identity: block from a plan file
- resolve_native_plan_path() : 9-step discovery algorithm for native plan path
- validate_plan_ownership()  : Confirm plan belongs to current session via lock files
- validate_plan_mutability() : Confirm plan lifecycle state permits mutation
- build_plan_write_event()   : Build audit-trail record for any plan write attempt

See docs/governance/plan-identity-schema.md for the full schema spec.
"""

from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Repository root detection
# ---------------------------------------------------------------------------
_THIS_FILE = Path(__file__).resolve()
_REPO_ROOT = _THIS_FILE.parent.parent.parent  # tools/supervisor/plan_identity.py → repo root

_PLAN_LOCKS_DIR = _REPO_ROOT / ".local" / "supervisor" / "plan-locks"
_SHARED_LOCK_PATH = _REPO_ROOT / ".local" / "supervisor" / "active-plan-lock.json"
_LEDGER_PATH = _REPO_ROOT / "plans" / "master-plan-memory.md"

# Pattern to extract YAML body from HTML comment block: <!--plan_identity: ... -->
_IDENTITY_COMMENT_RE = re.compile(
    r"<!--plan_identity:\s*\n(.*?)-->",
    re.DOTALL,
)

# F-003: Also match YAML fenced code block format produced by Claude plan mode:
#   ```yaml
#   plan_identity:
#     key: value
#   ```
_IDENTITY_CODEBLOCK_RE = re.compile(
    r"```ya?ml\s*\nplan_identity:\s*\n(.*?)```",
    re.DOTALL,
)


# ---------------------------------------------------------------------------
# 1. extract_plan_identity
# ---------------------------------------------------------------------------

def extract_plan_identity(plan_path: Path) -> Optional[dict]:
    """Parse the ``plan_identity:`` YAML block from a plan file.

    The block is expected to be wrapped in an HTML comment at the top of the
    file::

        <!--plan_identity:
          schema_version: "1.0"
          plan_id: "my-plan"
          ...
        -->

    Returns the parsed fields as a dict, or ``None`` if no block is found
    (backward-compatible — callers must handle None gracefully).
    """
    try:
        text = Path(plan_path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None

    match = _IDENTITY_COMMENT_RE.search(text)
    if not match:
        # F-003: Fallback to YAML fenced code block format (Claude plan mode)
        match = _IDENTITY_CODEBLOCK_RE.search(text)
    if not match:
        return None

    yaml_body = match.group(1)
    # Simple key: value parser (not full YAML — avoids adding a hard dependency)
    result: dict = {}
    for line in yaml_body.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" in stripped:
            key, _, raw_value = stripped.partition(":")
            key = key.strip()
            value = raw_value.strip().strip('"').strip("'")
            # Convert boolean literals
            if value.lower() == "true":
                value = True  # type: ignore[assignment]
            elif value.lower() == "false":
                value = False  # type: ignore[assignment]
            elif value.lower() == "null":
                value = None  # type: ignore[assignment]
            result[key] = value
    return result if result else None


# ---------------------------------------------------------------------------
# 2. resolve_native_plan_path  — 9-step discovery algorithm
# ---------------------------------------------------------------------------

def resolve_native_plan_path(
    mission_context: Optional[dict] = None,
    explicit_path: Optional[str] = None,
) -> tuple[Optional[Path], str]:
    """Resolve the authoritative native plan path using the governed 9-step algorithm.

    Priority order (first match wins):
      Step 1 — Execution-state-bound path from IN_PROGRESS session-keyed lock files
      Step 2 — Plan ID from mission_context dict (e.g. "plan_id" key)
      Step 3 — native_plan_path from plan identity front-matter of a candidate file
      Step 4 — Explicit path supplied by caller
      Step 5 — Matching ledger entry in master-plan-memory.md
      Step 6 — Repository plans/ directory (repo supplement plans only)
      Step 7 — Current plan-mode creation event (not resolvable here — skipped)

    Returns (Path | None, resolution_source).
    If multiple candidates remain after all steps: (None, "PLAN_IDENTITY_AMBIGUOUS").

    Forbidden resolution sources (never used):
      - Newest/most-recently-modified .md file
      - Global default plan name
      - plans/snoopy-juggling-seal.md unless its plan_id matches the mission
      - Another session's lock that belongs to a different mission
    """
    candidates: list[tuple[Path, str]] = []  # (path, source)

    # ------------------------------------------------------------------
    # Step 1: IN_PROGRESS session-keyed lock files
    # De-duplicate by resolved path so that session-keyed + shared lock
    # for the same plan do not produce false PLAN_IDENTITY_AMBIGUOUS.
    # ------------------------------------------------------------------
    in_progress_locks = _scan_lock_files(status_filter="IN_PROGRESS")
    seen_step1: dict[Path, str] = {}
    for lock in in_progress_locks:
        raw = lock.get("plan_path", "")
        p = _resolve_path(raw)
        if p and p.exists() and p not in seen_step1:
            seen_step1[p] = f"LOCK_FILE_IN_PROGRESS:{lock.get('session_id','?')}"
    candidates = [(p, src) for p, src in seen_step1.items()]

    if len(candidates) == 1:
        return candidates[0]

    if len(candidates) > 1:
        return (None, "PLAN_IDENTITY_AMBIGUOUS")

    # ------------------------------------------------------------------
    # Step 2: Plan ID from mission_context
    # ------------------------------------------------------------------
    if mission_context:
        plan_id = mission_context.get("plan_id") or mission_context.get("plan_path")
        if plan_id:
            p = _resolve_path(str(plan_id))
            if p and p.exists():
                candidates.append((p, "MISSION_CONTEXT"))

    if len(candidates) == 1:
        return candidates[0]

    # ------------------------------------------------------------------
    # Step 3: native_plan_path from plan identity front-matter
    #         (check candidate files gathered so far if any)
    # ------------------------------------------------------------------
    for path_candidate, _ in list(candidates):
        identity = extract_plan_identity(path_candidate)
        if identity and identity.get("native_plan_path"):
            p = _resolve_path(str(identity["native_plan_path"]))
            if p and p.exists() and (p, "FRONT_MATTER") not in candidates:
                candidates.append((p, "FRONT_MATTER"))

    if len(candidates) == 1:
        return candidates[0]

    # ------------------------------------------------------------------
    # Step 4: Explicit path supplied by caller
    # ------------------------------------------------------------------
    if explicit_path:
        p = _resolve_path(explicit_path)
        if p and p.exists():
            candidates.append((p, "EXPLICIT_CALLER"))
        if len(candidates) == 1:
            return candidates[0]

    # ------------------------------------------------------------------
    # Step 5: Matching ledger entry in master-plan-memory.md
    # ------------------------------------------------------------------
    if mission_context:
        mission_id = mission_context.get("mission_id")
        if mission_id:
            ledger_path = _find_in_ledger(mission_id)
            if ledger_path:
                p = _resolve_path(ledger_path)
                if p and p.exists():
                    candidates.append((p, "LEDGER_ENTRY"))

    if len(candidates) == 1:
        return candidates[0]

    # ------------------------------------------------------------------
    # Step 6: Repository plans/ directory (repo supplement plans)
    #         Only for repo-relative plans (not .claude/plans/)
    # ------------------------------------------------------------------
    if mission_context:
        plan_id = mission_context.get("plan_id")
        if plan_id:
            repo_plan = _REPO_ROOT / "plans" / f"{plan_id}.md"
            if repo_plan.exists():
                candidates.append((repo_plan, "REPO_PLANS_DIR"))

    # De-duplicate
    seen: set[Path] = set()
    unique_candidates: list[tuple[Path, str]] = []
    for p, src in candidates:
        if p not in seen:
            seen.add(p)
            unique_candidates.append((p, src))
    candidates = unique_candidates

    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) == 0:
        return (None, "NO_PLAN_FOUND")
    return (None, "PLAN_IDENTITY_AMBIGUOUS")


# ---------------------------------------------------------------------------
# 3. validate_plan_ownership
# ---------------------------------------------------------------------------

def validate_plan_ownership(
    plan_path: Path,
    session_id: Optional[str] = None,
) -> tuple[bool, str]:
    """Check whether the plan at ``plan_path`` belongs to the given session.

    A plan is considered owned by the session if:
      - A session-keyed lock file exists for the session_id with a matching plan_path
      - OR the shared active-plan-lock.json references this plan_path with matching session_id

    Returns (allowed: bool, reason: str).
    """
    plan_path_norm = _normalise(str(plan_path))

    # Auto-detect session_id if not provided
    if session_id is None:
        session_id = _get_session_id()

    # Check session-keyed lock
    session_lock_file = _PLAN_LOCKS_DIR / f"{session_id}.json"
    if session_lock_file.exists():
        try:
            lock_data = json.loads(session_lock_file.read_text(encoding="utf-8"))
            lock_path = _normalise(lock_data.get("plan_path", ""))
            if lock_path == plan_path_norm:
                return (True, f"OWNED_BY_SESSION:{session_id}")
            return (
                False,
                f"SESSION_OWNS_DIFFERENT_PLAN: session {session_id} owns "
                f"{lock_data.get('plan_path')} not {plan_path}",
            )
        except (json.JSONDecodeError, OSError) as exc:
            return (False, f"SESSION_LOCK_READ_ERROR:{exc}")

    # Check shared lock as fallback
    if _SHARED_LOCK_PATH.exists():
        try:
            shared = json.loads(_SHARED_LOCK_PATH.read_text(encoding="utf-8"))
            shared_path = _normalise(shared.get("plan_path", ""))
            shared_session = shared.get("session_id", "")
            if shared_path == plan_path_norm and shared_session == session_id:
                return (True, "OWNED_VIA_SHARED_LOCK")
        except (json.JSONDecodeError, OSError):
            pass

    return (False, f"NO_OWNERSHIP_FOUND_FOR_SESSION:{session_id}")


# ---------------------------------------------------------------------------
# 4. validate_plan_mutability
# ---------------------------------------------------------------------------

def validate_plan_mutability(plan_path: Path) -> tuple[bool, str]:
    """Check whether the plan at ``plan_path`` is in a mutable lifecycle state.

    A plan is NOT mutable if:
      - Any lock file records status == TERMINAL_CLOSED for this plan_path
      - The plan's own front-matter has ownership_status == TERMINALLY_LOCKED

    Returns (allowed: bool, reason: str).
    """
    plan_path_norm = _normalise(str(plan_path))

    # Check ALL lock files (not just session-keyed) for TERMINAL_CLOSED
    all_locks = _scan_lock_files(status_filter=None)
    for lock in all_locks:
        lock_path_norm = _normalise(lock.get("plan_path", ""))
        if lock_path_norm == plan_path_norm:
            status = lock.get("status", "")
            if status == "TERMINAL_CLOSED":
                return (
                    False,
                    f"TERMINAL_PLAN_MUTATION_REJECTED: plan is terminally locked "
                    f"(session {lock.get('session_id', 'unknown')}, "
                    f"locked_at {lock.get('updated_at', 'unknown')})",
                )

    # Check plan identity front-matter
    identity = extract_plan_identity(plan_path)
    if identity:
        ownership = identity.get("ownership_status", "")
        if str(ownership).upper() == "TERMINALLY_LOCKED":
            return (
                False,
                "TERMINAL_PLAN_MUTATION_REJECTED: plan_identity.ownership_status == TERMINALLY_LOCKED",
            )
        terminal_lock = identity.get("terminal_lock", False)
        if terminal_lock is True:
            return (
                False,
                "TERMINAL_PLAN_MUTATION_REJECTED: plan_identity.terminal_lock == true",
            )

    # TC-PG-007: Check for durable <!--plan_terminal_lock:--> HTML comment in plan file
    try:
        text = Path(plan_path).read_text(encoding="utf-8", errors="replace")
        if "<!--plan_terminal_lock:" in text:
            return (
                False,
                "TERMINAL_PLAN_MUTATION_REJECTED: plan file contains "
                "<!--plan_terminal_lock:--> durable marker",
            )
    except OSError:
        pass  # File unreadable — skip this check

    return (True, "PLAN_IS_MUTABLE")


# ---------------------------------------------------------------------------
# 5. build_plan_write_event
# ---------------------------------------------------------------------------

def build_plan_write_event(
    plan_path: Path,
    writer: str,
    intent: str,
    allowed: bool,
    reason: str,
    *,
    mission_id: Optional[str] = None,
    run_id: Optional[str] = None,
    lifecycle_stage: Optional[str] = None,
) -> dict:
    """Build a ``plan_write_event:`` audit-trail record.

    Fields match the schema in §8 of the plan governance requirements:
      event_id, timestamp, mission_id, run_id, lifecycle_stage, writer,
      requested_plan_path, resolved_plan_path, actual_written_path,
      resolution_source, ownership_valid, divergence, evidence.
    """
    plan_path_str = str(plan_path)
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mission_id": mission_id or "unknown",
        "run_id": run_id or "unknown",
        "lifecycle_stage": lifecycle_stage or "unknown",
        "writer": writer,
        "intent": intent,
        "requested_plan_path": plan_path_str,
        "resolved_plan_path": plan_path_str,
        "actual_written_path": plan_path_str if allowed else None,
        "resolution_source": "explicit_caller",
        "ownership_valid": allowed,
        "divergence": None if allowed else reason,
        "allowed": allowed,
        "block_reason": None if allowed else reason,
        "evidence": {
            "lock_files_scanned": str(_PLAN_LOCKS_DIR),
            "shared_lock": str(_SHARED_LOCK_PATH),
            "ledger": str(_LEDGER_PATH),
        },
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _normalise(path_str: str) -> str:
    """Normalise a path string for comparison (forward slashes, lowercase on Windows)."""
    return path_str.replace("\\", "/").rstrip("/")


def _resolve_path(raw: str) -> Optional[Path]:
    """Resolve a raw path string to an absolute Path, or None if invalid."""
    if not raw:
        return None
    p = Path(raw)
    if not p.is_absolute():
        p = _REPO_ROOT / p
    return p.resolve() if p else None


def _scan_lock_files(status_filter: Optional[str] = None) -> list[dict]:
    """Return all lock file contents, optionally filtered by status."""
    results: list[dict] = []

    lock_files: list[Path] = []
    if _PLAN_LOCKS_DIR.is_dir():
        lock_files.extend(sorted(_PLAN_LOCKS_DIR.glob("*.json")))
    if _SHARED_LOCK_PATH.exists():
        lock_files.append(_SHARED_LOCK_PATH)

    for lf in lock_files:
        try:
            data = json.loads(lf.read_text(encoding="utf-8"))
            if status_filter is None or data.get("status") == status_filter:
                results.append(data)
        except (json.JSONDecodeError, OSError):
            continue
    return results


def _find_in_ledger(mission_id: str) -> Optional[str]:
    """Search master-plan-memory.md for a ledger entry matching mission_id.

    Returns the plan_path from the matching YAML block, or None.
    """
    try:
        text = _LEDGER_PATH.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None

    # Find YAML blocks that contain the mission_id
    pattern = re.compile(
        r"```yaml\s*\n(.*?)```",
        re.DOTALL,
    )
    for block_match in pattern.finditer(text):
        block = block_match.group(1)
        if f"mission_id: {mission_id}" in block:
            for line in block.splitlines():
                if line.strip().startswith("plan_path:"):
                    _, _, value = line.partition(":")
                    return value.strip()
    return None


def _get_session_id() -> str:
    """Get the current session ID via CCI machinery, or fall back to env/pid."""
    try:
        from continuation_identity import get_or_create_session_identity  # type: ignore[import]
        return get_or_create_session_identity()
    except ImportError:
        pass
    return os.environ.get("CLAUDE_SESSION_ID") or f"pid-{os.getpid()}"


# ---------------------------------------------------------------------------
# CLI entry point (for quick diagnostics)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    print("=== plan_identity.py — diagnostic mode ===")
    print(f"Repo root : {_REPO_ROOT}")
    print(f"Locks dir : {_PLAN_LOCKS_DIR}")
    print()

    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
        identity = extract_plan_identity(target)
        print(f"Identity block for: {target}")
        print(json.dumps(identity, indent=2, default=str) if identity else "  (none found)")
        print()
        allowed, reason = validate_plan_mutability(target)
        print(f"Mutability: {'ALLOWED' if allowed else 'BLOCKED'} — {reason}")
    else:
        path, source = resolve_native_plan_path()
        print(f"Resolved plan path : {path}")
        print(f"Resolution source  : {source}")
