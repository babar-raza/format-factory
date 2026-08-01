"""Deterministic FF6 provider-neutral handover projection.

generated_by: codex
visibility: internal

The controller and native journal are authoritative.  This module renders the
operational packet from those inputs; it never promotes a product or edits
controller state.  The source checkpoint is supplied explicitly so a packet
never tries to embed the commit containing its own final bytes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml


HANDOVER_ROOT = Path(__file__).resolve().parent
REPO_ROOT = HANDOVER_ROOT.parents[2]
CONTROLLER_PATH = REPO_ROOT / "plans/strategic/ff6/controller-state.yaml"
JOURNAL_PATH = REPO_ROOT / "plans/strategic/ff6/events.jsonl"
TASK_INDEX_PATH = REPO_ROOT / "taskcards/index.yaml"
CANONICAL_WINDOWS_START_PATH = (
    r"C:\Users\prora\OneDrive\Documents\GitHub\format-factory"
    r"\plans\codex\handover\START-HERE.md"
)

GENERATED_PATHS = (
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

PACKET_PATHS = (
    *GENERATED_PATHS,
    "plans/codex/handover/handover_projection.py",
    "plans/codex/handover/validate_handover.py",
    "plans/codex/handover/validate_committed_checkpoint.py",
    "plans/codex/handover/PROVIDER-SHIFT-CONTRACT.md",
    "plans/codex/handover/SHIFT-AND-RESUME-PROTOCOL.md",
    "plans/codex/handover/EXECUTION-RUNBOOK.md",
    "plans/codex/handover/STATE-MACHINE-AND-TASKCARD-PROTOCOL.md",
    "plans/codex/handover/VALIDATION-AND-RELEASE.md",
    "plans/codex/handover/CURRENT-STATE-AND-ROOT-CAUSES.md",
    "plans/codex/handover/PARALLEL-UBL-CHECKPOINT.yaml",
)

PROOF_INPUT_PATHS = (
    "plans/strategic/ff6/product-goal.yaml",
    "plans/strategic/ff6/controller-state.yaml",
    "plans/strategic/ff6/events.jsonl",
    "taskcards/TC-FF6-ACCEL-CONTROL-001.md",
    "taskcards/TC-FF6-NRRD-READINESS-001.md",
    "taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md",
    "taskcards/TC-FF6-UBL-TYPING-001.md",
    "taskcards/index.yaml",
    "reports/ff6/xliff-core-authority-candidate-census.yaml",
    "reports/ff6/xliff-core-obligation-denominator.yaml",
    "reports/sal-verification/xliff-core-candidate-adjudications.yaml",
    "reports/ff6/xliff-core-obligation-inventory.yaml",
)


class ProjectionError(RuntimeError):
    """Raised when authoritative inputs cannot produce a safe projection."""


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ProjectionError(f"{path.relative_to(REPO_ROOT)} is not a mapping")
    return value


def _load_events() -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for number, line in enumerate(
        JOURNAL_PATH.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ProjectionError(f"journal line {number} is not an object")
        events.append(value)
    if not events:
        raise ProjectionError("native event journal is empty")
    return events


def event_hash(event: Mapping[str, Any]) -> str:
    body = dict(event)
    body.pop("event_hash", None)
    encoded = json.dumps(
        body, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_event_chain(events: Sequence[Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    previous: str | None = None
    for expected, event in enumerate(events, start=1):
        if event.get("sequence") != expected:
            errors.append(f"event {expected}: sequence mismatch")
        claimed = event.get("event_hash")
        if claimed != event_hash(event):
            errors.append(f"event {expected}: hash mismatch")
        if expected > 1 and event.get("previous_event_hash") != previous:
            errors.append(f"event {expected}: predecessor mismatch")
        previous = claimed if isinstance(claimed, str) else None
    return errors


def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=REPO_ROOT, check=False, capture_output=True, text=True
    )
    if result.returncode != 0:
        raise ProjectionError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def _yaml_bytes(value: Mapping[str, Any]) -> bytes:
    return yaml.safe_dump(
        value,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        width=100,
    ).encode("utf-8")


def _front_matter(artifact_id: str, artifact_type: str) -> str:
    return (
        "---\n"
        f"artifact_id: {artifact_id}\n"
        f"artifact_type: {artifact_type}\n"
        "visibility: internal\n"
        "publish_allowed: false\n"
        "generated_by: codex\n"
        "generated_at: 2026-08-01\n"
        "---\n\n"
    )


@dataclass(frozen=True)
class ProjectionContext:
    """Digest-bound inputs used by all operational renderers."""

    source_checkpoint: str
    controller: Mapping[str, Any]
    latest_event: Mapping[str, Any]
    events: Sequence[Mapping[str, Any]]

    @property
    def sequence(self) -> int:
        value = self.latest_event.get("sequence")
        if not isinstance(value, int):
            raise ProjectionError("latest event sequence is not an integer")
        return value

    @property
    def event_id(self) -> str:
        return str(self.latest_event.get("event_id"))

    @property
    def event_hash(self) -> str:
        return str(self.latest_event.get("event_hash"))

    @property
    def control_task(self) -> Mapping[str, Any]:
        return self.latest_event

    @property
    def product_task(self) -> Mapping[str, Any]:
        value = self.controller.get("active_task", {})
        return value if isinstance(value, Mapping) else {}

    @property
    def product_continuation(self) -> Mapping[str, Any]:
        """Resolve continuation fields from the checkpoint owned by the active task."""

        task = self.product_task
        task_id = str(task.get("task_id", ""))
        checkpoint: Mapping[str, Any] = {}
        checkpoint_name = "active_task"
        for marker, candidate_name in (
            ("NRRD", "nrrd_checkpoint"),
            ("XLIFF", "xlf_checkpoint"),
            ("UBL", "ubl_checkpoint"),
        ):
            if marker in task_id:
                candidate = self.controller.get(candidate_name, {})
                if isinstance(candidate, Mapping):
                    checkpoint = candidate
                    checkpoint_name = candidate_name
                break

        semantic_commit = checkpoint.get("source_checkpoint_commit") or checkpoint.get(
            "checkpoint_source_commit"
        )
        if semantic_commit is None:
            commits = checkpoint.get("checkpoint_source_commits")
            if isinstance(commits, list) and commits:
                semantic_commit = commits[-1]

        return {
            "task_id": task.get("task_id"),
            "state": task.get("state"),
            "microstep": checkpoint.get("active_microstep")
            or checkpoint.get("first_unmet_step")
            or task.get("first_unmet_step"),
            "semantic_commit": semantic_commit
            or self.latest_event.get("semantic_commit"),
            "action": checkpoint.get("exact_next_action")
            or self.latest_event.get("exact_next_action"),
            "checkpoint_name": checkpoint_name,
        }

    @property
    def xlf(self) -> Mapping[str, Any]:
        value = self.controller.get("xlf_checkpoint", {})
        return value if isinstance(value, Mapping) else {}

    @property
    def ubl(self) -> Mapping[str, Any]:
        value = self.controller.get("ubl_checkpoint", {})
        return value if isinstance(value, Mapping) else {}

    @property
    def lane_a(self) -> Mapping[str, Any]:
        bootstrap = self.controller.get("acceleration_bootstrap", {})
        lanes = bootstrap.get("lanes", []) if isinstance(bootstrap, Mapping) else []
        for lane in lanes:
            if isinstance(lane, Mapping) and lane.get("lane") == "A":
                return lane
        raise ProjectionError("controller has no acceleration lane A")


def load_context(source_checkpoint: str | None = None) -> ProjectionContext:
    controller = _load_yaml(CONTROLLER_PATH)
    events = _load_events()
    chain_errors = validate_event_chain(events)
    if chain_errors:
        raise ProjectionError("; ".join(chain_errors))
    latest = events[-1]
    verified = controller.get("last_verified_event", {})
    if not isinstance(verified, Mapping):
        raise ProjectionError("controller last_verified_event is not a mapping")
    if verified.get("event_id") != latest.get("event_id"):
        raise ProjectionError("controller event id does not match journal head")
    if verified.get("event_hash") != latest.get("event_hash"):
        raise ProjectionError("controller event hash does not match journal head")
    if controller.get("transition_sequence") != latest.get("sequence"):
        raise ProjectionError("controller sequence does not match journal head")
    checkpoint = source_checkpoint or _git("rev-parse", "origin/main")
    if len(checkpoint) != 40:
        raise ProjectionError("source checkpoint is not a full Git commit id")
    return ProjectionContext(checkpoint, controller, latest, events)


def _common(ctx: ProjectionContext) -> dict[str, Any]:
    latest = ctx.latest_event
    immediate = ctx.lane_a
    continuation = ctx.product_continuation
    promotion = ctx.controller.get("promotion", {})
    return {
        "source_checkpoint": ctx.source_checkpoint,
        "event_id": ctx.event_id,
        "event_hash": ctx.event_hash,
        "event_sequence": ctx.sequence,
        "controller_state": ctx.controller.get("controller_state"),
        "control_task_id": latest.get("task_id"),
        "control_task_state": latest.get("task_state_after"),
        "control_transition": latest.get("transition"),
        "control_semantic_commit": latest.get("semantic_commit"),
        "control_next_action": latest.get("exact_next_action"),
        "immediate_task_id": immediate.get("task_id"),
        "immediate_task_state": immediate.get("state"),
        "immediate_task_action": immediate.get("first_action"),
        "product_task_id": continuation.get("task_id"),
        "product_task_state": continuation.get("state"),
        "product_microstep": continuation.get("microstep"),
        "product_semantic_commit": continuation.get("semantic_commit"),
        "product_next_action": continuation.get("action"),
        "product_checkpoint_name": continuation.get("checkpoint_name"),
        "certifications": ctx.controller.get("current_gap_summary", {}).get(
            "production_certifications"
        ),
        "promotion": promotion,
    }


def render_projection(ctx: ProjectionContext) -> dict[str, bytes]:
    """Render all operational files without touching the filesystem."""

    c = _common(ctx)
    xlf = ctx.xlf
    ubl = ctx.ubl
    lane = ctx.lane_a
    event_no = ctx.sequence
    same_active_task = c["immediate_task_id"] == c["product_task_id"]
    if same_active_task:
        continuation_text = (
            f"The controller-selected product continuation is the same task, "
            f"`{c['product_task_id']}`, at `{c['product_microstep']}`. Its accepted "
            f"semantic checkpoint is `{c['product_semantic_commit']}`."
        )
        ordering_invariant = (
            "The active controller task and product continuation are the same task. "
            "Continuation fields must come from that format's checkpoint; stale "
            "cross-format microsteps are invalid."
        )
    else:
        continuation_text = (
            f"The preserved product continuation is `{c['product_task_id']}` at "
            f"`{c['product_microstep']}`. Its accepted semantic checkpoint is "
            f"`{c['product_semantic_commit']}`. Controller closure must select it "
            "before product mutation begins."
        )
        ordering_invariant = (
            "The controller task and preserved product continuation are distinct. "
            "Controller closure selects the next task; their fields must never be mixed."
        )
    # The user requested one absolute Windows entry path.  Keep that display
    # value stable across detached replays; it is documentation, not an input
    # used to locate authoritative state.
    absolute_start = CANONICAL_WINDOWS_START_PATH
    start = _front_matter(
        f"FF6-HANDOVER-START-EVENT-{event_no}", "provider_neutral_handover_entry"
    ) + f"""# FF6 production program: start here

