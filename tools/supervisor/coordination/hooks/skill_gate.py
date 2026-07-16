"""skill_gate.py — SFC-GAP-C (2026-07-17): tool-layer skill-resolution check.

Called from gate.py's `_on_pre_file` AFTER the existing coordination-lease logic.
Answers, for a single file path, one of three non-binary verdicts — deliberately
non-binary to avoid false-blocking legitimate work during the staged rollout:

  MANIFEST_COVERING          — a live, unexpired execution manifest (see
                                tools/governance/skills_first/manifest.py)
                                whose allowed_paths covers this file. Always
                                allow.
  NO_SKILL_RESOLVED_FOR_PATH — no active skill's declared path scope
                                (allowed_paths/implementation_paths) covers
                                this file at all. Always allow, NEVER
                                block-eligible — there is no skill to
                                require yet, and blocking here would make
                                the skill-gap workflow itself impossible to
                                bootstrap.
  SKILL_EXISTS_BUT_NO_MANIFEST — a registered active skill's path scope
                                covers this file, but no live manifest does.
                                The ONLY block-eligible tier, and only once
                                this specific check's mode is 'enforcing'
                                (tools.supervisor.coordination.db.get_check_mode,
                                decoupled from the global coordination `mode`).

Design note: this deliberately does NOT reuse
tools/governance/skills_first/resolve.py's operation-description matching —
that function is built to score a natural-language operation string against
route descriptions, and a bare PreToolUse hook only has a file path, no
operation text. Forcing resolve() to work with an empty operation string would
be an unreliable repurposing of a different tool. Instead this module asks a
narrower, more honest question directly answerable from a path alone: "does any
active skill's OWN declared path scope cover this file?" — reusing the same
glob semantics (`closeout.path_allowed`) the closeout gate itself uses, so a
skill's declared ownership means the same thing at every enforcement point.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import NamedTuple

_HERE = Path(__file__).resolve()
_SUPERVISOR_DIR = _HERE.parents[2]
_REPO_ROOT = _HERE.parents[4]
if str(_SUPERVISOR_DIR) not in sys.path:
    sys.path.insert(0, str(_SUPERVISOR_DIR))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

CHECK_ID = "skill_resolution"

MANIFEST_COVERING = "MANIFEST_COVERING"
NO_SKILL_RESOLVED_FOR_PATH = "NO_SKILL_RESOLVED_FOR_PATH"
SKILL_EXISTS_BUT_NO_MANIFEST = "SKILL_EXISTS_BUT_NO_MANIFEST"

_BLOCK_ELIGIBLE = {SKILL_EXISTS_BUT_NO_MANIFEST}


class SkillGateVerdict(NamedTuple):
    tier: str
    detail: str
    block_eligible: bool


def _iter_live_manifests():
    """Yield (path, manifest_dict) for every manifest file that parses.
    Malformed/unreadable manifest files are skipped, not treated as covering
    (fail closed on the manifest's own claim, never on the scan itself)."""
    try:
        from tools.governance.skills_first.manifest import MANIFEST_DIR
    except ImportError:
        return
    if not MANIFEST_DIR.exists():
        return
    for p in MANIFEST_DIR.glob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(data, dict):
            yield p, data


def _manifest_covers(rel_path: str) -> "dict | None":
    """Return the first live, unexpired manifest whose allowed_paths covers
    rel_path, or None. 'Live' = status CREATED or IN_PROGRESS (CLOSED/ABORTED
    manifests no longer authorize anything)."""
    try:
        from tools.governance.skills_first.closeout import path_allowed
        from tools.governance.skills_first.manifest import is_expired
    except ImportError:
        return None
    for _p, m in _iter_live_manifests():
        if m.get("status") not in ("CREATED", "IN_PROGRESS"):
            continue
        if is_expired(m):
            continue
        allowed = m.get("allowed_paths") or []
        if path_allowed(rel_path, allowed):
            return m
    return None


def _skill_scope_covers(rel_path: str) -> "str | None":
    """Return the skill_id of the first ACTIVE skill whose own declared
    allowed_paths/implementation_paths covers rel_path, or None if no
    registered skill's scope reaches this path at all."""
    try:
        from tools.governance.skills_first.closeout import path_allowed
        from tools.governance.skills_first.registries import load_skills
    except ImportError:
        return None
    try:
        skills = load_skills()
    except Exception:
        return None
    for s in skills:
        if not s.is_active:
            continue
        candidate_paths = (s.allowed_paths or []) + (s.implementation_paths or [])
        if candidate_paths and path_allowed(rel_path, candidate_paths):
            return s.skill_id
    return None


def evaluate_path(rel_path: str) -> SkillGateVerdict:
    """Core, side-effect-free evaluation for a single repo-relative path."""
    covering = _manifest_covers(rel_path)
    if covering is not None:
        return SkillGateVerdict(
            MANIFEST_COVERING,
            f"live manifest {covering.get('execution_id')} covers this path",
            False,
        )

    owning_skill = _skill_scope_covers(rel_path)
    if owning_skill is None:
        return SkillGateVerdict(
            NO_SKILL_RESOLVED_FOR_PATH,
            "no active skill's declared path scope covers this file",
            False,
        )

    return SkillGateVerdict(
        SKILL_EXISTS_BUT_NO_MANIFEST,
        f"skill '{owning_skill}' governs this path but no live manifest exists",
        True,
    )
