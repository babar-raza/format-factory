"""Coordination doctor (TC-COORD-005): integrity probe + conformance selftest.

Checks are read-only unless --fix-safe: fix-safe releases orphan leases whose
owner is terminal, reaps, and quarantines malformed rows. It NEVER touches
working-tree files and never deletes coordination history.
"""
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

from . import PROTOCOL_VERSION
from .db import connect, emit_event, ensure_db, get_mode, immediate
from .root import (db_path, is_anchored, resolve_coordination_root,
                   worktree_identity)


def run_doctor(root: Path | None = None, fix_safe: bool = False,
               selftest: bool = False) -> dict:
    root = root or resolve_coordination_root()
    checks: list[dict] = []
    healthy = True

    def check(name: str, ok: bool, detail: str = "", warn: bool = False):
        nonlocal healthy
        if not ok and not warn:
            healthy = False
        checks.append({"check": name,
                       "result": "PASS" if ok else ("WARN" if warn else "FAIL"),
                       "detail": detail})

    dbp = db_path(root)
    check("root-resolved", True, str(root))
    check("root-anchored", is_anchored(), "keyed on git common dir"
          if is_anchored() else "UNANCHORED: no git repo found; leases will"
          " not be shared with repo-anchored agents", warn=not is_anchored())
    onedrive = "onedrive" in str(root).casefold()
    check("root-not-synced", not onedrive,
          "coordination root is under a OneDrive path; set"
          " FF_AGENT_COORDINATION_ROOT to a local directory" if onedrive
          else "not under OneDrive", warn=onedrive)

    if not dbp.exists():
        check("db-present", False,
              f"{dbp} missing (will be created on first register/hook)",
              warn=True)
        return {"healthy": healthy, "root": str(root), "checks": checks,
                "fixes": [], "selftest": None}
    check("db-present", True, str(dbp))

    conn = None
    fixes: list[str] = []
    try:
        # connect() runs PRAGMAs immediately, so a corrupt file raises HERE
        # -- it must be inside the corruption-handling block.
        conn = connect(root)
        integ = conn.execute("PRAGMA integrity_check").fetchone()[0]
        check("db-integrity", integ == "ok", str(integ))
        row = conn.execute(
            "SELECT value FROM schema_meta WHERE key='protocol_version'"
        ).fetchone()
        pv = int(row[0]) if row else -1
        check("protocol-version", pv == PROTOCOL_VERSION,
              f"db={pv} code={PROTOCOL_VERSION}")
        mode = get_mode(conn)
        check("mode-valid", mode in ("off", "advisory", "enforcing"), mode)

        orphans = conn.execute(
            "SELECT l.lease_id, a.status AS owner_status FROM leases l"
            " JOIN agents a ON a.agent_id = l.agent_id"
            " WHERE l.status IN ('ACTIVE','STALE') AND a.status IN"
            " ('COMPLETED','ABANDONED','TAKEN_OVER')").fetchall()
        check("no-orphan-leases", len(orphans) == 0,
              f"{len(orphans)} live leases owned by terminal agents",
              warn=fix_safe)
        malformed = []
        for r in conn.execute("SELECT lease_id, intended_ops FROM leases"):
            try:
                json.loads(r["intended_ops"])
            except (TypeError, ValueError):
                malformed.append(r)
        check("no-malformed-rows", len(malformed) == 0,
              f"{len(malformed)} leases with invalid JSON columns",
              warn=fix_safe)
        open_conflicts = conn.execute(
            "SELECT COUNT(*) AS n FROM conflicts WHERE"
            " resolution_state='OPEN'").fetchone()["n"]
        check("open-conflicts", open_conflicts == 0,
              f"{open_conflicts} open", warn=True)
        stale = conn.execute(
            "SELECT COUNT(*) AS n FROM agents WHERE"
            " status='STALE_SUSPECT'").fetchone()["n"]
        check("stale-candidates", True, f"{stale} agents STALE_SUSPECT")
        runtime_ok = os.access(root / "runtime", os.W_OK)
        check("runtime-writable", runtime_ok, str(root / "runtime"))

        if fix_safe and (orphans or malformed):
            with immediate(conn):
                for o in orphans:
                    conn.execute(
                        "UPDATE leases SET status='RELEASED',"
                        " status_reason='doctor: owner terminal'"
                        " WHERE lease_id=?", (o["lease_id"],))
                    emit_event(conn, "doctor", o["lease_id"],
                               "DOCTOR_RELEASE_ORPHAN", to_status="RELEASED")
                    fixes.append(f"released orphan lease {o['lease_id']}")
                from .db import quarantine_row
                for m in malformed:
                    quarantine_row(conn, "leases", m, "invalid intended_ops")
                    conn.execute(
                        "UPDATE leases SET intended_ops='[]' WHERE lease_id=?",
                        (m["lease_id"],))
                    fixes.append(f"quarantined malformed lease {m['lease_id']}")
    except sqlite3.DatabaseError as exc:
        # Corruption path (OneDrive sync damage etc.): rename aside, re-init.
        # Losing leases is safe by design (re-register + re-claim + recapture);
        # working-tree files are never touched.
        check("db-integrity", False, f"{exc}")
        if fix_safe:
            if conn is not None:
                conn.close()
            from .ids import utcnow
            aside = dbp.with_suffix(
                ".corrupt-" + utcnow().strftime("%Y%m%dT%H%M%S"))
            os.replace(str(dbp), str(aside))
            ensure_db(root)
            fixes.append(f"renamed corrupt db to {aside.name} and re-initialized")
            return {"healthy": False, "root": str(root), "checks": checks,
                    "fixes": fixes, "selftest": None}
    finally:
        try:
            if conn is not None:
                conn.close()
        except Exception:
            pass

    selftest_report = run_selftest(root) if selftest else None
    if selftest_report is not None:
        check("selftest", selftest_report["passed"],
              f"{selftest_report['pass_count']}/{selftest_report['total']}"
              " golden fixtures")
    return {"healthy": healthy, "root": str(root), "checks": checks,
            "fixes": fixes, "selftest": selftest_report}


