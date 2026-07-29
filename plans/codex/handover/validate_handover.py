"""Fail-closed semantic validator for the provider-neutral FF6 handover.

generated_by: codex
visibility: internal

The manifest already protects bytes.  This validator additionally proves that
the derived packet still projects the latest native FF6 event and controller
semantics.  It is deliberately read-only and does not repair stale state.
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
CHECKPOINT_PATH = HANDOVER_ROOT / "event-26/CHECKPOINT.yaml"
MACHINE_STATE_PATH = CHECKPOINT_PATH
CONTROLLER_PATH = REPO_ROOT / "plans/strategic/ff6/controller-state.yaml"
JOURNAL_PATH = REPO_ROOT / "plans/strategic/ff6/events.jsonl"

EXPECTED_EVIDENCE_WORDING = (
    "six committed-file digests (four implementation/report files and two "
    "skill transcripts)"
)
STALE_ACTIVE_PATTERNS = {
    "plans/codex/handover/CLAUDE-START.md": ("batch-002 RED receipt",),
    "plans/codex/handover/ACTIVE-WORK-CHECKPOINT.md": (
        "Event 24 binds the current implementation",
        "current XLF-04 suite passes 24",
    ),
    "plans/codex/handover/VALIDATION-AND-RELEASE.md": (
        "current XLF-04 slice is bound to commit",
    ),
}
LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


class ValidationFailure(RuntimeError):
    """Raised when one or more handover invariants fail."""


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValidationFailure(f"{path.relative_to(REPO_ROOT)} is not a mapping")
    return value


def _lf_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n")


def _tracked_lf_bytes(relative: str) -> bytes:
    """Return committed bytes so concurrent classified writes cannot poison proof."""
    result = subprocess.run(
        ["git", "show", f"HEAD:{relative}"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode == 0:
        return result.stdout.replace(b"\r\n", b"\n")
    path = REPO_ROOT / relative
    return _lf_bytes(path)


def _tracked_lf_sha256(relative: str) -> str:
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
        raise ValidationFailure("native FF6 event journal is empty")
    return events


def _validate_event_chain(events: Sequence[Mapping[str, Any]]) -> list[str]:
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
                f"event {sequence} previous_event_hash does not bind event "
                f"{expected_sequence - 1}"
            )
        previous_hash = str(actual_hash)
    return errors


def _event_projection(latest_event: Mapping[str, Any]) -> dict[str, Any]:
    evidence = latest_event.get("evidence")
    if not isinstance(evidence, Mapping):
        raise ValidationFailure("latest event evidence is not a mapping")
    task_steps = evidence.get("completed_task_steps", [])
    batches = evidence.get("completed_xlf_04_batches", [])
    if not isinstance(task_steps, list) or not isinstance(batches, list):
        raise ValidationFailure("latest event completed-step fields are not lists")
    return {
        "sequence": latest_event.get("sequence"),
        "event_id": latest_event.get("event_id"),
        "event_hash": latest_event.get("event_hash"),
        "state": latest_event.get("state_after"),
        "parent_task": latest_event.get("parent_task"),
        "parent_state": latest_event.get("parent_task_state"),
        "next_task": latest_event.get("next_task"),
        "next_state": latest_event.get("next_task_state"),
        "completed_steps": [*task_steps, *batches],
        "first_unmet_step": evidence.get("first_unmet_task_step"),
        "next_action": latest_event.get("exact_next_action"),
        "obligations": evidence.get("batch_obligations"),
        "expected": evidence.get("expected_obligation_ids"),
        "resolved": evidence.get("resolved_expected_obligation_ids"),
        "missing": evidence.get("missing_expected_obligation_ids"),
    }


def _expect_equal(
    errors: list[str], label: str, actual: Any, expected: Any
) -> None:
    if actual != expected:
        errors.append(f"{label}: expected {expected!r}, got {actual!r}")


def _semantic_errors(
    *,
    manifest: Mapping[str, Any],
    checkpoint: Mapping[str, Any],
    machine: Mapping[str, Any],
    controller: Mapping[str, Any],
    latest_event: Mapping[str, Any],
    texts: Mapping[str, str],
) -> list[str]:
    errors: list[str] = []
    projection = _event_projection(latest_event)
    controller_event = controller.get("last_verified_event", {})
    controller_active = controller.get("active_task", {})
    controller_xlf = controller.get("xlf_checkpoint", {})
    manifest_controller = manifest.get("controller", {})
    checkpoint_controller = checkpoint.get("controller_checkpoint", {})
    checkpoint_xlf = checkpoint.get("current_xliff_compiler_checkpoint", {})
    checkpoint_defects = checkpoint.get("xliff_starting_defects", {})
    machine_controller = machine.get("controller", {})
    machine_next = machine.get("next_task_prerequisite", {})
    machine_xlf = machine_next.get("xlf_04_batch_003", {})

    _expect_equal(
        errors,
        "controller.transition_sequence",
        controller.get("transition_sequence"),
        projection["sequence"],
    )
    _expect_equal(
        errors,
        "controller.last_verified_event.event_id",
        controller_event.get("event_id"),
        projection["event_id"],
    )
    _expect_equal(
        errors,
        "controller.last_verified_event.event_hash",
        controller_event.get("event_hash"),
        projection["event_hash"],
    )
    _expect_equal(
        errors,
        "controller.controller_state",
        controller.get("controller_state"),
        projection["state"],
    )
    _expect_equal(
        errors,
        "controller.active_task.task_id",
        controller_active.get("task_id"),
        projection["next_task"],
    )
    _expect_equal(
        errors,
        "controller.active_task.state",
        controller_active.get("state"),
        projection["next_state"],
    )
    combined_controller_steps = [
        *controller_active.get("completed_steps", []),
        *controller_xlf.get("completed_xlf_04_batches", []),
    ]
    _expect_equal(
        errors,
        "controller combined completed steps",
        combined_controller_steps,
        projection["completed_steps"],
    )

    for label, current in (
        ("manifest.controller", manifest_controller),
        ("checkpoint.controller_checkpoint", checkpoint_controller),
        ("machine.controller", machine_controller),
    ):
        _expect_equal(
            errors,
            f"{label}.sequence",
            current.get("event_sequence", current.get("transition_sequence", current.get("sequence"))),
            projection["sequence"],
        )
        _expect_equal(
            errors,
            f"{label}.event_hash",
            current.get("event_head", current.get("last_event_hash", current.get("event_hash"))),
            projection["event_hash"],
        )
        _expect_equal(
            errors,
            f"{label}.next_task",
            current.get("exact_next_task", current.get("next_task")),
            projection["next_task"],
        )
        _expect_equal(
            errors,
            f"{label}.next_state",
            current.get("exact_next_state", current.get("next_task_state")),
            projection["next_state"],
        )

    step_projections = (
        ("manifest.controller.completed_steps", manifest_controller.get("completed_steps")),
        (
            "checkpoint.current_xliff_compiler_checkpoint.completed_xlf_04_batches",
            [
                *projection["completed_steps"][:3],
                *checkpoint_xlf.get("completed_xlf_04_batches", []),
            ],
        ),
        (
            "checkpoint.xliff_starting_defects.completed_steps",
            checkpoint_defects.get("completed_steps"),
        ),
        (
            "machine.next_task_prerequisite.completed_steps",
            machine_next.get("completed_steps"),
        ),
    )
    for label, value in step_projections:
        _expect_equal(errors, label, value, projection["completed_steps"])

    for label, current in (
        ("checkpoint.current_xliff_compiler_checkpoint", checkpoint_xlf),
        ("machine.xlf_checkpoint", machine_xlf),
    ):
        _expect_equal(
            errors,
            f"{label}.obligation_count",
            current.get(
                "core_obligation_count",
                current.get(
                    "obligation_count",
                    current.get("core_obligation_inventory", {}).get("obligations"),
                ),
            ),
            projection["obligations"],
        )
        _expect_equal(
            errors,
            f"{label}.expected",
            current.get(
                "core_expected_obligation_count",
                current.get(
                    "expected_obligation_count",
                    current.get("core_obligation_inventory", {}).get(
                        "expected_obligation_count",
                        current.get("core_obligation_denominator", {}).get(
                            "expected_obligation_count"
                        ),
                    ),
                ),
            ),
            projection["expected"],
        )
        _expect_equal(
            errors,
            f"{label}.resolved",
            current.get(
                "core_resolved_expected_obligation_count",
                current.get(
                    "resolved_expected_obligation_count",
                    current.get("core_obligation_inventory", {}).get(
                        "resolved_expected_obligation_count",
                        current.get("core_obligation_denominator", {}).get(
                            "resolved_expected_obligation_count"
                        ),
                    ),
                ),
            ),
            projection["resolved"],
        )
        _expect_equal(
            errors,
            f"{label}.missing",
            current.get(
                "core_missing_expected_obligation_count",
                current.get(
                    "missing_expected_obligation_count",
                    current.get("core_obligation_inventory", {}).get(
                        "missing_expected_obligation_count",
                        current.get("core_obligation_denominator", {}).get(
                            "missing_expected_obligation_count"
                        ),
                    ),
                ),
            ),
            projection["missing"],
        )

    next_match = re.search(r"XLF-04-BATCH-\d{3}", str(projection["next_action"]))
    if next_match is None:
        errors.append("latest event does not select a bounded XLF-04 batch")
        expected_next = ""
    else:
        expected_next = next_match.group(0)
    for label, action in (
        ("manifest.controller.exact_next_action", manifest_controller.get("exact_next_action")),
        ("checkpoint exact_next_action", checkpoint_xlf.get("exact_next_action")),
        ("machine exact_next_action", machine_next.get("exact_next_action")),
    ):
        if expected_next and expected_next not in str(action):
            errors.append(f"{label} does not select {expected_next}")

    for path, patterns in STALE_ACTIVE_PATTERNS.items():
        text = texts.get(path, "")
        for pattern in patterns:
            if pattern in text:
                errors.append(f"{path} contains stale active-state phrase: {pattern!r}")

    return errors


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
        if not isinstance(relative, str):
            errors.append("manifest file entry lacks path")
            continue
        if relative in seen:
            errors.append(f"duplicate manifest path: {relative}")
        seen.add(relative)
        path = REPO_ROOT / relative
        if not path.is_file():
            errors.append(f"manifest path missing: {relative}")
            continue
        actual = _tracked_lf_sha256(relative)
        expected = entry.get("sha256")
        if actual != expected:
            errors.append(
                f"manifest digest mismatch for {relative}: expected {expected}, got {actual}"
            )
    if "plans/codex/handover/manifest.yaml" in seen:
        errors.append("manifest must exclude its own digest")
    if "plans/codex/handover/validate_handover.py" not in seen:
        errors.append("semantic validator is not bound into the manifest")
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
            if (
                not target
                or target.startswith(("#", "http://", "https://", "mailto:"))
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
    source = manifest.get("source_checkpoint", {})
    ancestor = source.get("required_ancestor")
    remote_ref = source.get("required_remote_ref")
    if not isinstance(ancestor, str) or not isinstance(remote_ref, str):
        return ["manifest source checkpoint lacks required ancestor or remote ref"]
    checks = (
        (ancestor, remote_ref, "source checkpoint"),
        ("HEAD", remote_ref, "current HEAD"),
    )
    for older, newer, label in checks:
        result = subprocess.run(
            ["git", "merge-base", "--is-ancestor", older, newer],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            errors.append(f"{label} {older} is not an ancestor of {newer}")
    remote = source.get("remote")
    branch = source.get("branch")
    if (remote, branch, source.get("forge")) != ("origin", "main", "GitLab"):
        errors.append("handover source is not GitLab origin/main")
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
    controller = _load_yaml(CONTROLLER_PATH)
    events = _load_events()
    latest = events[-1]
    texts = _tracked_texts(manifest)
    errors = [
        *_validate_event_chain(events),
        *_manifest_errors(manifest),
        *_link_errors(manifest),
        *_semantic_errors(
            manifest=manifest,
            checkpoint=checkpoint,
            machine=machine,
            controller=controller,
            latest_event=latest,
            texts=texts,
        ),
        *_git_errors(manifest),
    ]
    result = {
        "schema": "ff6/handover-validation@1",
        "valid": not errors,
        "event_id": latest.get("event_id"),
        "event_sequence": latest.get("sequence"),
        "event_hash": latest.get("event_hash"),
        "manifest_files": len(manifest.get("files", [])),
        "errors": errors,
    }
    context = {
        "manifest": manifest,
        "checkpoint": checkpoint,
        "machine": machine,
        "controller": controller,
        "latest": latest,
        "texts": texts,
    }
    return result, context


def run_self_test(context: Mapping[str, Any]) -> dict[str, Any]:
    cases: list[tuple[str, dict[str, Any]]] = []

    missing_batch = copy.deepcopy(context)
    missing_batch["checkpoint"]["xliff_starting_defects"]["completed_steps"].pop()
    cases.append(("missing_completed_batch", missing_batch))

    stale_next = copy.deepcopy(context)
    stale_next["manifest"]["controller"]["exact_next_action"] = "stale restart"
    cases.append(("stale_next_batch", stale_next))

    bad_head = copy.deepcopy(context)
    bad_head["machine"]["controller"]["event_hash"] = "0" * 64
    cases.append(("wrong_controller_head", bad_head))

    stale_phrase = copy.deepcopy(context)
    stale_path = "plans/codex/handover/ACTIVE-WORK-CHECKPOINT.md"
    stale_phrase["texts"][stale_path] += "\nEvent 24 binds the current implementation\n"
    cases.append(("stale_predecessor_as_current", stale_phrase))

    outcomes: list[dict[str, Any]] = []
    for name, case in cases:
        errors = _semantic_errors(
            manifest=case["manifest"],
            checkpoint=case["checkpoint"],
            machine=case["machine"],
            controller=case["controller"],
            latest_event=case["latest"],
            texts=case["texts"],
        )
        outcomes.append({"case": name, "rejected": bool(errors)})
    passed = all(item["rejected"] for item in outcomes)
    return {
        "schema": "ff6/handover-validation-self-test@1",
        "valid": passed,
        "negative_controls": outcomes,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="also prove that four semantic corruptions are rejected",
    )
    args = parser.parse_args(argv)
    try:
        result, context = validate_current()
        if args.self_test:
            result["self_test"] = run_self_test(context)
            result["valid"] = bool(result["valid"] and result["self_test"]["valid"])
    except (OSError, ValueError, TypeError, json.JSONDecodeError, yaml.YAMLError) as exc:
        result = {
            "schema": "ff6/handover-validation@1",
            "valid": False,
            "errors": [f"{type(exc).__name__}: {exc}"],
        }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
