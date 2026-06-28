"""Test assertion quality scorer for certification.

Scores each test function's assertions on a 1-5 scale:
  1 = assert True / no assertion / assert x (bare)
  2 = assert x is not None / isinstance check only
  3 = type/len/membership check
  4 = value comparison (==, !=, >, <, in with specific values)
  5 = structural/behavioral verification with specific expected values

mission_id: CERT-EXHAUST-20260628
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]


def _rel(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()


def _score_assert(node: ast.Assert) -> int:
    """Score an assert statement 1-5."""
    test = node.test

    # assert True / assert False / assert 1
    if isinstance(test, ast.Constant):
        return 1

    # bare assert x
    if isinstance(test, ast.Name):
        return 1

    # assert not x
    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
        if isinstance(test.operand, ast.Name):
            return 1

    # assert x is (not) None
    if isinstance(test, ast.Compare) and len(test.ops) == 1:
        op = test.ops[0]
        comp = test.comparators[0]
        if isinstance(op, (ast.Is, ast.IsNot)) and isinstance(comp, ast.Constant) and comp.value is None:
            return 2

    # isinstance check
    if isinstance(test, ast.Call) and isinstance(test.func, ast.Name) and test.func.id == "isinstance":
        return 2

    # len() check or membership (in / not in)
    if isinstance(test, ast.Compare) and len(test.ops) == 1:
        op = test.ops[0]
        left = test.left
        comp = test.comparators[0]

        # assert len(x) == N or assert len(x) > 0
        if isinstance(left, ast.Call) and isinstance(left.func, ast.Name) and left.func.id == "len":
            if isinstance(comp, ast.Constant):
                return 4 if isinstance(comp.value, int) and comp.value > 0 else 3
            return 3

        # assert x in collection
        if isinstance(op, (ast.In, ast.NotIn)):
            if isinstance(comp, (ast.List, ast.Tuple, ast.Set)) and len(comp.elts) > 0:
                return 4
            return 3

        # Value comparison with specific constants
        if isinstance(op, (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE)):
            if isinstance(comp, ast.Constant) and comp.value is not None:
                # Specific value comparisons
                if isinstance(comp.value, (int, float, str)):
                    return 5 if isinstance(comp.value, str) and len(comp.value) > 0 else 4
                return 4
            if isinstance(left, ast.Constant) and left.value is not None:
                return 4
            # Variable == variable (structural comparison)
            return 3

    # Catch-all: any comparison with a constant literal
    if isinstance(test, ast.Compare):
        for comp in test.comparators:
            if isinstance(comp, ast.Constant) and comp.value is not None:
                return 4
        return 3

    # Method calls like x.startswith(), x.endswith() — moderate quality
    if isinstance(test, ast.Call):
        return 3

    # Default: bare expression
    return 2


def _score_pytest_assert(node: ast.Expr) -> int | None:
    """Score pytest.raises or similar context manager usage."""
    if not isinstance(node.value, ast.Call):
        return None
    func = node.value.func
    if isinstance(func, ast.Attribute) and func.attr == "raises":
        return 4  # pytest.raises is good exception testing
    return None


def score_test_file(path: Path) -> dict[str, Any]:
    """Score all test functions in a file."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError):
        return {"file": _rel(path), "functions": [], "error": "parse_error"}

    functions = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not node.name.startswith("test_"):
            continue

        assert_scores = []
        has_pytest_raises = False
        for child in ast.walk(node):
            if isinstance(child, ast.Assert):
                assert_scores.append(_score_assert(child))
            elif isinstance(child, ast.With):
                for item in child.items:
                    ctx = item.context_expr
                    if isinstance(ctx, ast.Call) and isinstance(ctx.func, ast.Attribute):
                        if ctx.func.attr == "raises":
                            has_pytest_raises = True
                            assert_scores.append(4)

        if not assert_scores:
            # No assertions found — could be using pytest.raises or implicit
            score = 2 if has_pytest_raises else 1
        else:
            score = min(assert_scores)

        functions.append({
            "name": node.name,
            "line": node.lineno,
            "assertion_count": len(assert_scores),
            "min_score": score,
            "scores": assert_scores,
        })

    avg = sum(f["min_score"] for f in functions) / len(functions) if functions else 0
    return {
        "file": _rel(path),
        "function_count": len(functions),
        "functions": functions,
        "file_avg_score": round(avg, 2),
        "file_min_score": min((f["min_score"] for f in functions), default=0),
    }


def score_test_directory(test_dir: Path) -> dict[str, Any]:
    """Score all test files in a directory."""
    target = test_dir if test_dir.is_absolute() else REPO_ROOT / test_dir
    if not target.exists():
        return {"error": f"{target} does not exist", "files": []}

    files = sorted(target.rglob("test_*.py")) if target.is_dir() else [target]
    results = []
    for path in files:
        if "__pycache__" in path.parts:
            continue
        results.append(score_test_file(path))

    total_functions = sum(r["function_count"] for r in results)
    all_scores = [f["min_score"] for r in results for f in r.get("functions", [])]
    score_dist = {s: all_scores.count(s) for s in range(1, 6)}
    weak_count = score_dist.get(1, 0)

    return {
        "metadata": {
            "authoritative_plan": "plans/.claude/crispy-jingling-snail.md",
            "mission_id": "CERT-EXHAUST-20260628",
            "tool": "assertion_quality_scorer",
        },
        "target": _rel(target),
        "file_count": len(results),
        "total_test_functions": total_functions,
        "score_distribution": score_dist,
        "weak_assertion_count": weak_count,
        "overall_avg_score": round(sum(all_scores) / len(all_scores), 2) if all_scores else 0,
        "overall_min_score": min(all_scores) if all_scores else 0,
        "files": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = score_test_directory(args.path)
    if args.output:
        output = args.output if args.output.is_absolute() else REPO_ROOT / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=False) + "\n", encoding="utf-8")
        print(json.dumps({
            "output": _rel(output),
            "total_functions": result["total_test_functions"],
            "weak_count": result["weak_assertion_count"],
            "avg_score": result["overall_avg_score"],
        }, sort_keys=True))
    else:
        print(json.dumps(result, indent=2, sort_keys=False))
    return 1 if result["weak_assertion_count"] > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
