"""Staged-set validation for the pre-commit choke point (TC-COORD-010).

Fail-closed, provider-agnostic: whatever agent (or human) staged the files,
committing content that is under another live agent's write lease, or whose
resource carries an unresolved OPEN conflict, is blocked. The existing
`.local/exceptions/*.yaml` bypass contract of pre-commit-skill-guard applies
at the hook wrapper level, not here.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

from .db import connect
from .errors import ResourceEscape
from .preflight import resolve_identity
from .registry import AgentRegistry
from .root import (canonical_resource, db_path, resolve_coordination_root,
                   worktree_identity)


def _staged_files(repo: str | Path) -> list[str]:
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--no-renames"],
        cwd=str(repo), capture_output=True, text=True, timeout=30)
    if out.returncode != 0:
        raise RuntimeError(f"git diff --cached failed: {out.stderr.strip()}")
    return [l.strip() for l in out.stdout.splitlines() if l.strip()]


def precommit_check(root: Path | None = None,
                    staged_files: list[str] | None = None,
                    repo: str | Path | None = None,
                    session_id: str | None = None) -> dict:
    root = root or resolve_coordination_root(repo)
    wt_id, wt_path = worktree_identity(repo)
    repo = repo or wt_path

    if not db_path(root).exists():
        return {"ok": True, "checked": 0, "violations": [],
                "note": "coordination db absent; nothing to enforce"}

    if staged_files is None:
        staged_files = _staged_files(repo)
    if not staged_files:
        return {"ok": True, "checked": 0, "violations": []}

    registry = AgentRegistry(root, start=repo)
    ident = resolve_identity(registry, session_id=session_id)
    own_agent = ident[0] if ident else None

    conn = connect(root)
    violations: list[dict] = []
    try:
        from .leases import LeaseManager
        lm = LeaseManager(root, start=repo)
        for f in staged_files:
            try:
                key, display = canonical_resource(f, wt_path)
            except ResourceEscape:
                violations.append({
                    "file": f, "kind": "path-escape",
                    "message": f"staged path escapes the worktree: {f}"})
                continue
            for other in lm._overlapping_live(conn, key, wt_id,
                                              exclude_agent=own_agent):
                if other["mode"] in ("EXCLUSIVE_WRITE", "SRSW", "APPEND"):
                    violations.append({
                        "file": display, "kind": "foreign-lease",
                        "owner": other["agent_id"],
                        "lease_id": other["lease_id"],
                        "task": other["task_id"],
                        "message": (
                            f"'{display}' is under live lease"
                            f" {other['lease_id']} of agent"
                            f" {other['agent_id']}"
                            f" (task {other['task_id'] or '-'}); do not"
                            " commit another agent's in-progress work")})
                    break
            open_conf = conn.execute(
                "SELECT conflict_id, conflict_type, safe_action FROM"
                " conflicts WHERE resource_key=? AND resolution_state='OPEN'",
                (key,)).fetchone()
            if open_conf is not None:
                violations.append({
                    "file": display, "kind": "unresolved-conflict",
                    "conflict_id": open_conf["conflict_id"],
                    "message": (
                        f"'{display}' has unresolved conflict"
                        f" {open_conf['conflict_id']}"
                        f" ({open_conf['conflict_type']}); resolve it first:"
                        " python -m tools.supervisor.coordination conflicts"
                        f" resolve --id {open_conf['conflict_id']} ...")})
    finally:
        conn.close()

    return {"ok": not violations, "checked": len(staged_files),
            "violations": violations, "own_agent": own_agent}
