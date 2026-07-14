"""playbook_drift_checker.py — Post-grading drift detection (TC-PBHP-003).

Checks whether a sprint declaration's work items show any evidence of following
their applicable playbook phases. Returns PLAYBOOK_DRIFT findings (WARN-only,
never blocking). Called from autonomous_cycle.py after grading completes.
"""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING


def check_playbook_drift(declaration: dict, repo_root: Path) -> list[dict]:
    """Post-grading drift check.

    For each work item with an applicable playbook, checks whether evidence paths
    or notes mention the playbook's required phases (simple string membership check).
    Returns a list of PLAYBOOK_DRIFT findings (may be empty). Never raises.
    """
    findings = []
    try:
        import sys as _sys
        _sys.path.insert(0, str(repo_root / "tools" / "playbook"))
        from playbook_selector import select_playbook
        from generate_playbook_taskcards import parse_contract

        for item in declaration.get("planned_work_items", []):
            item_type = item.get("item_type", "")
            if not item_type:
                continue
            path = select_playbook(item_type)
            if not path:
                continue
            contract = parse_contract(Path(repo_root / path))
            if not contract or contract.get("status") != "ACTIVE":
                continue
            phases = contract.get("phases", [])
            if not phases:
                continue

            evidence_text = " ".join(
                str(p) for p in item.get("evidence_paths", [])
            ) + " " + str(item.get("notes", ""))

            phases_seen = [p for p in phases if p.lower() in evidence_text.lower()]
            if not phases_seen:
                findings.append({
                    "finding_type": "PLAYBOOK_DRIFT",
                    "work_item_id": item.get("item_id", ""),
                    "work_item_type": item_type,
                    "applicable_playbook": path,
                    "required_phases": phases,
                    "phases_evidenced": [],
                    "description": (
                        f"Playbook '{path}' was applicable for {item_type} "
                        f"but none of its {len(phases)} required phases appear "
                        f"in the item's evidence paths or notes."
                    ),
                    "severity": "WARN",
                    "blocks_sprint": False,
                })
    except Exception as e:
        findings.append({
            "finding_type": "PLAYBOOK_DRIFT_CHECK_ERROR",
            "error": str(e),
            "severity": "INFO",
            "blocks_sprint": False,
        })
    return findings
