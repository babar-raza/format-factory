"""
neighboring_risk_reviewer.py — Neighboring risk scanner (TC-FG-006).

Scans sibling test files in the same directory to identify:
- Duplicate test function names (same function in multiple files)
- Weaker sibling tests (neighboring files with lower proof level)
- Misleading evidence (assertions that pass constant-zero/constant-false implementations)

Used by closure_challenger.py as an additive (non-blocking) gate.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Optional

_SUPERVISOR = Path(__file__).resolve().parent
if str(_SUPERVISOR) not in sys.path:
    sys.path.insert(0, str(_SUPERVISOR))

from proof_adequacy_contract import assess_proof_level


def _get_function_names(file_path: str) -> list:
    """Return all test function names from a Python test file."""
    try:
        source = Path(file_path).read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
        names = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                names.append(node.name)
        return names
    except Exception:
        return []


def _detect_misleading_assertions(file_path: str) -> list:
    """
    Detect assertions that would pass a constant-zero or constant-false implementation.

    A misleading assertion is one like:
    - assert result == [0, 0, 0, 0]  (passes constant-zero return)
    - assert result == []             (passes empty return)
    - assert result == False          (passes constant-false return)
    - assert len(result) == 0         (passes empty return)

    Returns list of (function_name, reason) tuples.
    """
    misleading = []
    try:
        source = Path(file_path).read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
    except Exception:
        return misleading

    _ZERO_LIKE_SCALAR_CONSTANTS = (0, False, None, "")

    for node in ast.walk(tree):
        if not (isinstance(node, ast.FunctionDef) and node.name.startswith("test_")):
            continue
        fn_name = node.name
        for anode in ast.walk(node):
            if not isinstance(anode, ast.Assert):
                continue
            test = anode.test
            if not isinstance(test, ast.Compare):
                continue
            ops = test.ops
            comparators = test.comparators
            if not any(isinstance(op, ast.Eq) for op in ops):
                continue
            # Check if ALL comparators are zero-like constants
            for c in comparators:
                if isinstance(c, ast.Constant) and c.value in (0, False, None, ""):
                    misleading.append((fn_name, f"asserts == {c.value!r} (passes constant-zero/false impl)"))
                elif isinstance(c, (ast.List, ast.Tuple)) and not c.elts:
                    misleading.append((fn_name, "asserts == [] or () (passes empty-return impl)"))
                elif isinstance(c, ast.List):
                    # Check for all-zeros list like [0,0,0,0]
                    all_zero = all(
                        isinstance(e, ast.Constant) and e.value in (0, 0.0, False)
                        for e in c.elts
                    )
                    if all_zero and len(c.elts) > 0:
                        misleading.append((fn_name, f"asserts == {[0]*len(c.elts)} (passes constant-zero impl)"))

    return misleading


def review_neighboring_risks(
    target_test_path: str,
    target_module: str,
    test_dir: str,
    authorized_exclusions: Optional[list] = None,
) -> dict:
    """
    Scan neighboring test files for risks.

    Returns:
        {
          "target": str,
          "duplicate_tests": [str],
          "weaker_sibling_tests": [{"file": str, "name": str, "level": int, "reason": str}],
          "misleading_evidence": [{"function": str, "reason": str}],
          "classification": {
              "must_fix": [str],
              "must_reconcile": [str],
              "valid_deferred": [str],
              "out_of_scope": [str],
          }
        }
    """
    exclusion_ids = set()
    if authorized_exclusions:
        for ex in authorized_exclusions:
            if isinstance(ex, dict):
                exclusion_ids.add(ex.get("id", ""))
                exclusion_ids.add(ex.get("test_name", ""))

    result: dict = {
        "target": target_test_path,
        "duplicate_tests": [],
        "weaker_sibling_tests": [],
        "misleading_evidence": [],
        "classification": {
            "must_fix": [],
            "must_reconcile": [],
            "valid_deferred": [],
            "out_of_scope": [],
        },
    }

    target_path = Path(target_test_path)
    test_dir_path = Path(test_dir)
    if not target_path.exists() or not test_dir_path.exists():
        return result

    # Get target file's assessment and function names
    target_assessment = assess_proof_level(str(target_path))
    target_level = target_assessment.get("level", 0)
    target_fn_names = set(_get_function_names(str(target_path)))

    # Detect misleading assertions in TARGET file itself
    misleading_in_target = _detect_misleading_assertions(str(target_path))
    for fn_name, reason in misleading_in_target:
        if fn_name not in exclusion_ids:
            result["misleading_evidence"].append({"function": fn_name, "reason": reason})
            # Misleading assertions in the primary file are must_reconcile (not must_fix)
            result["classification"]["must_reconcile"].append(
                f"{target_path.name}::{fn_name} — {reason}"
            )

    # Scan siblings
    sibling_files = [
        f for f in test_dir_path.glob("test_*.py")
        if f.resolve() != target_path.resolve() and f.name != target_path.name
    ]

    all_sibling_fn_names: dict = {}  # name → [file, ...]
    for sf in sibling_files:
        sibling_fns = _get_function_names(str(sf))
        for fn in sibling_fns:
            all_sibling_fn_names.setdefault(fn, []).append(str(sf))

    # Duplicate test detection
    for fn_name in target_fn_names:
        if fn_name in all_sibling_fn_names and fn_name not in exclusion_ids:
            for sibling_file in all_sibling_fn_names[fn_name]:
                dup_key = f"{target_path.name}::{fn_name} also in {Path(sibling_file).name}"
                result["duplicate_tests"].append(dup_key)
                result["classification"]["must_reconcile"].append(
                    f"Duplicate: {dup_key}"
                )

    # Weaker sibling detection — check first few siblings for now
    for sf in sibling_files[:10]:  # limit scan scope
        sibling_assessment = assess_proof_level(str(sf))
        sibling_level = sibling_assessment.get("level", 0)
        if sibling_level < target_level and sibling_level > 0:
            weak_sibling_fns = sibling_assessment.get("weak_tests", [])
            for wf in weak_sibling_fns:
                wf_name = wf.get("name", "")
                if wf_name not in exclusion_ids:
                    result["weaker_sibling_tests"].append({
                        "file": str(sf),
                        "name": wf_name,
                        "level": wf.get("max_level", sibling_level),
                        "reason": f"sibling {sf.name} has lower proof level ({sibling_level} < {target_level})",
                    })
            # Weaker siblings are out_of_scope unless they directly relate to same target_module
            if target_module.lower() in sf.name.lower():
                result["classification"]["must_reconcile"].append(
                    f"Weaker sibling: {sf.name} (level {sibling_level} < target level {target_level})"
                )
            else:
                result["classification"]["out_of_scope"].append(
                    f"Weaker sibling (different module): {sf.name}"
                )

    # Misleading evidence in siblings related to target_module
    for sf in sibling_files:
        if target_module.lower() not in sf.name.lower():
            continue
        misleading = _detect_misleading_assertions(str(sf))
        for fn_name, reason in misleading:
            if fn_name not in exclusion_ids:
                result["misleading_evidence"].append({"function": fn_name, "file": str(sf), "reason": reason})
                result["classification"]["must_reconcile"].append(
                    f"Misleading in sibling {sf.name}::{fn_name} — {reason}"
                )

    return result
