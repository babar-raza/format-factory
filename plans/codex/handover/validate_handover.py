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
    "plans/codex/handover/CLEAN-REPLAY-REPAIR.md",
    "plans/codex/handover/ACTIVE-WORK-CHECKPOINT.md",
    "plans/codex/handover/CURRENT-MACHINE-STATE.yaml",
    "plans/codex/handover/checkpoint.yaml",
    "plans/codex/handover/NEXT-MICROSTEP.yaml",
    "plans/codex/handover/CURRENT-SHIFT-HANDOVER.md",
    "plans/codex/handover/INFLIGHT-RECOVERY.yaml",
)
REFERENCE_DOC_PATHS = (
    "plans/codex/handover/PROVIDER-SHIFT-CONTRACT.md",
    "plans/codex/handover/SHIFT-AND-RESUME-PROTOCOL.md",
    "plans/codex/handover/EXECUTION-RUNBOOK.md",
    "plans/codex/handover/STATE-MACHINE-AND-TASKCARD-PROTOCOL.md",
    "plans/codex/handover/VALIDATION-AND-RELEASE.md",
    "plans/codex/handover/CURRENT-STATE-AND-ROOT-CAUSES.md",
)
PARALLEL_UBL_PATH = "plans/codex/handover/PARALLEL-UBL-CHECKPOINT.yaml"

