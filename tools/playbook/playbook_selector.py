"""
playbook_selector.py — Sprint Task Template Selector

FF-PLAYBOOK-SYSTEM-001 (bright-marinating-map), TC-PB-008

Selects the applicable Sprint Task Template for a given work item type.
Returns None (not failure) when no playbook applies — absence of a playbook
is NEVER a blocker for sprint continuation.

Authority boundaries:
  - Selection is ADVISORY ONLY — does not block sprints
  - Missing playbook = log warning, continue without playbook
  - Deprecated playbook = reject (log warning, return None)
  - Never overrides plan authority or continuation logic
  - Best-effort only — all failures return None (never raise to caller)

Usage (standalone):
  python tools/playbook/playbook_selector.py --work-item-type FORMAT_FEATURE_EXPANSION

Usage (programmatic):
  from tools.playbook.playbook_selector import select_playbook
  path = select_playbook(work_item_type="FORMAT_FEATURE_EXPANSION")
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

# ─────────────────────────────────────────────────────────
# Work item type → playbook file mapping
# ─────────────────────────────────────────────────────────

_REPO_ROOT = Path(__file__).parent.parent.parent

_WORK_ITEM_MAP: dict[str, str] = {
    # Sprint Task Templates
    "FORMAT_FEATURE_EXPANSION": "playbooks/format-factory/format-feature-expansion.md",
    "NEW_FORMAT_KICKSTART": "playbooks/format-factory/new-format-kickstart-template.md",
    "PRODUCT_SOURCE_PATCH_BOUNDED": "playbooks/format-factory/product-source-task-template.md",
    "VERTICAL_SLICE_ADVANCEMENT": "playbooks/format-factory/product-source-task-template.md",
    "RELEASE_READINESS_CHECK": "playbooks/format-factory/package-release-readiness.md",
    "PACKAGE_RELEASE_PREP": "playbooks/format-factory/package-release-readiness.md",
    "PIPELINE_INCIDENT_RESPONSE": "playbooks/format-factory/pipeline-incident-response.md",
    "GOV_BLOCK_REMEDIATION": "playbooks/format-factory/pipeline-incident-response.md",
    "TEST_BASELINE_REPAIR": "playbooks/format-factory/pipeline-incident-response.md",
    "AUDIT_HEALING_SPRINT": "playbooks/format-factory/audit-healing-sprint.md",
    "STALE_STATE_REMEDIATION": "playbooks/format-factory/audit-healing-sprint.md",
    "GAP_CLOSURE": "playbooks/format-factory/audit-healing-sprint.md",
    # Acquisition playbooks (family-level)
    "ACQUISITION_ODF_FLAT": "acquisition-packs/_families/odf-flat/playbook.yaml",
}

# Contract pattern for Markdown templates
_CONTRACT_PATTERN = re.compile(
    r"<!--\s*\n(playbook_contract:.*?)-->",
    re.DOTALL,
)


def _parse_markdown_contract(path: Path) -> dict[str, Any] | None:
    """Parse playbook_contract from Markdown HTML comment front-matter."""
    try:
        content = path.read_text(encoding="utf-8")
        m = _CONTRACT_PATTERN.search(content)
        if not m:
            return None
        parsed = yaml.safe_load(m.group(1).strip())
        return parsed.get("playbook_contract") if isinstance(parsed, dict) else None
    except Exception:
        return None


def _parse_yaml_playbook(path: Path) -> dict[str, Any] | None:
    """Parse top-level YAML playbook file."""
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _get_status(path: Path) -> str:
    """Get playbook status from contract or YAML. Returns 'UNKNOWN' on failure."""
    if path.suffix == ".md":
        contract = _parse_markdown_contract(path)
        if contract:
            return str(contract.get("status", "UNKNOWN")).upper()
    elif path.suffix in (".yaml", ".yml"):
        data = _parse_yaml_playbook(path)
        if data:
            return str(data.get("status", "UNKNOWN")).upper()
    return "UNKNOWN"


def select_playbook(
    work_item_type: str,
    log: Any = None,
) -> str | None:
    """
    Select the applicable Sprint Task Template path for a work item type.

    Returns:
        str path (relative to repo root) if applicable playbook found and active.
        None if no applicable playbook, or if playbook is deprecated.
        NEVER raises — all errors return None.

    Args:
        work_item_type: Task classification (e.g., FORMAT_FEATURE_EXPANSION)
        log: Optional callable for logging (defaults to stderr print)
    """
    if log is None:
        def log(msg: str) -> None:
            print(f"[playbook_selector] {msg}", file=sys.stderr)

    if not work_item_type:
        return None

    # Guard against non-string input — never raise, return None
    if not isinstance(work_item_type, str):
        return None

    normalized = work_item_type.upper().strip()
    relative_path = _WORK_ITEM_MAP.get(normalized)

    if not relative_path:
        # No playbook for this work item type — not a failure
        log(f"No applicable playbook for work_item_type='{work_item_type}' — continuing without playbook")
        return None

    full_path = _REPO_ROOT / relative_path
    if not full_path.exists():
        log(f"WARNING: Mapped playbook not found on disk: {relative_path} — continuing without playbook")
        return None

    # Check status
    try:
        status = _get_status(full_path)
    except Exception as e:
        log(f"WARNING: Could not read status from {relative_path}: {e} — continuing without playbook")
        return None

    if status in ("DEPRECATED", "SUPERSEDED", "INVALID", "HISTORICAL"):
        log(f"REJECTED: Playbook '{relative_path}' has status '{status}' — deprecated playbooks cannot generate taskcards")
        return None

    if status not in ("ACTIVE", "PILOT", "PROPOSED", "ACTIVE", "DOCUMENTATION_EXAMPLE_ONLY"):
        log(f"WARNING: Playbook '{relative_path}' has unexpected status '{status}' — treating as no playbook")
        return None

    log(f"Selected playbook: {relative_path} (status={status}) for work_item_type='{work_item_type}'")
    return relative_path


def select_and_validate(
    work_item_type: str,
    log: Any = None,
) -> dict[str, Any]:
    """
    Select playbook and return a structured selection result.
    Always returns a dict — never raises.
    """
    if log is None:
        def log(msg: str) -> None:
            print(f"[playbook_selector] {msg}", file=sys.stderr)

    path = select_playbook(work_item_type=work_item_type, log=log)
    if path is None:
        return {
            "selected": False,
            "work_item_type": work_item_type,
            "playbook_path": None,
            "status": None,
            "authority": "NONE",
            "blocks_sprint": False,
        }

    full_path = _REPO_ROOT / path
    status = _get_status(full_path)

    return {
        "selected": True,
        "work_item_type": work_item_type,
        "playbook_path": path,
        "status": status,
        "authority": "TASK_TEMPLATE",
        "blocks_sprint": False,  # NEVER blocks sprint — advisory only
        "note": "Selection is advisory only. Missing or invalid playbook never blocks continuation.",
    }


def list_supported_types() -> list[str]:
    """Return all work item types that have a registered playbook mapping."""
    return sorted(_WORK_ITEM_MAP.keys())


# ─────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Select Sprint Task Template for a work item type"
    )
    parser.add_argument(
        "--work-item-type",
        required=True,
        help="Work item type (e.g., FORMAT_FEATURE_EXPANSION)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON result",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all supported work item types",
    )
    args = parser.parse_args(argv)

    if args.list:
        print("Supported work item types:")
        for wtype, path in sorted(_WORK_ITEM_MAP.items()):
            print(f"  {wtype:45s} → {path}")
        return 0

    result = select_and_validate(work_item_type=args.work_item_type)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["selected"]:
            print(f"SELECTED: {result['playbook_path']} (status={result['status']})")
        else:
            print(f"NO_PLAYBOOK: No applicable playbook for '{args.work_item_type}'")

    return 0


if __name__ == "__main__":
    sys.exit(main())
