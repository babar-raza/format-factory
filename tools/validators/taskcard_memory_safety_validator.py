#!/usr/bin/env python3
"""Taskcard Memory Safety Validator — 13 checks ensuring taskcards are self-contained.

Each taskcard must be usable by a weak agent without access to the full master plan.
"""
import argparse
import glob
import os
import sys
import yaml


def _load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def check_invariants_present(tc, tc_path):
    """Check 1: Global invariants referenced or embedded."""
    inv = tc.get("global_invariants", [])
    if not inv:
        return f"FAIL: {tc_path} — no global_invariants field"
    return None


def check_no_full_plan_refs(tc, tc_path):
    """Check 2: No references to 'read the full plan' or 'see master plan'."""
    text = yaml.dump(tc).lower()
    bad_phrases = ["read the full plan", "see master plan", "read master plan",
                   "load the full plan", "see full plan"]
    for phrase in bad_phrases:
        if phrase in text:
            return f"FAIL: {tc_path} — contains '{phrase}'"
    return None


def check_spec_context_on_product(tc, tc_path):
    """Check 3: Product taskcards (wave 5+) must have spec_context or spec_naming_rule."""
    wave = str(tc.get("wave", ""))
    if wave in ("5", "6", "7"):
        has_spec = tc.get("spec_context") or tc.get("spec_naming_rule")
        if not has_spec:
            text = yaml.dump(tc)
            if "spec_qname" in text or "canonical" in text.lower():
                return None  # has spec references inline
            return f"FAIL: {tc_path} — product taskcard (wave {wave}) missing spec_context"
    return None


def check_no_legacy_canonical(tc, tc_path):
    """Check 4: No format-prefixed names used as primary canonical targets."""
    text = yaml.dump(tc)
    # Only flag if these appear as "canonical_class:" values, not as facade references
    for field in ["canonical_class", "canonical_namespace"]:
        val = tc.get(field, "")
        if val and any(val.startswith(p) for p in ["Fods", "Fodt", "Fod"]):
            return f"FAIL: {tc_path} — {field}={val} uses format-prefix as canonical"
    return None


def check_paths_defined(tc, tc_path):
    """Check 5: allowed_paths and forbidden_paths defined."""
    if not tc.get("allowed_paths") and not tc.get("forbidden_paths"):
        return f"FAIL: {tc_path} — no allowed_paths or forbidden_paths"
    return None


def check_evidence_required(tc, tc_path):
    """Check 6: evidence_required field non-empty."""
    ev = tc.get("evidence_required", [])
    if not ev:
        return f"FAIL: {tc_path} — no evidence_required"
    return None


def check_stop_conditions(tc, tc_path):
    """Check 7: stop_conditions field present."""
    sc = tc.get("stop_conditions", [])
    if not sc:
        return f"FAIL: {tc_path} — no stop_conditions"
    return None


def check_no_gate11_claims(tc, tc_path):
    """Check 8: gate11_policy says NOT approved."""
    policy = tc.get("gate11_policy", "")
    if policy and "NOT" not in policy.upper() and "not" not in policy:
        return f"FAIL: {tc_path} — gate11_policy does not say NOT approved"
    return None


def check_capsule_exists(tc, tc_path, capsules_dir):
    """Check 9: Corresponding context capsule file exists."""
    tc_id = tc.get("id", "")
    capsule_path = os.path.join(capsules_dir, f"{tc_id}.yaml")
    if not os.path.isfile(capsule_path):
        return f"FAIL: {tc_path} — capsule missing: {capsule_path}"
    return None


def check_mission_present(tc, tc_path):
    """Check 10: mission field is non-empty."""
    mission = tc.get("mission", "")
    if not mission or len(str(mission).strip()) < 10:
        return f"FAIL: {tc_path} — mission empty or too short"
    return None


def check_depends_on_valid(tc, tc_path, all_tc_ids):
    """Check 11: depends_on references only known taskcard IDs."""
    deps = tc.get("depends_on", [])
    if deps:
        for dep in deps:
            if dep not in all_tc_ids:
                return f"FAIL: {tc_path} — depends_on references unknown TC: {dep}"
    return None


def check_section_ids_present(tc, tc_path):
    """Check 12: source_section_ids field present for non-coordinator cards."""
    role = tc.get("agent_role", "")
    if role != "coordinator":
        sids = tc.get("source_section_ids", [])
        if not sids:
            return f"WARN: {tc_path} — no source_section_ids"
    return None


def check_execution_steps(tc, tc_path):
    """Check 13: execution_steps field present and non-empty."""
    steps = tc.get("execution_steps", [])
    if not steps:
        return f"FAIL: {tc_path} — no execution_steps"
    return None


def run_all_checks(bundle_dir):
    """Run all 13 checks on all taskcards in the bundle."""
    tc_dir = os.path.join(bundle_dir, "taskcards", "by-lane")
    capsules_dir = os.path.join(bundle_dir, "taskcards", "context-capsules")

    tc_files = sorted(glob.glob(os.path.join(tc_dir, "*", "TC-*.yaml")))
    if not tc_files:
        print(f"ERROR: No taskcard files found in {tc_dir}")
        return 1

    # Collect all TC IDs first
    all_tc_ids = set()
    all_tcs = []
    for fp in tc_files:
        tc = _load_yaml(fp)
        tc_id = tc.get("id", os.path.basename(fp).replace(".yaml", ""))
        all_tc_ids.add(tc_id)
        all_tcs.append((fp, tc))

    checks = [
        check_invariants_present,
        check_no_full_plan_refs,
        check_spec_context_on_product,
        check_no_legacy_canonical,
        check_paths_defined,
        check_evidence_required,
        check_stop_conditions,
        check_no_gate11_claims,
        check_mission_present,
        check_execution_steps,
        check_section_ids_present,
    ]

    failures = []
    warnings = []
    total_checks = 0

    for fp, tc in all_tcs:
        for check_fn in checks:
            total_checks += 1
            result = check_fn(tc, fp)
            if result:
                if result.startswith("WARN"):
                    warnings.append(result)
                else:
                    failures.append(result)

        # Capsule check
        total_checks += 1
        result = check_capsule_exists(tc, fp, capsules_dir)
        if result:
            failures.append(result)

        # depends_on check
        total_checks += 1
        result = check_depends_on_valid(tc, fp, all_tc_ids)
        if result:
            failures.append(result)

    print(f"Taskcard Memory Safety Validator")
    print(f"Bundle: {bundle_dir}")
    print(f"Taskcards: {len(all_tcs)}")
    print(f"Checks run: {total_checks}")
    print(f"Failures: {len(failures)}")
    print(f"Warnings: {len(warnings)}")
    print()

    for f in failures:
        print(f"  {f}")
    for w in warnings:
        print(f"  {w}")

    if failures:
        print(f"\nVERDICT: FAIL ({len(failures)} failures)")
        return 1
    else:
        print(f"\nVERDICT: PASS (with {len(warnings)} warnings)")
        return 0


def main():
    parser = argparse.ArgumentParser(description="Taskcard Memory Safety Validator")
    parser.add_argument("bundle_dir", help="Path to the bootstrap bundle directory")
    args = parser.parse_args()
    sys.exit(run_all_checks(args.bundle_dir))


if __name__ == "__main__":
    main()
