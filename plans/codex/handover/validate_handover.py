"""Fail-closed validator for the FF6 provider-neutral handover.

generated_by: codex
visibility: internal

The packet is a derived projection. GitLab main, the native journal,
controller, taskcards, and content-addressed evidence remain authoritative.
This program validates; it never repairs or promotes state.
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


HANDOVER_ROOT = Path(__file__).resolve().parent
REPO_ROOT = HANDOVER_ROOT.parents[2]
MANIFEST_PATH = HANDOVER_ROOT / "manifest.yaml"
CHECKPOINT_PATH = HANDOVER_ROOT / "checkpoint.yaml"
MACHINE_PATH = HANDOVER_ROOT / "CURRENT-MACHINE-STATE.yaml"
RECOVERY_PATH = HANDOVER_ROOT / "INFLIGHT-RECOVERY.yaml"
NEXT_PATH = HANDOVER_ROOT / "NEXT-MICROSTEP.yaml"
CONTROLLER_PATH = REPO_ROOT / "plans/strategic/ff6/controller-state.yaml"
JOURNAL_PATH = REPO_ROOT / "plans/strategic/ff6/events.jsonl"
TASK_INDEX_PATH = REPO_ROOT / "taskcards/index.yaml"
XLIFF_TASK_PATH = REPO_ROOT / "taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md"
CENSUS_PATH = REPO_ROOT / "reports/ff6/xliff-core-authority-candidate-census.yaml"
ADJUDICATION_PATH = (
    REPO_ROOT / "reports/sal-verification/xliff-core-candidate-adjudications.yaml"
)
INVENTORY_PATH = REPO_ROOT / "reports/ff6/xliff-core-obligation-inventory.yaml"
OPERATIONAL_DOC_PATHS = (
    "plans/codex/handover/START-HERE.md",
    "plans/codex/handover/CLAUDE-START.md",
    "plans/codex/handover/ACTIVE-WORK-CHECKPOINT.md",
    "plans/codex/handover/CURRENT-MACHINE-STATE.yaml",
    "plans/codex/handover/checkpoint.yaml",
    "plans/codex/handover/NEXT-MICROSTEP.yaml",
    "plans/codex/handover/CURRENT-SHIFT-HANDOVER.md",
    "plans/codex/handover/PROVIDER-SHIFT-CONTRACT.md",
    "plans/codex/handover/SHIFT-AND-RESUME-PROTOCOL.md",
    "plans/codex/handover/EXECUTION-RUNBOOK.md",
    "plans/codex/handover/STATE-MACHINE-AND-TASKCARD-PROTOCOL.md",
    "plans/codex/handover/VALIDATION-AND-RELEASE.md",
    "plans/codex/handover/PARALLEL-UBL-CHECKPOINT.yaml",
    "plans/codex/handover/INFLIGHT-RECOVERY.yaml",
    "plans/codex/handover/EVENT-31-DELTA.md",
    "plans/codex/handover/event-31/START-HERE.md",
    "plans/codex/handover/event-31/RUNBOOK.md",
)

EXPECTED_EVENT_ID = "FF6-EVENT-000031"
EXPECTED_EVENT_HASH = (
    "26f95f054774f35244a2edbfc08072156a1422acfb1e1d29c2c37a617dd90d55"
)
EXPECTED_CONTROL = "240474babf868fa141850d4ed4792d3a8269ef28"
EXPECTED_IMPLEMENTATION = "d99fc6bf3679cd39396afbf5621847e3009ddf31"
EXPECTED_ACCEPTED_IMPLEMENTATION = "e13e103de0bb789ff51a8e931af0fb649474be20"
EXPECTED_TASK = "TC-FF6-XLIFF-PROFILE-SURFACE-001"
EXPECTED_MICROSTEP = "XLF-04-BATCH-005-PARTIAL-002-B-REPAIR-001"
EXPECTED_PLAN_MICROSTEP = "XLF-04-BATCH-005-PARTIAL-002-B"
EXPECTED_CANDIDATE = "XLF-CAND-CORE-SCHEMATRON-00C4A041AF12C8A1"
EXPECTED_CANDIDATE_SHA256 = (
    "0a37761215603eb4db3f9602f6e979869b4f1f44c124c1f5ca2183cba1d7578a"
)
EXPECTED_RECIPROCAL_CANDIDATE = "XLF-CAND-CORE-SCHEMATRON-4BE479DD3F5875EF"
EXPECTED_RECIPROCAL_CANDIDATE_SHA256 = (
    "246f6e9e4c64fe142760045dbca69070405ae50f552b34387ce8709c3c7226e3"
)
EXPECTED_PAIRING_OBLIGATION = "SAL-XLIFF-CORE-INLINE-PAIRING-001"
EXPECTED_ADJUDICATION_SHA256 = (
    "3d9c81773ceaddaae97a55fc804bd35efaf6501fe24c9fae8bf941fe338ceb01"
)
EXPECTED_INVENTORY_SHA256 = (
    "d5f77d95c703f62766e4ef4178ee3d811147df06844f0eacdec372bbd51cb351"
)
STALE_OPERATIONAL_TOKENS = (
    "FF6-EVENT-000029",
    "315efa5f5f4420202b5254c86ccd8863a91c385f",
    "c1f4be66b97acb9a23faa02764e3d41ec1e4a3b0",
    "edcc121152e4a238b62c33180f9e733badfde4b7",
    "XLF-04-BATCH-005-PARTIAL-002_DISPOSITION_VERIFICATION_AND_OBLIGATION_COMPILATION",
    "seven recovery paths",
    "seven matching recovery",
    "packet_projection_changes_pending_commit: true",
)
SHA256 = re.compile(r"^[0-9a-f]{64}$")
LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
ALLOWED_DIRTY_PREFIXES = (
    "plans/codex/handover/",
    "reports/skills-rff6/skill-transcripts/"
    "plan-control-xliff-profile-surface-wip-009.json",
    "reports/skills-rff6/skill-transcripts/"
    "refresh-provider-neutral-handover-event-30.json",
)
ALLOWED_DIRTY_EXACT = {
    "plans/strategic/ff6/controller-state.yaml",
    "plans/strategic/ff6/events.jsonl",
    "taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md",
    "taskcards/TC-FF6-HANDOVER-CLAUDE-001.md",
    "reports/skills-rff6/skill-transcripts/"
    "refresh-provider-neutral-handover-event-30-deep-resume.json",
    "reports/skills-rff6/skill-transcripts/"
    "refresh-provider-neutral-handover-event-31.json",
}


class ValidationFailure(RuntimeError):
    """Raised when an input cannot be parsed."""


def _git(*args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
    )


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValidationFailure(f"{path.relative_to(REPO_ROOT)} is not a mapping")
    return value


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValidationFailure(f"{path.relative_to(REPO_ROOT)} is not an object")
    return value


def _lf_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n")


def _sha256(path: Path) -> str:
    return hashlib.sha256(_lf_bytes(path)).hexdigest()


def _event_hash(event: Mapping[str, Any]) -> str:
    body = dict(event)
    body.pop("event_hash", None)
    encoded = json.dumps(
        body,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _events() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(
        JOURNAL_PATH.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValidationFailure(f"journal line {number} is not an object")
        rows.append(value)
    if not rows:
        raise ValidationFailure("native event journal is empty")
    return rows


def _event_chain_errors(events: Sequence[Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    previous: str | None = None
    for sequence, event in enumerate(events, start=1):
        if event.get("sequence") != sequence:
            errors.append(f"event {sequence}: non-sequential sequence")
        claimed = event.get("event_hash")
        if claimed != _event_hash(event):
            errors.append(f"event {sequence}: hash mismatch")
        if sequence > 1 and event.get("previous_event_hash") != previous:
            errors.append(f"event {sequence}: predecessor mismatch")
        previous = claimed if isinstance(claimed, str) else None
    return errors


def _expect(
    errors: list[str],
    label: str,
    actual: Any,
    expected: Any,
) -> None:
    if actual != expected:
        errors.append(f"{label}: expected {expected!r}, got {actual!r}")


def _semantic_errors(
    *,
    manifest: Mapping[str, Any],
    checkpoint: Mapping[str, Any],
    machine: Mapping[str, Any],
    recovery: Mapping[str, Any],
    next_step: Mapping[str, Any],
    controller: Mapping[str, Any],
    latest: Mapping[str, Any],
    adjudication: Mapping[str, Any],
    inventory: Mapping[str, Any],
) -> list[str]:
    errors: list[str] = []
    event_views = (
        ("manifest", manifest.get("controller", {})),
        ("checkpoint", checkpoint.get("controller_checkpoint", {})),
        ("machine", machine.get("controller", {})),
    )
    for label, value in event_views:
        event_id = value.get("event_id")
        event_hash = value.get("event_hash", value.get("event_head"))
        sequence = value.get("event_sequence", value.get("transition_sequence"))
        _expect(errors, f"{label} event id", event_id, EXPECTED_EVENT_ID)
        _expect(errors, f"{label} event hash", event_hash, EXPECTED_EVENT_HASH)
        _expect(errors, f"{label} event sequence", sequence, 31)

    _expect(errors, "latest event id", latest.get("event_id"), EXPECTED_EVENT_ID)
    _expect(errors, "latest event hash", latest.get("event_hash"), EXPECTED_EVENT_HASH)
    _expect(errors, "latest state", latest.get("state_after"), "CONTRACT")
    _expect(errors, "latest task", latest.get("task_id"), EXPECTED_TASK)
    _expect(
        errors,
        "latest implementation",
        latest.get("evidence", {}).get("checkpoint_source_commit"),
        EXPECTED_IMPLEMENTATION,
    )
    _expect(
        errors,
        "controller event hash",
        controller.get("last_verified_event", {}).get("event_hash"),
        EXPECTED_EVENT_HASH,
    )
    _expect(errors, "controller sequence", controller.get("transition_sequence"), 31)
    _expect(errors, "controller state", controller.get("controller_state"), "CONTRACT")

    _expect(
        errors,
        "machine microstep",
        machine.get("controller", {}).get("exact_microstep"),
        EXPECTED_MICROSTEP,
    )
    _expect(
        errors,
        "next microstep",
        next_step.get("task", {}).get("microstep"),
        EXPECTED_PLAN_MICROSTEP,
    )
    _expect(
        errors,
        "next candidate",
        next_step.get("selected_candidate", {}).get("candidate_id"),
        EXPECTED_CANDIDATE,
    )
    _expect(
        errors,
        "next candidate digest",
        next_step.get("selected_candidate", {}).get("candidate_content_sha256"),
        EXPECTED_CANDIDATE_SHA256,
    )
    _expect(
        errors,
        "reciprocal candidate",
        next_step.get("reciprocal_candidate", {}).get("candidate_id"),
        EXPECTED_RECIPROCAL_CANDIDATE,
    )
    _expect(
        errors,
        "reciprocal candidate digest",
        next_step.get("reciprocal_candidate", {}).get(
            "candidate_content_sha256"
        ),
        EXPECTED_RECIPROCAL_CANDIDATE_SHA256,
    )
    _expect(
        errors,
        "direct semantic owner",
        next_step.get("deep_reassessment", {})
        .get("direct_semantic_owner", {})
        .get("obligation_id"),
        EXPECTED_PAIRING_OBLIGATION,
    )
    _expect(
        errors,
        "reassessment implementation status",
        next_step.get("deep_reassessment", {}).get("evidence_status"),
        "READ_ONLY_FINDING_NOT_YET_IMPLEMENTED",
    )

    xliff = machine.get("xliff", {})
    baseline = next_step.get("baseline", {})
    event_evidence = latest.get("evidence", {})
    _expect(
        errors,
        "machine accepted dispositions",
        xliff.get("adjudication", {}).get("production_accepted_dispositions"),
        1,
    )
    _expect(
        errors,
        "machine open dispositions",
        xliff.get("adjudication", {}).get("production_open_dispositions"),
        1129,
    )
    _expect(errors, "plan verified dispositions", baseline.get("dispositions_verified"), 1)
    _expect(errors, "plan open dispositions", baseline.get("dispositions_unverified"), 1129)
    _expect(
        errors,
        "event accepted dispositions",
        event_evidence.get("production_accepted_candidate_dispositions"),
        1,
    )

    inventory_view = xliff.get("obligation_inventory", {})
    _expect(errors, "machine expected obligations", inventory_view.get("expected"), 105)
    _expect(
        errors,
        "machine accepted source-bound obligations",
        inventory_view.get("production_accepted_source_bound"),
        26,
    )
    _expect(
        errors,
        "machine accepted missing obligations",
        inventory_view.get("production_accepted_missing"),
        79,
    )
    _expect(errors, "machine mechanical source-bound", inventory_view.get("mechanical_source_bound"), 27)
    _expect(errors, "machine mechanical missing", inventory_view.get("mechanical_missing"), 78)
    _expect(errors, "machine XLF complete", inventory_view.get("complete"), False)
    _expect(errors, "inventory expected", inventory.get("expected_obligation_count"), 105)
    _expect(errors, "inventory resolved", inventory.get("resolved_expected_obligation_count"), 27)
    _expect(
        errors,
        "inventory missing",
        len(inventory.get("missing_expected_obligation_ids", [])),
        78,
    )
    _expect(errors, "inventory complete", inventory.get("complete"), False)
    _expect(errors, "adjudication candidate count", adjudication.get("candidate_count"), 1130)
    _expect(errors, "adjudication verified", adjudication.get("verified_disposition_count"), 2)
    _expect(errors, "adjudication unverified", adjudication.get("unverified_disposition_count"), 1128)
    _expect(errors, "adjudication complete", adjudication.get("disposition_verification_complete"), False)

    _expect(
        errors,
        "recovery product overlay",
        recovery.get("captured_workspace", {}).get("product_overlay_status"),
        "NONE_COMMITTED_ATTEMPT_PRESERVED",
    )
    _expect(
        errors,
        "recovery local dependency",
        recovery.get("captured_workspace", {}).get("local_only_required_for_resume"),
        False,
    )
    _expect(
        errors,
        "products certified",
        machine.get("program_truth", {}).get("production_certifications"),
        0,
    )
    for product, state in machine.get("program_truth", {}).get("promotion", {}).items():
        _expect(errors, f"promotion {product}", state, "UNASSESSED")
    return errors


def _manifest_errors(manifest: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    files = manifest.get("files")
    if not isinstance(files, list):
        return ["manifest files is not a list"]
    seen: set[str] = set()
    for index, row in enumerate(files):
        if not isinstance(row, Mapping):
            errors.append(f"manifest file {index} is not a mapping")
            continue
        relative = row.get("path")
        digest = row.get("sha256")
        size = row.get("canonical_bytes")
        if not isinstance(relative, str):
            errors.append(f"manifest file {index} has no path")
            continue
        if relative in seen:
            errors.append(f"manifest duplicate path: {relative}")
        seen.add(relative)
        path = REPO_ROOT / relative
        if not path.is_file():
            errors.append(f"manifest missing file: {relative}")
            continue
        data = _lf_bytes(path)
        actual = hashlib.sha256(data).hexdigest()
        if digest != actual:
            errors.append(f"manifest digest mismatch: {relative}")
        if size != len(data):
            errors.append(f"manifest byte count mismatch: {relative}")
        if not isinstance(digest, str) or not SHA256.fullmatch(digest):
            errors.append(f"manifest invalid digest: {relative}")
    expected_count = manifest.get("validation", {}).get("expected_manifest_files")
    _expect(errors, "manifest file count", len(files), expected_count)
    return errors


def _manifest_parse_errors(manifest: Mapping[str, Any]) -> list[str]:
    """Parse every structured artifact named by the packet manifest."""

    errors: list[str] = []
    for row in manifest.get("files", []):
        if not isinstance(row, Mapping) or not isinstance(row.get("path"), str):
            continue
        relative = row["path"]
        path = REPO_ROOT / relative
        if not path.is_file():
            continue
        try:
            if path.suffix in {".yaml", ".yml"}:
                yaml.safe_load(path.read_text(encoding="utf-8"))
            elif path.suffix == ".json":
                json.loads(path.read_text(encoding="utf-8"))
            elif path.suffix == ".jsonl":
                for number, line in enumerate(
                    path.read_text(encoding="utf-8").splitlines(),
                    start=1,
                ):
                    if line.strip():
                        json.loads(line)
        except (UnicodeDecodeError, json.JSONDecodeError, yaml.YAMLError) as exc:
            errors.append(f"structured artifact parse failed: {relative}: {exc}")
    return errors


def _link_errors(manifest: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    rows = manifest.get("files", [])
    markdown = [
        REPO_ROOT / row["path"]
        for row in rows
        if isinstance(row, Mapping)
        and isinstance(row.get("path"), str)
        and row["path"].endswith(".md")
        and (REPO_ROOT / row["path"]).is_file()
    ]
    for path in markdown:
        for target in LINK.findall(path.read_text(encoding="utf-8")):
            target = target.split("#", 1)[0].strip()
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            if not (path.parent / target).resolve().exists():
                errors.append(
                    f"broken link in {path.relative_to(REPO_ROOT)}: {target}"
                )
    return errors


def _task_errors() -> list[str]:
    errors: list[str] = []
    index = _load_yaml(TASK_INDEX_PATH)
    serialized = json.dumps(index, sort_keys=True, default=str)
    if EXPECTED_TASK not in serialized:
        errors.append("active task is absent from taskcards/index.yaml")
    text = XLIFF_TASK_PATH.read_text(encoding="utf-8")
    for value in (EXPECTED_EVENT_ID, EXPECTED_MICROSTEP, EXPECTED_CANDIDATE):
        if value not in text:
            errors.append(f"active taskcard omits {value}")
    return errors


def _operational_documents() -> dict[str, str]:
    return {
        relative: (REPO_ROOT / relative).read_text(encoding="utf-8")
        for relative in OPERATIONAL_DOC_PATHS
    }


def _operational_doc_errors(documents: Mapping[str, str]) -> list[str]:
    """Reject current instructions that still route through an older event."""

    errors: list[str] = []
    for relative in OPERATIONAL_DOC_PATHS:
        text = documents.get(relative)
        if text is None:
            errors.append(f"operational document missing from validation: {relative}")
            continue
        for token in STALE_OPERATIONAL_TOKENS:
            if token in text:
                errors.append(f"stale operational token in {relative}: {token}")

    required_markers = {
        "plans/codex/handover/PROVIDER-SHIFT-CONTRACT.md": (
            EXPECTED_EVENT_ID,
            EXPECTED_IMPLEMENTATION,
            EXPECTED_MICROSTEP,
        ),
        "plans/codex/handover/SHIFT-AND-RESUME-PROTOCOL.md": (
            EXPECTED_EVENT_ID,
            EXPECTED_IMPLEMENTATION,
            EXPECTED_MICROSTEP,
        ),
        "plans/codex/handover/EXECUTION-RUNBOOK.md": (
            EXPECTED_EVENT_ID,
            EXPECTED_MICROSTEP,
        ),
        "plans/codex/handover/STATE-MACHINE-AND-TASKCARD-PROTOCOL.md": (
            EXPECTED_EVENT_ID,
            EXPECTED_MICROSTEP,
        ),
        "plans/codex/handover/VALIDATION-AND-RELEASE.md": (
            EXPECTED_EVENT_ID,
        ),
        "plans/codex/handover/PARALLEL-UBL-CHECKPOINT.yaml": (
            EXPECTED_EVENT_ID,
        ),
        "plans/codex/handover/INFLIGHT-RECOVERY.yaml": (
            EXPECTED_EVENT_ID,
            EXPECTED_IMPLEMENTATION,
            EXPECTED_MICROSTEP,
        ),
    }
    for relative, markers in required_markers.items():
        text = documents.get(relative, "")
        for marker in markers:
            if marker not in text:
                errors.append(f"current marker missing from {relative}: {marker}")
    return errors


def _git_errors(*, require_clean: bool) -> list[str]:
    errors: list[str] = []
    control = _git(
        "merge-base",
        "--is-ancestor",
        EXPECTED_CONTROL,
        "origin/main",
    )
    if control.returncode != 0:
        errors.append("Event 31 control commit is not an ancestor of origin/main")
    ancestor = _git(
        "merge-base",
        "--is-ancestor",
        EXPECTED_IMPLEMENTATION,
        "origin/main",
    )
    if ancestor.returncode != 0:
        errors.append("implementation commit is not an ancestor of origin/main")
    remote = _git("remote", "get-url", "origin")
    if remote.returncode != 0 or b"gitlab" not in remote.stdout.lower():
        errors.append("origin is not the GitLab remote")
    status = _git("status", "--porcelain=v1")
    if status.returncode != 0:
        errors.append("git status failed")
        return errors
    dirty: list[str] = []
    for raw in status.stdout.decode("utf-8", errors="replace").splitlines():
        path = raw[3:].replace("\\", "/")
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        dirty.append(path)
        if not (
            path in ALLOWED_DIRTY_EXACT
            or any(path.startswith(prefix) for prefix in ALLOWED_DIRTY_PREFIXES)
        ):
            errors.append(f"unexplained dirty path: {path}")
    if require_clean and dirty:
        errors.append(f"worktree is not clean: {len(dirty)} path(s)")
    return errors


def _negative_control_errors(base: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    cases: list[tuple[str, tuple[str, ...], Any]] = [
        ("wrong event", ("machine", "controller", "event_hash"), "0" * 64),
        ("false completion", ("machine", "xliff", "obligation_inventory", "complete"), True),
        ("inflated certification", ("machine", "program_truth", "production_certifications"), 1),
        ("wrong candidate", ("next", "selected_candidate", "candidate_id"), "XLF-CAND-FORGED"),
        (
            "wrong reciprocal candidate",
            ("next", "reciprocal_candidate", "candidate_id"),
            "XLF-CAND-FORGED-RECIPROCAL",
        ),
        (
            "wrong direct semantic owner",
            (
                "next",
                "deep_reassessment",
                "direct_semantic_owner",
                "obligation_id",
            ),
            "SAL-XLIFF-CORE-INLINE-PC-001",
        ),
        (
            "inflated accepted row count",
            (
                "machine",
                "xliff",
                "obligation_inventory",
                "production_accepted_source_bound",
            ),
            105,
        ),
        ("local-only dependency", ("recovery", "captured_workspace", "local_only_required_for_resume"), True),
    ]
    for label, path, value in cases:
        mutated = copy.deepcopy(base)
        cursor: dict[str, Any] = mutated
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = value
        found = _semantic_errors(
            manifest=mutated["manifest"],
            checkpoint=mutated["checkpoint"],
            machine=mutated["machine"],
            recovery=mutated["recovery"],
            next_step=mutated["next"],
            controller=mutated["controller"],
            latest=mutated["latest"],
            adjudication=mutated["adjudication"],
            inventory=mutated["inventory"],
        )
        if not found:
            errors.append(f"negative control was not rejected: {label}")
    mutated_documents = copy.deepcopy(base["documents"])
    provider_contract = "plans/codex/handover/PROVIDER-SHIFT-CONTRACT.md"
    mutated_documents[provider_contract] += "\nFF6-EVENT-000029\n"
    if not _operational_doc_errors(mutated_documents):
        errors.append("negative control was not rejected: stale operational event")
    return errors


def validate(*, require_clean: bool = False) -> dict[str, Any]:
    manifest = _load_yaml(MANIFEST_PATH)
    checkpoint = _load_yaml(CHECKPOINT_PATH)
    machine = _load_yaml(MACHINE_PATH)
    recovery = _load_yaml(RECOVERY_PATH)
    next_step = _load_yaml(NEXT_PATH)
    controller = _load_yaml(CONTROLLER_PATH)
    adjudication = _load_yaml(ADJUDICATION_PATH)
    inventory = _load_yaml(INVENTORY_PATH)
    events = _events()
    latest = events[-1]
    documents = _operational_documents()
    base = {
        "manifest": manifest,
        "checkpoint": checkpoint,
        "machine": machine,
        "recovery": recovery,
        "next": next_step,
        "controller": controller,
        "latest": latest,
        "adjudication": adjudication,
        "inventory": inventory,
        "documents": documents,
    }
    errors = [
        *_event_chain_errors(events),
        *_semantic_errors(
            manifest=manifest,
            checkpoint=checkpoint,
            machine=machine,
            recovery=recovery,
            next_step=next_step,
            controller=controller,
            latest=latest,
            adjudication=adjudication,
            inventory=inventory,
        ),
        *_manifest_errors(manifest),
        *_manifest_parse_errors(manifest),
        *_link_errors(manifest),
        *_task_errors(),
        *_operational_doc_errors(documents),
        *_git_errors(require_clean=require_clean),
        *_negative_control_errors(base),
    ]
    return {
        "result": "PASS" if not errors else "FAIL",
        "event_id": latest.get("event_id"),
        "event_hash": latest.get("event_hash"),
        "implementation_commit": EXPECTED_IMPLEMENTATION,
        "next_microstep": EXPECTED_MICROSTEP,
        "next_candidate": EXPECTED_CANDIDATE,
        "manifest_files": len(manifest.get("files", [])),
        "semantic_negative_controls": 9,
        "errors": errors,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-clean", action="store_true")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the built-in semantic tamper controls (always enabled).",
    )
    args = parser.parse_args(argv)
    try:
        result = validate(require_clean=args.require_clean)
    except (OSError, ValueError, ValidationFailure, yaml.YAMLError) as exc:
        result = {"result": "FAIL", "errors": [str(exc)]}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
