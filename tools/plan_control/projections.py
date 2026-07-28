from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from .journal import canonical_json
from .models import ExecutionState, TERMINAL_STATES


def empty_state() -> dict[str, Any]:
    return {
        "plans": {},
        "tasks": {},
        "aliases": {},
        "source_items": {},
        "gaps": {},
        "claims": [],
        "domain_checkpoints": [],
        "verified_plan_checkpoints": [],
        "journal_head": "GENESIS",
    }


def reduce_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    state = empty_state()
    for event in events:
        kind = event["event_type"]
        # Reducers own their materialized objects.  EventJournal caches verified
        # event dictionaries, so retaining nested payload references here would
        # let evidence/checkpoint updates mutate the authoritative replay input
        # and make a second reduction produce a different projection.
        payload = copy.deepcopy(event["payload"])
        if kind == "PLAN_UPSERTED":
            plan = dict(payload["plan"])
            existing = state["plans"].get(plan["plan_id"], {})
            occurrences = existing.get("occurrences", [])
            plan["aliases"] = sorted(
                set(existing.get("aliases", [])) | set(plan.get("aliases", []))
            )
            plan["occurrences"] = occurrences
            state["plans"][plan["plan_id"]] = plan
            for alias in plan.get("aliases", []):
                normalized = alias.strip().lower()
                owner = state["aliases"].get(normalized)
                if owner and owner != plan["plan_id"]:
                    state["gaps"][f"alias:{normalized}"] = {
                        "kind": "DUPLICATE_ALIAS",
                        "alias": alias,
                        "plan_ids": sorted({owner, plan["plan_id"]}),
                        "state": "OPEN",
                    }
                else:
                    state["aliases"][normalized] = plan["plan_id"]
        elif kind == "OCCURRENCE_OBSERVED":
            plan = state["plans"].setdefault(payload["plan_id"], {"plan_id": payload["plan_id"]})
            occurrence = payload["occurrence"]
            by_key = {
                (item.get("path"), item.get("branch"), item.get("commit")): item
                for item in plan.setdefault("occurrences", [])
            }
            by_key[(occurrence.get("path"), occurrence.get("branch"), occurrence.get("commit"))] = occurrence
            plan["occurrences"] = [by_key[key] for key in sorted(by_key, key=str)]
        elif kind == "PLAN_EXTERNAL_CLAIMED":
            plan = state["plans"].setdefault(payload["plan_id"], {"plan_id": payload["plan_id"]})
            plan["external_claimed"] = bool(payload["claimed"])
            plan["coordination_owner"] = payload.get("coordination_owner")
        elif kind == "WORKTREE_SNAPSHOT_RECORDED":
            active = {
                (item["path"], item.get("branch"), item.get("commit"))
                for item in payload["worktrees"]
            }
            for plan in state["plans"].values():
                for occurrence in plan.get("occurrences", []):
                    if occurrence.get("canonical"):
                        continue
                    occurrence["active"] = (
                        occurrence.get("worktree_path"),
                        occurrence.get("branch"),
                        occurrence.get("commit"),
                    ) in active
        elif kind == "PLAN_STATE_CHANGED":
            plan = state["plans"][payload["plan_id"]]
            plan["execution_state"] = payload["target_state"]
            plan["last_reason"] = payload.get("reason")
        elif kind == "TASK_UPSERTED":
            task = dict(payload["task"])
            existing = state["tasks"].get(task["task_id"], {})
            for field in (
                "evidence",
                "retry_count",
                "retry_history",
                "retry_not_before",
                "external_blocker",
            ):
                if field in existing:
                    task[field] = existing[field]
            if existing.get("_runtime_override"):
                task["state"] = existing["state"]
                task["_runtime_override"] = True
            state["tasks"][task["task_id"]] = task
        elif kind == "TASK_STATE_CHANGED":
            task = state["tasks"][payload["task_id"]]
            task["state"] = payload["target_state"]
            task["last_reason"] = payload.get("reason")
            task["_runtime_override"] = True
            task["external_blocker"] = bool(payload.get("external_blocker", False))
            if payload.get("evidence"):
                task.setdefault("evidence", []).append(payload["evidence"])
        elif kind == "TASK_FAILURE_RECORDED":
            task = state["tasks"][payload["task_id"]]
            history = task.setdefault("retry_history", [])
            signature = payload["failure_signature"]
            root_cause = payload["root_cause"]
            if not any(
                item["root_cause"] == root_cause
                and item["failure_signature"] == signature
                for item in history
            ):
                history.append(payload)
            distinct = {
                item["failure_signature"]
                for item in history
                if item["root_cause"] == root_cause
            }
            task["retry_count"] = len(history)
            task["_runtime_override"] = True
            if len(distinct) >= 3 or not payload.get("transient", True):
                task["state"] = ExecutionState.BLOCKED.value
                task["retry_not_before"] = None
                task["last_reason"] = f"failure quarantine:{root_cause}"
            else:
                task["state"] = ExecutionState.PENDING.value
                task["retry_not_before"] = payload["retry_not_before"]
                task["last_reason"] = f"bounded retry:{root_cause}"
        elif kind == "TASK_RETRY_READY":
            task = state["tasks"][payload["task_id"]]
            task["state"] = ExecutionState.READY.value
            task["retry_not_before"] = None
            task["_runtime_override"] = True
        elif kind == "SOURCE_ITEM_UPSERTED":
            state["source_items"][payload["source_item"]["source_item_id"]] = payload["source_item"]
        elif kind == "GAP_RECORDED":
            state["gaps"][payload["gap_id"]] = payload
        elif kind == "DOMAIN_CHECKPOINT_RECORDED":
            if payload not in state["domain_checkpoints"]:
                state["domain_checkpoints"].append(payload)
        elif kind == "DOMAIN_CHECKPOINT_VERIFIED":
            for checkpoint in state["domain_checkpoints"]:
                if checkpoint["checkpoint_id"] == payload["checkpoint_id"]:
                    checkpoint["verified"] = payload["result"] == "PASS"
                    checkpoint["verification"] = payload
                    break
        elif kind == "PLAN_CHECKPOINT_RECORDED":
            if payload not in state["verified_plan_checkpoints"]:
                state["verified_plan_checkpoints"].append(payload)
        elif kind == "CLAIM_MIRRORED":
            if payload not in state["claims"]:
                state["claims"].append(payload)
        elif kind == "AUTHORITY_CHANGED":
            state["plans"][payload["plan_id"]]["authority_mode"] = payload["authority_mode"]
            state["plans"][payload["plan_id"]]["related_plan_id"] = payload.get("related_plan_id")
        state["journal_head"] = event["event_hash"]
    return state


