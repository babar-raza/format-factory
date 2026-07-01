#!/usr/bin/env python3
"""Executable system-healing gate check (TC-GATE-002).

Evaluates lane acceptance criteria programmatically by inspecting the
repository. Replaces prose-only gate verdicts with testable checks.

Usage:
    python tools/supervisor/check_system_healing_gate.py [--json]

Exit codes:
    0 = gate PASSED (all lanes meet minimum criteria)
    1 = gate FAILED (one or more lanes below minimum)
    2 = gate CONDITIONAL (all critical lanes pass, non-critical have warnings)
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _file_exists(rel: str) -> bool:
    return (REPO_ROOT / rel).is_file()


def _file_lines(rel: str) -> int:
    p = REPO_ROOT / rel
    if not p.is_file():
        return 0
    try:
        return len(p.read_text(encoding="utf-8", errors="replace").splitlines())
    except OSError:
        return 0


def _dir_file_count(rel: str, ext: str = ".py") -> int:
    d = REPO_ROOT / rel
    if not d.is_dir():
        return 0
    return sum(1 for f in d.rglob(f"*{ext}") if f.is_file())


def _count_exports(module_path: str) -> int:
    """Count __all__ exports from a Python module."""
    p = REPO_ROOT / module_path
    if not p.is_file():
        return 0
    try:
        spec = importlib.util.spec_from_file_location("_mod", str(p))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return len(getattr(mod, "__all__", []))
    except Exception:
        return 0


def _sal_fact_count(format_id: str) -> int:
    """Count format-specific + base facts for a format from SAL runner."""
    sal_path = REPO_ROOT / "tools" / "specification-authority-layer" / "sal_master_runner.py"
    if not sal_path.is_file():
        return 0
    try:
        spec = importlib.util.spec_from_file_location("sal", str(sal_path))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        specific = mod._FORMAT_SPECIFIC_FACTS.get(format_id.lower(), [])
        return len(specific)
    except Exception:
        return 0


def _sal_workbench_verified_count(format_id: str) -> int:
    """Return the workbench_verified_fact_count for a format from sal-facts-latest.json.

    Added by A5 (spec-authority-healing sprint, 2026-06-22) to check that workbench-
    reviewed facts exist per format, not just template/bootstrap facts.
    Returns 0 if the file is missing or the format is not found.
    """
    sal_latest = REPO_ROOT / ".local" / "sal-output" / "sal-facts-latest.json"
    if not sal_latest.is_file():
        return 0
    try:
        data = json.loads(sal_latest.read_text(encoding="utf-8"))
        for result in data.get("results", []):
            if result.get("format_id", "").lower() == format_id.lower():
                return result.get("workbench_verified_fact_count", 0)
    except Exception:
        pass
    return 0


# ── Lane check functions ─────────────────────────────────────────────────────

def check_lane_1_sal() -> dict:
    """Lane 1: SAL Pipeline — modules exist, facts have depth."""
    sal_runner = "tools/specification-authority-layer/sal_master_runner.py"
    sal_lines = _file_lines(sal_runner)
    sal_modules = _dir_file_count("tools/specification-authority-layer")
    fods_facts = _sal_fact_count("fods")
    fodt_facts = _sal_fact_count("fodt")
    fods_wb_count = _sal_workbench_verified_count("fods")
    fodt_wb_count = _sal_workbench_verified_count("fodt")

    checks = {
        "sal_runner_exists": _file_exists(sal_runner),
        "sal_runner_lines_gte_500": sal_lines >= 500,
        "sal_module_count": sal_modules,
        "fods_format_specific_facts": fods_facts,
        "fodt_format_specific_facts": fodt_facts,
        "fods_facts_gte_10": fods_facts >= 10,
        "fodt_facts_gte_10": fodt_facts >= 10,
        # A5 (spec-authority-healing, 2026-06-22): workbench-verified depth checks
        # These ensure sal-facts-latest.json contains real workbench evidence, not
        # just bootstrap template facts that exist without spec text verification.
        "fods_workbench_verified_count": fods_wb_count,
        "fodt_workbench_verified_count": fodt_wb_count,
        "fods_workbench_verified_count_positive": fods_wb_count > 0,
        "fodt_workbench_verified_count_positive": fodt_wb_count > 0,
    }
    passed = all([
        checks["sal_runner_exists"],
        checks["sal_runner_lines_gte_500"],
        checks["fods_facts_gte_10"],
        checks["fodt_facts_gte_10"],
        checks["fods_workbench_verified_count_positive"],
        checks["fodt_workbench_verified_count_positive"],
    ])
    return {"lane": 1, "name": "SAL Pipeline", "passed": passed, "checks": checks}


def check_lane_2_capability() -> dict:
    """Lane 2: Capability Reintegration — gap ledger and capability map exist AND are consumed.

    TC-GATE-001: Hardened from file-existence-only to include consumption checks:
    - capability map has records (not just a file stub)
    - consumer subprocess is wired in autonomous_cycle.py (Step 3e)
    - consumer output directory exists (consumer has been invoked at least once)
    - action queue advisory_only is false (TC-C3-001 fix active)
    """
    # File-existence checks (original)
    # TC-CAP-008: prefer active split; fall back to full ledger
    gap_ledger_exists = (
        _file_exists("reports/capability-layer/gap-ledger-active.json")
        or _file_exists("reports/capability-layer/gap-ledger.json")
    )
    unified_map_exists = _file_exists("reports/capability-layer/unified-capability-map.json")
    action_queue_exists = _file_exists("reports/capability-layer/action-queue.json")
    cap_verifier_exists = _file_exists("tools/supervisor/capability_verifier.py")

    # Consumption checks (TC-GATE-001 hardening)
    cap_map_record_count = 0
    if unified_map_exists:
        try:
            data = json.loads((REPO_ROOT / "reports/capability-layer/unified-capability-map.json").read_text(encoding="utf-8"))
            cap_map_record_count = len(data.get("capabilities", []))
        except (json.JSONDecodeError, OSError):
            pass

    action_queue_not_advisory = False
    action_queue_hash_fresh = False
    if action_queue_exists:
        try:
            import hashlib
            aq = json.loads((REPO_ROOT / "reports/capability-layer/action-queue.json").read_text(encoding="utf-8"))
            action_queue_not_advisory = not aq.get("advisory_only", True)
            # TC-CAP-010: Verify source_ledger_hash matches current active ledger
            stored_hash = aq.get("source_ledger_hash", "")
            if stored_hash:
                # Check against active ledger first, then full ledger
                for ledger_rel in ("reports/capability-layer/gap-ledger-active.json",
                                   "reports/capability-layer/gap-ledger.json"):
                    ledger_path = REPO_ROOT / ledger_rel
                    if ledger_path.is_file():
                        current_hash = hashlib.sha256(ledger_path.read_bytes()).hexdigest()
                        if current_hash == stored_hash:
                            action_queue_hash_fresh = True
                        break
        except (json.JSONDecodeError, OSError):
            pass

    consumer_wired_in_cycle = False
    cycle_path = REPO_ROOT / "tools/supervisor/autonomous_cycle.py"
    if cycle_path.is_file():
        try:
            consumer_wired_in_cycle = "Step 3e: Capability Queue Consumer" in cycle_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            pass

    consumer_output_exists = (REPO_ROOT / ".local" / "capability-consumer" / "taskcards").is_dir()

    checks = {
        # File-existence (original)
        "gap_ledger_exists": gap_ledger_exists,
        "unified_cap_map_exists": unified_map_exists,
        "action_queue_exists": action_queue_exists,
        "capability_verifier_exists": cap_verifier_exists,
        # Consumption checks (TC-GATE-001)
        "cap_map_record_count": cap_map_record_count,
        "cap_map_has_records": cap_map_record_count > 0,
        "action_queue_not_advisory": action_queue_not_advisory,
        "action_queue_hash_fresh": action_queue_hash_fresh,
        "consumer_wired_in_autonomous_cycle": consumer_wired_in_cycle,
        "consumer_output_dir_exists": consumer_output_exists,
    }
    passed = all([
        checks["gap_ledger_exists"],
        checks["unified_cap_map_exists"],
        checks["action_queue_exists"],
        checks["cap_map_has_records"],
        checks["consumer_wired_in_autonomous_cycle"],
    ])
    return {"lane": 2, "name": "Capability Reintegration", "passed": passed, "checks": checks}


def check_lane_3_compiler() -> dict:
    """Lane 3: Compiler — 2-phase compiler exists with tests."""
    compiler = "tools/supervisor/capability_compiler.py"
    compiler_lines = _file_lines(compiler)
    test_exists = _file_exists("tests/supervisor/test_capability_compiler.py")

    checks = {
        "compiler_exists": _file_exists(compiler),
        "compiler_lines_gte_300": compiler_lines >= 300,
        "compiler_lines": compiler_lines,
        "compiler_tests_exist": test_exists,
    }
    passed = checks["compiler_exists"] and checks["compiler_lines_gte_300"]
    return {"lane": 3, "name": "Compiler", "passed": passed, "checks": checks}


def check_lane_4_skills() -> dict:
    """Lane 4: Skills/Prompts — skill files registered."""
    commands_dir = REPO_ROOT / ".claude" / "commands"
    skill_count = 0
    if commands_dir.is_dir():
        skill_count = sum(1 for f in commands_dir.rglob("*.md") if f.is_file())

    checks = {
        "commands_dir_exists": commands_dir.is_dir(),
        "skill_count": skill_count,
        "skill_count_gte_3": skill_count >= 3,
    }
    passed = checks["commands_dir_exists"] and checks["skill_count_gte_3"]
    return {"lane": 4, "name": "Skills/Prompts", "passed": passed, "checks": checks}


def check_lane_5_validators() -> dict:
    """Lane 5: Validators — governance_validators.py has all validators."""
    gov_val = "tools/supervisor/governance_validators.py"
    gov_lines = _file_lines(gov_val)
    test_lines = _file_lines("tests/supervisor/test_depth_validators.py")

    checks = {
        "governance_validators_exists": _file_exists(gov_val),
        "governance_validators_lines": gov_lines,
        "governance_validators_lines_gte_1000": gov_lines >= 1000,
        "depth_validator_tests_exist": _file_exists("tests/supervisor/test_depth_validators.py"),
        "depth_validator_test_lines": test_lines,
    }
    passed = (
        checks["governance_validators_exists"]
        and checks["governance_validators_lines_gte_1000"]
        and checks["depth_validator_tests_exist"]
    )
    return {"lane": 5, "name": "Validators", "passed": passed, "checks": checks}


def check_lane_6_ontology() -> dict:
    """Lane 6: QName Ontology — design YAMLs exist (in evidence root or repo)."""
    evidence_root = REPO_ROOT / ".local" / "evidences"
    yaml_count = 0
    if evidence_root.is_dir():
        yaml_count = sum(
            1 for f in evidence_root.rglob("*.yaml")
            if "ontology" in f.name.lower() or "qname" in f.name.lower()
               or "namespace" in f.name.lower() or "containment" in f.name.lower()
        )

    # Also check for format registry
    registry_exists = _file_exists("registry/format-registry.yaml")

    checks = {
        "ontology_yamls_found": yaml_count,
        "format_registry_exists": registry_exists,
    }
    # Lane 6 is PARTIAL — design artifacts exist but not deployed
    passed = registry_exists
    return {"lane": 6, "name": "QName Ontology", "passed": passed, "checks": checks}


def check_lane_14_supervision() -> dict:
    """Lane 14: Supervision Audit — supervisor infrastructure exists."""
    checks = {
        "supervisor_loop_exists": _file_exists("tools/supervisor/supervisor_loop.py"),
        "autonomous_cycle_exists": _file_exists("tools/supervisor/autonomous_cycle.py"),
        "governance_validators_exists": _file_exists("tools/supervisor/governance_validators.py"),
        "lane_enforcement_exists": _file_exists("tools/supervisor/lane_enforcement_validator.py"),
    }
    passed = all(checks.values())
    return {"lane": 14, "name": "Supervision Audit", "passed": passed, "checks": checks}


def check_lane_15_healing() -> dict:
    """Lane 15: Healing/Learning — failure analysis infrastructure exists."""
    checks = {
        "ai_learning_loop_exists": _file_exists("tools/supervisor/ai_learning_loop.py"),
        "bounded_repair_exists": _file_exists("tools/supervisor/bounded_repair_engine.py"),
        "anti_skip_checker_exists": _file_exists("tools/supervisor/anti_skip_checker.py"),
    }
    passed = sum(checks.values()) >= 2  # At least 2 of 3 modules
    return {"lane": 15, "name": "Healing/Learning", "passed": passed, "checks": checks}


# ── Gate evaluation ──────────────────────────────────────────────────────────

def check_lane_7_byp001_authority_depth() -> dict:
    """Lane 7: BYP-001 Advisory — formats with gap-ledger refs but 0 workbench facts.

    TC-GUARD-001 checks gap_ledger_ref PRESENCE only. A PRODUCT_SOURCE item citing
    a gap for a format with 0 workbench SAL facts satisfies the gate despite having
    no real spec authority. This lane identifies such formats as an advisory signal.

    Added by spec-authority-healing sprint (BYP-001 repair, 2026-06-22).
    Advisory-only: always passes (does not block sprint) but surfaces authority gaps.
    """
    # TC-CAP-008: prefer active split for Lane 7 gap analysis
    _gl_active = REPO_ROOT / "reports" / "capability-layer" / "gap-ledger-active.json"
    _gl_full = REPO_ROOT / "reports" / "capability-layer" / "gap-ledger.json"
    gap_ledger_path = _gl_active if _gl_active.is_file() else _gl_full
    sal_latest = REPO_ROOT / ".local" / "sal-output" / "sal-facts-latest.json"

    if not gap_ledger_path.is_file() or not sal_latest.is_file():
        return {
            "lane": 7,
            "name": "BYP-001 Authority Depth",
            "passed": True,
            "checks": {"advisory": True, "error": "gap-ledger or sal-facts not found"},
        }

    try:
        gaps = json.loads(gap_ledger_path.read_text(encoding="utf-8")).get("gaps", [])
        sal_data = json.loads(sal_latest.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "lane": 7,
            "name": "BYP-001 Authority Depth",
            "passed": True,
            "checks": {"advisory": True, "error": str(exc)},
        }

    # Build workbench count index from SAL output
    wb_counts: dict[str, int] = {}
    for result in sal_data.get("results", []):
        fmt = result.get("format_id", "").lower()
        wb_counts[fmt] = result.get("workbench_verified_fact_count", 0)

    # Find formats that have gap-ledger entries but 0 workbench facts
    gap_formats: set[str] = set()
    for g in gaps:
        fmt = g.get("format", "").lower()
        if fmt:
            gap_formats.add(fmt)

    zero_wb_formats = sorted(
        f for f in gap_formats if wb_counts.get(f, 0) == 0
    )
    positive_wb_formats = sorted(
        f for f in gap_formats if wb_counts.get(f, 0) > 0
    )

    checks = {
        "advisory": True,
        "gap_ledger_formats_total": len(gap_formats),
        "formats_with_gap_and_zero_wb_facts": len(zero_wb_formats),
        "formats_with_gap_and_positive_wb_facts": len(positive_wb_formats),
        "zero_wb_format_list": zero_wb_formats,
        # BYP-001 is resolved when all gap-referenced formats have workbench facts
        "byp001_zero_wb_format_count": len(zero_wb_formats),
    }
    # Advisory lane: always passes (non-critical), surfaces info only
    passed = True
    return {"lane": 7, "name": "BYP-001 Authority Depth", "passed": passed, "checks": checks}


CRITICAL_LANES = {1, 3, 5}  # SAL, Compiler, Validators must pass


def evaluate_gate() -> dict:
    """Run all lane checks and produce gate verdict."""
    lane_results = [
        check_lane_1_sal(),
        check_lane_2_capability(),
        check_lane_3_compiler(),
        check_lane_4_skills(),
        check_lane_5_validators(),
        check_lane_6_ontology(),
        check_lane_7_byp001_authority_depth(),
        check_lane_14_supervision(),
        check_lane_15_healing(),
    ]

    all_passed = all(r["passed"] for r in lane_results)
    critical_passed = all(
        r["passed"] for r in lane_results if r["lane"] in CRITICAL_LANES
    )
    failed_lanes = [r["lane"] for r in lane_results if not r["passed"]]

    if all_passed:
        verdict = "PASSED"
        exit_code = 0
    elif critical_passed:
        verdict = "CONDITIONAL"
        exit_code = 2
    else:
        verdict = "FAILED"
        exit_code = 1

    return {
        "verdict": verdict,
        "exit_code": exit_code,
        "all_passed": all_passed,
        "critical_passed": critical_passed,
        "failed_lanes": failed_lanes,
        "lane_results": lane_results,
    }


def check_healing_gate(repo_root=None, advisory: bool = True) -> dict:
    """Programmatic API for checking the system healing gate.

    Returns a dict with keys: exit_code, verdict, critical_passed, failed_lanes,
    advisory (bool), blocks_sprint (bool).

    When advisory=True (default / GATE_ADVISORY mode), blocks_sprint is always False
    so callers receive the signal without being blocked. Set advisory=False to enable
    GATE_STRICT mode where blocks_sprint reflects the actual exit_code.
    """
    result = evaluate_gate()
    blocks_sprint = False if advisory else (result["exit_code"] != 0)
    return {
        "exit_code": result["exit_code"],
        "verdict": result["verdict"],
        "critical_passed": result["critical_passed"],
        "all_passed": result["all_passed"],
        "failed_lanes": result["failed_lanes"],
        "lane_results": result["lane_results"],
        "advisory": advisory,
        "blocks_sprint": blocks_sprint,
    }


def main() -> int:
    result = evaluate_gate()
    use_json = "--json" in sys.argv

    if use_json:
        print(json.dumps(result, indent=2))
    else:
        print(f"System-Healing Gate: {result['verdict']}")
        print(f"Critical lanes passed: {result['critical_passed']}")
        print(f"All lanes passed: {result['all_passed']}")
        if result["failed_lanes"]:
            print(f"Failed lanes: {result['failed_lanes']}")
        print()
        for lr in result["lane_results"]:
            status = "PASS" if lr["passed"] else "FAIL"
            print(f"  Lane {lr['lane']:2d} ({lr['name']}): {status}")
            for k, v in lr["checks"].items():
                print(f"    {k}: {v}")

    return result["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