def run_selftest(root: Path) -> dict:
    """Replay golden hook stdin fixtures through the gate in-process.
    Catches harness hook-schema drift across Claude Code upgrades -- the top
    rerun-consistency risk (plan section 9).

    Fixtures run against a THROWAWAY root: two of them are deliberate
    failure payloads, and their FAIL_OPEN incidents must not pollute the
    real ledger that V195 audits."""
    import shutil
    import tempfile

    from .hooks import gate

    wt_id, wt_path = worktree_identity()
    scratch = Path(tempfile.mkdtemp(prefix="ff-coord-selftest-"))
    root = scratch / "root"
    ensure_db(root)
    fixtures = [
        {"name": "unknown-event-fails-open",
         "payload": {"hook_event_name": "SomethingNew", "session_id": "st-x",
                     "cwd": wt_path},
         "expect_exit": 0},
        {"name": "malformed-json-fails-open",
         "payload": None,  # raw garbage
         "expect_exit": 0},
        {"name": "read-only-bash-passes",
         "payload": {"hook_event_name": "PreToolUse", "session_id": "st-x",
                     "cwd": wt_path, "tool_name": "Bash",
                     "tool_input": {"command": "git status"}},
         "expect_exit": 0},
        {"name": "local-path-fast-path",
         "payload": {"hook_event_name": "PreToolUse", "session_id": "st-x",
                     "cwd": wt_path, "tool_name": "Write",
                     "tool_input": {"file_path":
                                    str(Path(wt_path) / ".local" / "x.json")}},
         "expect_exit": 0},
    ]
    results = []
    try:
        for f in fixtures:
            raw = ("this is not json" if f["payload"] is None
                   else json.dumps(f["payload"]))
            code = gate.process(raw, root=root)
            results.append({"fixture": f["name"], "exit": code,
                            "expected": f["expect_exit"],
                            "pass": code == f["expect_exit"]})
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    passed = all(r["pass"] for r in results)
    return {"passed": passed, "total": len(results),
            "pass_count": sum(1 for r in results if r["pass"]),
            "results": results}
