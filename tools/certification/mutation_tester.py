"""Lightweight mutation tester for Windows (mutmut requires WSL).

Applies simple AST-level mutations to a target module, runs the test suite,
and records kill/survive rates. Each mutation is applied in isolation.

TC-CERT-R3 certification hardening.

Usage:
    python tools/certification/mutation_tester.py \
        --target src/python/fods/parser.py \
        --tests tests/python/fods/ \
        --output reports/certification/fods/mutation-baseline.json
"""
from __future__ import annotations

import argparse
import ast
import copy
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VENV_PYTEST = str(REPO_ROOT / ".venv" / "Scripts" / "pytest.exe")


class MutationOperator:
    """Defines simple mutation operators."""

    @staticmethod
    def negate_comparison(node: ast.Compare) -> list[ast.Compare]:
        """Swap comparison operators."""
        swap = {
            ast.Eq: ast.NotEq, ast.NotEq: ast.Eq,
            ast.Lt: ast.GtE, ast.GtE: ast.Lt,
            ast.Gt: ast.LtE, ast.LtE: ast.Gt,
            ast.Is: ast.IsNot, ast.IsNot: ast.Is,
            ast.In: ast.NotIn, ast.NotIn: ast.In,
        }
        mutations = []
        for i, op in enumerate(node.ops):
            new_op_type = swap.get(type(op))
            if new_op_type:
                new_node = copy.deepcopy(node)
                new_node.ops[i] = new_op_type()
                mutations.append(new_node)
        return mutations

    @staticmethod
    def negate_boolean(node: ast.UnaryOp) -> ast.UnaryOp | None:
        """Remove 'not' from boolean expressions."""
        if isinstance(node.op, ast.Not):
            return node.operand
        return None

    @staticmethod
    def swap_true_false(node: ast.Constant) -> ast.Constant | None:
        """Swap True/False constants."""
        if node.value is True:
            return ast.Constant(value=False)
        if node.value is False:
            return ast.Constant(value=True)
        return None

    @staticmethod
    def boundary_off_by_one(node: ast.Constant) -> list[ast.Constant]:
        """Change integer constants by +/- 1."""
        if isinstance(node.value, int) and not isinstance(node.value, bool):
            return [
                ast.Constant(value=node.value + 1),
                ast.Constant(value=node.value - 1),
            ]
        return []

    @staticmethod
    def swap_return_none(node: ast.Return) -> ast.Return | None:
        """Replace return value with None."""
        if node.value is not None:
            new_node = copy.deepcopy(node)
            new_node.value = ast.Constant(value=None)
            return new_node
        return None


def collect_mutations(source: str) -> list[dict]:
    """Collect all possible mutations from source code."""
    tree = ast.parse(source)
    mutations = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            for mutated in MutationOperator.negate_comparison(node):
                mutations.append({
                    "type": "negate_comparison",
                    "line": node.lineno,
                    "original": ast.dump(node),
                    "mutated": ast.dump(mutated),
                    "node": node,
                    "replacement": mutated,
                })

        elif isinstance(node, ast.Constant):
            # True/False swap
            swapped = MutationOperator.swap_true_false(node)
            if swapped:
                mutations.append({
                    "type": "swap_bool",
                    "line": node.lineno,
                    "original": repr(node.value),
                    "mutated": repr(swapped.value),
                    "node": node,
                    "replacement": swapped,
                })
            # Off-by-one
            for m in MutationOperator.boundary_off_by_one(node):
                mutations.append({
                    "type": "off_by_one",
                    "line": node.lineno,
                    "original": repr(node.value),
                    "mutated": repr(m.value),
                    "node": node,
                    "replacement": m,
                })

        elif isinstance(node, ast.Return):
            ret_none = MutationOperator.swap_return_none(node)
            if ret_none:
                mutations.append({
                    "type": "return_none",
                    "line": node.lineno,
                    "original": "return <value>",
                    "mutated": "return None",
                    "node": node,
                    "replacement": ret_none,
                })

    return mutations


