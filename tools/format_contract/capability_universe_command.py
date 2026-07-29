"""Command-line boundary for the FF6 production capability compiler."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Sequence

from .capability_universe_runtime import (
    UniverseError,
    check_outputs,
    load_yaml,
    safe_path,
    verify_idempotency,
    write_outputs,
    yaml_bytes,
)


def scaffold_enrichment(
    repo_root: Path,
    format_id: str,
    *,
    policy_path: Path,
    output_path: Path,
    task_id: str,
) -> None:
    """Create a deterministic, contract-derived enrichment ready for explicit implementation proof."""

    root = repo_root.resolve()
    policy, _ = load_yaml(root, policy_path)
    contract, _ = load_yaml(
        root, Path(f"shared/format-contracts/{format_id}.yaml")
    )
    format_policy = policy.get("formats", {}).get(format_id)
    if not isinstance(format_policy, dict):
        raise UniverseError(f"format is absent from policy: {format_id}")
    target_profiles = [str(item) for item in format_policy.get("target_profiles", [])]
    if not target_profiles:
        raise UniverseError(f"{format_id}: target_profiles must not be empty")
    applicability = format_policy.get("profile_applicability", {}) or {}
    locks = format_policy.get("classification_locks", {}) or {}

    target = safe_path(root, output_path)
    existing_by_id: dict[str, dict[str, Any]] = {}
    if target.is_file():
        existing, _ = load_yaml(root, output_path)
        if existing.get("format_id") != format_id:
            raise UniverseError(
                f"{output_path}: existing enrichment format_id does not match "
                f"{format_id}"
            )
        existing_records = existing.get("capabilities", [])
        if not isinstance(existing_records, list):
            raise UniverseError(
                f"{output_path}: existing enrichment capabilities must be a list"
            )
        for record in existing_records:
            if not isinstance(record, dict) or not record.get("capability_id"):
                raise UniverseError(
                    f"{output_path}: every existing enrichment must have capability_id"
                )
            capability_id = str(record["capability_id"])
            if capability_id in existing_by_id:
                raise UniverseError(
                    f"{output_path}: duplicate existing capability {capability_id}"
                )
            existing_by_id[capability_id] = record

    preservation = contract.get("preservation_contract", {}) or {}
    preservation_rules = [
        str(item)
        for value in preservation.values()
        for item in (value if isinstance(value, list) else [value])
        if item
    ] or ["Preserve every safely representable unknown construct without silent loss."]
    diagnostics = [
        "code",
        "severity",
        "message",
        "source_location",
        "object_path",
        "originating_rule",
        "repair_suggestion",
        "auto_repair_eligible",
    ]
    records: list[dict[str, Any]] = []
    for capability in contract.get("capabilities", []):
        capability_id = str(capability["capability_id"])
        profiles = [
            str(item)
            for item in applicability.get(capability_id, target_profiles)
        ]
        if not profiles or set(profiles) - set(target_profiles):
            raise UniverseError(
                f"{capability_id}: invalid profile_applicability {profiles}"
            )
        security = [
            str(item)
            for item in capability.get("security_requirements", [])
        ] or [
            "Treat all input as untrusted and enforce configured resource limits before allocation or external access."
        ]
        resource_limits = [
            str(item)
            for item in contract.get("security_contract", {}).get(
                "resource_limits", []
            )
        ] or [
            "Bound input bytes, expanded bytes, nesting, object count, and decoded payload size."
        ]
        scaffold = {
                "capability_id": capability_id,
                "stable_name": str(capability.get("title", capability_id)),
                "classification": str(
                    locks.get(capability_id, "STABLE_REQUIRED")
                ),
                "developer_use_cases": [
                    str(capability.get("developer_use_case"))
                ],
                "spec_profiles": profiles,
                "authority_fact_ids": [
                    str(item) for item in capability.get("provenance", [])
                ],
                "public_symbols": "PLANNED",
                "source_symbols": "PLANNED",
                "model_invariants": [
                    str(item)
                    for item in capability.get(
                        "required_behavior",
                        [capability.get("production_meaning", capability_id)],
                    )
                ],
                "preservation_contract": preservation_rules,
                "error_contract": diagnostics,
                "security_contract": security,
                "resource_limits": resource_limits,
                "performance_budget": "PLANNED",
                "dependency_policy": "PLANNED",
                "positive_tests": "PLANNED",
                "negative_tests": "PLANNED",
                "property_tests": "PLANNED",
                "roundtrip_tests": "PLANNED",
                "fixtures": "PLANNED",
                "independent_oracles": "PLANNED",
                "documentation_examples": "PLANNED",
                "compatibility_status": "PLANNED",
                "proof_node_ids": "PLANNED",
                "invalidation_inputs": [
                    "canonical authority lock and materialized authority bytes",
                    "canonical format contract and SAL facts/evidence",
                    "FF6 capability and profile policy",
                ],
                "taskcard_ids": [task_id],
                "release_state": "PLANNED",
            }
        previous = existing_by_id.get(capability_id)
        record = {**scaffold, **previous} if previous else scaffold
        # These fields are contract/policy projections, not manually curated
        # implementation detail. Refresh them on every scaffold replay so a
        # source-contract expansion cannot retain stale fact or profile claims.
        record["capability_id"] = capability_id
        record["spec_profiles"] = profiles
        record["authority_fact_ids"] = list(capability.get("provenance", []))
        record["classification"] = str(
            locks.get(capability_id, record.get("classification", "STABLE_REQUIRED"))
        )
        taskcard_ids = [
            str(item) for item in record.get("taskcard_ids", []) if str(item)
        ]
        if task_id not in taskcard_ids:
            taskcard_ids.append(task_id)
        record["taskcard_ids"] = taskcard_ids
        exclusion = (format_policy.get("exclusions", {}) or {}).get(capability_id)
        if exclusion is not None:
            record["exclusion"] = exclusion
        else:
            record.pop("exclusion", None)
        records.append(record)
    payload = {
        "schema": "ff6/capability-enrichment@1",
        "goal_id": policy.get("goal_id"),
        "format_id": format_id,
        "capabilities": sorted(records, key=lambda item: item["capability_id"]),
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(yaml_bytes(payload))


def migrate_drafts(
    repo_root: Path,
    format_ids: Sequence[str],
    *,
    policy_path: Path,
    draft_dir: Path,
    enrichment_dir: Path,
) -> None:
    """Losslessly project preserved draft detail into compiler-owned enrichments."""

    from .capability_universe import (
        DERIVED_FIELDS,
        LEGACY_CLASSIFICATIONS,
        REQUIRED_ENRICHMENT_FIELDS,
    )

    root = repo_root.resolve()
    policy, _ = load_yaml(root, policy_path)
    for format_id in format_ids:
        draft, _ = load_yaml(root, draft_dir / f"{format_id}.yaml")
        locks = policy["formats"][format_id].get("classification_locks", {}) or {}
        exclusions = policy["formats"][format_id].get("exclusions", {}) or {}
        records: list[dict[str, Any]] = []
        for source in draft.get("capabilities", []):
            record = {
                key: value for key, value in source.items() if key not in DERIVED_FIELDS
            }
            classification = LEGACY_CLASSIFICATIONS.get(
                str(record.get("classification")), record.get("classification")
            )
            capability_id = str(record.get("capability_id"))
            record["classification"] = locks.get(capability_id, classification)
            for field in REQUIRED_ENRICHMENT_FIELDS:
                if record.get(field) in (None, "", [], {}):
                    record[field] = "PLANNED"
            if capability_id in exclusions:
                record["exclusion"] = exclusions[capability_id]
            records.append(record)
        payload = {
            "schema": "ff6/capability-enrichment@1",
            "goal_id": policy.get("goal_id"),
            "format_id": format_id,
            "capabilities": sorted(records, key=lambda item: item["capability_id"]),
        }
        target = safe_path(root, enrichment_dir / f"{format_id}.yaml")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(yaml_bytes(payload))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compile the deterministic FF6 production capability universe."
    )
    sub = parser.add_subparsers(dest="command", required=True)
    compile_parser = sub.add_parser("compile")
    migrate_parser = sub.add_parser("migrate-draft")
    scaffold_parser = sub.add_parser("scaffold-enrichment")
    for item in (compile_parser, migrate_parser):
        item.add_argument("--repo-root", type=Path, default=Path("."))
        item.add_argument("--policy", type=Path, required=True)
        item.add_argument("--format", action="append", dest="formats", required=True)
    compile_parser.add_argument("--enrichment-dir", type=Path, required=True)
    compile_parser.add_argument("--output-dir", type=Path, required=True)
    compile_parser.add_argument("--schema", type=Path)
    compile_parser.add_argument("--check", action="store_true")
    compile_parser.add_argument("--verify-idempotency", action="store_true")
    compile_parser.add_argument("--allow-blocked-authority", action="store_true")
    migrate_parser.add_argument("--draft-dir", type=Path, required=True)
    migrate_parser.add_argument("--enrichment-dir", type=Path, required=True)
    scaffold_parser.add_argument("--repo-root", type=Path, default=Path("."))
    scaffold_parser.add_argument("--policy", type=Path, required=True)
    scaffold_parser.add_argument("--format", required=True)
    scaffold_parser.add_argument("--output", type=Path, required=True)
    scaffold_parser.add_argument("--task-id", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Execute compilation or preserved-draft migration."""

    from .capability_universe import compile_universe

    args = _parser().parse_args(argv)
    try:
        if args.command == "scaffold-enrichment":
            scaffold_enrichment(
                args.repo_root,
                str(args.format).lower(),
                policy_path=args.policy,
                output_path=args.output,
                task_id=args.task_id,
            )
            print(f"SCAFFOLDED_FORMAT: {str(args.format).lower()}")
            return 0
        if args.command == "migrate-draft":
            migrate_drafts(
                args.repo_root,
                args.formats,
                policy_path=args.policy,
                draft_dir=args.draft_dir,
                enrichment_dir=args.enrichment_dir,
            )
            print(f"MIGRATED_FORMATS: {len(args.formats)}")
            return 0

        schema_paths = (args.schema,) if args.schema else None

        def factory():
            return compile_universe(
                args.repo_root,
                args.formats,
                policy_path=args.policy,
                enrichment_dir=args.enrichment_dir,
                schema_paths=schema_paths,
                allow_blocked_authority=args.allow_blocked_authority,
            )

        result = factory()
        if args.verify_idempotency:
            digest = verify_idempotency(factory)
            print(f"THREE_RUN_DIGEST: {digest}")
        if args.check:
            check_outputs(args.output_dir, result.outputs)
            print(f"CHECK_PASS: {result.manifest['aggregate_sha256']}")
        else:
            write_outputs(args.output_dir, result.outputs)
            print(f"COMPILED_FORMATS: {len(args.formats)}")
            print(f"AGGREGATE_SHA256: {result.manifest['aggregate_sha256']}")
        return 0
    except UniverseError as exc:
        print(f"CAPABILITY_UNIVERSE_ERROR: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
