"""
closure_challenger.py — Independent closure challenge gate (TC-FG-004).

Runs AFTER grade_all() to independently assess whether ACCEPTED_VERIFIED items
have adequate proof, using proof_adequacy_contract.py rather than trusting
the intermediate fallback that produced the grade.

Called from autonomous_cycle.py after line 977 (grade_all call).

Entry point: run_closure_challenge(item, evidence_root, repo_root, proof_contracts)

Returns verdict:
  - CLOSURE_CHALLENGE_PASSED: assessed level meets contract.proof_target
  - CLOSURE_CHALLENGE_FOUND_REWORK: level below target, or fault survives
  - CLOSURE_CHALLENGE_INVALID: cannot assess (no test files, bad paths)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

_SUPERVISOR = Path(__file__).resolve().parent
if str(_SUPERVISOR) not in sys.path:
    sys.path.insert(0, str(_SUPERVISOR))

from proof_adequacy_contract import (
    ProofContract,
    ProofLevel,
    assess_proof_level,
    infer_default_contract,
    proof_sufficient_for_closure,
)


def _resolve_contract(item: dict, proof_contracts: Optional[list]) -> ProofContract:
    """Return an explicit or inferred ProofContract for the item."""
    if proof_contracts:
        item_id = item.get("item_id", "")
        for pc in proof_contracts:
            if isinstance(pc, dict) and pc.get("requirement_id") == item_id:
                # Convert dict to ProofContract
                try:
                    return ProofContract(
                        requirement_id=pc.get("requirement_id", item_id),
                        target=pc.get("target", item_id),
                        behavior_claim=pc.get("behavior_claim", ""),
                        risk=pc.get("risk", "MEDIUM"),
                        proof_target=ProofLevel(int(pc.get("proof_target", 3))),
                        plausible_faults=pc.get("plausible_faults", []),
                        negative_cases=pc.get("negative_cases", []),
                        exact_expected_results=pc.get("exact_expected_results", []),
                        before_after_comparison=pc.get("before_after_comparison", False),
                        neighboring_risk_review=pc.get("neighboring_risk_review", False),
                    )
                except Exception:
                    pass
    return infer_default_contract(item)


def _challenge_plausible_faults(assessment: dict, contract: ProofContract) -> tuple:
    """Check which plausible faults are detected vs surviving.

    Returns (detected: list, surviving: list).
    """
    detected = []
    surviving = []
    weak_tests = assessment.get("weak_tests", [])
    strong_tests = assessment.get("strong_tests", [])
    strong_ratio = assessment.get("strong_ratio", 0.0)

    for fault in contract.plausible_faults:
        # Heuristic: strong tests detect most faults; weak tests miss constant_return and wrong_default
        if fault in ("constant_return", "constant_zero_return"):
            # Only exact/behavioral assertions would catch constant return
            if strong_ratio > 0:
                detected.append(fault)
            else:
                surviving.append(fault)
        elif fault in ("wrong_default", "off_by_one"):
            # Shape-only (len()==N) assertions catch wrong count but not wrong values
            # Exact value assertions catch both
            if len(strong_tests) >= 1:
                detected.append(fault)
            else:
                surviving.append(fault)
        elif fault in ("not_implemented", "stub_return"):
            if strong_ratio > 0:
                detected.append(fault)
            else:
                surviving.append(fault)
        else:
            # Unknown fault — classify as detected if any strong tests exist
            if strong_ratio > 0:
                detected.append(fault)
            else:
                surviving.append(fault)

    return detected, surviving


def run_closure_challenge(
    item: dict,
    evidence_root: str,
    repo_root: str,
    proof_contracts: Optional[list] = None,
) -> dict:
    """
    Independently challenge whether an ACCEPTED_VERIFIED item has adequate proof.

    Args:
        item: Work item dict from grading output (must have item_id, tests_supporting)
        evidence_root: Path to evidence directory for writing results
        repo_root: Repository root path
        proof_contracts: Optional list of explicit proof contract dicts from declaration.
                         If None or empty, infer_default_contract() is used.

    Returns dict with:
        verdict: CLOSURE_CHALLENGE_PASSED | CLOSURE_CHALLENGE_FOUND_REWORK | CLOSURE_CHALLENGE_INVALID
        item_id: str
        assessed_level: int
        required_level: int
        new_findings: list[str]
        weak_tests: list
        strong_tests: list
        plausible_faults_tested: list[str]
        plausible_faults_surviving: list[str]
        strong_ratio: float
        neighboring_risk_summary: dict
    """
    item_id = item.get("item_id", "UNKNOWN")
    result: dict = {
        "verdict": "CLOSURE_CHALLENGE_INVALID",
        "item_id": item_id,
        "assessed_level": 0,
        "required_level": 3,
        "new_findings": [],
        "weak_tests": [],
        "strong_tests": [],
        "plausible_faults_tested": [],
        "plausible_faults_surviving": [],
        "strong_ratio": 0.0,
        "neighboring_risk_summary": {},
    }

    # 1. Resolve proof contract
    contract = _resolve_contract(item, proof_contracts)
    result["required_level"] = int(contract.proof_target)

    # 2. Find test files to assess
    test_paths = item.get("tests_supporting", []) or []
    _repo = Path(repo_root) if repo_root else Path(".")

    # Resolve relative paths
    resolved_test_paths = []
    for tp in test_paths:
        tp_path = Path(tp)
        if tp_path.is_absolute():
            if tp_path.exists():
                resolved_test_paths.append(str(tp_path))
        else:
            full = _repo / tp
            if full.exists():
                resolved_test_paths.append(str(full))

    if not resolved_test_paths:
        result["new_findings"] = ["no test files found at declared tests_supporting paths"]
        result["verdict"] = "CLOSURE_CHALLENGE_INVALID"
        return result

    # 3. Assess all test files, take overall max
    all_assessments = []
    for tp in resolved_test_paths:
        a = assess_proof_level(tp, contract)
        all_assessments.append(a)

    # Combine: max level, aggregate weak/strong tests
    assessed_level = max(a.get("level", 0) for a in all_assessments)
    all_weak = []
    all_strong = []
    for a in all_assessments:
        all_weak.extend(a.get("weak_tests", []))
        all_strong.extend(a.get("strong_tests", []))

    total_tests = sum(a.get("test_count", 0) for a in all_assessments)
    strong_count = sum(a.get("test_count", 0) * a.get("strong_ratio", 0.0) for a in all_assessments)
    strong_ratio = strong_count / total_tests if total_tests > 0 else 0.0

    result["assessed_level"] = assessed_level
    result["weak_tests"] = all_weak
    result["strong_tests"] = all_strong
    result["strong_ratio"] = round(strong_ratio, 3)

    # 4. Challenge plausible faults
    combined_assessment = {
        "level": assessed_level,
        "strong_ratio": strong_ratio,
        "weak_tests": all_weak,
        "strong_tests": all_strong,
    }
    detected, surviving = _challenge_plausible_faults(combined_assessment, contract)
    result["plausible_faults_tested"] = detected + surviving
    result["plausible_faults_surviving"] = surviving

    # 5. Neighboring risk review (non-blocking, best-effort)
    try:
        from neighboring_risk_reviewer import review_neighboring_risks
        if resolved_test_paths:
            tp0 = resolved_test_paths[0]
            test_dir = str(Path(tp0).parent)
            target = item.get("gap_ledger_ref") or item.get("title") or item_id
            nbr = review_neighboring_risks(tp0, target, test_dir,
                                           authorized_exclusions=item.get("exclusions", []))
            result["neighboring_risk_summary"] = nbr
        else:
            result["neighboring_risk_summary"] = {}
    except Exception as _nbr_err:
        result["neighboring_risk_summary"] = {"error": str(_nbr_err)}

    # 6. Determine verdict
    new_findings = []

    sufficient, gaps = proof_sufficient_for_closure(contract, resolved_test_paths, combined_assessment)
    if not sufficient:
        new_findings.extend(gaps)

    # Risk-qualified fault gate: surviving faults of HIGH/MEDIUM risk trigger rework
    if surviving and contract.risk not in ("LOW",):
        for f in surviving:
            new_findings.append(f"plausible fault SURVIVES: {f}")

    # Neighboring risk must_fix items trigger rework
    must_fix = result.get("neighboring_risk_summary", {}).get("classification", {}).get("must_fix", [])
    for mf in must_fix:
        new_findings.append(f"neighboring risk must_fix: {mf}")

    result["new_findings"] = new_findings

    if new_findings:
        result["verdict"] = "CLOSURE_CHALLENGE_FOUND_REWORK"
    else:
        result["verdict"] = "CLOSURE_CHALLENGE_PASSED"

    # 7. Write result JSON to evidence root (best-effort)
    try:
        out_dir = Path(evidence_root)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"closure-challenge-{item_id}.json"
        out_file.write_text(json.dumps(result, indent=2, default=str))
    except Exception:
        pass

    return result
