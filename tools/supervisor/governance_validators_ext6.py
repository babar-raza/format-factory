"""governance_validators_ext6.py — V224: Backfill Completeness (TC-GOV-V224-001)

V224: validate_backfill_completeness
    WARN when a format has a migration map with actionable entries but no backfill plan.
    Checks reports/qname-migration/ for {fmt}-migration-map.json and {fmt}-backfill-plan.yaml pairs.
"""

from __future__ import annotations

import json
from pathlib import Path

from governance_validators_contract import validator


@validator(
    rule_id="V224",
    domain="governance",
    description="Formats with actionable qname migration maps should have backfill plans",
)
def validate_backfill_completeness(
    declaration: dict,
    repo_root: "Path | None" = None,
) -> dict:
    root = Path(repo_root) if repo_root else Path(".")
    migration_dir = root / "reports" / "qname-migration"
    violations: list[str] = []

    if not migration_dir.is_dir():
        return {
            "validator": "validate_backfill_completeness",
            "result": "PASS",
            "blocks_sprint": False,
            "violations": [],
            "summary": "V224: no migration directory — nothing to check",
        }

    for map_file in sorted(migration_dir.glob("*-migration-map.json")):
        fmt = map_file.name.replace("-migration-map.json", "")
        try:
            data = json.loads(map_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        entries = data.get("entries", [])
        has_actionable = any(
            e.get("action_required", "NONE") != "NONE" for e in entries
        )
        if not has_actionable:
            continue

        plan_path = migration_dir / f"{fmt}-backfill-plan.yaml"
        if not plan_path.exists() or plan_path.stat().st_size == 0:
            violations.append(f"{fmt}: migration map has actionable entries but no backfill plan")

    passed = len(violations) == 0
    return {
        "validator": "validate_backfill_completeness",
        "result": "PASS" if passed else "WARN",
        "blocks_sprint": False,
        "violations": violations,
        "summary": f"V224: {'passed' if passed else f'{len(violations)} format(s) missing backfill plans'}",
    }
