"""Skills-First Control — fail-closed closeout gate.

A task must NOT close merely because files changed or tests passed. This gate
verifies, against an execution manifest, that:

  1. the manifest is schema-valid, IN a closeable state, and NOT EXPIRED
     (SFC-GAP-C: an abandoned manifest that outlived its TTL no longer
     authorizes anything — expiry is checked before any other evaluation);
  2. every selected skill is still registered + active;
  3. each selected skill's command file still hashes to the value captured at
     resolution time (no silent command drift between resolve and close);
  4. every changed file is inside allowed_paths and outside forbidden_paths
     (GLOBAL_EXEMPT bookkeeping paths excepted);
  5. skill-use evidence exists (a declared evidence path that resolves, or a
     skill-execution receipt referencing this task/skill).

Any failure -> CLOSE_BLOCKED (exit 1). A missing/unreadable manifest -> exit 2.
Naming a skill is never sufficient; evidence must resolve on disk.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from .registries import REPO_ROOT, RegistryError, load_skills
from .manifest import ManifestError, is_expired, load_manifest, validate_manifest

RECEIPTS_DIR = REPO_ROOT / ".local" / "skill-execution-receipts"

# Bookkeeping paths that legitimately cross task ownership (mirrors
# pre_mutation_guard.GLOBAL_EXEMPT_PATHS).
GLOBAL_EXEMPT_PATHS = (
    "reports/capability-layer/gap-ledger.json",
    "registry/source-structure-baseline.json",
    ".local/supervisor/continuation-signal.json",
    "reports/supervisor/",
    ".local/skills-first/",
)


def _norm(p: str) -> str:
    return p.replace("\\", "/").lstrip("./")


def path_allowed(changed: str, allowed: list[str]) -> bool:
    """Glob-ish containment: supports exact, `dir/` prefix, `dir/**`, `*` suffix."""
    c = _norm(changed)
    for a in allowed:
        a = _norm(a)
        if a.endswith("/**"):
            base = a[:-3].rstrip("/")
            if c == base or c.startswith(base + "/"):
                return True
        elif a.endswith("/*"):
            base = a[:-2]
            if c.startswith(base + "/") and "/" not in c[len(base) + 1:]:
                return True
        elif a.endswith("*"):
            if c.startswith(a[:-1]):
                return True
        elif a.endswith("/"):
            if c.startswith(a):
                return True
        else:
            if c == a or c.startswith(a + "/"):
                return True
    return False


def _is_exempt(changed: str) -> bool:
    c = _norm(changed)
    return any(c.startswith(_norm(e)) for e in GLOBAL_EXEMPT_PATHS)


def _receipt_references(task_id: str, skill_ids: list[str]) -> bool:
    if not RECEIPTS_DIR.exists():
        return False
    for p in RECEIPTS_DIR.glob("*.yaml"):
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if task_id and task_id in text and any(s in text for s in skill_ids):
            return True
    return False


def evaluate(manifest: dict[str, Any], changed_files: list[str],
             evidence_paths: list[str] | None = None) -> dict[str, Any]:
    reasons: list[str] = []
    evidence_paths = evidence_paths or []

    errs = validate_manifest(manifest)
    if errs:
        reasons.extend(f"manifest_invalid: {e}" for e in errs)
        # An invalid manifest cannot be reasoned about further -> block now.
        return {"verdict": "CLOSE_BLOCKED", "reasons": reasons,
                "checks": {"manifest_valid": False}}

    if manifest.get("status") == "ABORTED":
        reasons.append("manifest status is ABORTED")

    expired = is_expired(manifest)
    if expired:
        reasons.append(
            f"manifest expired at {manifest.get('expires_at')!r} — an "
            "abandoned/stale manifest no longer authorizes its allowed_paths"
        )

    skills = {s.skill_id: s for s in load_skills()}
    checks: dict[str, Any] = {"manifest_valid": True, "manifest_expired": expired}

    # 2 + 3. skills active + command hash stable
    hash_ok = True
    for sid in manifest["selected_skill_ids"]:
        s = skills.get(sid)
        if s is None:
            reasons.append(f"selected skill '{sid}' no longer registered")
            hash_ok = False
            continue
        if not s.is_active:
            reasons.append(f"selected skill '{sid}' is not active (status={s.status})")
        cmd_path = REPO_ROOT / s.command_file if s.command_file else None
        captured = (manifest.get("skill_hashes") or {}).get(sid, "")
        if cmd_path and cmd_path.exists() and captured:
            cur = hashlib.sha256(cmd_path.read_bytes()).hexdigest()
            if cur != captured:
                reasons.append(
                    f"command for skill '{sid}' drifted since resolution "
                    f"({captured[:12]}->{cur[:12]})")
                hash_ok = False
        elif not captured:
            reasons.append(f"no captured hash for skill '{sid}'")
            hash_ok = False
    checks["skill_hashes_stable"] = hash_ok

    # 4. changed files within allowed_paths, outside forbidden_paths
    allowed = manifest.get("allowed_paths") or []
    forbidden = manifest.get("forbidden_paths") or []
    out_of_scope = []
    forbidden_hits = []
    for f in changed_files:
        if _is_exempt(f):
            continue
        if forbidden and path_allowed(f, forbidden):
            forbidden_hits.append(f)
        elif not path_allowed(f, allowed):
            out_of_scope.append(f)
    if out_of_scope:
        reasons.append(f"changed files outside allowed_paths: {out_of_scope[:8]}")
    if forbidden_hits:
        reasons.append(f"changed files hit forbidden_paths: {forbidden_hits[:8]}")
    checks["all_changes_in_scope"] = not out_of_scope and not forbidden_hits

    # 5. skill-use evidence exists
    resolved_ev = [e for e in evidence_paths if (REPO_ROOT / _norm(e)).exists()]
    receipt = _receipt_references(manifest["task_id"], manifest["selected_skill_ids"])
    has_evidence = bool(resolved_ev) or receipt
    if not has_evidence:
        reasons.append("no skill-use evidence (no resolving evidence path and no "
                       "receipt referencing this task+skill)")
    checks["skill_use_evidence"] = has_evidence
    checks["resolved_evidence_paths"] = resolved_ev
    checks["receipt_found"] = receipt

    verdict = "CLOSE_OK" if not reasons else "CLOSE_BLOCKED"
    return {"verdict": verdict, "reasons": reasons, "checks": checks,
            "execution_id": manifest.get("execution_id")}


def _main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Skills-First closeout gate")
    ap.add_argument("--manifest", required=True, help="execution_id or path")
    ap.add_argument("--changed-files", nargs="*", default=[],
                    help="explicit changed file list")
    ap.add_argument("--changed-from-git", action="store_true",
                    help="derive changed files from `git diff --name-only HEAD`")
    ap.add_argument("--evidence", nargs="*", default=[])
    ap.add_argument("--close", action="store_true",
                    help="on CLOSE_OK, mark the manifest CLOSED")
    args = ap.parse_args(argv)

    try:
        m = load_manifest(args.manifest)
    except (ManifestError, RegistryError) as exc:
        print(json.dumps({"verdict": "CONFIG_ERROR", "error": str(exc)}), file=sys.stderr)
        return 2

    changed = list(args.changed_files)
    if args.changed_from_git:
        import subprocess
        r = subprocess.run(["git", "diff", "--name-only", "HEAD"],
                           capture_output=True, text=True, cwd=str(REPO_ROOT))
        changed += [x.strip() for x in r.stdout.splitlines() if x.strip()]

    result = evaluate(m, changed, args.evidence)
    print(json.dumps(result, indent=2))

    if result["verdict"] == "CLOSE_OK" and args.close:
        from .manifest import set_status
        set_status(m["execution_id"], "CLOSED", final_outcome="closeout_gate_passed")
    return 0 if result["verdict"] == "CLOSE_OK" else 1


if __name__ == "__main__":
    raise SystemExit(_main())
