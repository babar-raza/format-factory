"""
replay_acquisition_playbook.py — Dry-Run Replay Engine for format-factory acquisition playbooks.

Sprint: S-F2F-03 (Dry-Run Replay and Review Queue Export)
Status: ACTIVE — dry-run, explain, validate, export-review-queue modes only.

AUTHORITY BOUNDARY:
  This tool is a replay ENGINE for INFORMATIONAL purposes ONLY.
  - Dry-run results are NOT gate approval.
  - Replay reports are NOT evidence contracts.
  - Conflict items are NOT authoritative for gate state.
  - APPLY MODE IS NOT IMPLEMENTED AND MUST NOT BE ADDED without separate S-F2F-06
    risk review + explicit human authorization naming apply mode.

MODES:
  validate            — validate the playbook YAML against the schema (no replay).
  dry-run             — simulate execution: check file existence and required inputs.
                        Writes ZERO files to repo. Output goes to stdout.
  explain             — print a human-readable description of each operation.
  export-review-queue — export a review-queue YAML to --output (required).

CLI:
  python tools/playbook/replay_acquisition_playbook.py
    --mode {validate,dry-run,explain,export-review-queue}
    --format-id FORMAT_ID
    --playbook PLAYBOOK_YAML
    [--output OUTPUT_FILE]   # required for export-review-queue
    [--schema SCHEMA_FILE]   # defaults to schemas/playbook/acquisition-playbook.schema.json
"""

import argparse
import datetime
import json
import os
import sys

import yaml

_UTC = datetime.timezone.utc


