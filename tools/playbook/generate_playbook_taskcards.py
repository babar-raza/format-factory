"""
generate_playbook_taskcards.py — Sprint Task Template Taskcard Generator

FF-PLAYBOOK-SYSTEM-001 (bright-marinating-map), TC-PB-007

Reads machine-readable YAML front-matter (playbook_contract) from Markdown Sprint Task
Templates and generates bounded governed taskcards with provenance.

Authority boundaries:
  - Does NOT approve gates
  - Does NOT mark work complete
  - Does NOT override plan authority
  - Every generated taskcard preserves: playbook_id, playbook_version, plan_id, gap_ids,
    allowed_paths, forbidden_paths, validation, rollback, evidence_root

Usage:
  python tools/playbook/generate_playbook_taskcards.py \\
    --playbook playbooks/format-factory/format-feature-expansion.md \\
    --plan-id FF-PLAYBOOK-SYSTEM-001 \\
    --gap-ids GAP-PB-001 GAP-PB-002 \\
    --parameters format_name=tsv function_name=export_to_csv \\
    --output .local/taskcards/tc-pb-generated.yaml

Exit codes:
  0 = taskcards generated successfully
  1 = validation failure (missing required parameters, deprecated playbook)
  2 = error (file not found, parse error)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


# ─────────────────────────────────────────────────────────
# Front-matter parser
# ─────────────────────────────────────────────────────────

_CONTRACT_PATTERN = re.compile(
    r"<!--\s*\n(playbook_contract:.*?)-->",
    re.DOTALL,
)


def parse_contract(playbook_path: Path) -> dict[str, Any]:
    """Parse playbook_contract YAML from HTML comment front-matter."""
    content = playbook_path.read_text(encoding="utf-8")
    m = _CONTRACT_PATTERN.search(content)
    if not m:
        raise ValueError(
            f"No playbook_contract front-matter found in {playbook_path}. "
            "Expected HTML comment block starting with 'playbook_contract:'"
        )
    raw_yaml = m.group(1).strip()
    parsed = yaml.safe_load(raw_yaml)
    if not isinstance(parsed, dict) or "playbook_contract" not in parsed:
        raise ValueError(
            f"playbook_contract block not found in YAML from {playbook_path}"
        )
    return parsed["playbook_contract"]


# ─────────────────────────────────────────────────────────
# Contract validation
# ─────────────────────────────────────────────────────────

REQUIRED_CONTRACT_FIELDS = [
    "playbook_id",
    "version",
    "status",
    "category",
    "owner_layer",
    "authority",
    "required_inputs",
    "allowed_paths",
    "forbidden_paths",
    "validation",
    "evidence_requirements",
    "rollback",
    "stop_conditions",
    "limitations",
]


def validate_contract(contract: dict[str, Any]) -> list[str]:
    """Return list of validation errors. Empty = valid."""
    errors = []
    for field in REQUIRED_CONTRACT_FIELDS:
        if field not in contract:
            errors.append(f"Missing required contract field: {field}")

    status = contract.get("status", "")
    if status == "DEPRECATED":
        errors.append(
            f"Playbook '{contract.get('playbook_id')}' is DEPRECATED — "
            "cannot generate taskcards from deprecated playbooks"
        )
    elif status not in ("ACTIVE", "PILOT"):
        errors.append(
            f"Playbook status is '{status}' — must be ACTIVE or PILOT to generate taskcards"
        )

    authority = contract.get("authority", "")
    forbidden_authorities = ("ACQUISITION_REPLAY",)
    if authority in forbidden_authorities:
        errors.append(
            f"Authority '{authority}' is not eligible for taskcard generation via this tool. "
            "Acquisition playbooks use tools/playbook/replay_acquisition_playbook.py"
        )

    limitations = contract.get("limitations", [])
    has_no_gate_approval = any(
        "gate approval" in lim.lower() for lim in limitations
    )
    if not has_no_gate_approval:
        errors.append(
            "Contract limitations must explicitly include 'No gate approval authority'"
        )

    return errors


# ─────────────────────────────────────────────────────────
# Parameter resolution
# ─────────────────────────────────────────────────────────

def resolve_parameters(
    contract: dict[str, Any],
    raw_params: list[str],
) -> tuple[dict[str, str], list[str]]:
    """
    Parse key=value parameters and check required_inputs.
    Returns (resolved_params, missing_required_inputs).
    """
    params: dict[str, str] = {}
    for kv in raw_params:
        if "=" not in kv:
            raise ValueError(f"Parameter must be in key=value format: '{kv}'")
        k, _, v = kv.partition("=")
        params[k.strip()] = v.strip()

    required_inputs = contract.get("required_inputs", [])
    missing = [inp for inp in required_inputs if inp not in params]
    return params, missing


# ─────────────────────────────────────────────────────────
# Taskcard generation
# ─────────────────────────────────────────────────────────

def generate_taskcards(
    contract: dict[str, Any],
    plan_id: str,
    gap_ids: list[str],
    parameters: dict[str, str],
    evidence_root: str | None = None,
) -> list[dict[str, Any]]:
    """
    Generate bounded governed taskcards from a validated contract.
    Each taskcard preserves full provenance.
    """
    playbook_id = contract["playbook_id"]
    playbook_version = contract["version"]
    phases = contract.get("phases", ["execute"])
    task_types = contract.get("task_types", ["TASK"])

    base_evidence_root = evidence_root or f".local/evidences/{playbook_id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    taskcards = []
    for i, phase in enumerate(phases, start=1):
        taskcard_id = f"TC-{playbook_id.upper()}-{i:03d}-{uuid.uuid4().hex[:6].upper()}"
        tc: dict[str, Any] = {
            # Provenance — must be present in every generated taskcard
            "playbook_id": playbook_id,
            "playbook_version": playbook_version,
            "plan_id": plan_id,
            "gap_ids": gap_ids,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generator": "tools/playbook/generate_playbook_taskcards.py",
            # Taskcard identity
            "taskcard_id": taskcard_id,
            "phase": phase,
            "phase_index": i,
            "total_phases": len(phases),
            # Execution constraints — preserved from contract
            "parameters": parameters,
            "allowed_paths": contract.get("allowed_paths", []),
            "forbidden_paths": contract.get("forbidden_paths", []),
            "required_skills": contract.get("required_skills", []),
            "required_commands": contract.get("required_commands", []),
            "task_types": task_types,
            # Validation and evidence — preserved from contract
            "validation": contract.get("validation", {}),
            "evidence_requirements": contract.get("evidence_requirements", []),
            "evidence_root": base_evidence_root,
            # Safety — preserved from contract
            "rollback": contract.get("rollback", ""),
            "stop_conditions": contract.get("stop_conditions", []),
            # Authority constraints — explicit in every taskcard
            "authority_constraints": {
                "no_gate_approval": True,
                "no_mark_work_complete_without_evidence": True,
                "no_plan_override": True,
                "no_evidence_contract_replacement": True,
                "limitations": contract.get("limitations", []),
            },
            # Status
            "status": "OPEN",
            "owner_layer": contract.get("owner_layer", ""),
        }
        taskcards.append(tc)

    return taskcards


# ─────────────────────────────────────────────────────────
# Binding record
# ─────────────────────────────────────────────────────────

def build_binding_record(
    contract: dict[str, Any],
    plan_id: str,
    gap_ids: list[str],
    parameters: dict[str, str],
    taskcards: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build playbook_task_binding record for the full generation run."""
    return {
        "schema": "playbook-task-binding/1.0",
        "binding_id": f"BIND-{uuid.uuid4().hex[:8].upper()}",
        "playbook_id": contract["playbook_id"],
        "playbook_version": contract["version"],
        "plan_id": plan_id,
        "gap_ids": gap_ids,
        "parameters": parameters,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "tools/playbook/generate_playbook_taskcards.py",
        "taskcards_generated": len(taskcards),
        "taskcard_ids": [tc["taskcard_id"] for tc in taskcards],
        "authority_statement": (
            "Taskcards generated from Sprint Task Template. "
            "Does NOT approve gates, does NOT mark work complete, "
            "does NOT replace evidence contracts or plan authority."
        ),
        "taskcards": taskcards,
    }


