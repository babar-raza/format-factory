"""
proof_adequacy_contract.py — Deterministic AST-based assertion strength analysis.

Replaces the intermediate_content_check blanket adequate=True with graded
proof-level assessment. Used by grade_intermediate_verify.py (TC-FG-002b)
and the closure challenger (TC-FG-004).

SHAPE vs EXACT discrimination:
  assert isinstance(x, list)     → TYPE    (level 2) — left is isinstance call
  assert len(result) == 4        → SHAPE   (level 2) — left is len/sum/type call
  assert sum(result) == 4        → SHAPE   (level 2) — left is sum call
  assert result is not None      → NONEMPTY(level 2) — comparator is None
  assert result == [0, 0, 0, 1]  → EXACT   (level 3) — left is Name/Subscript
  assert f(x) == [1, 1, 1, 1]   → BEHAVIORAL (level 3) — left is Call to subject
  assert result[85] == 1         → SUBSCRIPT_EXACT (level 3)
  assert True / assert x         → BARE    (level 1)
"""
from __future__ import annotations

import ast
import textwrap
from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path
from typing import Optional


STRONG_RATIO_THRESHOLD = 0.5  # fraction of test functions that must have ≥1 strong assertion


class ProofLevel(IntEnum):
    NO_PROOF = 0
    ARTIFACT_PRESENT = 1
    HAPPY_PATH_EXECUTED = 2
    EXACT_BEHAVIOR_VERIFIED = 3
    ADVERSARIAL_AND_INTEGRATION_VERIFIED = 4
    PRODUCTION_SHAPED_REPEATABLE_AND_FAULT_SENSITIVE = 5


@dataclass
class ProofContract:
    requirement_id: str
    target: str
    behavior_claim: str
    risk: str
    proof_target: ProofLevel
    required_test_layer: int = 3
    positive_cases: list = field(default_factory=list)
    exact_expected_results: list = field(default_factory=list)
    invariants: list = field(default_factory=list)
    negative_cases: list = field(default_factory=list)
    boundary_cases: list = field(default_factory=list)
    adversarial_cases: list = field(default_factory=list)
    plausible_faults: list = field(default_factory=list)
    mutation_or_fault_challenge: bool = False
    before_after_comparison: bool = False
    neighboring_risk_review: bool = False
    exclusions: list = field(default_factory=list)
    closure_conditions: list = field(default_factory=list)


@dataclass
class FaultSensitivity:
    requirement_id: str
    plausible_fault: str
    old_proof_verdict: str
    new_proof_verdict: str
    detection_mechanism: str
    evidence: str


@dataclass
class BeforeAfterProof:
    requirement_id: str
    baseline_revision: str
    final_revision: str
    before_tests: list = field(default_factory=list)
    before_behaviors_proven: list = field(default_factory=list)
    before_faults_detected: list = field(default_factory=list)
    after_tests: list = field(default_factory=list)
    after_behaviors_proven: list = field(default_factory=list)
    after_faults_detected: list = field(default_factory=list)
    improvements: list = field(default_factory=list)
    unchanged_weaknesses: list = field(default_factory=list)
    regressions: list = field(default_factory=list)
    new_findings: list = field(default_factory=list)
    verdict: str = "UNCHANGED"


_SHAPE_FUNCS = frozenset({"len", "sum", "type", "min", "max", "abs", "round", "int", "float", "str", "bool"})


