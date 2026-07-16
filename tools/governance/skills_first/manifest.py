"""Skills-First Control — execution manifest.

The concrete "skill-resolution record + execution manifest" that the skill-only
policy references but never had a tested implementation for. A manifest is
created (status CREATED) BEFORE material work, binding {task, agent, operation,
selected skills + their content hashes, command + hash, allowed/forbidden paths,
validators, tests, evidence requirements}. It is closed (status CLOSED) only via
the closeout gate.

Fail-closed: create_manifest refuses to bind a skill that is not registered+active
or a command file whose hash cannot be computed. validate_manifest returns a list
of schema violations (empty == valid). No network, no third-party deps beyond the
schema check being pure-python (jsonschema optional).

CLI:
  python -m tools.governance.skills_first.manifest create \
      --task-id TC-X --agent-type CLAUDE_CODE --operation "modify machinery" \
      --skill add-python-api --allowed-paths tools/governance/**  [--write]
  python -m tools.governance.skills_first.manifest validate <path>
  python -m tools.governance.skills_first.manifest show <execution_id>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .registries import REPO_ROOT, RegistryError, load_skills

MANIFEST_DIR = REPO_ROOT / ".local" / "skills-first" / "manifests"
SCHEMA_FILE = REPO_ROOT / ".supervisor" / "schemas" / "execution-manifest.schema.json"
SCHEMA_CONST = "skills-first-control/execution-manifest@1"

# SFC-GAP-C (2026-07-17): manifest TTL. Without an expiry, a manifest created
# by a crashed/abandoned task stays "live" forever, which would make a
# tool-layer check for "a live manifest covers this path" (Gap C's skill_gate)
# a hollow security property. Default window is hours, not days — a manifest
# is meant to authorize ONE bounded unit of work, not stand in indefinitely
# for a skill binding. Additive: old manifests written before this field
# existed have no `expires_at` and are treated as ALREADY EXPIRED (fail
# closed, forcing explicit re-creation) rather than perpetually live.
DEFAULT_TTL_HOURS = 4

_REQUIRED = [
    "schema", "execution_id", "task_id", "agent_type", "requested_operation",
    "selected_skill_ids", "skill_hashes", "allowed_paths", "status", "created_at",
    "expires_at",
]
_STATUSES = {"CREATED", "IN_PROGRESS", "CLOSED", "ABORTED"}
_AGENTS = {"CLAUDE_CODE", "CODEX", "SUPERVISOR", "CI", "LOCAL_AUTOMATION"}
_DECISIONS = {
    "REUSE_EXACT_MATCH", "REUSE_PARAMETERIZED_MATCH", "COMPOSE_EXISTING_SKILLS",
    "REPAIR_EXISTING_SKILL", "EXTEND_EXISTING_SKILL", "CREATE_MISSING_MICRO_SKILL",
}


class ManifestError(RuntimeError):
    """Raised on an unsatisfiable manifest request (fail-closed)."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _execution_id(task_id: str, skills: list[str], now: str) -> str:
    raw = f"{task_id}:{','.join(sorted(skills))}:{now}"
    return "sfx-" + hashlib.sha256(raw.encode()).hexdigest()[:16]