Canonical start file:

```text
{absolute_start}
```

GitLab `origin/main` is the only integration authority. The current native
controller head is `{c['event_id']}` (sequence `{event_no}`), hash
`{c['event_hash']}`, derived from source checkpoint
`{c['source_checkpoint']}`. Product certification remains `{c['certifications']}`;
all six promotion states remain `UNASSESSED`.

## Mission

Deliver independently publishable production-grade Python libraries for
IPYNB, OpenRaster, NRRD, XLIFF, SafeTensors, and OASIS UBL. Completion requires
all six technical certifications, installed-wheel proof, independent
interoperability, security/resource-limit proof, reproducible packages,
documentation, SBOMs, provenance, and extraction-ready repositories.

## Exact immediate controller work

Run `{lane.get('task_id')}` through the registered skill sequence declared in
its taskcard. Current action:

> {lane.get('first_action')}

{continuation_text}

## Honest boundary

- technical certifications: `{c['certifications']}`;
- OpenRaster source: absent;
- the other five product trees: partial and non-certified;
- XLIFF: `{xlf.get('core_production_accepted_obligation_count')}` of
  `{xlf.get('core_expected_obligation_count')}` expected Core obligations,
  `{xlf.get('candidate_dispositions_verified')}` of
  `{xlf.get('core_authority_candidate_count')}` candidate dispositions;
