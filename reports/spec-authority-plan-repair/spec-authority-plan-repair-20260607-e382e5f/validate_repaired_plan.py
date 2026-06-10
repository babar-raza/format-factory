#!/usr/bin/env python3
"""
validate_repaired_plan.py
Validator for FORMAT-FACTORY-SPEC-AUTHORITY-PLAN-REPAIR-FOR-SINGLE-GO-EXECUTION-001

Usage: python validate_repaired_plan.py [--run-dir <path>]

Exit code 0 = all checks pass
Exit code 1 = one or more failures
"""

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_FILES = [
    "authority-healing-state-machine.json",
    "authority-healing-state-machine.md",
    "taskcard-schema.json",
    "authority-healing-taskcards.json",
    "taskcard-state.json",
    "taskcard-transition-ledger.jsonl",
    "lane-ownership-map.json",
    "lane-ownership-map.md",
    "rollback-recovery-plan.json",
    "rollback-recovery-plan.md",
    "verification-gates.json",
    "verification-gates.md",
    "plan-readiness-review.md",
    "evidence-import-review.md",
    "required-plan-repairs.md",
    "repaired-plan.md",
    "repaired-plan.json",
    "adversarial-review.md",
    "evidence-bundle-contract.md",
    "plan-completeness-check.md",
    "final-summary.md",
]

TASKCARD_REQUIRED_FIELDS = [
    "taskcard_id", "title", "stream", "lane", "root_cause_ids",
    "evidence_source_ids", "affected_pipeline_stages", "affected_formats",
    "current_state", "allowed_paths", "forbidden_paths",
    "prerequisite_taskcards", "authority_inputs_required",
    "authority_outputs_expected", "implementation_scope", "non_goals",
    "blocking_gates", "validation_commands", "negative_tests_required",
    "pilot_required", "evidence_required", "state_transition_rules",
    "rollback_plan", "risk_level", "owner_lane",
    "independent_verifier_lane", "final_state", "closure_criteria",
]

VALID_LANES = {
    "L-COORD", "L-EVIDENCE", "L-STATEMACHINE", "L-GOVERNANCE",
    "L-SCHEMA", "L-SELECTOR", "L-VERIFY", "L-ADVERSARIAL", "L-BUNDLE",
}

TERMINAL_STATES = {"CLOSED_VERIFIED", "CLOSED_WITH_AUTHORITY_DEBT", "REJECTED_FALSE_CLAIM"}


def load_json(path: Path, checks: list) -> dict | None:
    try:
        with path.open() as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        checks.append((False, f"JSON parse error in {path.name}: {e}"))
        return None
    except FileNotFoundError:
        checks.append((False, f"File not found: {path.name}"))
        return None


