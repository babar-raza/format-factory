"""
autonomous_cycle.py — Declaration-Driven Autonomous Supervisor Cycle
Orchestrates the full cycle: validate -> inspect -> grade -> plan-next -> manifest

This is the canonical supervisor command. It takes a declaration path
(not a ZIP, not a watcher state) and produces a complete review.

Exit codes:
  0 — cycle complete, autonomous continue possible
  3 — cycle complete, critical rework exists
  9 — unexpected error
"""

import argparse
import json
import os
import shutil
import sys

from atomic_io import atomic_write_json, atomic_write_text  # noqa: E402
import uuid
from datetime import datetime
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent

# Import sibling modules
sys.path.insert(0, str(SCRIPT_DIR))

# Structured logging (TC-APRV-011)
from logging_config import configure_supervisor_logging
_logger = configure_supervisor_logging()

from evidence_declaration import validate_declaration
from inspect_declared_evidence import inspect_declaration
from grade_declared_work import grade_all, write_outputs
from generate_next_worker_prompt import generate_prompt, generate_next_work_items
from evidence_manifest import generate_from_declaration, validate_manifest, write_manifest
from materialize_declared_evidence import materialize as materialize_evidence
from build_context_pack import build_context_pack, generate_md as generate_context_md
from anti_skip_checker import run_all_checks as run_anti_skip_checks
from failure_memory import FailureMemory


def classify_continuation_state(
    auto_continue_value, at_max_iterations: bool, hard_stops: list,
    overclaimed: list, rework_items: list, review: dict,
    policies_path: Path, anti_skip_result: dict | None = None,
    dirty_state_classified: bool = True,
    required_artifacts_present: bool = True,
    product_output_floor_met: bool = True,
) -> str:
    """Classify the continuation state using a proper state machine.

    States (R112 — extended with YES_WITH_LIMITATIONS):
      YES                              — all accepted, anti-skip clean, pure new-work sprint
      YES_WITH_LIMITATIONS             — accepted but anti-skip has low-severity notes (R112)
      YES_WITH_REWORK                  — rework items but safe lanes continue
      NO_MAX_ITERATIONS                — iteration limit reached
      NO_EXTERNAL_GATE                 — blocked by gate approval / credentials / push
      NO_BROKEN_BASELINE               — critical rework blocks continuation
      NO_UNSAFE_SOURCE_STATE           — overclaimed items present
      NO_NO_PROGRESS                   — consecutive sprints with no product gap closure
      NO_POLICY_BLOCK                  — policy explicitly blocks continuation
      NO_GENERIC_NEXT_PROMPT           — generated prompt is generic, not stream-specific
      NO_LEGACY_REVIEW_CONTRADICTION   — legacy review disagrees with declaration cycle
      NO_STALE_GAPS                    — selected-product-gaps.json is stale
      NO_MISSING_EVIDENCE_MANIFEST     — evidence manifest missing or invalid
      NO_WRONG_STREAM_CONTEXT          — context pack/evidence-review references wrong stream
      NO_MISSING_RAW_LOGS_FOR_VERIFIED_CLAIMS — ACCEPTED_VERIFIED but no raw logs packaged
      NO_PROMPT_QUALITY_FAILURE              — prompt quality validation failed (R108)
      NO_UNCLASSIFIED_DIRTY_STATE       — dirty git state without dirty_state_classification
      NO_MISSING_REQUIRED_ARTIFACTS     — declared required artifacts not found on disk
      NO_PRODUCT_OUTPUT_FLOOR           — Mainstream breadth < floor, no blocker removed
    """
    # Check for policy block
    if policies_path and policies_path.exists():
        try:
            policies = yaml.safe_load(policies_path.read_text(encoding="utf-8"))
            ac_policy = policies.get("autonomous_continuation", {})
            if ac_policy.get("force_stop", False):
                return "NO_POLICY_BLOCK"
        except Exception:
            pass

    # Priority-ordered classification
    if overclaimed:
        return "NO_UNSAFE_SOURCE_STATE"

    # Product-first traffic controller states (R113)
    if not dirty_state_classified:
        return "NO_UNCLASSIFIED_DIRTY_STATE"
    if not required_artifacts_present:
        return "NO_MISSING_REQUIRED_ARTIFACTS"
    if not product_output_floor_met:
        return "NO_PRODUCT_OUTPUT_FLOOR"

    if at_max_iterations:
        return "NO_MAX_ITERATIONS"

    # R102: Check for specific hard stop types
    for hs in hard_stops:
        if hs == "max_iterations_reached":
            continue
        if hs == "generic_next_prompt":
            return "NO_GENERIC_NEXT_PROMPT"
        if hs == "legacy_review_contradiction":
            return "NO_LEGACY_REVIEW_CONTRADICTION"
        if hs == "stale_gaps":
            return "NO_STALE_GAPS"
        if hs == "missing_evidence_manifest":
            return "NO_MISSING_EVIDENCE_MANIFEST"
        if hs == "wrong_stream_context":
            return "NO_WRONG_STREAM_CONTEXT"
        if hs == "missing_raw_logs_for_verified_claims":
            return "NO_MISSING_RAW_LOGS_FOR_VERIFIED_CLAIMS"
        if hs == "prompt_quality_failure":
            return "NO_PROMPT_QUALITY_FAILURE"

    non_iter_hard_stops = [h for h in hard_stops if h != "max_iterations_reached"]
    if non_iter_hard_stops:
        return "NO_BROKEN_BASELINE"

    if auto_continue_value == "true_with_rework":
        return "YES_WITH_REWORK"

    if auto_continue_value:
        # R112: Check anti-skip for low-severity limitations
        if anti_skip_result and not anti_skip_result.get("all_pass", True):
            # Has violations but not blocked/downgraded — low-severity only
            impact = anti_skip_result.get("impact", {})
            if not impact.get("block") and not impact.get("downgrade"):
                return "YES_WITH_LIMITATIONS"
        return "YES"

    return "NO_EXTERNAL_GATE"


def run_stale_repair_pre_cycle(
    repo_root: Path,
    dry_run: bool = True,
    enabled: bool = False,
) -> dict:
    """Pre-cycle stale queue repair step (disabled by default).

    Calls stale_queue_repair_hook to detect and mark STALE_QUEUE_ITEM defects
    before the main autonomous cycle runs.

    Args:
        repo_root: Repository root path.
        dry_run: If True, report stale items without writing repairs. Default True.
        enabled: Master enable switch. Default False (disabled by default).

    Returns:
        dict with keys: enabled, skipped, stale_count, gap_count, status
    """
    if not enabled:
        return {"enabled": False, "skipped": True, "status": "DISABLED_BY_DEFAULT"}

    try:
        _supervisor_dir = Path(__file__).resolve().parent
        import sys as _sys
        if str(_supervisor_dir) not in _sys.path:
            _sys.path.insert(0, str(_supervisor_dir))
        from stale_queue_repair_hook import run_stale_repair  # type: ignore[import]

        result = run_stale_repair(repo_root=repo_root, dry_run=dry_run)
        return {
            "enabled": True,
            "skipped": False,
            "stale_count": result.get("stale_count", 0),
            "gap_count": result.get("gap_count", 0),
            "status": result.get("status", "UNKNOWN"),
            "dry_run": dry_run,
        }
    except ImportError as exc:
        return {
            "enabled": True,
            "skipped": False,
            "status": f"IMPORT_ERROR: {exc}",
            "stale_count": 0,
            "gap_count": 0,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "enabled": True,
            "skipped": False,
            "status": f"ERROR: {type(exc).__name__}: {exc}",
            "stale_count": 0,
            "gap_count": 0,
        }


_PRODUCT_SOURCE_TYPES = frozenset({
    "PRODUCT_SOURCE", "PRODUCT_TEST", "READINESS", "TEST",
})


def _compute_exit_code(review: dict, decl: dict, gov_result: dict | None) -> int:
    """Compute exit code for the cycle manifest.

    TC-H4-001: If governance blocks_sprint=True AND declaration has PRODUCT_SOURCE
    items → exit 3 (not 0). GOVERNANCE_DOC/GOVERNANCE_TOOL items are exempt.

    Exit codes:
      0 = all accepted, governance clean
      3 = critical rework OR governance blocks PRODUCT_SOURCE items
    """
    if review["critical_rework_count"] > 0:
        return 3
    if gov_result is not None and gov_result.get("blocks_sprint"):
        items = decl.get("planned_work_items", [])
        has_product_items = any(
            item.get("item_type", "") in _PRODUCT_SOURCE_TYPES for item in items
        )
        if has_product_items:
            print("  [EXIT_CODE] governance blocks_sprint=True with PRODUCT_SOURCE items -> exit 3")
            return 3
        else:
            print("  [EXIT_CODE] governance blocks_sprint=True, all items are governance/doc -> exit 0 with WARNING")
    return 0


