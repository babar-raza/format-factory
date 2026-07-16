"""validate_skills_first_control.py — Skills-First Control gate (SFC-V001).

Standalone, FAIL-CLOSED validator that a CI job, a closeout step, or a pre-commit
hook can call to assert the skills-first control system is internally consistent.
It composes three checks:

  A. Parity/coverage audit (tools.governance.skills_first.audit)
     -> CRITICAL findings always fail; HIGH fail unless --warn-high.
  B. Execution-manifest schema self-test: the schema file exists, is valid JSON,
     and a freshly minted manifest validates against the module's own checker.
  C. Policy self-consistency: docs/governance/skill-only-policy.yaml references
     the concrete primitives (execution manifest schema) and carries no known
     stale enforcement-status (EP-007 must not claim NOT_IMPLEMENTED while the
     pre-commit hook is installed).

Exit codes:
  0 = PASS (or PASS_WITH_WARNINGS under --warn-high)
  1 = FAIL (control inconsistency present)
  2 = CONFIG_ERROR (registry/schema unreadable — never a clean pass)

This validator is intentionally standalone (mirrors ci_skill_attribution_check.py
and validate_plan_skill_routes.py) so it composes into any layer without
depending on the 226-validator runner. Wiring it into that runner as the next
reserved validator id is the recommended follow-up (documented, not silent).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.governance.skills_first import audit as sfc_audit  # noqa: E402
from tools.governance.skills_first import exceptions as sfc_exc  # noqa: E402
from tools.governance.skills_first import manifest as sfc_manifest  # noqa: E402
from tools.governance.skills_first.registries import (  # noqa: E402
    RegistryError, load_policy,
)

SCHEMA_FILE = REPO_ROOT / ".supervisor" / "schemas" / "execution-manifest.schema.json"


def check_manifest_schema() -> list[str]:
    errs: list[str] = []
    if not SCHEMA_FILE.exists():
        return [f"execution-manifest schema missing: {SCHEMA_FILE}"]
    try:
        json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
    except ValueError as exc:
        return [f"execution-manifest schema not valid JSON: {exc}"]
    # Mint a manifest via the module and confirm it self-validates.
    try:
        m = sfc_manifest.create_manifest(
            task_id="SFC-SELFTEST",
            agent_type="CI",
            requested_operation="schema self-test",
            selected_skill_ids=_any_active_skill(),
            allowed_paths=["tools/governance/skills_first/**"],
            resolution_rationale="validator self-test",
            write=False,
        )
    except sfc_manifest.ManifestError as exc:
        return [f"could not mint self-test manifest: {exc}"]
    verrs = sfc_manifest.validate_manifest(m)
    if verrs:
        errs.append("self-test manifest failed validation: " + "; ".join(verrs))
    # Negative control: an empty-skill manifest MUST be rejected.
    try:
        sfc_manifest.create_manifest(
            task_id="SFC-NEG", agent_type="CI", requested_operation="neg",
            selected_skill_ids=[], allowed_paths=["x/**"], write=False)
        errs.append("manifest creator accepted an empty skill list (not fail-closed)")
    except sfc_manifest.ManifestError:
        pass
    return errs


def _any_active_skill() -> list[str]:
    from tools.governance.skills_first.registries import load_skills
    for s in load_skills():
        if s.is_active and s.command_file and (REPO_ROOT / s.command_file).exists():
            return [s.skill_id]
    raise RegistryError("no active skill with an on-disk command file found")


def check_policy_consistency() -> list[str]:
    errs: list[str] = []
    policy = load_policy()
    text = (REPO_ROOT / "docs" / "governance" / "skill-only-policy.yaml").read_text(
        encoding="utf-8")
    if "execution-manifest.schema.json" not in text:
        errs.append("policy does not reference the execution-manifest schema")
    # EP-007 staleness: NOT_IMPLEMENTED while the hook is installed.
    hook_installed = (REPO_ROOT / ".git" / "hooks" / "pre-commit").exists()
    for ep in policy.get("enforcement_points", []):
        if isinstance(ep, dict) and ep.get("id") == "EP-007":
            if hook_installed and ep.get("current_status") == "NOT_IMPLEMENTED":
                errs.append("EP-007 stale: declares NOT_IMPLEMENTED but hook installed")
    return errs


def run(warn_high: bool) -> dict:
    try:
        report = sfc_audit.run_audit(scan_generators=False)
    except RegistryError as exc:
        return {"verdict": "CONFIG_ERROR", "error": str(exc)}

    try:
        schema_errs = check_manifest_schema()
        policy_errs = check_policy_consistency()
        accepted_sigs, invalid_exceptions = sfc_exc.active_accepted_signatures()
    except (RegistryError, sfc_exc.ExceptionError) as exc:
        return {"verdict": "CONFIG_ERROR", "error": str(exc)}

    sc = report["severity_counts"]

    # HIGH findings block UNLESS a valid, non-expired exception covers the exact
    # signature. Uncovered HIGH -> blocking (unless --warn-high). Any INVALID
    # exception is itself a hard failure (fail-closed): expired/broad/ownerless
    # exceptions can never launder a finding.
    uncovered_high = []
    for f in report["findings"]:
        if f.get("severity") != "HIGH":
            continue
        sig = sfc_exc.finding_signature(f)
        if sig not in accepted_sigs:
            uncovered_high.append(sig)

    fail = (
        sc["CRITICAL"] > 0
        or bool(schema_errs)
        or bool(policy_errs)
        or bool(invalid_exceptions)
    )
    if uncovered_high and not warn_high:
        fail = True

    verdict = "FAIL" if fail else (
        "PASS_WITH_WARNINGS" if (uncovered_high or sc["MEDIUM"]) else "PASS")
    return {
        "verdict": verdict,
        "audit_severity": sc,
        "schema_errors": schema_errs,
        "policy_errors": policy_errs,
        "invalid_exceptions": invalid_exceptions,
        "uncovered_high_signatures": uncovered_high,
        "accepted_exception_count": len(accepted_sigs),
        "audit_critical": [f for f in report["findings"]
                           if f.get("severity") == "CRITICAL"],
        "audit_high_count": sc["HIGH"],
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Skills-First Control gate")
    ap.add_argument("--warn-high", action="store_true",
                    help="treat HIGH parity findings as warnings")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    result = run(args.warn_high)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"[skills-first-control] verdict={result['verdict']}")
        if result.get("error"):
            print("  error:", result["error"])
        for k in ("schema_errors", "policy_errors", "uncovered_high_signatures"):
            for e in result.get(k, []):
                print(f"  {k}: {e}")
        for ie in result.get("invalid_exceptions", []):
            print(f"  invalid_exception: {ie['exception_id']} -> {ie['errors']}")
        if result.get("audit_severity"):
            print("  audit:", result["audit_severity"],
                  "| accepted_exceptions:", result.get("accepted_exception_count", 0))

    if result["verdict"] == "CONFIG_ERROR":
        return 2
    return 1 if result["verdict"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
