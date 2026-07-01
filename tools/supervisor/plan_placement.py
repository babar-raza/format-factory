"""plan_placement.py - Resolve canonical destination for plan files.

Given a plan filename or type, returns the correct subfolder under plans/.
Used by governance validators for plan root policy enforcement.

V90 validator and plan routing policy enforcement.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent

PLAN_ROOT_ALLOWED = frozenset({"master-plan.md", "master-plan-memory.md", "README.md"})

ROUTING_TABLE = {
    "strategic": "plans/strategic/",
    "healing": "plans/healing/",
    "secondary": "plans/secondary/",
    "per_chat": "plans/.claude/",
    "layer": "plans/layers/",
}


def resolve_plan_destination(filename: str, plan_type: str = "secondary") -> str:
    """Return canonical path for a plan file based on its type.

    Args:
        filename: Plan filename (e.g., "my-new-plan.md")
        plan_type: One of strategic, healing, secondary, per_chat, layer

    Returns:
        Full relative path like "plans/healing/my-new-plan.md"
    """
    if filename in PLAN_ROOT_ALLOWED:
        return f"plans/{filename}"
    folder = ROUTING_TABLE.get(plan_type, "plans/secondary/")
    return f"{folder}{filename}"


def validate_root_policy(repo_root: Path | None = None) -> tuple[bool, list[str]]:
    """Check that only allowed files exist at plans/ root.

    Returns (compliant, violations) where violations is list of unauthorized filenames.
    """
    root = (repo_root or REPO_ROOT) / "plans"
    violations = []
    if not root.exists():
        return (True, [])
    for f in root.iterdir():
        if f.is_dir():
            continue
        if f.name not in PLAN_ROOT_ALLOWED:
            violations.append(str(f.relative_to(repo_root or REPO_ROOT)))
    return (len(violations) == 0, violations)


def migrate_plan_locks(
    repo_root: Path | None = None,
    migration_map: dict[str, str] | None = None,
) -> int:
    """Update plan_path in lock files that reference old paths.

    Args:
        repo_root: Repository root path
        migration_map: Dict mapping old_path -> new_path

    Returns:
        Count of updated lock files.
    """
    _r = repo_root or REPO_ROOT
    if migration_map is None:
        return 0

    locks_dir = _r / ".local" / "supervisor" / "plan-locks"
    shared_lock = _r / ".local" / "supervisor" / "active-plan-lock.json"
    updated = 0

    lock_files = list(locks_dir.glob("*.json")) if locks_dir.exists() else []
    if shared_lock.exists():
        lock_files.append(shared_lock)

    for lf in lock_files:
        try:
            data = json.loads(lf.read_text(encoding="utf-8"))
            old_path = data.get("plan_path", "").replace("\\", "/")
            if old_path in migration_map:
                data["plan_path"] = migration_map[old_path]
                data["path_migrated_from"] = old_path
                lf.write_text(
                    json.dumps(data, indent=2) + "\n", encoding="utf-8"
                )
                updated += 1
        except Exception:
            continue
    return updated


if __name__ == "__main__":
    compliant, violations = validate_root_policy()
    if compliant:
        print("PASS: plans/ root contains only allowed files")
    else:
        print(f"VIOLATIONS ({len(violations)}):")
        for v in violations:
            print(f"  - {v}")
