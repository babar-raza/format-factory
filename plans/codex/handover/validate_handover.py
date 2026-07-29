"""Fail-closed, event-neutral validator for the FF6 provider handover.

generated_by: codex
visibility: internal

The packet is a derived projection. The native FF6 journal, controller,
taskcards, immutable Git commits, and content digests remain authoritative.
This validator never repairs state.
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
PARALLEL_UBL_PATH = HANDOVER_ROOT / "PARALLEL-UBL-CHECKPOINT.yaml"
CONTROLLER_PATH = REPO_ROOT / "plans/strategic/ff6/controller-state.yaml"
JOURNAL_PATH = REPO_ROOT / "plans/strategic/ff6/events.jsonl"
TASK_INDEX_PATH = REPO_ROOT / "taskcards/index.yaml"
XLIFF_TASK_PATH = REPO_ROOT / "taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md"
UBL_TASK_PATH = REPO_ROOT / "taskcards/TC-FF6-UBL-TYPING-001.md"

SHA256 = re.compile(r"^[0-9a-f]{64}$")
LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
ALLOWED_STAGED = {
    "reports/skills-rff6/skill-transcripts/"
    "refresh-provider-neutral-handover-event-28.json"
}
ALLOWED_PREFIX = "plans/codex/handover/"


class ValidationFailure(RuntimeError):
    """Raised when a packet input cannot be parsed."""


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


def _snapshot_bytes(relative: str) -> bytes:
    """Use staged bytes, then HEAD, then worktree bytes."""

    for spec in (f":{relative}", f"HEAD:{relative}"):
        result = _git("show", spec)
        if result.returncode == 0:
            return result.stdout.replace(b"\r\n", b"\n")
    path = REPO_ROOT / relative
    if not path.is_file():
        raise ValidationFailure(f"missing packet input: {relative}")
    return _lf_bytes(path)


def _snapshot_sha256(relative: str) -> str:
    return hashlib.sha256(_snapshot_bytes(relative)).hexdigest()


def _event_hash(event: Mapping[str, Any]) -> str:
    body = dict(event)
    body.pop("event_hash", None)
    encoded = json.dumps(
        body, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _load_events() -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for number, line in enumerate(
        JOURNAL_PATH.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValidationFailure(f"journal line {number} is not an object")
        events.append(value)
    if not events:
        raise ValidationFailure("native FF6 journal is empty")
    return events


def _event_chain_errors(events: Sequence[Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    previous: str | None = None
    for expected_sequence, event in enumerate(events, start=1):
        actual_hash = event.get("event_hash")
        if event.get("sequence") != expected_sequence:
            errors.append(
                f"event sequence: expected {expected_sequence}, "
                f"got {event.get('sequence')}"
            )
        if actual_hash != _event_hash(event):
            errors.append(f"event {expected_sequence} hash mismatch")
        if expected_sequence > 1 and event.get("previous_event_hash") != previous:
            errors.append(f"event {expected_sequence} does not bind its predecessor")
        previous = str(actual_hash)
    return errors


def _task_status(value: Any, task_id: str) -> str | None:
    if isinstance(value, Mapping):
        if value.get("id") == task_id:
            return str(value.get("status", "")).lower()
        for child in value.values():
            status = _task_status(child, task_id)
            if status is not None:
                return status
    elif isinstance(value, list):
        for child in value:
            status = _task_status(child, task_id)
            if status is not None:
                return status
    return None


def _expect(
    errors: list[str], label: str, actual: Any, expected: Any
) -> None:
    if actual != expected:
        errors.append(f"{label}: expected {expected!r}, got {actual!r}")


def _manifest_errors(manifest: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    rows = manifest.get("files")
    if not isinstance(rows, list):
        return ["manifest.files is not a list"]
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, Mapping):
            errors.append("manifest entry is not a mapping")
            continue
        relative = row.get("path")
        digest = row.get("sha256")
        size = row.get("canonical_bytes")
        if not isinstance(relative, str) or not isinstance(digest, str):
            errors.append("manifest entry lacks path or sha256")
            continue
        if relative in seen:
            errors.append(f"duplicate manifest path: {relative}")
        seen.add(relative)
        try:
            data = _snapshot_bytes(relative)
        except ValidationFailure as exc:
            errors.append(str(exc))
            continue
        if hashlib.sha256(data).hexdigest() != digest:
            errors.append(f"manifest digest mismatch: {relative}")
        if size is not None and size != len(data):
            errors.append(f"manifest byte-count mismatch: {relative}")
        suffix = Path(relative).suffix.lower()
        try:
            text = data.decode("utf-8")
            if suffix in {".yaml", ".yml"}:
                yaml.safe_load(text)
            elif suffix == ".json":
                json.loads(text)
        except (UnicodeDecodeError, json.JSONDecodeError, yaml.YAMLError) as exc:
            errors.append(f"manifest parse failure {relative}: {exc}")
    if "plans/codex/handover/manifest.yaml" in seen:
        errors.append("root manifest cannot hash itself")
    required = {
        "AGENTS.md",
        "plans/strategic/ff6/controller-state.yaml",
        "plans/strategic/ff6/events.jsonl",
        "taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md",
        "taskcards/TC-FF6-UBL-TYPING-001.md",
        "tools/spec/ubl_schema_graph.py",
        "tools/spec/compile_ubl_schema_graph.py",
        "tests/tools/test_ubl_schema_graph.py",
        "plans/codex/handover/START-HERE.md",
        "plans/codex/handover/CURRENT-SHIFT-HANDOVER.md",
        "plans/codex/handover/CURRENT-MACHINE-STATE.yaml",
        "plans/codex/handover/checkpoint.yaml",
        "plans/codex/handover/INFLIGHT-RECOVERY.yaml",
        "plans/codex/handover/PARALLEL-UBL-CHECKPOINT.yaml",
        "plans/codex/handover/validate_handover.py",
        "plans/codex/handover/event-28/manifest.yaml",
    }
    for missing in sorted(required - seen):
        errors.append(f"required manifest binding absent: {missing}")
    return errors


def _versioned_manifest_errors(
    root_manifest: Mapping[str, Any]
) -> tuple[list[str], dict[str, Any]]:
    versioned_name = root_manifest.get("versioned_packet")
    if not isinstance(versioned_name, str) or not re.fullmatch(
        r"event-\d+", versioned_name
    ):
        return ["manifest.versioned_packet is invalid"], {}
    versioned_root = HANDOVER_ROOT / versioned_name
    manifest_path = versioned_root / "manifest.yaml"
    try:
        manifest = _load_yaml(manifest_path)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return [f"versioned manifest unavailable: {exc}"], {}
    errors: list[str] = []
    rows = manifest.get("files")
    if not isinstance(rows, list):
        return ["versioned manifest.files is not a list"], manifest
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, Mapping):
            errors.append("versioned manifest entry is not a mapping")
            continue
        relative = row.get("path")
        digest = row.get("lf_sha256")
        size = row.get("canonical_bytes")
        if not isinstance(relative, str) or not isinstance(digest, str):
            errors.append("versioned entry lacks path or lf_sha256")
            continue
        seen.add(relative)
        repo_relative = f"plans/codex/handover/{versioned_name}/{relative}"
        try:
            data = _snapshot_bytes(repo_relative)
        except ValidationFailure as exc:
            errors.append(str(exc))
            continue
        if hashlib.sha256(data).hexdigest() != digest:
            errors.append(f"versioned digest mismatch: {relative}")
        if size is not None and size != len(data):
            errors.append(f"versioned byte-count mismatch: {relative}")
    expected = {"START-HERE.md", "CHECKPOINT.yaml", "RUNBOOK.md", "receipt.json"}
    if seen != expected:
        errors.append(
            f"versioned file set: expected {sorted(expected)}, got {sorted(seen)}"
        )
    return errors, manifest


def _link_errors(manifest: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for row in manifest.get("files", []):
        if not isinstance(row, Mapping):
            continue
        relative = row.get("path")
        if not isinstance(relative, str) or not relative.endswith(".md"):
            continue
        path = REPO_ROOT / relative
        text = _snapshot_bytes(relative).decode("utf-8")
        for raw_target in LINK.findall(text):
            target = raw_target.strip()
            if (
                not target
                or target.startswith(("#", "http://", "https://", "mailto:"))
            ):
                continue
            target = target.split("#", 1)[0]
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            candidate = (path.parent / target).resolve()
            try:
                candidate.relative_to(REPO_ROOT.resolve())
            except ValueError:
                errors.append(f"{relative} link escapes repository: {target}")
                continue
            if not candidate.exists():
                errors.append(f"{relative} broken link: {target}")
    return errors


def _git_errors(manifest: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    source = manifest.get("source_checkpoint", {})
    if not isinstance(source, Mapping):
        return ["manifest.source_checkpoint is not a mapping"]
    remote_ref = source.get("required_remote_ref")
    ancestors = [
        source.get("required_ancestor"),
        source.get("implementation_ancestor"),
    ]
    if not isinstance(remote_ref, str):
        errors.append("manifest lacks required_remote_ref")
        return errors
    for ancestor in ancestors:
        if not isinstance(ancestor, str):
            errors.append("manifest lacks a required ancestor")
            continue
        if _git("merge-base", "--is-ancestor", ancestor, remote_ref).returncode:
            errors.append(f"{ancestor} is not an ancestor of {remote_ref}")
    if (
        source.get("forge"),
        source.get("remote"),
        source.get("branch"),
    ) != ("GitLab", "origin", "main"):
        errors.append("canonical source is not GitLab origin/main")
    remote = _git("remote", "get-url", "origin")
    if remote.returncode or b"gitlab" not in remote.stdout.lower():
        errors.append("origin is not a GitLab remote")
    head = _git("rev-parse", "HEAD")
    remote_head = _git("rev-parse", remote_ref)
    if (
        head.returncode
        or remote_head.returncode
        or head.stdout.strip() != remote_head.stdout.strip()
    ):
        errors.append("HEAD must equal fetched origin/main before packet transfer")
    return errors


def _staged_scope_errors() -> list[str]:
    result = _git("diff", "--cached", "--name-only")
    if result.returncode:
        return ["cannot inspect staged paths"]
    errors: list[str] = []
    for line in result.stdout.decode("utf-8").splitlines():
        path = line.strip().replace("\\", "/")
        if path.startswith(ALLOWED_PREFIX) or path in ALLOWED_STAGED:
            continue
        errors.append(f"handover index contains out-of-scope path: {path}")
    return errors


def _handover_worktree_errors() -> list[str]:
    errors: list[str] = []
    unstaged = _git("diff", "--name-only", "--", "plans/codex/handover")
    if unstaged.returncode:
        return ["cannot inspect unstaged handover paths"]
    for line in unstaged.stdout.decode("utf-8").splitlines():
        if line.strip():
            errors.append(f"handover path has unstaged bytes: {line.strip()}")
    untracked = _git(
        "ls-files", "--others", "--exclude-standard", "--", "plans/codex/handover"
    )
    if untracked.returncode:
        errors.append("cannot inspect untracked handover paths")
    else:
        for line in untracked.stdout.decode("utf-8").splitlines():
            if line.strip():
                errors.append(f"handover path is untracked: {line.strip()}")
    return errors


def _porcelain(relative: str) -> str:
    result = _git("status", "--porcelain=v1", "--untracked-files=all", "--", relative)
    if result.returncode:
        raise ValidationFailure(f"cannot inspect Git state for {relative}")
    lines = [line for line in result.stdout.decode("utf-8").splitlines() if line]
    return lines[0][:2] if lines else ""


def _recovery_errors(
    machine: Mapping[str, Any], recovery: Mapping[str, Any]
) -> list[str]:
    errors: list[str] = []
    transfer = machine.get("workspace_transfer", {})
    captured = recovery.get("captured_workspace", {})
    if not isinstance(transfer, Mapping) or not isinstance(captured, Mapping):
        return ["recovery projections are not mappings"]
    machine_assets = transfer.get("recovery_assets")
    recovery_assets = captured.get("recovery_assets")
    _expect(errors, "recovery asset projection", recovery_assets, machine_assets)
    if not isinstance(machine_assets, list):
        return [*errors, "recovery asset list is absent"]
    expected_paths = {
        "reports/ff6/xliff-core-authority-candidate-census.yaml",
        "tests/tools/test_extract_sal_facts.py",
        "tools/spec/extract_sal_facts.py",
        "tests/tools/test_extract_sal_facts_candidate_binding.py",
        "tools/spec/xliff_core_candidate_binding.py",
    }
    seen: set[str] = set()
    for asset in machine_assets:
        if not isinstance(asset, Mapping):
            errors.append("recovery asset is not a mapping")
            continue
        relative = asset.get("path")
        digest = asset.get("lf_sha256")
        size = asset.get("canonical_bytes")
        lines = asset.get("lines")
        state = asset.get("git_state_at_capture")
        if not isinstance(relative, str):
            errors.append("recovery asset lacks path")
            continue
        seen.add(relative)
        if asset.get("presence_policy") != "OPTIONAL_LOCAL_RECOVERY":
            errors.append(f"invalid presence policy: {relative}")
        if (
            not isinstance(digest, str)
            or SHA256.fullmatch(digest) is None
            or not isinstance(size, int)
            or size < 1
            or not isinstance(lines, int)
            or lines < 1
            or state not in {"MODIFIED_TRACKED", "UNTRACKED"}
        ):
            errors.append(f"invalid recovery identity: {relative}")
            continue
        status = _porcelain(relative)
        dirty_as_captured = (
            state == "UNTRACKED"
            and status == "??"
            or state == "MODIFIED_TRACKED"
            and status not in {"", "??"}
        )
        if not dirty_as_captured:
            # A clean checkout does not require provider-local recovery bytes.
            if status == "":
                continue
            if state == "UNTRACKED" and not (REPO_ROOT / relative).exists():
                continue
            errors.append(
                f"recovery Git state mismatch for {relative}: "
                f"expected {state}, got {status or 'CLEAN'}"
            )
            continue
        path = REPO_ROOT / relative
        data = _lf_bytes(path)
        actual_lines = len(data.splitlines())
        if hashlib.sha256(data).hexdigest() != digest:
            errors.append(f"recovery digest mismatch: {relative}")
        if len(data) != size:
            errors.append(f"recovery byte-count mismatch: {relative}")
        if actual_lines != lines:
            errors.append(f"recovery line-count mismatch: {relative}")
    if seen != expected_paths:
        errors.append(
            f"recovery path set: expected {sorted(expected_paths)}, got {sorted(seen)}"
        )
    _expect(
        errors,
        "recovery status",
        captured.get("status"),
        "STALE_SUSPECT_XLIFF_BATCH005_RECOVERY_WORKING_SET",
    )
    _expect(errors, "recovery focused passes", captured.get("focused_test_result", {}).get("passed"), 62)
    _expect(errors, "recovery focused failures", captured.get("focused_test_result", {}).get("failed"), 0)
    _expect(errors, "recovery takeover", captured.get("takeover_required"), True)
    _expect(errors, "recovery canonical bytes", captured.get("current_bytes_canonical"), False)
    return errors


def _semantic_errors(context: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    manifest = context["manifest"]
    checkpoint = context["checkpoint"]
    machine = context["machine"]
    recovery = context["recovery"]
    parallel = context["parallel"]
    versioned = context["versioned"]
    controller = context["controller"]
    task_index = context["task_index"]
    latest = context["latest"]
    texts = context["texts"]

    source = manifest.get("source_checkpoint", {})
    for label, projection in (
        ("checkpoint", checkpoint.get("source_checkpoint", {})),
        ("machine", machine.get("source_checkpoint", {})),
    ):
        _expect(
            errors,
            f"{label} packet input",
            projection.get("packet_input_commit"),
            source.get("required_ancestor"),
        )

    controller_event = controller.get("last_verified_event", {})
    controller_active = controller.get("active_task", {})
    machine_controller = machine.get("controller", {})
    checkpoint_controller = checkpoint.get("controller_checkpoint", {})
    versioned_controller = versioned.get("controller", {})
    manifest_controller = manifest.get("controller", {})
    for label, sequence, event_id, event_hash, state in (
        (
            "controller",
            controller.get("transition_sequence"),
            controller_event.get("event_id"),
            controller_event.get("event_hash"),
            controller.get("controller_state"),
        ),
        (
            "machine",
            machine_controller.get("transition_sequence"),
            machine_controller.get("event_id"),
            machine_controller.get("event_hash"),
            machine_controller.get("state"),
        ),
        (
            "checkpoint",
            checkpoint_controller.get("event_sequence"),
            checkpoint_controller.get("event_id"),
            checkpoint_controller.get("event_head"),
            checkpoint_controller.get("controller_state"),
        ),
        (
            "versioned",
            versioned_controller.get("sequence"),
            versioned_controller.get("event_id"),
            versioned_controller.get("event_hash"),
            versioned_controller.get("state"),
        ),
        (
            "manifest",
            manifest_controller.get("event_sequence"),
            manifest_controller.get("event_id"),
            manifest_controller.get("event_hash"),
            manifest_controller.get("state"),
        ),
    ):
        _expect(errors, f"{label} sequence", sequence, latest.get("sequence"))
        _expect(errors, f"{label} event id", event_id, latest.get("event_id"))
        _expect(errors, f"{label} event hash", event_hash, latest.get("event_hash"))
        _expect(errors, f"{label} state", state, latest.get("state_after"))

    active_task = latest.get("next_task")
    active_state = latest.get("next_task_state")
    for label, task, state in (
        ("controller", controller_active.get("task_id"), controller_active.get("state")),
        ("machine", machine_controller.get("next_task"), machine_controller.get("next_task_state")),
        ("checkpoint", checkpoint_controller.get("exact_next_task"), checkpoint_controller.get("exact_next_state")),
        ("versioned", versioned_controller.get("active_task"), versioned_controller.get("active_task_state")),
        ("manifest", manifest_controller.get("exact_next_task"), manifest_controller.get("exact_next_state")),
    ):
        _expect(errors, f"{label} active task", task, active_task)
        _expect(errors, f"{label} active state", state, active_state)

    _expect(
        errors,
        "XLIFF task registration",
        _task_status(task_index, "TC-FF6-XLIFF-PROFILE-SURFACE-001"),
        "work_in_progress",
    )
    _expect(
        errors,
        "UBL task registration",
        _task_status(task_index, "TC-FF6-UBL-TYPING-001"),
        "work_in_progress",
    )
    _expect(errors, "latest active task", active_task, "TC-FF6-XLIFF-PROFILE-SURFACE-001")
    if "XLF-04-BATCH-005" not in str(latest.get("exact_next_action", "")):
        errors.append("latest event does not preserve XLF-04-BATCH-005")

    event_evidence = latest.get("evidence", {})
    controller_ubl = controller.get("ubl_checkpoint", {})
    machine_ubl = machine.get("parallel_ubl_checkpoint", {})
    checkpoint_ubl = checkpoint.get("verified_ubl_microstep", {})
    parallel_result = parallel.get("bounded_result", {})
    for label, substate in (
        ("event", event_evidence.get("ubl_substate")),
        ("controller", controller_ubl.get("detailed_substate")),
        ("machine", machine_ubl.get("detailed_substate")),
        ("parallel", parallel_result.get("detailed_substate")),
    ):
        _expect(
            errors,
            f"{label} UBL substate",
            substate,
            "SCHEMA_GRAPH_ROOT_TYPE_BINDING_PARTIAL",
        )
    for label, complete in (
        ("event", event_evidence.get("ubl_reachable_schema_graph_complete")),
        ("controller", controller_ubl.get("reachable_schema_graph_complete")),
        ("machine", machine_ubl.get("reachable_schema_graph_complete")),
        ("parallel", parallel.get("truth_boundary", {}).get("reachable_schema_graph_complete")),
        ("checkpoint", checkpoint_ubl.get("complete")),
    ):
        _expect(errors, f"{label} UBL completion", complete, False)
    for label, digest in (
        ("event", event_evidence.get("ubl_root_type_graph_sha256")),
        ("controller", controller_ubl.get("root_type_graph_sha256")),
        ("machine", machine_ubl.get("graph_sha256")),
        ("checkpoint", checkpoint_ubl.get("graph_sha256")),
        ("parallel", parallel.get("graph", {}).get("graph_sha256")),
    ):
        _expect(
            errors,
            f"{label} graph digest",
            digest,
            "7b754187690ce1bb04db62657cfb552653cb381a1bdd745a56856e58215af029",
        )
    for label, value in (
        ("schemas", machine_ubl.get("schema_documents")),
        ("roots", machine_ubl.get("document_roots")),
        ("nodes", machine_ubl.get("root_type_nodes")),
        ("edges", machine_ubl.get("root_type_edges")),
    ):
        _expect(errors, f"UBL {label}", value, {"schemas": 106, "roots": 91, "nodes": 182, "edges": 91}[label])
    _expect(
        errors,
        "UBL implementation commit",
        parallel.get("source_checkpoint", {}).get("implementation_commit"),
        "f98d220a0a3903b1107de90b2e39bf480ec4b19d",
    )
    _expect(
        errors,
        "UBL next microstep",
        machine_ubl.get("next_microstep"),
        "UBL-03-PARTIAL-002",
    )
    if "UBL-03-PARTIAL-002" not in texts["taskcards/TC-FF6-UBL-TYPING-001.md"]:
        errors.append("UBL taskcard lacks exact next microstep")

    workspace = machine.get("workspace_transfer", {})
    _expect(
        errors,
        "workspace transfer state",
        workspace.get("status"),
        "RESUMABLE_COMMITTED_BOUNDARY_WITH_STALE_XLIFF_RECOVERY",
    )
    _expect(errors, "workspace clean bytes", workspace.get("current_bytes_are_clean_checkpoint"), False)
    _expect(errors, "workspace frozen bytes", workspace.get("current_bytes_frozen_by_handover"), False)
    _expect(
        errors,
        "XLIFF recovery status",
        machine.get("latest_xliff_observation", {}).get("status"),
        "STALE_SUSPECT_XLIFF_BATCH005_RECOVERY_WORKING_SET",
    )
    _expect(
        errors,
        "XLIFF current bytes canonical",
        machine.get("latest_xliff_observation", {}).get("current_bytes_canonical"),
        False,
    )

    _expect(errors, "certified products", machine.get("goal", {}).get("products_certified"), 0)
    promotions = machine.get("program_truth", {}).get("promotions", {})
    if not isinstance(promotions, Mapping) or any(
        value != "UNASSESSED" for value in promotions.values()
    ):
        errors.append("one or more promotions are not UNASSESSED")
    _expect(
        errors,
        "parallel certified products",
        parallel.get("truth_boundary", {}).get("products_certified"),
        0,
    )
    _expect(
        errors,
        "Event 28 promotion effect",
        latest.get("promotion_effect"),
        "none",
    )

    start = texts["plans/codex/handover/START-HERE.md"]
    for token in (
        "FF6-EVENT-000028",
        "XLF-04-BATCH-005",
        "UBL-03-PARTIAL-002",
        "STALE_SUSPECT",
        "0/6",
    ):
        if token not in start:
            errors.append(f"START-HERE lacks {token}")

    errors.extend(_recovery_errors(machine, recovery))
    return errors


def validate_current() -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = _load_yaml(MANIFEST_PATH)
    checkpoint = _load_yaml(CHECKPOINT_PATH)
    machine = _load_yaml(MACHINE_PATH)
    recovery = _load_yaml(RECOVERY_PATH)
    parallel = _load_yaml(PARALLEL_UBL_PATH)
    controller = _load_yaml(CONTROLLER_PATH)
    task_index = _load_yaml(TASK_INDEX_PATH)
    events = _load_events()
    latest = events[-1]
    versioned_errors, versioned_manifest = _versioned_manifest_errors(manifest)
    versioned_name = str(manifest.get("versioned_packet", ""))
    versioned = _load_yaml(HANDOVER_ROOT / versioned_name / "CHECKPOINT.yaml")
    text_paths = {
        "plans/codex/handover/START-HERE.md",
        "plans/codex/handover/CURRENT-SHIFT-HANDOVER.md",
        "plans/codex/handover/CLAUDE-START.md",
        "taskcards/TC-FF6-UBL-TYPING-001.md",
        "taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md",
    }
    texts = {
        relative: _snapshot_bytes(relative).decode("utf-8")
        for relative in text_paths
    }
    context = {
        "manifest": manifest,
        "checkpoint": checkpoint,
        "machine": machine,
        "recovery": recovery,
        "parallel": parallel,
        "versioned_manifest": versioned_manifest,
        "versioned": versioned,
        "controller": controller,
        "task_index": task_index,
        "events": events,
        "latest": latest,
        "texts": texts,
    }
    errors = [
        *_event_chain_errors(events),
        *_manifest_errors(manifest),
        *versioned_errors,
        *_link_errors(manifest),
        *_git_errors(manifest),
        *_staged_scope_errors(),
        *_handover_worktree_errors(),
        *_semantic_errors(context),
    ]
    return (
        {
            "schema": "ff6/handover-validation@4",
            "valid": not errors,
            "event_id": latest.get("event_id"),
            "event_sequence": latest.get("sequence"),
            "event_hash": latest.get("event_hash"),
            "canonical_next_task": latest.get("next_task"),
            "canonical_next_microstep": "XLF-04-BATCH-005",
            "fallback_microstep": "UBL-03-PARTIAL-002",
            "manifest_files": len(manifest.get("files", [])),
            "errors": errors,
        },
        context,
    )


def _semantic_only(context: Mapping[str, Any]) -> list[str]:
    return _semantic_errors(context)


def run_self_test(context: dict[str, Any]) -> dict[str, Any]:
    cases: list[tuple[str, dict[str, Any]]] = []

    wrong_head = copy.deepcopy(context)
    wrong_head["machine"]["controller"]["event_hash"] = "0" * 64
    cases.append(("wrong_controller_head", wrong_head))

    false_cert = copy.deepcopy(context)
    false_cert["machine"]["goal"]["products_certified"] = 6
    cases.append(("false_product_certification", false_cert))

    false_ubl_complete = copy.deepcopy(context)
    false_ubl_complete["machine"]["parallel_ubl_checkpoint"][
        "reachable_schema_graph_complete"
    ] = True
    cases.append(("false_ubl_completion", false_ubl_complete))

    wrong_task = copy.deepcopy(context)
    wrong_task["checkpoint"]["controller_checkpoint"][
        "exact_next_task"
    ] = "TC-FF6-UBL-TYPING-001"
    cases.append(("wrong_active_task", wrong_task))

    bad_recovery = copy.deepcopy(context)
    bad_recovery["machine"]["workspace_transfer"]["recovery_assets"][0][
        "lf_sha256"
    ] = "not-a-digest"
    cases.append(("invalid_recovery_identity", bad_recovery))

    false_promotion = copy.deepcopy(context)
    false_promotion["machine"]["program_truth"]["promotions"]["ubl"] = "RELEASED"
    cases.append(("manual_promotion", false_promotion))

    wrong_graph = copy.deepcopy(context)
    wrong_graph["parallel"]["graph"]["graph_sha256"] = "0" * 64
    cases.append(("wrong_graph_identity", wrong_graph))

    missing_task = copy.deepcopy(context)
    for row in missing_task["task_index"].get("taskcards", []):
        if isinstance(row, dict) and row.get("id") == "TC-FF6-UBL-TYPING-001":
            row["status"] = "pass"
    cases.append(("task_registration_drift", missing_task))

    false_xlf_canonical = copy.deepcopy(context)
    false_xlf_canonical["machine"]["latest_xliff_observation"][
        "current_bytes_canonical"
    ] = True
    cases.append(("uncommitted_xliff_adopted", false_xlf_canonical))

    wrong_packet = copy.deepcopy(context)
    wrong_packet["checkpoint"]["source_checkpoint"]["packet_input_commit"] = "0" * 40
    cases.append(("packet_input_mismatch", wrong_packet))

    wrong_ubl_next = copy.deepcopy(context)
    wrong_ubl_next["machine"]["parallel_ubl_checkpoint"][
        "next_microstep"
    ] = "UBL-04"
    cases.append(("wrong_ubl_next_microstep", wrong_ubl_next))

    wrong_event_effect = copy.deepcopy(context)
    wrong_event_effect["latest"]["promotion_effect"] = "promoted"
    cases.append(("event_promotion_overclaim", wrong_event_effect))

    outcomes = [
        {"case": name, "rejected": bool(_semantic_only(case))}
        for name, case in cases
    ]
    return {
        "schema": "ff6/handover-validation-self-test@8",
        "valid": all(item["rejected"] for item in outcomes),
        "negative_controls": outcomes,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    try:
        result, context = validate_current()
        if args.self_test:
            result["self_test"] = run_self_test(context)
            result["valid"] = bool(result["valid"] and result["self_test"]["valid"])
    except (
        OSError,
        ValueError,
        UnicodeDecodeError,
        json.JSONDecodeError,
        yaml.YAMLError,
        ValidationFailure,
    ) as exc:
        result = {
            "schema": "ff6/handover-validation@4",
            "valid": False,
            "errors": [f"{type(exc).__name__}: {exc}"],
        }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("valid") else 1


if __name__ == "__main__":
    sys.exit(main())
