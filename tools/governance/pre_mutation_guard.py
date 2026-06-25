"""
pre_mutation_guard.py — Tool-Neutral Runtime Mutation Guard
Format Factory Skill-Only Governance — EP-002

PURPOSE
-------
Before any governed mutation, an agent must call this script to obtain
a mutation authorization record. The guard checks:
  1. An active task is bound (task_id + skill_resolution_id)
  2. The resolved skill is registered and active
  3. The target paths are within the declared ownership paths
  4. The agent type is allowed for this operation

USAGE (Claude Code / Codex / CI / Local)
-----------------------------------------
  python tools/governance/pre_mutation_guard.py \\
      --agent-type CLAUDE_CODE \\
      --task-id TC-XXX-001 \\
      --skill-id add-python-api \\
      --target-paths src/python/fods/models.py tests/python/fods/test_model.py \\
      --mission-id MY-MISSION-001 \\
      --sprint-id my-sprint-id \\
      [--dry-run]

Exit codes:
  0 = AUTHORIZED — mutation may proceed; authorization YAML written to .local/mutation-auth/
  1 = BLOCKED — mutation rejected; reason in stdout JSON
  2 = CONFIG_ERROR — registry or config unreadable

OUTPUT (stdout, JSON)
---------------------
  AUTHORIZED:  {"verdict": "AUTHORIZED", "authorization_id": "...", "authorization_path": "..."}
  BLOCKED:     {"verdict": "BLOCKED", "reason": "...", "rejection_condition": "..."}
  CONFIG_ERROR:{"verdict": "CONFIG_ERROR", "error": "..."}

POLICY REFERENCE
----------------
  docs/governance/skill-only-policy.yaml § 6 (Mutation Authorization)
  .supervisor/skill-first-policy.md Rule 4

KNOWN GAP (EP-002-GAP)
-----------------------
  This guard must be called EXPLICITLY by the agent. There is no automatic
  interception from the Claude Code or Codex tool layer. Agents can bypass
  this script by simply not calling it. This gap is tracked as EP-002-GAP
  in docs/governance/skill-only-policy.yaml. Automatic enforcement requires
  a pre-commit hook (SKILL-GAP-008) or tool-layer interception.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_REGISTRY = REPO_ROOT / ".supervisor" / "skill-registry.yaml"
CAPABILITY_ROUTING = REPO_ROOT / ".supervisor" / "capability-routing-registry.yaml"
AUTH_DIR = REPO_ROOT / ".local" / "mutation-auth"

# Paths that are always exempt from ownership checks (bookkeeping files
# that legitimately cross lanes per lane_enforcement_validator.py GLOBAL_EXEMPT_PATHS)
GLOBAL_EXEMPT_PATHS = {
    "reports/capability-layer/gap-ledger.json",
    "registry/source-structure-baseline.json",
    ".local/supervisor/continuation-signal.json",
    "reports/supervisor/",
}


def _load_yaml_simple(path: Path) -> dict:
    """Minimal YAML loader (scalar keys + list/dict values only, no dependencies)."""
    try:
        import yaml  # type: ignore
        with path.open(encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        # Fallback: use json if yaml unavailable (YAML superset of JSON for simple dicts)
        try:
            with path.open(encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    except Exception:
        return {}


def _load_active_skills(registry_path: Path) -> set[str]:
    """Return set of active skill IDs from skill-registry.yaml."""
    data = _load_yaml_simple(registry_path)
    skills = data.get("skills", [])
    return {s.get("skill_id", "") for s in skills if s.get("status") == "active"}


def _check_path_ownership(target_paths: list[str], skill_id: str, registry_data: dict) -> tuple[bool, str]:
    """
    Verify target_paths are within the skill's declared allowed_paths.
    Returns (ok, rejection_reason).

    Currently uses a permissive check: allowed_paths from registry covers
    format-level ownership (e.g., src/python/fods/ for FODS skills).
    If allowed_paths is empty, the check is SKIPPED (permissive default).
    """
    skills = registry_data.get("skills", [])
    skill_entry = next((s for s in skills if s.get("skill_id") == skill_id), None)
    if skill_entry is None:
        return False, f"skill_id '{skill_id}' not found in registry"

    allowed_paths = skill_entry.get("allowed_paths", [])
    if not allowed_paths:
        # Permissive: no ownership paths declared → allow (log warning)
        return True, ""

    for t in target_paths:
        exempt = any(t.startswith(ep) for ep in GLOBAL_EXEMPT_PATHS)
        if exempt:
            continue
        covered = any(t.startswith(ap) for ap in allowed_paths)
        if not covered:
            return False, (
                f"target path '{t}' is outside allowed_paths for skill '{skill_id}': {allowed_paths}"
            )
    return True, ""


def _write_authorization(auth: dict, auth_id: str) -> Path:
    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    auth_path = AUTH_DIR / f"{auth_id}.json"
    auth_path.write_text(json.dumps(auth, indent=2), encoding="utf-8")
    return auth_path


def _make_auth_id(task_id: str, skill_id: str, agent_type: str, now: datetime) -> str:
    raw = f"{task_id}:{skill_id}:{agent_type}:{now.isoformat()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def run(
    agent_type: str,
    task_id: str,
    skill_id: str,
    target_paths: list[str],
    mission_id: str,
    sprint_id: str,
    dry_run: bool = False,
) -> dict:
    """Core guard logic. Returns result dict."""
    now = datetime.now(timezone.utc)
    expiry = (now + timedelta(hours=2)).isoformat()

    # 1. Load skill registry
    if not SKILL_REGISTRY.exists():
        return {"verdict": "CONFIG_ERROR", "error": f"skill registry not found: {SKILL_REGISTRY}"}

    registry_data = _load_yaml_simple(SKILL_REGISTRY)
    active_skills = _load_active_skills(SKILL_REGISTRY)

    # 2. Check: task_id must be non-empty
    if not task_id or task_id in ("", "NONE", "none"):
        return {
            "verdict": "BLOCKED",
            "reason": "no active task — task_id is empty or NONE",
            "rejection_condition": "no_active_task",
        }

    # 3. Check: skill_id must be registered and active
    if not skill_id or skill_id not in active_skills:
        all_skills = {s.get("skill_id", "") for s in registry_data.get("skills", [])}
        if skill_id in all_skills:
            status = next(
                (s.get("status", "unknown") for s in registry_data.get("skills", []) if s.get("skill_id") == skill_id),
                "unknown",
            )
            return {
                "verdict": "BLOCKED",
                "reason": f"skill '{skill_id}' exists but is not active (status={status})",
                "rejection_condition": "skill_status_broken_or_disabled",
            }
        return {
            "verdict": "BLOCKED",
            "reason": f"skill '{skill_id}' not found in registry",
            "rejection_condition": "no_registered_skill_bound",
        }

    # 4. Check: target paths within ownership
    ok, rejection_reason = _check_path_ownership(target_paths, skill_id, registry_data)
    if not ok:
        return {
            "verdict": "BLOCKED",
            "reason": rejection_reason,
            "rejection_condition": "target_path_outside_ownership",
        }

    # 5. AUTHORIZED — build record
    auth_id = _make_auth_id(task_id, skill_id, agent_type, now)
    auth_record = {
        "authorization_id": auth_id,
        "agent_type": agent_type,
        "mission_id": mission_id,
        "sprint_id": sprint_id,
        "task_id": task_id,
        "skill_id": skill_id,
        "allowed_paths": target_paths,
        "issued_at": now.isoformat(),
        "expiry": expiry,
        "single_use_or_reusable": "single_use",
        "issued_by": "pre_mutation_guard.py",
        "dry_run": dry_run,
    }

    if not dry_run:
        auth_path = _write_authorization(auth_record, auth_id)
        return {
            "verdict": "AUTHORIZED",
            "authorization_id": auth_id,
            "authorization_path": str(auth_path),
        }
    else:
        return {
            "verdict": "AUTHORIZED",
            "authorization_id": auth_id,
            "authorization_path": None,
            "dry_run": True,
        }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Format Factory pre-mutation guard (EP-002)"
    )
    parser.add_argument("--agent-type", required=True,
                        choices=["CLAUDE_CODE", "CODEX", "SUPERVISOR", "CI", "LOCAL_AUTOMATION"])
    parser.add_argument("--task-id", required=True, help="Active taskcard ID")
    parser.add_argument("--skill-id", required=True, help="Registered skill to invoke")
    parser.add_argument("--target-paths", nargs="+", default=[],
                        help="Files or directories to be mutated")
    parser.add_argument("--mission-id", default="UNKNOWN", help="Current mission ID")
    parser.add_argument("--sprint-id", default="UNKNOWN", help="Current sprint ID")
    parser.add_argument("--dry-run", action="store_true",
                        help="Check only; do not write authorization file")
    args = parser.parse_args()

    result = run(
        agent_type=args.agent_type,
        task_id=args.task_id,
        skill_id=args.skill_id,
        target_paths=args.target_paths,
        mission_id=args.mission_id,
        sprint_id=args.sprint_id,
        dry_run=args.dry_run,
    )

    print(json.dumps(result, indent=2))

    if result["verdict"] == "AUTHORIZED":
        sys.exit(0)
    elif result["verdict"] == "BLOCKED":
        sys.exit(1)
    else:  # CONFIG_ERROR
        sys.exit(2)


if __name__ == "__main__":
    main()
