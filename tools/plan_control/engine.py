from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .identity import stable_task_id
from .journal import EventJournal, JournalError, canonical_json
from .models import AuthorityMode, ExecutionState, validate_transition
from .parser import ParsedPlan, materialize_task, parse_plan
from .portfolio import read_source_items
from .producer import read_checkpoint
from .projections import (
    projection_digest,
    projection_documents,
    queue_projection,
    reduce_events,
    write_projections,
)
from .worktrees import observe_worktrees, parse_active_tasks, verify_commit_occurrence


APPROVED_PLAN_DIRS = (
    ".claude",
    ".governance",
    "healing",
    "layers",
    "secondary",
    "source-portfolios",
    "strategic",
)
IGNORED_ROOT_FILES = {"README.md", "master-plan.md"}


@dataclass(slots=True)
class ControlPaths:
    repo: Path
    control_root: Path
    local_root: Path

    @classmethod
    def create(
        cls,
        repo: Path,
        control_root: Path | None = None,
        local_root: Path | None = None,
    ) -> "ControlPaths":
        resolved = repo.resolve()
        return cls(
            resolved,
            (control_root or resolved / "plans" / ".control").resolve(),
            (local_root or resolved / ".local" / "plan-control").resolve(),
        )

    @property
    def journal(self) -> Path:
        return self.control_root / "events.jsonl"

    @property
    def projection_root(self) -> Path:
        return self.control_root / "projections"