def apply_mutation(source: str, mutation: dict) -> str:
    """Apply a single mutation to source and return modified source."""
    tree = ast.parse(source)
    target_line = mutation["line"]
    mutation_type = mutation["type"]

    class Mutator(ast.NodeTransformer):
        def __init__(self):
            self.applied = False

        def visit_Compare(self, node):
            if not self.applied and node.lineno == target_line and mutation_type == "negate_comparison":
                self.applied = True
                return ast.fix_missing_locations(mutation["replacement"])
            return self.generic_visit(node)

        def visit_Constant(self, node):
            if not self.applied and node.lineno == target_line and mutation_type in ("swap_bool", "off_by_one"):
                if repr(node.value) == mutation["original"]:
                    self.applied = True
                    return ast.fix_missing_locations(mutation["replacement"])
            return self.generic_visit(node)

        def visit_Return(self, node):
            if not self.applied and node.lineno == target_line and mutation_type == "return_none":
                self.applied = True
                return ast.fix_missing_locations(mutation["replacement"])
            return self.generic_visit(node)

    mutator = Mutator()
    new_tree = mutator.visit(tree)
    ast.fix_missing_locations(new_tree)
    return ast.unparse(new_tree)


def run_tests(test_dir: str, timeout: int = 60) -> bool:
    """Run pytest on test_dir. Returns True if tests pass (mutation survived)."""
    try:
        result = subprocess.run(
            [VENV_PYTEST, test_dir, "-x", "-q", "--tb=no", "--no-header", "--timeout=30"],
            capture_output=True, text=True, timeout=timeout,
            cwd=str(REPO_ROOT),
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False  # Timeout = killed


def run_mutation_testing(target_path: str, test_dir: str, max_mutations: int = 50) -> dict:
    """Run mutation testing on target module."""
    target = Path(target_path)
    original_source = target.read_text(encoding="utf-8")

    mutations = collect_mutations(original_source)
    print(f"Found {len(mutations)} possible mutations in {target.name}")

    if len(mutations) > max_mutations:
        # Sample evenly across lines
        step = len(mutations) // max_mutations
        mutations = mutations[::step][:max_mutations]
        print(f"Sampled down to {len(mutations)} mutations")

    killed = 0
    survived = 0
    errors = 0
    results = []

    for i, mut in enumerate(mutations):
        # Strip non-serializable AST nodes before recording
        mut_record = {k: v for k, v in mut.items() if k not in ("node", "replacement")}

        try:
            mutated_source = apply_mutation(original_source, mut)
        except Exception as e:
            mut_record["status"] = "error"
            mut_record["error"] = str(e)
            errors += 1
            results.append(mut_record)
            continue

        # Write mutated source
        target.write_text(mutated_source, encoding="utf-8")

        try:
            tests_pass = run_tests(test_dir)
            if tests_pass:
                mut_record["status"] = "survived"
                survived += 1
            else:
                mut_record["status"] = "killed"
                killed += 1
        except Exception as e:
            mut_record["status"] = "error"
            mut_record["error"] = str(e)
            errors += 1
        finally:
            # Restore original
            target.write_text(original_source, encoding="utf-8")

        results.append(mut_record)
        total = killed + survived
        print(f"  [{i+1}/{len(mutations)}] {mut_record['type']} L{mut_record['line']}: "
              f"{mut_record['status']} (kill rate: {killed}/{total}={killed/total*100:.0f}%)" if total else "")

    total_tested = killed + survived
    kill_rate = (killed / total_tested * 100) if total_tested else 0

    return {
        "target": str(target),
        "test_dir": test_dir,
        "total_mutations": len(mutations),
        "killed": killed,
        "survived": survived,
        "errors": errors,
        "kill_rate_pct": round(kill_rate, 1),
        "verdict": "STRONG" if kill_rate >= 70 else "NEEDS_HARDENING",
        "survivors": [r for r in results if r.get("status") == "survived"],
    }


def main():
    parser = argparse.ArgumentParser(description="Lightweight mutation tester")
    parser.add_argument("--target", required=True, help="Path to source file to mutate")
    parser.add_argument("--tests", required=True, help="Path to test directory")
    parser.add_argument("--output", help="Path to write JSON results")
    parser.add_argument("--max-mutations", type=int, default=50, help="Max mutations to test")
    args = parser.parse_args()

    print(f"Mutation testing: {args.target}")
    print(f"Test suite: {args.tests}")

    result = run_mutation_testing(args.target, args.tests, args.max_mutations)

    print("\n=== Results ===")
    print(f"Total mutations: {result['total_mutations']}")
    print(f"Killed: {result['killed']}")
    print(f"Survived: {result['survived']}")
    print(f"Errors: {result['errors']}")
    print(f"Kill rate: {result['kill_rate_pct']}%")
    print(f"Verdict: {result['verdict']}")

    if result["survivors"]:
        print("\nSurvivors (test gaps):")
        for s in result["survivors"][:10]:
            print(f"  L{s['line']}: {s['type']} {s['original']} -> {s['mutated']}")

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(f"\nResults written to: {out}")


if __name__ == "__main__":
    main()
