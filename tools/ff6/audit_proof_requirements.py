"""Audit obligation evidence against each obligation's declared proof requirements.

Why this exists
---------------
``proof_requirement_audit_lesson`` in the execution directive was written after
TC-FF6-NRRD-GOLDEN-SLICE-001 shipped an interoperability defect while passing 28
tests, two independent oracles, an installed-wheel proof and an independent
validator review. None of those checks compared the tests that were WRITTEN
against the proof the obligation DECLARES. Its obligation asked for a matrix
"by type AND encoding"; only the type axis was tested, and the defect lived in
the untested axis.

The judgement half of that audit -- does this selector really exercise that
named dimension -- needs a reader. But several ways of failing it are purely
mechanical, and those are what this module catches:

* an obligation with no positive selector at all,
* a selector naming a test function that does not exist,
* a selector pointing at a test file that imports only the deprecated shadow
  package rather than the shipped ``format_factory.{format}`` namespace,
* a selector pointing at a test that is skipped or xfailed -- the exact shape
  of the golden slice's "empty endian value" case, which sat in a selector list
  looking like proof while ``pytest.skip`` made it prove nothing,
* an obligation whose requirement names more dimensions than it has selectors,
  which cannot be conclusive but reliably surfaces the "matrix with one axis
  tested" shape.

Everything here is a finding, not a verdict. The tool never marks an obligation
implemented; it narrows what a reader must judge.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTER_DIR = REPO_ROOT / "plans" / "strategic" / "ff6" / "obligations"
EVIDENCE_DIR = REPO_ROOT / "shared" / "format-contracts" / "implementation-evidence"

#: Requirement prose is split on these to count declared dimensions. Deliberately
#: crude: the count is a prompt for a reader, never a pass/fail.
_DIMENSION_SPLIT = re.compile(r";|\band\b|,")

SKIP_MARKERS = ("skip", "xfail")


class AuditError(RuntimeError):
    """The register or evidence ledger could not be read."""


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise AuditError(f"not found: {path}")
    value = yaml.safe_load(path.read_bytes().decode("utf-8"))
    if not isinstance(value, dict):
        raise AuditError(f"{path} is not a mapping")
    return value


def _test_index(format_id: str) -> tuple[dict[str, set[str]], dict[str, bool], dict[str, set[str]]]:
    """Return per-file test names, shipped-namespace flags, and skipped tests."""
    root = REPO_ROOT / "tests" / "python" / format_id
    names: dict[str, set[str]] = {}
    shipped: dict[str, bool] = {}
    skipped: dict[str, set[str]] = {}
    if not root.exists():
        return names, shipped, skipped

    for path in sorted(root.rglob("*.py")):
        rel = path.relative_to(REPO_ROOT).as_posix()
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue

        modules: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    modules.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                modules.add(node.module.split(".")[0])
        shipped[rel] = "format_factory" in modules

        found: set[str] = set()
        skips: set[str] = set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef) or not node.name.startswith("test_"):
                continue
            found.add(node.name)
            decorated = any(
                marker in ast.unparse(decorator)
                for decorator in node.decorator_list
                for marker in SKIP_MARKERS
            )
            # A skip nested inside an `if` still leaves other paths running, so
            # it is reported distinctly: the golden slice's empty-endian case is
            # one branch of a parametrized test, not a wholly dead test. Both
            # weaken a selector, but conflating them would overstate the finding.
            conditional_skip = False
            unconditional_skip = False
            for inner in ast.walk(node):
                if not (isinstance(inner, ast.Call) and "skip" in ast.unparse(inner.func)):
                    continue
                if any(
                    isinstance(ancestor, ast.If)
                    for ancestor in ast.walk(node)
                    if isinstance(ancestor, ast.If)
                    and any(inner is n for n in ast.walk(ancestor))
                ):
                    conditional_skip = True
                else:
                    unconditional_skip = True
            if decorated or unconditional_skip:
                skips.add(node.name)
            elif conditional_skip:
                skips.add(f"~{node.name}")  # '~' marks a partial skip path
        names[rel] = found
        skipped[rel] = skips
    return names, shipped, skipped


def audit_format(format_id: str) -> dict[str, Any]:
    """Audit every obligation for one format. Pure: reads, never writes."""
    register = _load_yaml(REGISTER_DIR / f"{format_id}.yaml")
    evidence = _load_yaml(EVIDENCE_DIR / f"{format_id}.yaml")
    requirements = {
        entry["obligation_id"]: entry for entry in register.get("obligations", [])
    }
    names, shipped, skipped = _test_index(format_id)

    findings: list[dict[str, Any]] = []
    for entry in evidence.get("obligations", []):
        obligation_id = entry.get("obligation_id")
        source = requirements.get(obligation_id, {})
        declared = source.get("required_tests") or []
        selectors = list(entry.get("positive_test_selectors") or []) + list(
            entry.get("negative_test_selectors") or []
        )

        issues: list[str] = []
        if not selectors:
            issues.append("NO_SELECTORS")

        for selector in selectors:
            file_part, _, test_name = selector.partition("::")
            # Selectors may be file::test, file::Class::method, or carry pytest
            # parametrization. Only the final segment is the function name;
            # matching the whole remainder reported class-based tests as missing.
            base = test_name.split("::")[-1].split("[")[0]
            if file_part not in names:
                issues.append(f"MISSING_FILE:{file_part}")
                continue
            if base not in names[file_part]:
                issues.append(f"MISSING_TEST:{selector}")
            if not shipped.get(file_part, False):
                issues.append(f"SHADOW_PACKAGE_SELECTOR:{file_part}")
            file_skips = skipped.get(file_part, set())
            if base in file_skips:
                issues.append(f"SKIPPED_TEST_AS_PROOF:{selector}")
            elif f"~{base}" in file_skips:
                issues.append(f"PARTIAL_SKIP_PATH_IN_SELECTOR:{selector}")

        dimensions = 0
        for requirement in declared:
            dimensions += len(
                [part for part in _DIMENSION_SPLIT.split(requirement) if part.strip()]
            )
        if dimensions and selectors and dimensions > len(selectors):
            issues.append(
                f"FEWER_SELECTORS_THAN_DECLARED_DIMENSIONS:{len(selectors)}<{dimensions}"
            )

        findings.append(
            {
                "obligation_id": obligation_id,
                "capability_id": entry.get("capability_id"),
                "status": entry.get("status"),
                "level": source.get("level"),
                "declared_requirements": declared,
                "declared_dimension_estimate": dimensions,
                "selector_count": len(selectors),
                "issues": sorted(set(issues)),
                "audit_ready": not issues,
            }
        )

    blocking = [f for f in findings if f["issues"]]
    return {
        "format_id": format_id,
        "obligations": len(findings),
        "mechanically_clean": len(findings) - len(blocking),
        "with_issues": len(blocking),
        "issue_histogram": _histogram(blocking),
        "findings": findings,
        "truth_boundary": (
            "Mechanical findings only. A clean result means nothing here is "
            "provably wrong; it does NOT mean the selectors actually exercise "
            "the declared dimensions. That judgement still requires a reader, "
            "and no obligation may move off `partial` on this tool's output "
            "alone."
        ),
    }


def _histogram(findings: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for finding in findings:
        for issue in finding["issues"]:
            key = issue.split(":")[0]
            counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: -item[1]))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tools.ff6.audit_proof_requirements",
        description="Audit obligation evidence against declared proof requirements.",
    )
    parser.add_argument("--format-id", required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--issues-only", action="store_true", help="list only obligations with findings"
    )
    args = parser.parse_args(argv)

    try:
        result = audit_format(args.format_id)
    except AuditError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    print(f"{result['format_id']}: {result['obligations']} obligations")
    print(f"  mechanically clean : {result['mechanically_clean']}")
    print(f"  with findings      : {result['with_issues']}")
    for issue, count in result["issue_histogram"].items():
        print(f"      {issue:<40} {count}")
    for finding in result["findings"]:
        if args.issues_only and not finding["issues"]:
            continue
        if finding["issues"]:
            print(f"  {finding['obligation_id']} [{finding['level']}]")
            for issue in finding["issues"]:
                print(f"      {issue}")
    print()
    print(result["truth_boundary"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
