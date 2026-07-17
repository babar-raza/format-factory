"""governance_validators_coordination.py — V194-V196 (TC-COORD-013)

Mission AGENT-COORD-2026-07-15 (plans/.claude/lazy-hugging-lovelace.md).

V194: validate_coordination_parity
    FAIL (blocks) when the multi-agent coordination protocol drifts across
    provider surfaces: adapter docs / AGENTS.md missing required verbs,
    hooks block absent from .claude/settings.json, or the gate script gone.

V195: validate_coordination_audit_trail
    FAIL (blocks) on OPEN coordination conflicts older than 48h at the
    machine-local coordination root; WARN on recent FAIL_OPEN/BYPASS events
    (enforcement degradations must be explained, never silent).

V196: validate_generator_output_manifests
    FAIL (blocks) when a guarded generator loses its output manifest or its
    guard wiring (silent broad regeneration is how concurrent work gets
    clobbered).
"""
from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from pathlib import Path

from governance_validators_contract import validator

_OPEN_CONFLICT_MAX_AGE_H = 48
_DEGRADATION_LOOKBACK_D = 7

_GUARDED_GENERATORS = (
    ("capability_sync", "tools/capability_sync/run_sync.py",
     "tools/capability_sync/output-manifest.yaml"),
    ("readme_sync", "tools/readme_sync/run_sync.py",
     "tools/readme_sync/output-manifest.yaml"),
)
_BRIDGE_MANIFESTS = (
    "tools/supervisor/autonomous-cycle-output-manifest.yaml",
)
_PARITY_SURFACES = (
    "docs/governance/codex-adapter.md",
    "docs/governance/kilo-adapter.md",
    "AGENTS.md",
)


def _result(fn_name: str, rule: str, result: str, blocks: bool,
            violations: list[str], summary: str) -> dict:
    return {"validator": fn_name, "result": result, "blocks_sprint": blocks,
            "violations": violations, "summary": f"{rule}: {summary}"}


def _coordination_import(repo_root: Path):
    supervisor_dir = repo_root / "tools" / "supervisor"
    if str(supervisor_dir) not in sys.path:
        sys.path.insert(0, str(supervisor_dir))
    from coordination.root import db_path, resolve_coordination_root
    from coordination.verbs import REQUIRED_ADAPTER_VERBS
    return db_path, resolve_coordination_root, REQUIRED_ADAPTER_VERBS


@validator(
    rule_id="V194",
    domain="governance",
    description="Coordination protocol parity across Claude/Codex/Kilo"
                " surfaces and the hook plane",
)
def validate_coordination_parity(declaration: dict,
                                 repo_root: "Path | None" = None) -> dict:
    root = Path(repo_root) if repo_root else Path(".")
    violations: list[str] = []
    try:
        _dbp, _rcr, required_verbs = _coordination_import(root)
    except Exception as exc:
        return _result("validate_coordination_parity", "V194", "FAIL", True,
                       [f"coordination package unimportable: {exc}"],
                       "coordination package missing")

    for surface in _PARITY_SURFACES:
        p = root / surface
        if not p.exists():
            violations.append(f"parity surface missing: {surface}")
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        missing = [v for v in required_verbs if v not in text]
        if missing:
            violations.append(
                f"{surface} missing required coordination verbs: {missing}")

    settings = root / ".claude" / "settings.json"
    try:
        cfg = json.loads(settings.read_text(encoding="utf-8"))
        hooks = cfg.get("hooks", {})
        if "PreToolUse" not in hooks or "SessionStart" not in hooks:
            violations.append(
                ".claude/settings.json hooks block lacks"
                " SessionStart/PreToolUse coordination gate wiring")
        else:
            commands = json.dumps(hooks)
            if "coordination/hooks/gate.py" not in commands:
                violations.append(
                    "hooks block does not reference"
                    " tools/supervisor/coordination/hooks/gate.py")
    except (OSError, ValueError) as exc:
        violations.append(f".claude/settings.json unreadable: {exc}")

    gate = root / "tools/supervisor/coordination/hooks/gate.py"
    if not gate.exists():
        violations.append("hook gate script missing: "
                          "tools/supervisor/coordination/hooks/gate.py")

    matrix = root / "docs" / "agents" / "agent-parity-matrix.yaml"
    if matrix.exists():
        if "coordination_protocol" not in matrix.read_text(
                encoding="utf-8", errors="replace"):
            violations.append(
                "agent-parity-matrix.yaml lacks a coordination_protocol row")
    else:
        violations.append("docs/agents/agent-parity-matrix.yaml missing")

    ok = not violations
    return _result("validate_coordination_parity", "V194",
                   "PASS" if ok else "FAIL", not ok, violations,
                   "parity surfaces synchronized" if ok
                   else f"{len(violations)} parity violation(s)")


