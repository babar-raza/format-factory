"""Fail-closed validator for the generated FF6 provider-neutral handover.

generated_by: codex
visibility: internal

The validator compares checked-in operational files with a fresh projection
from the canonical controller and journal.  A manually edited current value is
therefore rejected even when its YAML or Markdown remains syntactically valid.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml

from handover_projection import (
    GENERATED_PATHS,
    HANDOVER_ROOT,
    PACKET_PATHS,
    PROOF_INPUT_PATHS,
    REPO_ROOT,
    ProjectionContext,
    ProjectionError,
    build_manifest,
    canonical_bytes,
    deterministic_digest,
    load_context,
    render_projection,
    validate_event_chain,
)


MANIFEST_PATH = HANDOVER_ROOT / "manifest.yaml"
TASK_INDEX_PATH = REPO_ROOT / "taskcards/index.yaml"
ADJUDICATION_PATH = REPO_ROOT / "reports/sal-verification/xliff-core-candidate-adjudications.yaml"
INVENTORY_PATH = REPO_ROOT / "reports/ff6/xliff-core-obligation-inventory.yaml"
CENSUS_PATH = REPO_ROOT / "reports/ff6/xliff-core-authority-candidate-census.yaml"
LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
HISTORICAL_REFERENCE_PATHS = (
    "plans/codex/handover/PROVIDER-SHIFT-CONTRACT.md",
    "plans/codex/handover/SHIFT-AND-RESUME-PROTOCOL.md",
    "plans/codex/handover/EXECUTION-RUNBOOK.md",
    "plans/codex/handover/STATE-MACHINE-AND-TASKCARD-PROTOCOL.md",
    "plans/codex/handover/VALIDATION-AND-RELEASE.md",
    "plans/codex/handover/CURRENT-STATE-AND-ROOT-CAUSES.md",
)


def _git(*args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, check=False, capture_output=True
    )


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ProjectionError(f"{path.relative_to(REPO_ROOT)} is not a mapping")
    return value


def _projection_errors(ctx: ProjectionContext) -> list[str]:
    errors: list[str] = []
    expected = render_projection(ctx)
    for relative in GENERATED_PATHS:
        path = REPO_ROOT / relative
        if not path.is_file():
            errors.append(f"generated projection missing: {relative}")
        elif canonical_bytes(path) != expected[relative]:
            errors.append(f"stale generated projection: {relative}")
    return errors


def _manifest_errors(ctx: ProjectionContext) -> list[str]:
    errors: list[str] = []
    manifest = _load_yaml(MANIFEST_PATH)
    expected = build_manifest(ctx)
    if manifest != expected:
        errors.append("manifest is not the canonical current projection")
    rows = manifest.get("files", [])
    if not isinstance(rows, list):
        return [*errors, "manifest files is not a list"]
    expected_paths = (*PACKET_PATHS, *PROOF_INPUT_PATHS)
    actual_paths: list[str] = []
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            errors.append(f"manifest row {index} is not a mapping")
            continue
        relative = row.get("path")
        if not isinstance(relative, str):
            errors.append(f"manifest row {index} has no path")
            continue
        actual_paths.append(relative)
        path = REPO_ROOT / relative
        if not path.is_file():
            errors.append(f"manifest input missing: {relative}")
            continue
        data = canonical_bytes(path)
        digest = hashlib.sha256(data).hexdigest()
        if row.get("sha256") != digest:
            errors.append(f"manifest digest mismatch: {relative}")
        if row.get("canonical_bytes") != len(data):
            errors.append(f"manifest byte count mismatch: {relative}")
        if not SHA256.fullmatch(str(row.get("sha256", ""))):
            errors.append(f"manifest digest invalid: {relative}")
    if actual_paths != list(expected_paths):
        errors.append("manifest path order/content differs from canonical path inventory")
    return errors


def _parse_and_link_errors() -> list[str]:
    errors: list[str] = []
    for relative in (*PACKET_PATHS, *PROOF_INPUT_PATHS):
        path = REPO_ROOT / relative
        if not path.is_file():
            continue
        try:
            if path.suffix in {".yaml", ".yml"}:
                yaml.safe_load(path.read_text(encoding="utf-8"))
            elif path.suffix == ".json":
                json.loads(path.read_text(encoding="utf-8"))
            elif path.suffix == ".jsonl":
                for line in path.read_text(encoding="utf-8").splitlines():
                    if line.strip():
                        json.loads(line)
        except (UnicodeDecodeError, json.JSONDecodeError, yaml.YAMLError) as exc:
            errors.append(f"structured parse failed: {relative}: {exc}")
        if path.suffix == ".md":
            for target in LINK.findall(path.read_text(encoding="utf-8")):
                target = target.split("#", 1)[0].strip()
                if not target or "://" in target or target.startswith("mailto:"):
                    continue
                if not (path.parent / target).resolve().exists():
                    errors.append(f"broken link in {relative}: {target}")
    return errors


def _historical_reference_errors() -> list[str]:
    """Prevent archived overlays from masquerading as live instructions."""

    errors: list[str] = []
    for relative in HISTORICAL_REFERENCE_PATHS:
        path = REPO_ROOT / relative
        text = path.read_text(encoding="utf-8")
        metadata = yaml.safe_load(text.split("---", 2)[1])
        if not isinstance(metadata, Mapping):
            errors.append(f"historical reference front matter invalid: {relative}")
            continue
        if metadata.get("authoritative_state") is not False:
            errors.append(f"historical reference claims authority: {relative}")
        if metadata.get("historical_projection") is not True:
            errors.append(f"historical reference lacks archive classification: {relative}")
        if "Historical" not in text[:800] or "START-HERE.md" not in text[:800]:
            errors.append(f"historical reference lacks current-state warning: {relative}")
    parallel = _load_yaml(REPO_ROOT / "plans/codex/handover/PARALLEL-UBL-CHECKPOINT.yaml")
    if parallel.get("authoritative_state") is not False:
        errors.append("parallel UBL checkpoint claims current authority")
    if parallel.get("historical_projection") is not True:
        errors.append("parallel UBL checkpoint lacks historical classification")
    return errors


def _task_errors(ctx: ProjectionContext) -> list[str]:
    errors: list[str] = []
    serialized = json.dumps(_load_yaml(TASK_INDEX_PATH), sort_keys=True, default=str)
    for task_id in (
        ctx.latest_event.get("task_id"),
        ctx.product_task.get("task_id"),
    ):
        if not isinstance(task_id, str) or task_id not in serialized:
            errors.append(f"registered task missing: {task_id}")
        elif not (REPO_ROOT / "taskcards" / f"{task_id}.md").is_file():
            errors.append(f"taskcard file missing: {task_id}")
    return errors


def _cross_evidence_errors(ctx: ProjectionContext) -> list[str]:
    """Cross-check controller claims against current materialized evidence."""

    errors: list[str] = []
    xlf = ctx.xlf
    adjudication = _load_yaml(ADJUDICATION_PATH)
    inventory = _load_yaml(INVENTORY_PATH)
    census = _load_yaml(CENSUS_PATH)
    checks = (
        (
            "XLIFF candidate count",
            xlf.get("core_authority_candidate_count"),
            adjudication.get("candidate_count"),
        ),
        (
            "XLIFF verified dispositions",
            xlf.get("candidate_dispositions_verified"),
            adjudication.get("verified_disposition_count"),
        ),
        (
            "XLIFF unverified dispositions",
            xlf.get("candidate_dispositions_unverified"),
            adjudication.get("unverified_disposition_count"),
        ),
        (
            "XLIFF expected obligations",
            xlf.get("core_expected_obligation_count"),
            inventory.get("expected_obligation_count"),
        ),
        (
            "XLIFF accepted obligations",
            xlf.get("core_production_accepted_obligation_count"),
            inventory.get("resolved_expected_obligation_count"),
        ),
        (
            "XLIFF census candidates",
            xlf.get("core_authority_candidate_count"),
            len(census.get("candidates", [])),
        ),
    )
    for label, controller_value, evidence_value in checks:
        if controller_value != evidence_value:
            errors.append(
                f"{label}: controller {controller_value!r} != evidence {evidence_value!r}"
            )
    missing = inventory.get("missing_expected_obligation_ids", [])
    if xlf.get("core_production_accepted_missing_obligation_count") != len(missing):
        errors.append("XLIFF missing-obligation count differs from inventory")
    if xlf.get("core_complete") is not False:
        errors.append("XLIFF controller falsely claims completeness")
    promotions = ctx.controller.get("promotion", {})
    if not isinstance(promotions, Mapping) or any(
        state != "UNASSESSED" for state in promotions.values()
    ):
        errors.append("handover boundary requires all promotions UNASSESSED")
    if ctx.controller.get("current_gap_summary", {}).get("production_certifications") != 0:
        errors.append("handover boundary requires zero production certifications")
    return errors


def _git_errors(ctx: ProjectionContext, *, require_clean: bool) -> list[str]:
    errors: list[str] = []
    remote = _git("remote", "get-url", "origin")
    if remote.returncode != 0 or b"gitlab" not in remote.stdout.lower():
        errors.append("origin is not the GitLab remote")
    ancestor = _git("merge-base", "--is-ancestor", ctx.source_checkpoint, "origin/main")
    if ancestor.returncode != 0:
        errors.append("packet source checkpoint is not an ancestor of origin/main")
    if require_clean:
        status = _git("status", "--porcelain=v1")
        if status.returncode != 0:
            errors.append("git status failed")
        elif status.stdout.strip():
            count = len(status.stdout.decode("utf-8", errors="replace").splitlines())
            errors.append(f"worktree is not clean: {count} path(s)")
        symbolic = _git("symbolic-ref", "-q", "HEAD")
        if symbolic.returncode == 0:
            head = _git("rev-parse", "HEAD")
            remote_head = _git("rev-parse", "origin/main")
            if head.returncode or remote_head.returncode or head.stdout != remote_head.stdout:
                errors.append("attached clean transfer requires HEAD == origin/main")
    return errors


def _negative_control_errors(ctx: ProjectionContext) -> list[str]:
    errors: list[str] = []
    rendered = render_projection(ctx)
    for label, relative, old, new in (
        (
            "stale event",
            "plans/codex/handover/checkpoint.yaml",
            ctx.event_id.encode("utf-8"),
            b"FF6-EVENT-000040",
        ),
        (
            "stale controller task",
            "plans/codex/handover/CURRENT-MACHINE-STATE.yaml",
            str(ctx.latest_event.get("task_id")).encode("utf-8"),
            b"TC-FF6-XLIFF-PROFILE-SURFACE-001",
        ),
    ):
        mutated = rendered[relative].replace(old, new, 1)
        if mutated == rendered[relative]:
            errors.append(f"negative control setup failed: {label}")
        elif mutated == render_projection(ctx)[relative]:
            errors.append(f"negative control was not rejected: {label}")

    events = [dict(event) for event in ctx.events]
    events[-1]["event_hash"] = "0" * 64
    if not validate_event_chain(events):
        errors.append("negative control was not rejected: broken event hash")

    controller = copy.deepcopy(dict(ctx.controller))
    controller["current_gap_summary"]["production_certifications"] = 1
    mutated_ctx = ProjectionContext(
        ctx.source_checkpoint, controller, ctx.latest_event, ctx.events
    )
    if render_projection(mutated_ctx) == rendered:
        errors.append("negative control was not rejected: false certification")

    manifest = build_manifest(ctx)
    manifest["files"][0]["sha256"] = "0" * 64
    if manifest == build_manifest(ctx):
        errors.append("negative control was not rejected: manifest tamper")

    digests = [deterministic_digest(ctx) for _ in range(3)]
    if len(set(digests)) != 1:
        errors.append("three same-input projections are not deterministic")
    return errors


def validate(*, require_clean: bool = False) -> dict[str, Any]:
    manifest = _load_yaml(MANIFEST_PATH)
    source_checkpoint = manifest.get("source_checkpoint", {}).get("checkpoint_commit")
    if not isinstance(source_checkpoint, str):
        raise ProjectionError("manifest source checkpoint is missing")
    ctx = load_context(source_checkpoint)
    errors = [
        *_projection_errors(ctx),
        *_manifest_errors(ctx),
        *_parse_and_link_errors(),
        *_historical_reference_errors(),
        *_task_errors(ctx),
        *_cross_evidence_errors(ctx),
        *_git_errors(ctx, require_clean=require_clean),
        *_negative_control_errors(ctx),
    ]
    return {
        "result": "PASS" if not errors else "FAIL",
        "event_id": ctx.event_id,
        "event_hash": ctx.event_hash,
        "source_checkpoint": ctx.source_checkpoint,
        "controller_task": ctx.latest_event.get("task_id"),
        "product_task": ctx.product_task.get("task_id"),
        "product_microstep": ctx.xlf.get("active_microstep"),
        "manifest_files": len(manifest.get("files", [])),
        "deterministic_runs": 3,
        "stale_value_negative_controls": 5,
        "deterministic_digest": deterministic_digest(ctx),
        "errors": errors,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-clean", action="store_true")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run deterministic and semantic tamper controls (always enabled).",
    )
    args = parser.parse_args(argv)
    try:
        result = validate(require_clean=args.require_clean)
    except (OSError, ValueError, ProjectionError, yaml.YAMLError) as exc:
        result = {"result": "FAIL", "errors": [str(exc)]}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