- UBL: `{ubl.get('document_roots')}` roots identified, but UBL-03 is incomplete;
- no gate, release, publication, certification, or product promotion follows
  from this packet.

## Mandatory resume order

1. Read [AGENTS.md](../../../AGENTS.md) and the active
   [taskcard](../../../taskcards/{c['immediate_task_id']}.md).
2. Fetch only GitLab `origin/main`; require local `HEAD == origin/main` before
   a clean transfer mutation.
3. Run `python plans/codex/handover/validate_handover.py --self-test --require-clean`.
4. Query coordination, register a fresh identity, claim exact paths, create a
   live skill manifest, and use preflight/record-write for every mutation.
5. Execute the immediate controller action above. A new provider must never
   reuse this shift's identity, token, lease, manifest, or authorization.

## Packet map

- [Machine state](CURRENT-MACHINE-STATE.yaml)
- [Checkpoint contract](checkpoint.yaml)
- [Current shift handover](CURRENT-SHIFT-HANDOVER.md)
- [Exact task split](NEXT-MICROSTEP.yaml)
- [Provider commands](CLAUDE-START.md)
- [Active work checkpoint](ACTIVE-WORK-CHECKPOINT.md)
- [Recovery contract](INFLIGHT-RECOVERY.yaml)
- [Clean replay rules](CLEAN-REPLAY-REPAIR.md)
- [Root causes and durable design](CURRENT-STATE-AND-ROOT-CAUSES.md)
- [Provider shift contract](PROVIDER-SHIFT-CONTRACT.md)
- [Execution runbook](EXECUTION-RUNBOOK.md)
- [State machine and taskcards](STATE-MACHINE-AND-TASKCARD-PROTOCOL.md)
- [Validation and release](VALIDATION-AND-RELEASE.md)
- [Parallel UBL checkpoint](PARALLEL-UBL-CHECKPOINT.yaml)
- [Manifest](manifest.yaml)
"""

    machine = {
        "schema": "ff6/provider-neutral-machine-state@21",
        "artifact_id": f"FF6-CURRENT-MACHINE-STATE-EVENT-{event_no}",
        "visibility": "internal",
        "publish_allowed": False,
        "generated_by": "codex",
        "repository": {
            "forge": "GitLab",
            "remote": "origin",
            "branch": "main",
            "source_checkpoint": c["source_checkpoint"],
            "github_authorized": False,
            "other_branches_authorized": False,
        },
        "controller": {
            "state": c["controller_state"],
            "event_sequence": event_no,
            "event_id": c["event_id"],
            "event_hash": c["event_hash"],
            "task_id": c["control_task_id"],
            "task_state": c["control_task_state"],
            "semantic_commit": c["control_semantic_commit"],
            "exact_next_action": c["control_next_action"],
        },
        "immediate_lane": {
            "task_id": c["immediate_task_id"],
            "task_state": c["immediate_task_state"],
            "exact_next_action": c["immediate_task_action"],
        },
        "product_continuation": {
            "task_id": c["product_task_id"],
            "state": c["product_task_state"],
            "microstep": c["product_microstep"],
            "semantic_commit": c["product_semantic_commit"],
            "exact_next_action": c["product_next_action"],
        },
        "program_truth": {
            "production_certifications": c["certifications"],
            "promotion": c["promotion"],
            "terminal_condition_met": False,
        },
        "xliff": {
            "expected_core_obligations": xlf.get("core_expected_obligation_count"),
            "accepted_core_obligations": xlf.get(
                "core_production_accepted_obligation_count"
            ),
            "missing_core_obligations": xlf.get(
                "core_production_accepted_missing_obligation_count"
            ),
            "candidate_count": xlf.get("core_authority_candidate_count"),
            "verified_dispositions": xlf.get("candidate_dispositions_verified"),
            "unverified_dispositions": xlf.get("candidate_dispositions_unverified"),
            "complete": xlf.get("core_complete"),
        },
        "ubl": {
            "document_roots": ubl.get("document_roots"),
            "schema_documents": ubl.get("schema_documents_parsed"),
            "local_particle_nodes": ubl.get("local_particle_nodes"),
            "derivation_edges": ubl.get("derivation_edges"),
            "next_microstep": ubl.get("next_microstep"),
            "complete": ubl.get("reachable_schema_graph_complete"),
        },
        "workspace_transfer": {
            "requires_clean_head_equal_origin_main": True,
            "provider_identity_transferable": False,
            "leases_transferable": False,
            "execution_manifests_transferable": False,
            "local_only_required_for_resume": False,
        },
    }

    checkpoint = {
        "schema": "ff6/provider-neutral-checkpoint@19",
        "artifact_id": f"FF6-HANDOVER-CHECKPOINT-EVENT-{event_no}",
        "visibility": "internal",
        "publish_allowed": False,
        "generated_by": "codex",
        "source_checkpoint": {
            "forge": "GitLab",
            "remote": "origin",
            "branch": "main",
            "repository_checkpoint": c["source_checkpoint"],
            "packet_commit_rule": (
                "The packet commit must descend from repository_checkpoint; "
                "the packet never self-references its containing commit."
            ),
        },
        "controller_checkpoint": machine["controller"],
        "product_checkpoint": machine["product_continuation"],
        "truth_boundary": machine["program_truth"],
        "mandatory_resume_action": {
            "task_id": c["immediate_task_id"],
            "task_state": c["immediate_task_state"],
            "action": c["immediate_task_action"],
        },
    }

    next_step = {
        "schema": "ff6/next-microstep@3",
        "artifact_id": f"FF6-NEXT-MICROSTEP-EVENT-{event_no}",
        "visibility": "internal",
        "generated_by": "codex",
        "controller_task": {
            "task_id": c["immediate_task_id"],
            "state": c["immediate_task_state"],
            "event_id": c["event_id"],
            "accepted_event_task_id": c["control_task_id"],
            "action": c["immediate_task_action"],
        },
        "product_continuation": {
            "task_id": c["product_task_id"],
            "state": c["product_task_state"],
            "microstep": c["product_microstep"],
            "semantic_commit": c["product_semantic_commit"],
            "action": c["product_next_action"],
        },
        "ordering_invariant": ordering_invariant,
    }

    recovery = {
        "schema": "ff6/inflight-recovery@2",
        "artifact_id": f"FF6-INFLIGHT-RECOVERY-EVENT-{event_no}",
        "visibility": "internal",
        "generated_by": "codex",
        "canonical_reconstruction": {
            "remote": "origin",
            "branch": "main",
            "source_checkpoint": c["source_checkpoint"],
            "event_id": c["event_id"],
            "event_hash": c["event_hash"],
            "controller_path": "plans/strategic/ff6/controller-state.yaml",
            "journal_path": "plans/strategic/ff6/events.jsonl",
        },
        "non_transferable": [
            "provider identity",
            "coordination token",
            "leases",
            "execution manifests",
            "mutation authorizations",
            "ignored local state",
        ],
        "recovery_rule": (
            "Reconstruct from GitLab main and validate the committed packet; "
            "never recover by resetting, stashing, cleaning, or reusing a prior identity."
        ),
    }

    shift = _front_matter(
        f"FF6-CURRENT-SHIFT-HANDOVER-EVENT-{event_no}", "provider_shift_handover"
    ) + f"""# Current shift handover: {c['event_id']}