@validator(
    rule_id="V195",
    domain="governance",
    description="Coordination degradations (fail-open, bypass, stale open"
                " conflicts) must be explained, never silent",
)
def validate_coordination_audit_trail(declaration: dict,
                                      repo_root: "Path | None" = None) -> dict:
    root = Path(repo_root) if repo_root else Path(".")
    fn = "validate_coordination_audit_trail"
    try:
        db_path, resolve_root, _verbs = _coordination_import(root)
        croot = resolve_root(root)
        dbp = db_path(croot)
    except Exception as exc:
        return _result(fn, "V195", "WARN", False,
                       [f"coordination unavailable: {exc}"],
                       "cannot audit (package unavailable)")
    if not dbp.exists():
        return _result(fn, "V195", "PASS", False, [],
                       "no coordination db on this machine; nothing to audit")

    violations: list[str] = []
    warns: list[str] = []
    try:
        conn = sqlite3.connect(str(dbp), timeout=5)
        conn.row_factory = sqlite3.Row
        try:
            stale_open = conn.execute(
                "SELECT conflict_id, resource_display, conflict_type,"
                " detected_at FROM conflicts WHERE resolution_state='OPEN'"
                " AND (julianday('now') - julianday(detected_at)) * 24.0 > ?",
                (_OPEN_CONFLICT_MAX_AGE_H,)).fetchall()
            for r in stale_open:
                violations.append(
                    f"OPEN conflict {r['conflict_id']}"
                    f" ({r['conflict_type']}, {r['resource_display']})"
                    f" unresolved since {r['detected_at']}")
            degradations = conn.execute(
                "SELECT verb, COUNT(*) AS n FROM coordination_events"
                " WHERE verb IN ('FAIL_OPEN','BYPASS') AND"
                " (julianday('now') - julianday(occurred_at)) < ?"
                " GROUP BY verb", (_DEGRADATION_LOOKBACK_D,)).fetchall()
            for r in degradations:
                warns.append(f"{r['n']} {r['verb']} event(s) in the last"
                             f" {_DEGRADATION_LOOKBACK_D} days")
        finally:
            conn.close()
        incidents = croot / "hook-incidents.jsonl"
        if incidents.exists():
            n = sum(1 for line in
                    incidents.read_text(encoding="utf-8",
                                        errors="replace").splitlines()
                    if line.strip())
            if n:
                warns.append(f"{n} hook incident record(s) at {incidents}")
    except sqlite3.DatabaseError as exc:
        return _result(fn, "V195", "WARN", False,
                       [f"coordination db unreadable: {exc}; run doctor"
                        " --fix-safe"], "db unreadable")

    if violations:
        return _result(fn, "V195", "FAIL", True, violations + warns,
                       f"{len(violations)} stale open conflict(s)")
    if warns:
        return _result(fn, "V195", "WARN", False, warns,
                       "degradation events present (explained via audit"
                       " trail review)")
    return _result(fn, "V195", "PASS", False, [], "audit trail clean")


@validator(
    rule_id="V196",
    domain="governance",
    description="Guarded generators keep their output manifests and guard"
                " wiring",
)
def validate_generator_output_manifests(declaration: dict,
                                        repo_root: "Path | None" = None) -> dict:
    root = Path(repo_root) if repo_root else Path(".")
    fn = "validate_generator_output_manifests"
    violations: list[str] = []
    for gen_id, source, manifest in _GUARDED_GENERATORS:
        mp = root / manifest
        if not mp.exists():
            violations.append(f"{gen_id}: manifest missing ({manifest})")
        else:
            try:
                import yaml
                data = yaml.safe_load(mp.read_text(encoding="utf-8"))
                if (not isinstance(data, dict)
                        or data.get("generator_id") != gen_id
                        or not data.get("outputs")):
                    violations.append(f"{gen_id}: manifest invalid"
                                      f" ({manifest})")
            except Exception as exc:
                violations.append(f"{gen_id}: manifest unparseable: {exc}")
        sp = root / source
        if sp.exists():
            if "guarded_generation" not in sp.read_text(
                    encoding="utf-8", errors="replace"):
                violations.append(
                    f"{gen_id}: {source} lost its guarded_generation wiring")
        else:
            violations.append(f"{gen_id}: source missing ({source})")
    for manifest in _BRIDGE_MANIFESTS:
        if not (root / manifest).exists():
            violations.append(f"guard-run bridge manifest missing:"
                              f" {manifest}")
    ok = not violations
    return _result(fn, "V196", "PASS" if ok else "FAIL", not ok, violations,
                   "generator guards intact" if ok
                   else f"{len(violations)} generator-guard violation(s)")