def run_checks(run_dir: Path) -> list:
    checks = []

    # 1. All required files exist
    for fname in REQUIRED_FILES:
        p = run_dir / fname
        exists = p.exists()
        checks.append((exists, f"Required file exists: {fname}"))

    # 2. State machine JSON
    sm_path = run_dir / "authority-healing-state-machine.json"
    sm = load_json(sm_path, checks)
    if sm is not None:
        # State count = 32
        state_count = len(sm.get("states", []))
        checks.append((state_count == 32, f"State count = 32 (got {state_count})"))

        # declared state_count matches
        declared = sm.get("state_count", -1)
        checks.append((declared == 32, f"Declared state_count = 32 (got {declared})"))

        # Terminal states present
        state_ids = {s["state_id"] for s in sm.get("states", [])}
        for ts in TERMINAL_STATES:
            checks.append((ts in state_ids, f"Terminal state present: {ts}"))

        # Terminal flags
        terminal_flagged = {s["state_id"] for s in sm.get("states", []) if s.get("terminal")}
        checks.append((terminal_flagged == TERMINAL_STATES,
                        f"Exactly 3 states marked terminal (got {terminal_flagged})"))

    # 3. Taskcard schema JSON
    ts_path = run_dir / "taskcard-schema.json"
    ts = load_json(ts_path, checks)
    checks.append((ts is not None, "taskcard-schema.json is valid JSON"))

    # 4. All taskcards JSON
    tc_path = run_dir / "authority-healing-taskcards.json"
    tc_data = load_json(tc_path, checks)
    state_machine_ids = set()
    if sm:
        state_machine_ids = {s["state_id"] for s in sm.get("states", [])}

    if tc_data is not None:
        taskcards = tc_data.get("taskcards", [])
        count = len(taskcards)
        checks.append((count >= 24, f"Taskcard count >= 24 (got {count})"))

        # All required fields
        tca_ids = set()
        for tc in taskcards:
            tca_id = tc.get("taskcard_id", "UNKNOWN")
            tca_ids.add(tca_id)
            for field in TASKCARD_REQUIRED_FIELDS:
                checks.append((field in tc,
                                f"Taskcard {tca_id} has required field: {field}"))
            # Lane is valid
            lane = tc.get("lane", "")
            checks.append((lane in VALID_LANES,
                            f"Taskcard {tca_id} has valid lane: {lane}"))
            # current_state is in state machine
            if state_machine_ids:
                cs = tc.get("current_state", "")
                checks.append((cs in state_machine_ids,
                                f"Taskcard {tca_id} current_state '{cs}' exists in state machine"))
            # No src/ in allowed_paths (plan-repair sprint)
            allowed = tc.get("allowed_paths", [])
            has_src = any("src/" in str(p) for p in allowed)
            checks.append((not has_src,
                            f"Taskcard {tca_id} does not have src/ in allowed_paths"))

        # All prerequisite references exist
        for tc in taskcards:
            for prereq in tc.get("prerequisite_taskcards", []):
                checks.append((prereq in tca_ids,
                                f"Prerequisite {prereq} exists in taskcards"))

    # 5. Taskcard state JSON
    tstate_path = run_dir / "taskcard-state.json"
    tstate = load_json(tstate_path, checks)
    if tstate is not None:
        states = tstate.get("states", {})
        tca000 = states.get("TCA-000", {})
        tca000_state = tca000.get("state", "UNKNOWN")
        checks.append((tca000_state in ("IMPLEMENTING", "IMPLEMENTED", "VALIDATING"),
                        f"TCA-000 starts as IMPLEMENTING/IMPLEMENTED/VALIDATING (got {tca000_state})"))
        # TCA-000 should NOT be CLOSED_VERIFIED at initial write
        # (it closes at end of sprint but starts as IMPLEMENTING)

    # 6. Transition ledger JSONL
    ledger_path = run_dir / "taskcard-transition-ledger.jsonl"
    if ledger_path.exists():
        try:
            lines = [line for line in ledger_path.read_text().splitlines() if line.strip()]
            for i, line in enumerate(lines):
                try:
                    json.loads(line)
                except json.JSONDecodeError as e:
                    checks.append((False, f"Transition ledger line {i+1} is invalid JSON: {e}"))
            checks.append((True, f"Transition ledger JSONL valid ({len(lines)} entries)"))
        except Exception as e:
            checks.append((False, f"Transition ledger read error: {e}"))

    # 7. Lane ownership map
    lm_path = run_dir / "lane-ownership-map.json"
    lm = load_json(lm_path, checks)
    if lm is not None:
        lane_count = len(lm.get("lanes", []))
        checks.append((lane_count == 9, f"Lane count = 9 (got {lane_count})"))
        lm_ids = {l["lane_id"] for l in lm.get("lanes", [])}
        checks.append((lm_ids == VALID_LANES, f"All 9 expected lanes present"))

        # Overlap check: each exclusive_write_path assigned to at most one lane
        exclusive_map = {}
        for lane_def in lm.get("lanes", []):
            for path in lane_def.get("exclusive_write_paths", []):
                if path in exclusive_map:
                    checks.append((False,
                                    f"CONFLICT: {path} claimed exclusively by both {exclusive_map[path]} and {lane_def['lane_id']}"))
                else:
                    exclusive_map[path] = lane_def["lane_id"]
        if exclusive_map:
            checks.append((True, f"No exclusive write path conflicts ({len(exclusive_map)} exclusive paths)"))

    # 8. Repaired plan checks
    rp_path = run_dir / "repaired-plan.md"
    if rp_path.exists():
        content = rp_path.read_text(encoding="utf-8", errors="ignore")

        # No hardcoded Windows paths
        win_count = content.count("C:\\Users") + content.count("C:/Users/prora")
        checks.append((win_count == 0, f"No hardcoded Windows paths in repaired-plan.md (found {win_count})"))

        # No validated_by: human as default (without human_approval_required_reason context)
        # Safe pattern: "validated_by: independent_agent_verifier" is fine
        # Look for raw "validated_by.*human" not adjacent to an approval reason
        unsafe_human = re.findall(
            r'validated_by[:\s]+["\']?human["\']?',
            content, re.IGNORECASE
        )
        checks.append((len(unsafe_human) == 0,
                        f"No 'validated_by: human' as default in repaired-plan.md (found {len(unsafe_human)})"))

        # No warning-only spec_fact_refs
        warn_refs = re.findall(
            r'(?:warn|warning).{0,80}spec_fact_refs|spec_fact_refs.{0,80}(?:warn|warning)',
            content, re.IGNORECASE
        )
        checks.append((len(warn_refs) == 0,
                        f"No warning-only spec_fact_refs in repaired-plan.md (found {len(warn_refs)})"))

        # Must mention non-FODS formats or bypass
        multi_format = ("gnumeric" in content.lower() or "abw" in content.lower()
                        or "bypass" in content.lower())
        checks.append((multi_format, "Repaired plan covers non-FODS formats or bypass pilot"))

    # repaired-plan.json
    rp_json_path = run_dir / "repaired-plan.json"
    rp_json = load_json(rp_json_path, checks)
    if rp_json is not None:
        repairs = rp_json.get("repairs_applied", [])
        checks.append((len(repairs) >= 10, f"repairs_applied has >=10 entries (got {len(repairs)})"))
        state_count_json = rp_json.get("state_count", -1)
        checks.append((state_count_json == 32, f"repaired-plan.json state_count=32 (got {state_count_json})"))

    # 9. Rollback plan
    rp2_path = run_dir / "rollback-recovery-plan.json"
    rp2 = load_json(rp2_path, checks)
    if rp2 is not None:
        fm_count = len(rp2.get("failure_modes", []))
        checks.append((fm_count >= 12, f"Rollback plan covers >=12 failure modes (got {fm_count})"))

    # 10. Verification gates
    vg_path = run_dir / "verification-gates.json"
    vg = load_json(vg_path, checks)
    if vg is not None:
        gate_count = len(vg.get("gates", []))
        checks.append((gate_count == 20, f"Verification gates count = 20 (got {gate_count})"))
        all_local = all(not g.get("ci_available", True) for g in vg.get("gates", []))
        checks.append((all_local, "All verification gates have ci_available=false"))

    # 11. Evidence bundle contract
    ebc_path = run_dir / "evidence-bundle-contract.md"
    if ebc_path.exists():
        content = ebc_path.read_text(encoding="utf-8", errors="ignore")
        checks.append((len(content) > 200, "Evidence bundle contract is non-trivial"))

    return checks


def main():
    parser = argparse.ArgumentParser(description="Validate repaired plan artifacts")
    parser.add_argument("--run-dir", default=".", help="Directory containing plan artifacts")
    parser.add_argument("--check", default=None, help="Run only specified check category")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).resolve()
    print(f"Validating artifacts in: {run_dir}")
    print("=" * 60)

    checks = run_checks(run_dir)

    failures = []
    passes = []
    for passed, msg in checks:
        if passed:
            passes.append(msg)
            print(f"  PASS: {msg}")
        else:
            failures.append(msg)
            print(f"  FAIL: {msg}")

    print("=" * 60)
    print(f"Results: {len(passes)} passed, {len(failures)} failed")

    if failures:
        print(f"\nFAILURES:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("\nAll checks passed. Verdict: PLAN_REPAIRED_READY_FOR_SINGLE_GO_EXECUTION")
        sys.exit(0)


if __name__ == "__main__":
    main()
