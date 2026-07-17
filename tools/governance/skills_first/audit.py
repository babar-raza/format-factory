"""Skills-First Control — deterministic parity + coverage auditor.

Loads the three registries + on-disk command files and emits the machine-
readable coverage reports the skills-first policy requires (skill inventory,
command inventory, skill<->command matrix, material-action matrix, enforcement-
point report, stale-command / hash-drift report, ungoverned-generator signal).

FAIL-CLOSED. Missing/malformed registry -> exit 2. Any CRITICAL/HIGH parity
finding -> exit 1 (downgrade HIGH with --warn-high). Output is deterministic
(sorted) and suitable for CI.

Usage:
  python -m tools.governance.skills_first.audit [--write] [--warn-high] [--json]

  --write     persist reports under reports/skills-first-control/ and refresh the
              command-skill hash baseline for any command that currently has none
              (never silently overwrites an existing baseline hash -> that is how
              stale-command drift is detected).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import SFC_VERSION
from .registries import (
    COMMANDS_DIR,
    REPO_ROOT,
    RegistryError,
    load_commands,
    load_policy,
    load_routes,
    load_skills,
    sha256_of,
)

REPORT_DIR = REPO_ROOT / "reports" / "skills-first-control"
HASH_BASELINE = REPORT_DIR / "command-skill-hash-baseline.json"

# Registry/source roots a "generator" script writing directly would bypass skills.
_MUTATION_TARGET_RE = re.compile(r"src/(python|net)/|registry/|\.supervisor/|oracle/")
_WRITE_CALL_RE = re.compile(r"\.write_text\(|open\([^)]*['\"][wa]|\.dump\(|shutil\.copy")
# TC-RG-002 (2026-07-17): a target-pattern match now only counts near an actual
# write call (a bounded line window) instead of anywhere in the whole file.
# The original whole-file check conflated an unrelated write (e.g. to reports/)
# with an unrelated mention of src/, registry/, etc. elsewhere in the same file
# (a module docstring describing what the tool *reads*, e.g. "Scans
# src/python/{format}/..." on a report generator that writes only to reports/).
#
# A tighter "the match must be on a path-construction-syntax line" gate was
# tried and reverted: this codebase's idiom is `Path` objects joined with `/`
# across separately-quoted segments (`root / "src" / "python" / mod`), which
# never produces a contiguous "src/python/" substring in the actual
# construction code -- the literal substring this regex can find mostly shows
# up in comments/docstrings/error-messages describing the target, which
# remains a legitimate (if imperfect) signal here. Requiring path-join syntax
# produced false NEGATIVES on confirmed real gaps (e.g. an f-string error
# message "not found in src/python/" is exactly this shape and is the only
# nearby textual evidence for a genuine direct src/ writer). Windowing alone
# is the defensible fix; the residual candidates still require human/agent
# triage -- this remains a signal scan, never a precise static analyzer.
_PROXIMITY_WINDOW_BEFORE = 8
_PROXIMITY_WINDOW_AFTER = 2

SEVERITY_CRITICAL = "CRITICAL"  # blocks always
SEVERITY_HIGH = "HIGH"          # blocks unless --warn-high
SEVERITY_MEDIUM = "MEDIUM"      # reported + tracked, never blocks (calibrated risk)
SEVERITY_INFO = "INFO"          # informational
_SEV_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "INFO": 3}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_baseline() -> dict[str, str]:
    if HASH_BASELINE.exists():
        try:
            data = json.loads(HASH_BASELINE.read_text(encoding="utf-8"))
            return data.get("hashes", {}) if isinstance(data, dict) else {}
        except (ValueError, OSError):
            return {}
    return {}


def build_skill_command_matrix(skills, commands) -> dict[str, Any]:
    """Cross-check skills <-> commands <-> on-disk files. Returns findings.

    A command .md is *governed* if any of these hold:
      - a skill's command_file points at it (skill ownership), OR
      - the command-registry has an entry whose `file` is that path, OR
      - the command-registry has an entry whose command_id equals the slug
        (the registry's documented command_id -> <slug>.md convention).
    Ownerless .md (none of the above) is a HIGH ungoverned-surface finding.
    Registry entries missing the `file` field are a separate, aggregated
    registry-completeness finding (traceability, not ownerless).
    """
    skill_ids = {s.skill_id for s in skills}
    active_skills = [s for s in skills if s.is_active]

    on_disk = {
        p.relative_to(REPO_ROOT).as_posix()
        for p in COMMANDS_DIR.glob("*.md")
    }
    skill_cmd_files = {s.command_file for s in skills if s.command_file}
    skill_cmd_slugs = {Path(f).stem for f in skill_cmd_files}
    reg_files = {c.file for c in commands if c.file}
    reg_slugs = {c.command_id for c in commands}
    registered_skill_ids_in_cmds = {c.skill_id for c in commands if c.skill_id}

    governed_paths = reg_files | skill_cmd_files
    governed_slugs = reg_slugs | skill_cmd_slugs

    findings: list[dict[str, Any]] = []

    # 1. Active skill with no command file, or command file missing on disk.
    for s in active_skills:
        if not s.command_file:
            findings.append({
                "category": "skill_without_command",
                "severity": SEVERITY_HIGH,
                "skill_id": s.skill_id,
                "detail": "active skill has no command_file",
            })
        elif s.command_file not in on_disk:
            findings.append({
                "category": "broken_command_ref",
                "severity": SEVERITY_CRITICAL,
                "skill_id": s.skill_id,
                "detail": f"command_file does not exist on disk: {s.command_file}",
            })

    # 2. Registry command whose skill_id is not a registered skill.
    for c in commands:
        if c.status != "active":
            continue
        if not c.skill_id:
            findings.append({
                "category": "command_without_skill_owner",
                "severity": SEVERITY_CRITICAL,
                "command_id": c.command_id,
                "detail": "active command has empty skill_id",
            })
        elif c.skill_id not in skill_ids:
            findings.append({
                "category": "command_without_skill_owner",
                "severity": SEVERITY_CRITICAL,
                "command_id": c.command_id,
                "detail": f"skill_id '{c.skill_id}' not in skill registry",
            })

    # 3. Active command whose owning skill is deprecated.
    skill_status = {s.skill_id: s.status for s in skills}
    for c in commands:
        if c.status == "active" and c.skill_id in skill_status:
            if skill_status[c.skill_id] not in ("active",):
                findings.append({
                    "category": "active_command_deprecated_skill",
                    "severity": SEVERITY_HIGH,
                    "command_id": c.command_id,
                    "detail": f"command active but skill '{c.skill_id}' status="
                              f"{skill_status[c.skill_id]}",
                })

    # 4. On-disk .md that no skill owns and no registry entry references.
    ignore = {"command-registry.yaml"}
    ownerless = []
    for f in sorted(on_disk):
        base = Path(f).name
        slug = Path(f).stem
        if base in ignore or base.startswith("_"):
            continue
        if f in governed_paths or slug in governed_slugs:
            continue
        ownerless.append(f)
        findings.append({
            "category": "unregistered_command_md",
            "severity": SEVERITY_HIGH,
            "file": f,
            "detail": "command .md on disk owned by no skill and no registry entry",
        })

    # 5. Registry completeness: entries missing the `file` field (aggregated).
    missing_file = sorted(c.command_id for c in commands if not c.file)
    if missing_file:
        findings.append({
            "category": "command_registry_entry_missing_file_field",
            # MEDIUM: the documented command_id -> <slug>.md convention still
            # resolves these, so they are traceability debt, not an ownerless
            # surface. Tracked for backfill via the normalize-skill-registry skill.
            "severity": SEVERITY_MEDIUM,
            "detail": f"{len(missing_file)} command-registry entries lack a 'file' "
                      f"field (rely on command_id convention); traceability debt "
                      f"-- backfill via normalize-skill-registry",
            "sample": missing_file[:10],
        })

    return {
        "counts": {
            "skills_total": len(skills),
            "skills_active": len(active_skills),
            "commands_registered": len(commands),
            "command_md_on_disk": len(on_disk),
            "skills_referenced_by_commands": len(registered_skill_ids_in_cmds),
            "ownerless_command_md": len(ownerless),
            "registry_entries_missing_file_field": len(missing_file),
        },
        "findings": findings,
    }


def build_hash_drift(skills, baseline: dict[str, str]) -> dict[str, Any]:
    """Detect command<->skill divergence by content hash. Introduces the
    binding the registries never had. STALE = baseline hash differs from current.
    NO_BASELINE entries are surfaced so --write can seed them."""
    current: dict[str, str] = {}
    stale: list[dict[str, str]] = []
    no_baseline: list[str] = []
    for s in skills:
        if not s.is_active or not s.command_file:
            continue
        p = REPO_ROOT / s.command_file
        h = sha256_of(p)
        if not h:
            continue  # missing file already flagged by matrix as broken_command_ref
        key = s.command_file
        current[key] = h
        prev = baseline.get(key)
        if prev is None:
            no_baseline.append(key)
        elif prev != h:
            stale.append({"command_file": key, "skill_id": s.skill_id,
                          "baseline": prev[:12], "current": h[:12]})
    return {
        "current_hashes": current,
        "stale": sorted(stale, key=lambda x: x["command_file"]),
        "no_baseline": sorted(no_baseline),
    }


# Governed operation -> route keywords used to prove routing coverage.
_OP_ROUTE_HINTS = {
    "creating_editing_moving_deleting_files": ["product_source", "source", "taskcard_execution"],
    "generating_code": ["source", "kickstart", "stub", "product"],
    "changing_tests_or_fixtures": ["test", "roundtrip"],
    "modifying_validators": ["validator", "governance"],
    "changing_taskcard_states": ["taskcard", "plan"],
    "changing_sprint_state": ["sprint", "closeout", "audit"],
    "changing_ledgers_or_registries": ["ledger", "registry", "gap", "obligation"],
    "accepting_or_closing_gap_findings": ["gap", "closeout", "audit"],
    "producing_canonical_evidence": ["evidence"],
    "running_migrations_or_backfills": ["backfill", "migrat"],
    "marking_gates_complete": ["gate", "certification"],
}


def build_material_action_matrix(policy, routes, skills) -> dict[str, Any]:
    ops = policy.get("governed_operations", [])
    active_routes = [r for r in routes if r.is_active]
    active_skill_ids = {s.skill_id for s in skills if s.is_active}
    rows = []
    for op in ops:
        hints = _OP_ROUTE_HINTS.get(op, [op.split("_")[0]])
        covering = []
        for r in active_routes:
            blob = (r.route_id + " " + r.description).lower()
            if any(h in blob for h in hints):
                usable = [sid for sid in r.preferred_skill_ids if sid in active_skill_ids]
                if usable:
                    covering.append({"route_id": r.route_id, "skills": usable[:3]})
        rows.append({
            "operation": op,
            "covered": bool(covering),
            "routes": covering[:3],
        })
    uncovered = [r["operation"] for r in rows if not r["covered"]]
    return {"rows": rows, "uncovered_operations": uncovered}


def build_enforcement_report(policy) -> dict[str, Any]:
    """Report policy enforcement points + verify ground-truth facts that the
    policy's own status fields are known to get wrong."""
    eps = policy.get("enforcement_points", [])
    # Ground-truth probes (cheap, deterministic).
    precommit_hook = REPO_ROOT / ".hooks" / "pre-commit-skill-guard"
    git_hook = REPO_ROOT / ".git" / "hooks" / "pre-commit"
    gate_py = REPO_ROOT / "tools" / "supervisor" / "coordination" / "hooks" / "gate.py"
    facts = {
        "precommit_hook_file_exists": precommit_hook.exists(),
        "precommit_hook_installed": git_hook.exists()
        or git_hook.is_symlink(),
        "tool_layer_hook_exists": gate_py.exists(),
        "tool_layer_hook_skill_aware": bool(
            gate_py.exists()
            and re.search(r"skill|receipt|mutation_guard",
                          gate_py.read_text(encoding="utf-8", errors="replace"))
        ),
    }
    ep_ids = {e.get("id") for e in eps if isinstance(e, dict)}
    return {
        "declared_points": [
            {"id": e.get("id"), "name": e.get("name"),
             "declared_status": e.get("current_status")}
            for e in eps if isinstance(e, dict)
        ],
        "ground_truth": facts,
        "inconsistencies": _enforcement_inconsistencies(eps, facts, ep_ids),
        "acknowledged_gaps": _acknowledged_gaps(eps, facts, ep_ids),
    }


def _tool_layer_gap_documented(eps, ep_ids) -> bool:
    """True if the policy documents the skill-blind tool-layer hook as a known
    gap (EP-010 tool_layer_skill_gate). Once acknowledged with compensating
    controls it is a documented gap, not a hidden inconsistency."""
    for e in eps:
        if isinstance(e, dict) and e.get("id") == "EP-010" \
                and e.get("name") == "tool_layer_skill_gate":
            return True
    return False


def _enforcement_inconsistencies(eps, facts, ep_ids) -> list[str]:
    out = []
    for e in eps:
        if not isinstance(e, dict):
            continue
        if e.get("id") == "EP-007":
            declared = e.get("current_status", "")
            if facts["precommit_hook_installed"] and declared == "NOT_IMPLEMENTED":
                out.append(
                    "EP-007 declared NOT_IMPLEMENTED but pre-commit hook IS installed"
                )
    if (facts["tool_layer_hook_exists"] and not facts["tool_layer_hook_skill_aware"]
            and not _tool_layer_gap_documented(eps, ep_ids)):
        out.append(
            "tool-layer PreToolUse hook (gate.py) is coordination-only / skill-blind"
            " and is NOT documented as a known gap (EP-010)"
        )
    return out


def _acknowledged_gaps(eps, facts, ep_ids) -> list[str]:
    out = []
    if (facts["tool_layer_hook_exists"] and not facts["tool_layer_hook_skill_aware"]
            and _tool_layer_gap_documented(eps, ep_ids)):
        out.append(
            "tool-layer PreToolUse hook is skill-blind — ACKNOWLEDGED as EP-010 gap"
            " with compensating controls (EP-007/EP-012/EP-013)"
        )
    return out


def _write_call_targets_mutation_path(lines: list[str], write_line_idx: int) -> bool:
    """True if the write call at `lines[write_line_idx]` has a mutation-target
    string in a nearby line (bounded window, not just anywhere in the file)."""
    lo = max(0, write_line_idx - _PROXIMITY_WINDOW_BEFORE)
    hi = min(len(lines), write_line_idx + _PROXIMITY_WINDOW_AFTER + 1)
    return any(_MUTATION_TARGET_RE.search(line) for line in lines[lo:hi])


def scan_ungoverned_generators(limit: int = 40) -> dict[str, Any]:
    """Signal scan: tools/**/*.py that both write files AND target src/ or a
    registry are candidate ungoverned mutation entry points. Heuristic — this is
    a *signal*, deduped and bounded; never a clean-pass gate on its own."""
    tools_dir = REPO_ROOT / "tools"
    hits: list[str] = []
    for p in sorted(tools_dir.rglob("*.py")):
        rel = p.relative_to(REPO_ROOT).as_posix()
        if "/tests/" in rel or rel.endswith("_test.py"):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if not _WRITE_CALL_RE.search(text):
            continue
        lines = text.splitlines()
        if any(_WRITE_CALL_RE.search(line) and _write_call_targets_mutation_path(lines, i)
               for i, line in enumerate(lines)):
            hits.append(rel)
    return {"count": len(hits), "sample": hits[:limit], "truncated": len(hits) > limit}


def run_audit(scan_generators: bool = True) -> dict[str, Any]:
    skills = load_skills()
    commands = load_commands()
    routes = load_routes()
    policy = load_policy()
    baseline = _load_baseline()

    matrix = build_skill_command_matrix(skills, commands)
    hashes = build_hash_drift(skills, baseline)
    material = build_material_action_matrix(policy, routes, skills)
    enforcement = build_enforcement_report(policy)
    generators = scan_ungoverned_generators() if scan_generators else {"count": None}

    all_findings = list(matrix["findings"])
    for st in hashes["stale"]:
        all_findings.append({
            "category": "stale_command_hash",
            "severity": SEVERITY_HIGH,
            "command_file": st["command_file"],
            "skill_id": st["skill_id"],
            "detail": f"command content diverged from baseline "
                      f"({st['baseline']}->{st['current']})",
        })
    for op in material["uncovered_operations"]:
        all_findings.append({
            "category": "governed_operation_without_route",
            "severity": SEVERITY_INFO,
            "operation": op,
            "detail": "no active route/skill maps to this governed operation",
        })
    for inc in enforcement["inconsistencies"]:
        all_findings.append({
            "category": "enforcement_inconsistency",
            "severity": SEVERITY_HIGH,
            "detail": inc,
        })

    sev_counts = {SEVERITY_CRITICAL: 0, SEVERITY_HIGH: 0,
                  SEVERITY_MEDIUM: 0, SEVERITY_INFO: 0}
    for f in all_findings:
        sev_counts[f.get("severity", SEVERITY_INFO)] += 1

    # TC-STRUCT-001 (2026-07-17): record HIGH/CRITICAL findings to the ambient
    # per-agent surfaced-findings log so a plan-closure guard can require a
    # disposition later, regardless of whether anyone submits a formal
    # declaration for this specific run — closes the "found in an interactive
    # session, never declared, never checked" gap this mechanism exists for.
    try:
        from .surfaced_findings import record_surfaced_findings
        record_surfaced_findings(all_findings)
    except Exception:
        pass  # Never let logging failure break the audit it's observing.

    return {
        "schema": "skills-first-control/audit@1",
        "sfc_version": SFC_VERSION,
        "generated_at": _now(),
        "counts": matrix["counts"],
        "severity_counts": sev_counts,
        "skill_command_matrix": matrix,
        "hash_drift": {"stale": hashes["stale"], "no_baseline": hashes["no_baseline"]},
        "material_action_matrix": material,
        "enforcement_report": enforcement,
        "ungoverned_generator_signal": generators,
        "findings": sorted(all_findings, key=lambda x: (
            _SEV_ORDER.get(x.get("severity", "INFO"), 3),
            x.get("category", ""),
        )),
        "_current_hashes": hashes["current_hashes"],
    }


def verdict_for(report: dict[str, Any], warn_high: bool) -> tuple[str, int]:
    sc = report["severity_counts"]
    if sc[SEVERITY_CRITICAL] > 0:
        return "FAIL", 1
    if sc[SEVERITY_HIGH] > 0 and not warn_high:
        return "FAIL", 1
    if sc[SEVERITY_HIGH] > 0:
        return "PASS_WITH_WARNINGS", 0
    return "PASS", 0


def _write_reports(report: dict[str, Any]) -> list[str]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    current = report.pop("_current_hashes", {})

    summary = REPORT_DIR / "audit-summary.json"
    summary.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                       encoding="utf-8")
    written.append(summary.relative_to(REPO_ROOT).as_posix())

    # Seed hash baseline ONLY for command files without an existing entry.
    baseline = _load_baseline()
    changed = False
    for k, v in current.items():
        if k not in baseline:
            baseline[k] = v
            changed = True
    if changed or not HASH_BASELINE.exists():
        HASH_BASELINE.write_text(
            json.dumps({"generated_at": _now(), "hashes": baseline},
                       indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written.append(HASH_BASELINE.relative_to(REPO_ROOT).as_posix())

    md = REPORT_DIR / "audit-summary.md"
    md.write_text(_render_md(report), encoding="utf-8")
    written.append(md.relative_to(REPO_ROOT).as_posix())
    return written


def _render_md(r: dict[str, Any]) -> str:
    c = r["counts"]
    sc = r["severity_counts"]
    lines = [
        "# Skills-First Control — Audit Summary",
        f"_Generated: {r['generated_at']} · SFC v{r['sfc_version']}_",
        "",
        "## Counts",
        f"- Skills total / active: {c['skills_total']} / {c['skills_active']}",
        f"- Commands registered / on disk: {c['commands_registered']} / "
        f"{c['command_md_on_disk']}",
        "",
        "## Severity",
        f"- CRITICAL: {sc['CRITICAL']}  ·  HIGH: {sc['HIGH']}  ·  "
        f"MEDIUM: {sc['MEDIUM']}  ·  INFO: {sc['INFO']}",
        "",
        "## Findings",
    ]
    if not r["findings"]:
        lines.append("- (none)")
    for f in r["findings"]:
        who = f.get("skill_id") or f.get("command_id") or f.get("file") \
            or f.get("command_file") or f.get("operation") or ""
        lines.append(f"- **{f['severity']}** `{f['category']}` {who} — {f.get('detail','')}")
    lines.append("")
    lines.append("## Enforcement inconsistencies")
    incs = r["enforcement_report"]["inconsistencies"]
    lines.extend([f"- {i}" for i in incs] or ["- (none)"])
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Skills-First Control auditor")
    ap.add_argument("--write", action="store_true", help="persist reports + seed baseline")
    ap.add_argument("--warn-high", action="store_true",
                    help="treat HIGH findings as warnings (exit 0)")
    ap.add_argument("--json", action="store_true", help="print full JSON to stdout")
    ap.add_argument("--no-generator-scan", action="store_true")
    args = ap.parse_args(argv)

    try:
        report = run_audit(scan_generators=not args.no_generator_scan)
    except RegistryError as exc:
        print(json.dumps({"verdict": "CONFIG_ERROR", "error": str(exc)}), file=sys.stderr)
        return 2

    verdict, code = verdict_for(report, args.warn_high)
    report_out = dict(report)
    if args.write:
        written = _write_reports(report_out)
    else:
        report_out.pop("_current_hashes", None)
        written = []

    if args.json:
        print(json.dumps(report_out, indent=2, sort_keys=True))
    else:
        c = report["counts"]
        sc = report["severity_counts"]
        print(f"[skills-first-audit] verdict={verdict} "
              f"skills={c['skills_active']}/{c['skills_total']} "
              f"commands={c['commands_registered']} "
              f"CRITICAL={sc['CRITICAL']} HIGH={sc['HIGH']} "
              f"MEDIUM={sc['MEDIUM']} INFO={sc['INFO']}")
        for f in report["findings"][:25]:
            who = f.get("skill_id") or f.get("command_id") or f.get("file") \
                or f.get("command_file") or f.get("operation") or ""
            print(f"  {f['severity']:8} {f['category']:34} {who} :: {f.get('detail','')}")
        if written:
            print("  wrote: " + ", ".join(written))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
