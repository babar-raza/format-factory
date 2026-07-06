"""governance_validators_layers.py — Layer control plane governance validators V83-V86.

Extracted as a standalone module to keep governance_validators.py within its LOC cap.
These validators enforce the plans/layers/ permanent control plane contracts.
All are WARN-level (never FAIL) during the bootstrap phase to avoid blocking
existing sprints while the control plane is being established.

V83: validate_primary_layer_classified — PRODUCT_SOURCE items should include primary_layer_id
V84: validate_permanent_layer_plan_exists — if primary_layer_id present, layer file must exist
V85: validate_prework_log_present — PRODUCT_SOURCE items should have a work_log_id in evidence
V86: validate_layer_task_registered — sprint task_id should appear in task-register.yaml

Created: TC-LP-024 (2026-06-26)
"""
from __future__ import annotations
from governance_validators_contract import validator  # noqa: F401

from pathlib import Path

# Canonical repo root (two parents up from tools/supervisor/)
_DEFAULT_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


@validator(rule_id="V_VALIDATE_PRIMARY_LAYER_CLASSIFIED", domain="layers")
def validate_primary_layer_classified(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V83 (TC-LP-024): PRODUCT_SOURCE items should include primary_layer_id field.

    WARN-only during bootstrap phase. Does not block sprint execution.
    """
    _r = repo_root or _DEFAULT_REPO_ROOT
    items_missing = []
    for item in declaration.get("planned_work_items", []):
        if not isinstance(item, dict):
            continue
        if item.get("item_type") != "PRODUCT_SOURCE":
            continue
        if not item.get("primary_layer_id"):
            items_missing.append({
                "work_item_id": item.get("work_item_id", "unknown"),
                "item_type": item.get("item_type"),
                "issue": "missing primary_layer_id",
            })
    if items_missing:
        return {
            "validator": "validate_primary_layer_classified",
            "result": "WARN",
            "items": items_missing,
            "summary": (
                f"V83: {len(items_missing)} PRODUCT_SOURCE item(s) missing primary_layer_id. "
                f"Add primary_layer_id field per plans/layers/validation-policy-layer.md"
            ),
            "blocks_sprint": False,
        }
    return {
        "validator": "validate_primary_layer_classified",
        "result": "PASS",
        "items": [],
        "summary": "V83: All PRODUCT_SOURCE items have primary_layer_id classified",
        "blocks_sprint": False,
    }


@validator(rule_id="V_VALIDATE_PERMANENT_LAYER_PLAN_EXISTS", domain="layers")
def validate_permanent_layer_plan_exists(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V84 (TC-LP-024): If primary_layer_id is present, plans/layers/<slug>.md must exist.

    Reads plans/layers/index.yaml to resolve layer_id to permanent_plan_path.
    WARN-only during bootstrap phase. Does not block sprint execution.
    """
    _r = repo_root or _DEFAULT_REPO_ROOT
    index_path = _r / "plans" / "layers" / "index.yaml"
    if not index_path.exists():
        return {
            "validator": "validate_permanent_layer_plan_exists",
            "result": "PASS",
            "items": [],
            "summary": "V84: plans/layers/index.yaml not found — layer plan check skipped",
            "blocks_sprint": False,
        }

    try:
        import yaml as _yaml  # noqa: PLC0415
        index_data = _yaml.safe_load(index_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {
            "validator": "validate_permanent_layer_plan_exists",
            "result": "PASS",
            "items": [],
            "summary": "V84: Could not parse index.yaml — layer plan check skipped",
            "blocks_sprint": False,
        }

    # Build lookup: layer_id -> permanent_plan_path
    layer_lookup: dict[str, str] = {}
    for entry in index_data.get("layers", []):
        if isinstance(entry, dict) and entry.get("layer_id") and entry.get("permanent_plan_path"):
            layer_lookup[entry["layer_id"]] = entry["permanent_plan_path"]

    items_missing = []
    seen_layer_ids: set[str] = set()
    for item in declaration.get("planned_work_items", []):
        if not isinstance(item, dict):
            continue
        layer_id = item.get("primary_layer_id")
        if not layer_id or layer_id in seen_layer_ids:
            continue
        seen_layer_ids.add(layer_id)
        plan_path = layer_lookup.get(layer_id)
        if plan_path is None:
            items_missing.append({
                "layer_id": layer_id,
                "issue": f"layer_id {layer_id} not found in plans/layers/index.yaml",
            })
        elif not (_r / plan_path).exists():
            items_missing.append({
                "layer_id": layer_id,
                "permanent_plan_path": plan_path,
                "issue": f"permanent layer plan file not found on disk: {plan_path}",
            })

    if items_missing:
        return {
            "validator": "validate_permanent_layer_plan_exists",
            "result": "WARN",
            "items": items_missing,
            "summary": (
                f"V84: {len(items_missing)} layer(s) referenced in declaration have no "
                f"permanent plan file. Run /create-permanent-layer-plan to bootstrap."
            ),
            "blocks_sprint": False,
        }
    return {
        "validator": "validate_permanent_layer_plan_exists",
        "result": "PASS",
        "items": [],
        "summary": "V84: All referenced layers have permanent plan files",
        "blocks_sprint": False,
    }


@validator(rule_id="V_VALIDATE_PREWORK_LOG_PRESENT", domain="layers")
def validate_prework_log_present(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V85 (TC-LP-024): PRODUCT_SOURCE items should reference a layer work log entry.

    Checks for work_log_id field (or provenance_chain entry referencing layer work log)
    in PRODUCT_SOURCE planned_work_items. WARN-only during bootstrap phase.
    """
    _r = repo_root or _DEFAULT_REPO_ROOT  # noqa: F841
    items_missing = []
    for item in declaration.get("planned_work_items", []):
        if not isinstance(item, dict):
            continue
        if item.get("item_type") != "PRODUCT_SOURCE":
            continue
        # Check for work_log_id field or provenance_chain with layer_work_log ref
        has_work_log_ref = bool(item.get("work_log_id"))
        if not has_work_log_ref:
            chain = item.get("provenance_chain", [])
            if isinstance(chain, list):
                has_work_log_ref = any(
                    isinstance(c, dict) and "layer_work_log" in str(c.get("source_type", ""))
                    for c in chain
                )
        if not has_work_log_ref:
            items_missing.append({
                "work_item_id": item.get("work_item_id", "unknown"),
                "item_type": item.get("item_type"),
                "issue": "no work_log_id or layer_work_log provenance chain entry",
            })
    if items_missing:
        return {
            "validator": "validate_prework_log_present",
            "result": "WARN",
            "items": items_missing,
            "summary": (
                f"V85: {len(items_missing)} PRODUCT_SOURCE item(s) missing layer work log reference. "
                f"Use /append-layer-work-log and add work_log_id to declaration."
            ),
            "blocks_sprint": False,
        }
    return {
        "validator": "validate_prework_log_present",
        "result": "PASS",
        "items": [],
        "summary": "V85: All PRODUCT_SOURCE items have layer work log reference",
        "blocks_sprint": False,
    }


@validator(rule_id="V_VALIDATE_LAYER_TASK_REGISTERED", domain="layers")
def validate_layer_task_registered(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V86 (TC-LP-024): Tasks cited in the declaration should appear in task-register.yaml.

    Reads plans/layers/task-register.yaml and checks that any task_id field in
    planned_work_items appears there. WARN-only during bootstrap phase.
    """
    _r = repo_root or _DEFAULT_REPO_ROOT
    register_path = _r / "plans" / "layers" / "task-register.yaml"
    if not register_path.exists():
        return {
            "validator": "validate_layer_task_registered",
            "result": "PASS",
            "items": [],
            "summary": "V86: plans/layers/task-register.yaml not found — task register check skipped",
            "blocks_sprint": False,
        }

    try:
        import yaml as _yaml  # noqa: PLC0415
        register_data = _yaml.safe_load(register_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {
            "validator": "validate_layer_task_registered",
            "result": "PASS",
            "items": [],
            "summary": "V86: Could not parse task-register.yaml — task register check skipped",
            "blocks_sprint": False,
        }

    registered_ids: set[str] = {
        t.get("task_id", "")
        for t in register_data.get("tasks", [])
        if isinstance(t, dict) and t.get("task_id")
    }

    items_missing = []
    for item in declaration.get("planned_work_items", []):
        if not isinstance(item, dict):
            continue
        task_id = item.get("task_id") or item.get("work_item_id", "")
        # Only check if task_id looks like a layer task (TC- prefix)
        if not task_id or not task_id.startswith("TC-"):
            continue
        if task_id not in registered_ids:
            items_missing.append({
                "task_id": task_id,
                "work_item_id": item.get("work_item_id", "unknown"),
                "issue": f"{task_id} not found in plans/layers/task-register.yaml",
            })
    if items_missing:
        return {
            "validator": "validate_layer_task_registered",
            "result": "WARN",
            "items": items_missing,
            "summary": (
                f"V86: {len(items_missing)} task(s) not in plans/layers/task-register.yaml. "
                f"Use /register-layer-task to register them."
            ),
            "blocks_sprint": False,
        }
    return {
        "validator": "validate_layer_task_registered",
        "result": "PASS",
        "items": [],
        "summary": "V86: All TC-* task IDs are registered in task-register.yaml",
        "blocks_sprint": False,
    }
