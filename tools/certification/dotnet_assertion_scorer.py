"""Regex-based .NET test assertion quality scorer.

Scores each test method's assertions on a 1-5 scale:
  1 = no assertion / Assert.True(true) / bare Assert.NotNull
  2 = Assert.NotNull(x) / Assert.IsType<T>(x)
  3 = Assert.NotEmpty / Assert.Contains / type checks
  4 = Assert.Equal(expected, actual) with specific values
  5 = Assert.Equal with string/structural verification

TC-CERT-H-NETQA certification hardening.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

# Regex patterns for C# test methods and assertions
RE_TEST_METHOD = re.compile(r"\[(?:Fact|Theory)\].*?\n\s*public\s+(?:async\s+)?(?:Task|void)\s+(\w+)\s*\(", re.DOTALL)
RE_ASSERT_EQUAL = re.compile(r"Assert\.Equal\s*\(")
RE_ASSERT_TRUE = re.compile(r"Assert\.True\s*\(")
RE_ASSERT_FALSE = re.compile(r"Assert\.False\s*\(")
RE_ASSERT_NOTNULL = re.compile(r"Assert\.NotNull\s*\(")
RE_ASSERT_NULL = re.compile(r"Assert\.Null\s*\(")
RE_ASSERT_NOTEMPTY = re.compile(r"Assert\.NotEmpty\s*\(")
RE_ASSERT_EMPTY = re.compile(r"Assert\.Empty\s*\(")
RE_ASSERT_CONTAINS = re.compile(r"Assert\.Contains\s*\(")
RE_ASSERT_ISTYPE = re.compile(r"Assert\.IsType\s*<")
RE_ASSERT_THROWS = re.compile(r"Assert\.Throws\s*<")
RE_ASSERT_STARTSWITH = re.compile(r"Assert\.StartsWith\s*\(")
RE_ASSERT_ENDSWITH = re.compile(r"Assert\.EndsWith\s*\(")
RE_ASSERT_INRANGE = re.compile(r"Assert\.InRange\s*\(")
RE_ASSERT_GT = re.compile(r"Assert\.True\s*\(\s*\w+\s*[><=!]")

# Score each assertion type
ASSERTION_SCORES = {
    "Equal": 4,
    "True_bare": 1,
    "True_comparison": 4,
    "False": 3,
    "NotNull": 2,
    "Null": 2,
    "NotEmpty": 3,
    "Empty": 3,
    "Contains": 4,
    "IsType": 2,
    "Throws": 4,
    "StartsWith": 4,
    "EndsWith": 4,
    "InRange": 4,
}


def _score_assertions_in_method(method_body: str) -> list[int]:
    """Return list of assertion scores found in a method body."""
    scores = []

    for m in RE_ASSERT_EQUAL.finditer(method_body):
        # Check if it's Assert.Equal("specific", ...) vs Assert.Equal(var, var)
        after = method_body[m.end():m.end()+100]
        if re.match(r'\s*"[^"]+"\s*,', after) or re.match(r"\s*\d+\s*,", after):
            scores.append(5)  # String or numeric literal comparison
        else:
            scores.append(4)

    for _ in RE_ASSERT_CONTAINS.finditer(method_body):
        scores.append(4)

    for _ in RE_ASSERT_STARTSWITH.finditer(method_body):
        scores.append(4)

    for _ in RE_ASSERT_ENDSWITH.finditer(method_body):
        scores.append(4)

    for _ in RE_ASSERT_THROWS.finditer(method_body):
        scores.append(4)

    for _ in RE_ASSERT_INRANGE.finditer(method_body):
        scores.append(4)

    for _ in RE_ASSERT_NOTEMPTY.finditer(method_body):
        scores.append(3)

    for _ in RE_ASSERT_EMPTY.finditer(method_body):
        scores.append(3)

    for _ in RE_ASSERT_FALSE.finditer(method_body):
        scores.append(3)

    for _ in RE_ASSERT_NOTNULL.finditer(method_body):
        scores.append(2)

    for _ in RE_ASSERT_NULL.finditer(method_body):
        scores.append(2)

    for _ in RE_ASSERT_ISTYPE.finditer(method_body):
        scores.append(2)

    # Assert.True — check if it's bare true or comparison
    for m in RE_ASSERT_TRUE.finditer(method_body):
        after = method_body[m.end():m.end()+50]
        if re.match(r"\s*true\s*\)", after, re.IGNORECASE):
            scores.append(1)  # Assert.True(true) — trivial
        elif re.match(r"\s*\w+\s*[><=!]", after):
            scores.append(4)  # Assert.True(x > 0) — comparison
        else:
            scores.append(2)  # Assert.True(x) — truthiness check

    return scores


def score_test_file(path: Path) -> dict[str, Any]:
    """Score all test methods in a .cs file."""
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (UnicodeDecodeError, OSError):
        return {"file": str(path), "functions": [], "error": "read_error"}

    # Find test methods by [Fact] or [Theory] attributes
    functions = []
    # Split on method boundaries
    method_starts = [(m.start(), m.group(1)) for m in RE_TEST_METHOD.finditer(text)]

    for i, (start, name) in enumerate(method_starts):
        end = method_starts[i + 1][0] if i + 1 < len(method_starts) else len(text)
        body = text[start:end]

        scores = _score_assertions_in_method(body)

        if not scores:
            min_score = 1
        else:
            min_score = min(scores)

        line = text[:start].count("\n") + 1

        functions.append({
            "name": name,
            "line": line,
            "assertion_count": len(scores),
            "min_score": min_score,
            "scores": scores,
        })

    avg = sum(f["min_score"] for f in functions) / len(functions) if functions else 0
    return {
        "file": str(path.relative_to(REPO_ROOT).as_posix()) if path.is_relative_to(REPO_ROOT) else str(path),
        "function_count": len(functions),
        "functions": functions,
        "file_avg_score": round(avg, 2),
        "file_min_score": min((f["min_score"] for f in functions), default=0),
    }


def score_test_directory(test_dir: Path) -> dict[str, Any]:
    """Score all .cs test files in a directory."""
    target = test_dir if test_dir.is_absolute() else REPO_ROOT / test_dir
    if not target.exists():
        return {"error": f"{target} does not exist", "files": []}

    files = sorted(target.rglob("*Tests.cs")) if target.is_dir() else [target]
    results = []
    for path in files:
        if "bin" in path.parts or "obj" in path.parts:
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
            "tool": "dotnet_assertion_scorer",
        },
        "target": str(target.relative_to(REPO_ROOT).as_posix()) if target.is_relative_to(REPO_ROOT) else str(target),
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
        output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({
            "output": str(output.relative_to(REPO_ROOT).as_posix()),
            "total_functions": result["total_test_functions"],
            "weak_count": result["weak_assertion_count"],
            "avg_score": result["overall_avg_score"],
        }, sort_keys=True))
    else:
        print(json.dumps(result, indent=2))
    return 1 if result["weak_assertion_count"] > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
