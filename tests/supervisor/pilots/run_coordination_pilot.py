"""Multi-agent coordination pilot -- 16 proofs (TC-COORD-011).

Mission AGENT-COORD-2026-07-15 (plans/.claude/lazy-hugging-lovelace.md).

Standalone evidence-producing pilot following the repo convention
(tests/supervisor/pilots/run_pilot_a.py): [PASS]/[FAIL] per proof, sandbox
state only (temp dirs + temp coordination roots -- NEVER the real repo
working tree or the real coordination DB), evidence JSONs written to
reports/coordination/pilot-evidence/coordination-pilot-NN.json.

Cast per scenario: Agent A (claude-code, src/python/fods/**),
Agent B (codex, disjoint tools/readme_sync/**), Agent C (overlapping A).

Run:  .venv/Scripts/python tests/supervisor/pilots/run_coordination_pilot.py
Exit: 0 = all proofs PASS, 1 = any FAIL.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from datetime import timedelta
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from coordination import db as cdb  # noqa: E402
from coordination.baselines import sha256_file  # noqa: E402
from coordination.conflicts import ConflictLog  # noqa: E402
from coordination.errors import (GeneratorBlocked, LeaseConflict,  # noqa: E402
                                 LeaseStale, TakeoverDenied)
from coordination.generator_guard import guarded_generation  # noqa: E402
from coordination.hooks import gate  # noqa: E402
from coordination.ids import iso, utcnow  # noqa: E402
from coordination.leases import LeaseManager  # noqa: E402
from coordination.precommit import precommit_check  # noqa: E402
from coordination.preflight import preflight, record_write  # noqa: E402
from coordination.registry import AgentRegistry  # noqa: E402

EVIDENCE_DIR = _REPO / "reports" / "coordination" / "pilot-evidence"


def future(seconds: int):
    return lambda: iso(utcnow() + timedelta(seconds=seconds))


class Sandbox:
    """Fresh coordination root + fake worktree per scenario."""

    def __init__(self, base: Path, name: str, real_git: bool = False):
        self.root = base / name / "coord"
        self.repo = base / name / "repo"
        if real_git:
            self.repo.mkdir(parents=True)
            subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True,
                           timeout=30)
            subprocess.run(["git", "config", "user.email", "pilot@ff"],
                           cwd=self.repo, check=True, timeout=30)
            subprocess.run(["git", "config", "user.name", "pilot"],
                           cwd=self.repo, check=True, timeout=30)
        else:
            (self.repo / ".git").mkdir(parents=True)
        for d in ("src/python/fods", "tools/readme_sync", "out"):
            (self.repo / d).mkdir(parents=True, exist_ok=True)
        (self.repo / "src/python/fods/model.py").write_text(
            "model = 1\n", encoding="utf-8")
        (self.repo / "tools/readme_sync/run.py").write_text(
            "run = 1\n", encoding="utf-8")
        cdb.ensure_db(self.root)

    def registry(self, now_fn=None):
        kw = {"now_fn": now_fn} if now_fn else {}
        return AgentRegistry(self.root, start=self.repo, **kw)

    def leases(self, now_fn=None):
        kw = {"now_fn": now_fn} if now_fn else {}
        return LeaseManager(self.root, start=self.repo, **kw)

    def payload(self, event: str, session="sess-pilot", **kw) -> str:
        return json.dumps({"hook_event_name": event, "session_id": session,
                           "cwd": str(self.repo), **kw})

    def set_mode(self, mode: str):
        conn = cdb.connect(self.root)
        try:
            cdb.set_mode(conn, mode, "pilot", "pilot scenario")
        finally:
            conn.close()

    def query(self, sql: str, params=()):
        conn = cdb.connect(self.root)
        try:
            return [dict(r) for r in conn.execute(sql, params).fetchall()]
        finally:
            conn.close()

    def live_leases(self) -> int:
        return self.query("SELECT COUNT(*) AS n FROM leases WHERE status IN"
                          " ('ACTIVE','STALE')")[0]["n"]


# ---------------------------------------------------------------------------
# Pilots. Each returns (ok: bool, evidence: dict).
# ---------------------------------------------------------------------------

def pilot_01_unregistered_write_blocked(base: Path):
    sb = Sandbox(base, "p01")
    sb.set_mode("enforcing")
    # No session_id -> identity cannot be bound -> enforcing blocks.
    payload = json.dumps({"hook_event_name": "PreToolUse", "session_id": "",
                          "cwd": str(sb.repo), "tool_name": "Write",
                          "tool_input": {"file_path": str(
                              sb.repo / "src/python/fods/model.py")}})
    code = gate.process(payload, root=sb.root)
    return code == 2, {"exit_code": code,
                       "expectation": "write without bindable identity"
                                      " exits 2 in enforcing mode"}


def pilot_02_disjoint_agents_parallel(base: Path):
    sb = Sandbox(base, "p02")
    reg = sb.registry()
    a = reg.register("claude-code", task_id="TC-A")
    b = reg.register("codex", task_id="TC-B")
    results = {}

    def work(name, ra, resource, target):
        lm = sb.leases()
        lm.claim(ra.agent_id, ra.token, [resource])
        res = preflight(target, root=sb.root, start=sb.repo,
                        agent_id=ra.agent_id, token=ra.token)
        (sb.repo / target).write_text(f"written by {name}\n",
                                      encoding="utf-8")
        record_write(target, root=sb.root, start=sb.repo,
                     agent_id=ra.agent_id, token=ra.token, source="cli")
        results[name] = res.allowed

    t1 = threading.Thread(target=work, args=(
        "A", a, "src/python/fods", "src/python/fods/model.py"))
    t2 = threading.Thread(target=work, args=(
        "B", b, "tools/readme_sync", "tools/readme_sync/run.py"))
    t1.start(); t2.start(); t1.join(30); t2.join(30)
    open_conflicts = ConflictLog(sb.root).open_count()
    visible = sb.query("SELECT agent_id, task_id, status FROM agents")
    ok = (results.get("A") and results.get("B") and open_conflicts == 0
          and len(visible) == 2)
    return ok, {"a_allowed": results.get("A"), "b_allowed": results.get("B"),
                "open_conflicts": open_conflicts,
                "mutual_visibility": visible}


def pilot_03_overlapping_claim_rejected(base: Path):
    sb = Sandbox(base, "p03")
    reg = sb.registry()
    a = reg.register("claude-code", task_id="TC-A")
    c = reg.register("claude-code", task_id="TC-C")
    lm = sb.leases()
    lm.claim(a.agent_id, a.token, ["src/python/fods"])
    try:
        lm.claim(c.agent_id, c.token, ["src/python/fods/model.py"])
        return False, {"error": "overlap not rejected"}
    except LeaseConflict as exc:
        return exc.holder_agent_id == a.agent_id, {
            "holder": exc.holder_agent_id, "lease": exc.holder_lease_id,
            "parent_child": "dir lease blocked contained-file claim"}


def pilot_04_claim_race_single_winner(base: Path):
    sb = Sandbox(base, "p04")
    reg = sb.registry()
    agents = [reg.register("claude-code", task_id=f"TC-{i}")
              for i in range(10)]
    wins, losses = [], []

    def contender(ra):
        try:
            sb.leases().claim(ra.agent_id, ra.token,
                              ["src/python/fods/model.py"])
            wins.append(ra.agent_id)
        except LeaseConflict:
            losses.append(ra.agent_id)

    threads = [threading.Thread(target=contender, args=(ra,))
               for ra in agents]
    for t in threads:
        t.start()
    for t in threads:
        t.join(30)
    return len(wins) == 1 and len(losses) == 9, {
        "winners": len(wins), "losers": len(losses)}


def pilot_05_foreign_owned_file_edit_blocked(base: Path):
    sb = Sandbox(base, "p05")
    sb.set_mode("enforcing")
    reg = sb.registry()
    a = reg.register("claude-code", task_id="TC-A")
    sb.leases().claim(a.agent_id, a.token, ["src/python/fods"])
    gate.process(sb.payload("SessionStart", session="sess-c"), root=sb.root)
    code = gate.process(sb.payload(
        "PreToolUse", session="sess-c", tool_name="Edit",
        tool_input={"file_path": str(sb.repo / "src/python/fods/model.py")}),
        root=sb.root)
    conflicts = sb.query("SELECT conflict_type FROM conflicts")
    return code == 2 and any(c["conflict_type"] == "lease-denied"
                             for c in conflicts), {
        "exit_code": code, "conflicts": conflicts}


def pilot_06_broad_staging_blocked(base: Path):
    sb = Sandbox(base, "p06")
    sb.set_mode("enforcing")
    gate.process(sb.payload("SessionStart", session="sess-a"), root=sb.root)
    sb.registry().register("codex", task_id="TC-B")  # second live agent
    broad = gate.process(sb.payload(
        "PreToolUse", session="sess-a", tool_name="Bash",
        tool_input={"command": "git add -A"}), root=sb.root)
    dotted = gate.process(sb.payload(
        "PreToolUse", session="sess-a", tool_name="Bash",
        tool_input={"command": "git add ."}), root=sb.root)
    explicit = gate.process(sb.payload(
        "PreToolUse", session="sess-a", tool_name="Bash",
        tool_input={"command": "git add src/python/fods/model.py"}),
        root=sb.root)
    return broad == 2 and dotted == 2 and explicit == 0, {
        "git_add_A": broad, "git_add_dot": dotted,
        "git_add_explicit_path": explicit}


def pilot_07_commit_under_foreign_lease_blocked(base: Path):
    sb = Sandbox(base, "p07", real_git=True)
    reg = sb.registry()
    a = reg.register("claude-code", task_id="TC-A")
    sb.leases().claim(a.agent_id, a.token, ["src/python/fods"])
    # Agent C stages A's in-progress file.
    subprocess.run(["git", "add", "src/python/fods/model.py"],
                   cwd=sb.repo, check=True, timeout=30)
    report = precommit_check(root=sb.root, repo=sb.repo)
    ok = (not report["ok"]
          and report["violations"][0]["kind"] == "foreign-lease"
          and a.agent_id in report["violations"][0]["message"])
    return ok, {"report": report}


def pilot_08_generator_without_claim_fails_before_write(base: Path):
    sb = Sandbox(base, "p08")
    reg = sb.registry()
    a = reg.register("claude-code", task_id="TC-A")
    sb.leases().claim(a.agent_id, a.token, ["out"])
    manifest = sb.repo / "manifest.yaml"
    manifest.write_text("generator_id: stub\nmode: exclusive\noutputs:\n"
                        "  - out/gen.yaml\n", encoding="utf-8")
    target = sb.repo / "out" / "gen.yaml"
    try:
        with guarded_generation("stub", manifest, root=sb.root,
                                start=sb.repo):
            target.write_text("clobbered", encoding="utf-8")
        return False, {"error": "generator not blocked"}
    except GeneratorBlocked as exc:
        return not target.exists(), {"blocked": str(exc),
                                     "target_written": target.exists()}


def pilot_09_generator_with_manifest_and_drift(base: Path):
    sb = Sandbox(base, "p09")
    manifest = sb.repo / "manifest.yaml"
    manifest.write_text("generator_id: stub\nmode: exclusive\noutputs:\n"
                        "  - out/gen.yaml\n", encoding="utf-8")
    with guarded_generation("stub", manifest, root=sb.root,
                            start=sb.repo) as g:
        (sb.repo / "out" / "gen.yaml").write_text("ok\n", encoding="utf-8")
        g.record_written(sb.repo / "out" / "gen.yaml")
        (sb.repo / "out" / "rogue.yaml").write_text("rogue\n",
                                                    encoding="utf-8")
        g.record_written(sb.repo / "out" / "rogue.yaml")
    drift = sb.query("SELECT resource_key FROM conflicts WHERE"
                     " conflict_type='generator-drift'")
    return (g.drift == ["out/rogue.yaml"]
            and drift and drift[0]["resource_key"] == "out/rogue.yaml"), {
        "declared_written": g.written, "drift_flagged": g.drift,
        "conflict_rows": drift}


def pilot_10_stale_takeover_preserves_work(base: Path):
    sb = Sandbox(base, "p10")
    reg = sb.registry()
    a = reg.register("claude-code", task_id="TC-A", heartbeat_ttl_s=60)
    lm = sb.leases()
    la = lm.claim(a.agent_id, a.token, ["src/python/fods"],
                  ttl_seconds=60)[0]
    # A "crashes" after writing uncommitted work.
    crash_file = sb.repo / "src/python/fods/model.py"
    crash_file.write_text("half-finished work by A\n", encoding="utf-8")
    pre_sha = sha256_file(crash_file)
    # One hour later C recovers.
    fut = sb.leases(now_fn=future(3600))
    reaped = fut.reap()
    c = reg.register("claude-code", task_id="TC-C")
    denied_without_reason = False
    try:
        fut.takeover(c.agent_id, c.token, la["lease_id"], "")
    except TakeoverDenied:
        denied_without_reason = True
    new = fut.takeover(c.agent_id, c.token, la["lease_id"],
                       "agent A crashed mid-sprint; resuming TC-A")
    audit = sb.query("SELECT verb, detail FROM coordination_events WHERE"
                     " verb='TAKEOVER'")
    post_sha = sha256_file(crash_file)
    ok = (reaped["leases_marked"] == 1 and denied_without_reason
          and new["takeover_of"] == la["lease_id"]
          and post_sha == pre_sha  # A's on-disk work untouched
          and audit and "crashed" in audit[0]["detail"])
    return ok, {"reaped": reaped, "new_lease": new["lease_id"],
                "predecessor_work_preserved": post_sha == pre_sha,
                "audit_row": audit}


def pilot_11_non_owner_release_denied(base: Path):
    sb = Sandbox(base, "p11")
    reg = sb.registry()
    a = reg.register("claude-code", task_id="TC-A")
    b = reg.register("codex", task_id="TC-B")
    lm = sb.leases()
    la = lm.claim(a.agent_id, a.token, ["src/python/fods"])[0]
    try:
        lm.release(b.agent_id, b.token, [la["lease_id"]])
        return False, {"error": "foreign release permitted"}
    except LeaseStale:
        status = sb.query("SELECT status FROM leases WHERE lease_id=?",
                          (la["lease_id"],))[0]["status"]
        return status == "ACTIVE", {"lease_status_after_attempt": status}


def pilot_12_conflicts_not_silently_ignorable(base: Path):
    import contextlib
    import io
    import os

    from coordination.cli import main as cli_main

    sb = Sandbox(base, "p12")
    reg = sb.registry()
    a = reg.register("claude-code", task_id="TC-A")
    b = reg.register("codex", task_id="TC-B")
    sb.leases().claim(a.agent_id, a.token, ["src/python/fods"])
    res = preflight("src/python/fods/model.py", root=sb.root, start=sb.repo,
                    agent_id=b.agent_id, token=b.token)
    cwd = os.getcwd()
    try:
        os.chdir(sb.repo)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            code_open = cli_main(["--root", str(sb.root), "--json", "status"])
            code_resolve = cli_main([
                "--root", str(sb.root), "--json", "conflicts", "resolve",
                "--id", res.conflict_id, "--state", "ACKNOWLEDGED",
                "--note", "B queues behind A for TC-A files"])
            code_clean = cli_main(["--root", str(sb.root), "--json",
                                   "status"])
    finally:
        os.chdir(cwd)
    conflict_rows = sb.query(
        "SELECT conflict_id, resource_key, detected_by, apparent_owner,"
        " conflict_type, safe_action, resolution_state, resolution_note"
        " FROM conflicts")
    ok = (res.exit_code == 2 and code_open == 1 and code_resolve == 0
          and code_clean == 0
          and conflict_rows[0]["apparent_owner"] == a.agent_id)
    return ok, {"preflight_exit": res.exit_code,
                "status_exit_with_open_conflict": code_open,
                "status_exit_after_ack": code_clean,
                "conflict_record": conflict_rows[0] if conflict_rows else None}


def pilot_13_corrupt_db_fails_open_with_incident(base: Path):
    sb = Sandbox(base, "p13")
    sb.set_mode("enforcing")
    gate.process(sb.payload("SessionStart"), root=sb.root)
    (sb.root / "coordination.db").write_bytes(b"garbage not sqlite")
    code = gate.process(sb.payload(
        "PreToolUse", tool_name="Write",
        tool_input={"file_path": str(sb.repo / "src/python/fods/model.py")}),
        root=sb.root)
    incidents = (sb.root / "hook-incidents.jsonl")
    from coordination.doctor import run_doctor
    report = run_doctor(sb.root, fix_safe=True)
    healthy_after = run_doctor(sb.root)
    ok = (code == 0 and incidents.exists()
          and "FAIL_OPEN" in incidents.read_text(encoding="utf-8")
          and any("corrupt" in f for f in report["fixes"])
          and healthy_after["healthy"])
    return ok, {"exit_code": code, "incident_logged": incidents.exists(),
                "doctor_fixes": report["fixes"],
                "healthy_after_fix": healthy_after["healthy"]}


def pilot_14_ambient_zero_ceremony_path(base: Path):
    sb = Sandbox(base, "p14")
    target = sb.repo / "src/python/fods/model.py"
    # A session that ONLY emits harness hooks -- no CLI, no env, no ceremony.
    s1 = gate.process(sb.payload("SessionStart"), root=sb.root)
    hb1 = sb.query("SELECT last_heartbeat FROM agents")
    p1 = gate.process(sb.payload("PreToolUse", tool_name="Write",
                                 tool_input={"file_path": str(target)}),
                      root=sb.root)
    target.write_text("ambient write\n", encoding="utf-8")
    gate.process(sb.payload("PostToolUse", tool_name="Write",
                            tool_input={"file_path": str(target)},
                            tool_response={"success": True}), root=sb.root)
    hb2 = sb.query("SELECT last_heartbeat, status FROM agents")
    agents = sb.query("SELECT provider, claude_session_id, status FROM agents")
    leases = sb.query("SELECT origin, resource_key, status FROM leases")
    journal = sb.query("SELECT source, post_sha256 FROM write_journal")
    end = gate.process(sb.payload("SessionEnd"), root=sb.root)
    after = sb.query("SELECT status FROM leases")
    ok = (s1 == 0 and p1 == 0 and end == 0
          and agents and agents[0]["claude_session_id"] == "sess-pilot"
          and leases and leases[0]["origin"] == "auto"
          and journal and journal[0]["source"] == "hook"
          and journal[0]["post_sha256"] == sha256_file(target)
          and hb2[0]["last_heartbeat"] >= hb1[0]["last_heartbeat"]
          and after[0]["status"] == "RELEASED")
    return ok, {"registered": agents, "auto_lease": leases,
                "journal": journal,
                "heartbeat_advanced": hb2[0]["last_heartbeat"]
                >= hb1[0]["last_heartbeat"],
                "released_on_session_end": after}


def pilot_15_before_after_damage_demo(base: Path):
    """The R1227 class of incident, reproduced then blocked."""
    evidence = {}

    # BEFORE: coordination off. A has an uncommitted hunk; C sweeps it into
    # C's own commit with `git add -A`.
    sb1 = Sandbox(base, "p15-before", real_git=True)
    sb1.set_mode("off")
    subprocess.run(["git", "add", "-A"], cwd=sb1.repo, check=True, timeout=30)
    subprocess.run(["git", "commit", "-qm", "base"], cwd=sb1.repo,
                   check=True, timeout=30)
    a_file = sb1.repo / "src/python/fods/model.py"
    a_file.write_text("model = 1\nAGENT_A_UNCOMMITTED_HUNK = True\n",
                      encoding="utf-8")
    (sb1.repo / "tools/readme_sync/c_feature.py").write_text(
        "c_work = 1\n", encoding="utf-8")
    code_add = gate.process(sb1.payload(
        "PreToolUse", session="sess-c", tool_name="Bash",
        tool_input={"command": "git add -A"}), root=sb1.root)
    subprocess.run(["git", "add", "-A"], cwd=sb1.repo, check=True, timeout=30)
    subprocess.run(["git", "commit", "-qm", "C: feature commit"],
                   cwd=sb1.repo, check=True, timeout=30)
    swept = subprocess.run(
        ["git", "show", "--name-only", "--format=", "HEAD"],
        cwd=sb1.repo, capture_output=True, text=True, timeout=30).stdout
    damage = "src/python/fods/model.py" in swept
    evidence["before"] = {
        "mode": "off", "gate_exit_for_git_add_A": code_add,
        "files_in_C_commit": swept.split(),
        "damage_observed": damage,
        "narrative": "A's uncommitted hunk was swept into C's commit"}

    # AFTER: enforcing. Same actions are blocked at the hook AND at
    # pre-commit.
    sb2 = Sandbox(base, "p15-after", real_git=True)
    subprocess.run(["git", "add", "-A"], cwd=sb2.repo, check=True, timeout=30)
    subprocess.run(["git", "commit", "-qm", "base"], cwd=sb2.repo,
                   check=True, timeout=30)
    sb2.set_mode("enforcing")
    reg = sb2.registry()
    a = reg.register("claude-code", task_id="TC-A")
    sb2.leases().claim(a.agent_id, a.token, ["src/python/fods"])
    (sb2.repo / "src/python/fods/model.py").write_text(
        "model = 1\nAGENT_A_UNCOMMITTED_HUNK = True\n", encoding="utf-8")
    gate.process(sb2.payload("SessionStart", session="sess-c"), root=sb2.root)
    code_add2 = gate.process(sb2.payload(
        "PreToolUse", session="sess-c", tool_name="Bash",
        tool_input={"command": "git add -A"}), root=sb2.root)
    # Even if C stages through a side channel, pre-commit blocks.
    subprocess.run(["git", "add", "-A"], cwd=sb2.repo, check=True, timeout=30)
    report = precommit_check(root=sb2.root, repo=sb2.repo,
                             session_id="sess-c")
    evidence["after"] = {
        "mode": "enforcing", "gate_exit_for_git_add_A": code_add2,
        "precommit_ok": report["ok"],
        "precommit_violations": report["violations"],
        "narrative": "broad add blocked at hook; side-channel staging"
                     " blocked at pre-commit"}
    ok = damage and code_add2 == 2 and not report["ok"]
    return ok, evidence


def pilot_16_hotfile_generator_contention(base: Path):
    """SFC-GAP-B (2026-07-17): two concurrent `guarded_generation` runs racing
    for the SAME hot-governance-files output -- exactly one must win the
    exclusive lease and write; the other must be denied BEFORE writing
    anything (GeneratorBlocked), never a lost-update race on the file
    content. Real threads, real DB, real lease contention -- not sequential."""
    sb = Sandbox(base, "p16")
    manifest = sb.repo / "hot-manifest.yaml"
    manifest.write_text(
        "generator_id: hot-governance-files\nmode: exclusive\noutputs:\n"
        "  - out/hot.yaml\n", encoding="utf-8")
    target = sb.repo / "out" / "hot.yaml"
    outcomes: dict[str, str] = {}
    write_order: list[str] = []
    barrier = threading.Barrier(2, timeout=30)

    def contender(name: str, payload: str):
        try:
            barrier.wait()  # maximize actual overlap, not just interleaving
        except threading.BrokenBarrierError:
            pass
        try:
            with guarded_generation("hot-governance-files", manifest,
                                    root=sb.root, start=sb.repo):
                write_order.append(f"{name}-start")
                # Hold the critical section open long enough that the other
                # thread's (barrier-synchronized) claim attempt genuinely
                # collides while this lease is still live -- a bare
                # claim+write+release round-trip on a few-byte file is fast
                # enough that both threads can otherwise run fully
                # sequentially without ever actually contending.
                time.sleep(0.3)
                target.write_text(payload, encoding="utf-8")
                write_order.append(f"{name}-end")
            outcomes[name] = "WON"
        except GeneratorBlocked:
            outcomes[name] = "BLOCKED"

    t1 = threading.Thread(target=contender, args=("A", "written by A\n"))
    t2 = threading.Thread(target=contender, args=("B", "written by B\n"))
    t1.start(); t2.start(); t1.join(30); t2.join(30)

    winners = [n for n, v in outcomes.items() if v == "WON"]
    losers = [n for n, v in outcomes.items() if v == "BLOCKED"]
    # The loser's write_order entries must be entirely absent -- it must never
    # have reached the write at all (blocked BEFORE writing, not raced after).
    loser_wrote = any(w.startswith(losers[0]) for w in write_order) if losers else True
    ok = (len(winners) == 1 and len(losers) == 1 and not loser_wrote
          and target.exists())
    return ok, {"outcomes": outcomes, "write_order": write_order,
                "loser_never_wrote": not loser_wrote,
                "final_content": target.read_text(encoding="utf-8")
                if target.exists() else None}


PILOTS = [
    ("01", "unregistered write blocked", pilot_01_unregistered_write_blocked),
    ("02", "disjoint agents proceed in parallel with mutual visibility",
     pilot_02_disjoint_agents_parallel),
    ("03", "overlapping exclusive claim rejected (parent/child)",
     pilot_03_overlapping_claim_rejected),
    ("04", "claim race: exactly one winner", pilot_04_claim_race_single_winner),
    ("05", "cannot edit another agent's owned file",
     pilot_05_foreign_owned_file_edit_blocked),
    ("06", "broad staging blocked; explicit staging allowed",
     pilot_06_broad_staging_blocked),
    ("07", "cannot commit another agent's leased file",
     pilot_07_commit_under_foreign_lease_blocked),
    ("08", "generator without output claim fails before writing",
     pilot_08_generator_without_claim_fails_before_write),
    ("09", "manifest generator proceeds; out-of-manifest drift flagged",
     pilot_09_generator_with_manifest_and_drift),
    ("10", "stale lease governed takeover preserves predecessor work",
     pilot_10_stale_takeover_preserves_work),
    ("11", "non-owner release denied", pilot_11_non_owner_release_denied),
    ("12", "conflicts carry evidence and are not silently ignorable",
     pilot_12_conflicts_not_silently_ignorable),
    ("13", "corrupt db fails open with audited incident + doctor recovery",
     pilot_13_corrupt_db_fails_open_with_incident),
    ("14", "ambient zero-ceremony path (hooks only, no CLI)",
     pilot_14_ambient_zero_ceremony_path),
    ("15", "before-vs-after: unsafe sweep reproduced then blocked",
     pilot_15_before_after_damage_demo),
    ("16", "hot-governance-files: concurrent generator contention, exactly"
           " one winner, loser never writes (SFC-GAP-B)",
     pilot_16_hotfile_generator_contention),
]


def run_all(base: Path) -> list[dict]:
    results = []
    for num, title, fn in PILOTS:
        try:
            ok, evidence = fn(base)
        except Exception as exc:  # a pilot crash is a FAIL, not an abort
            ok, evidence = False, {"exception":
                                   f"{type(exc).__name__}: {exc}"}
        results.append({"pilot": num, "title": title, "pass": bool(ok),
                        "evidence": evidence})
        print(f"[{'PASS' if ok else 'FAIL'}] pilot {num}: {title}")
    return results


def main() -> int:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    stamp = iso()
    tmp = Path(tempfile.mkdtemp(prefix="ff-coord-pilot-"))
    try:
        print("=== Coordination pilot, run 1 ===")
        run1 = run_all(tmp / "run1")
        print("=== Coordination pilot, run 2 (idempotency) ===")
        run2 = run_all(tmp / "run2")
        digest1 = [(r["pilot"], r["pass"]) for r in run1]
        digest2 = [(r["pilot"], r["pass"]) for r in run2]
        p_idempotency_ok = digest1 == digest2 and all(p for _, p in digest1)
        print(f"[{'PASS' if p_idempotency_ok else 'FAIL'}] pilot 17: double-run"
              " idempotency (identical pass set)")
        for r in run1:
            out = EVIDENCE_DIR / f"coordination-pilot-{r['pilot']}.json"
            out.write_text(json.dumps(
                {"mission": "AGENT-COORD-2026-07-15", "generated_at": stamp,
                 **r}, indent=2, default=str) + "\n", encoding="utf-8")
        (EVIDENCE_DIR / "coordination-pilot-17.json").write_text(json.dumps(
            {"mission": "AGENT-COORD-2026-07-15", "generated_at": stamp,
             "pilot": "17", "title": "double-run idempotency",
             "pass": p_idempotency_ok,
             "evidence": {"run1": digest1, "run2": digest2}},
            indent=2) + "\n", encoding="utf-8")
        total = sum(1 for r in run1 if r["pass"]) + (1 if p_idempotency_ok else 0)
        print(f"\n{total}/{len(PILOTS) + 1} proofs PASS; evidence in {EVIDENCE_DIR}")
        return 0 if total == len(PILOTS) + 1 else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