## Goal

Six production-grade, independently publishable Python format libraries plus
the proof, packaging, extraction, and release-preparation machinery. The
mission remains active and technical certification is `{c['certifications']}`.

## Accepted control work

`{c['event_id']}` records transition `{c['control_transition']}` and binds
semantic commit `{c['control_semantic_commit']}`. This projection transfers only
that recorded state; it does not upgrade product, certification, gate, release,
or publication status.

## Exact continuation

- accepted event task: `{c['control_task_id']}`;
- immediate lane task: `{c['immediate_task_id']}`;
- source checkpoint: `{c['source_checkpoint']}`;
- control semantic commit: `{c['control_semantic_commit']}`;
- action: {lane.get('first_action')}

{continuation_text}

## Current product truth

- OpenRaster source remains absent.
- Five existing product trees remain partial and non-certified.
- XLIFF remains {xlf.get('core_production_accepted_obligation_count')}/
  {xlf.get('core_expected_obligation_count')} obligations and
  {xlf.get('candidate_dispositions_verified')}/
  {xlf.get('core_authority_candidate_count')} adjudicated candidates.
- UBL-03 remains incomplete after {ubl.get('derivation_edges')} derivation edges.
- No product, certification, promotion, release, publication, or gate state
  changed in this control slice.

## Verification required before transfer