def run_cycle(declaration_path: Path, repo_root: Path, track: str | None = None) -> dict:
    """Run a complete autonomous supervisor cycle.

    track: TC-P2-002 — "product" | "machinery" | None.
      product  → work_groups=["G3","G4","G5"], signal written to product/ subdir
      machinery → work_groups=["G1","G2","G6","G7","G8"], signal written to machinery/ subdir
      None     → legacy mode (all groups, shared .local/supervisor/ path)
    """
    timestamp = datetime.now().isoformat()

    # Step 0 (pre-cycle): Stale queue repair (disabled by default, dry-run safe)
    print("=== STEP 0: PRE-CYCLE STALE REPAIR ===")
    repair_result = run_stale_repair_pre_cycle(repo_root, dry_run=True, enabled=False)
    if repair_result.get("skipped"):
        print(f"  Stale repair: {repair_result['status']}")
    else:
        print(f"  Stale repair: stale={repair_result.get('stale_count', 0)} "
              f"gaps={repair_result.get('gap_count', 0)} "
              f"status={repair_result.get('status', 'UNKNOWN')}")

    # Step 0b: Detect active per-chat plan lock
    plan_lock = None
    _plan_locks_dir = repo_root / ".local" / "supervisor" / "plan-locks"
    _plan_lock_candidates: list[Path] = []
    if _plan_locks_dir.is_dir():
        _plan_lock_candidates.extend(sorted(_plan_locks_dir.glob("*.json")))
    _shared_lock = repo_root / ".local" / "supervisor" / "active-plan-lock.json"
    if _shared_lock.exists():
        _plan_lock_candidates.append(_shared_lock)
    for _lp in _plan_lock_candidates:
        try:
            _ld = json.loads(_lp.read_text(encoding="utf-8"))
            if _ld.get("status") != "COMPLETE":
                plan_lock = _ld
                print(f"  [PLAN_LOCK] Active plan: {plan_lock.get('plan_path')}")
                print(f"  [PLAN_LOCK] Last taskcard: {plan_lock.get('last_taskcard')}")
                break
        except Exception as _pe:
            print(f"  [PLAN_LOCK] Warning: could not read {_lp.name}: {_pe}")

    # Step 1: Validate declaration
    _logger.info("Step 1: Validate declaration", extra={"sprint_id": "pending"})
    print("=== STEP 1: VALIDATE DECLARATION ===")
    validation = validate_declaration(declaration_path, repo_root)
    if not validation["valid"]:
        print(f"DECLARATION_INVALID: {declaration_path}")
        for e in validation.get("schema_errors", []):
            print(f"  SCHEMA_ERROR: {e}")
        for e in validation.get("path_errors", []):
            print(f"  PATH_ERROR: {e}")
        return {"exit_code": 1, "error": "Declaration validation failed"}

    decl = validation["declaration"]
    run_id = decl.get("run_id", "unknown")
    sprint_id = decl.get("sprint_id", "unknown")
    _logger.info("Declaration validated", extra={"sprint_id": run_id})
    print(f"  VALID: run_id={run_id}, sprint_id={sprint_id}")

    # TC-H2-002: Anti-inflation check — tests_run vs tests_created
    _tests_run = decl.get("tests_run", 0)
    _tests_created = decl.get("tests_created")
    if _tests_created is not None and _tests_created < 5 and _tests_run > 1000:
        print(f"  [WARN] TEST_COUNT_INFLATION: tests_run={_tests_run} but tests_created={_tests_created}. "
              f"tests_run reflects full-suite regression; tests_created should count new tests only.")
    elif _tests_created is None and _tests_run > 1000:
        print(f"  [INFO] tests_created not declared. Add tests_created to distinguish "
              f"new tests from full-suite run ({_tests_run} tests_run).")

    # Step 1b: System healing gate check (GATE_ADVISORY — warns but does not block)
    _healing_gate_failed = False
    _has_product_source_items = any(
        item.get("item_type", "") in _PRODUCT_SOURCE_TYPES
        for item in decl.get("planned_work_items", [])
    )
    if _has_product_source_items:
        try:
            _sys_heal_dir = Path(__file__).parent
            import sys as _sys_mod
            if str(_sys_heal_dir) not in _sys_mod.path:
                _sys_mod.path.insert(0, str(_sys_heal_dir))
            from check_system_healing_gate import check_healing_gate as _chg
            _gate_result = _chg(repo_root=repo_root, advisory=True)
            _gate_verdict = _gate_result.get("verdict", "UNKNOWN")
            _gate_exit = _gate_result.get("exit_code", -1)
            _failed_lanes = _gate_result.get("failed_lanes", [])
            if _gate_exit != 0:
                print(f"  [SYSTEM_HEALING_GATE] ADVISORY: verdict={_gate_verdict}, "
                      f"failed_lanes={_failed_lanes}. "
                      f"Product source work proceeding (advisory mode). "
                      f"Resolve healing gate before switching to GATE_STRICT mode.")
                _healing_gate_failed = True
            else:
                print(f"  [SYSTEM_HEALING_GATE] PASSED: verdict={_gate_verdict}")
        except Exception as _ghg_err:
            print(f"  [SYSTEM_HEALING_GATE] Could not check: {_ghg_err}")
            _healing_gate_failed = False

    # Step 2: Inspect declared evidence
    print("\n=== STEP 2: INSPECT DECLARED EVIDENCE ===")
    inspection = inspect_declaration(decl, repo_root)
    item_count = len(inspection.get("item_inspections", []))
    artifact_count = len(inspection.get("artifact_inspections", []))
    print(f"  Inspected: {item_count} work items, {artifact_count} artifacts")

    # Step 2b: Generate/validate evidence manifest
    print("\n=== STEP 2b: EVIDENCE MANIFEST ===")
    try:
        evidence_manifest = generate_from_declaration(declaration_path, repo_root)
        evidence_manifest_path = (repo_root / decl["evidence_root"]) / "evidence-manifest.yaml"
        if evidence_manifest_path.exists():
            # Validate existing manifest
            val_result = validate_manifest(evidence_manifest_path, repo_root)
            print(f"  Existing manifest: {'VALID' if val_result['valid'] else 'INVALID'} ({val_result['checked']} artifacts checked)")
            if not val_result["valid"]:
                for err in val_result["errors"][:5]:
                    print(f"    {err}")
        else:
            # Write generated manifest
            write_manifest(evidence_manifest, evidence_manifest_path)
            print(f"  Generated: {evidence_manifest_path} ({len(evidence_manifest['artifacts'])} artifacts)")
    except Exception as e:
        print(f"  WARNING: Manifest step skipped: {e}")

    # Step 2c: Materialize declared evidence (R99 fix: D99-MODEL-01)
    print("\n=== STEP 2c: MATERIALIZE DECLARED EVIDENCE ===")
    try:
        mat_dir = repo_root / ".local" / "supervisor" / "materialized" / run_id
        mat_result = materialize_evidence(declaration_path, repo_root, mat_dir)
        print(f"  Verified: {mat_result['artifacts_verified']}, Missing: {mat_result['artifacts_missing']}")
    except Exception as e:
        print(f"  WARNING: Materialization skipped: {e}")

    # Step 2d: Adoption compliance validation (R111: consumed by cycle)
    print("\n=== STEP 2d: ADOPTION COMPLIANCE VALIDATION ===")
    review_dir = repo_root / ".local" / "supervisor" / "reviews" / run_id
    review_dir.mkdir(parents=True, exist_ok=True)
    adoption_result = None
    try:
        from validate_adoption_compliance import validate_adoption
        adoption_result = validate_adoption(decl)
        (review_dir / "adoption-compliance-result.json").write_text(
            json.dumps(adoption_result, indent=2), encoding="utf-8"
        )
        print(f"  Adoption compliance: {'PASS' if adoption_result['compliant'] else 'FAIL'} "
              f"({adoption_result['non_exempt_items']} non-exempt, "
              f"{adoption_result['items_with_transcript']} with transcript, "
              f"{adoption_result['items_with_skill_id']} with skill_id)")
    except Exception as e:
        print(f"  WARNING: Adoption compliance check skipped: {e}")

    # Step 2d2: Requirements authority validation (SAL-I-004, Sprint 2 advisory / Sprint 3 hard-block)
    # REQUIREMENT and READINESS items must pass requirements authority validation.
    # Sprint 3 promotion: failure for these item types marks critical rework (blocks continuation).
    print("\n=== STEP 2d2: REQUIREMENTS AUTHORITY VALIDATION ===")
    _BLOCKING_RA_TYPES = frozenset({"REQUIREMENT", "READINESS", "RELEASE_GATE"})
    requirement_items = [
        item for item in decl.get("planned_work_items", [])
        if item.get("item_type") in _BLOCKING_RA_TYPES
    ]
    _ra_failure_blocks = False  # set True if blocking item types fail RA validation
    if requirement_items:
        try:
            import sys as _sys
            _ra_dir = repo_root / "tools" / "requirements_authority"
            if str(_ra_dir) not in _sys.path:
                _sys.path.insert(0, str(_ra_dir))
            from validate_requirements_authority import run_validation
            _ra_output_dir = review_dir / "requirements-authority"
            _ra_output_dir.mkdir(parents=True, exist_ok=True)
            _ra_result = run_validation(
                graph_dir=None,
                fixtures_dir=None,
                output_dir=_ra_output_dir,
            )
            _ra_overall = _ra_result.overall
            _blocking_count = sum(
                1 for i in requirement_items if i.get("item_type") in _BLOCKING_RA_TYPES
            )
            print(f"  Requirements authority: {_ra_overall} ({_blocking_count} blocking-type items)")
            if _ra_overall != "PASS":
                _ra_failure_blocks = True
                print(f"  BLOCK: Requirements authority validation FAIL for {_blocking_count} "
                      f"REQUIREMENT/READINESS/RELEASE_GATE items. "
                      f"Review {_ra_output_dir} for details.")
            else:
                print(f"  PASS: Requirements authority validation passed.")
            (_ra_output_dir / "item-count.txt").write_text(
                f"{_blocking_count} blocking-type items validated, overall={_ra_overall}\n",
                encoding="utf-8",
            )
        except Exception as _ra_e:
            print(f"  WARNING: Requirements authority validation skipped: {_ra_e}")
    else:
        print(f"  No REQUIREMENT/READINESS/RELEASE_GATE items in declaration — "
              f"requirements authority step skipped")

    # Step 2e: Governance validators (GRE-TC-002: wired into pipeline)
    print("\n=== STEP 2e: GOVERNANCE VALIDATORS ===")
    governance_validation_result = None
    try:
        # governance_validators.py internally uses `from tools.supervisor.*` imports,
        # which requires REPO_ROOT (not just SCRIPT_DIR) to be on sys.path.
        if str(REPO_ROOT) not in sys.path:
            sys.path.insert(0, str(REPO_ROOT))
        from governance_validators import run_all_governance_validators
        governance_validation_result = run_all_governance_validators(decl, repo_root)
        (review_dir / "governance-validation-result.json").write_text(
            json.dumps(governance_validation_result, indent=2), encoding="utf-8"
        )
        _gov_fail = governance_validation_result.get("fail_count", 0)
        _gov_warn = governance_validation_result.get("warn_count", 0)
        _gov_pass = governance_validation_result.get("pass_count", 0)
        _gov_blocks = governance_validation_result.get("blocks_sprint", False)
        print(f"  Governance: {_gov_pass} PASS / {_gov_warn} WARN / {_gov_fail} FAIL"
              f" | blocks_sprint={_gov_blocks}")
        if _gov_fail > 0:
            for v in governance_validation_result.get("validators", []):
                if v.get("result") == "FAIL":
                    print(f"    FAIL [{v['validator']}]: {v.get('summary', '')[:120]}")
    except Exception as e:
        print(f"  WARNING: Governance validators skipped: {e}")

    # Step 2e½: Source structure validator (spec-derived architecture governance)
    print("\n=== STEP 2e½: SOURCE STRUCTURE VALIDATOR ===")
    try:
        _validator_path = repo_root / "tools" / "validators" / "source_structure_validator.py"
        if _validator_path.is_file():
            import importlib.util
            _spec = importlib.util.spec_from_file_location("source_structure_validator", str(_validator_path))
            _ssv = importlib.util.module_from_spec(_spec)
            _spec.loader.exec_module(_ssv)
            _ss_result = _ssv.run_full_scan(repo_root)
            (review_dir / "source-structure-result.json").write_text(
                json.dumps(_ss_result, indent=2), encoding="utf-8"
            )
            _ss_blocks = _ss_result.get("blocks_sprint", False)
            _ss_status = _ss_result.get("result", _ss_result.get("status", "UNKNOWN"))
            print(f"  Source structure: {_ss_status} | blocks_sprint={_ss_blocks}")
            if _ss_blocks:
                for k in ("new_violations", "regressions"):
                    items = _ss_result.get(k, [])
                    if items:
                        print(f"    {k}: {'; '.join(items[:5])}")
        else:
            print("  Source structure validator not found — skipped")
    except Exception as e:
        print(f"  WARNING: Source structure validator skipped: {e}")

    # ENFORCEMENT BOUNDARY NOTE:
    # Route decision PRESENCE is validated by Validator 11 (validate_route_decision_required).
    # Route decision CONTENT (allowed_paths, forbidden_paths, required_tests) is enforced
    # at action dispatch time via next_action_runner.run_action() → check_action_route_allowed().
    # Manual/skill execution bypasses this dispatch-time enforcement.
    # See docs/governance/autonomy-default-routing-policy.md for full boundary specification.

    # Step 2f (SUP-RECT-002): DAG prerequisite validation
    print("\n=== STEP 2f: DAG PREREQUISITE VALIDATION ===")
    dag_validation_result = {"status": "skipped"}
    try:
        dag_path = repo_root / ".local" / "evidences" / "spec-to-feature-radical-correction-plan-20260612-915cfd2" / "execution-dag.yaml"
        if dag_path.exists():
            dag_data = yaml.safe_load(dag_path.read_text(encoding="utf-8"))
            waves = dag_data.get("waves", [])
            declared_wave = decl.get("wave", None)
            if declared_wave is not None:
                # Check all prerequisite waves are COMPLETED
                target_wave = None
                for w in waves:
                    if w.get("wave") == declared_wave:
                        target_wave = w
                        break
                if target_wave:
                    depends_on = target_wave.get("depends_on", [])
                    unmet = []
                    for dep in depends_on:
                        dep_num = int(str(dep).replace("wave-", ""))
                        for w in waves:
                            if w.get("wave") == dep_num and w.get("status") != "COMPLETED":
                                unmet.append(f"wave-{dep_num} (status={w.get('status', 'UNKNOWN')})")
                    dag_validation_result = {
                        "status": "checked",
                        "declared_wave": declared_wave,
                        "prerequisites": depends_on,
                        "unmet": unmet,
                        "passed": len(unmet) == 0,
                    }
                    if unmet:
                        print(f"  DAG validation: WARN — unmet prerequisites: {unmet}")
                    else:
                        print(f"  DAG validation: PASS (wave {declared_wave}, deps={depends_on})")
                else:
                    dag_validation_result = {"status": "wave_not_found", "declared_wave": declared_wave}
                    print(f"  DAG validation: wave {declared_wave} not found in DAG")
            else:
                dag_validation_result = {"status": "no_wave_declared"}
                print("  DAG validation: no wave declared in evidence — skipped")
        else:
            print("  DAG validation: execution-dag.yaml not found — skipped")
    except Exception as dag_err:
        safe_err = str(dag_err).encode("ascii", "replace").decode()
        print(f"  WARNING: DAG prerequisite check skipped: {safe_err}")
    # dag_validation_result is applied to review after grade_all() creates it (below)

    # Step 3: Grade work items (includes Step 3a: LLM semantic verification)
    print("\n=== STEP 3: GRADE WORK ITEMS ===")
    # Inject repo_root for semantic verification (LLM reads evidence files)
    decl["_repo_root"] = str(repo_root)
    # Debug: check LLM gateway availability before grading
    try:
        from grade_declared_work import _get_sv_gateway
        _dbg_gw, _dbg_cfg = _get_sv_gateway()
        print(f"  LLM gateway: {'AVAILABLE' if _dbg_gw else 'UNAVAILABLE'} (configured={getattr(_dbg_cfg, 'is_configured', False) if _dbg_cfg else False})")
    except Exception as _dbg_e:
        print(f"  LLM gateway check failed: {_dbg_e}")
    # TC-P2-004: Track-scoped grade cache (REQ-TRK-008)
    _supervisor_base = repo_root / ".local" / "supervisor"
    if track == "product":
        _grade_cache_path = _supervisor_base / "product" / "grade-cache.json"
    elif track == "machinery":
        _grade_cache_path = _supervisor_base / "machinery" / "grade-cache.json"
    else:
        _grade_cache_path = None  # Use default (legacy path)
    review = grade_all(inspection, decl, grade_cache_path=_grade_cache_path)
    review["declaration_path"] = str(declaration_path)
    review["dag_validation"] = dag_validation_result

    # Step 2d2 post-grading: promote requirements authority failure to critical rework
    # Sprint 3: REQUIREMENT/READINESS/RELEASE_GATE failure is now a hard block.
    if _ra_failure_blocks:
        review["critical_rework_count"] = max(review.get("critical_rework_count", 0) + 1, 1)
        if review.get("overall_verdict") in ("ACCEPTED", "ACCEPTED_WITH_LIMITATIONS"):
            review["overall_verdict"] = "ACCEPTED_WITH_REWORK"
        review["stop_reason"] = (
            review.get("stop_reason", "") +
            " Requirements authority validation FAIL for REQUIREMENT/READINESS items."
        ).strip()
        print("  [Step 2d2] Requirements authority failure promoted to CRITICAL REWORK.")

    print(f"  Verdict: {review['overall_verdict']}")
    print(f"  Accepted: {len(review['accepted_items'])}")
    print(f"  Rework: {len(review['rework_items'])}")
    print(f"  Overclaimed: {len(review['overclaimed_items'])}")
    print(f"  Autonomous Continue: {review['autonomous_continue']}")

    # Step 3a: Report LLM semantic verification results
    sv_items = [g for g in review.get("item_grades", []) if g.get("semantic_verification", {}).get("llm_used")]
    if sv_items:
        sv_downgrades = [g for g in sv_items if not g["semantic_verification"].get("adequate")]
        sv_stubs = [g for g in sv_items if g["semantic_verification"].get("stub_detected")]
        print("\n  --- Step 3a: LLM Semantic Verification ---")
        print(f"  Items verified: {len(sv_items)}")
        print(f"  Downgrades: {len(sv_downgrades)}")
        print(f"  Stubs detected: {len(sv_stubs)}")
        for g in sv_downgrades:
            deficiencies = g["semantic_verification"].get("deficiencies", [])
            safe_deficiencies = [d.encode("ascii", "replace").decode() for d in deficiencies[:2]]
            print(f"    [{g['item_id']}] {'; '.join(safe_deficiencies)}")

    # R111: Attach adoption compliance result to review for downstream consumption
    if adoption_result is not None:
        review["adoption_compliance"] = adoption_result
        if not adoption_result["compliant"]:
            # Adoption non-compliance downgrades clean ACCEPTED to ACCEPTED_WITH_REWORK
            if review["overall_verdict"] == "ACCEPTED":
                review["overall_verdict"] = "ACCEPTED_WITH_REWORK"
                review["stop_reason"] = (
                    review.get("stop_reason", "") +
                    f" Adoption compliance FAIL: {adoption_result['summary']}"
                ).strip()

    # GRE-TC-002: Attach governance validation result to review
    if governance_validation_result is not None:
        review["governance_validation"] = governance_validation_result
        if governance_validation_result.get("blocks_sprint"):
            # Blocking governance failure is a hard block (exit 3), not just a downgrade
            review["critical_rework_count"] = max(review.get("critical_rework_count", 0) + 1, 1)
            review["autonomous_continue"] = False
            if review["overall_verdict"] in ("ACCEPTED", "ACCEPTED_WITH_LIMITATIONS",
                                              "ACCEPTED_WITH_REWORK"):
                review["overall_verdict"] = "ACCEPTED_WITH_REWORK"
            review["stop_reason"] = (
                review.get("stop_reason", "") +
                f" Governance validator FAIL (blocks_sprint): {governance_validation_result.get('summary', '')}"
            ).strip()
            # Add blocking validators to rework_items so they are visible
            for v in governance_validation_result.get("validators", []):
                if v.get("result") == "FAIL" and v.get("blocks_sprint"):
                    rework_id = f"GOV_BLOCK:{v['validator']}"
                    if rework_id not in review.get("rework_items", []):
                        review.setdefault("rework_items", []).append(rework_id)

    # Step 2e (SUP-RECT-001): Lane enforcement validation
    print("\n=== STEP 2e: LANE ENFORCEMENT VALIDATION ===")
    try:
        from lane_enforcement_validator import LaneEnforcementValidator
        lane_validator = LaneEnforcementValidator()
        declared_lane = decl.get("lane", None)
        lane_result = lane_validator.validate(decl, declared_lane=declared_lane)
        (review_dir / "lane-enforcement-result.json").write_text(
            json.dumps({"passed": lane_result.passed, "violations": lane_result.violations,
                        "evidence": lane_result.evidence}, indent=2), encoding="utf-8"
        )
        if lane_result.passed:
            print(f"  Lane enforcement: PASS ({len(lane_result.evidence)} files checked)")
        else:
            print(f"  Lane enforcement: FAIL — {len(lane_result.violations)} violation(s)")
            for v in lane_result.violations:
                print(f"    [VIOLATION] {v}")
            # Lane violations are advisory rework, not hard stops (multi-lane sprints are common)
            review.setdefault("rework_items", [])
            review["rework_items"].append(f"LANE_ENFORCEMENT:{len(lane_result.violations)}_violations")
    except Exception as lane_err:
        print(f"  WARNING: Lane enforcement check skipped: {lane_err}")

    # Lane 5: Record governance failures to durable failure memory
    if governance_validation_result is not None and governance_validation_result.get("blocks_sprint"):
        try:
            from failure_memory import FailureMemory
            fm = FailureMemory(repo_root)
            for v in governance_validation_result.get("validators", []):
                if v.get("result") == "FAIL":
                    fm.record_failure(
                        category="GOVERNANCE_FALSE_TRIGGER" if not v.get("blocks_sprint") else "SUPERVISOR_CONTROL_FAILURE",
                        root_cause=f"governance_validator_{v['validator']}_failed",
                        correction="Requires item-level fix in declaration",
                        sprint_id=sprint_id,
                    )
            fm.save()
        except Exception as fm_err:
            print(f"  [WARN] Failure memory recording failed: {fm_err}")

    # HEAL-RECT-002: Run learning consumer — scan learnings, generate rule proposals
    print("\n=== STEP 2g: LEARNING CONSUMER ===")
    try:
        from learning_consumer import LearningConsumer
        lc = LearningConsumer(repo_root)
        scan_count = lc.scan_all_learnings()
        proposals = lc.generate_proposals(threshold=3)
        if proposals:
            lc.save_proposals()
            print(f"  Learning consumer: {scan_count} entries, {len(proposals)} rule proposal(s) promoted")
        else:
            print(f"  Learning consumer: {scan_count} entries scanned, no promotions")
        review["learning_consumer"] = {"scanned": scan_count, "proposals": len(proposals)}
    except Exception as lc_err:
        print(f"  WARNING: Learning consumer skipped: {lc_err}")

    # Write review outputs
    review_dir = repo_root / ".local" / "supervisor" / "reviews" / run_id
    write_outputs(review, review_dir)

    # Write inspection JSON
    (review_dir / "inspection.json").write_text(
        json.dumps(inspection, indent=2), encoding="utf-8"
    )

    # Step 3.5: Quality Scoring via grade-to-quality adapter (advisory, non-blocking)
    print("\n=== STEP 3.5: QUALITY SCORING ===")
    quality_result = None
    try:
        from grade_to_quality_adapter import adapt_item_grades
        from quality_scorer import score_execution
        taskcard_results = adapt_item_grades(review.get("item_grades", []))
        quality_result = score_execution(taskcard_results, repo_root=repo_root)
        (review_dir / "quality-scores.json").write_text(
            json.dumps(quality_result, indent=2), encoding="utf-8"
        )
        review["quality_scores"] = quality_result.get("overall_scores", {})
        review["quality_verdict"] = quality_result.get("overall_verdict", "UNKNOWN")
        all_green = quality_result.get("all_green", False)
        print(f"  Quality verdict: {quality_result.get('overall_verdict')} (all_green={all_green})")
        if not all_green:
            for r in quality_result.get("reroute_log", []):
                print(f"    Reroute: {r.get('taskcard_id')} — {r.get('reason', '')[:100]}")
    except Exception as qs_err:
        print(f"  WARNING: Quality scoring skipped: {qs_err}")

    # Step 3b: Post-grading anti-skip checks (R107: hard gates with severity)
    print("\n=== STEP 3b: ANTI-SKIP QUALITY CHECKS ===")
    anti_skip_impact = None
    anti_skip_result = None
    try:
        from validate_package_identity import _extract_stream_from_sprint
        evidence_root = repo_root / decl.get("evidence_root", "")
        target_stream = _extract_stream_from_sprint(sprint_id)
        sample_outputs_dir = evidence_root / "sample-outputs"

        # Load gaps if available
        gaps_data = None
        gaps_path = evidence_root / f"selected-gaps-{run_id}.json"
        if gaps_path.exists():
            try:
                gaps_data = json.loads(gaps_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        # Load generated prompt if available
        prompt_text = ""
        prompt_path = review_dir / "combined-next-worker-prompt.md"
        if prompt_path.exists():
            prompt_text = prompt_path.read_text(encoding="utf-8")

        # R111: Load global next-sprint.md for stream-output authority check
        global_next_sprint_text = ""
        global_ns_path = repo_root / "reports" / "supervisor" / "next-sprint.md"
        if global_ns_path.exists():
            try:
                global_next_sprint_text = global_ns_path.read_text(encoding="utf-8")
            except Exception:
                pass

        # Extract declared item types for stream-aware anti-skip exemptions
        _declared_item_types = list({
            item.get("item_type", "")
            for item in decl.get("planned_work_items", [])
            if item.get("item_type")
        }) if decl else None

        anti_skip_result = run_anti_skip_checks(
            prompt_text=prompt_text,
            gaps_data=gaps_data,
            expected_sprint=sprint_id,
            evidence_root=evidence_root,
            declaration=decl,
            grades=review.get("item_grades", []),
            target_stream=target_stream,
            repo_root=repo_root,
            sample_outputs_dir=sample_outputs_dir if sample_outputs_dir.exists() else None,
            next_sprint_text=global_next_sprint_text,
            declared_scope=_declared_item_types,
        )
        # Write anti-skip results
        (review_dir / "anti-skip-check-result.json").write_text(
            json.dumps(anti_skip_result, indent=2), encoding="utf-8"
        )
        anti_skip_impact = anti_skip_result.get("impact", {})
        print(f"  Anti-skip: {anti_skip_result['total_checks']} checks, "
              f"{anti_skip_result['violations']} violations")
        if anti_skip_impact:
            if anti_skip_impact.get("block"):
                print(f"  HARD GATE BLOCK: {anti_skip_impact['block_items']}")
            if anti_skip_impact.get("downgrade"):
                print(f"  DOWNGRADE: {anti_skip_impact['downgrade_items']}")
            if anti_skip_impact.get("caveats"):
                print(f"  CAVEATS: {anti_skip_impact['caveats']}")
        if anti_skip_result["violations"] > 0:
            for check in anti_skip_result["checks"]:
                if check.get("is_violation"):
                    sev = check.get("severity", "medium")
                    print(f"    [{sev.upper()}] {check['check']} — {check.get('recommendation', '')[:100]}")

        # R107: Apply hard gate enforcement to review
        if anti_skip_impact and anti_skip_impact.get("block"):
            review["autonomous_continue"] = False
            review["stop_reason"] = f"Anti-skip critical block: {anti_skip_impact['block_items']}"
            review["critical_rework_count"] = max(review["critical_rework_count"], 1)
            print("  >>> CONTINUATION BLOCKED by anti-skip critical violations")
        elif anti_skip_impact and anti_skip_impact.get("downgrade"):
            # High-severity violations downgrade the overall verdict
            if review["overall_verdict"] == "ACCEPTED":
                review["overall_verdict"] = "ACCEPTED_WITH_REWORK"
            review["anti_skip_downgrade_reasons"] = anti_skip_impact["downgrade_items"]
            print("  >>> VERDICT DOWNGRADED by anti-skip high-severity violations")

    except Exception as e:
        print(f"  WARNING: Anti-skip checks skipped: {e}")

    # Step 3c (SUP-RECT-003): Run overclaim detector if graph store available
    print("\n=== STEP 3c: OVERCLAIM DETECTOR ===")
    try:
        ra_tools = REPO_ROOT / "tools" / "requirements_authority"
        if str(ra_tools) not in sys.path:
            sys.path.insert(0, str(ra_tools))
        from overclaim_detector import OverclaimDetector, OverclaimReport
        from graph_store import GraphStore

        graph_path = repo_root / "reports" / "capability-layer" / "proof-graph.json"
        if graph_path.exists():
            store = GraphStore.load(graph_path)
            detector = OverclaimDetector(store)
            oc_report: OverclaimReport = detector.detect_all()
            oc_dict = oc_report.to_dict()
            (review_dir / "overclaim-detector-result.json").write_text(
                json.dumps(oc_dict, indent=2), encoding="utf-8"
            )
            print(f"  Overclaim detector: {oc_report.error_count} ERROR, "
                  f"{oc_report.warning_count} WARNING findings")
            if oc_report.error_count > 0:
                review["overclaim_detector_errors"] = oc_report.error_count
                # Promote ERROR findings to critical rework if items are overclaimed
                for finding in oc_report.findings:
                    if finding.severity == "ERROR":
                        review.setdefault("overclaim_findings", []).append(finding.to_dict())
                print(f"  >>> {oc_report.error_count} ERROR overclaim findings recorded")
        else:
            print("  Overclaim detector: proof-graph.json not found — skipped")
    except ImportError:
        print("  Overclaim detector: import failed — skipped (non-blocking)")
    except Exception as e:
        print(f"  WARNING: Overclaim detector failed: {e}")

    # Step 3d: SAL + Capability Map Recompute (R1/R2 — recon sprint repair)
    # Triggers SAL pipeline refresh and capability map regeneration after grading.
    # Non-blocking: failures are logged but do not stop the cycle.
    print("\n=== STEP 3d: SAL + CAPABILITY MAP RECOMPUTE ===")
    import subprocess as _subprocess_recompute
    sal_recompute_result = {"status": "skipped"}
    capmap_recompute_result = {"status": "skipped"}

    changed_files = decl.get("changed_files", [])
    product_src_changed = any(
        f.startswith("src/") for f in changed_files
    )
    if product_src_changed:
        try:
            sal_runner_path = repo_root / "tools" / "specification-authority-layer" / "sal_master_runner.py"
            if sal_runner_path.exists():
                sal_proc = _subprocess_recompute.run(
                    [sys.executable, str(sal_runner_path), "--all", "--output-dir",
                     str(repo_root / ".local" / "sal-output")],
                    capture_output=True, text=True, timeout=120, cwd=str(repo_root)
                )
                sal_recompute_result = {
                    "status": "completed" if sal_proc.returncode == 0 else "failed",
                    "returncode": sal_proc.returncode,
                    "trigger": "product_src_changed",
                }
                print(f"  SAL recompute: {'OK' if sal_proc.returncode == 0 else 'FAILED'} "
                      f"(exit {sal_proc.returncode})")
            else:
                sal_recompute_result = {"status": "not_found", "path": str(sal_runner_path)}
                print(f"  SAL recompute: sal_master_runner.py not found — skipped")
        except Exception as sal_err:
            sal_recompute_result = {"status": "error", "error": str(sal_err)}
            print(f"  WARNING: SAL recompute failed: {sal_err}")

        try:
            capmap_gen_path = repo_root / "tools" / "capability_layer" / "capability_map_generator.py"
            if capmap_gen_path.exists():
                capmap_proc = _subprocess_recompute.run(
                    [sys.executable, str(capmap_gen_path)],
                    capture_output=True, text=True, timeout=120, cwd=str(repo_root)
                )
                capmap_recompute_result = {
                    "status": "completed" if capmap_proc.returncode == 0 else "failed",
                    "returncode": capmap_proc.returncode,
                    "trigger": "sal_recompute_completed",
                }
                print(f"  Capability map recompute: {'OK' if capmap_proc.returncode == 0 else 'FAILED'} "
                      f"(exit {capmap_proc.returncode})")
            else:
                capmap_recompute_result = {"status": "not_found", "path": str(capmap_gen_path)}
                print(f"  Capability map recompute: capability_map_generator.py not found — skipped")
        except Exception as cap_err:
            capmap_recompute_result = {"status": "error", "error": str(cap_err)}
            print(f"  WARNING: Capability map recompute failed: {cap_err}")
    else:
        print("  No product source changes detected — recompute skipped")

    review["sal_recompute"] = sal_recompute_result
    review["capmap_recompute"] = capmap_recompute_result

    # Step 3e: Capability Queue Consumer (TC-WIRE-001)
    # Run capability_queue_consumer.py after every capability map recompute to compile
    # fresh gap entries into actionable taskcards. Uses subprocess pattern consistent
    # with SAL + capability map recompute above. Non-blocking.
    print("\n=== STEP 3e: CAPABILITY QUEUE CONSUMER ===")
    cap_consumer_result = {"status": "skipped"}
    consumer_path = repo_root / "tools" / "supervisor" / "capability_queue_consumer.py"
    if consumer_path.exists():
        try:
            consumer_proc = _subprocess_recompute.run(
                [sys.executable, str(consumer_path), "--max-gaps", "5"],
                capture_output=True, text=True, timeout=60, cwd=str(repo_root)
            )
            cap_consumer_result = {
                "status": "completed" if consumer_proc.returncode == 0 else "failed",
                "returncode": consumer_proc.returncode,
                "trigger": "post_capmap_recompute",
                "stdout_tail": consumer_proc.stdout.strip().splitlines()[-3:] if consumer_proc.stdout else [],
            }
            print(f"  Capability queue consumer: {'OK' if consumer_proc.returncode == 0 else 'FAILED'} "
                  f"(exit {consumer_proc.returncode})")
            if consumer_proc.stdout:
                for line in consumer_proc.stdout.strip().splitlines()[-3:]:
                    print(f"    {line}")
        except Exception as consumer_err:
            cap_consumer_result = {"status": "error", "error": str(consumer_err)}
            print(f"  WARNING: Capability queue consumer failed: {consumer_err}")
    else:
        cap_consumer_result = {"status": "not_found", "path": str(consumer_path)}
        print(f"  Capability queue consumer: not found — skipped")
    review["cap_consumer"] = cap_consumer_result

    # Step 3f: Authority Integration Fabric (TC-FABRIC-001)
    # Subprocess-invoke authority_integration_fabric.py to produce 4 canonical outputs:
    # spec-context-pack-index.json, authority-integration-contract.json,
    # mainstream-gap-queue-authoritative.json, supervisor-verdict-authority-packet.json.
    # Non-blocking — failure is logged but does not prevent continuation.
    print("\n=== STEP 3f: AUTHORITY INTEGRATION FABRIC ===")
    fabric_result = {"status": "skipped"}
    fabric_script = repo_root / "tools" / "supervisor" / "authority_integration_fabric.py"
    if fabric_script.exists():
        try:
            fabric_proc = _subprocess_recompute.run(
                [sys.executable, str(fabric_script)],
                capture_output=True, text=True, timeout=120, cwd=str(repo_root)
            )
            fabric_result = {
                "status": "completed" if fabric_proc.returncode == 0 else "failed",
                "returncode": fabric_proc.returncode,
                "stdout_lines": fabric_proc.stdout.strip().splitlines()[-5:] if fabric_proc.stdout else [],
                "stderr_lines": fabric_proc.stderr.strip().splitlines()[-5:] if fabric_proc.stderr else [],
            }
            if fabric_proc.returncode == 0:
                print("  Authority integration fabric: OK")
            else:
                print(f"  Authority integration fabric: non-zero exit {fabric_proc.returncode} (non-blocking)")
        except Exception as fabric_err:
            fabric_result = {"status": "error", "error": str(fabric_err)}
            print(f"  Authority integration fabric error (non-blocking): {fabric_err}")
    review["authority_fabric"] = fabric_result

    # Step 3g: Track P reads machinery_to_product handoff (TC-P2-005-04, advisory)
    # Advisory only — if Track M has published a fresh gap snapshot, log it for
    # sprint context. Does NOT block if missing or stale.
    if track == "product":
        try:
            from write_track_handoff import read_machinery_handoff
            _m2p = read_machinery_handoff(repo_root)
            if _m2p:
                print("\n=== STEP 3g: TRACK M HANDOFF (advisory) ===")
                print(f"  machinery_to_product: written_at={_m2p.get('written_at', 'unknown')}")
                print(f"    validated_gap_count: {_m2p.get('validated_gap_count', 'n/a')}")
                print(f"    high_priority_gap_count: {_m2p.get('high_priority_gap_count', 'n/a')}")
                print(f"    gap_ledger_snapshot: {_m2p.get('gap_ledger_snapshot_path', 'n/a')}")
                review["machinery_handoff"] = _m2p
            else:
                review["machinery_handoff"] = None
        except Exception as _m2p_err:
            review["machinery_handoff"] = {"error": str(_m2p_err)}

    # Step 4: Generate next worker prompt (R108: stream-specific)
    print("\n=== STEP 4: GENERATE NEXT WORKER PROMPT ===")
    try:
        from validate_package_identity import _extract_stream_from_sprint
        detected_stream = _extract_stream_from_sprint(sprint_id)
    except Exception:
        detected_stream = "mainstream"
    # TC-P2-002/TC-P2-003: Derive work_groups from track for two-track routing.
    try:
        from generate_next_worker_prompt import TRACK_GROUPS
        _work_groups = list(TRACK_GROUPS[track]) if track and track in TRACK_GROUPS else None
    except Exception:
        _work_groups = None
    if _work_groups:
        print(f"  Track={track!r} -> work_groups={_work_groups}")

    prompt = generate_prompt(review, repo_root=repo_root, stream=detected_stream,
                             work_groups=_work_groups)
    prompt_path = review_dir / "combined-next-worker-prompt.md"
    prompt_path.write_text(prompt, encoding="utf-8")

    next_work = generate_next_work_items(review, stream=detected_stream, plan_lock=plan_lock,
                                         work_groups=_work_groups)
    work_path = review_dir / "next-work-items.yaml"
    work_path.write_text(
        yaml.dump(next_work, default_flow_style=False, sort_keys=False), encoding="utf-8"
    )
    (review_dir / "next-work-items.json").write_text(
        json.dumps(next_work, indent=2), encoding="utf-8"
    )
    print(f"  Prompt: {prompt_path}")

    # Step 4b: Prompt quality validation (R108: moved after prompt generation)
    print("\n=== STEP 4b: PROMPT QUALITY VALIDATION ===")
    try:
        from validate_prompt_quality import validate_prompt_quality
        target_stream = detected_stream
        if prompt_path.exists():
            prompt_text = prompt_path.read_text(encoding="utf-8")
            has_repairs = len(review.get("rework_items", [])) > 0
            pq_result = validate_prompt_quality(
                prompt_text, target_stream,
                has_repairs=has_repairs, has_advancement=True,
            )
            (review_dir / "prompt-quality-result.json").write_text(
                json.dumps(pq_result, indent=2), encoding="utf-8"
            )
            if pq_result["valid"]:
                print(f"  Prompt quality: PASS ({pq_result['passed']}/{pq_result['total_checks']} checks)")
            else:
                failed_checks = [c["check"] for c in pq_result["checks"] if not c["pass"]]
                print(f"  Prompt quality: FAIL ({pq_result['failed']} failures: {failed_checks})")
                # R108: Prompt quality failures — hard-stop only for truly unrecoverable issues
                hard_prompt_failures = {"stream_identity", "not_generic"}
                soft_prompt_failures = {"no_wrong_stream", "advancement_lane"}
                failed_set = set(failed_checks)
                has_hard = bool(hard_prompt_failures & failed_set)
                has_soft_only = bool(soft_prompt_failures & failed_set) and not has_hard
                if has_hard:
                    review["autonomous_continue"] = False
                    review["stop_reason"] = f"Prompt quality gate: {failed_checks}"
                    review["prompt_quality_failure"] = True
                    print("  >>> CONTINUATION BLOCKED by prompt quality failures")
                elif has_soft_only:
                    # Soft failures become rework items — safe lanes can continue
                    review.setdefault("rework_items", [])
                    review["rework_items"].append(f"PROMPT_QUALITY_REWORK:{','.join(failed_checks)}")
                    print(f"  Prompt quality: soft failure {failed_checks} → rework (not hard stop)")
        else:
            print("  No prompt file to validate")
    except Exception as e:
        print(f"  WARNING: Prompt quality check skipped: {e}")
    print(f"  Next work: {len(next_work['items'])} items (stream={detected_stream})")

    # SUP-RECT-005: Circuit breaker for zero-task loops
    if len(next_work.get("items", [])) == 0:
        zero_task_counter_path = repo_root / ".local" / "supervisor" / "zero-task-counter.json"
        ztc = {"count": 0, "sprints": []}
        try:
            if zero_task_counter_path.exists():
                ztc = json.loads(zero_task_counter_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
        ztc["count"] = ztc.get("count", 0) + 1
        ztc.setdefault("sprints", []).append(sprint_id)
        zero_task_counter_path.parent.mkdir(parents=True, exist_ok=True)
        zero_task_counter_path.write_text(json.dumps(ztc, indent=2), encoding="utf-8")
        if ztc["count"] >= 3:
            print(f"  CIRCUIT BREAKER: {ztc['count']} consecutive zero-task cycles detected!")
            review["stop_reason"] = (
                review.get("stop_reason", "") +
                f" CIRCUIT_BREAKER: {ztc['count']} zero-task cycles ({ztc['sprints'][-3:]})"
            ).strip()
            review["autonomous_continue"] = False
        else:
            print(f"  Zero-task warning: {ztc['count']}/3 before circuit breaker triggers")
    else:
        # Reset counter on successful task generation
        ztc_path = repo_root / ".local" / "supervisor" / "zero-task-counter.json"
        if ztc_path.exists():
            ztc_path.write_text(json.dumps({"count": 0, "sprints": []}, indent=2), encoding="utf-8")

    # Step 4b: Validate next-work-items stream correctness (R108)
    try:
        from validate_prompt_quality import validate_next_work_items
        nwi_result = validate_next_work_items(next_work, detected_stream)
        (review_dir / "next-work-items-quality.json").write_text(
            json.dumps(nwi_result, indent=2), encoding="utf-8"
        )
        if nwi_result["valid"]:
            print(f"  Next-work-items quality: PASS ({nwi_result['passed']}/{nwi_result['total_checks']})")
        else:
            failed = [c["check"] for c in nwi_result["checks"] if not c["pass"]]
            print(f"  Next-work-items quality: FAIL ({failed})")
            if "no_wrong_stream_items" in failed or "stream_field_match" in failed:
                review["autonomous_continue"] = False
                review["stop_reason"] = f"Next-work-items stream violation: {failed}"
    except Exception as e:
        print(f"  WARNING: Next-work-items validation skipped: {e}")

    # Step 4c: Validate generated prompt has required sections
    # NOTE: summary_classifier.classify_summary is NOT used here because it was designed
    # for Stage 3 structured JSON/YAML outputs. Generated prompts are Markdown by design,
    # and classify_summary always returns PROSE_ONLY on Markdown (false positive).
    # Instead, we check that the generated prompt contains expected structural sections.
    print("\n=== STEP 4c: PROMPT COMPLETENESS VALIDATION ===")
    try:
        if prompt_path.exists():
            prompt_text = prompt_path.read_text(encoding="utf-8")
            required_sections = ["## Sprint", "## Mandatory Evidence", "## Hard Prohibitions"]
            found = [s for s in required_sections if s in prompt_text]
            missing = [s for s in required_sections if s not in prompt_text]
            has_tasks = "TASK-" in prompt_text or "## Group G" in prompt_text or "## Section 1" in prompt_text
            classification = {
                "classification": "STRUCTURED_PROMPT" if not missing and has_tasks else "INCOMPLETE_PROMPT",
                "required_sections_found": found,
                "required_sections_missing": missing,
                "has_task_items": has_tasks,
                "line_count": len(prompt_text.splitlines()),
            }
            (review_dir / "output-classification.json").write_text(
                json.dumps(classification, indent=2), encoding="utf-8"
            )
            if missing or not has_tasks:
                review.setdefault("rework_items", [])
                review["rework_items"].append(f"PROMPT_INCOMPLETE:missing={missing},tasks={has_tasks}")
                print(f"  Prompt completeness: INCOMPLETE (missing={missing}, tasks={has_tasks})")
            else:
                print(f"  Prompt completeness: PASS ({len(found)} sections, tasks=True, {classification['line_count']} lines)")
        else:
            print("  No prompt file to validate")
            review["autonomous_continue"] = False
            review["stop_reason"] = "No generated prompt file"
    except Exception as e:
        print(f"  WARNING: Prompt completeness check skipped: {e}")

    # Step 5: Write cycle manifest
    print("\n=== STEP 5: WRITE CYCLE MANIFEST ===")
    manifest = {
        "cycle_id": f"cycle-{run_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "run_id": run_id,
        "sprint_id": sprint_id,
        "timestamp": timestamp,
        "declaration_path": str(declaration_path),
        "review_path": str(review_dir / "supervisor-review.json"),
        "next_prompt_path": str(prompt_path),
        "item_grades_path": str(review_dir / "item-grades.yaml"),
        "next_work_items_path": str(work_path),
        "memory_synced": False,
        "autonomous_continue": review["autonomous_continue"],
        "stop_reason": review.get("stop_reason", ""),
        "exit_code": _compute_exit_code(review, decl, governance_validation_result),
        "accepted_count": len(review["accepted_items"]),
        "rework_count": len(review["rework_items"]),
        "rejected_count": len(review["rejected_items"]),
        "overclaimed_count": len(review["overclaimed_items"]),
        "blocked_count": len([g for g in review["item_grades"] if g["supervisor_grade"] == "BLOCKED_EXTERNAL_GATE"]),
    }
    manifest_path = review_dir / "supervisor-cycle-manifest.yaml"
    manifest_path.write_text(
        yaml.dump(manifest, default_flow_style=False, sort_keys=False), encoding="utf-8"
    )
    print(f"  Manifest: {manifest_path}")

    # TC-H5-001: Append grading history BEFORE overwriting latest-review
    try:
        import json as _json
        grading_history_path = repo_root / "reports" / "supervisor" / "grading-history.jsonl"
        grading_history_path.parent.mkdir(parents=True, exist_ok=True)
        _history_record = {
            "sprint_id": sprint_id,
            "run_id": run_id,
            "timestamp": timestamp,
            "verdict": review.get("overall_verdict", ""),
            "accepted_count": len(review["accepted_items"]),
            "rework_count": len(review.get("rework_items", [])),
            "overclaimed_count": len(review.get("overclaimed_items", [])),
            "rework_items": list(review.get("rework_items", [])),
            "continuation_state": manifest.get("autonomous_continue", False),
            "exit_code": manifest.get("exit_code", 0),
        }
        with grading_history_path.open("a", encoding="utf-8") as _gf:
            _gf.write(_json.dumps(_history_record) + "\n")
        print(f"  [HISTORY] Appended to grading-history.jsonl (total lines: {sum(1 for _ in grading_history_path.open())})")
    except Exception as _hist_err:
        print(f"  [WARN] grading-history.jsonl append failed: {_hist_err}")

    # Step 6: Copy latest summaries to reports/supervisor/
    print("\n=== STEP 6: COPY LATEST SUMMARIES ===")
    latest_dir = repo_root / "reports" / "supervisor"
    latest_dir.mkdir(parents=True, exist_ok=True)

    copies = [
        ("supervisor-review.md", "latest-review.md"),
        ("combined-next-worker-prompt.md", "latest-next-worker-prompt.md"),
        ("item-grades.json", "work-item-grades.json"),
        ("item-grades.yaml", "work-item-grades.yaml"),
    ]
    for src_name, dst_name in copies:
        src = review_dir / src_name
        dst = latest_dir / dst_name
        if src.exists():
            shutil.copy2(str(src), str(dst))
            print(f"  Copied: {dst}")

    # R108: Also copy to per-stream state directory
    stream_dir = repo_root / "reports" / "supervisor-streams" / detected_stream
    stream_dir.mkdir(parents=True, exist_ok=True)
    for src_name, dst_name in copies:
        src = review_dir / src_name
        dst = stream_dir / dst_name
        if src.exists():
            shutil.copy2(str(src), str(dst))
    print(f"  Stream dir: {stream_dir}")

    # Canonical work-items copy for check_continuation.py
    # TC-P2-002: Write to track-specific subdir when --track is set.
    _supervisor_dir = repo_root / ".local" / "supervisor"
    if track == "product":
        _track_supervisor_dir = _supervisor_dir / "product"
    elif track == "machinery":
        _track_supervisor_dir = _supervisor_dir / "machinery"
    else:
        _track_supervisor_dir = _supervisor_dir
    canonical_work_items = _track_supervisor_dir / "next-work-items.json"
    canonical_work_items.parent.mkdir(parents=True, exist_ok=True)
    # Also always write to legacy path for backward compat (non-track callers)
    legacy_work_items = _supervisor_dir / "next-work-items.json"
    legacy_work_items.parent.mkdir(parents=True, exist_ok=True)
    src_work = review_dir / "next-work-items.json"
    if src_work.exists():
        shutil.copy2(str(src_work), str(canonical_work_items))
        if track:
            shutil.copy2(str(src_work), str(legacy_work_items))
        print(f"  Canonical work items: {canonical_work_items}")

    # R112: Write stream-local authority map
    authority_map = {
        "stream": detected_stream,
        "run_id": run_id,
        "sprint_id": sprint_id,
        "timestamp": timestamp,
        "stream_local_dir": str(stream_dir),
        "global_dir": str(latest_dir),
        "authority": "STREAM_LOCAL",
        "global_status": "ADVISORY_REFERENCE",
        "stream_local_files": {
            "evidence_review": str(stream_dir / "evidence-review.json"),
            "contradictions": str(stream_dir / "contradictions.json"),
            "next_prompt": str(stream_dir / "latest-next-worker-prompt.md"),
            "work_item_grades": str(stream_dir / "work-item-grades.json"),
            "continuation_signal": str(
                repo_root / ".local" / "supervisor" / "streams" / detected_stream / "continuation-signal.json"
            ),
        },
    }
    (stream_dir / "authority-map.json").write_text(
        json.dumps(authority_map, indent=2), encoding="utf-8"
    )
    print(f"  Authority map: {stream_dir / 'authority-map.json'}")

    # Write human-readable work-item-grades.md to reports/supervisor/
    grades = review.get("item_grades", [])
    if grades:
        wg_lines = [
            "# Work Item Grades",
            f"Sprint: {sprint_id}",
            f"Generated: {timestamp}",
            f"Global Status: {review.get('overall_verdict', 'UNKNOWN')}",
            "",
            "| Item ID | Grade | Rework Required |",
            "|---------|-------|-----------------|",
        ]
        for g in grades:
            rework = (g.get("required_rework") or "")[:80]
            wg_lines.append(
                f"| {g['item_id']} | {g['supervisor_grade']} | {rework} |"
            )
        wg_lines += [
            "",
            "## Summary",
            f"- Accepted: {len(review['accepted_items'])}",
            f"- Rework: {len(review['rework_items'])}",
            f"- Overclaimed: {len(review['overclaimed_items'])}",
            f"- Autonomous Continue: {review['autonomous_continue']}",
        ]
        (latest_dir / "work-item-grades.md").write_text("\n".join(wg_lines) + "\n", encoding="utf-8")
        print(f"  Written: {latest_dir / 'work-item-grades.md'}")

    # Write latest cycle summary
    summary_lines = [
        "# Latest Supervisor Cycle Summary",
        f"Run: {run_id}",
        f"Sprint: {sprint_id}",
        f"Timestamp: {timestamp}",
        f"Verdict: {review['overall_verdict']}",
        f"Autonomous Continue: {review['autonomous_continue']}",
        f"Accepted: {len(review['accepted_items'])}",
        f"Rework: {len(review['rework_items'])}",
        f"Overclaimed: {len(review['overclaimed_items'])}",
        f"Review: {review_dir / 'supervisor-review.md'}",
        f"Next Prompt: {prompt_path}",
    ]
    (latest_dir / "latest-cycle-summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    # Step 7: Bridge to legacy format for session-resume/approval-gates/next-sprint
    print("\n=== STEP 7: BRIDGE TO LEGACY PACKET FORMAT ===")
    try:
        bridge_to_legacy_format(review, manifest, decl, repo_root)
        print("  Bridge: evidence-review.json + contradictions.json written to reports/supervisor/")
    except Exception as e:
        print(f"  WARNING: Bridge step failed: {e}")

    # Step 7b: Regenerate legacy markdown files (R99 fix: D99-STALE-01)
    # R101: Pass detected stream so next-sprint.md is stream-specific
    print("\n=== STEP 7b: REGENERATE LEGACY MARKDOWN ===")
    try:
        from generate_supervisor_packet import generate_packet, detect_stream_from_sprint_id
        detected_stream = detect_stream_from_sprint_id(sprint_id)
        generate_packet(repo_root, stream=detected_stream, plan_lock=plan_lock)
        print(f"  Regenerated: session-resume.md, approval-gates.md, next-sprint.md (stream={detected_stream})")
    except Exception as e:
        print(f"  WARNING: Legacy markdown regeneration failed: {e}")

    # Step 7c: Rebuild context pack (R99 fix: D99-STALE-02)
    print("\n=== STEP 7c: REBUILD CONTEXT PACK ===")
    try:
        pack = build_context_pack(repo_root)
        context_yaml_path = repo_root / ".supervisor" / "context-pack.yaml"
        context_yaml_path.write_text(
            yaml.dump(pack, default_flow_style=False, sort_keys=False),
            encoding="utf-8"
        )
        context_md_path = repo_root / "reports" / "supervisor" / "context-pack.md"
        context_md_path.write_text(generate_context_md(pack), encoding="utf-8")
        print(f"  Context pack rebuilt: {context_yaml_path}")
    except Exception as e:
        print(f"  WARNING: Context pack rebuild failed: {e}")

    # Step 7b: Track P Ledger Enforcement (TC-P2-008 — REQ-LED-001/LED-002/LED-003)
    # For Track P sprints, validate that at least one ledger entry exists in
    # product-code-change-ledger.json for this sprint_id before writing signal.
    # Non-Track-P: skipped entirely (backward compat).
    if track == "product":
        print("\n=== STEP 7b: TRACK P LEDGER VALIDATION ===")
        try:
            from validate_ledger_entry import validate_ledger_entry_exists
            _led_items = decl.get("planned_work_items", [])
            _ledger_path = repo_root / "reports" / "r90" / "product-code-change-ledger.json"
            _led_valid, _led_missing, _led_error = validate_ledger_entry_exists(
                sprint_id=sprint_id,
                work_items=_led_items,
                ledger_path=_ledger_path,
            )
            if _led_valid:
                print(f"  Ledger validation: PASS (sprint_id={sprint_id!r})")
                review["ledger_validation"] = {"status": "passed", "sprint_id": sprint_id}
            else:
                print(f"  Ledger validation: FAIL — {_led_error}", file=sys.stderr)
                review["ledger_validation"] = {
                    "status": "failed",
                    "sprint_id": sprint_id,
                    "missing": _led_missing,
                    "error": _led_error,
                }
                # REQ-LED-003: Reject declaration if ledger entry is missing for product work items
                sys.exit(7)
        except ImportError as _led_import_err:
            print(f"  WARNING: validate_ledger_entry unavailable — skipping ({_led_import_err})")
            review["ledger_validation"] = {"status": "skipped", "reason": str(_led_import_err)}
        except SystemExit:
            raise
        except Exception as _led_exc:
            print(f"  WARNING: Ledger validation error (non-blocking): {_led_exc}")
            review["ledger_validation"] = {"status": "error", "error": str(_led_exc)}

    # Step 8: Write continuation signal for autonomous loop (MODE 5)
    print("\n=== STEP 8: WRITE CONTINUATION SIGNAL ===")
    try:
        signal_dir = repo_root / ".local" / "supervisor"
        signal_dir.mkdir(parents=True, exist_ok=True)
        # TC-P2-002: Route signal to track-specific subdirectory when --track is set.
        # Legacy path is always updated for backward compat.
        if track == "product":
            _track_signal_dir = signal_dir / "product"
            _track_signal_dir.mkdir(parents=True, exist_ok=True)
            signal_path = _track_signal_dir / "continuation-signal.json"
            _legacy_signal_path = signal_dir / "continuation-signal.json"
        elif track == "machinery":
            _track_signal_dir = signal_dir / "machinery"
            _track_signal_dir.mkdir(parents=True, exist_ok=True)
            signal_path = _track_signal_dir / "continuation-signal.json"
            _legacy_signal_path = None  # Track M: no legacy fallback (strict isolation)
        else:
            signal_path = signal_dir / "continuation-signal.json"
            _legacy_signal_path = None

        # Read existing signal to preserve iteration count, then increment
        existing_iteration = 0
        if signal_path.exists():
            try:
                existing = json.loads(signal_path.read_text(encoding="utf-8"))
                existing_iteration = existing.get("iteration", 0)
            except Exception:
                pass
        existing_iteration += 1  # Each cycle run advances the counter

        # Load max_iterations from policies
        max_iterations = 5
        policies_path = repo_root / ".supervisor" / "policies.yaml"
        if policies_path.exists():
            try:
                policies = yaml.safe_load(policies_path.read_text(encoding="utf-8"))
                max_iterations = policies.get("autonomous_continuation", {}).get("max_iterations", 5)
            except Exception:
                pass

        hard_stops = []
        if manifest.get("exit_code") == 3:
            hard_stops.append("critical_rework_blocks_continuation")

        # Determine continuation mode:
        #   true            — all items accepted, pure new-work sprint
        #   true_with_rework — rework items exist but safe lanes can continue
        #   false           — hard stop (overclaim/reject/external gate)
        rework_items = review.get("rework_items", [])
        overclaimed = review.get("overclaimed_items", [])

        # R98 fix: Check iteration >= max_iterations before allowing continuation
        at_max_iterations = existing_iteration >= max_iterations
        rollover_note = None
        if at_max_iterations:
            # R5: CHECKPOINT_ROLLOVER — per stop_reason_adjudicator Rule 6, max_iterations
            # is NOT terminal when no other hard stops exist. The agent can handle by resetting
            # the iteration counter (governed rollover, not manual reset required).
            # Check whether any OTHER hard stops exist before deciding to rollover vs stop.
            non_iter_hard_stops_early = [
                h for h in hard_stops if h != "max_iterations_reached"
            ]
            overclaimed_or_rework_blocks = bool(
                manifest.get("exit_code") == 3 or
                review.get("overclaimed_items")
            )
            if not non_iter_hard_stops_early and not overclaimed_or_rework_blocks:
                # Governed rollover: reset iteration to 0 and continue
                rollover_note = {
                    "rollover_from_iteration": existing_iteration,
                    "rollover_at_max": max_iterations,
                    "rollover_rule": "CHECKPOINT_ROLLOVER_CONTINUE (stop_reason_adjudicator Rule 6)",
                    "rollover_action": "iteration reset to 0 — new autonomous batch starting",
                }
                existing_iteration = 0
                at_max_iterations = False
            else:
                hard_stops.append("max_iterations_reached")

        # R107 Lane G: Check evidence quality — stop on quality regression
        # Legacy evidence_quality_score is deprecated; check semantic_quality_score first
        eqb = review.get("evidence_quality_breakdown", {})
        sqs = eqb.get("semantic_quality_score")
        eqs = review.get("evidence_quality_score", 1.0)
        if sqs is None and eqs == 0.0 and len(review.get("accepted_items", [])) > 0:
            hard_stops.append("evidence_quality_zero")

        # R107 Lane G: Check anti-skip critical blocks
        if anti_skip_impact and anti_skip_impact.get("block"):
            hard_stops.append("anti_skip_critical_block")

        # R108: Prompt quality failure blocks continuation
        if review.get("prompt_quality_failure"):
            hard_stops.append("prompt_quality_failure")

        # R-CLOSEOUT: Run closeout gate and no-stop watchdog if evidence root exists
        evidence_root_path = None
        if declaration_path and declaration_path.parent.exists():
            evidence_root_path = declaration_path.parent
        if evidence_root_path:
            try:
                from validate_closeout_gate import run_closeout_gate
                closeout_result = run_closeout_gate(evidence_root_path)
                review["closeout_gate_verdict"] = closeout_result.get("verdict", "UNKNOWN")
                review["closeout_gate_checks"] = closeout_result.get("gates", [])
                print(f"  Closeout gate: {closeout_result.get('verdict', 'UNKNOWN')} "
                      f"({closeout_result.get('passed_count', 0)}/{closeout_result.get('total_gates', 0)})")
            except ImportError:
                print("  WARNING: validate_closeout_gate not available, skipping")
            except Exception as cg_err:
                print(f"  WARNING: Closeout gate check failed: {cg_err}")

            try:
                from validate_no_stop_watchdog import run_no_stop_watchdog
                watchdog_result = run_no_stop_watchdog(evidence_root_path)
                review["watchdog_verdict"] = watchdog_result.get("verdict", "UNKNOWN")
                review["watchdog_checks"] = watchdog_result.get("checks", [])
                wd_verdict = watchdog_result.get("verdict", "ALLOW_STOP")
                print(f"  No-stop watchdog: {wd_verdict} "
                      f"({watchdog_result.get('block_count', 0)} blocks)")
            except ImportError:
                print("  WARNING: validate_no_stop_watchdog not available, skipping")
            except Exception as wd_err:
                print(f"  WARNING: No-stop watchdog check failed: {wd_err}")

        if hard_stops or overclaimed:
            auto_continue_value = False
        elif rework_items and not overclaimed:
            auto_continue_value = "true_with_rework"
        else:
            auto_continue_value = bool(manifest.get("autonomous_continue", False))

        # R99: Full continuation state classification (D99-CONT-01)
        # R112: Pass anti_skip_result for YES_WITH_LIMITATIONS detection
        continuation_state = classify_continuation_state(
            auto_continue_value, at_max_iterations, hard_stops,
            overclaimed, rework_items, review, policies_path,
            anti_skip_result=anti_skip_result,
            # New params use default True — backward compatible (R113 product-first)
        )

        # CCI-MVP: Stable session_id for cross-chat isolation (TC-CCI-200)
        try:
            from continuation_identity import get_or_create_session_identity
            _cci_identity = get_or_create_session_identity(sprint_id=sprint_id)
            session_id = _cci_identity.session_id
        except Exception as _cci_err:
            print(f"  WARNING: CCI identity fallback: {_cci_err}", file=sys.stderr)
            session_id = os.environ.get("CLAUDE_SESSION_ID") or str(uuid.uuid4())[:12]

        # TC-P2-002: Include track and chat_id (for Track M) in signal.
        _chat_id_value = None
        if track == "machinery":
            try:
                from continuation_identity import get_or_create_machinery_identity
                _m_identity = get_or_create_machinery_identity()
                _chat_id_value = _m_identity.chat_id
                # Write current-chat-id.json for check_continuation.py resolution
                _chat_id_reg = signal_dir / "machinery" / "current-chat-id.json"
                _chat_id_reg.parent.mkdir(parents=True, exist_ok=True)
                atomic_write_json(_chat_id_reg, {"chat_id": _chat_id_value, "written_at": timestamp})
            except Exception as _cid_err:
                print(f"  WARNING: Track M chat_id generation failed: {_cid_err}", file=sys.stderr)

        signal = {
            "autonomous_continue": auto_continue_value,
            "iteration": existing_iteration,
            "max_iterations": max_iterations,
            "next_sprint_path": "reports/supervisor/next-sprint.md",
            "stop_reason": hard_stops[0] if hard_stops else None,
            "rework_items": rework_items,
            "safe_lanes_available": not bool(hard_stops),
            "generated_at": timestamp,
            "source_sprint_id": sprint_id,
            "hard_stops_detected": hard_stops,
            "continuation_state": continuation_state,
            "session_id": session_id,
            "owner": "autonomous_cycle",
        }
        if track:
            signal["track"] = track
        if _chat_id_value:
            signal["chat_id"] = _chat_id_value
        if rollover_note:
            signal["checkpoint_rollover"] = rollover_note
        atomic_write_json(signal_path, signal)
        # Also update legacy path for Track P (backward compat) — NOT for Track M (strict isolation)
        if _legacy_signal_path is not None:
            atomic_write_json(_legacy_signal_path, signal)
        print(f"  Signal: {signal_path} (continue={signal['autonomous_continue']}, "
              f"iter={existing_iteration}/{max_iterations}, track={track!r})")

        # CCI: Record signal creation in continuation ledger (TC-CCI-202)
        try:
            from continuation_ledger import append_event
            append_event("CREATED", "continuation-signal.json",
                         session_id=session_id, sprint_id=sprint_id)
        except Exception:
            pass  # Ledger is best-effort

        # R109: Also write stream-local continuation signal
        stream_signal_dir = signal_dir / "streams" / detected_stream
        stream_signal_dir.mkdir(parents=True, exist_ok=True)
        stream_signal = {**signal, "stream": detected_stream}
        stream_signal_path = stream_signal_dir / "continuation-signal.json"
        atomic_write_json(stream_signal_path, stream_signal)
        print(f"  Stream signal: {stream_signal_path}")

        # HEAL-RECT-005: Archive rework items for cross-sprint persistence
        if rework_items:
            rework_archive_path = signal_dir / "rework_archive.jsonl"
            try:
                with open(rework_archive_path, "a", encoding="utf-8") as ra:
                    for rw_id in rework_items:
                        ra.write(json.dumps({
                            "item_id": rw_id,
                            "sprint_id": sprint_id,
                            "archived_at": timestamp,
                            "resolved": False,
                        }) + "\n")
            except Exception as ra_err:
                print(f"  WARNING: Rework archive failed: {ra_err}")

        # R-NMPC: Wire evidence_continuation to produce machine-readable continuation.
        # Without this, autonomous_continue=true points only to advisory Markdown
        # (next-sprint.md), which continuation_router.py rejects, causing the user
        # to manually paste prompts. We always call this when autonomous_continue is
        # truthy so next-action.json + active-continuation.json are fresh.
        if auto_continue_value:
            try:
                from evidence_continuation import (
                    apply_post_closeout_continuation,
                    repair_global_continuation_signal,
                    seed_post_closeout_queue_item,
                )
                post_result = apply_post_closeout_continuation(
                    sprint_id=sprint_id,
                    run_id=getattr(manifest, "get", lambda k, d=None: d)("run_id"),
                    cycle_index=existing_iteration,
                )
                repair_result = repair_global_continuation_signal(sprint_id=sprint_id)
                seed_result = seed_post_closeout_queue_item(sprint_id=sprint_id)
                print(f"  Machine continuation: {post_result.get('next_action_path')}")
                print(f"  Signal repair: {repair_result.get('status')}")
                print(f"  Queue seed: {seed_result.get('status')}")
            except Exception as ec_err:
                print(f"  WARNING: evidence_continuation bridge failed: {ec_err}")
                # Non-silent: record failure in signal so check_continuation surfaces it
                signal["evidence_continuation_failed"] = True
                signal["evidence_continuation_error"] = str(ec_err)
                atomic_write_json(signal_path, signal)
    except Exception as e:
        print(f"  WARNING: Continuation signal failed: {e}")

    # TC-P2-002-04: Write Track P handoff entry when running as Track P
    # (so Track M can read it to learn about new capabilities)
    if track == "product":
        try:
            _shared_dir = repo_root / ".local" / "supervisor" / "shared"
            _shared_dir.mkdir(parents=True, exist_ok=True)
            _handoff_path = _shared_dir / "track-handoff.json"
            _existing_handoff: dict = {}
            if _handoff_path.exists():
                try:
                    _existing_handoff = json.loads(_handoff_path.read_text(encoding="utf-8"))
                except Exception:
                    pass
            _existing_handoff["handoff_version"] = 1
            _existing_handoff["product_to_machinery"] = {
                "written_at": timestamp,
                "written_by_session": session_id,
                "sprint_id": sprint_id,
                "new_capabilities_count": len(review.get("accepted_items", [])),
                "test_count": review.get("total_test_count", 0),
            }
            atomic_write_json(_handoff_path, _existing_handoff)
            print(f"  Track P handoff: {_handoff_path}")
        except Exception as _hf_err:
            print(f"  WARNING: Track P handoff write failed: {_hf_err}")

    # Step 8b: Loop Controller State Tracking (advisory, non-blocking)
    print("\n=== STEP 8b: LOOP CONTROLLER STATE ===")
    try:
        from post_sprint_loop_controller import init_loop, transition_to, classify_and_decide, get_next_stages
        loop_state_path = repo_root / ".local" / "supervisor" / "post-sprint-loop-state.json"

        # Read max_iterations from policies (align with continuation signal)
        _lc_max_iter = 12  # default matching continuation signal
        _lc_policies_path = repo_root / ".supervisor" / "policies.yaml"
        if _lc_policies_path.exists():
            try:
                _lc_policies = yaml.safe_load(_lc_policies_path.read_text(encoding="utf-8"))
                _lc_max_iter = _lc_policies.get("autonomous_continuation", {}).get("max_iterations", 12)
            except Exception:
                pass

        # Determine if loop state needs (re)initialization
        _lc_needs_init = not loop_state_path.exists()
        if not _lc_needs_init and loop_state_path.exists():
            try:
                _lc_existing = json.loads(loop_state_path.read_text(encoding="utf-8"))
                _lc_existing_run_id = _lc_existing.get("run_id", "")
                _lc_existing_state = _lc_existing.get("current_state", "")
                _lc_terminal_states = {"MAX_LOOPS_EXCEEDED", "HARD_STOP", "BLOCKED_EXTERNAL", "ACCEPTED_ALL_GREEN"}
                if _lc_existing_run_id != run_id or _lc_existing_state in _lc_terminal_states:
                    # Archive old state before reset
                    _lc_archive_path = repo_root / ".local" / "supervisor" / "post-sprint-loop-state-previous.json"
                    _lc_archive_path.write_text(
                        loop_state_path.read_text(encoding="utf-8"), encoding="utf-8"
                    )
                    _lc_needs_init = True
                    print(f"  Loop state reset (was run_id={_lc_existing_run_id}, state={_lc_existing_state})")
            except Exception:
                _lc_needs_init = True

        if _lc_needs_init:
            init_loop(repo_root, run_id, max_loops=_lc_max_iter)
            print(f"  Loop state initialized (run_id={run_id}, max_iterations={_lc_max_iter})")
            # Fast-forward through audit/hardening since autonomous_cycle is the execution
            _lc_fast_forward = [
                ("AUDIT_RUNNING", "cycle_audit_phase"),
                ("AUDIT_COMPLETE", "cycle_audit_done"),
                ("HARDENING_RUNNING", "cycle_harden_phase"),
                ("HARDENING_COMPLETE", "cycle_harden_done"),
                ("EXECUTION_RUNNING", "cycle_execution_phase"),
                ("EXECUTION_COMPLETE", "cycle_execution_done"),
            ]
            for _lc_state, _lc_trigger in _lc_fast_forward:
                transition_to(repo_root, _lc_state, _lc_trigger)
        quality_path = review_dir / "quality-scores.json"
        if quality_path.exists():
            decision = classify_and_decide(repo_root, quality_path)
            (review_dir / "loop-decision.json").write_text(
                json.dumps(decision, indent=2), encoding="utf-8"
            )
            next_state = decision.get("next_state", "UNKNOWN")
            next_stages = get_next_stages(next_state)
            print(f"  Loop decision: {next_state}")
            print(f"  Next stages: {next_stages}")
        else:
            print("  No quality scores — loop classification skipped")
    except Exception as lc_err:
        print(f"  WARNING: Loop controller skipped: {lc_err}")

    return manifest


def bridge_to_legacy_format(review: dict, manifest: dict, decl: dict, repo_root: Path) -> None:
    """Convert declaration-driven cycle outputs to the JSON format expected by
    generate_supervisor_packet.py so that session-resume.md, approval-gates.md,
    and next-sprint.md are regenerated from fresh data.

    Writes:
      reports/supervisor/evidence-review.json
      reports/supervisor/contradictions.json
    """
    output_dir = repo_root / "reports" / "supervisor"
    output_dir.mkdir(parents=True, exist_ok=True)

    test_results = decl.get("test_results", {})
    passed = test_results.get("passed", 0)
    failed = test_results.get("failed", 0)

    # Build evidence-review.json in the format generate_supervisor_packet expects
    # R102: Mark as declaration-sourced so legacy checks (final-verdict.md,
    # sidecar, R90 contract) are skipped by compare_goal_to_evidence.py
    evidence_review = {
        "_declaration_sourced": True,
        "_source_cycle": "autonomous_cycle.py::bridge_to_legacy_format",
        "sprint_id": manifest.get("sprint_id", "unknown"),
        "timestamp": manifest.get("timestamp", datetime.now().isoformat()),
        "verdict": review.get("overall_verdict", "unknown"),
        "bundle_path": str(decl.get("evidence_root", "")),
        "facts": {
            "test_count": passed,
            "fail_count": failed,
            "skip_count": test_results.get("skipped", 0),
            "git_head": decl.get("git_head_end", "unknown"),
            "gate_states": {},
            "final_verdict_text": review.get("overall_verdict", ""),
            "pending_marker_count": 0,
            "bundle_entry_count": len(review.get("item_grades", [])),
            "bundle_validation_pass": manifest.get("exit_code", 9) != 9,
        },
        "contradictions": [],
        "limitation_notes": [],
        "validator_invoked": True,
        "bundle_validation_pass": manifest.get("exit_code", 9) != 9,
        "exit_code": manifest.get("exit_code", 0),
        "status": "complete",
        "evidence_quality_score": review.get("evidence_quality_score", 0.0),
        "verified_item_count": review.get("verified_item_count", 0),
        "evidence_quality_breakdown": review.get("evidence_quality_breakdown", {}),
    }

    # Build contradictions.json
    contradictions_list = []
    if review.get("critical_rework_count", 0) > 0:
        for grade in review.get("item_grades", []):
            if grade.get("supervisor_grade") in ("OVERCLAIMED", "REJECTED"):
                contradictions_list.append({
                    "severity": "CRITICAL",
                    "description": f"{grade['supervisor_grade']}: {grade.get('item_title', grade.get('item_id', 'unknown'))}",
                    "detail": grade.get("required_rework", ""),
                })
    if failed > 0:
        contradictions_list.append({
            "severity": "CRITICAL",
            "description": f"Tests failed: {failed} failures detected",
            "detail": "All tests must pass per Format Factory policy",
        })

    critical_count = sum(1 for c in contradictions_list if c["severity"] == "CRITICAL")
    contradictions = {
        "sprint_id": manifest.get("sprint_id", "unknown"),
        "timestamp": manifest.get("timestamp", datetime.now().isoformat()),
        "overall": "CRITICAL_CONTRADICTIONS" if critical_count > 0 else "CLEAN",
        "critical_count": critical_count,
        "warning_count": 0,
        "autonomous_continue": manifest.get("autonomous_continue", False),
        "contradictions": contradictions_list,
    }

    (output_dir / "evidence-review.json").write_text(
        json.dumps(evidence_review, indent=2), encoding="utf-8"
    )
    (output_dir / "contradictions.json").write_text(
        json.dumps(contradictions, indent=2), encoding="utf-8"
    )

    # R109: Also write stream-local evidence-review and contradictions
    try:
        from validate_package_identity import _extract_stream_from_sprint
        stream = _extract_stream_from_sprint(manifest.get("sprint_id", ""))
        stream_dir = repo_root / "reports" / "supervisor-streams" / stream
        stream_dir.mkdir(parents=True, exist_ok=True)
        (stream_dir / "evidence-review.json").write_text(
            json.dumps(evidence_review, indent=2), encoding="utf-8"
        )
        (stream_dir / "contradictions.json").write_text(
            json.dumps(contradictions, indent=2), encoding="utf-8"
        )
    except Exception:
        pass


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run declaration-driven autonomous supervisor cycle"
    )
    parser.add_argument(
        "--declaration", type=Path, required=True,
        help="Path to evidence-declaration.yaml"
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--track", type=str, choices=["product", "machinery"], default=None,
        help=(
            "TC-P2-002: Track type for two-track separation. "
            "product → G3/G4/G5 work groups, product/ signal path. "
            "machinery → G1/G2/G6/G7/G8 work groups, machinery/ signal path. "
            "None (default) → legacy mode (all groups, shared signal path)."
        ),
    )
    args = parser.parse_args()

    if not args.declaration.exists():
        print(f"ERROR: Declaration not found: {args.declaration}", file=sys.stderr)
        return 1

    _logger.info("Autonomous supervisor cycle starting", extra={"sprint_id": str(args.declaration)})
    print("=" * 60)
    print("AUTONOMOUS SUPERVISOR CYCLE")
    print(f"Declaration: {args.declaration}")
    if args.track:
        print(f"Track: {args.track}")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)

    manifest = run_cycle(args.declaration, args.repo_root, track=args.track)

    exit_code = manifest.get("exit_code", 9)
    _logger.info(
        "Cycle complete",
        extra={
            "sprint_id": manifest.get("run_id", "unknown"),
            "work_item": f"exit_{exit_code}",
        },
    )

    # TC-RECON-007 / HEAL-RECT-001: Record failure on exit code 3 (rework required).
    # Best-effort — wrapped in try/except so failure memory write never blocks sprint exit.
    if exit_code == 3:
        try:
            sprint_id = manifest.get("run_id", "unknown")
            rework_items = manifest.get("rework_items", [])
            correction = f"Rework required: {', '.join(str(r) for r in rework_items[:5])}" if rework_items else "critical_rework_required"
            fm = FailureMemory(args.repo_root)
            fm.record_failure(
                category="SUPERVISOR_CONTROL_FAILURE",
                root_cause="exit_code_3_rework_required",
                correction=correction,
                sprint_id=sprint_id,
                files_modified=[str(args.declaration)],
                verification_command=f"python autonomous_cycle.py --declaration {args.declaration}",
                severity="HIGH",
            )
            fm.save()
            print(f"  [FAILURE_MEMORY] Recorded exit-3 failure for sprint {sprint_id}")
        except Exception as _fm_err:  # noqa: BLE001
            print(f"  [FAILURE_MEMORY] Warning: could not record failure: {_fm_err}")

    print()
    print("=" * 60)
    print(f"CYCLE COMPLETE (exit {exit_code})")
    print(f"Autonomous Continue: {manifest.get('autonomous_continue', False)}")
    if manifest.get("stop_reason"):
        print(f"Stop Reason: {manifest['stop_reason']}")
    print("=" * 60)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
