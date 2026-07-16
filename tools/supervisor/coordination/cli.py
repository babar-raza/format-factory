"""Coordination CLI (TC-COORD-005).

    python -m tools.supervisor.coordination <verb> [...]

ASCII-only output. Exit codes: 0 ok / 1 error / 2 conflict / 3 not-registered
/ 4 stale / 5 baseline-drift-preserve / 6 takeover-denied.
`status` exits 1 while OPEN conflicts exist (conflicts are not silently
ignorable). Identity resolves from --agent/--token, FF_AGENT_ID/FF_AGENT_TOKEN,
or runtime token files under <root>/runtime/.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .conflicts import ConflictLog
from .db import connect, ensure_db, get_mode, set_mode
from .errors import CoordinationError
from .leases import LeaseManager
from .preflight import preflight, record_write, resolve_identity
from .registry import AgentRegistry
from .root import is_anchored, resolve_coordination_root, worktree_identity


def _emit(args, ok: bool, exit_code: int, verb: str, data=None, error=None):
    if getattr(args, "json", False):
        print(json.dumps({"ok": ok, "exit": exit_code, "verb": verb,
                          "data": data, "error": error},
                         default=str, indent=2))
    else:
        if error:
            print(f"[{verb}] ERROR: {error}", file=sys.stderr)
        elif isinstance(data, str):
            print(f"[{verb}] {data}")
        elif data is not None:
            print(json.dumps(data, default=str, indent=2))
    return exit_code


def _identity(args, registry: AgentRegistry):
    return resolve_identity(registry, agent_id=getattr(args, "agent", None),
                            token=getattr(args, "token", None),
                            session_id=getattr(args, "session", None))


def _require_identity(args, registry: AgentRegistry) -> tuple[str, str]:
    ident = _identity(args, registry)
    if ident is None:
        raise CoordinationError_NotRegistered()
    return ident


def CoordinationError_NotRegistered():
    from .errors import NotRegistered
    return NotRegistered(
        "no agent identity; pass --agent/--token or register first")


def status_snapshot(root: Path, include_done: bool = False) -> dict:
    conn = connect(root)
    try:
        live = "('ACTIVE','IDLE','STALE_SUSPECT')"
        agents = [dict(r) for r in conn.execute(
            "SELECT agent_id, provider, agent_type, task_id, status,"
            " last_heartbeat, heartbeat_ttl_s, worktree_path, pid,"
            " claude_session_id FROM agents" +
            ("" if include_done else f" WHERE status IN {live}") +
            " ORDER BY started_at DESC LIMIT 200").fetchall()]
        for a in agents:
            a.pop("agent_token_hash", None)
        leases = [dict(r) for r in conn.execute(
            "SELECT lease_id, agent_id, task_id, resource_display,"
            " resource_key, mode, origin, status, last_renewed_at,"
            " ttl_seconds FROM leases WHERE status IN ('ACTIVE','STALE')"
            " ORDER BY acquired_at DESC LIMIT 500").fetchall()]
        conflicts = [dict(r) for r in conn.execute(
            "SELECT * FROM conflicts WHERE resolution_state='OPEN'"
            " ORDER BY detected_at").fetchall()]
        recent_done = [dict(r) for r in conn.execute(
            "SELECT agent_id, provider, task_id, status, last_heartbeat"
            " FROM agents WHERE status IN"
            " ('COMPLETED','ABANDONED','TAKEN_OVER')"
            " ORDER BY last_heartbeat DESC LIMIT 10").fetchall()]
        stale_candidates = [a["agent_id"] for a in agents
                            if a["status"] == "STALE_SUSPECT"]
        return {
            "mode": get_mode(conn),
            "active_agents": agents,
            "live_leases": leases,
            "blocked_resources": [l["resource_key"] for l in leases
                                  if l["status"] == "STALE"],
            "stale_candidates": stale_candidates,
            "open_conflicts": conflicts,
            "recently_completed": recent_done,
        }
    finally:
        conn.close()


def _print_status_text(snap: dict) -> None:
    print(f"mode: {snap['mode']}")
    print(f"agents ({len(snap['active_agents'])}):")
    for a in snap["active_agents"]:
        print(f"  {a['agent_id']}  [{a['status']}]  provider={a['provider']}"
              f" task={a['task_id'] or '-'} hb={a['last_heartbeat']}")
    print(f"leases ({len(snap['live_leases'])}):")
    for l in snap["live_leases"]:
        print(f"  {l['lease_id']}  [{l['status']}] {l['mode']:15s}"
              f" {l['resource_display']}  owner={l['agent_id']}"
              f" origin={l['origin']}")
    if snap["stale_candidates"]:
        print(f"stale candidates: {', '.join(snap['stale_candidates'])}")
    print(f"open conflicts ({len(snap['open_conflicts'])}):")
    for c in snap["open_conflicts"]:
        print(f"  {c['conflict_id']}  {c['conflict_type']:16s}"
              f" {c['resource_display']}  owner={c['apparent_owner'] or '?'}"
              f"  next: {c['safe_action']}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m tools.supervisor.coordination",
        description="Multi-agent shared-state coordination")
    p.add_argument("--root", help="coordination root override")
    p.add_argument("--json", action="store_true")
    p.add_argument("--agent", help="agent id")
    p.add_argument("--token", help="agent token")
    p.add_argument("--session", help="harness session id")
    sub = p.add_subparsers(dest="verb", required=True)

    reg = sub.add_parser("register")
    reg.add_argument("--provider", required=True)
    reg.add_argument("--agent-type", default="interactive",
                     choices=["interactive", "headless", "subagent"])
    reg.add_argument("--mode", dest="execution_mode", default="interactive",
                     choices=["interactive", "headless", "ci"])
    reg.add_argument("--task")
    reg.add_argument("--plan")
    reg.add_argument("--scope", action="append", default=[])
    reg.add_argument("--ttl", type=int)

    for name in ("status", "who"):
        s = sub.add_parser(name)
        s.add_argument("--all", action="store_true")

    c = sub.add_parser("claim")
    c.add_argument("--resource", action="append", required=True)
    c.add_argument("--mode", dest="lease_mode", default="EXCLUSIVE_WRITE",
                   choices=["EXCLUSIVE_WRITE", "OBSERVE", "APPEND", "SRSW"])
    c.add_argument("--ops", default="edit")
    c.add_argument("--ttl", type=int, default=3600)
    c.add_argument("--task")

    ck = sub.add_parser("check")
    ck.add_argument("--resource", action="append", required=True)
    ck.add_argument("--mode", dest="lease_mode", default="EXCLUSIVE_WRITE")

    pf = sub.add_parser("preflight")
    pf.add_argument("--file", required=True)
    pf.add_argument("--op", default="edit")

    hb = sub.add_parser("heartbeat")
    hb.add_argument("--renew-leases", action="store_true")

    rel = sub.add_parser("release")
    rel.add_argument("--lease", action="append", default=[])
    rel.add_argument("--all", action="store_true")

    comp = sub.add_parser("complete")
    comp.add_argument("--reason")

    ab = sub.add_parser("abandon")
    ab.add_argument("--reason", required=True)

    rw = sub.add_parser("record-write")
    rw.add_argument("--file", required=True)
    rw.add_argument("--op", default="edit")

    cf = sub.add_parser("conflicts")
    cfsub = cf.add_subparsers(dest="conflicts_cmd", required=True)
    cfl = cfsub.add_parser("list")
    cfl.add_argument("--all", action="store_true")
    cfr = cfsub.add_parser("resolve")
    cfr.add_argument("--id", required=True)
    cfr.add_argument("--state", required=True,
                     choices=["ACKNOWLEDGED", "RESOLVED", "WONT_FIX"])
    cfr.add_argument("--note", required=True)

    tk = sub.add_parser("takeover")
    tk.add_argument("--lease", required=True)
    tk.add_argument("--reason", required=True)

    ren = sub.add_parser("renew")
    ren.add_argument("--lease", action="append", default=[])
    ren.add_argument("--rebaseline", action="store_true")

    md = sub.add_parser("mode")
    mdsub = md.add_subparsers(dest="mode_cmd", required=True)
    mdsub.add_parser("get")
    mds = mdsub.add_parser("set")
    mds.add_argument("--to", required=True,
                     choices=["off", "advisory", "enforcing"])
    mds.add_argument("--reason", required=True)

    # SFC-GAP-C (2026-07-17): per-check mode, independent of the global
    # `mode` above -- lets a NEW check (e.g. skill_resolution) roll out
    # advisory->enforcing on its own schedule without touching the already-
    # proven, already-enforcing global coordination checks.
    cm = sub.add_parser("check-mode")
    cmsub = cm.add_subparsers(dest="check_mode_cmd", required=True)
    cmg = cmsub.add_parser("get")
    cmg.add_argument("--check", required=True)
    cms = cmsub.add_parser("set")
    cms.add_argument("--check", required=True)
    cms.add_argument("--to", required=True, choices=["advisory", "enforcing"])
    cms.add_argument("--reason", required=True)

    ar = sub.add_parser("advisory-report")
    ar.add_argument("--check", required=True)
    ar.add_argument("--window-hours", type=float, default=None)

    pc = sub.add_parser("precommit-check")
    pc.add_argument("--staged-file", action="append", default=[])
    pc.add_argument("--repo")

    dr = sub.add_parser("doctor")
    dr.add_argument("--fix-safe", action="store_true")
    dr.add_argument("--selftest", action="store_true")

    gr = sub.add_parser("guard-run")
    gr.add_argument("--generator-id", required=True)
    gr.add_argument("--manifest-file", required=True)
    gr.add_argument("command", nargs=argparse.REMAINDER)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root) if args.root else resolve_coordination_root()
    registry = AgentRegistry(root)
    lm = LeaseManager(root)
    clog = ConflictLog(root)
    verb = args.verb
    try:
        if verb == "register":
            ensure_db(root)
            ra = registry.register(
                args.provider, agent_type=args.agent_type,
                execution_mode=args.execution_mode, session_id=args.session,
                task_id=args.task, plan_authority=args.plan,
                declared_scope=args.scope, heartbeat_ttl_s=args.ttl)
            data = {"agent_id": ra.agent_id, "token": ra.token,
                    "resumed": ra.resumed,
                    "runtime_file": str(registry.runtime_file(ra.agent_id)),
                    "export_hint": (f"FF_AGENT_ID={ra.agent_id} "
                                    f"FF_AGENT_TOKEN={ra.token}")}
            return _emit(args, True, 0, verb, data)

        if verb in ("status", "who"):
            ensure_db(root)
            snap = status_snapshot(root, include_done=args.all)
            code = 1 if snap["open_conflicts"] else 0
            if args.json:
                return _emit(args, code == 0, code, "status", snap)
            _print_status_text(snap)
            if code:
                print("NOTE: open conflicts require resolution"
                      " (conflicts resolve --id ... )", file=sys.stderr)
            return code

        if verb == "claim":
            aid, tok = _require_identity(args, registry)
            leases = lm.claim(aid, tok, args.resource, mode=args.lease_mode,
                              intended_ops=args.ops.split(","),
                              ttl_seconds=args.ttl, task_id=args.task)
            data = [{"lease_id": l["lease_id"], "resource": l["resource_key"],
                     "mode": l["mode"], "reused": l.get("reused", False)}
                    for l in leases]
            return _emit(args, True, 0, verb, data)

        if verb == "check":
            conflicts = lm.check(args.resource, mode=args.lease_mode)
            code = 2 if conflicts else 0
            return _emit(args, code == 0, code, verb,
                         {"conflicts": conflicts})

        if verb == "preflight":
            aid_tok = _identity(args, registry)
            kwargs = {}
            if aid_tok:
                kwargs = {"agent_id": aid_tok[0], "token": aid_tok[1]}
            elif args.session:
                kwargs = {"session_id": args.session}
            res = preflight(args.file, args.op, root=root, **kwargs)
            data = {"decision": res.decision, "reason": res.reason,
                    "lease_id": res.lease_id,
                    "classification": res.classification,
                    "conflict_id": res.conflict_id,
                    "auto_claimed": res.auto_claimed}
            return _emit(args, res.allowed, res.exit_code, verb, data,
                         None if res.allowed else res.reason)

        if verb == "heartbeat":
            aid, tok = _require_identity(args, registry)
            registry.heartbeat(aid, tok)
            renewed = lm.renew(aid, tok) if args.renew_leases else 0
            return _emit(args, True, 0, verb, {"renewed_leases": renewed})

        if verb == "renew":
            aid, tok = _require_identity(args, registry)
            n = lm.renew(aid, tok, args.lease or None)
            if args.rebaseline:
                from .baselines import BaselineTracker
                from .db import connect as _c, immediate as _imm
                from .root import worktree_identity as _wi
                conn = _c(root)
                try:
                    with _imm(conn):
                        _, wt_path = _wi()
                        tracker = BaselineTracker()
                        sql = ("SELECT l.lease_id, b.file_key, b.file_display"
                               " FROM leases l JOIN lease_baselines b ON"
                               " b.lease_id = l.lease_id WHERE l.agent_id=?"
                               " AND l.status='ACTIVE'")
                        params = [aid]
                        if args.lease:
                            sql += (" AND l.lease_id IN ("
                                    + ",".join("?" * len(args.lease)) + ")")
                            params += args.lease
                        rows = conn.execute(sql, params).fetchall()
                        for r in rows:
                            tracker.capture(conn, r["lease_id"],
                                            [(r["file_key"],
                                              r["file_display"])], wt_path)
                finally:
                    conn.close()
            return _emit(args, True, 0, verb,
                         {"renewed": n, "rebaselined": bool(args.rebaseline)})

        if verb == "release":
            aid, tok = _require_identity(args, registry)
            n = lm.release(aid, tok, args.lease or None,
                           release_all=args.all)
            return _emit(args, True, 0, verb, {"released": n})

        if verb == "complete":
            aid, tok = _require_identity(args, registry)
            n = registry.complete(aid, tok, args.reason)
            return _emit(args, True, 0, verb, {"released_leases": n})

        if verb == "abandon":
            aid, tok = _require_identity(args, registry)
            n = registry.abandon(aid, tok, args.reason)
            return _emit(args, True, 0, verb, {"released_leases": n})

        if verb == "record-write":
            aid, tok = _require_identity(args, registry)
            payload = record_write(args.file, args.op, root=root,
                                   agent_id=aid, token=tok, source="cli")
            return _emit(args, True, 0, verb, payload)

        if verb == "conflicts":
            if args.conflicts_cmd == "list":
                rows = clog.list_conflicts(open_only=not args.all)
                return _emit(args, True, 0, verb, rows)
            ident = _identity(args, registry)
            resolver = ident[0] if ident else "operator"
            clog.resolve(args.id, resolver, args.state, args.note)
            return _emit(args, True, 0, verb, {"resolved": args.id,
                                               "state": args.state})

        if verb == "takeover":
            aid, tok = _require_identity(args, registry)
            lease = lm.takeover(aid, tok, args.lease, args.reason)
            return _emit(args, True, 0, verb,
                         {"new_lease": lease["lease_id"],
                          "resource": lease["resource_key"],
                          "note": "baselines will be recaptured on first"
                                  " preflight before any write"})

        if verb == "mode":
            ensure_db(root)
            conn = connect(root)
            try:
                if args.mode_cmd == "get":
                    return _emit(args, True, 0, verb,
                                 {"mode": get_mode(conn)})
                ident = _identity(args, registry)
                actor = ident[0] if ident else "operator"
                set_mode(conn, args.to, actor, args.reason)
                return _emit(args, True, 0, verb, {"mode": args.to})
            finally:
                conn.close()

        if verb == "check-mode":
            from .db import get_check_mode, set_check_mode
            ensure_db(root)
            conn = connect(root)
            try:
                if args.check_mode_cmd == "get":
                    return _emit(args, True, 0, verb,
                                 {"check": args.check,
                                  "mode": get_check_mode(conn, args.check)})
                ident = _identity(args, registry)
                actor = ident[0] if ident else "operator"
                set_check_mode(conn, args.check, args.to, actor, args.reason)
                return _emit(args, True, 0, verb,
                             {"check": args.check, "mode": args.to})
            finally:
                conn.close()

        if verb == "advisory-report":
            from .advisory_analyzer import analyze
            report = analyze(root, args.check, args.window_hours)
            return _emit(args, True, 0, verb, report)

        if verb == "precommit-check":
            from .precommit import precommit_check
            report = precommit_check(root=root,
                                     staged_files=args.staged_file or None,
                                     repo=args.repo)
            code = 0 if report["ok"] else 2
            return _emit(args, report["ok"], code, verb, report,
                         None if report["ok"] else "; ".join(
                             v["message"] for v in report["violations"]))

        if verb == "doctor":
            from .doctor import run_doctor
            report = run_doctor(root, fix_safe=args.fix_safe,
                                selftest=args.selftest)
            code = 0 if report["healthy"] else 1
            return _emit(args, report["healthy"], code, verb, report)

        if verb == "guard-run":
            from .generator_guard import guard_run_cli
            return guard_run_cli(root, args.generator_id, args.manifest_file,
                                 args.command, registry, lm, emit=lambda
                                 ok, code, data, err=None:
                                 _emit(args, ok, code, verb, data, err))

        return _emit(args, False, 1, verb, None, f"unhandled verb: {verb}")
    except CoordinationError as exc:
        return _emit(args, False, exc.exit_code, verb, None, str(exc))
    except Exception as exc:  # malformed state must not traceback to agents
        return _emit(args, False, 1, verb, None,
                     f"{type(exc).__name__}: {exc}")