Run the validator with `--self-test --require-clean`, then run
`validate_committed_checkpoint.py --ref origin/main` from a clean checkout.
Three same-input generations must be byte-identical and a stale event/task
mutation must be rejected.
"""

    claude = _front_matter(
        f"FF6-PROVIDER-START-EVENT-{event_no}", "provider_start_commands"
    ) + f"""# Provider-neutral start commands

Start at [START-HERE.md](START-HERE.md). Verify GitLab `origin/main`, event
`{c['event_id']}`, and source checkpoint `{c['source_checkpoint']}`. Run:

```powershell
git fetch origin
git status --short --branch
python plans/codex/handover/validate_handover.py --self-test --require-clean
python plans/codex/handover/validate_committed_checkpoint.py --ref origin/main
python -m tools.supervisor.coordination status
```

Then register a fresh identity and execute `{c['immediate_task_id']}` through
its registered skill sequence. Never reuse recorded provider-local state.
"""

    active = _front_matter(
        f"FF6-ACTIVE-WORK-EVENT-{event_no}", "active_work_checkpoint"
    ) + f"""# Active work checkpoint

Controller head: `{c['event_id']}` / `{c['event_hash']}`.

Immediate task: `{c['immediate_task_id']}`. Immediate action:

> {lane.get('first_action')}