# ─────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate bounded governed taskcards from a Sprint Task Template"
    )
    parser.add_argument(
        "--playbook",
        required=True,
        help="Path to Markdown Sprint Task Template (must have playbook_contract front-matter)",
    )
    parser.add_argument(
        "--plan-id",
        required=True,
        help="Plan ID providing authority for this taskcard generation (e.g., FF-PLAYBOOK-SYSTEM-001)",
    )
    parser.add_argument(
        "--gap-ids",
        nargs="*",
        default=[],
        help="Gap IDs authorizing this taskcard generation",
    )
    parser.add_argument(
        "--parameters",
        nargs="*",
        default=[],
        help="key=value parameters for the playbook (e.g., format_name=tsv function_name=export_to_csv)",
    )
    parser.add_argument(
        "--output",
        help="Output path for generated taskcards YAML (default: stdout)",
    )
    parser.add_argument(
        "--evidence-root",
        help="Override evidence root path in generated taskcards",
    )
    parser.add_argument(
        "--format",
        choices=["yaml", "json"],
        default="yaml",
        help="Output format (default: yaml)",
    )
    args = parser.parse_args(argv)

    playbook_path = Path(args.playbook)
    if not playbook_path.exists():
        print(f"ERROR: Playbook not found: {playbook_path}", file=sys.stderr)
        return 2

    # Parse contract
    try:
        contract = parse_contract(playbook_path)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"ERROR: Failed to parse contract from {playbook_path}: {e}", file=sys.stderr)
        return 2

    # Validate contract
    contract_errors = validate_contract(contract)
    if contract_errors:
        print("VALIDATION FAILED:", file=sys.stderr)
        for err in contract_errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    # Resolve parameters
    try:
        params, missing = resolve_parameters(contract, args.parameters)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    if missing:
        print("VALIDATION FAILED: Missing required inputs:", file=sys.stderr)
        for inp in missing:
            print(f"  - {inp}", file=sys.stderr)
        print(
            f"\nPlaybook '{contract['playbook_id']}' requires: "
            + ", ".join(contract.get("required_inputs", [])),
            file=sys.stderr,
        )
        return 1

    # Generate taskcards
    taskcards = generate_taskcards(
        contract=contract,
        plan_id=args.plan_id,
        gap_ids=args.gap_ids,
        parameters=params,
        evidence_root=args.evidence_root,
    )

    # Build binding record
    binding = build_binding_record(
        contract=contract,
        plan_id=args.plan_id,
        gap_ids=args.gap_ids,
        parameters=params,
        taskcards=taskcards,
    )

    # Output
    if args.format == "json":
        output_text = json.dumps(binding, indent=2, default=str)
    else:
        output_text = yaml.dump(binding, default_flow_style=False, sort_keys=False, allow_unicode=True)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output_text, encoding="utf-8")
        print(f"Generated {len(taskcards)} taskcard(s) → {output_path}", file=sys.stderr)
    else:
        print(output_text)

    print(
        f"PLAYBOOK_TASKCARD_GENERATION: PASS | playbook={contract['playbook_id']} "
        f"version={contract['version']} taskcards={len(taskcards)} plan={args.plan_id}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