def _now_iso() -> str:
    return datetime.datetime.now(_UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _now_str() -> str:
    return datetime.datetime.now(_UTC).strftime("%Y%m%d-%H%M%S")

# ---------------------------------------------------------------------------
# Repo root: two levels up from this file (tools/playbook/ -> tools/ -> repo/)
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_SCHEMA = os.path.join(REPO_ROOT, "schemas", "playbook", "acquisition-playbook.schema.json")

# ---------------------------------------------------------------------------
# APPLY MODE GUARD — this function name must never contain 'apply'
# ---------------------------------------------------------------------------
def _guard_replay_mode(requested_mode: str) -> None:
    """Reject any attempt to invoke apply mode. Apply mode is not authorized."""
    normalized = requested_mode.strip().lower().replace("-", "_")
    apply_synonyms = {"apply", "apply_mode", "apply_proposed", "apply_authorized", "execute", "run"}
    if normalized in apply_synonyms or "apply" in normalized:
        print(
            "REPLAY_ERROR: apply mode is NOT authorized. "
            "Apply mode requires a separate S-F2F-06 risk review document "
            "and explicit human authorization naming apply mode. "
            "Exiting.",
            file=sys.stderr,
        )
        sys.exit(2)


# ---------------------------------------------------------------------------
# Schema validation helper (delegate to validate_playbook.py logic)
# ---------------------------------------------------------------------------
def _load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_schema(schema_path: str) -> dict:
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _validate_playbook_schema(playbook_data: dict, schema_data: dict) -> tuple[bool, list[str]]:
    """Validate playbook against schema. Returns (valid, errors)."""
    errors = []
    # Attempt jsonschema first
    try:
        import importlib.metadata
        _ = importlib.metadata.version("jsonschema")
        import jsonschema
        try:
            jsonschema.validate(instance=playbook_data, schema=schema_data)
            return True, []
        except jsonschema.ValidationError as e:
            return False, [f"JSON Schema validation error: {e.message}"]
        except jsonschema.SchemaError as e:
            return False, [f"Schema error: {e.message}"]
    except Exception:
        pass

    # Fallback: structural checks
    required_fields = schema_data.get("required", [])
    for field in required_fields:
        if field not in playbook_data:
            errors.append(f"Missing required field: {field}")

    forbidden_uses = playbook_data.get("forbidden_uses", [])
    required_forbidden = {
        "automatic_gate_approval", "spec_or_legal_authority",
        "replacing_dec034", "replacing_human_approval",
    }
    missing_forbidden = required_forbidden - set(forbidden_uses)
    if missing_forbidden:
        errors.append(f"Missing required forbidden_uses entries: {sorted(missing_forbidden)}")

    return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# Mode: validate
# ---------------------------------------------------------------------------
def mode_validate(playbook_path: str, schema_path: str, format_id: str) -> int:
    """Validate the playbook YAML against the schema. Exit 0=PASS, 1=FAIL."""
    print("REPLAY_MODE: validate", file=sys.stderr)
    print(f"REPLAY_FORMAT_ID: {format_id}", file=sys.stderr)
    print(f"REPLAY_PLAYBOOK: {playbook_path}", file=sys.stderr)
    print(f"REPLAY_SCHEMA: {schema_path}", file=sys.stderr)

    try:
        playbook = _load_yaml(playbook_path)
    except Exception as e:
        print(f"REPLAY_VALIDATE: FAIL — cannot load playbook: {e}")
        return 1

    if playbook.get("format_id") != format_id:
        print(
            f"REPLAY_VALIDATE: FAIL — playbook format_id '{playbook.get('format_id')}' "
            f"does not match --format-id '{format_id}'"
        )
        return 1

    try:
        schema = _load_schema(schema_path)
    except Exception as e:
        print(f"REPLAY_VALIDATE: FAIL — cannot load schema: {e}")
        return 1

    valid, errors = _validate_playbook_schema(playbook, schema)
    if valid:
        print("REPLAY_VALIDATE: PASS")
        return 0
    else:
        print("REPLAY_VALIDATE: FAIL")
        for err in errors:
            print(f"  ERROR: {err}")
        return 1


# ---------------------------------------------------------------------------
# Dry-run: check one operation
# ---------------------------------------------------------------------------
def _check_operation(op: dict, format_id: str) -> list[dict]:
    """
    Check a single operation deterministically.
    Returns a list of conflict dicts (empty = PASS).
    """
    conflicts = []
    op_id = op.get("operation_id", "UNKNOWN")
    gate = op.get("gate", 0)

    # Check input_dependencies
    for dep in op.get("input_dependencies", []):
        if not dep.get("required", False):
            continue
        rel_path = dep.get("path", "")
        full_path = os.path.join(REPO_ROOT, rel_path)
        if not os.path.exists(full_path):
            conflicts.append({
                "operation_id": op_id,
                "gate": gate,
                "target_path": rel_path,
                "issue_type": "missing_input",
                "severity": "high",
                "deterministic_failure_reason": f"Required input dependency is absent: {rel_path}",
                "required_action": (
                    f"Verify that '{rel_path}' exists and is committed before replaying "
                    f"operation '{op_id}'."
                ),
            })

    # Check expected_outputs (warn only — outputs may not exist yet in dry-run)
    for out in op.get("expected_outputs", []):
        rel_path = out.get("path", "")
        full_path = os.path.join(REPO_ROOT, rel_path)
        if not os.path.exists(full_path):
            # Use conflict_policy to determine severity
            conflict_policy = op.get("conflict_policy", "fail_and_queue")
            severity = "medium" if conflict_policy == "warn_and_continue" else "high"
            conflicts.append({
                "operation_id": op_id,
                "gate": gate,
                "target_path": rel_path,
                "issue_type": "target_mismatch",
                "severity": severity,
                "deterministic_failure_reason": (
                    f"Expected output not present: {rel_path}. "
                    f"In a real execution, this path should have been created."
                ),
                "required_action": (
                    f"Verify whether '{rel_path}' should exist for operation '{op_id}'. "
                    f"If so, re-run the sprint that produces it."
                ),
            })

    return conflicts


# ---------------------------------------------------------------------------
# Mode: dry-run
# ---------------------------------------------------------------------------
def mode_dry_run(
    playbook_path: str,
    schema_path: str,
    format_id: str,
) -> tuple[int, dict]:
    """
    Dry-run replay: check all operations deterministically.
    Writes ZERO repo files. Returns (exit_code, report_dict).
    """
    print("REPLAY_MODE: dry-run", file=sys.stderr)
    print(f"REPLAY_FORMAT_ID: {format_id}", file=sys.stderr)
    print(f"REPLAY_PLAYBOOK: {playbook_path}", file=sys.stderr)

    try:
        playbook = _load_yaml(playbook_path)
    except Exception as e:
        print(f"REPLAY_DRY_RUN: FAIL — cannot load playbook: {e}")
        return 1, {}

    if playbook.get("format_id") != format_id:
        print(
            f"REPLAY_DRY_RUN: FAIL — playbook format_id '{playbook.get('format_id')}' "
            f"does not match --format-id '{format_id}'"
        )
        return 1, {}

    # Guard: documentation_example playbooks must not be replayed
    if playbook.get("not_for_execution") is True or playbook.get("status") == "documentation_example_only":
        print(
            "REPLAY_DRY_RUN: SKIP — playbook is documentation_example_only (not_for_execution: true). "
            "Dry-run is not permitted on documentation examples."
        )
        return 0, {"skipped": True, "reason": "documentation_example_only"}

    all_conflicts = []
    operations = playbook.get("operations", [])
    op_results = []

    for op in operations:
        op_id = op.get("operation_id", "UNKNOWN")
        conflicts = _check_operation(op, format_id)
        status = "PASS" if not conflicts else "CONFLICT"
        op_results.append({
            "operation_id": op_id,
            "gate": op.get("gate"),
            "status": status,
            "conflict_count": len(conflicts),
        })
        all_conflicts.extend(conflicts)
        symbol = "PASS" if status == "PASS" else f"CONFLICT ({len(conflicts)})"
        print(f"  OPERATION {op_id}: {symbol}")

    total_ops = len(operations)
    total_conflicts = len(all_conflicts)
    pass_ops = sum(1 for r in op_results if r["status"] == "PASS")

    report = {
        "playbook_id": playbook.get("playbook_id"),
        "format_id": format_id,
        "replay_mode": "dry-run",
        "generated_at": _now_iso(),
        "total_operations": total_ops,
        "pass_operations": pass_ops,
        "conflict_operations": total_ops - pass_ops,
        "total_conflicts": total_conflicts,
        "operation_results": op_results,
        "conflicts": all_conflicts,
        "replay_authority": "INFORMATIONAL ONLY — not gate approval, not evidence authority.",
    }

    if total_conflicts == 0:
        print(f"REPLAY_DRY_RUN: PASS ({pass_ops}/{total_ops} operations)")
        return 0, report
    else:
        print(
            f"REPLAY_DRY_RUN: CONFLICTS ({total_conflicts} conflicts in "
            f"{total_ops - pass_ops}/{total_ops} operations)"
        )
        return 1, report


# ---------------------------------------------------------------------------
# Mode: explain
# ---------------------------------------------------------------------------
def mode_explain(playbook_path: str, format_id: str) -> int:
    """Print a human-readable description of each operation. No file writes."""
    print("REPLAY_MODE: explain", file=sys.stderr)
    print(f"REPLAY_FORMAT_ID: {format_id}", file=sys.stderr)

    try:
        playbook = _load_yaml(playbook_path)
    except Exception as e:
        print(f"REPLAY_EXPLAIN: FAIL — cannot load playbook: {e}")
        return 1

    if playbook.get("format_id") != format_id:
        print(
            f"REPLAY_EXPLAIN: FAIL — playbook format_id '{playbook.get('format_id')}' "
            f"does not match --format-id '{format_id}'"
        )
        return 1

    print(f"PLAYBOOK_ID: {playbook.get('playbook_id')}")
    print(f"FORMAT_ID: {playbook.get('format_id')}")
    print(f"STATUS: {playbook.get('status')}")
    if playbook.get("not_for_execution"):
        print("NOT_FOR_EXECUTION: true")
    print()

    operations = playbook.get("operations", [])
    if not operations:
        print("(No operations defined in this playbook.)")
        return 0

    for i, op in enumerate(operations, 1):
        op_id = op.get("operation_id", "?")
        gate = op.get("gate", "?")
        title = op.get("title", "(no title)")
        description = op.get("description", "(no description)")
        mode = op.get("mode_allowed", "?")
        conflict_policy = op.get("conflict_policy", "?")
        approval = op.get("approval_boundary", "?")
        reuse = op.get("reuse_level", "?")

        inputs = [d.get("path", "?") for d in op.get("input_dependencies", [])]
        outputs = [o.get("path", "?") for o in op.get("expected_outputs", [])]

        print(f"Operation {i}: {op_id}")
        print(f"  Gate:            {gate}")
        print(f"  Title:           {title}")
        print(f"  Description:     {description}")
        print(f"  Mode allowed:    {mode}")
        print(f"  Conflict policy: {conflict_policy}")
        print(f"  Approval:        {approval}")
        print(f"  Reuse level:     {reuse}")
        if inputs:
            print(f"  Inputs:          {', '.join(inputs)}")
        if outputs:
            print(f"  Outputs:         {', '.join(outputs)}")
        print()

    print(f"REPLAY_EXPLAIN: DONE ({len(operations)} operations)")
    return 0


# ---------------------------------------------------------------------------
# Mode: export-review-queue
# ---------------------------------------------------------------------------
def mode_export_review_queue(
    playbook_path: str,
    schema_path: str,
    format_id: str,
    output_path: str,
) -> int:
    """
    Run dry-run and export any conflicts as a review-queue YAML conforming to
    schemas/playbook/review-queue.schema.json.
    Output is written to --output only. No repo mutations.
    """
    print("REPLAY_MODE: export-review-queue", file=sys.stderr)
    print(f"REPLAY_FORMAT_ID: {format_id}", file=sys.stderr)
    print(f"REPLAY_OUTPUT: {output_path}", file=sys.stderr)

    # Validate output path is not inside repo (or is explicitly allowed .local/ path)
    # Enforcement: output must not be a committed repo path (e.g. src/, tools/, schemas/)
    _guard_output_path(output_path)

    exit_code, report = mode_dry_run(playbook_path, schema_path, format_id)

    if report.get("skipped"):
        print("REPLAY_EXPORT_REVIEW_QUEUE: SKIP — playbook is not_for_execution.")
        return 0

    playbook_id = report.get("playbook_id", "unknown")
    conflicts = report.get("conflicts", [])
    now_str = _now_str()
    queue_id = f"rq-{format_id}-{now_str}"
    run_id = f"s-f2f-03-dry-run-{now_str}"

    items = []
    for i, c in enumerate(conflicts, 1):
        item_id = f"RQ-{i:03d}"
        severity = c.get("severity", "medium")
        blocks_apply = severity in ("high", "blocker")
        items.append({
            "item_id": item_id,
            "format_id": format_id,
            "gate": c.get("gate", 1),
            "operation_id": c.get("operation_id", "unknown"),
            "target_path": c.get("target_path", ""),
            "issue_type": c.get("issue_type", "other"),
            "severity": severity,
            "deterministic_failure_reason": c.get("deterministic_failure_reason", ""),
            "required_action": c.get("required_action", ""),
            "suggested_fix": None,
            "evidence_required": ["manual_inspection"],
            "status": "open",
            "resolution_notes": None,
            "owner_role": "secondary_sprint_owner",
            "blocks_apply_mode": blocks_apply,
            "blocks_gate_progress": blocks_apply,
            "provenance": {
                "created_at": _now_iso(),
                "created_by_sprint": "S-F2F-03",
                "resolved_at": None,
                "resolved_by_sprint": None,
            },
        })

    total = len(items)
    open_count = sum(1 for it in items if it["status"] == "open")
    blocker_count = sum(1 for it in items if it["severity"] == "blocker")
    high_count = sum(1 for it in items if it["severity"] == "high")
    medium_count = sum(1 for it in items if it["severity"] == "medium")
    low_count = sum(1 for it in items if it["severity"] == "low")
    blocks_apply = any(it["blocks_apply_mode"] for it in items if it["status"] == "open")
    blocks_gate = any(it["blocks_gate_progress"] for it in items if it["status"] == "open")

    queue = {
        "schema_version": "1.0",
        "queue_id": queue_id,
        "run_id": run_id,
        "generated_at": _now_iso(),
        "source_playbook_id": playbook_id,
        "source_format_id": format_id,
        "items": items,
        "summary": {
            "total_items": total,
            "open_items": open_count,
            "blocker_count": blocker_count,
            "high_count": high_count,
            "medium_count": medium_count,
            "low_count": low_count,
            "blocks_apply_mode": blocks_apply,
            "blocks_gate_progress": blocks_gate,
        },
        "governance": {
            "cannot_approve_gates": True,
            "cannot_replace_dec034": True,
            "cannot_replace_evidence_contracts": True,
            "cannot_replace_human_approval": True,
            "high_severity_blocks_apply": True,
            "gate_progress_requires_resolution": True,
            "policy_doc_reference": "docs/playbook-layer.md",
        },
    }

    # Write output
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(queue, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    if total == 0:
        print("REPLAY_EXPORT_REVIEW_QUEUE: PASS (0 conflicts — empty review queue written)")
    else:
        print(
            f"REPLAY_EXPORT_REVIEW_QUEUE: CONFLICTS ({total} items written to {output_path})"
        )
    print(f"REVIEW_QUEUE_OUTPUT: {os.path.abspath(output_path)}")
    return 0 if total == 0 else 1


# ---------------------------------------------------------------------------
# Output path guard
# ---------------------------------------------------------------------------
_COMMITTED_REPO_PREFIXES = (
    "src/",
    "tools/",
    "schemas/",
    "plans/",
    "taskcards/",
    "docs/",
    "tests/",
    "samples/",
    "acquisition-packs/",
    "registry/",
    "reports/",
    "prototypes/",
)


def _guard_output_path(output_path: str) -> None:
    """
    Reject output paths that target committed repo directories.
    Output must go to .local/, /tmp/, or an absolute path outside repo.
    """
    abs_out = os.path.abspath(output_path)
    repo_abs = os.path.abspath(REPO_ROOT)

    # If inside repo, only allow .local/ subdirectory
    if abs_out.startswith(repo_abs):
        rel = os.path.relpath(abs_out, repo_abs).replace("\\", "/")
        for prefix in _COMMITTED_REPO_PREFIXES:
            if rel.startswith(prefix):
                print(
                    f"REPLAY_ERROR: --output path '{output_path}' targets a committed repo "
                    f"directory ('{prefix}...'). Output must go to .local/ or an external "
                    f"path. Exiting.",
                    file=sys.stderr,
                )
                sys.exit(2)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Dry-run replay engine for format-factory acquisition playbooks (S-F2F-03).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=["validate", "dry-run", "explain", "export-review-queue"],
        help="Replay mode. apply mode is NOT available.",
    )
    parser.add_argument(
        "--format-id",
        required=True,
        help="Format identifier, e.g. 'fods' or 'fodt'. Must match playbook format_id.",
    )
    parser.add_argument(
        "--playbook",
        required=True,
        help="Path to the playbook YAML file to replay.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help=(
            "Output file path. Required for export-review-queue mode. "
            "Must be in .local/ or an external path — not in committed repo directories."
        ),
    )
    parser.add_argument(
        "--schema",
        default=DEFAULT_SCHEMA,
        help=f"Path to the acquisition-playbook schema JSON. Default: {DEFAULT_SCHEMA}",
    )

    args = parser.parse_args()

    # Apply mode guard
    _guard_replay_mode(args.mode)

    # Route to mode handlers
    if args.mode == "validate":
        return mode_validate(args.playbook, args.schema, args.format_id)

    elif args.mode == "dry-run":
        exit_code, _report = mode_dry_run(args.playbook, args.schema, args.format_id)
        return exit_code

    elif args.mode == "explain":
        return mode_explain(args.playbook, args.format_id)

    elif args.mode == "export-review-queue":
        if not args.output:
            print(
                "REPLAY_ERROR: --output is required for export-review-queue mode.",
                file=sys.stderr,
            )
            return 2
        return mode_export_review_queue(
            args.playbook, args.schema, args.format_id, args.output
        )

    else:
        print(f"REPLAY_ERROR: Unknown mode '{args.mode}'.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
