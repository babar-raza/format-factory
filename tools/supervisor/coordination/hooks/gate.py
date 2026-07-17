"""Claude Code hook gate (TC-COORD-006): the ambient enforcement plane.

One entrypoint dispatching on hook_event_name:
  SessionStart -> auto-register agent bound to session_id (zero ceremony)
  PreToolUse   -> file tools: preflight (auto-claim / attribute / deny);
                  Bash: tripwires for broad staging, destructive cleanup,
                  and known broad generators
  PostToolUse  -> file tools: journal the completed write (attribution)
  SessionEnd   -> release auto-leases, mark agent IDLE

Semantics (plan section 5.3):
- exit 0 allow, exit 2 block (stderr is fed back to the model)
- FAIL-OPEN on any internal error or unknown payload schema, but every
  fail-open appends an incident record -- audited, sprint-failing via V195
- advisory mode never blocks: would-block verdicts go to the advisory log
- FF_COORD_BYPASS=<reason> allows but records a BYPASS event
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path

FILE_TOOLS = {"Edit": "file_path", "Write": "file_path",
              "MultiEdit": "file_path", "NotebookEdit": "notebook_path"}

BROAD_ADD_RE = re.compile(
    r"\bgit\s+add\s+(?:[^|;&]*\s)?(-A\b|--all\b|\.(?:\s|$))")
DESTRUCTIVE_RE = re.compile(
    r"\bgit\s+(clean\b|checkout\s+--\s|checkout\s+\.|restore\b|stash\b"
    r"|reset\s+--hard\b)")
GENERATOR_PATTERNS = (
    ("capability_sync", re.compile(r"tools[/\\]capability_sync[/\\]run_sync\.py")),
    ("readme_sync", re.compile(r"tools[/\\]readme_sync[/\\]run_sync\.py")),
    ("project_status", re.compile(r"tools[/\\]docs[/\\]generate_project_status\.py")),
    ("sync_local_memory", re.compile(r"tools[/\\]supervisor[/\\]sync_local_memory\.py")),
    ("plan_importer", re.compile(r"tools[/\\]supervisor[/\\]plan_importer\.py")),
    # SFC-GAP-B (2026-07-17): known script-based writers of the ~8 hot canonical
    # governance files (skill-registry.yaml, command-registry.yaml, etc. — see
    # tools/governance/hot-governance-files/output-manifest.yaml). These scripts
    # previously bypassed lease/attribution entirely when invoked via Bash.
    # TC-RG-002 (2026-07-17): build_context_pack.py added — writes
    # .supervisor/context-pack.yaml the same ungoverned way, surfaced by the
    # DIRECT-GENERATOR-GAP triage (plans/.claude/sfc-remaining-gaps-closure.md).
    ("hot-governance-files", re.compile(
        r"tools[/\\]supervisor[/\\]sync_skill_command_registry\.py"
        r"|tools[/\\]supervisor[/\\]patch_registry_missing_fields\.py"
        r"|tools[/\\]supervisor[/\\]build_capability_routes\.py"
        r"|tools[/\\]supervisor[/\\]build_context_pack\.py")),
)
READONLY_BASH_HINT = re.compile(
    r"^\s*(git\s+(status|log|diff|show|rev-parse|branch)\b|ls\b|dir\b|cat\b"
    r"|type\b|grep\b|rg\b|find\b|python\s+-c\s+[\"']print)")


def _incident(root: Path | None, kind: str, detail: dict) -> None:
    """Append an incident line; never raises."""
    try:
        from ..ids import iso
        line = json.dumps({"ts": iso(), "kind": kind, **detail},
                          default=str)
        target = (root or Path(tempfile.gettempdir())) / "hook-incidents.jsonl"
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except Exception:
        pass


def _advisory(root: Path, detail: dict) -> None:
    try:
        from ..ids import iso
        with (root / "advisory-log.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"ts": iso(), **detail}, default=str) + "\n")
    except Exception:
        pass


def _db_event(root: Path, verb: str, detail: dict, actor=None) -> None:
    try:
        from ..db import connect, emit_event, immediate
        conn = connect(root)
        try:
            with immediate(conn):
                emit_event(conn, "system", "hook", verb, actor=actor,
                           detail=detail)
        finally:
            conn.close()
    except Exception:
        pass


def _fast_skip_path(path: str, wt_path: str, root: Path) -> bool:
    """Coordinate only writes INSIDE the worktree; within it, skip runtime
    dirs. Paths outside the worktree (scratchpad, system temp, coordination
    root) are not production writes and are never gated."""
    p = os.path.normcase(os.path.realpath(path)).replace("\\", "/")
    wt = os.path.normcase(os.path.realpath(wt_path)).replace("\\", "/")
    if not (p == wt or p.startswith(wt + "/")):
        return True
    rel = p[len(wt) + 1:] if p != wt else ""
    for marker in (".git/", ".local/", "__pycache__/"):
        if rel.startswith(marker) or f"/{marker}" in rel + "/":
            return True
    return False


def _block(reason: str) -> int:
    sys.stderr.write(reason.strip() + "\n")
    return 2


def _bypass_reason() -> str | None:
    val = os.environ.get("FF_COORD_BYPASS")
    return val if val and val.strip() else None


def process(raw: str, root: Path | None = None) -> int:
    """Testable core. Returns the process exit code."""
    from ..db import connect, ensure_db, get_mode
    from ..root import db_path, resolve_coordination_root, worktree_identity

    try:
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError("payload is not an object")
    except (ValueError, TypeError) as exc:
        if root is None:
            try:
                root = resolve_coordination_root()
            except Exception:
                root = None
        _incident(root, "FAIL_OPEN",
                  {"stage": "parse", "error": str(exc)})
        return 0

    try:
        event = payload.get("hook_event_name", "")
        session_id = payload.get("session_id") or ""
        cwd = payload.get("cwd") or os.getcwd()
        root = root or resolve_coordination_root(cwd)
        wt_id, wt_path = worktree_identity(cwd)

        if event == "SessionStart":
            return _on_session_start(root, cwd, session_id)
        if event == "SessionEnd":
            return _on_session_end(root, cwd, session_id)
        if event not in ("PreToolUse", "PostToolUse"):
            # Unknown/newer harness event: fail open WITH incident (P6).
            _incident(root, "FAIL_OPEN",
                      {"stage": "dispatch", "event": event})
            return 0

        if not db_path(root).exists():
            return 0  # system not initialized yet; SessionStart creates it
        conn = connect(root)
        try:
            mode = get_mode(conn)
        finally:
            conn.close()
        if mode == "off":
            return 0

        tool = payload.get("tool_name", "")
        tool_input = payload.get("tool_input") or {}

        if event == "PostToolUse":
            if tool in FILE_TOOLS:
                _on_post_write(root, cwd, session_id,
                               tool_input.get(FILE_TOOLS[tool], ""))
            return 0

        # PreToolUse
        if tool in FILE_TOOLS:
            return _on_pre_file(root, cwd, wt_path, session_id, mode,
                                tool, tool_input.get(FILE_TOOLS[tool], ""))
        if tool == "Bash":
            return _on_pre_bash(root, cwd, session_id, mode,
                                tool_input.get("command", "") or "")
        return 0
    except Exception as exc:
        _incident(root, "FAIL_OPEN",
                  {"stage": "process", "error": f"{type(exc).__name__}: {exc}"})
        if root is not None:
            _db_event(root, "FAIL_OPEN",
                      {"error": f"{type(exc).__name__}: {exc}"})
        return 0


def _agent_for_session(root: Path, cwd: str, session_id: str,
                       create: bool = True):
    """(agent_id, token) for this harness session; ambient auto-register."""
    from ..registry import AgentRegistry
    registry = AgentRegistry(root, start=cwd)
    ident = registry.read_runtime_identity(session_id=session_id)
    if ident is not None:
        return ident["agent_id"], ident["token"]
    if not session_id or not create:
        return None
    ra = registry.register("claude-code", agent_type="interactive",
                           execution_mode="interactive",
                           session_id=session_id)
    return ra.agent_id, ra.token


def _on_session_start(root: Path, cwd: str, session_id: str) -> int:
    from ..db import ensure_db
    from ..leases import LeaseManager

    ensure_db(root)
    if session_id:
        _agent_for_session(root, cwd, session_id, create=True)
    try:
        LeaseManager(root, start=cwd).reap()
    except Exception:
        pass
    return 0


def _on_session_end(root: Path, cwd: str, session_id: str) -> int:
    from ..registry import AgentRegistry

    try:
        registry = AgentRegistry(root, start=cwd)
        ident = registry.read_runtime_identity(session_id=session_id)
        if ident:
            registry.idle(ident["agent_id"], ident["token"])
    except Exception as exc:
        _incident(root, "FAIL_OPEN", {"stage": "session-end",
                                      "error": str(exc)})
    return 0


def _on_pre_file(root: Path, cwd: str, wt_path: str, session_id: str,
                 mode: str, tool: str, file_path: str) -> int:
    from ..preflight import preflight

    if not file_path or _fast_skip_path(file_path, wt_path, root):
        return 0
    bypass = _bypass_reason()
    if bypass:
        _db_event(root, "BYPASS", {"file": file_path, "reason": bypass,
                                   "session": session_id})
        return 0

    ident = _agent_for_session(root, cwd, session_id, create=True)
    if ident is None:
        verdict = ("no session identity; cannot bind writes to an agent."
                   " Register explicitly:"
                   " python -m tools.supervisor.coordination register"
                   " --provider <p>")
        if mode == "enforcing":
            _db_event(root, "HOOK_BLOCK", {"file": file_path,
                                           "reason": "unregistered"})
            return _block("[coordination] BLOCKED: " + verdict)
        _advisory(root, {"tool": tool, "file": file_path,
                         "would_block": True, "reason": "unregistered"})
        return 0

    aid, tok = ident
    res = preflight(file_path, "edit", root=root, start=cwd,
                    agent_id=aid, token=tok)
    if res.allowed:
        return _on_pre_file_skill_gate(root, wt_path, tool, file_path, aid)
    if mode == "enforcing":
        _db_event(root, "HOOK_BLOCK",
                  {"file": file_path, "reason": res.reason,
                   "classification": res.classification,
                   "conflict_id": res.conflict_id}, actor=aid)
        return _block(f"[coordination] BLOCKED ({res.exit_code}): {res.reason}")
    _advisory(root, {"tool": tool, "file": file_path, "would_block": True,
                     "reason": res.reason,
                     "classification": res.classification,
                     "agent": aid})
    return 0


def _on_pre_file_skill_gate(root: Path, wt_path: str, tool: str,
                            file_path: str, agent_id: str) -> int:
    """SFC-GAP-C: independent per-check skill-resolution gate, decoupled from
    the coordination `mode` gate above via get_check_mode(CHECK_ID) (own
    settings row, defaults to 'advisory'). LOAD-BEARING: this function only
    ever runs once the coordination gate has ALREADY allowed the write -- it
    can add an additional, independently-toggled restriction on top of an
    allowed write, but can never override a coordination denial, and a bug
    here (any exception) fails OPEN with an incident record, never silently
    escalates to block."""
    try:
        from ..db import connect, get_check_mode
        from . import skill_gate
    except ImportError:
        return 0  # SFC package not present in this checkout; fail open

    p = os.path.normcase(os.path.realpath(file_path)).replace("\\", "/")
    wt = os.path.normcase(os.path.realpath(wt_path)).replace("\\", "/")
    rel = p[len(wt) + 1:] if p != wt and p.startswith(wt + "/") else p

    try:
        verdict = skill_gate.evaluate_path(rel)
    except Exception as exc:
        _incident(root, "FAIL_OPEN", {"stage": "skill_gate",
                                      "error": f"{type(exc).__name__}: {exc}"})
        return 0  # a bug in a NEW check must never block existing work

    if not verdict.block_eligible:
        return 0  # MANIFEST_COVERING / NO_SKILL_RESOLVED_FOR_PATH: always allow

    conn = connect(root)
    try:
        check_mode = get_check_mode(conn, skill_gate.CHECK_ID)
    finally:
        conn.close()

    payload = {"tool": tool, "file": rel, "check": skill_gate.CHECK_ID,
              "tier": verdict.tier, "detail": verdict.detail,
              "agent": agent_id}
    if check_mode == "enforcing":
        payload["would_block"] = False
        _db_event(root, "HOOK_BLOCK", payload, actor=agent_id)
        return _block(f"[skill-gate] BLOCKED: {verdict.detail}")
    payload["would_block"] = True
    _advisory(root, payload)
    return 0


def _live_other_agents(root: Path, agent_id: str | None) -> int:
    from ..db import connect
    conn = connect(root)
    try:
        row = conn.execute(
            "SELECT COUNT(*) AS n FROM agents WHERE status IN"
            " ('ACTIVE','IDLE','STALE_SUSPECT') AND agent_id != ?",
            (agent_id or "",)).fetchone()
        return row["n"]
    finally:
        conn.close()


def _has_command_lease(root: Path, agent_id: str, gen_id: str) -> bool:
    from ..db import connect
    conn = connect(root)
    try:
        row = conn.execute(
            "SELECT 1 FROM leases WHERE agent_id=? AND status IN"
            " ('ACTIVE','STALE') AND resource_type='command' AND"
            " resource_key=?", (agent_id, f"cmd:{gen_id}")).fetchone()
        return row is not None
    finally:
        conn.close()


def _on_pre_bash(root: Path, cwd: str, session_id: str, mode: str,
                 command: str) -> int:
    if READONLY_BASH_HINT.match(command):
        return 0
    broad = BROAD_ADD_RE.search(command)
    destructive = DESTRUCTIVE_RE.search(command)
    generator = next((gid for gid, pat in GENERATOR_PATTERNS
                      if pat.search(command)), None)
    if not (broad or destructive or generator):
        return 0

    bypass = _bypass_reason()
    if bypass:
        _db_event(root, "BYPASS", {"command": command[:400],
                                   "reason": bypass, "session": session_id})
        return 0

    ident = _agent_for_session(root, cwd, session_id, create=True)
    aid = ident[0] if ident else None
    others = _live_other_agents(root, aid)

    verdict: str | None = None
    kind = None
    if broad and others > 0:
        kind = "broad-staging"
        verdict = (f"broad staging ('{broad.group(0).strip()}') is unsafe"
                   f" while {others} other agent(s) are live -- another"
                   " agent's uncommitted work could be swept into your"
                   " commit. Stage an explicit reviewed file list instead"
                   " (git add <path> ...).")
    elif destructive and others > 0:
        kind = "destructive-cleanup"
        verdict = (f"'{destructive.group(0).strip()}' can destroy another"
                   f" agent's uncommitted work ({others} other agent(s)"
                   " live). Never clean or revert unexplained changes;"
                   " inspect owners first: python -m"
                   " tools.supervisor.coordination status")
    elif generator and others > 0 and (aid is None or
                                       not _has_command_lease(root, aid,
                                                              generator)):
        kind = "unguarded-generator"
        verdict = (f"generator '{generator}' writes a broad shared output"
                   " set; run it through the guard so its outputs are"
                   " leased: python -m tools.supervisor.coordination"
                   f" guard-run --generator-id {generator} --manifest-file"
                   f" tools/<pkg>/output-manifest.yaml -- <command>")

    if verdict is None:
        return 0
    if mode == "enforcing":
        _db_event(root, "HOOK_BLOCK", {"command": command[:400],
                                       "kind": kind}, actor=aid)
        return _block("[coordination] BLOCKED: " + verdict)
    _advisory(root, {"tool": "Bash", "command": command[:400],
                     "would_block": True, "kind": kind, "agent": aid})
    return 0


def _on_post_write(root: Path, cwd: str, session_id: str,
                   file_path: str) -> None:
    from ..preflight import record_write
    from ..root import worktree_identity

    if not file_path:
        return
    _, wt_path = worktree_identity(cwd)
    if _fast_skip_path(file_path, wt_path, root):
        return
    ident = _agent_for_session(root, cwd, session_id, create=False)
    if ident is None:
        return
    try:
        record_write(file_path, "edit", root=root, start=cwd,
                     agent_id=ident[0], token=ident[1], source="hook")
    except Exception as exc:
        _incident(root, "FAIL_OPEN", {"stage": "post-write",
                                      "file": file_path, "error": str(exc)})


def main() -> int:
    raw = sys.stdin.read()
    return process(raw)


if __name__ == "__main__" and __package__ in (None, ""):
    # Direct-script invocation (hook command). Bootstrap package imports.
    _here = Path(__file__).resolve()
    sys.path.insert(0, str(_here.parents[2]))
    from coordination.hooks.gate import main as _pkg_main  # noqa: E402

    sys.exit(_pkg_main())
elif __name__ == "__main__":
    sys.exit(main())
