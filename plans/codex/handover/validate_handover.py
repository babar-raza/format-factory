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
NEXT_MICROSTEP_PATH = HANDOVER_ROOT / "NEXT-MICROSTEP.yaml"
CONTROLLER_PATH = REPO_ROOT / "plans/strategic/ff6/controller-state.yaml"
JOURNAL_PATH = REPO_ROOT / "plans/strategic/ff6/events.jsonl"
TASK_INDEX_PATH = REPO_ROOT / "taskcards/index.yaml"
XLIFF_TASK_PATH = REPO_ROOT / "taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md"
UBL_TASK_PATH = REPO_ROOT / "taskcards/TC-FF6-UBL-TYPING-001.md"
XLIFF_CENSUS_PATH = (
    REPO_ROOT / "reports/ff6/xliff-core-authority-candidate-census.yaml"
)

SHA256 = re.compile(r"^[0-9a-f]{64}$")
LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
ALLOWED_STAGED = {
    "reports/skills-rff6/skill-transcripts/"
    "refresh-provider-neutral-handover-event-29.json",
    "reports/skills-rff6/skill-transcripts/"
    "refresh-provider-neutral-handover-event-29-hardening.json",
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
        "plans/codex/handover/NEXT-MICROSTEP.yaml",
        "plans/codex/handover/validate_handover.py",
        "plans/codex/handover/event-29/manifest.yaml",
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
    _expect(errors, "recovery assets", machine_assets, [])
    _expect(
        errors,
        "recovery status",
        captured.get("status"),
        "CLEAN_COMMITTED_GITLAB_MAIN",
    )
    _expect(errors, "recovery takeover", captured.get("takeover_required"), False)
    _expect(errors, "recovery canonical bytes", captured.get("current_bytes_canonical"), True)
    return errors


def _semantic_errors(context: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    manifest = context["manifest"]
    checkpoint = context["checkpoint"]
    machine = context["machine"]
    recovery = context["recovery"]
    parallel = context["parallel"]
    next_microstep = context["next_microstep"]
    census = context["census"]
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

    next_checkpoint = next_microstep.get("checkpoint", {})
    next_task = next_microstep.get("task", {})
    next_baseline = next_microstep.get("baseline", {})
    first_batch = next_microstep.get("first_candidate_batch", {})
    _expect(
        errors,
        "next-microstep event",
        next_checkpoint.get("event_id"),
        latest.get("event_id"),
    )
    _expect(
        errors,
        "next-microstep event hash",
        next_checkpoint.get("event_hash"),
        latest.get("event_hash"),
    )
    _expect(
        errors,
        "next-microstep task",
        next_task.get("task_id"),
        active_task,
    )
    _expect(
        errors,
        "next-microstep task state",
        next_task.get("task_state"),
        active_state,
    )
    _expect(errors, "next-microstep first unmet", next_task.get("first_unmet_step"), "XLF-04")
    _expect(
        errors,
        "next-microstep exact action",
        next_task.get("microstep"),
        "XLF-04-BATCH-005-PARTIAL-002_DISPOSITION_VERIFICATION_AND_OBLIGATION_COMPILATION",
    )

    event_evidence = latest.get("evidence", {})
    controller_ubl = controller.get("ubl_checkpoint", {})
    machine_ubl = machine.get("parallel_ubl_checkpoint", {})
    parallel_result = parallel.get("bounded_result", {})
    for label, substate in (
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
        ("controller", controller_ubl.get("reachable_schema_graph_complete")),
        ("machine", machine_ubl.get("reachable_schema_graph_complete")),
        ("parallel", parallel.get("truth_boundary", {}).get("reachable_schema_graph_complete")),
    ):
        _expect(errors, f"{label} UBL completion", complete, False)
    for label, digest in (
        ("controller", controller_ubl.get("root_type_graph_sha256")),
        ("machine", machine_ubl.get("graph_sha256")),
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
        "RESUMABLE_CLEAN_COMMITTED_BOUNDARY",
    )
    _expect(errors, "workspace clean bytes", workspace.get("current_bytes_are_clean_checkpoint"), True)
    _expect(errors, "workspace frozen bytes", workspace.get("current_bytes_frozen_by_handover"), False)
    _expect(
        errors,
        "XLIFF recovery status",
        machine.get("latest_xliff_observation", {}).get("status"),
        "COMMITTED_SOURCE_AUTHENTIC_DISPOSITIONS_UNVERIFIED",
    )
    _expect(
        errors,
        "XLIFF current bytes canonical",
        machine.get("latest_xliff_observation", {}).get("current_bytes_canonical"),
        True,
    )
    _expect(errors, "candidate count", event_evidence.get("candidate_count"), 1130)
    _expect(
        errors,
        "verified candidate dispositions",
        event_evidence.get("candidate_dispositions_verified"),
        0,
    )
    _expect(
        errors,
        "unverified candidate dispositions",
        event_evidence.get("candidate_dispositions_unverified"),
        1130,
    )
    _expect(
        errors,
        "missing source-bound obligations",
        event_evidence.get("missing_source_bound_obligation_rows"),
        80,
    )
    _expect(errors, "XLF-04 completion", event_evidence.get("xlf_04_complete"), False)
    for label, actual, expected in (
        ("next candidate count", next_baseline.get("candidates"), 1130),
        ("next verified dispositions", next_baseline.get("dispositions_verified"), 0),
        ("next unverified dispositions", next_baseline.get("dispositions_unverified"), 1130),
        ("next expected IDs", next_baseline.get("expected_obligation_ids"), 105),
        (
            "next IDs without candidate mapping",
            next_baseline.get("expected_ids_without_candidate_mapping"),
            60,
        ),
        (
            "next source-bound rows",
            next_baseline.get("source_bound_obligation_rows"),
            25,
        ),
        (
            "next missing source-bound rows",
            next_baseline.get("missing_source_bound_obligation_rows"),
            80,
        ),
    ):
        _expect(errors, label, actual, expected)
    _expect(
        errors,
        "next census digest",
        next_baseline.get("candidate_census_sha256"),
        _snapshot_sha256(
            "reports/ff6/xliff-core-authority-candidate-census.yaml"
        ),
    )

    selected_ids = first_batch.get("candidate_ids")
    _expect(
        errors,
        "first candidate IDs",
        selected_ids,
        ["XLF-CAND-CORE-SCHEMATRON-B109E9507A685F90"],
    )
    census_candidates = census.get("candidates", [])
    selected = [
        row
        for row in census_candidates
        if isinstance(row, Mapping)
        and row.get("candidate_id")
        == "XLF-CAND-CORE-SCHEMATRON-B109E9507A685F90"
    ]
    if len(selected) != 1:
        errors.append(
            "first candidate must resolve exactly once in the canonical census"
        )
    else:
        candidate = selected[0]
        occurrences = candidate.get("occurrences", [])
        occurrence = (
            occurrences[0]
            if isinstance(occurrences, list) and occurrences
            else {}
        )
        authority = first_batch.get("authority", {})
        for candidate_label, candidate_actual, candidate_expected in (
            (
                "first candidate content digest",
                authority.get("candidate_content_sha256"),
                candidate.get("candidate_content_sha256"),
            ),
            (
                "first candidate occurrence digest",
                authority.get("occurrence_sha256"),
                occurrence.get("occurrence_sha256"),
            ),
            (
                "first candidate source digest",
                authority.get("source_sha256"),
                occurrence.get("source_sha256"),
            ),
            (
                "first candidate member digest",
                authority.get("member_sha256"),
                occurrence.get("member_sha256"),
            ),
            (
                "first candidate member",
                authority.get("member"),
                occurrence.get("member"),
            ),
            (
                "first candidate location",
                authority.get("location"),
                occurrence.get("location"),
            ),
            (
                "first candidate proposal",
                first_batch.get("current_generated_proposal", {}).get(
                    "obligation_ids"
                ),
                candidate.get("disposition", {}).get("obligation_ids"),
            ),
        ):
            _expect(
                errors,
                candidate_label,
                candidate_actual,
                candidate_expected,
            )
    _expect(
        errors,
        "independent review state",
        first_batch.get("independent_review", {}).get("status"),
        "NOT_YET_EXECUTED",
    )
    red_ids = {
        row.get("id")
        for row in next_microstep.get("red_controls", [])
        if isinstance(row, Mapping)
    }
    _expect(
        errors,
        "next RED controls",
        red_ids,
        {
            "RED-XLF-DISPOSITION-001",
            "RED-XLF-DISPOSITION-002",
            "RED-XLF-DISPOSITION-003",
            "RED-XLF-DISPOSITION-004",
        },
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
        "Event 29 promotion effect",
        latest.get("promotion_effect"),
        "none",
    )

    start = texts["plans/codex/handover/START-HERE.md"]
    for token in (
        "FF6-EVENT-000029",
        "XLF-04-BATCH-005-PARTIAL-002",
        "UBL-03-PARTIAL-002",
        "1,130",
        "0/6",
    ):
        if token not in start:
            errors.append(f"START-HERE lacks {token}")

    live_projection_requirements = {
        "plans/codex/handover/ACTIVE-WORK-CHECKPOINT.md": (
            "FF6-EVENT-000029",
            "XLF-04-BATCH-005-PARTIAL-002",
            "CLEAN_COMMITTED_GITLAB_MAIN",
        ),
        "plans/codex/handover/PROVIDER-SHIFT-CONTRACT.md": (
            "Event 29",
            "XLF-04-BATCH-005-PARTIAL-002",
            "NEXT-MICROSTEP.yaml",
        ),
        "plans/codex/handover/STATE-MACHINE-AND-TASKCARD-PROTOCOL.md": (
            "Event-29 resume invariant",
            "XLF-04-BATCH-005-PARTIAL-002",
            "NEXT-MICROSTEP.yaml",
        ),
        "plans/codex/handover/VALIDATION-AND-RELEASE.md": (
            "Event 29",
            "NEXT-MICROSTEP.yaml",
            "zero of 1,130",
        ),
    }
    for relative, required_tokens in live_projection_requirements.items():
        text = texts[relative]
        for token in required_tokens:
            if token not in text:
                errors.append(f"{relative} lacks current token {token}")

    stale_projection_phrases = {
        "plans/codex/handover/ACTIVE-WORK-CHECKPOINT.md": (
            "FF6-EVENT-000027",
            "IN_FLIGHT_RED_NOT_TRANSFERABLE",
            "18bb295f94e43338611ef88caff073eed17411c9",
        ),
        "plans/codex/handover/PROVIDER-SHIFT-CONTRACT.md": (
            "Five dirty XLIFF paths are foreign",
            "Canonical exact next microstep is `XLF-04-BATCH-005`.",
            "`CONTRACT`, Event 27, XLIFF `XLF-04-BATCH-005`",
        ),
    }
    for relative, stale_phrases in stale_projection_phrases.items():
        text = texts[relative]
        for phrase in stale_phrases:
            if phrase in text:
                errors.append(f"{relative} retains stale current-state text: {phrase}")

    errors.extend(_recovery_errors(machine, recovery))
    return errors


def validate_current() -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = _load_yaml(MANIFEST_PATH)
    checkpoint = _load_yaml(CHECKPOINT_PATH)
    machine = _load_yaml(MACHINE_PATH)
    recovery = _load_yaml(RECOVERY_PATH)
    parallel = _load_yaml(PARALLEL_UBL_PATH)
    next_microstep = _load_yaml(NEXT_MICROSTEP_PATH)
    census = _load_yaml(XLIFF_CENSUS_PATH)
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
        "plans/codex/handover/ACTIVE-WORK-CHECKPOINT.md",
        "plans/codex/handover/PROVIDER-SHIFT-CONTRACT.md",
        "plans/codex/handover/STATE-MACHINE-AND-TASKCARD-PROTOCOL.md",
        "plans/codex/handover/VALIDATION-AND-RELEASE.md",
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
        "next_microstep": next_microstep,
        "census": census,
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
            "schema": "ff6/handover-validation@5",
            "valid": not errors,
            "event_id": latest.get("event_id"),
            "event_sequence": latest.get("sequence"),
            "event_hash": latest.get("event_hash"),
            "canonical_next_task": latest.get("next_task"),
            "canonical_next_microstep": "XLF-04-BATCH-005-PARTIAL-002_DISPOSITION_VERIFICATION_AND_OBLIGATION_COMPILATION",
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
    bad_recovery["machine"]["workspace_transfer"]["recovery_assets"] = [
        {"path": "uncommitted-provider-local-byte"}
    ]
    cases.append(("unexpected_recovery_asset", bad_recovery))

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
    ] = False
    cases.append(("committed_xliff_rejected", false_xlf_canonical))

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

    stale_provider = copy.deepcopy(context)
    stale_provider["texts"][
        "plans/codex/handover/PROVIDER-SHIFT-CONTRACT.md"
    ] += "\nFive dirty XLIFF paths are foreign\n"
    cases.append(("stale_provider_projection", stale_provider))

    wrong_candidate_digest = copy.deepcopy(context)
    wrong_candidate_digest["next_microstep"]["first_candidate_batch"][
        "authority"
    ]["candidate_content_sha256"] = "0" * 64
    cases.append(("next_candidate_digest_drift", wrong_candidate_digest))

    false_independent_review = copy.deepcopy(context)
    false_independent_review["next_microstep"]["first_candidate_batch"][
        "independent_review"
    ]["status"] = "VERIFIED"
    cases.append(("unexecuted_adjudication_overclaim", false_independent_review))

    missing_red_control = copy.deepcopy(context)
    missing_red_control["next_microstep"]["red_controls"] = missing_red_control[
        "next_microstep"
    ]["red_controls"][:-1]
    cases.append(("missing_next_red_control", missing_red_control))

    outcomes = [
        {"case": name, "rejected": bool(_semantic_only(case))}
        for name, case in cases
    ]
    return {
        "schema": "ff6/handover-validation-self-test@9",
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
            "schema": "ff6/handover-validation@5",
            "valid": False,
            "errors": [f"{type(exc).__name__}: {exc}"],
        }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("valid") else 1


if __name__ == "__main__":
    sys.exit(main())