def _classify_assert_node(node: ast.Assert) -> int:
    """
    Classify a single ast.Assert node → proof level integer 1-4.

    Level 1 (BARE):    assert True / assert False / assert x (no comparison)
    Level 2 (WEAK):    isinstance(...), len(...)==N, sum(...)==N, x is None/not None
    Level 3 (STRONG):  result == specific_value, f(args) == value, container[i] == v
    Level 4 (ADVERSARIAL): kept for future use — treat same as level 3 from AST alone
    """
    test = node.test

    # BARE: no comparison operator → level 1
    if isinstance(test, ast.Constant):
        return 1
    if isinstance(test, ast.Name):
        return 1

    # isinstance() → level 2
    if isinstance(test, ast.Call):
        func = test.func
        if isinstance(func, ast.Name) and func.id == "isinstance":
            return 2

    # Compare node — the rich case
    if isinstance(test, ast.Compare):
        left = test.left
        ops = test.ops
        comparators = test.comparators

        # is None / is not None → level 2
        if any(isinstance(op, (ast.Is, ast.IsNot)) for op in ops):
            if comparators and isinstance(comparators[0], ast.Constant) and comparators[0].value is None:
                return 2

        # in / not in membership → level 3
        if any(isinstance(op, (ast.In, ast.NotIn)) for op in ops):
            return 3

        # == or != comparison: distinguish SHAPE from EXACT
        if any(isinstance(op, (ast.Eq, ast.NotEq)) for op in ops):
            # Check if comparator is None/True/False (trivial)
            # IMPORTANT: use 'is' identity, NOT 'in', because 1==True and 0==False in Python
            def _is_trivial_constant(c: ast.expr) -> bool:
                if not isinstance(c, ast.Constant):
                    return False
                v = c.value
                return v is None or v is True or v is False

            trivial = all(_is_trivial_constant(c) for c in comparators)
            if trivial:
                return 2

            # Left side determines SHAPE vs EXACT
            if isinstance(left, ast.Call):
                func = left.func
                # len(x)==N, sum(x)==N, type(x)==T → SHAPE (level 2)
                if isinstance(func, ast.Name) and func.id in _SHAPE_FUNCS:
                    return 2
                # isinstance(x, T) — already handled above but guard here too
                if isinstance(func, ast.Name) and func.id == "isinstance":
                    return 2
                # Other call on left: f(args)==value → BEHAVIORAL (level 3)
                return 3

            # result[i] == value → SUBSCRIPT_EXACT (level 3)
            if isinstance(left, ast.Subscript):
                return 3

            # result == value, variable == value → EXACT (level 3)
            if isinstance(left, (ast.Name, ast.Attribute)):
                return 3

            # Unary negation or other expr → level 2 fallback
            return 2

        # Ordering comparisons (<, >, <=, >=) — meaningful but not exact
        if any(isinstance(op, (ast.Lt, ast.Gt, ast.LtE, ast.GtE)) for op in ops):
            # len(x) > 0 → SHAPE (level 2)
            if isinstance(left, ast.Call):
                func = left.func
                if isinstance(func, ast.Name) and func.id in _SHAPE_FUNCS:
                    return 2
            return 2

    # UnaryOp (not x) → level 1
    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
        return 1

    # BoolOp (and/or) — recurse into operand assertions
    if isinstance(test, ast.BoolOp):
        levels = []
        for v in test.values:
            sub = ast.Assert(test=v, msg=None)
            levels.append(_classify_assert_node(sub))
        return max(levels) if levels else 1

    return 1  # fallback


def _get_test_functions(tree: ast.Module) -> list[ast.FunctionDef]:
    """Return top-level and class-method test functions."""
    funcs = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            funcs.append(node)
        elif isinstance(node, ast.ClassDef):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.FunctionDef) and child.name.startswith("test_"):
                    funcs.append(child)
    return funcs


def assess_proof_level(test_path: str, contract: Optional[ProofContract] = None) -> dict:
    """
    Parse a Python test file and assess assertion strength.

    Returns:
        {
          "level": int (max level across ALL strong tests, or max overall if no strong),
          "strong_ratio": float,
          "test_count": int,
          "level_distribution": {1: int, 2: int, 3: int, 4: int},
          "weak_tests": [{"name": str, "max_level": int, "assertions": [...]}],
          "strong_tests": [{"name": str, "max_level": int}],
          "gaps": [str],
          "overall_classification": str,
        }
    """
    path = Path(test_path)
    if not path.exists():
        return {
            "level": 0, "strong_ratio": 0.0, "test_count": 0,
            "level_distribution": {1: 0, 2: 0, 3: 0, 4: 0},
            "weak_tests": [], "strong_tests": [],
            "gaps": [f"file not found: {test_path}"],
            "overall_classification": "NO_PROOF",
        }

    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
    except SyntaxError as e:
        return {
            "level": 0, "strong_ratio": 0.0, "test_count": 0,
            "level_distribution": {1: 0, 2: 0, 3: 0, 4: 0},
            "weak_tests": [], "strong_tests": [],
            "gaps": [f"syntax error: {e}"],
            "overall_classification": "PARSE_ERROR",
        }

    test_funcs = _get_test_functions(tree)
    if not test_funcs:
        return {
            "level": 0, "strong_ratio": 0.0, "test_count": 0,
            "level_distribution": {1: 0, 2: 0, 3: 0, 4: 0},
            "weak_tests": [], "strong_tests": [],
            "gaps": ["no test functions found"],
            "overall_classification": "NO_PROOF",
        }

    dist = {1: 0, 2: 0, 3: 0, 4: 0}
    weak_tests = []
    strong_tests = []

    for fn in test_funcs:
        assert_nodes = [n for n in ast.walk(fn) if isinstance(n, ast.Assert)]
        if not assert_nodes:
            # No assertions at all → BARE
            max_level = 1
        else:
            levels = [_classify_assert_node(n) for n in assert_nodes]
            max_level = max(levels)

        dist[min(max_level, 4)] = dist.get(min(max_level, 4), 0) + 1

        if max_level >= 3:
            strong_tests.append({"name": fn.name, "max_level": max_level})
        else:
            weak_tests.append({"name": fn.name, "max_level": max_level})

    total = len(test_funcs)
    strong_count = len(strong_tests)
    strong_ratio = strong_count / total if total > 0 else 0.0

    # Overall level = max among all functions
    all_levels = [t["max_level"] for t in strong_tests] + [t["max_level"] for t in weak_tests]
    overall_level = max(all_levels) if all_levels else 0

    if strong_ratio >= STRONG_RATIO_THRESHOLD and overall_level >= 3:
        classification = "STRONG_PROOF"
    elif strong_ratio > 0 and strong_ratio < STRONG_RATIO_THRESHOLD:
        # Has some strong tests but not enough → PARTIAL_PROOF
        classification = "PARTIAL_PROOF"
    elif overall_level >= 2:
        # Has assertions but ALL are TYPE/SHAPE only (no strong tests at all) → WEAK_PROOF
        classification = "WEAK_PROOF"
    elif overall_level >= 1:
        # Only bare assertions (assert True, assert x) → BARE_PROOF
        classification = "WEAK_PROOF"
    else:
        classification = "NO_PROOF"

    gaps = []
    if weak_tests:
        gaps.append(f"{len(weak_tests)} test(s) have only TYPE/SHAPE assertions: "
                    + ", ".join(t["name"] for t in weak_tests))
    if contract:
        if contract.negative_cases and not any("negative" in fn.name or "invalid" in fn.name or "error" in fn.name
                                                 for fn in test_funcs):
            gaps.append("contract requires negative_cases but none found in test names")
        if contract.exact_expected_results and strong_ratio == 0.0:
            gaps.append("contract requires exact_expected_results but no strong assertions found")

    return {
        "level": overall_level,
        "strong_ratio": strong_ratio,
        "test_count": total,
        "level_distribution": dist,
        "weak_tests": weak_tests,
        "strong_tests": strong_tests,
        "gaps": gaps,
        "overall_classification": classification,
    }