class PlanControlEngine:
    def __init__(
        self,
        repo: Path,
        *,
        control_root: Path | None = None,
        local_root: Path | None = None,
        repository_id: str = "format-factory",
    ):
        self.paths = ControlPaths.create(repo, control_root, local_root)
        self.repository_id = repository_id
        self.journal = EventJournal(
            self.paths.journal,
            lock_path=self.paths.local_root / "locks" / "journal.lock",
        )

    def state(self) -> dict[str, Any]:
        return reduce_events(self.journal.read())

    def _append(self, kind: str, payload: dict[str, Any], identity: str) -> bool:
        return self.journal.append(kind, payload, event_id=identity).appended

    def route_violations(self) -> list[str]:
        plans = self.paths.repo / "plans"
        violations: list[str] = []
        oracle = plans / "oracle"
        if oracle.exists():
            violations.append("UNAPPROVED_PLAN_ROOT:plans/oracle")
        for path in sorted(plans.glob("*.md")):
            if path.name not in IGNORED_ROOT_FILES:
                violations.append(f"UNROUTED_PLAN_FILE:{path.relative_to(self.paths.repo).as_posix()}")
        return violations

    def canonical_plan_paths(self) -> list[Path]:
        plans = self.paths.repo / "plans"
        paths: list[Path] = []
        master = plans / "master-plan.md"
        if master.exists():
            paths.append(master)
        for directory in APPROVED_PLAN_DIRS:
            root = plans / directory
            if root.exists():
                paths.extend(sorted(root.rglob("*.md")))
        return paths

    @staticmethod
    def _event_identity(prefix: str, value: Any) -> str:
        digest = hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()[:24]
        return f"{prefix}:{digest}"

    def _plan_records(
        self,
        parsed: ParsedPlan,
        *,
        relative_path: str,
        canonical: bool,
        branch: str | None,
        commit: str | None,
        dirty: bool,
        worktree_path: str | None = None,
        abandoned: bool = False,
        coordination_owner: str | None = None,
        include_definition: bool = True,
    ) -> tuple[list[tuple[str, dict[str, Any], str, None]], int]:
        records: list[tuple[str, dict[str, Any], str, None]] = []
        tasks_added = 0
        if include_definition:
            execution_state = parsed.execution_state
            if any(
                warning.startswith(("PARSER_GAP:", "UNKNOWN_", "CONTRADICTORY_"))
                for warning in parsed.warnings
            ):
                execution_state = ExecutionState.BLOCKED
            if execution_state == ExecutionState.COMPLETE:
                has_open_tasks = any(
                    task.state
                    not in {
                        ExecutionState.VERIFIED,
                        ExecutionState.COMPLETE,
                        ExecutionState.CANCELLED,
                        ExecutionState.TERMINAL_CLOSED,
                    }
                    for task in parsed.tasks
                )
                execution_state = (
                    ExecutionState.ITERATION_REQUIRED
                    if has_open_tasks
                    else ExecutionState.COMPLETION_CANDIDATE
                )
            plan = {
                "plan_id": parsed.plan_id,
                "title": parsed.title,
                "aliases": parsed.aliases,
                "authority_mode": parsed.authority_mode.value,
                "execution_state": execution_state.value,
                "parent_plan_id": None,
                "occurrences": [],
                "external_claimed": bool(coordination_owner),
                "source": "canonical" if canonical else "external_observation",
                "warnings": parsed.warnings,
            }
            records.append(
                (
                    "PLAN_UPSERTED",
                    {"plan": plan},
                    self._event_identity(
                        "plan-upsert", [parsed.plan_id, parsed.content_sha256, canonical]
                    ),
                    None,
                )
            )
            for task in parsed.tasks:
                payload = materialize_task(parsed.plan_id, task, relative_path)
                if not canonical and dirty and payload["state"] in {
                    ExecutionState.COMPLETE.value,
                    ExecutionState.VERIFIED.value,
                }:
                    payload["state"] = ExecutionState.AWAITING_VERIFICATION.value
                    payload["warnings"].append("UNCOMMITTED_EXTERNAL_CLOSURE_NOT_CANONICAL")
                records.append(
                    (
                        "TASK_UPSERTED",
                        {"task": payload},
                        self._event_identity("task-upsert", payload),
                        None,
                    )
                )
                tasks_added += 1
            for warning in parsed.warnings:
                if warning.startswith(
                    ("PARSER_GAP:", "UNKNOWN_", "CONTRADICTORY_", "SUPERSEDED_")
                ):
                    gap = {
                        "gap_id": "parser:"
                        + hashlib.sha256(
                            f"{parsed.plan_id}:{relative_path}:{warning}".encode()
                        ).hexdigest()[:16],
                        "kind": "PLAN_PARSE",
                        "plan_id": parsed.plan_id,
                        "path": relative_path,
                        "detail": warning,
                        "state": "OPEN",
                    }
                    records.append(
                        (
                            "GAP_RECORDED",
                            gap,
                            self._event_identity("parser-gap", gap),
                            None,
                        )
                    )
        occurrence = {
            "path": relative_path,
            "worktree_path": worktree_path,
            "branch": branch,
            "commit": commit,
            "canonical": canonical,
            "dirty": dirty,
            "coordination_owner": coordination_owner,
            "content_sha256": parsed.content_sha256,
            "active": True,
            "abandoned": abandoned,
        }
        records.append(
            (
                "OCCURRENCE_OBSERVED",
                {"plan_id": parsed.plan_id, "occurrence": occurrence},
                self._event_identity("occurrence", [parsed.plan_id, occurrence]),
                None,
            )
        )
        if coordination_owner:
            claim = {
                "plan_id": parsed.plan_id,
                "claimed": True,
                "coordination_owner": coordination_owner,
            }
            records.append(
                (
                    "PLAN_EXTERNAL_CLAIMED",
                    claim,
                    self._event_identity(
                        "external-claim", [parsed.plan_id, coordination_owner, commit]
                    ),
                    None,
                )
            )
        return records, tasks_added

    def _upsert_plan(
        self,
        parsed: ParsedPlan,
        **kwargs: Any,
    ) -> tuple[int, int]:
        records, tasks_added = self._plan_records(parsed, **kwargs)
        results = self.journal.append_many(records)
        return sum(result.appended for result in results), tasks_added

    def discover(self) -> dict[str, Any]:
        records: list[tuple[str, dict[str, Any], str, None]] = []
        task_count = 0
        paths = self.canonical_plan_paths()
        alias_owners = dict(self.state()["aliases"])
        for path in paths:
            parsed = parse_plan(path, repository_id=self.repository_id)
            owners = {
                alias_owners[alias.lower()]
                for alias in parsed.aliases
                if alias.lower() in alias_owners
            }
            if len(owners) == 1:
                parsed.plan_id = owners.pop()
            elif len(owners) > 1:
                parsed.warnings.append(
                    "PARSER_GAP:ALIASES_RESOLVE_TO_MULTIPLE_PLAN_IDENTITIES"
                )
            for alias in parsed.aliases:
                alias_owners.setdefault(alias.lower(), parsed.plan_id)
            plan_records, tasks = self._plan_records(
                parsed,
                relative_path=path.relative_to(self.paths.repo).as_posix(),
                canonical=True,
                branch=None,
                commit=None,
                dirty=False,
                worktree_path=str(self.paths.repo),
                abandoned=False,
            )
            records.extend(plan_records)
            task_count += tasks
        for violation in self.route_violations():
            records.append(
                (
                    "GAP_RECORDED",
                    {
                        "gap_id": f"routing:{hashlib.sha256(violation.encode()).hexdigest()[:16]}",
                        "kind": "PLAN_ROUTING",
                        "detail": violation,
                        "state": "OPEN",
                    },
                    f"routing-gap:{hashlib.sha256(violation.encode()).hexdigest()[:24]}",
                    None,
                )
            )
        results = self.journal.append_many(records)
        return {
            "canonical_plan_count": len(paths),
            "parsed_task_count": task_count,
            "events_appended": sum(result.appended for result in results),
            "route_violations": self.route_violations(),
        }

    def observe_external_worktrees(self, coordination_status: str = "") -> dict[str, Any]:
        observations = observe_worktrees(self.paths.repo)
        active = parse_active_tasks(coordination_status)
        canonical_hashes = {
            path.relative_to(self.paths.repo).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in self.canonical_plan_paths()
        }
        records: list[tuple[str, dict[str, Any], str, None]] = []
        plans_observed = 0
        current_state = self.state()
        known_plan_ids = set(current_state["plans"])
        alias_owners = dict(current_state["aliases"])
        for observation in observations:
            if observation.canonical:
                continue
            root = Path(observation.path)
            plan_root = root / "plans"
            if not plan_root.exists():
                continue
            for path in sorted(plan_root.rglob("*.md")):
                if ".control" in path.parts:
                    continue
                relative = path.relative_to(root).as_posix()
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                if canonical_hashes.get(relative) == digest:
                    continue
                parsed = parse_plan(path, repository_id=self.repository_id)
                owners = {
                    alias_owners[alias.lower()]
                    for alias in parsed.aliases
                    if alias.lower() in alias_owners
                }
                if len(owners) == 1:
                    parsed.plan_id = owners.pop()
                elif len(owners) > 1:
                    parsed.warnings.append(
                        "PARSER_GAP:ALIASES_RESOLVE_TO_MULTIPLE_PLAN_IDENTITIES"
                    )
                for alias in parsed.aliases:
                    alias_owners.setdefault(alias.lower(), parsed.plan_id)
                active_owner = next(
                    (active[alias.lower()] for alias in parsed.aliases if alias.lower() in active),
                    None,
                )
                owner = active_owner or (
                    f"abandoned-worktree:{observation.branch or observation.path}"
                    if getattr(observation, "abandoned", False)
                    else
                    f"uncommitted-worktree:{observation.branch or observation.path}"
                    if observation.dirty
                    else f"external-worktree:{observation.branch or observation.path}"
                )
                plan_records, _ = self._plan_records(
                    parsed,
                    relative_path=str(path),
                    canonical=False,
                    branch=observation.branch,
                    commit=observation.commit,
                    dirty=observation.dirty,
                    worktree_path=observation.path,
                    abandoned=getattr(observation, "abandoned", False),
                    coordination_owner=owner,
                    include_definition=parsed.plan_id not in known_plan_ids,
                )
                records.extend(plan_records)
                known_plan_ids.add(parsed.plan_id)
                plans_observed += 1
                if getattr(observation, "abandoned", False):
                    gap = {
                        "gap_id": "worktree:"
                        + hashlib.sha256(
                            f"{observation.path}:{observation.branch}".encode()
                        ).hexdigest()[:16],
                        "kind": "ABANDONED_WORKTREE_BRANCH",
                        "path": observation.path,
                        "branch": observation.branch,
                        "commit": observation.commit,
                        "state": "OPEN",
                    }
                    records.append(
                        (
                            "GAP_RECORDED",
                            gap,
                            self._event_identity("worktree-gap", gap),
                            None,
                        )
                    )
        snapshot = {
            "worktrees": [
                {
                    "path": observation.path,
                    "branch": observation.branch,
                    "commit": observation.commit,
                    "abandoned": getattr(observation, "abandoned", False),
                }
                for observation in observations
                if not observation.canonical
            ]
        }
        previous_snapshot = next(
            (
                event
                for event in reversed(self.journal.read())
                if event["event_type"] == "WORKTREE_SNAPSHOT_RECORDED"
            ),
            None,
        )
        snapshot_event_id = (
            previous_snapshot["event_id"]
            if previous_snapshot and previous_snapshot["payload"] == snapshot
            else self._event_identity(
                "worktree-snapshot",
                [
                    previous_snapshot["event_hash"] if previous_snapshot else "GENESIS",
                    snapshot,
                ],
            )
        )
        records.append(
            (
                "WORKTREE_SNAPSHOT_RECORDED",
                snapshot,
                snapshot_event_id,
                None,
            )
        )
        results = self.journal.append_many(records)
        return {
            "worktrees": [item.to_dict() for item in observations],
            "external_plans_observed": plans_observed,
            "events_appended": sum(result.appended for result in results),
            "active_tasks": active,
        }

    def reconcile_portfolio(self, register: Path | None = None) -> dict[str, Any]:
        path = register or (
            self.paths.repo
            / "reports"
            / "portfolio-execution"
            / "ff-portfolio-41-prod-001"
            / "source-taskcard-register.json"
        )
        items = read_source_items(path)
        records: list[tuple[str, dict[str, Any], str, None]] = []
        for item in items:
            records.append(
                (
                    "SOURCE_ITEM_UPSERTED",
                    {"source_item": item},
                    self._event_identity("source-item", item),
                    None,
                )
            )
            if item.get("contradiction"):
                gap = {
                    "gap_id": f"portfolio:{item['source_item_id']}",
                    "kind": "PORTFOLIO_FALSE_CLOSURE",
                    "source_item_id": item["source_item_id"],
                    "detail": item["contradiction"],
                    "state": "OPEN",
                }
                records.append(
                    (
                        "GAP_RECORDED",
                        gap,
                        self._event_identity("portfolio-gap", gap),
                        None,
                    )
                )
        results = self.journal.append_many(records)
        return {
            "source_item_count": len(items),
            "still_open": sum(item["disposition"] == "STILL_OPEN" for item in items),
            "events_appended": sum(result.appended for result in results),
        }

    def project(self) -> dict[str, Any]:
        state = self.state()
        documents = projection_documents(state)
        digest = write_projections(self.paths.projection_root, documents)
        return {
            "journal_head": state["journal_head"],
            "projection_digest": digest,
            "documents": sorted(documents),
            **documents["status.json"],
        }

    def reconcile(self, *, coordination_status: str = "", include_worktrees: bool = True) -> dict[str, Any]:
        result = {
            "discover": self.discover(),
            "portfolio": self.reconcile_portfolio(),
        }
        if include_worktrees:
            result["worktrees"] = self.observe_external_worktrees(coordination_status)
        result["migration_checkpoints"] = self.reconcile_migration_checkpoints()
        result["retries"] = self.release_due_retries()
        result["projection"] = self.project()
        return result

    def reconcile_migration_checkpoints(self) -> dict[str, Any]:
        canonical_config = self.paths.repo / "plans" / ".control" / "config.json"
        config_path = (
            canonical_config
            if canonical_config.exists()
            else self.paths.control_root / "config.json"
        )
        if not config_path.exists():
            return {"configured": 0, "recorded": 0}
        config = json.loads(config_path.read_text(encoding="utf-8"))
        configured = config.get("migration_checkpoints") or []
        results = []
        for checkpoint in configured:
            kind, plan_id = self.resolve_id(checkpoint["plan_alias"])
            if kind != "plan":
                raise ValueError(f"{checkpoint['plan_alias']} is not a plan")
            proof = verify_commit_occurrence(
                self.paths.repo,
                checkpoint["source_commit"],
                checkpoint.get("branch"),
            )
            payload = {
                "plan_id": plan_id,
                "plan_alias": checkpoint["plan_alias"],
                "source_commit": proof["source_commit"],
                "branch": checkpoint.get("branch"),
                "commit_object_digest": proof["commit_object_digest"],
                "verification": checkpoint.get(
                    "verification", "git-object-and-ancestry"
                ),
                "verified": True,
            }
            results.append(
                self.journal.append(
                    "PLAN_CHECKPOINT_RECORDED",
                    payload,
                    event_id=self._event_identity("plan-checkpoint", payload),
                )
            )
        return {
            "configured": len(configured),
            "recorded": sum(result.appended for result in results),
        }

    def doctor(self) -> dict[str, Any]:
        findings: list[str] = []
        try:
            state = self.state()
        except JournalError as exc:
            return {"ok": False, "findings": [str(exc)]}
        documents = projection_documents(state)
        for name, expected in documents.items():
            path = self.paths.projection_root / name
            if not path.exists():
                findings.append(f"MISSING_PROJECTION:{name}")
                continue
            try:
                actual = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                findings.append(f"CORRUPT_PROJECTION:{name}")
                continue
            if actual != expected:
                findings.append(f"STALE_PROJECTION:{name}")
        findings.extend(self.route_violations())
        duplicate_task_ids = len(state["tasks"]) != len(set(state["tasks"]))
        if duplicate_task_ids:
            findings.append("DUPLICATE_TASK_ID")
        return {
            "ok": not findings,
            "findings": findings,
            "journal_head": state["journal_head"],
            "projection_digest": projection_digest(documents),
            "plan_count": len(state["plans"]),
            "task_count": len(state["tasks"]),
            "source_item_count": len(state["source_items"]),
        }

    def resolve_id(self, value: str) -> tuple[str, str]:
        state = self.state()
        if value in state["plans"]:
            return "plan", value
        if value in state["tasks"]:
            return "task", value
        alias = state["aliases"].get(value.lower())
        if alias:
            return "plan", alias
        matches = [
            task_id
            for task_id, task in state["tasks"].items()
            if task.get("external_id", "").lower() == value.lower()
        ]
        if len(matches) == 1:
            return "task", matches[0]
        raise KeyError(value)

    def transition_task(
        self,
        value: str,
        target: ExecutionState,
        *,
        reason: str,
        evidence: dict[str, Any] | None = None,
        external_blocker: bool = False,
    ) -> dict[str, Any]:
        kind, task_id = self.resolve_id(value)
        if kind != "task":
            raise ValueError(f"{value} is not a task")
        state = self.state()
        current = ExecutionState(state["tasks"][task_id]["state"])
        checkpoint = next(
            (
                item
                for item in reversed(state["domain_checkpoints"])
                if item.get("task_id") == task_id and not item.get("verified")
            ),
            None,
        )
        if target == ExecutionState.VERIFIED:
            if not evidence or not evidence.get("reference") or not evidence.get("verifier"):
                raise ValueError("verification requires evidence reference and verifier")
            if checkpoint:
                reference = str(evidence["reference"]).removeprefix("sha256:")
                if reference.lower() != checkpoint["evidence_digest"].lower():
                    raise ValueError("verification evidence does not match producer checkpoint")
                if evidence["verifier"] != checkpoint["declared_verifier"]:
                    raise ValueError("verification must use the checkpoint declared verifier")
        if target == ExecutionState.CANCELLED:
            if not evidence or not re.fullmatch(
                r"(?:decision|record|delegation):\S+",
                str(evidence.get("authority") or ""),
            ):
                raise ValueError("cancellation requires explicit authority")
        validate_transition(current, target)
        payload = {
            "task_id": task_id,
            "current_state": current.value,
            "target_state": target.value,
            "reason": reason,
            "evidence": evidence,
            "external_blocker": external_blocker,
        }
        records: list[tuple[str, dict[str, Any], str, None]] = []
        if target == ExecutionState.VERIFIED and checkpoint:
            checkpoint_verification = {
                "checkpoint_id": checkpoint["checkpoint_id"],
                "task_id": task_id,
                "verifier": evidence["verifier"],
                "evidence_digest": checkpoint["evidence_digest"],
                "result": "PASS",
            }
            records.append(
                (
                    "DOMAIN_CHECKPOINT_VERIFIED",
                    checkpoint_verification,
                    self._event_identity(
                        "checkpoint-verified", checkpoint_verification
                    ),
                    None,
                )
            )
        records.append(
            (
                "TASK_STATE_CHANGED",
                payload,
                self._event_identity("task-state", payload),
                None,
            )
        )
        results = self.journal.append_many(records)
        return {
            "appended": any(result.appended for result in results),
            "task_id": task_id,
            "state": target.value,
        }

    def transition_plan(
        self,
        value: str,
        target: ExecutionState,
        *,
        reason: str,
        evidence: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        kind, plan_id = self.resolve_id(value)
        if kind != "plan":
            raise ValueError(f"{value} is not a plan")
        current = ExecutionState(
            self.state()["plans"][plan_id].get("execution_state", "DISCOVERED")
        )
        if target in {
            ExecutionState.VERIFIED,
            ExecutionState.COMPLETE,
            ExecutionState.TERMINAL_CLOSED,
        }:
            tasks = [
                task
                for task in self.state()["tasks"].values()
                if task["plan_id"] == plan_id
            ]
            open_tasks = [
                task["external_id"]
                for task in tasks
                if ExecutionState(task["state"])
                not in {
                    ExecutionState.VERIFIED,
                    ExecutionState.COMPLETE,
                    ExecutionState.CANCELLED,
                    ExecutionState.TERMINAL_CLOSED,
                }
            ]
            if open_tasks:
                raise ValueError(
                    "terminal closure rejected; open tasks: " + ", ".join(sorted(open_tasks))
                )
            missing_evidence = [
                task["external_id"]
                for task in tasks
                if ExecutionState(task["state"]) != ExecutionState.CANCELLED
                and not task.get("evidence")
            ]
            if missing_evidence:
                raise ValueError(
                    "terminal closure rejected; missing evidence: "
                    + ", ".join(sorted(missing_evidence))
                )
            if not tasks and not evidence:
                raise ValueError("terminal closure rejected; plan evidence is required")
        validate_transition(current, target)
        payload = {
            "plan_id": plan_id,
            "current_state": current.value,
            "target_state": target.value,
            "reason": reason,
            "evidence": evidence,
        }
        result = self.journal.append(
            "PLAN_STATE_CHANGED",
            payload,
            event_id=self._event_identity("plan-state", payload),
        )
        return {"appended": result.appended, "plan_id": plan_id, "state": target.value}

    def change_authority(
        self,
        value: str,
        authority_mode: AuthorityMode,
        related_plan_id: str | None = None,
    ) -> dict[str, Any]:
        kind, plan_id = self.resolve_id(value)
        if kind != "plan":
            raise ValueError(f"{value} is not a plan")
        payload = {
            "plan_id": plan_id,
            "authority_mode": authority_mode.value,
            "related_plan_id": related_plan_id,
        }
        result = self.journal.append(
            "AUTHORITY_CHANGED",
            payload,
            event_id=self._event_identity("authority", payload),
        )
        return {"appended": result.appended, **payload}

    def ingest_producer(
        self,
        *,
        state_dir: Path,
        producer: str,
        plan_id: str,
        task_id: str | None,
        source_commit: str,
        evidence_path: Path | None,
        declared_verifier: str,
    ) -> dict[str, Any]:
        plan_kind, resolved_plan_id = self.resolve_id(plan_id)
        if plan_kind != "plan":
            raise ValueError(f"{plan_id} is not a plan")
        resolved_task_id = None
        if task_id:
            task_kind, resolved_task_id = self.resolve_id(task_id)
            if task_kind != "task":
                raise ValueError(f"{task_id} is not a task")
            task = self.state()["tasks"][resolved_task_id]
            if task["plan_id"] != resolved_plan_id:
                raise ValueError("producer task does not belong to producer plan")
        payload = read_checkpoint(
            state_dir=state_dir,
            producer=producer,
            plan_id=resolved_plan_id,
            task_id=resolved_task_id,
            source_commit=source_commit,
            evidence_path=evidence_path,
            declared_verifier=declared_verifier,
        )
        result = self.journal.append(
            "DOMAIN_CHECKPOINT_RECORDED",
            payload,
            event_id=f"producer:{payload['checkpoint_id']}",
        )
        return {"appended": result.appended, **payload}

    def mirror_claim(self, action: str, target_id: str, resource: str, output_digest: str) -> bool:
        payload = {
            "action": action,
            "target_id": target_id,
            "resource": resource,
            "coordination_output_digest": output_digest,
        }
        return self.journal.append(
            "CLAIM_MIRRORED",
            payload,
            event_id=self._event_identity("claim", payload),
        ).appended

    def list_records(self, kind: str) -> list[dict[str, Any]]:
        state = self.state()
        values = state["plans"] if kind == "plans" else state["tasks"]
        return [values[key] for key in sorted(values)]

    def show(self, value: str) -> dict[str, Any]:
        kind, identity = self.resolve_id(value)
        return self.state()[f"{kind}s"][identity]

    def history(self, value: str) -> list[dict[str, Any]]:
        kind, identity = self.resolve_id(value)
        keys = {"plan": {"plan_id"}, "task": {"task_id", "plan_id"}}[kind]
        return [
            event
            for event in self.journal.read()
            if any(event["payload"].get(key) == identity for key in keys)
            or any(
                isinstance(item, dict) and item.get(f"{kind}_id") == identity
                for item in event["payload"].values()
            )
        ]

    def queue(self) -> list[dict[str, Any]]:
        return queue_projection(self.state())

    def explain(self, value: str) -> dict[str, Any]:
        kind, identity = self.resolve_id(value)
        if kind != "task":
            raise ValueError(f"{value} is not a task")
        state = self.state()
        task = state["tasks"][identity]
        runnable = next(
            (item for item in queue_projection(state) if item["task_id"] == identity),
            None,
        )
        if runnable:
            return {**runnable, "runnable": True}
        plan = state["plans"].get(task["plan_id"], {})
        reasons: list[str] = []
        if plan.get("external_claimed"):
            reasons.append(
                f"external occurrence owned by {plan.get('coordination_owner', 'external worktree')}"
            )
        if task["state"] not in {
            ExecutionState.READY.value,
            ExecutionState.PENDING.value,
            ExecutionState.DISCOVERED.value,
        }:
            reasons.append(f"state={task['state']}")
        if task.get("retry_not_before") is not None:
            reasons.append(f"retry_not_before={task['retry_not_before']}")
        if task.get("external_blocker"):
            reasons.append("quarantined external blocker")
        return {
            "task_id": identity,
            "external_id": task["external_id"],
            "runnable": False,
            "reason": ";".join(reasons) or "dependencies or authority not ready",
            "state": task["state"],
        }

    def record_failure(
        self,
        value: str,
        *,
        root_cause: str,
        failure_signature: str,
        transient: bool = True,
        observed_at: float | None = None,
    ) -> dict[str, Any]:
        kind, task_id = self.resolve_id(value)
        if kind != "task":
            raise ValueError(f"{value} is not a task")
        task = self.state()["tasks"][task_id]
        history = task.get("retry_history", [])
        duplicate = any(
            item["root_cause"] == root_cause
            and item["failure_signature"] == failure_signature
            for item in history
        )
        distinct_count = len(
            {
                item["failure_signature"]
                for item in history
                if item["root_cause"] == root_cause
            }
        ) + (0 if duplicate else 1)
        timestamp = observed_at if observed_at is not None else time.time()
        retry_after = timestamp + min(5 * (2 ** max(distinct_count - 1, 0)), 300)
        payload = {
            "task_id": task_id,
            "root_cause": root_cause,
            "failure_signature": failure_signature,
            "transient": transient,
            "observed_at": timestamp,
            "retry_not_before": retry_after,
        }
        result = self.journal.append(
            "TASK_FAILURE_RECORDED",
            payload,
            event_id=self._event_identity("task-failure", payload),
        )
        current = self.state()["tasks"][task_id]
        return {
            "appended": result.appended,
            "task_id": task_id,
            "state": current["state"],
            "retry_count": current["retry_count"],
            "retry_not_before": current["retry_not_before"],
        }

    def release_due_retries(self, *, now: float | None = None) -> dict[str, Any]:
        timestamp = now if now is not None else time.time()
        records: list[tuple[str, dict[str, Any], str, None]] = []
        for task in self.state()["tasks"].values():
            not_before = task.get("retry_not_before")
            if (
                task["state"] == ExecutionState.PENDING.value
                and not_before is not None
                and float(not_before) <= timestamp
            ):
                payload = {"task_id": task["task_id"], "released_at": timestamp}
                records.append(
                    (
                        "TASK_RETRY_READY",
                        payload,
                        self._event_identity(
                            "retry-ready", [task["task_id"], not_before]
                        ),
                        None,
                    )
                )
        results = self.journal.append_many(records)
        return {"released": sum(result.appended for result in results)}
