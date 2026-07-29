"""Fail-closed validator for the provider-neutral FF6 handover.

generated_by: codex
visibility: internal

The packet is a derived projection. This validator binds it to the native FF6
journal, controller, task registry, GitLab ancestry, and LF-normalized bytes.
It is read-only and never repairs state.
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
MACHINE_STATE_PATH = HANDOVER_ROOT / "CURRENT-MACHINE-STATE.yaml"
VERSIONED_CHECKPOINT_PATH = HANDOVER_ROOT / "event-26/CHECKPOINT.yaml"
VERSIONED_MANIFEST_PATH = HANDOVER_ROOT / "event-26/manifest.yaml"
CONTROLLER_PATH = REPO_ROOT / "plans/strategic/ff6/controller-state.yaml"
JOURNAL_PATH = REPO_ROOT / "plans/strategic/ff6/events.jsonl"
TASK_INDEX_PATH = REPO_ROOT / "taskcards/index.yaml"
ACTIVE_TASK_PATH = REPO_ROOT / "taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md"

BATCH_PATTERN = re.compile(r"\bXLF-04-BATCH-\d{3}\b")
LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
CURRENT_TEXT_PATHS = (
    "plans/codex/handover/START-HERE.md",
    "plans/codex/handover/CLAUDE-START.md",
    "plans/codex/handover/ACTIVE-WORK-CHECKPOINT.md",
)
ALLOWED_CHANGED_PATHS = {
    "taskcards/TC-FF6-HANDOVER-CLAUDE-001.md",
}
ALLOWED_CHANGED_PREFIX = "plans/codex/handover/"


class ValidationFailure(RuntimeError):
    """Raised when a packet cannot be parsed as a governed projection."""


def _run_git(*args: str) -> subprocess.CompletedProcess[bytes]:
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


def _tracked_lf_bytes(relative: str) -> bytes:
    """Use the staged snapshot first, then HEAD, then the worktree."""
    for spec in (f":{relative}", f"HEAD:{relative}"):
        result = _run_git("show", spec)
        if result.returncode == 0:
            return result.stdout.replace(b"\r\n", b"\n")
    return _lf_bytes(REPO_ROOT / relative)


def _tracked_sha256(relative: str) -> str:
    return hashlib.sha256(_tracked_lf_bytes(relative)).hexdigest()


def _canonical_event_hash(event: Mapping[str, Any]) -> str:
    payload = dict(event)
    payload.pop("event_hash", None)
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _load_events() -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        JOURNAL_PATH.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValidationFailure(f"journal line {line_number} is not an object")
        events.append(value)
    if not events:
        raise ValidationFailure("native FF6 journal is empty")
    return events


def _event_chain_errors(events: Sequence[Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    previous_hash: str | None = None
    for expected_sequence, event in enumerate(events, start=1):
        sequence = event.get("sequence")
        if sequence != expected_sequence:
            errors.append(
                f"event sequence mismatch: expected {expected_sequence}, got {sequence}"
            )
        actual_hash = event.get("event_hash")
        computed_hash = _canonical_event_hash(event)
        if actual_hash != computed_hash:
            errors.append(
                f"event {sequence} hash mismatch: expected {actual_hash}, "
                f"computed {computed_hash}"
            )
        if expected_sequence > 1 and event.get("previous_event_hash") != previous_hash:
            errors.append(
                f"event {sequence} does not bind event {expected_sequence - 1}"
            )
        previous_hash = str(actual_hash)
    return errors


def _projection(latest: Mapping[str, Any]) -> dict[str, Any]:
    evidence = latest.get("evidence")
    if not isinstance(evidence, Mapping):
        raise ValidationFailure("latest event evidence is not a mapping")
    task_steps = evidence.get("completed_task_steps")
    batches = evidence.get("completed_xlf_04_batches")
    if not isinstance(task_steps, list) or not isinstance(batches, list):
        raise ValidationFailure("latest event completed steps are not lists")
    next_batches = sorted(
        set(BATCH_PATTERN.findall(str(latest.get("exact_next_action", ""))))
    )
    if len(next_batches) != 1:
        raise ValidationFailure(
            f"latest event must select exactly one next XLF-04 batch: {next_batches}"
        )
    return {
        "sequence": latest.get("sequence"),
        "event_id": latest.get("event_id"),
        "event_hash": latest.get("event_hash"),
        "state": latest.get("state_after"),
        "task": latest.get("next_task"),
        "task_state": latest.get("next_task_state"),
        "parent": latest.get("parent_task"),
        "parent_state": latest.get("parent_task_state"),
        "completed_task_steps": task_steps,
        "completed_batches": batches,
        "completed_steps": [*task_steps, *batches],
        "first_unmet": evidence.get("first_unmet_task_step"),
        "next_batch": next_batches[0],
        "next_action": latest.get("exact_next_action"),
        "obligations": evidence.get("batch_obligations"),
        "expected": evidence.get("expected_obligation_ids"),
        "resolved": evidence.get("resolved_expected_obligation_ids"),
        "missing": evidence.get("missing_expected_obligation_ids"),
        "candidate_count": evidence.get("candidate_count"),
        "coarse": evidence.get("candidate_coarse_structural_dispositions"),
        "non_modal_complete": evidence.get(
            "non_modal_prose_classification_complete"
        ),
    }


def _expect(
    errors: list[str], label: str, actual: Any, expected: Any
) -> None:
    if actual != expected:
        errors.append(f"{label}: expected {expected!r}, got {actual!r}")


def _manifest_errors(manifest: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    files = manifest.get("files")
    if not isinstance(files, list):
        return ["manifest.files is not a list"]
    seen: set[str] = set()
    for entry in files:
        if not isinstance(entry, Mapping):
            errors.append("manifest file entry is not a mapping")
            continue
        relative = entry.get("path")
        expected = entry.get("sha256")
        if not isinstance(relative, str) or not isinstance(expected, str):
            errors.append("manifest entry lacks path or sha256")
            continue
        if relative in seen:
            errors.append(f"duplicate manifest path: {relative}")
        seen.add(relative)
        path = REPO_ROOT / relative
        if not path.is_file():
            errors.append(f"manifest path missing: {relative}")
            continue
        actual = _tracked_sha256(relative)
        if actual != expected:
            errors.append(
                f"manifest digest mismatch for {relative}: "
                f"expected {expected}, got {actual}"
            )
        try:
            if path.suffix.lower() in {".yaml", ".yml"}:
                yaml.safe_load(path.read_text(encoding="utf-8"))
            elif path.suffix.lower() == ".json":
                json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, yaml.YAMLError) as exc:
            errors.append(f"parse failure for {relative}: {exc}")
    if "plans/codex/handover/manifest.yaml" in seen:
        errors.append("root manifest must exclude its own digest")
    required = {
        "plans/codex/handover/START-HERE.md",
        "plans/codex/handover/validate_handover.py",
        "plans/codex/handover/event-26/manifest.yaml",
        "plans/strategic/ff6/controller-state.yaml",
        "plans/strategic/ff6/events.jsonl",
        "taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md",
    }
    for path in sorted(required - seen):
        errors.append(f"required manifest binding absent: {path}")
    return errors


def _versioned_manifest_errors(manifest: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    files = manifest.get("files")
    if not isinstance(files, list):
        return ["event-26 manifest.files is not a list"]
    seen: set[str] = set()
    for entry in files:
        if not isinstance(entry, Mapping):
            errors.append("event-26 manifest entry is not a mapping")
            continue
        relative = entry.get("path")
        expected = entry.get("lf_sha256")
        if not isinstance(relative, str) or not isinstance(expected, str):
            errors.append("event-26 entry lacks path or lf_sha256")
            continue
        if relative in seen:
            errors.append(f"duplicate event-26 manifest path: {relative}")
        seen.add(relative)
        repo_relative = f"plans/codex/handover/event-26/{relative}"
        path = REPO_ROOT / repo_relative
        if not path.is_file():
            errors.append(f"event-26 path missing: {relative}")
            continue
        actual = _tracked_sha256(repo_relative)
        if actual != expected:
            errors.append(
                f"event-26 digest mismatch for {relative}: "
                f"expected {expected}, got {actual}"
            )
    if "manifest.yaml" in seen:
        errors.append("event-26 manifest must exclude itself")
    if seen != {"START-HERE.md", "CHECKPOINT.yaml", "RUNBOOK.md", "receipt.json"}:
        errors.append(f"unexpected event-26 file set: {sorted(seen)}")
    return errors


def _link_errors(manifest: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for entry in manifest.get("files", []):
        relative = entry.get("path") if isinstance(entry, Mapping) else None
        if not isinstance(relative, str) or not relative.lower().endswith(".md"):
            continue
        source = REPO_ROOT / relative
        if not source.is_file():
            continue
        for target in LINK_PATTERN.findall(source.read_text(encoding="utf-8")):
            target = target.strip().strip("<>")
            if not target or target.startswith(
                ("#", "http://", "https://", "mailto:")
            ):
                continue
            target_path = target.split("#", 1)[0]
            if not target_path:
                continue
            resolved = (source.parent / target_path).resolve()
            try:
                resolved.relative_to(REPO_ROOT)
            except ValueError:
                errors.append(f"{relative} link escapes repository: {target}")
                continue
            if not resolved.exists():
                errors.append(f"{relative} has broken local link: {target}")
    return errors


def _git_errors(manifest: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    source = manifest.get("source_checkpoint")
    if not isinstance(source, Mapping):
        return ["manifest source_checkpoint is not a mapping"]
    ancestor = source.get("required_ancestor")
    remote_ref = source.get("required_remote_ref")
    if not isinstance(ancestor, str) or not isinstance(remote_ref, str):
        return ["manifest lacks required ancestor or remote ref"]
    for older, newer, label in (
        (ancestor, remote_ref, "source checkpoint"),
        ("HEAD", remote_ref, "current HEAD"),
    ):
        result = _run_git("merge-base", "--is-ancestor", older, newer)
        if result.returncode != 0:
            errors.append(f"{label} {older} is not an ancestor of {newer}")
    if (
        source.get("forge"),
        source.get("remote"),
        source.get("branch"),
    ) != ("GitLab", "origin", "main"):
        errors.append("handover source is not GitLab origin/main")
    remote_url = _run_git("remote", "get-url", "origin")
    if remote_url.returncode != 0 or b"gitlab" not in remote_url.stdout.lower():
        errors.append("origin does not resolve to a GitLab URL")
    return errors


def _staged_path_errors() -> list[str]:
    """Prove the packet commit scope without rejecting classified concurrent dirt."""
    errors: list[str] = []
    result = _run_git("diff", "--cached", "--name-only")
    if result.returncode != 0:
        return ["cannot inspect staged handover paths"]
    staged = {
        line.strip().replace("\\", "/")
        for line in result.stdout.decode("utf-8").splitlines()
        if line.strip()
    }
    for path in sorted(staged):
        if path in ALLOWED_CHANGED_PATHS or path.startswith(ALLOWED_CHANGED_PREFIX):
            continue
        errors.append(f"handover index contains out-of-scope change: {path}")
    return errors


def _task_registered(value: Any, task_id: str) -> bool:
    if isinstance(value, Mapping):
        if value.get("id") == task_id:
            return str(value.get("status", "")).lower() == "work_in_progress"
        return any(_task_registered(item, task_id) for item in value.values())
    if isinstance(value, list):
        return any(_task_registered(item, task_id) for item in value)
    return False


def _semantic_errors(
    *,
    manifest: Mapping[str, Any],
    checkpoint: Mapping[str, Any],
    machine: Mapping[str, Any],
    versioned: Mapping[str, Any],
    controller: Mapping[str, Any],
    task_index: Mapping[str, Any],
    latest: Mapping[str, Any],
    texts: Mapping[str, str],
) -> list[str]:
    errors: list[str] = []
    p = _projection(latest)
    controller_event = controller.get("last_verified_event", {})
    controller_active = controller.get("active_task", {})
    controller_xlf = controller.get("xlf_checkpoint", {})
    manifest_controller = manifest.get("controller", {})
    checkpoint_controller = checkpoint.get("controller_checkpoint", {})
    checkpoint_xlf = checkpoint.get("current_xliff_compiler_checkpoint", {})
    machine_controller = machine.get("controller", {})
    machine_next = machine.get("next_task_prerequisite", {})
    versioned_controller = versioned.get("controller", {})
    versioned_next = versioned.get("exact_next", {})

    _expect(errors, "controller sequence", controller.get("transition_sequence"), p["sequence"])
    _expect(errors, "controller event id", controller_event.get("event_id"), p["event_id"])
    _expect(errors, "controller event hash", controller_event.get("event_hash"), p["event_hash"])
    _expect(errors, "controller state", controller.get("controller_state"), p["state"])
    _expect(errors, "controller task", controller_active.get("task_id"), p["task"])
    _expect(errors, "controller task state", controller_active.get("state"), p["task_state"])
    _expect(
        errors,
        "controller completed steps",
        [
            *controller_active.get("completed_steps", []),
            *controller_xlf.get("completed_xlf_04_batches", []),
        ],
        p["completed_steps"],
    )

    for label, current, sequence_key, hash_key, task_key, state_key in (
        (
            "manifest",
            manifest_controller,
            "event_sequence",
            "event_hash",
            "exact_next_task",
            "exact_next_state",
        ),
        (
            "checkpoint",
            checkpoint_controller,
            "event_sequence",
            "event_head",
            "exact_next_task",
            "exact_next_state",
        ),
        (
            "machine",
            machine_controller,
            "transition_sequence",
            "event_hash",
            "next_task",
            "next_task_state",
        ),
        (
            "versioned",
            versioned_controller,
            "sequence",
            "event_hash",
            "active_task",
            "active_task_state",
        ),
    ):
        _expect(errors, f"{label} sequence", current.get(sequence_key), p["sequence"])
        _expect(errors, f"{label} event hash", current.get(hash_key), p["event_hash"])
        _expect(errors, f"{label} task", current.get(task_key), p["task"])
        _expect(errors, f"{label} task state", current.get(state_key), p["task_state"])

    _expect(
        errors,
        "manifest completed steps",
        manifest_controller.get("completed_steps"),
        p["completed_steps"],
    )
    _expect(
        errors,
        "checkpoint completed batches",
        checkpoint_xlf.get("completed_xlf_04_batches"),
        p["completed_batches"],
    )
    _expect(
        errors,
        "checkpoint all completed steps",
        checkpoint.get("xliff_starting_defects", {}).get("completed_steps"),
        p["completed_steps"],
    )
    _expect(
        errors,
        "machine completed steps",
        machine_next.get("completed_steps"),
        p["completed_steps"],
    )

    latest_key = p["completed_batches"][-1].lower().replace("-", "_")
    machine_batch = machine_next.get(latest_key, {})
    for label, current in (
        ("checkpoint XLF-04", checkpoint_xlf),
        ("machine latest batch", machine_batch),
    ):
        _expect(
            errors,
            f"{label} obligations",
            current.get("core_obligation_count", current.get("obligation_count")),
            p["obligations"],
        )
        _expect(
            errors,
            f"{label} expected",
            current.get(
                "core_expected_obligation_count",
                current.get("expected_obligation_count"),
            ),
            p["expected"],
        )
        _expect(
            errors,
            f"{label} resolved",
            current.get(
                "core_resolved_expected_obligation_count",
                current.get("resolved_expected_obligation_count"),
            ),
            p["resolved"],
        )
        _expect(
            errors,
            f"{label} missing",
            current.get(
                "core_missing_expected_obligation_count",
                current.get("missing_expected_obligation_count"),
            ),
            p["missing"],
        )

    actions = {
        "manifest": manifest_controller.get("exact_next_action"),
        "checkpoint": checkpoint_xlf.get("exact_next_action"),
        "machine": machine_next.get("exact_next_action"),
        "versioned": versioned_next.get("microstep"),
    }
    for label, action in actions.items():
        matches = sorted(set(BATCH_PATTERN.findall(str(action))))
        if matches != [p["next_batch"]]:
            errors.append(
                f"{label} exact next batch: expected {p['next_batch']}, got {matches}"
            )
    if p["next_batch"] in p["completed_batches"]:
        errors.append("latest event selects an already completed batch")

    _expect(errors, "machine candidate count", machine_batch.get("candidate_count"), p["candidate_count"])
    _expect(errors, "machine coarse dispositions", machine_batch.get("coarse_structural_dispositions"), p["coarse"])
    _expect(
        errors,
        "machine non-modal classification",
        machine_batch.get("non_modal_prose_classification_complete"),
        p["non_modal_complete"],
    )
    _expect(errors, "products certified", machine.get("goal", {}).get("products_certified"), 0)
    _expect(errors, "versioned products certified", versioned.get("program", {}).get("products_certified"), 0)

    transfer = machine.get("workspace_transfer", {})
    if machine.get("source_checkpoint", {}).get("worktree_at_capture") == (
        "CLASSIFIED_CONCURRENT_BATCH005_WORK_PRESENT"
    ):
        _expect(
            errors,
            "committed checkpoint transfer status",
            transfer.get("committed_checkpoint_status"),
            "RESUMABLE",
        )
        _expect(
            errors,
            "shared workspace transfer status",
            transfer.get("status"),
            "IN_FLIGHT_RED_NOT_TRANSFERABLE",
        )
        _expect(
            errors,
            "shared workspace clean checkpoint claim",
            transfer.get("current_bytes_are_clean_checkpoint"),
            False,
        )
        _expect(
            errors,
            "incoming Batch 005 claim authorization",
            transfer.get("incoming_provider_may_claim_batch005_now"),
            False,
        )
        _expect(
            errors,
            "unowned resume isolation",
            transfer.get("clean_checkout_required_for_unowned_resume"),
            True,
        )
        _expect(
            errors,
            "captured in-flight paths",
            sorted(transfer.get("untracked_paths", [])),
            sorted(
                [
                    "tools/spec/xliff_core_candidate_binding.py",
                    "tests/tools/test_extract_sal_facts_candidate_binding.py",
                ]
            ),
        )
        red_replay = transfer.get("focused_red_replay", {})
        _expect(errors, "captured RED passing tests", red_replay.get("passed"), 17)
        _expect(errors, "captured RED failing tests", red_replay.get("failed"), 10)

    if not _task_registered(task_index, str(p["task"])):
        errors.append(f"active task {p['task']} is not registered work_in_progress")
    task_text = ACTIVE_TASK_PATH.read_text(encoding="utf-8")
    if p["next_batch"] not in task_text:
        errors.append(f"active taskcard does not name {p['next_batch']}")

    required_truth = (
        p["next_batch"],
        "0/6",
        "80",
        "78",
    )
    for path in CURRENT_TEXT_PATHS:
        text = texts.get(path, "")
        for token in required_truth:
            if token not in text:
                errors.append(f"{path} lacks current truth token {token!r}")
        for completed in p["completed_batches"]:
            stale_phrase = f"exact next microstep: `{completed}`"
            if stale_phrase in text:
                errors.append(f"{path} treats completed {completed} as exact next")
    for path in (
        "plans/codex/handover/START-HERE.md",
        "plans/codex/handover/ACTIVE-WORK-CHECKPOINT.md",
        "plans/codex/handover/CLAUDE-START.md",
    ):
        if "IN_FLIGHT_RED_NOT_TRANSFERABLE" not in texts.get(path, ""):
            errors.append(f"{path} lacks explicit live-workspace transfer state")
    return errors


def _tracked_texts(manifest: Mapping[str, Any]) -> dict[str, str]:
    texts: dict[str, str] = {}
    for entry in manifest.get("files", []):
        relative = entry.get("path") if isinstance(entry, Mapping) else None
        if isinstance(relative, str):
            path = REPO_ROOT / relative
            if path.is_file() and path.suffix.lower() in {".md", ".yaml", ".yml"}:
                texts[relative] = path.read_text(encoding="utf-8")
    return texts


def validate_current() -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = _load_yaml(MANIFEST_PATH)
    checkpoint = _load_yaml(CHECKPOINT_PATH)
    machine = _load_yaml(MACHINE_STATE_PATH)
    versioned = _load_yaml(VERSIONED_CHECKPOINT_PATH)
    versioned_manifest = _load_yaml(VERSIONED_MANIFEST_PATH)
    controller = _load_yaml(CONTROLLER_PATH)
    task_index = _load_yaml(TASK_INDEX_PATH)
    events = _load_events()
    latest = events[-1]
    texts = _tracked_texts(manifest)
    errors = [
        *_event_chain_errors(events),
        *_manifest_errors(manifest),
        *_versioned_manifest_errors(versioned_manifest),
        *_link_errors(manifest),
        *_git_errors(manifest),
        *_staged_path_errors(),
        *_semantic_errors(
            manifest=manifest,
            checkpoint=checkpoint,
            machine=machine,
            versioned=versioned,
            controller=controller,
            task_index=task_index,
            latest=latest,
            texts=texts,
        ),
    ]
    result = {
        "schema": "ff6/handover-validation@2",
        "valid": not errors,
        "event_id": latest.get("event_id"),
        "event_sequence": latest.get("sequence"),
        "event_hash": latest.get("event_hash"),
        "next_batch": _projection(latest)["next_batch"],
        "manifest_files": len(manifest.get("files", [])),
        "errors": errors,
    }
    context = {
        "manifest": manifest,
        "checkpoint": checkpoint,
        "machine": machine,
        "versioned": versioned,
        "controller": controller,
        "task_index": task_index,
        "latest": latest,
        "texts": texts,
    }
    return result, context


def _semantic_only(context: Mapping[str, Any]) -> list[str]:
    return _semantic_errors(
        manifest=context["manifest"],
        checkpoint=context["checkpoint"],
        machine=context["machine"],
        versioned=context["versioned"],
        controller=context["controller"],
        task_index=context["task_index"],
        latest=context["latest"],
        texts=context["texts"],
    )


def run_self_test(context: Mapping[str, Any]) -> dict[str, Any]:
    cases: list[tuple[str, dict[str, Any]]] = []

    missing_batch = copy.deepcopy(context)
    missing_batch["checkpoint"]["xliff_starting_defects"]["completed_steps"].pop()
    cases.append(("missing_completed_batch", missing_batch))

    stale_next = copy.deepcopy(context)
    completed = _projection(context["latest"])["completed_batches"][-1]
    stale_next["manifest"]["controller"]["exact_next_action"] = completed
    cases.append(("completed_batch_reselected", stale_next))

    wrong_head = copy.deepcopy(context)
    wrong_head["machine"]["controller"]["event_hash"] = "0" * 64
    cases.append(("wrong_controller_head", wrong_head))

    false_certification = copy.deepcopy(context)
    false_certification["machine"]["goal"]["products_certified"] = 6
    cases.append(("false_product_certification", false_certification))

    false_workspace_transfer = copy.deepcopy(context)
    false_workspace_transfer["machine"]["workspace_transfer"]["status"] = "RESUMABLE"
    cases.append(("false_workspace_transferability", false_workspace_transfer))

    outcomes = [
        {"case": name, "rejected": bool(_semantic_only(case))}
        for name, case in cases
    ]
    return {
        "schema": "ff6/handover-validation-self-test@3",
        "valid": all(item["rejected"] for item in outcomes),
        "negative_controls": outcomes,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="also prove five semantic corruptions are rejected",
    )
    args = parser.parse_args(argv)
    try:
        result, context = validate_current()
        if args.self_test:
            result["self_test"] = run_self_test(context)
            result["valid"] = bool(result["valid"] and result["self_test"]["valid"])
    except (
        OSError,
        ValueError,
        TypeError,
        ValidationFailure,
        json.JSONDecodeError,
        yaml.YAMLError,
    ) as exc:
        result = {
            "schema": "ff6/handover-validation@2",
            "valid": False,
            "errors": [f"{type(exc).__name__}: {exc}"],
        }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