Product continuation: `{c['product_task_id']}` / `{c['product_microstep']}`
from `{c['product_checkpoint_name']}`.
Certification remains `{c['certifications']}` and all promotions remain
`UNASSESSED`.
"""

    replay = _front_matter(
        f"FF6-CLEAN-REPLAY-EVENT-{event_no}", "clean_replay_contract"
    ) + f"""# Clean replay and repair contract

Reconstruct from GitLab `origin/main`; require source checkpoint
`{c['source_checkpoint']}` to be an ancestor. Validate native event
`{c['event_id']}` and hash `{c['event_hash']}` before executing any mutation.

Use a fresh checkout/worktree, fresh environment, fresh coordination identity,
and immutable authority inputs. Never reset, stash, clean, or overwrite shared
state. A failed replay creates evidence and remediation; it cannot promote or
silently rewrite the accepted product checkpoint `{c['product_semantic_commit']}`.
"""

    return {
        "plans/codex/handover/START-HERE.md": start.encode("utf-8"),
        "plans/codex/handover/CLAUDE-START.md": claude.encode("utf-8"),
        "plans/codex/handover/CLEAN-REPLAY-REPAIR.md": replay.encode("utf-8"),
        "plans/codex/handover/ACTIVE-WORK-CHECKPOINT.md": active.encode("utf-8"),
        "plans/codex/handover/CURRENT-MACHINE-STATE.yaml": _yaml_bytes(machine),
        "plans/codex/handover/checkpoint.yaml": _yaml_bytes(checkpoint),
        "plans/codex/handover/NEXT-MICROSTEP.yaml": _yaml_bytes(next_step),
        "plans/codex/handover/CURRENT-SHIFT-HANDOVER.md": shift.encode("utf-8"),
        "plans/codex/handover/INFLIGHT-RECOVERY.yaml": _yaml_bytes(recovery),
    }


def canonical_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n")


def build_manifest(ctx: ProjectionContext) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for relative in (*PACKET_PATHS, *PROOF_INPUT_PATHS):
        path = REPO_ROOT / relative
        if not path.is_file():
            raise ProjectionError(f"manifest input missing: {relative}")
        data = canonical_bytes(path)
        rows.append(
            {
                "path": relative,
                "sha256": hashlib.sha256(data).hexdigest(),
                "canonical_bytes": len(data),
            }
        )
    return {
        "schema": "ff6/provider-neutral-handover-manifest@21",
        "artifact_id": f"FF6-HANDOVER-MANIFEST-EVENT-{ctx.sequence}",
        "visibility": "internal",
        "publish_allowed": False,
        "generated_by": "codex",
        "canonicalization": {
            "algorithm": "sha256",
            "line_endings": "LF",
            "manifest_self_hash": "excluded",
        },
        "controller": {
            "event_id": ctx.event_id,
            "event_hash": ctx.event_hash,
            "event_sequence": ctx.sequence,
            "state": ctx.controller.get("controller_state"),
        },
        "source_checkpoint": {
            "remote": "origin",
            "branch": "main",
            "checkpoint_commit": ctx.source_checkpoint,
        },
        "files": rows,
        "validation": {
            "expected_manifest_files": len(rows),
            "generated_operational_files": len(GENERATED_PATHS),
            "deterministic_runs_required": 3,
            "stale_value_negative_controls_required": True,
            "internal_links_required": True,
            "native_event_chain_required": True,
            "gitlab_ancestry_required": True,
            "clean_worktree_required_for_transfer": True,
        },
        "truth_boundary": {
            "products_certified": ctx.controller.get("current_gap_summary", {}).get(
                "production_certifications"
            ),
            "promotion_effect": "none",
        },
    }


def write_projection(ctx: ProjectionContext) -> list[str]:
    rendered = render_projection(ctx)
    changed: list[str] = []
    for relative, data in rendered.items():
        path = REPO_ROOT / relative
        if not path.exists() or canonical_bytes(path) != data:
            path.write_bytes(data)
            changed.append(relative)
    manifest_data = _yaml_bytes(build_manifest(ctx))
    manifest_path = HANDOVER_ROOT / "manifest.yaml"
    if not manifest_path.exists() or canonical_bytes(manifest_path) != manifest_data:
        manifest_path.write_bytes(manifest_data)
        changed.append("plans/codex/handover/manifest.yaml")
    return changed


def deterministic_digest(ctx: ProjectionContext) -> str:
    rendered = render_projection(ctx)
    payload = b"".join(
        relative.encode("utf-8") + b"\0" + rendered[relative]
        for relative in sorted(rendered)
    )
    return hashlib.sha256(payload).hexdigest()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-checkpoint")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        ctx = load_context(args.source_checkpoint)
        expected = render_projection(ctx)
        if args.check:
            stale = [
                relative
                for relative, data in expected.items()
                if not (REPO_ROOT / relative).is_file()
                or canonical_bytes(REPO_ROOT / relative) != data
            ]
            result = {
                "result": "PASS" if not stale else "FAIL",
                "event_id": ctx.event_id,
                "source_checkpoint": ctx.source_checkpoint,
                "deterministic_digest": deterministic_digest(ctx),
                "stale_paths": stale,
            }
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0 if not stale else 1
        changed = write_projection(ctx)
        print(
            json.dumps(
                {
                    "result": "PASS",
                    "event_id": ctx.event_id,
                    "source_checkpoint": ctx.source_checkpoint,
                    "deterministic_digest": deterministic_digest(ctx),
                    "changed_paths": changed,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    except (OSError, ValueError, ProjectionError, yaml.YAMLError) as exc:
        print(json.dumps({"result": "FAIL", "errors": [str(exc)]}, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
