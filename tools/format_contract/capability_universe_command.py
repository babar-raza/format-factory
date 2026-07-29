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
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Execute compilation or preserved-draft migration."""

    from .capability_universe import compile_universe

    args = _parser().parse_args(argv)
    try:
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