def create_manifest(
    task_id: str,
    agent_type: str,
    requested_operation: str,
    selected_skill_ids: list[str],
    allowed_paths: list[str],
    *,
    forbidden_paths: list[str] | None = None,
    affected_paths: list[str] | None = None,
    affected_layers: list[str] | None = None,
    resolution_decision: str = "REUSE_EXACT_MATCH",
    resolution_rationale: str = "",
    required_validators: list[str] | None = None,
    required_tests: list[str] | None = None,
    evidence_requirements: list[str] | None = None,
    mission_id: str = "UNKNOWN",
    sprint_id: str = "UNKNOWN",
    agent_instance: str = "",
    composition_order: list[str] | None = None,
    ttl_hours: float = DEFAULT_TTL_HOURS,
    write: bool = False,
) -> dict[str, Any]:
    """Build (and optionally persist) an execution manifest. Fail-closed on
    unregistered/inactive skills, empty skill list, or empty allowed_paths."""
    if agent_type not in _AGENTS:
        raise ManifestError(f"invalid agent_type: {agent_type}")
    if not task_id:
        raise ManifestError("task_id is required")
    selected_skill_ids = [s for s in (selected_skill_ids or []) if s and s.strip()]
    allowed_paths = [p for p in (allowed_paths or []) if p and p.strip()]
    forbidden_paths = [p for p in (forbidden_paths or []) if p and p.strip()]
    if not selected_skill_ids:
        raise ManifestError("at least one skill must be resolved before mutation")
    if not allowed_paths:
        raise ManifestError("allowed_paths must be non-empty (no unbounded mutation)")
    if resolution_decision not in _DECISIONS:
        raise ManifestError(f"invalid resolution_decision: {resolution_decision}")
    if ttl_hours <= 0:
        raise ManifestError(f"ttl_hours must be positive, got {ttl_hours}")

    skills = {s.skill_id: s for s in load_skills()}
    skill_hashes: dict[str, str] = {}
    selected_command = ""
    command_hash = ""
    for sid in selected_skill_ids:
        s = skills.get(sid)
        if s is None:
            raise ManifestError(f"skill '{sid}' is not registered")
        if not s.is_active:
            raise ManifestError(f"skill '{sid}' is not active (status={s.status})")
        cmd_path = REPO_ROOT / s.command_file if s.command_file else None
        if cmd_path is None or not cmd_path.exists():
            raise ManifestError(
                f"skill '{sid}' command_file missing: {s.command_file!r}")
        h = hashlib.sha256(cmd_path.read_bytes()).hexdigest()
        skill_hashes[sid] = h
        if not selected_command:
            selected_command = s.command
            command_hash = h

    now = _now()
    now_dt = datetime.now(timezone.utc)
    expires_at = (now_dt + timedelta(hours=ttl_hours)).isoformat()
    manifest = {
        "schema": SCHEMA_CONST,
        "execution_id": _execution_id(task_id, selected_skill_ids, now),
        "task_id": task_id,
        "agent_type": agent_type,
        "agent_instance": agent_instance,
        "mission_id": mission_id,
        "sprint_id": sprint_id,
        "requested_operation": requested_operation,
        "affected_layers": affected_layers or [],
        "affected_paths": affected_paths or [],
        "selected_skill_ids": list(selected_skill_ids),
        "skill_hashes": skill_hashes,
        "selected_command": selected_command,
        "command_hash": command_hash,
        "composition_order": composition_order or list(selected_skill_ids),
        "resolution_decision": resolution_decision,
        "resolution_rationale": resolution_rationale,
        "preconditions": [],
        "allowed_paths": list(allowed_paths),
        "forbidden_paths": forbidden_paths or [],
        "required_validators": required_validators or [],
        "required_tests": required_tests or [],
        "evidence_requirements": evidence_requirements or [],
        "exceptions": [],
        "status": "CREATED",
        "final_outcome": "",
        "created_at": now,
        "updated_at": now,
        "expires_at": expires_at,
    }
    # Self-validate before returning (never emit an invalid manifest).
    errs = validate_manifest(manifest)
    if errs:
        raise ManifestError("internal: generated manifest invalid: " + "; ".join(errs))
    if write:
        path = manifest_path(manifest["execution_id"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def manifest_path(execution_id: str) -> Path:
    return MANIFEST_DIR / f"{execution_id}.json"


def load_manifest(execution_id_or_path: str) -> dict[str, Any]:
    p = Path(execution_id_or_path)
    if not p.exists():
        p = manifest_path(execution_id_or_path)
    if not p.exists():
        raise ManifestError(f"manifest not found: {execution_id_or_path}")
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        raise ManifestError(f"manifest not readable: {exc}") from exc
    if not isinstance(data, dict):
        raise ManifestError("manifest is not an object")
    return data


def validate_manifest(m: dict[str, Any]) -> list[str]:
    """Pure schema/consistency check. Returns list of violations ([] == valid)."""
    errs: list[str] = []
    if not isinstance(m, dict):
        return ["manifest is not an object"]
    for k in _REQUIRED:
        if k not in m or m[k] in (None, "", []):
            errs.append(f"missing/empty required field: {k}")
    if m.get("schema") != SCHEMA_CONST:
        errs.append(f"schema must be {SCHEMA_CONST!r}")
    if m.get("agent_type") not in _AGENTS:
        errs.append(f"invalid agent_type: {m.get('agent_type')}")
    if m.get("status") not in _STATUSES:
        errs.append(f"invalid status: {m.get('status')}")
    if m.get("resolution_decision") and m["resolution_decision"] not in _DECISIONS:
        errs.append(f"invalid resolution_decision: {m['resolution_decision']}")
    sids = m.get("selected_skill_ids") or []
    hashes = m.get("skill_hashes") or {}
    if isinstance(sids, list) and isinstance(hashes, dict):
        for sid in sids:
            if sid not in hashes:
                errs.append(f"selected skill '{sid}' has no captured skill hash")
    if not isinstance(m.get("allowed_paths"), list) or not m.get("allowed_paths"):
        errs.append("allowed_paths must be a non-empty list")
    return errs


def is_expired(m: dict[str, Any], now: datetime | None = None) -> bool:
    """True if the manifest's TTL has elapsed (or it has no expires_at at all —
    fail closed: a manifest written before this field existed, or with a
    malformed timestamp, is treated as already expired, never as perpetually
    live). Used by closeout.py and the Gap C tool-layer check to decide
    whether a manifest still authorizes its allowed_paths."""
    now = now or datetime.now(timezone.utc)
    raw = m.get("expires_at")
    if not raw:
        return True
    try:
        exp = datetime.fromisoformat(raw)
    except (TypeError, ValueError):
        return True
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    return now >= exp


def set_status(execution_id: str, status: str, final_outcome: str = "") -> dict[str, Any]:
    if status not in _STATUSES:
        raise ManifestError(f"invalid status: {status}")
    m = load_manifest(execution_id)
    m["status"] = status
    m["updated_at"] = _now()
    if status in ("CLOSED", "ABORTED"):
        m["closed_at"] = _now()
        m["final_outcome"] = final_outcome
    manifest_path(execution_id).write_text(json.dumps(m, indent=2) + "\n",
                                           encoding="utf-8")
    return m


def _main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Skills-First execution manifest")
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("create")
    c.add_argument("--task-id", required=True)
    c.add_argument("--agent-type", required=True)
    c.add_argument("--operation", required=True)
    c.add_argument("--skill", dest="skills", action="append", required=True)
    c.add_argument("--allowed-paths", nargs="+", required=True)
    c.add_argument("--forbidden-paths", nargs="*", default=[])
    c.add_argument("--decision", default="REUSE_EXACT_MATCH")
    c.add_argument("--rationale", default="")
    c.add_argument("--mission-id", default="UNKNOWN")
    c.add_argument("--sprint-id", default="UNKNOWN")
    c.add_argument("--write", action="store_true")

    v = sub.add_parser("validate")
    v.add_argument("path")

    s = sub.add_parser("show")
    s.add_argument("execution_id")

    args = ap.parse_args(argv)
    try:
        if args.cmd == "create":
            m = create_manifest(
                task_id=args.task_id, agent_type=args.agent_type,
                requested_operation=args.operation, selected_skill_ids=args.skills,
                allowed_paths=args.allowed_paths, forbidden_paths=args.forbidden_paths,
                resolution_decision=args.decision, resolution_rationale=args.rationale,
                mission_id=args.mission_id, sprint_id=args.sprint_id, write=args.write)
            print(json.dumps(m, indent=2))
            return 0
        if args.cmd == "validate":
            m = load_manifest(args.path)
            errs = validate_manifest(m)
            print(json.dumps({"valid": not errs, "errors": errs}, indent=2))
            return 0 if not errs else 1
        if args.cmd == "show":
            print(json.dumps(load_manifest(args.execution_id), indent=2))
            return 0
    except (ManifestError, RegistryError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(_main())
