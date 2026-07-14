"""governance_validators_control_layer.py — V176-V181: Control Layer Validators (TC-OCRD-C6)

V176: validate_evidence_paths_resolve
    FAIL — evidence_paths declared in work items must resolve to existing files.

V177: validate_receipt_claimed_before_closure
    WARN — advisory: PRODUCT_SOURCE items should declare skill_ids.

V178: validate_no_quarantined_plan_source
    FAIL+blocks — if the active plan's source file is quarantined, block sprint.

V179: validate_contradiction_signal_checked
    WARN — advisory: continuation signal should have been checked before sprint start.

V180: validate_gap_not_exhausted
    WARN — advisory: if gap_ledger_ref appears in exhausted gaps, warn per item.

V181: validate_sync_report_fresh
    WARN — advisory: control index sync report should be <24h old.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

try:
    from governance_validators_contract import validator as _validator
except ImportError:
    def _validator(**_kw):  # type: ignore[misc]
        def _wrap(fn):
            return fn
        return _wrap

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


@_validator(rule_id="V176", domain="control_layer",
            description="Evidence paths declared in work items must resolve to existing files")
def validate_evidence_paths_resolve(
    declaration: dict, repo_root: Path | None = None
) -> dict:
    """V176: Declared evidence_paths must resolve to existing files.

    Checks all evidence_paths listed in work items. Files that do not exist
    are reported as failures. Symbolic/relative paths are resolved against repo_root.

    Enforcement: FAIL + blocks_sprint=True when any evidence path is missing.
    If no evidence paths declared: PASS (advisory — not all items require evidence files).
    """
    repo = repo_root or _REPO_ROOT
    all_items = (
        (declaration.get("completed_work_items") or []) +
        (declaration.get("planned_work_items") or [])
    )

    missing: list[dict] = []
    for item in all_items:
        if not isinstance(item, dict):
            continue
        paths = item.get("evidence_paths") or []
        for ep in paths:
            if not ep:
                continue
            resolved = Path(ep) if Path(ep).is_absolute() else repo / ep
            if not resolved.exists():
                missing.append({
                    "item_id": item.get("item_id", item.get("id", "UNKNOWN")),
                    "missing_path": ep,
                })

    if not missing:
        return {
            "validator": "validate_evidence_paths_resolve",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V176: All declared evidence paths resolve to existing files.",
        }

    return {
        "validator": "validate_evidence_paths_resolve",
        "result": "FAIL",
        "blocks_sprint": True,
        "items": missing,
        "summary": (
            f"V176: {len(missing)} declared evidence path(s) do not exist. "
            "Evidence files must be written before declaration submission."
        ),
    }


@_validator(rule_id="V177", domain="control_layer",
            description="PRODUCT_SOURCE items should declare skill_ids (advisory)")
def validate_receipt_claimed_before_closure(
    declaration: dict, repo_root: Path | None = None
) -> dict:
    """V177: PRODUCT_SOURCE items should declare skill_ids (advisory).

    If a PRODUCT_SOURCE item exists with no declared_skill_ids, this is a soft
    signal that the skill-first execution policy may not have been followed.

    Enforcement: WARN-only (blocks_sprint=False).
    """
    all_items = (
        (declaration.get("completed_work_items") or []) +
        (declaration.get("planned_work_items") or [])
    )

    no_skill: list[dict] = []
    for item in all_items:
        if not isinstance(item, dict):
            continue
        if item.get("item_type") not in ("PRODUCT_SOURCE", "PRODUCT_TEST"):
            continue
        if not (item.get("declared_skill_ids") or []):
            no_skill.append({
                "item_id": item.get("item_id", item.get("id", "UNKNOWN")),
                "item_type": item.get("item_type"),
            })

    if not no_skill:
        return {
            "validator": "validate_receipt_claimed_before_closure",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V177: All PRODUCT_SOURCE items declare skill_ids.",
        }

    return {
        "validator": "validate_receipt_claimed_before_closure",
        "result": "WARN",
        "blocks_sprint": False,
        "items": no_skill,
        "summary": (
            f"V177: {len(no_skill)} PRODUCT_SOURCE item(s) have no declared_skill_ids. "
            "Consider using skill-governed execution."
        ),
    }


@_validator(rule_id="V178", domain="control_layer",
            description="Block sprint if active plan source file is quarantined")
def validate_no_quarantined_plan_source(
    declaration: dict, repo_root: Path | None = None
) -> dict:
    """V178: If the active plan source is quarantined, block sprint.

    Checks quarantines table in control-index.db. If any ACTIVE quarantine
    references the plan file declared in the declaration, FAIL+blocks.

    Enforcement: FAIL + blocks_sprint=True if active plan is quarantined.
    WARN_MISSING_CONTROL_INDEX if DB not available.
    """
    repo = repo_root or _REPO_ROOT
    db_path = repo / ".local" / "supervisor" / "control-index.db"

    if not db_path.exists():
        return {
            "validator": "validate_no_quarantined_plan_source",
            "result": "WARN",
            "blocks_sprint": False,
            "items": [],
            "summary": "V178: WARN_MISSING_CONTROL_INDEX — cannot check quarantine status.",
        }

    plan_file = declaration.get("plan_file") or declaration.get("plan_path") or ""

    try:
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        try:
            quarantined = conn.execute(
                "SELECT quarantine_id, artifact_path, severity FROM quarantines "
                "WHERE status = 'ACTIVE' AND artifact_path = ?",
                (plan_file,),
            ).fetchall()
        finally:
            conn.close()
    except Exception as e:
        return {
            "validator": "validate_no_quarantined_plan_source",
            "result": "WARN",
            "blocks_sprint": False,
            "items": [],
            "summary": f"V178: WARN — could not query quarantines: {e}",
        }

    if not quarantined:
        return {
            "validator": "validate_no_quarantined_plan_source",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V178: Active plan source is not quarantined.",
        }

    return {
        "validator": "validate_no_quarantined_plan_source",
        "result": "FAIL",
        "blocks_sprint": True,
        "items": [dict(q) for q in quarantined],
        "summary": (
            f"V178: Plan source '{plan_file}' is QUARANTINED. "
            "Resolve quarantine before proceeding with sprint."
        ),
    }


@_validator(rule_id="V179", domain="control_layer",
            description="Advisory: continuation signal should reflect low contradiction count")
def validate_contradiction_signal_checked(
    declaration: dict, repo_root: Path | None = None
) -> dict:
    """V179: Advisory — continuation signal should reflect low contradiction count.

    Reads continuation-signal.json and warns if critical_contradiction_count > 0.
    This is informational — the declaration acknowledges the state.

    Enforcement: WARN-only (blocks_sprint=False).
    """
    repo = repo_root or _REPO_ROOT
    signal_path = repo / ".local" / "supervisor" / "continuation-signal.json"

    if not signal_path.exists():
        return {
            "validator": "validate_contradiction_signal_checked",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V179: No continuation signal found — contradiction check skipped.",
        }

    try:
        signal = json.loads(signal_path.read_text(encoding="utf-8"))
    except Exception:
        return {
            "validator": "validate_contradiction_signal_checked",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V179: Could not parse continuation signal — skipped.",
        }

    critical_count = int(signal.get("critical_contradiction_count", 0))
    if critical_count == 0:
        return {
            "validator": "validate_contradiction_signal_checked",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V179: No critical contradictions in continuation signal.",
        }

    return {
        "validator": "validate_contradiction_signal_checked",
        "result": "WARN",
        "blocks_sprint": False,
        "items": signal.get("contradiction_summary", []),
        "summary": (
            f"V179: {critical_count} critical contradiction(s) active in continuation signal. "
            "Verify resolution before submitting evidence."
        ),
    }


@_validator(rule_id="V180", domain="control_layer",
            description="Advisory: warn if declared gap_ledger_ref is already exhausted")
def validate_gap_not_exhausted(
    declaration: dict, repo_root: Path | None = None
) -> dict:
    """V180: Advisory — warns if a declared gap_ledger_ref is already exhausted.

    Checks gap_attempts table for gaps with >= 3 failed outcomes. If a work
    item references an exhausted gap, warn (advisory — does not block sprint).

    Enforcement: WARN-only. WARN_MISSING_CONTROL_INDEX if DB not available.
    """
    repo = repo_root or _REPO_ROOT
    db_path = repo / ".local" / "supervisor" / "control-index.db"

    if not db_path.exists():
        return {
            "validator": "validate_gap_not_exhausted",
            "result": "WARN",
            "blocks_sprint": False,
            "items": [],
            "summary": "V180: WARN_MISSING_CONTROL_INDEX — cannot check gap exhaustion.",
        }

    all_items = (
        (declaration.get("completed_work_items") or []) +
        (declaration.get("planned_work_items") or [])
    )
    gap_refs = [
        (item.get("item_id", "UNKNOWN"), item.get("gap_ledger_ref"))
        for item in all_items
        if isinstance(item, dict) and item.get("gap_ledger_ref")
    ]

    if not gap_refs:
        return {
            "validator": "validate_gap_not_exhausted",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V180: No gap_ledger_ref declared — exhaustion check skipped.",
        }

    try:
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                "SELECT gap_id, COUNT(*) as cnt FROM gap_attempts "
                "WHERE outcome IN ('failed', 'rework') "
                "GROUP BY gap_id HAVING cnt >= 3"
            ).fetchall()
            exhausted = {r["gap_id"] for r in rows}
        finally:
            conn.close()
    except Exception:
        exhausted = set()

    exhausted_refs = [
        {"item_id": iid, "gap_id": gref}
        for iid, gref in gap_refs
        if gref in exhausted
    ]

    if not exhausted_refs:
        return {
            "validator": "validate_gap_not_exhausted",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V180: No declared gaps are exhausted.",
        }

    return {
        "validator": "validate_gap_not_exhausted",
        "result": "WARN",
        "blocks_sprint": False,
        "items": exhausted_refs,
        "summary": (
            f"V180: {len(exhausted_refs)} declared gap(s) have >= 3 failed attempts. "
            "Consider selecting a different gap."
        ),
    }


@_validator(rule_id="V181", domain="control_layer",
            description="Advisory: control index sync report should be <24h old")
def validate_sync_report_fresh(
    declaration: dict, repo_root: Path | None = None
) -> dict:
    """V181: Advisory — control index sync report should be <24h old.

    Reads last-sync-report.json. If the report is >24h old or missing, warns.
    This is informational — stale index does not block sprint execution.

    Enforcement: WARN-only (blocks_sprint=False).
    """
    repo = repo_root or _REPO_ROOT
    sync_report_path = repo / ".local" / "supervisor" / "last-sync-report.json"

    if not sync_report_path.exists():
        return {
            "validator": "validate_sync_report_fresh",
            "result": "WARN",
            "blocks_sprint": False,
            "items": [],
            "summary": "V181: No last-sync-report.json found — control index may not be initialized.",
        }

    try:
        report = json.loads(sync_report_path.read_text(encoding="utf-8"))
        completed_at_str = report.get("completed_at", "2000-01-01T00:00:00")
        completed_at = datetime.fromisoformat(completed_at_str.replace("Z", "+00:00"))
        age_hours = (datetime.now(timezone.utc) - completed_at).total_seconds() / 3600
    except Exception as e:
        return {
            "validator": "validate_sync_report_fresh",
            "result": "WARN",
            "blocks_sprint": False,
            "items": [],
            "summary": f"V181: Could not parse last-sync-report.json: {e}",
        }

    if age_hours <= 24:
        return {
            "validator": "validate_sync_report_fresh",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": f"V181: Control index sync is fresh ({age_hours:.1f}h old).",
        }

    return {
        "validator": "validate_sync_report_fresh",
        "result": "WARN",
        "blocks_sprint": False,
        "items": [],
        "summary": (
            f"V181: Control index sync is {age_hours:.0f}h old (threshold: 24h). "
            "Run: python -m tools.supervisor.control_index sync"
        ),
    }
