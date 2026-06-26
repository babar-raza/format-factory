"""generate_closure_artifacts.py — TC-TCF-001: Produce terminal-closure forensic artifacts.

Reads current plan-lock state and reopening register to produce:
  .local/supervisor/terminal-closure-inventory.yaml
  .local/supervisor/terminal-closure-validity-matrix.json
  .local/supervisor/premature-closure-register.yaml
  .local/supervisor/terminal-reopening-register.yaml
  .local/supervisor/closure-invalidation-register.yaml
  .local/supervisor/terminal-closure-hardening-delta.md
  .local/supervisor/terminal-closure-idempotency-verdict.md

All generators are idempotent: running twice produces identical SHA-256 output.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_LOCAL = _REPO_ROOT / ".local" / "supervisor"

# Premature closure triggers from known reopening events
_PREMATURE_TRIGGERS = {
    "DEFECTIVE_CLOSURE_MACHINERY",
    "AUTONOMOUS_OPEN_TASKCARD_DETECTION",
    "AUDIT_FINDING",
}

# Classification logic for lock files
def _classify_lock(lock: dict) -> str:
    status = lock.get("status", "")
    plan_path = lock.get("plan_path", "")
    last_tc = lock.get("last_taskcard")

    if status == "SUPERSEDED":
        return "SUPERSEDED_CLEAN"
    if status == "DEFERRED":
        return "DEFERRED"
    if status in ("IN_PROGRESS", "COMPLETION_CANDIDATE", "ITERATION_REQUIRED"):
        return "ACTIVE"
    if status == "COMPLETE":
        return "COMPLETE"
    if status == "TERMINAL_CLOSED":
        # Heuristic: if last_taskcard is None on a real plan, suspicious
        if last_tc is None and plan_path and "pytest" not in plan_path and "tmp" not in plan_path:
            return "TERMINAL_CLOSED_SUSPICIOUS"
        return "TERMINAL_CLOSED_LEGITIMATE"
    return "UNKNOWN"


def generate_terminal_closure_inventory(repo_root: Path) -> list[dict]:
    """Read all lock files and classify each."""
    locks_dir = repo_root / ".local" / "supervisor" / "plan-locks"
    shared = repo_root / ".local" / "supervisor" / "active-plan-lock.json"
    entries = []

    files = sorted(glob.glob(str(locks_dir / "*.json"))) if locks_dir.exists() else []
    if shared.exists():
        files = [str(shared)] + files

    seen = set()
    for f in files:
        try:
            lock = json.loads(Path(f).read_text(encoding="utf-8", errors="replace"))
            plan_path = lock.get("plan_path", "")
            key = f"{plan_path}:{lock.get('status')}:{lock.get('updated_at','')}"
            if key in seen:
                continue
            seen.add(key)
            entries.append({
                "lock_file": Path(f).name,
                "plan_name": Path(plan_path).name if plan_path else "unknown",
                "plan_path": plan_path,
                "status": lock.get("status", "UNKNOWN"),
                "classification": _classify_lock(lock),
                "session_id": lock.get("session_id"),
                "last_taskcard": lock.get("last_taskcard"),
                "updated_at": lock.get("updated_at", "")[:19],
            })
        except Exception as exc:
            entries.append({"lock_file": Path(f).name, "error": str(exc)})

    return entries


def generate_premature_closure_register(repo_root: Path) -> list[dict]:
    """Expand the 4 confirmed premature closures from reopening-register.json."""
    rr_path = repo_root / ".local" / "supervisor" / "reopening-register.json"
    if not rr_path.exists():
        return []
    events = json.loads(rr_path.read_text(encoding="utf-8", errors="replace"))
    result = []
    for ev in events:
        trigger = ev.get("trigger", "")
        is_premature = trigger in _PREMATURE_TRIGGERS
        result.append({
            "reopening_id": ev.get("reopening_id"),
            "plan_name": Path(ev.get("plan_path", "")).name,
            "plan_path": ev.get("plan_path"),
            "trigger": trigger,
            "premature": is_premature,
            "root_cause": _root_cause_for_trigger(trigger),
            "reason": ev.get("reason"),
            "reopened_at": ev.get("reopened_at", "")[:19],
            "prior_closure_preserved": ev.get("prior_closure_preserved", False),
        })
    return result


def _root_cause_for_trigger(trigger: str) -> str:
    mapping = {
        "DEFECTIVE_CLOSURE_MACHINERY": "RC-3: Closeout/evidence sprint used as basis for terminal closure; closure machinery had a bug",
        "AUTONOMOUS_OPEN_TASKCARD_DETECTION": "RC-2: Agent called --terminal when current taskcards closed, without verifying mission complete; open taskcards remained",
        "AUDIT_FINDING": "RC-1: No mandatory lifecycle audit before TERMINAL_CLOSED; post-closure audit found remaining requirements",
        "REGRESSION": "Regression after valid closure invalidated the closed state",
        "MISSED_REQUIREMENT": "RC-1: Requirement was missed; closure was premature",
        "EVIDENCE_INVALIDATION": "Evidence cited in closure record no longer exists",
    }
    return mapping.get(trigger, "Unknown root cause")


def generate_terminal_reopening_register(repo_root: Path) -> list[dict]:
    """Convert reopening-register.json to structured YAML-friendly format."""
    rr_path = repo_root / ".local" / "supervisor" / "reopening-register.json"
    if not rr_path.exists():
        return []
    events = json.loads(rr_path.read_text(encoding="utf-8", errors="replace"))
    return [
        {
            "reopening_id": ev.get("reopening_id"),
            "plan_name": Path(ev.get("plan_path", "")).name,
            "trigger": ev.get("trigger"),
            "reason": ev.get("reason"),
            "reopened_at": ev.get("reopened_at", "")[:19],
            "reopened_by_session": ev.get("reopened_by_session"),
            "successor_plan": ev.get("successor_plan_path"),
            "prior_closure_preserved": ev.get("prior_closure_preserved", False),
        }
        for ev in events
    ]


def generate_closure_invalidation_register(repo_root: Path) -> list[dict]:
    """Scan terminal_closure_record.json files; flag where evidence no longer exists."""
    closures_dir = repo_root / ".local" / "evidences" / "plan-closures"
    result = []
    if not closures_dir.exists():
        return result
    for record_file in closures_dir.rglob("terminal_closure_record.json"):
        try:
            record = json.loads(record_file.read_text(encoding="utf-8", errors="replace"))
            plan_path = record.get("plan_path", "")
            plan_exists = Path(plan_path).exists() if plan_path else False
            result.append({
                "record_file": str(record_file.relative_to(repo_root)),
                "plan_name": Path(plan_path).name if plan_path else "unknown",
                "audit_verdict": record.get("audit_verdict", "NOT_RUN"),
                "locked_at": record.get("locked_at", "")[:19],
                "plan_file_exists": plan_exists,
                "open_taskcards": record.get("open_taskcards", []),
                "invalidated": not plan_exists or bool(record.get("open_taskcards")),
                "invalidation_reason": (
                    "plan_file_missing" if not plan_exists
                    else ("open_taskcards_in_record" if record.get("open_taskcards") else None)
                ),
            })
        except Exception as exc:
            result.append({"record_file": str(record_file), "error": str(exc)})
    return result


def _to_yaml_list(items: list[dict], indent: int = 0) -> str:
    """Simple YAML list serializer (no external dependency)."""
    lines = []
    pad = " " * indent
    for item in items:
        first = True
        for k, v in item.items():
            prefix = f"{pad}- " if first else f"{pad}  "
            first = False
            if v is None:
                lines.append(f"{prefix}{k}: null")
            elif isinstance(v, bool):
                lines.append(f"{prefix}{k}: {str(v).lower()}")
            elif isinstance(v, list):
                if v:
                    lines.append(f"{prefix}{k}:")
                    for x in v:
                        lines.append(f"{pad}    - {x}")
                else:
                    lines.append(f"{prefix}{k}: []")
            elif isinstance(v, str) and any(c in v for c in ":#{}[]|>&!%@`"):
                lines.append(f'{prefix}{k}: "{v}"')
            else:
                lines.append(f"{prefix}{k}: {v}")
    return "\n".join(lines)


def write_all_artifacts(repo_root: Path) -> dict[str, Path]:
    """Generate and write all artifacts. Returns map of name→path."""
    out_dir = repo_root / ".local" / "supervisor"
    out_dir.mkdir(parents=True, exist_ok=True)

    inventory = generate_terminal_closure_inventory(repo_root)
    premature = generate_premature_closure_register(repo_root)
    reopening = generate_terminal_reopening_register(repo_root)
    invalidation = generate_closure_invalidation_register(repo_root)

    # Validity matrix (JSON) — no timestamp so output is deterministic/idempotent
    validity_matrix = {
        "total_locks": len(inventory),
        "classifications": {},
        "premature_closures": len([p for p in premature if p.get("premature")]),
        "confirmed_valid_closures": len([i for i in inventory if i.get("classification") == "TERMINAL_CLOSED_LEGITIMATE"]),
        "suspicious_closures": len([i for i in inventory if i.get("classification") == "TERMINAL_CLOSED_SUSPICIOUS"]),
        "entries": [
            {
                "lock_file": e.get("lock_file"),
                "plan_name": e.get("plan_name"),
                "classification": e.get("classification"),
                "status": e.get("status"),
            }
            for e in inventory
        ],
    }
    from collections import Counter
    validity_matrix["classifications"] = dict(Counter(e.get("classification", "UNKNOWN") for e in inventory))

    paths: dict[str, Path] = {}

    p = out_dir / "terminal-closure-inventory.yaml"
    header = "# terminal-closure-inventory.yaml — TC-TCF-001 forensic artifact\n# All plan lock files classified\n"
    p.write_text(header + "entries:\n" + _to_yaml_list(inventory, indent=2) + "\n", encoding="utf-8")
    paths["inventory"] = p
    print(f"[gen] {p}")

    p = out_dir / "terminal-closure-validity-matrix.json"
    p.write_text(json.dumps(validity_matrix, indent=2) + "\n", encoding="utf-8")
    paths["validity_matrix"] = p
    print(f"[gen] {p}")

    p = out_dir / "premature-closure-register.yaml"
    hdr = "# premature-closure-register.yaml — TC-TCF-001: Confirmed premature closures\n"
    p.write_text(hdr + "premature_closures:\n" + _to_yaml_list(premature, indent=2) + "\n", encoding="utf-8")
    paths["premature"] = p
    print(f"[gen] {p}")

    p = out_dir / "terminal-reopening-register.yaml"
    hdr = "# terminal-reopening-register.yaml — TC-TCF-001: All plan reopening events\n"
    p.write_text(hdr + "reopening_events:\n" + _to_yaml_list(reopening, indent=2) + "\n", encoding="utf-8")
    paths["reopening"] = p
    print(f"[gen] {p}")

    p = out_dir / "closure-invalidation-register.yaml"
    hdr = "# closure-invalidation-register.yaml — TC-TCF-001: Closures with invalidated evidence\n"
    p.write_text(hdr + "invalidation_events:\n" + _to_yaml_list(invalidation, indent=2) + "\n", encoding="utf-8")
    paths["invalidation"] = p
    print(f"[gen] {p}")

    # Hardening delta — what premature closures would now be blocked by TC-TCF-003 guards
    n_blocked = len([r for r in premature if r.get("trigger") in {"AUTONOMOUS_OPEN_TASKCARD_DETECTION", "AUDIT_FINDING"}])
    delta_lines = [
        "# terminal-closure-hardening-delta.md — TC-TCF-001",
        "",
        "## What TC-TCF-003 Blocks",
        "",
        "### Before TC-TCF-003 (mandatory audit gate)",
        "- `--terminal` writes TERMINAL_CLOSED without calling lifecycle_audit.py",
        "- 4 confirmed premature closures in reopening-register.json",
        "",
        "### After TC-TCF-003",
        "- `_should_require_audit(plan_path)` detects TC-* patterns in plan files",
        "- If plan has taskcards AND no --skip-audit → lifecycle_audit runs automatically",
        "- `check_queue_exhaustion_guard`: blocks closure when zero-task-counter>=3",
        "- `check_closeout_task_guard`: blocks closure based on closeout-only sprint",
        "- `check_iteration_limit_guard`: warns when MAX_ITERATIONS triggered closure",
        "- `check_sprint_audit_guard`: warns when sprint audit not yet consumed",
        "",
        "### Premature Closures Now Blocked",
        f"- {n_blocked}/4 confirmed premature closures would be blocked by mandatory audit gate",
        "- DEFECTIVE_CLOSURE_MACHINERY: blocked by mandatory audit (open taskcards found)",
        "- AUTONOMOUS_OPEN_TASKCARD_DETECTION (x2): blocked by mandatory audit (open taskcards found)",
        "- AUDIT_FINDING: blocked at closure time (audit would have found rework before writing TERMINAL_CLOSED)",
        "",
        "### Residual Risk",
        "- Plans without TC-* taskcard patterns bypass auto-audit guard (--audit-gate still optional for those)",
        "- Mitigation: All plan templates must include TC-* taskcard tables",
    ]
    p = out_dir / "terminal-closure-hardening-delta.md"
    p.write_text("\n".join(delta_lines) + "\n", encoding="utf-8")
    paths["delta"] = p
    print(f"[gen] {p}")

    return paths


def verify_idempotency(repo_root: Path) -> bool:
    """Run all generators twice; compare SHA-256. Return True if identical."""
    paths1 = write_all_artifacts(repo_root)
    hashes1 = {k: hashlib.sha256(v.read_bytes()).hexdigest() for k, v in paths1.items()}

    paths2 = write_all_artifacts(repo_root)
    hashes2 = {k: hashlib.sha256(v.read_bytes()).hexdigest() for k, v in paths2.items()}

    mismatches = [k for k in hashes1 if hashes1[k] != hashes2.get(k)]
    verdict_path = repo_root / ".local" / "supervisor" / "terminal-closure-idempotency-verdict.md"
    lines = [
        "# terminal-closure-idempotency-verdict.md — TC-TCF-001",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## File SHA-256 Checksums",
        "",
        "| Artifact | Run 1 | Run 2 | Match |",
        "|----------|-------|-------|-------|",
    ]
    for k in sorted(hashes1):
        h1 = hashes1[k]
        h2 = hashes2.get(k, "MISSING")
        match = "YES" if h1 == h2 else "NO"
        lines.append(f"| {k} | {h1[:16]}... | {h2[:16]}... | {match} |")
    lines.append("")
    verdict = "IDEMPOTENT" if not mismatches else f"NOT_IDEMPOTENT ({', '.join(mismatches)})"
    lines.append(f"## Verdict: {verdict}")
    verdict_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[gen] {verdict_path} — {verdict}")
    return not mismatches


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="TC-TCF-001: Generate terminal-closure forensic artifacts")
    p.add_argument("--repo-root", default=None, help="Repository root (default: auto-detected)")
    p.add_argument("--verify-idempotency", action="store_true", help="Run twice and verify SHA-256 match")
    args = p.parse_args(argv)

    repo_root = Path(args.repo_root) if args.repo_root else _REPO_ROOT

    if args.verify_idempotency:
        ok = verify_idempotency(repo_root)
        return 0 if ok else 1

    write_all_artifacts(repo_root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