EXPECTED_EVENT_ID = "FF6-EVENT-000039"
EXPECTED_EVENT_HASH = (
    "5f76c75ca4f7bc0845b22dccd38a195e962fb49b5f4161651737ab23d560cd36"
)
EXPECTED_SEQUENCE = 39
EXPECTED_CONTROL = "c421940ae70a3dc949318eee00cbfc5e3cf8b9a3"
EXPECTED_IMPLEMENTATION = "39b2e89fde0f7dd5e1acebc424f4d700dfe74765"
EXPECTED_XLIFF_IMPLEMENTATION = "39b2e89fde0f7dd5e1acebc424f4d700dfe74765"
EXPECTED_PREVIOUS_NON_PROMOTING_ATTEMPT = (
    "2dcb161ed8e53bfc55e5be81374f5f7ddea3bb17"
)
EXPECTED_REPAIR_COMMIT = "809cc18cc6e62ae19f6ea5c11ed41ab9a7ec5956"
EXPECTED_EVENT_TASK = "TC-FF6-XLIFF-PROFILE-SURFACE-001"
EXPECTED_TASK = "TC-FF6-XLIFF-PROFILE-SURFACE-001"
EXPECTED_XLIFF_EVENT_ID = "FF6-EVENT-000039"
EXPECTED_MICROSTEP = "XLF-04-BATCH-005-PARTIAL-002-H"
EXPECTED_RESUME_MICROSTEP = "XLF-04-BATCH-005-PARTIAL-002-H"
EXPECTED_CANDIDATE = "XLF-CAND-CORE-SCHEMATRON-E891C4DEC555F165"
EXPECTED_CANDIDATE_CONTENT_SHA256 = (
    "04aeb46e7eeaa854cf9554005a11476334fa8f41f6db9a45ca2f0e38b8d6d0e6"
)
EXPECTED_REQUIREMENT_SHA256 = (
    "d7daf659d3b7ad1388c42203d845b452afe12e8e05134d35d36a26cb9cc5e60c"
)
EXPECTED_OCCURRENCE_SHA256 = (
    "cb57d9e386c6274b0aa0aedca3e2b4bab1dbaafb41ff2e66a884681485d6c84f"
)
EXPECTED_ADJUDICATION_SHA256 = (
    "d63a31f936262c9952a0f50afd076b8547bc5c26cbdfd5adf04464b5f2c3dcc2"
)
EXPECTED_INVENTORY_SHA256 = (
    "ea376cbaad5e8559b6789844be2bef06478e5b8ee69f7a3c557cfbc5bd474370"
)
EXPECTED_GENERATED_PROPOSAL_COUNT = 8
STALE_OPERATIONAL_TOKENS = (
    "FF6-EVENT-000033",
    "FF6-EVENT-000029",
    "315efa5f5f4420202b5254c86ccd8863a91c385f",
    "XLF-04-BATCH-005-PARTIAL-002_DISPOSITION_VERIFICATION_AND_OBLIGATION_COMPILATION",
    "packet_projection_changes_pending_commit: true",
    "local_only_required_for_resume: true",
    "Expected before work: both refs equal",
)
SHA256 = re.compile(r"^[0-9a-f]{64}$")
LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
ALLOWED_DIRTY_PREFIXES = (
    "plans/codex/handover/",
    "reports/skills-rff6/skill-transcripts/refresh-provider-neutral-handover-event-35",
    "reports/skills-rff6/skill-transcripts/refresh-provider-neutral-handover-replay-repair-001",
    "reports/skills-rff6/skill-transcripts/refresh-provider-neutral-handover-event-38",
    "reports/skills-rff6/skill-transcripts/refresh-provider-neutral-handover-event-39",
    "reports/skills-rff6/skill-transcripts/plan-control-handover-event-36",
)
ALLOWED_DIRTY_EXACT = {
    "plans/strategic/ff6/controller-state.yaml",
    "plans/strategic/ff6/events.jsonl",
    "taskcards/TC-FF6-UBL-TYPING-001.md",
    "taskcards/TC-FF6-HANDOVER-CLAUDE-001.md",
    "taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md",
    "reports/skills-rff6/skill-transcripts/plan-control-ubl-state-checkpoint-004.json",
    "reports/skills-rff6/skill-transcripts/refresh-provider-neutral-handover-event-35.json",
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


def _load_yaml_at_ref(path: Path, ref: str) -> dict[str, Any]:
    relative = path.relative_to(REPO_ROOT).as_posix()
    result = _git("show", f"{ref}:{relative}")
    if result.returncode != 0:
        raise ValidationFailure(f"cannot load {relative} from {ref}")
    value = yaml.safe_load(result.stdout.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValidationFailure(f"{relative} at {ref} is not a mapping")
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
    census: Mapping[str, Any],
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
        _expect(errors, f"{label} event sequence", sequence, EXPECTED_SEQUENCE)

    repository_views = (
        ("manifest", manifest.get("source_checkpoint", {}).get("checkpoint_commit")),
        (
            "checkpoint",
            checkpoint.get("source_checkpoint", {}).get("repository_checkpoint"),
        ),
        ("machine", machine.get("repository", {}).get("checkpoint_commit")),
    )
    for label, value in repository_views:
        _expect(errors, f"{label} repository checkpoint", value, EXPECTED_CONTROL)

    _expect(errors, "latest event id", latest.get("event_id"), EXPECTED_EVENT_ID)
    _expect(errors, "latest event hash", latest.get("event_hash"), EXPECTED_EVENT_HASH)
    _expect(errors, "latest state", latest.get("state_after"), "CONTRACT")
    _expect(errors, "latest task", latest.get("task_id"), EXPECTED_EVENT_TASK)
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
    _expect(
        errors,
        "controller sequence",
        controller.get("transition_sequence"),
        EXPECTED_SEQUENCE,
    )
    _expect(errors, "controller state", controller.get("controller_state"), "CONTRACT")

    _expect(
        errors,
        "machine microstep",
        machine.get("controller", {}).get("exact_microstep"),
        EXPECTED_RESUME_MICROSTEP,
    )
    _expect(
        errors,
        "next microstep",
        next_step.get("task", {}).get("microstep"),
        EXPECTED_RESUME_MICROSTEP,
    )
    _expect(
        errors,
        "machine semantic checkpoint",
        machine.get("repository", {}).get("semantic_commit"),
        EXPECTED_IMPLEMENTATION,
    )
    _expect(
        errors,
        "checkpoint semantic checkpoint",
        checkpoint.get("source_checkpoint", {}).get("semantic_commit"),
        EXPECTED_IMPLEMENTATION,
    )
    _expect(
        errors,
        "recovery non-promoting attempt",
        recovery.get("accepted_history", {})
        .get("source_language_semantics", {})
        .get("commit"),
        "3fc939ad70ec6caac9e0699041076e02de00c5d2",
    )
    _expect(
        errors,
        "machine repair commit",
        machine.get("repository", {}).get("verified_checkout_identity_repair"),
        EXPECTED_REPAIR_COMMIT,
    )
    _expect(
        errors,
        "checkpoint repair commit",
        checkpoint.get("source_checkpoint", {}).get(
            "verified_checkout_identity_repair"
        ),
        EXPECTED_REPAIR_COMMIT,
    )
    _expect(
        errors,
        "recovery repair commit",
        recovery.get("accepted_history", {})
        .get("checkout_identity_repair", {})
        .get("commit"),
        EXPECTED_REPAIR_COMMIT,
    )
    _expect(
        errors,
        "next candidate",
        next_step.get("selected_candidate", {}).get("candidate_id"),
        EXPECTED_CANDIDATE,
    )
    _expect(
        errors,
        "next candidate content digest",
        next_step.get("selected_candidate", {}).get("candidate_content_sha256"),
        EXPECTED_CANDIDATE_CONTENT_SHA256,
    )
    _expect(
        errors,
        "next candidate requirement digest",
        next_step.get("selected_candidate", {}).get("requirement_sha256"),
        EXPECTED_REQUIREMENT_SHA256,
    )
    _expect(
        errors,
        "next candidate occurrence digest",
        next_step.get("selected_candidate", {}).get("occurrence_sha256"),
        EXPECTED_OCCURRENCE_SHA256,
    )
    machine_candidate = machine.get("xliff", {}).get("pending_candidate", {})
    _expect(
        errors,
        "machine candidate content digest",
        machine_candidate.get("candidate_content_sha256"),
        EXPECTED_CANDIDATE_CONTENT_SHA256,
    )
    _expect(
        errors,
        "machine candidate requirement digest",
        machine_candidate.get("requirement_sha256"),
        EXPECTED_REQUIREMENT_SHA256,
    )
    _expect(
        errors,
        "machine candidate occurrence digest",
        machine_candidate.get("occurrence_sha256"),
        EXPECTED_OCCURRENCE_SHA256,
    )

    decision_lock = next_step.get("decision_lock", {})
    _expect(
        errors,
        "next candidate remains unadjudicated",
        decision_lock.get("adjudicated"),
        False,
    )
    _expect(
        errors,
        "next candidate has no preselected owner",
        decision_lock.get("accepted_obligation"),
        None,
    )
    _expect(
        errors,
        "generated proposal count",
        len(next_step.get("generated_proposals_only", [])),
        EXPECTED_GENERATED_PROPOSAL_COUNT,
    )

    candidates = [
        row
        for row in census.get("candidates", [])
        if isinstance(row, Mapping) and row.get("candidate_id") == EXPECTED_CANDIDATE
    ]
    _expect(errors, "candidate census match count", len(candidates), 1)
    if len(candidates) == 1:
        candidate = candidates[0]
        _expect(
            errors,
            "census candidate content digest",
            candidate.get("candidate_content_sha256"),
            EXPECTED_CANDIDATE_CONTENT_SHA256,
        )
        occurrences = candidate.get("occurrences", [])
        _expect(errors, "census candidate occurrence count", len(occurrences), 1)
        if len(occurrences) == 1 and isinstance(occurrences[0], Mapping):
            occurrence = occurrences[0]
            _expect(
                errors,
                "census requirement digest",
                occurrence.get("requirement_sha256"),
                EXPECTED_REQUIREMENT_SHA256,
            )
            _expect(
                errors,
                "census occurrence digest",
                occurrence.get("occurrence_sha256"),
                EXPECTED_OCCURRENCE_SHA256,
            )
    xliff = machine.get("xliff", {})
    baseline = next_step.get("accepted_baseline", {})
    event_evidence = latest.get("evidence", {})
    _expect(
        errors,
        "machine accepted dispositions",
        xliff.get("adjudication", {}).get("production_accepted_dispositions"),
        8,
    )
    _expect(
        errors,
        "machine open dispositions",
        xliff.get("adjudication", {}).get("production_open_dispositions"),
        1122,
    )
    _expect(errors, "plan verified dispositions", baseline.get("dispositions_verified"), 8)
    _expect(errors, "plan open dispositions", baseline.get("dispositions_unverified"), 1122)
    _expect(
        errors,
        "event accepted dispositions",
        event_evidence.get("candidate_dispositions_verified"),
        8,
    )

    inventory_view = xliff.get("obligation_inventory", {})
    _expect(errors, "machine expected obligations", inventory_view.get("expected"), 105)
    _expect(
        errors,
        "machine accepted source-bound obligations",
        inventory_view.get("production_accepted_source_bound"),
        30,
    )
    _expect(
        errors,
        "machine accepted missing obligations",
        inventory_view.get("production_accepted_missing"),
        75,
    )
    _expect(errors, "machine XLF complete", inventory_view.get("complete"), False)
    _expect(errors, "inventory expected", inventory.get("expected_obligation_count"), 105)
    _expect(errors, "inventory resolved", inventory.get("resolved_expected_obligation_count"), 30)
    _expect(
        errors,
        "inventory missing",
        len(inventory.get("missing_expected_obligation_ids", [])),
        75,
    )
    _expect(errors, "inventory complete", inventory.get("complete"), False)
    _expect(errors, "adjudication candidate count", adjudication.get("candidate_count"), 1130)
    _expect(errors, "adjudication verified", adjudication.get("verified_disposition_count"), 8)
    _expect(errors, "adjudication unverified", adjudication.get("unverified_disposition_count"), 1122)
    _expect(errors, "adjudication complete", adjudication.get("disposition_verification_complete"), False)
    materialized = next_step.get("accepted_baseline", {})
    _expect(errors, "accepted verified", materialized.get("dispositions_verified"), 8)
    _expect(errors, "accepted open", materialized.get("dispositions_unverified"), 1122)
    _expect(
        errors,
        "accepted adjudication digest",
        materialized.get("adjudication_sha256"),
        EXPECTED_ADJUDICATION_SHA256,
    )
    _expect(
        errors,
        "accepted inventory digest",
        materialized.get("inventory_sha256"),
        EXPECTED_INVENTORY_SHA256,
    )

    _expect(
        errors,
        "recovery product overlay",
        recovery.get("captured_workspace", {}).get("product_overlay_status"),
        "NO_UNCOMMITTED_XLIFF_OVERLAY",
    )
    _expect(
        errors,
        "recovery local dependency",
        recovery.get("captured_workspace", {}).get("local_only_required_for_resume"),
        False,
    )
    _expect(
        errors,
        "UBL particle nodes",
        machine.get("ubl", {}).get("local_particle_nodes"),
        6001,
    )
    _expect(
        errors,
        "UBL particle owners",
        machine.get("ubl", {}).get("local_particle_owners"),
        468,
    )
    _expect(
        errors,
        "UBL particle identity",
        machine.get("ubl", {}).get("particle_graph_sha256"),
        "49b0c1ba5c75df0562ab6334fb14f8fe6dc4a9db31ff8e2b130d3bf04cf8eae1",
    )
    _expect(
        errors,
        "UBL anonymous type nodes",
        machine.get("ubl", {}).get("anonymous_type_nodes"),
        0,
    )
    _expect(
        errors,
        "UBL anonymous type edges",
        machine.get("ubl", {}).get("anonymous_type_edges"),
        0,
    )
    _expect(
        errors,
        "UBL anonymous type identity",
        machine.get("ubl", {}).get("anonymous_type_graph_sha256"),
        "666634cb0d90f17b05e0b9fd4babe13fe5087f253ef2afb276bf6066d82eaf6e",
    )
    _expect(
        errors,
        "UBL derivation edges",
        machine.get("ubl", {}).get("derivation_edges"),
        1178,
    )
    _expect(
        errors,
        "UBL derivation identity",
        machine.get("ubl", {}).get("derivation_graph_sha256"),
        "783506c4dcccaefbeb94960dcb5e6d7e0c54a6d8487ee1746eca082535b60e9f",
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


def _manifest_errors(
    manifest: Mapping[str, Any],
    *,
    recovery: Mapping[str, Any],
) -> list[str]:
    errors: list[str] = []
    files = manifest.get("files")
    if not isinstance(files, list):
        return ["manifest files is not a list"]
    seen: set[str] = set()
    occurrence_paths = {
        row.get("path")
        for row in recovery.get("captured_workspace", {}).get(
            "occurrence_paths",
            [],
        )
        if isinstance(row, Mapping) and isinstance(row.get("path"), str)
    }
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
        if relative in occurrence_paths:
            result = _git("show", f"{EXPECTED_IMPLEMENTATION}:{relative}")
            if result.returncode != 0:
                errors.append(f"manifest canonical blob missing: {relative}")
                continue
            data = result.stdout.replace(b"\r\n", b"\n")
        else:
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
    for relative in (*OPERATIONAL_DOC_PATHS, *REFERENCE_DOC_PATHS, PARALLEL_UBL_PATH):
        if relative not in seen:
            errors.append(f"current handover artifact absent from manifest: {relative}")
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
    for value in (
        EXPECTED_XLIFF_EVENT_ID,
        EXPECTED_MICROSTEP,
        EXPECTED_CANDIDATE,
    ):
        if value not in text:
            errors.append(f"active taskcard omits {value}")
    return errors


def _operational_documents() -> dict[str, str]:
    return {
        relative: (REPO_ROOT / relative).read_text(encoding="utf-8")
        for relative in (*OPERATIONAL_DOC_PATHS, *REFERENCE_DOC_PATHS)
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
        "plans/codex/handover/START-HERE.md": (
            EXPECTED_EVENT_ID,
            EXPECTED_CONTROL,
            EXPECTED_IMPLEMENTATION,
            EXPECTED_XLIFF_IMPLEMENTATION,
            EXPECTED_RESUME_MICROSTEP,
        ),
        "plans/codex/handover/CLAUDE-START.md": (
            EXPECTED_EVENT_ID,
            EXPECTED_CONTROL,
            EXPECTED_IMPLEMENTATION,
            EXPECTED_XLIFF_IMPLEMENTATION,
            EXPECTED_RESUME_MICROSTEP,
        ),
        "plans/codex/handover/CLEAN-REPLAY-REPAIR.md": (
            EXPECTED_EVENT_ID,
            EXPECTED_IMPLEMENTATION,
            EXPECTED_PREVIOUS_NON_PROMOTING_ATTEMPT,
            EXPECTED_RESUME_MICROSTEP,
        ),
        "plans/codex/handover/ACTIVE-WORK-CHECKPOINT.md": (
            EXPECTED_EVENT_ID,
            EXPECTED_RESUME_MICROSTEP,
        ),
        "plans/codex/handover/CURRENT-SHIFT-HANDOVER.md": (
            EXPECTED_EVENT_ID,
            EXPECTED_RESUME_MICROSTEP,
        ),
        "plans/codex/handover/CURRENT-MACHINE-STATE.yaml": (
            EXPECTED_EVENT_ID,
            EXPECTED_RESUME_MICROSTEP,
        ),
        "plans/codex/handover/checkpoint.yaml": (
            EXPECTED_EVENT_ID,
            EXPECTED_RESUME_MICROSTEP,
        ),
        "plans/codex/handover/INFLIGHT-RECOVERY.yaml": (
            EXPECTED_EVENT_ID,
            EXPECTED_IMPLEMENTATION,
            EXPECTED_XLIFF_IMPLEMENTATION,
        ),
        "plans/codex/handover/NEXT-MICROSTEP.yaml": (
            EXPECTED_EVENT_ID,
            EXPECTED_RESUME_MICROSTEP,
            EXPECTED_CANDIDATE,
        ),
    }
    for relative, markers in required_markers.items():
        text = documents.get(relative, "")
        for marker in markers:
            if marker not in text:
                errors.append(f"current marker missing from {relative}: {marker}")
    for relative in REFERENCE_DOC_PATHS:
        text = documents.get(relative, "")
        for marker in (
            "Current authority overlay: Event 39",
            EXPECTED_EVENT_ID,
            "30/105",
            "8/1,130",
            "6,001",
        ):
            if marker not in text:
                errors.append(f"Event 39 overlay marker missing from {relative}: {marker}")
    return errors


def _git_errors(
    *,
    require_clean: bool,
    recovery: Mapping[str, Any],
) -> list[str]:
    errors: list[str] = []
    control = _git(
        "merge-base",
        "--is-ancestor",
        EXPECTED_CONTROL,
        "origin/main",
    )
    if control.returncode != 0:
        errors.append("verified handover checkpoint is not an ancestor of origin/main")
    ancestor = _git(
        "merge-base",
        "--is-ancestor",
        EXPECTED_IMPLEMENTATION,
        "origin/main",
    )
    if ancestor.returncode != 0:
        errors.append("implementation commit is not an ancestor of origin/main")
    xliff_ancestor = _git(
        "merge-base",
        "--is-ancestor",
        EXPECTED_XLIFF_IMPLEMENTATION,
        "origin/main",
    )
    if xliff_ancestor.returncode != 0:
        errors.append("accepted XLIFF implementation is not an ancestor of origin/main")
    remote = _git("remote", "get-url", "origin")
    if remote.returncode != 0 or b"gitlab" not in remote.stdout.lower():
        errors.append("origin is not the GitLab remote")
    status = _git("status", "--porcelain=v1")
    if status.returncode != 0:
        errors.append("git status failed")
        return errors
    dirty: list[str] = []
    occurrences = {
        row.get("path"): row
        for row in recovery.get("captured_workspace", {}).get(
            "occurrence_paths",
            [],
        )
        if isinstance(row, Mapping) and isinstance(row.get("path"), str)
    }
    current_foreign = recovery.get("captured_workspace", {}).get(
        "current_foreign_work",
        {},
    )
    foreign_paths = {
        current_foreign.get("observed_path")
    } if isinstance(current_foreign, Mapping) else set()
    foreign_paths.discard(None)
    for raw in status.stdout.decode("utf-8", errors="replace").splitlines():
        path = raw[3:].replace("\\", "/")
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        dirty.append(path)
        occurrence = occurrences.get(path)
        if occurrence is not None:
            actual = _sha256(REPO_ROOT / path)
            expected = occurrence.get("occurrence_sha256")
            if actual != expected:
                errors.append(
                    f"preserved occurrence digest mismatch: {path}: "
                    f"expected {expected}, got {actual}"
                )
        elif path in foreign_paths:
            # The shared-worktree validation may observe an explicitly
            # recorded foreign live path. It is never included in packet
            # evidence, and --require-clean still rejects the transfer.
            continue
        elif not (
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
        (
            "false pre-RED adjudication",
            ("next", "decision_lock", "adjudicated"),
            True,
        ),
        (
            "preselected candidate owner",
            ("next", "decision_lock", "accepted_obligation"),
            "SAL-XLIFF-CORE-DOCUMENT-TARGET-LANGUAGE-001",
        ),
        (
            "truncated proposal accountability",
            ("next", "generated_proposals_only"),
            [],
        ),
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
            census=mutated["census"],
            adjudication=mutated["adjudication"],
            inventory=mutated["inventory"],
        )
        if not found:
            errors.append(f"negative control was not rejected: {label}")
    mutated_documents = copy.deepcopy(base["documents"])
    provider_contract = "plans/codex/handover/START-HERE.md"
    mutated_documents[provider_contract] += "\nFF6-EVENT-000029\n"
    if not _operational_doc_errors(mutated_documents):
        errors.append("negative control was not rejected: stale operational event")
    mutated = copy.deepcopy(base)
    mutated["next"]["selected_candidate"]["candidate_content_sha256"] = (
        EXPECTED_REQUIREMENT_SHA256
    )
    if not _semantic_errors(
        manifest=mutated["manifest"],
        checkpoint=mutated["checkpoint"],
        machine=mutated["machine"],
        recovery=mutated["recovery"],
        next_step=mutated["next"],
        controller=mutated["controller"],
        latest=mutated["latest"],
        census=mutated["census"],
        adjudication=mutated["adjudication"],
        inventory=mutated["inventory"],
    ):
        errors.append("negative control was not rejected: digest role substitution")
    return errors


def validate(*, require_clean: bool = False) -> dict[str, Any]:
    manifest = _load_yaml(MANIFEST_PATH)
    checkpoint = _load_yaml(CHECKPOINT_PATH)
    machine = _load_yaml(MACHINE_PATH)
    recovery = _load_yaml(RECOVERY_PATH)
    next_step = _load_yaml(NEXT_PATH)
    controller = _load_yaml(CONTROLLER_PATH)
    census = _load_yaml(CENSUS_PATH)
    adjudication = _load_yaml_at_ref(
        ADJUDICATION_PATH,
        EXPECTED_CONTROL,
    )
    inventory = _load_yaml_at_ref(
        INVENTORY_PATH,
        EXPECTED_CONTROL,
    )
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
        "census": census,
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
            census=census,
            adjudication=adjudication,
            inventory=inventory,
        ),
        *_manifest_errors(manifest, recovery=recovery),
        *_manifest_parse_errors(manifest),
        *_link_errors(manifest),
        *_task_errors(),
        *_operational_doc_errors(documents),
        *_git_errors(require_clean=require_clean, recovery=recovery),
        *_negative_control_errors(base),
    ]
    return {
        "result": "PASS" if not errors else "FAIL",
        "event_id": latest.get("event_id"),
        "event_hash": latest.get("event_hash"),
        "implementation_commit": EXPECTED_IMPLEMENTATION,
        "next_microstep": EXPECTED_RESUME_MICROSTEP,
        "next_candidate": EXPECTED_CANDIDATE,
        "manifest_files": len(manifest.get("files", [])),
        "semantic_negative_controls": 11,
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