_KNOWN_GAPS_MAX_AGE_D = 14


@validator(
    rule_id="V252",
    domain="governance",
    description="Aging visibility for stale leases with real content drift"
                " and long-open known_gaps entries (TC-STRUCT-004,"
                " FOUND-ISSUE-OWNERSHIP-ENFORCEMENT-2026-07-17) -- extends"
                " V195's age-based pattern to two currently-invisible cases:"
                " (a) a STALE lease on a file that actually has uncommitted"
                " drift (V195 only ages OPEN conflicts, not leases"
                " themselves); (b) a docs/governance/skill-only-policy.yaml"
                " known_gaps entry open longer than 14 days with no aging"
                " signal anywhere today. WARN-only by design -- this makes"
                " currently-invisible, indefinitely-dormant items visible;"
                " it does not force a fix timeline (see TC-STRUCT-001's G5"
                " guard for the HIGH/CRITICAL-finding version of this,"
                " which does gate closure).",
)
def validate_stale_lease_drift_and_gap_aging(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    root = Path(repo_root) if repo_root else Path(".")
    fn = "validate_stale_lease_drift_and_gap_aging"
    warns: list[str] = []

    # Part A: STALE leases whose underlying file has real uncommitted drift.
    try:
        db_path, resolve_root, _verbs = _coordination_import(root)
        croot = resolve_root(root)
        dbp = db_path(croot)
        if dbp.exists():
            conn = sqlite3.connect(str(dbp), timeout=5)
            conn.row_factory = sqlite3.Row
            try:
                stale = conn.execute(
                    "SELECT resource_key, resource_display FROM leases"
                    " WHERE status='STALE'").fetchall()
            finally:
                conn.close()
            for r in stale:
                display = r["resource_display"] or r["resource_key"]
                path = root / display
                if not path.exists() or not path.is_file():
                    continue
                try:
                    result = subprocess.run(
                        ["git", "diff", "--quiet", "--", display],
                        cwd=str(root), capture_output=True, timeout=10)
                except Exception:
                    continue
                if result.returncode not in (0, 1):
                    continue  # not a tracked file / git error -- not our signal
                if result.returncode == 1:
                    warns.append(
                        f"STALE lease with real uncommitted drift: {display}")
    except Exception as exc:
        warns.append(f"stale-lease drift scan unavailable: {exc}")

    # Part B: known_gaps entries open longer than 14 days.
    try:
        import re as _re_gaps
        policy_path = root / "docs" / "governance" / "skill-only-policy.yaml"
        if policy_path.exists():
            text = policy_path.read_text(encoding="utf-8", errors="replace")
            open_gap_ids = _re_gaps.findall(
                r"gap_id:\s*(\S+)\s*\n(?:.*\n)*?\s*status:\s*open",
                text)
            for gap_id in open_gap_ids:
                try:
                    result = subprocess.run(
                        ["git", "log", "--diff-filter=A", "--format=%at",
                         "-S", f"gap_id: {gap_id}", "--",
                         "docs/governance/skill-only-policy.yaml"],
                        cwd=str(root), capture_output=True, text=True, timeout=10)
                except Exception:
                    continue
                lines = [ln for ln in result.stdout.splitlines() if ln.strip()]
                if not lines:
                    continue
                import time as _time_gaps
                introduced_at = int(lines[-1].strip())
                age_d = (_time_gaps.time() - introduced_at) / 86400.0
                if age_d > _KNOWN_GAPS_MAX_AGE_D:
                    warns.append(
                        f"known_gaps entry {gap_id} has been status: open"
                        f" for {age_d:.0f} days (> {_KNOWN_GAPS_MAX_AGE_D}"
                        " day visibility threshold)")
    except Exception as exc:
        warns.append(f"known_gaps aging scan unavailable: {exc}")

    if warns:
        return _result(fn, "V252", "WARN", False, warns,
                       f"{len(warns)} aging-visibility item(s)")
    return _result(fn, "V252", "PASS", False, [], "no aged items")
