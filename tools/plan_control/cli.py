from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from .coordination import CoordinationAdapter, CoordinationError
from .engine import PlanControlEngine
from .journal import JournalError
from .models import AuthorityMode, ExecutionState
from .producer import ProducerStateError


EXIT_OK = 0
EXIT_INVALID = 2
EXIT_EMPTY = 3
EXIT_BLOCKED = 4
EXIT_STATE_FAILURE = 5
EXIT_CLAIM_CONFLICT = 6


def _json(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True, default=str))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m tools.plan_control")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--control-root", type=Path)
    parser.add_argument("--local-root", type=Path)
    parser.add_argument("--version", action="store_true")
    sub = parser.add_subparsers(dest="command")
    for name in ("discover", "reconcile", "doctor", "project", "rebuild"):
        sub.add_parser(name)
    listing = sub.add_parser("list")
    listing.add_argument("kind", choices=("plans", "tasks"))
    for name in ("show", "history", "explain"):
        item = sub.add_parser(name)
        item.add_argument("id")
    sub.add_parser("queue")
    sub.add_parser("next")
    claim = sub.add_parser("claim")
    claim.add_argument("id")
    claim.add_argument("--resource")
    claim.add_argument("--takeover-lease")
    claim.add_argument("--takeover-reason")
    heartbeat = sub.add_parser("heartbeat")
    heartbeat.add_argument("--id", default="FF-PLAN-CONTROL-001")
    release = sub.add_parser("release")
    release.add_argument("--id", default="FF-PLAN-CONTROL-001")
    release.add_argument("--resource")
    block = sub.add_parser("block")
    block.add_argument("id")
    block.add_argument("--reason", required=True)
    block.add_argument("--external", action="store_true")
    lifecycle = sub.add_parser("lifecycle")
    lifecycle.add_argument("id")
    lifecycle.add_argument("state", choices=[state.value for state in ExecutionState])
    lifecycle.add_argument("--reason", required=True)
    lifecycle.add_argument("--evidence")
    authority = sub.add_parser("authority")
    authority.add_argument("id")
    authority.add_argument("mode", choices=[mode.value for mode in AuthorityMode])
    authority.add_argument("--related-plan-id")
    task = sub.add_parser("task")
    task_sub = task.add_subparsers(dest="task_action", required=True)
    for action in ("start", "complete", "verify", "reopen", "cancel", "fail"):
        action_parser = task_sub.add_parser(action)
        action_parser.add_argument("id")
        action_parser.add_argument("--reason", default=action)
        action_parser.add_argument("--evidence")
        action_parser.add_argument("--verifier")
        action_parser.add_argument("--authority")
        if action == "fail":
            action_parser.add_argument("--root-cause", required=True)
            action_parser.add_argument("--failure-signature", required=True)
            action_parser.add_argument("--permanent", action="store_true")
            action_parser.add_argument("--observed-at", type=float)
    worktrees = sub.add_parser("worktrees")
    worktree_sub = worktrees.add_subparsers(dest="worktree_action", required=True)
    worktree_sub.add_parser("observe")
    producer = sub.add_parser("producer")
    producer_sub = producer.add_subparsers(dest="producer_action", required=True)
    ingest = producer_sub.add_parser("ingest")
    ingest.add_argument("--plan-id", required=True)
    ingest.add_argument("--task-id")
    ingest.add_argument("--producer", required=True)
    ingest.add_argument("--state-dir", type=Path, required=True)
    ingest.add_argument("--source-commit", required=True)
    ingest.add_argument("--evidence-path", type=Path, required=True)
    ingest.add_argument("--verifier", required=True)
    return parser


def _engine(args: argparse.Namespace) -> PlanControlEngine:
    return PlanControlEngine(
        args.repo,
        control_root=args.control_root,
        local_root=args.local_root,
    )


