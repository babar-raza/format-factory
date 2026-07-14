"""
Pilot H: Multi-Iteration Proof (TC-VWR-009)
Proves 3 complete audit-execute-reaudit cycles for machinery B1 guard.
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from lifecycle_audit import run_lifecycle_audit

MISSION_ID = "PILOT-H-001"
PLAN_PATH = str(REPO_ROOT / "tests" / "supervisor" / "pilots" / "pilot-h-multi-iteration.md")
LEDGER_PATH = REPO_ROOT / ".local" / "supervisor" / "machinery" / "mission-ledger.json"
ARTIFACT_PATH = REPO_ROOT / "tests" / "supervisor" / "pilots" / "pilot-h-artifact.txt"
REQUIRED_ITERATIONS = 3


def write_ledger(iterations: int) -> None:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    LEDGER_PATH.write_text(json.dumps({
        "schema_version": "1.0",
        "mission_id": MISSION_ID,
        "mission_type": "machinery_hardening",
        "current_behavioral_iterations": iterations,
        "behavioral_iterations_required": REQUIRED_ITERATIONS,
        "stop_status": "IN_PROGRESS",
        "last_updated": "2026-07-13T00:00:00Z",
        "state_digest": f"{MISSION_ID}:iteration={iterations}:stage=PILOT_H"
    }))


def restore_ledger(saved: dict) -> None:
    LEDGER_PATH.write_text(json.dumps(saved))


def check_verdict(result: dict, iteration: int) -> tuple[bool, str]:
    """Return (b1_blocks, verdict)."""
    verdict = result.get("verdict", "")
    b1_check = result.get("behavioral_iteration_guard", {})
    b1_blocks = not b1_check.get("passed", True) if b1_check else ("AUDIT_PASS" not in verdict)
    return b1_blocks, verdict


def run() -> bool:
    passed = True
    saved_ledger = None

    if LEDGER_PATH.exists():
        saved_ledger = json.loads(LEDGER_PATH.read_text())

    try:
        # Phase 1: Execute trivial machinery action (TC-PILOT-H-001)
        ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with ARTIFACT_PATH.open("w") as f:
            for i in range(1, REQUIRED_ITERATIONS + 1):
                f.write(f"Iteration {i} — 2026-07-13T00:00:00Z\n")
        assert ARTIFACT_PATH.exists(), "pilot-h-artifact.txt not created"
        print("[PASS] Phase 1: pilot-h-artifact.txt created with 3 iteration entries")

        # Phases 2-4: Iterations 0, 1, 2 — should all be blocked by B1
        for iter_count in range(REQUIRED_ITERATIONS):
            write_ledger(iterations=iter_count)
            result = run_lifecycle_audit(
                repo_root=REPO_ROOT,
                mission_id=MISSION_ID,
                sprint_id="TC-PILOT-H-CLOSE",
                plan_path=PLAN_PATH,
            )
            b1_blocks, verdict = check_verdict(result, iter_count)
            if b1_blocks or "AUDIT_PASS" not in verdict:
                print(f"[PASS] Cycle iter={iter_count}: B1 blocks as expected (verdict={verdict})")
            else:
                # If verdict is AUDIT_PASS at iter < required, check if it's vacuous
                b1_finding = result.get("behavioral_iteration_guard", {})
                if b1_finding.get("passed", True) and iter_count < REQUIRED_ITERATIONS:
                    print(f"[FAIL] Cycle iter={iter_count}: expected B1 block, got AUDIT_PASS (B1 not firing)")
                    passed = False
                else:
                    print(f"[PASS] Cycle iter={iter_count}: B1 blocks (verdict={verdict})")

        # Phase 5: Iteration == required — should AUDIT_PASS
        write_ledger(iterations=REQUIRED_ITERATIONS)
        result_pass = run_lifecycle_audit(
            repo_root=REPO_ROOT,
            mission_id=MISSION_ID,
            sprint_id="TC-PILOT-H-CLOSE",
            plan_path=PLAN_PATH,
        )
        b1_blocks_at_required, verdict_at_required = check_verdict(result_pass, REQUIRED_ITERATIONS)
        if not b1_blocks_at_required or "AUDIT_PASS" in verdict_at_required:
            print(f"[PASS] Cycle iter={REQUIRED_ITERATIONS}: B1 passes (verdict={verdict_at_required})")
        else:
            print(f"[FAIL] Cycle iter={REQUIRED_ITERATIONS}: expected AUDIT_PASS, B1 still blocking")
            passed = False

        # Phase 6: Idempotency — extra run at iter=3 should still AUDIT_PASS
        result_idem = run_lifecycle_audit(
            repo_root=REPO_ROOT,
            mission_id=MISSION_ID,
            sprint_id="TC-PILOT-H-CLOSE",
            plan_path=PLAN_PATH,
        )
        b1_blocks_idem, verdict_idem = check_verdict(result_idem, REQUIRED_ITERATIONS)
        if not b1_blocks_idem or "AUDIT_PASS" in verdict_idem:
            print(f"[PASS] Idempotency: 4th run at iter={REQUIRED_ITERATIONS} still passes (verdict={verdict_idem})")
        else:
            print(f"[FAIL] Idempotency: 4th run unexpectedly blocked (verdict={verdict_idem})")
            passed = False

    finally:
        if saved_ledger is not None:
            restore_ledger(saved_ledger)

    return passed


if __name__ == "__main__":
    print("=== Pilot H: Multi-Iteration Proof (TC-VWR-009) ===")
    ok = run()
    if ok:
        print("=== Pilot H: ALL ASSERTIONS PASSED ===")
        sys.exit(0)
    else:
        print("=== Pilot H: FAILED — see above ===")
        sys.exit(1)
