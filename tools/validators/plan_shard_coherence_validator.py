#!/usr/bin/env python3
"""Plan Shard Coherence Validator — 10 checks ensuring decomposition preserves all information.

Verifies that the bootstrap decomposition is internally consistent and complete.
"""
import argparse
import csv
import glob
import os
import sys
import yaml


def _load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def check_all_requirements_mapped(bundle_dir):
    """Check 1: Every REQ-* in requirement-index maps to at least one TC-*."""
    req_index = _load_yaml(os.path.join(bundle_dir, "requirement-index.yaml"))
    reqs = req_index.get("requirements", [])

    map_path = os.path.join(bundle_dir, "requirement-to-taskcard-map-v3.csv")
    mapped_reqs = set()
    if os.path.isfile(map_path):
        with open(map_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rid = row.get("requirement_id", "").strip()
                tids = row.get("taskcard_ids", "").strip()
                if rid and tids:
                    mapped_reqs.add(rid)

    unmapped = []
    for r in reqs:
        rid = r.get("id", "")
        if rid and rid not in mapped_reqs:
            unmapped.append(rid)

    if unmapped:
        return f"FAIL: {len(unmapped)} requirements not mapped to taskcards: {unmapped[:5]}"
    return None


def check_all_sections_referenced(bundle_dir):
    """Check 2: Every SEC-* in section-index is consumed by at least one lane packet."""
    sec_index = _load_yaml(os.path.join(bundle_dir, "section-index.yaml"))
    sections = sec_index.get("sections", [])
    sec_ids = {s.get("id", "") for s in sections}

    map_path = os.path.join(bundle_dir, "section-to-lane-packet-map.csv")
    referenced_secs = set()
    if os.path.isfile(map_path):
        with open(map_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sid = row.get("section_id", "").strip()
                if sid:
                    referenced_secs.add(sid)

    orphans = sec_ids - referenced_secs - {""}
    if orphans:
        return f"FAIL: {len(orphans)} sections not referenced by any lane packet: {sorted(orphans)[:5]}"
    return None


def check_artifacts_registered(bundle_dir):
    """Check 3: All files in bundle are registered in artifact-registry.yaml."""
    all_files = set()
    for root, dirs, files in os.walk(bundle_dir):
        for f in files:
            rel = os.path.relpath(os.path.join(root, f), bundle_dir).replace("\\", "/")
            all_files.add(rel)

    ar = _load_yaml(os.path.join(bundle_dir, "artifact-registry.yaml"))
    registered = set()
    groups = ar.get("groups", ar.get("artifact_groups", []))
    for g in (groups or []):
        for a in g.get("artifacts", g.get("files", [])):
            if isinstance(a, str):
                registered.add(a)
            elif isinstance(a, dict):
                registered.add(a.get("path", a.get("file", "")))

    unregistered = all_files - registered - {""}
    coverage = len(all_files - unregistered) / max(len(all_files), 1) * 100
    if coverage < 80:
        return f"WARN: artifact registry covers {coverage:.0f}% of files ({len(unregistered)} unregistered)"
    return None


def check_invariants_propagated(bundle_dir):
    """Check 4: invariant-propagation-matrix.csv has no empty cells."""
    matrix_path = os.path.join(bundle_dir, "invariant-propagation-matrix.csv")
    if not os.path.isfile(matrix_path):
        return "FAIL: invariant-propagation-matrix.csv missing"

    with open(matrix_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        gaps = []
        for row_num, row in enumerate(reader, 2):
            for col_idx, cell in enumerate(row):
                if col_idx >= 2 and cell.strip() == "":
                    gaps.append(f"row {row_num} col {col_idx}")

    if gaps:
        return f"FAIL: Invariant propagation matrix has {len(gaps)} gaps: {gaps[:3]}"
    return None


def check_product_locked(bundle_dir):
    """Check 5: No pre-Wave-4 taskcard allows src/ modifications."""
    tc_dir = os.path.join(bundle_dir, "taskcards", "by-lane")
    tc_files = glob.glob(os.path.join(tc_dir, "*", "TC-*.yaml"))

    violations = []
    for fp in tc_files:
        tc = _load_yaml(fp)
        wave = str(tc.get("wave", ""))
        if wave in ("0", "1A", "1B", "2", "3"):
            allowed = tc.get("allowed_paths", [])
            for p in (allowed or []):
                if p.startswith("src/"):
                    violations.append(f"{tc.get('id', fp)} allows src/ in wave {wave}")
                    break

    if violations:
        return f"FAIL: Pre-Wave-4 taskcards allow src/: {violations[:3]}"
    return None


def check_no_legacy_canonical_names(bundle_dir):
    """Check 6: No taskcard uses format-prefixed name as canonical target."""
    tc_dir = os.path.join(bundle_dir, "taskcards", "by-lane")
    tc_files = glob.glob(os.path.join(tc_dir, "*", "TC-*.yaml"))

    violations = []
    for fp in tc_files:
        tc = _load_yaml(fp)
        for field in ["canonical_class", "canonical_namespace"]:
            val = tc.get(field, "")
            if val and any(val.startswith(p) for p in ["Fods", "Fodt"]):
                violations.append(f"{tc.get('id', fp)}.{field}={val}")

    if violations:
        return f"FAIL: Legacy canonical names found: {violations[:3]}"
    return None


def check_lane_packet_completeness(bundle_dir):
    """Check 7: All 16 lane packets exist."""
    lp_dir = os.path.join(bundle_dir, "lane-packets")
    expected = 16
    lp_files = glob.glob(os.path.join(lp_dir, "lane-*.md"))
    if len(lp_files) < expected:
        return f"FAIL: Only {len(lp_files)}/{expected} lane packets found"
    return None


def check_wave_plan_consistency(bundle_dir):
    """Check 8: wave-plan.yaml wave entries match wave_index in taskcards/index.yaml."""
    wp = _load_yaml(os.path.join(bundle_dir, "wave-plan.yaml"))
    waves_in_plan = {str(w.get("wave", w.get("id", w.get("wave_id", "")))) for w in wp.get("waves", [])}

    tc_index = _load_yaml(os.path.join(bundle_dir, "taskcards", "index.yaml"))
    waves_in_index = set(tc_index.get("wave_index", {}).keys())

    missing = waves_in_index - waves_in_plan - {""}
    if missing:
        return f"WARN: Wave index references waves not in wave-plan: {missing}"
    return None


def check_taskcard_requirement_traceability(bundle_dir):
    """Check 9: Every taskcard references at least one REQ-*."""
    tc_dir = os.path.join(bundle_dir, "taskcards", "by-lane")
    tc_files = glob.glob(os.path.join(tc_dir, "*", "TC-*.yaml"))

    no_reqs = []
    for fp in tc_files:
        tc = _load_yaml(fp)
        reqs = tc.get("requirement_ids", [])
        if not reqs:
            no_reqs.append(tc.get("id", os.path.basename(fp)))

    if no_reqs:
        return f"WARN: {len(no_reqs)} taskcards without requirement_ids: {no_reqs[:5]}"
    return None


def check_gate11_blocked(bundle_dir):
    """Check 10: No taskcard or evidence claims Gate 11 approved."""
    tc_dir = os.path.join(bundle_dir, "taskcards", "by-lane")
    tc_files = glob.glob(os.path.join(tc_dir, "*", "TC-*.yaml"))

    violations = []
    for fp in tc_files:
        tc = _load_yaml(fp)
        policy = tc.get("gate11_policy", "")
        if policy and "NOT" not in policy.upper():
            violations.append(tc.get("id", os.path.basename(fp)))

    ev_path = os.path.join(bundle_dir, "evidence-declaration.yaml")
    if os.path.isfile(ev_path):
        ev = _load_yaml(ev_path)
        if ev.get("gate11_approved_by_agent", False):
            violations.append("evidence-declaration.yaml gate11_approved_by_agent=true")

    if violations:
        return f"FAIL: Gate 11 appears approved: {violations[:3]}"
    return None


def run_all_checks(bundle_dir):
    """Run all 10 coherence checks."""
    checks = [
        ("All requirements mapped", check_all_requirements_mapped),
        ("All sections referenced", check_all_sections_referenced),
        ("Artifacts registered", check_artifacts_registered),
        ("Invariants propagated", check_invariants_propagated),
        ("Product locked pre-Wave-4", check_product_locked),
        ("No legacy canonical names", check_no_legacy_canonical_names),
        ("Lane packet completeness", check_lane_packet_completeness),
        ("Wave plan consistency", check_wave_plan_consistency),
        ("Taskcard-requirement traceability", check_taskcard_requirement_traceability),
        ("Gate 11 blocked", check_gate11_blocked),
    ]

    failures = []
    warnings = []
    passes = []

    for name, check_fn in checks:
        result = check_fn(bundle_dir)
        if result:
            if result.startswith("WARN"):
                warnings.append((name, result))
            else:
                failures.append((name, result))
        else:
            passes.append(name)

    print("Plan Shard Coherence Validator")
    print(f"Bundle: {bundle_dir}")
    print(f"Checks: {len(checks)}")
    print(f"Pass: {len(passes)}")
    print(f"Fail: {len(failures)}")
    print(f"Warn: {len(warnings)}")
    print()

    for name in passes:
        print(f"  PASS: {name}")
    for name, msg in warnings:
        print(f"  {msg}")
    for name, msg in failures:
        print(f"  {msg}")

    if failures:
        print(f"\nVERDICT: FAIL ({len(failures)} failures)")
        return 1
    else:
        print(f"\nVERDICT: PASS (with {len(warnings)} warnings)")
        return 0


def main():
    parser = argparse.ArgumentParser(description="Plan Shard Coherence Validator")
    parser.add_argument("bundle_dir", help="Path to the bootstrap bundle directory")
    args = parser.parse_args()
    sys.exit(run_all_checks(args.bundle_dir))


if __name__ == "__main__":
    main()