def infer_default_contract(item: dict) -> ProofContract:
    """
    Infer a default ProofContract from a work item when no explicit contract is declared.
    """
    item_type = item.get("item_type", "UNKNOWN")
    item_id = item.get("item_id", "UNKNOWN")
    target = item.get("gap_ledger_ref") or item.get("title") or item_id

    if item_type == "PRODUCT_TEST":
        return ProofContract(
            requirement_id=item_id,
            target=target,
            behavior_claim=f"behavioral correctness of {target}",
            risk="HIGH",
            proof_target=ProofLevel.EXACT_BEHAVIOR_VERIFIED,
            required_test_layer=3,
            plausible_faults=["constant_return", "wrong_default", "off_by_one"],
            before_after_comparison=True,
            neighboring_risk_review=True,
        )
    elif item_type == "PRODUCT_SOURCE":
        return ProofContract(
            requirement_id=item_id,
            target=target,
            behavior_claim=f"implementation of {target}",
            risk="MEDIUM",
            proof_target=ProofLevel.HAPPY_PATH_EXECUTED,
            plausible_faults=["not_implemented", "stub_return"],
        )
    else:
        # GOVERNANCE_DOC, GOVERNANCE_TASKCARD, etc.
        return ProofContract(
            requirement_id=item_id,
            target=target,
            behavior_claim=f"artifact exists: {target}",
            risk="LOW",
            proof_target=ProofLevel.ARTIFACT_PRESENT,
        )


def proof_sufficient_for_closure(
    contract: ProofContract,
    test_paths: list,
    assessment: Optional[dict] = None,
) -> tuple:
    """
    Returns (sufficient: bool, gaps: list[str]).
    """
    gaps = []

    if assessment is None and test_paths:
        # Assess first available test file
        existing = [p for p in test_paths if Path(p).exists()]
        if existing:
            assessment = assess_proof_level(existing[0], contract)
        else:
            gaps.append("no test files found at declared paths")
            return False, gaps

    if assessment is None:
        gaps.append("no assessment available and no test paths")
        return False, gaps

    current_level = assessment.get("level", 0)
    required_level = int(contract.proof_target)

    if current_level < required_level:
        gaps.append(
            f"proof level {current_level} below required {required_level} "
            f"({contract.proof_target.name})"
        )

    strong_ratio = assessment.get("strong_ratio", 0.0)
    if contract.proof_target >= ProofLevel.EXACT_BEHAVIOR_VERIFIED and strong_ratio < STRONG_RATIO_THRESHOLD:
        gaps.append(
            f"strong_ratio {strong_ratio:.2f} below threshold {STRONG_RATIO_THRESHOLD} "
            f"(only {assessment.get('test_count',0) * strong_ratio:.0f}/{assessment.get('test_count',0)} tests have exact assertions)"
        )

    if contract.negative_cases:
        existing_test_paths = [p for p in test_paths if Path(p).exists()]
        found_negative = False
        for tp in existing_test_paths:
            try:
                src = Path(tp).read_text(encoding="utf-8", errors="replace")
                if any(kw in src for kw in ["invalid", "error", "negative", "bad", "fail", "wrong", "corrupt"]):
                    found_negative = True
                    break
            except Exception:
                pass
        if not found_negative:
            gaps.append("contract requires negative_cases but none found in test suite")

    if contract.exact_expected_results and assessment.get("strong_ratio", 0.0) == 0.0:
        gaps.append("contract requires exact_expected_results but no strong assertions detected")

    return len(gaps) == 0, gaps