def _transition_target(action: str) -> ExecutionState:
    return {
        "start": ExecutionState.IN_PROGRESS,
        "complete": ExecutionState.AWAITING_VERIFICATION,
        "verify": ExecutionState.VERIFIED,
        "reopen": ExecutionState.IN_PROGRESS,
        "cancel": ExecutionState.CANCELLED,
    }[action]


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    if args.version:
        from . import __version__

        print(__version__)
        return EXIT_OK
    if not args.command:
        parser.print_help()
        return EXIT_INVALID
    engine = _engine(args)
    try:
        if args.command == "discover":
            result = {"discover": engine.discover(), "projection": engine.project()}
        elif args.command == "reconcile":
            adapter = CoordinationAdapter(args.repo)
            result = engine.reconcile(coordination_status=adapter.status())
        elif args.command == "doctor":
            result = engine.doctor()
            _json(result)
            return EXIT_OK if result["ok"] else EXIT_STATE_FAILURE
        elif args.command in {"project", "rebuild"}:
            result = engine.project()
        elif args.command == "list":
            result = engine.list_records(args.kind)
        elif args.command == "show":
            result = engine.show(args.id)
        elif args.command == "history":
            result = engine.history(args.id)
        elif args.command in {"queue", "next", "explain"}:
            queue = engine.queue()
            if args.command == "next":
                if not queue:
                    states = {task["state"] for task in engine.list_records("tasks")}
                    blocked = states & {
                        ExecutionState.BLOCKED.value,
                        ExecutionState.AWAITING_VERIFICATION.value,
                        ExecutionState.EXTERNALLY_CLAIMED.value,
                        ExecutionState.CLAIMED.value,
                    }
                    _json({"healthy": not blocked, "next": None, "states": sorted(blocked)})
                    return EXIT_BLOCKED if blocked else EXIT_EMPTY
                result = queue[0]
            elif args.command == "explain":
                result = engine.explain(args.id)
                _json(result)
                return EXIT_OK if result["runnable"] else EXIT_BLOCKED
            else:
                if not queue:
                    states = {task["state"] for task in engine.list_records("tasks")}
                    blocked = states & {
                        ExecutionState.BLOCKED.value,
                        ExecutionState.AWAITING_VERIFICATION.value,
                        ExecutionState.EXTERNALLY_CLAIMED.value,
                        ExecutionState.CLAIMED.value,
                    }
                    _json([])
                    return EXIT_BLOCKED if blocked else EXIT_EMPTY
                result = queue
        elif args.command == "claim":
            resource = args.resource or f"logical:plan-control:{args.id}"
            adapter = CoordinationAdapter(args.repo)
            if bool(args.takeover_lease) != bool(args.takeover_reason):
                raise ValueError(
                    "--takeover-lease and --takeover-reason must be supplied together"
                )
            output = (
                adapter.takeover(args.takeover_lease, args.takeover_reason)
                if args.takeover_lease
                else adapter.claim(resource, args.id)
            )
            engine.mirror_claim(
                "claim",
                args.id,
                resource,
                hashlib.sha256(output.encode("utf-8")).hexdigest(),
            )
            result = engine.transition_task(
                args.id, ExecutionState.CLAIMED, reason="coordination claim acquired"
            )
            result.update({"claimed": True, "id": args.id, "resource": resource})
            result["projection"] = engine.project()
        elif args.command == "heartbeat":
            output = CoordinationAdapter(args.repo).heartbeat()
            engine.mirror_claim(
                "heartbeat",
                args.id,
                "logical:mission:FF-PLAN-CONTROL-001",
                hashlib.sha256(output.encode("utf-8")).hexdigest(),
            )
            result = {"heartbeat": True}
        elif args.command == "release":
            output = CoordinationAdapter(args.repo).release(args.resource)
            engine.mirror_claim(
                "release",
                args.id,
                args.resource or "ALL_OWNED",
                hashlib.sha256(output.encode("utf-8")).hexdigest(),
            )
            try:
                task = engine.show(args.id)
            except KeyError:
                task = None
            if task and task.get("state") == ExecutionState.CLAIMED.value:
                result = engine.transition_task(
                    args.id, ExecutionState.READY, reason="coordination claim released"
                )
            else:
                result = {}
            result.update({"released": True, "resource": args.resource or "ALL_OWNED"})
            result["projection"] = engine.project()
        elif args.command == "block":
            result = engine.transition_task(
                args.id,
                ExecutionState.BLOCKED,
                reason=args.reason,
                external_blocker=args.external,
            )
            result["projection"] = engine.project()
        elif args.command == "task":
            if args.task_action == "fail":
                result = engine.record_failure(
                    args.id,
                    root_cause=args.root_cause,
                    failure_signature=args.failure_signature,
                    transient=not args.permanent,
                    observed_at=args.observed_at,
                )
            else:
                evidence = None
                if args.evidence or args.verifier or args.authority:
                    evidence = {
                        "reference": args.evidence,
                        "verifier": args.verifier,
                        "authority": args.authority,
                    }
                result = engine.transition_task(
                    args.id,
                    _transition_target(args.task_action),
                    reason=args.reason,
                    evidence=evidence,
                )
            result["projection"] = engine.project()
        elif args.command == "lifecycle":
            result = engine.transition_plan(
                args.id,
                ExecutionState(args.state),
                reason=args.reason,
                evidence={"reference": args.evidence} if args.evidence else None,
            )
            result["projection"] = engine.project()
        elif args.command == "authority":
            result = engine.change_authority(
                args.id,
                AuthorityMode(args.mode),
                related_plan_id=args.related_plan_id,
            )
            result["projection"] = engine.project()
        elif args.command == "worktrees":
            status = CoordinationAdapter(args.repo).status()
            result = engine.observe_external_worktrees(status)
            result["projection"] = engine.project()
        elif args.command == "producer":
            result = engine.ingest_producer(
                state_dir=args.state_dir,
                producer=args.producer,
                plan_id=args.plan_id,
                task_id=args.task_id,
                source_commit=args.source_commit,
                evidence_path=args.evidence_path,
                declared_verifier=args.verifier,
            )
            result["projection"] = engine.project()
        else:
            parser.error(f"unsupported command: {args.command}")
            return EXIT_INVALID
        _json(result)
        return EXIT_OK
    except CoordinationError as exc:
        _json({"error": str(exc), "kind": "coordination"})
        return exc.exit_code
    except (KeyError, ValueError, ProducerStateError) as exc:
        _json({"error": str(exc), "kind": "invalid"})
        return EXIT_INVALID
    except (JournalError, OSError, json.JSONDecodeError) as exc:
        _json({"error": str(exc), "kind": "state"})
        return EXIT_STATE_FAILURE


if __name__ == "__main__":
    sys.exit(main())
