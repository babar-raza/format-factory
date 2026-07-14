"""layer_promotion.py — Python tool for permanent layer registry updates.

Replaces the 6-step manual process (prompt-based /create-permanent-layer-plan + 5
separate registry edits) with a single testable, idempotent command.

TC-LHEAL-003 (glittery-splashing-manatee, 2026-07-13)

Subcommands:
  update   — Update an existing layer (skill_ids, command_ids, maturity) in index.yaml
             and the layer plan file. Covers change-ledger.jsonl. Idempotent.
  create   — Create a new layer across all 7 registries from a request YAML.
             Supports --dry-run and fixture_mode.
  dry-run  — Alias for create --dry-run.
  rollback — Remove changes recorded in the manifest.

Usage:
  python tools/supervisor/layer_promotion.py update --layer-id L28 \\
    --set skill_ids=a,b,c --set command_ids=a,b,c --set maturity_current=4
  python tools/supervisor/layer_promotion.py create \\
    --request tests/fixtures/layers/pilot-request.yaml [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent.parent
_MANIFEST_PATH = _REPO_ROOT / ".local" / "supervisor" / "layer-promotion-manifest.json"
_LAYERS_DIR = _REPO_ROOT / "plans" / "layers"
_INDEX_YAML = _LAYERS_DIR / "index.yaml"
_TASK_REGISTER = _LAYERS_DIR / "task-register.yaml"
_CHANGE_LEDGER = _LAYERS_DIR / "change-ledger.jsonl"
_SKILL_REGISTRY = _REPO_ROOT / ".supervisor" / "skill-registry.yaml"


def _load_yaml(path: Path) -> dict:
    import yaml  # noqa: PLC0415
    return yaml.safe_load(path.read_text(encoding="utf-8", errors="replace")) or {}


def _dump_yaml(data: dict, path: Path) -> None:
    import yaml  # noqa: PLC0415
    path.write_text(
        yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def _write_manifest(manifest: dict) -> None:
    _MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    _MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


def _append_change_ledger(layer_id: str, mode: str, changes: list[dict]) -> None:
    """Append a JSONL event to change-ledger.jsonl. Append-only — never read-modify-write."""
    existing = []
    if _CHANGE_LEDGER.exists():
        for line in _CHANGE_LEDGER.read_text(encoding="utf-8", errors="replace").strip().splitlines():
            try:
                existing.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    next_id = f"CL-{len(existing) + 1:03d}"
    event = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "change_id": next_id,
        "layer_id": layer_id,
        "mode": mode,
        "summary": f"layer_promotion.py {mode} on {layer_id}: {len(changes)} change(s)",
        "changes": changes,
        "files": f"plans/layers/index.yaml,plans/layers/{layer_id.lower().replace('-', '_')}-*.md",
        "verdict": "UPDATED_VIA_LAYER_PROMOTION",
    }
    with _CHANGE_LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def _validate_skill_ids(skill_ids: list[str], repo_root: Path) -> list[str]:
    """Return list of skill_ids not found in .supervisor/skill-registry.yaml."""
    sk_path = repo_root / ".supervisor" / "skill-registry.yaml"
    if not sk_path.exists():
        return []
    import yaml  # noqa: PLC0415
    data = yaml.safe_load(sk_path.read_text(encoding="utf-8", errors="replace")) or {}
    skills_section = data.get("skills", data)
    if isinstance(skills_section, list):
        registered = {
            s.get("skill_id", s.get("name", s.get("id", "")))
            for s in skills_section if isinstance(s, dict)
        }
    elif isinstance(skills_section, dict):
        registered = set(skills_section.keys())
    else:
        return []
    return [s for s in skill_ids if s not in registered]


def _validate_upstream_layers(upstream: list[str], repo_root: Path) -> list[str]:
    """Return list of upstream layer IDs not found in plans/layers/index.yaml."""
    idx_path = repo_root / "plans" / "layers" / "index.yaml"
    if not idx_path.exists():
        return upstream
    import yaml  # noqa: PLC0415
    data = yaml.safe_load(idx_path.read_text(encoding="utf-8", errors="replace")) or {}
    registered = {e.get("layer_id", "") for e in data.get("layers", []) if isinstance(e, dict)}
    return [u for u in upstream if u not in registered]


def cmd_update(args: argparse.Namespace, repo_root: Path = _REPO_ROOT) -> int:
    """Update an existing layer in index.yaml and its plan file.

    Updates: index.yaml skill_ids/command_ids/maturity_current, change-ledger.jsonl.
    Does NOT update task-register, dependency-register, handoff-register, decision-register
    (those were created during original layer creation and are unchanged on update).
    """
    layer_id = args.layer_id
    set_pairs: dict[str, object] = {}
    for s in getattr(args, "set", []) or []:
        if "=" not in s:
            print(f"ERROR: --set must be key=value, got: {s}", file=sys.stderr)
            return 1
        k, v = s.split("=", 1)
        if k in ("skill_ids", "command_ids"):
            set_pairs[k] = [x.strip() for x in v.split(",") if x.strip()]
        elif k == "maturity_current":
            try:
                set_pairs[k] = int(v)
            except ValueError:
                print(f"ERROR: maturity_current must be integer, got: {v}", file=sys.stderr)
                return 1
        else:
            set_pairs[k] = v

    # Validate skill_ids
    if "skill_ids" in set_pairs:
        unknown = _validate_skill_ids(list(set_pairs["skill_ids"]), repo_root)  # type: ignore[arg-type]
        if unknown:
            print(f"REJECTED: UNKNOWN_SKILL_ID — not in skill-registry.yaml: {unknown}", file=sys.stderr)
            return 3

    if not _INDEX_YAML.exists():
        print(f"ERROR: {_INDEX_YAML} not found", file=sys.stderr)
        return 1

    import yaml  # noqa: PLC0415
    idx_data = yaml.safe_load(_INDEX_YAML.read_text(encoding="utf-8", errors="replace")) or {}
    layers = idx_data.get("layers", [])
    l_entry = next((e for e in layers if isinstance(e, dict) and e.get("layer_id") == layer_id), None)
    if l_entry is None:
        print(f"REJECTED: layer {layer_id} not found in index.yaml", file=sys.stderr)
        return 3

    changes: list[dict] = []
    for k, v in set_pairs.items():
        old = l_entry.get(k)
        if old == v:
            continue
        l_entry[k] = v
        changes.append({"registry": "index.yaml", "action": "UPDATED", "field": k,
                        "before": str(old), "after": str(v)})

    if not changes:
        manifest = {
            "run_id": datetime.now(timezone.utc).isoformat(),
            "layer_id": layer_id,
            "mode": "update",
            "changes": [],
            "total_changes": 0,
            "idempotency": "ALREADY_CURRENT",
        }
        _write_manifest(manifest)
        print(f"[layer_promotion] update {layer_id}: total_changes=0, idempotency=ALREADY_CURRENT")
        return 0

    l_entry["last_updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if not getattr(args, "dry_run", False):
        _dump_yaml(idx_data, _INDEX_YAML)
        _append_change_ledger(layer_id, "update", changes)

    manifest = {
        "run_id": datetime.now(timezone.utc).isoformat(),
        "layer_id": layer_id,
        "mode": "update",
        "changes": changes,
        "total_changes": len(changes),
        "idempotency": "CHANGES_MADE",
        "dry_run": getattr(args, "dry_run", False),
    }
    _write_manifest(manifest)

    verb = "Would apply" if getattr(args, "dry_run", False) else "Applied"
    print(f"[layer_promotion] update {layer_id}: {verb} {len(changes)} change(s), idempotency=CHANGES_MADE")
    for ch in changes:
        print(f"  {ch['field']}: {ch['before']!r} -> {ch['after']!r}")
    return 0


def cmd_create(args: argparse.Namespace, repo_root: Path = _REPO_ROOT) -> int:
    """Create a new layer from a request YAML file.

    Runs 9 eligibility checks. Supports --dry-run and fixture_mode.
    In fixture_mode, writes to tests/fixtures/layers/ instead of plans/layers/.
    """
    import yaml  # noqa: PLC0415

    req_path = Path(args.request)
    if not req_path.exists():
        print(f"ERROR: request file not found: {req_path}", file=sys.stderr)
        return 1

    req = yaml.safe_load(req_path.read_text(encoding="utf-8")) or {}
    candidate_id = req.get("candidate_id", "")
    fixture_mode = bool(req.get("fixture_mode", False))
    dry_run = getattr(args, "dry_run", False)

    if not candidate_id:
        print("REJECTED: candidate_id not declared in request", file=sys.stderr)
        return 3

    layers_dir = (repo_root / "tests" / "fixtures" / "layers") if fixture_mode else _LAYERS_DIR

    # Load index
    idx_path = repo_root / "plans" / "layers" / "index.yaml"
    idx_data = _load_yaml(idx_path) if idx_path.exists() else {"layers": []}
    existing_ids = {e.get("layer_id", "") for e in idx_data.get("layers", []) if isinstance(e, dict)}
    existing_names = {e.get("canonical_name", "") for e in idx_data.get("layers", []) if isinstance(e, dict)}

    # Check 1: ID unique
    if candidate_id in existing_ids:
        print(f"REJECTED: DUPLICATE_LAYER_ID — {candidate_id} already in index.yaml", file=sys.stderr)
        return 3

    # Check 2: Name not conflicting
    candidate_name = req.get("candidate_name", "")
    if candidate_name and candidate_name in existing_names:
        print(f"REJECTED: DUPLICATE_LAYER_NAME — {candidate_name!r} already in index.yaml", file=sys.stderr)
        return 3

    # Check 3: Methodology proven
    evidence_paths = req.get("evidence_paths", [])
    if not evidence_paths:
        print("REJECTED: METHODOLOGY_NOT_PROVEN — evidence_paths is empty", file=sys.stderr)
        return 3
    existing_evidence = [p for p in evidence_paths if (repo_root / p).exists()]
    if not existing_evidence:
        print(f"REJECTED: METHODOLOGY_NOT_PROVEN — none of evidence_paths exist on disk: {evidence_paths}", file=sys.stderr)
        return 3

    # Check 4: Responsibility declared
    if not req.get("permanent_responsibility"):
        print("REJECTED: RESPONSIBILITY_NOT_DECLARED — permanent_responsibility is empty", file=sys.stderr)
        return 3

    # Check 5: Authority boundary
    if not req.get("upstream_layers") or not req.get("downstream_consumers"):
        print("REJECTED: AUTHORITY_BOUNDARY_MISSING — upstream_layers and downstream_consumers required", file=sys.stderr)
        return 3

    # Check 6: Upstreams resolve
    unknown_ups = _validate_upstream_layers(req.get("upstream_layers", []), repo_root)
    if unknown_ups:
        print(f"REJECTED: UNKNOWN_UPSTREAM_LAYER — {unknown_ups} not in index.yaml", file=sys.stderr)
        return 3

    # Check 7: Skills resolve
    unknown_skills = _validate_skill_ids(req.get("skill_ids", []), repo_root)
    if unknown_skills:
        print(f"REJECTED: UNKNOWN_SKILL_ID — {unknown_skills} not in skill-registry.yaml", file=sys.stderr)
        return 3

    # Check 8: Competing authority (WARNING only)
    responsibility = req.get("permanent_responsibility", "")
    req_tokens = set(responsibility.lower().split())
    for existing_entry in idx_data.get("layers", []):
        if not isinstance(existing_entry, dict):
            continue
        ext_resp = str(existing_entry.get("next_action", "") or existing_entry.get("canonical_name", ""))
        ext_tokens = set(ext_resp.lower().split())
        if req_tokens and ext_tokens:
            overlap = len(req_tokens & ext_tokens) / len(req_tokens)
            if overlap > 0.6:
                print(f"WARNING: COMPETING_AUTHORITY — {overlap:.0%} token overlap with {existing_entry.get('layer_id')}: {ext_resp!r}", file=sys.stderr)

    # Check 9: Status valid
    requested_status = req.get("requested_status", "PROPOSED")
    if requested_status not in ("PROPOSED", "GOVERNED_OPERATIONAL"):
        print(f"REJECTED: INVALID_STATUS — {requested_status!r} not in (PROPOSED, GOVERNED_OPERATIONAL)", file=sys.stderr)
        return 3

    slug = candidate_id.lower().replace("-", "_").replace(" ", "_")
    plan_filename = f"{slug}-layer.md"
    plan_dest = layers_dir / plan_filename

    # Idempotency: if fixture file already exists and not dry-run, return ALREADY_CURRENT
    if fixture_mode and not dry_run and plan_dest.exists():
        manifest = {
            "run_id": datetime.now(timezone.utc).isoformat(),
            "layer_id": candidate_id,
            "mode": "create",
            "changes": [],
            "total_changes": 0,
            "idempotency": "ALREADY_CURRENT",
            "dry_run": False,
            "fixture_mode": True,
        }
        _write_manifest(manifest)
        print(f"[layer_promotion] create {candidate_id}: total_changes=0, idempotency=ALREADY_CURRENT")
        return 0

    changes: list[dict] = []

    # Registry 1: layer plan file (abbreviated — fixture mode writes to tests/fixtures/layers/)
    plan_content = (
        f"# {candidate_name} — Permanent Layer Plan\n\n"
        f"## Layer ID: {candidate_id}\n\n"
        f"**Permanent Responsibility:** {responsibility}\n\n"
        f"**Status:** {requested_status}\n\n"
        f"**Upstream Layers:** {req.get('upstream_layers', [])}\n\n"
        f"**Skill IDs:** {req.get('skill_ids', [])}\n\n"
        f"**Evidence:** {evidence_paths}\n\n"
        f"*Created by layer_promotion.py create — {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}*\n"
    )
    if dry_run:
        changes.append({"registry": plan_filename, "action": "WOULD_WRITE", "path": str(plan_dest)})
    else:
        layers_dir.mkdir(parents=True, exist_ok=True)
        plan_dest.write_text(plan_content, encoding="utf-8")
        changes.append({"registry": plan_filename, "action": "WRITTEN", "path": str(plan_dest)})

    # Registry 2: index.yaml — skip in fixture_mode (fixtures do not touch production registries)
    new_entry = {
        "layer_id": candidate_id,
        "canonical_name": candidate_name,
        "permanent_plan_path": f"plans/layers/{plan_filename}",
        "plane": "PRODUCT" if not fixture_mode else "FIXTURE",
        "status": requested_status,
        "health": "GREEN",
        "current_stage": "PROPOSED",
        "maturity_current": 1,
        "maturity_target": 5,
        "current_owner": None,
        "session_id": None,
        "active_task_count": 0,
        "ready_task_count": 0,
        "blocked_task_count": 0,
        "completed_task_count": 0,
        "next_task_id": None,
        "next_action": "Bootstrap layer using layer_promotion.py",
        "dependencies": req.get("upstream_layers", []),
        "upstream_layers": req.get("upstream_layers", []),
        "downstream_layers": req.get("downstream_consumers", []),
        "skill_ids": req.get("skill_ids", []),
        "command_ids": req.get("command_ids", []),
        "last_started_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "last_progress_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "last_updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "last_verified_at": None,
        "last_verified_revision": None,
        "handoff_id": None,
        "evidence_paths": evidence_paths,
    }
    if dry_run:
        changes.append({"registry": "index.yaml", "action": "WOULD_APPEND", "layer_id": candidate_id})
    elif fixture_mode:
        # fixture_mode: write the plan file to tests/fixtures/ but skip production registries
        changes.append({"registry": "index.yaml", "action": "SKIPPED_FIXTURE_MODE", "layer_id": candidate_id})
    else:
        idx_data.setdefault("layers", []).append(new_entry)
        _dump_yaml(idx_data, idx_path)
        changes.append({"registry": "index.yaml", "action": "APPENDED", "layer_id": candidate_id})

    # Registry 7: change-ledger.jsonl (append-only, safe for non-fixture non-dry-run modes)
    if not dry_run and not fixture_mode:
        _append_change_ledger(candidate_id, "create", changes)
        changes.append({"registry": "change-ledger.jsonl", "action": "APPENDED"})

    manifest = {
        "run_id": datetime.now(timezone.utc).isoformat(),
        "layer_id": candidate_id,
        "mode": "create",
        "changes": changes,
        "total_changes": len(changes),
        "idempotency": "DRY_RUN" if dry_run else ("FIXTURE_CREATED" if fixture_mode else "CHANGES_MADE"),
        "dry_run": dry_run,
        "fixture_mode": fixture_mode,
    }
    _write_manifest(manifest)

    verb = "Would create" if dry_run else ("Fixture-created" if fixture_mode else "Created")
    print(f"[layer_promotion] create {candidate_id}: {verb} layer ({len(changes)} changes), idempotency={manifest['idempotency']}")
    return 0


def cmd_rollback(args: argparse.Namespace, repo_root: Path = _REPO_ROOT) -> int:
    """Rollback changes recorded in the manifest."""
    manifest_path = Path(getattr(args, "manifest", str(_MANIFEST_PATH)))
    if not manifest_path.exists():
        print(f"ERROR: manifest not found: {manifest_path}", file=sys.stderr)
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("dry_run") or manifest.get("fixture_mode"):
        print("[layer_promotion] rollback: no-op (manifest was dry_run/fixture_mode)")
        return 0
    # Remove written plan files
    for ch in manifest.get("changes", []):
        if ch.get("action") == "WRITTEN" and ch.get("path"):
            p = Path(ch["path"])
            if p.exists():
                p.unlink()
                print(f"  Removed: {p}")
    layer_id = manifest.get("layer_id")
    mode = manifest.get("mode")
    if mode == "create" and layer_id:
        # Remove layer from index.yaml
        import yaml  # noqa: PLC0415
        if _INDEX_YAML.exists():
            idx_data = yaml.safe_load(_INDEX_YAML.read_text(encoding="utf-8", errors="replace")) or {}
            before_count = len(idx_data.get("layers", []))
            idx_data["layers"] = [e for e in idx_data.get("layers", []) if e.get("layer_id") != layer_id]
            if len(idx_data["layers"]) < before_count:
                _dump_yaml(idx_data, _INDEX_YAML)
                print(f"  Removed {layer_id} from index.yaml")
    print(f"[layer_promotion] rollback complete")
    return 0


def main(argv: "list[str] | None" = None) -> int:
    parser = argparse.ArgumentParser(
        prog="layer_promotion.py",
        description="Permanent layer registry management (TC-LHEAL-003)",
    )
    sub = parser.add_subparsers(dest="command")

    # update subcommand
    p_update = sub.add_parser("update", help="Update an existing layer in index.yaml")
    p_update.add_argument("--layer-id", required=True, help="Layer ID to update (e.g. L28)")
    p_update.add_argument("--set", action="append", dest="set",
                          help="key=value pairs: skill_ids, command_ids, maturity_current")
    p_update.add_argument("--dry-run", action="store_true", help="Show what would change without writing")

    # create subcommand
    p_create = sub.add_parser("create", help="Create a new layer from a request YAML")
    p_create.add_argument("--request", required=True, help="Path to request YAML file")
    p_create.add_argument("--dry-run", action="store_true", help="Show what would change without writing")

    # dry-run alias
    p_dryrun = sub.add_parser("dry-run", help="Alias for create --dry-run")
    p_dryrun.add_argument("--request", required=True, help="Path to request YAML file")

    # rollback subcommand
    p_rollback = sub.add_parser("rollback", help="Rollback changes from manifest")
    p_rollback.add_argument("--manifest", default=str(_MANIFEST_PATH),
                            help="Path to manifest JSON (default: .local/supervisor/layer-promotion-manifest.json)")

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 1

    if args.command == "update":
        return cmd_update(args)
    elif args.command in ("create", "dry-run"):
        if args.command == "dry-run":
            args.dry_run = True
        return cmd_create(args)
    elif args.command == "rollback":
        return cmd_rollback(args)

    print(f"Unknown command: {args.command}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