def queue_projection(state: dict[str, Any]) -> list[dict[str, Any]]:
    severity = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    authority = {"CANONICAL": 0, "CHILD": 1, "ADVISORY": 2, "SUPERSEDED": 3, "ARCHIVED": 4}
    complete = {
        task_id
        for task_id, task in state["tasks"].items()
        if ExecutionState(task["state"]) in TERMINAL_STATES
    }
    queue: list[dict[str, Any]] = []
    for task in state["tasks"].values():
        plan = state["plans"].get(task["plan_id"], {})
        task_state = ExecutionState(task["state"])
        if task_state not in {ExecutionState.READY, ExecutionState.PENDING, ExecutionState.DISCOVERED}:
            continue
        if task.get("retry_not_before") is not None:
            continue
        if plan.get("external_claimed"):
            continue
        if plan.get("execution_state") == ExecutionState.BLOCKED.value:
            continue
        unmet = sorted(set(task.get("dependencies", [])) - complete)
        if unmet:
            continue
        created_at = str(task.get("created_at") or "9999-12-31T23:59:59Z")
        score = (
            severity.get(task.get("severity", "MEDIUM"), 2),
            created_at,
            authority.get(plan.get("authority_mode", "CHILD"), 1),
            int(task.get("retry_count", 0)),
            task["task_id"],
        )
        queue.append(
            {
                "task_id": task["task_id"],
                "external_id": task["external_id"],
                "plan_id": task["plan_id"],
                "title": task["title"],
                "score": list(score),
                "reason": (
                    f"severity={task.get('severity', 'MEDIUM')};"
                    f"age={created_at};"
                    f"authority={plan.get('authority_mode', 'CHILD')};"
                    f"retries={task.get('retry_count', 0)};dependencies=ready"
                ),
            }
        )
    return sorted(queue, key=lambda item: tuple(item["score"]))


def projection_documents(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    queue = queue_projection(state)
    source_items = list(state["source_items"].values())
    still_open = sum(item.get("disposition") == "STILL_OPEN" for item in source_items)
    registry = {
        "schema": "format-factory/plan-control-registry@1",
        "generated_by": "codex",
        "journal_head": state["journal_head"],
        "plans": [state["plans"][key] for key in sorted(state["plans"])],
        "tasks": [state["tasks"][key] for key in sorted(state["tasks"])],
        "aliases": dict(sorted(state["aliases"].items())),
        "gaps": [state["gaps"][key] for key in sorted(state["gaps"])],
        "verified_plan_checkpoints": state["verified_plan_checkpoints"],
        "source_accounting": {
            "total": len(source_items),
            "still_open": still_open,
            "disposed": len(source_items) - still_open,
        },
    }
    return {
        "registry.json": registry,
        "queue.json": {
            "schema": "format-factory/plan-control-queue@1",
            "generated_by": "codex",
            "journal_head": state["journal_head"],
            "items": queue,
        },
        "status.json": {
            "schema": "format-factory/plan-control-status@1",
            "generated_by": "codex",
            "journal_head": state["journal_head"],
            "plan_count": len(state["plans"]),
            "task_count": len(state["tasks"]),
            "runnable_count": len(queue),
            "gap_count": len(state["gaps"]),
            "source_item_count": len(source_items),
            "source_items_still_open": still_open,
        },
    }


def projection_digest(documents: dict[str, dict[str, Any]]) -> str:
    return hashlib.sha256(canonical_json(documents).encode("utf-8")).hexdigest()


def write_projections(root: Path, documents: dict[str, dict[str, Any]]) -> str:
    root.mkdir(parents=True, exist_ok=True)
    for name, document in documents.items():
        destination = root / name
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        temporary.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        os.replace(temporary, destination)
    return projection_digest(documents)
