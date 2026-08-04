"""Build a format's implementation-evidence ledger from verified inventory.

Generalized from the one-off IPYNB generator once four formats were found to
need the same work (GAP-020: safetensors 86, ubl 194, xliff 142, ora 134
obligations with no ledger at all). That is well past the directive's "at least
two accepted format slices prove a repeated need" threshold.

Two properties matter more than convenience:

**Nothing is invented.** Every source symbol and test selector is read out of
the real tree. The reconciler fails closed on a symbol that does not exist, so a
fabricated mapping cannot survive downstream anyway -- but it should not be
produced in the first place.

**The shipped-namespace filter is not optional.** A test file that imports only
the deprecated ``{format}.*`` shadow package cannot supply a selector, because
``forbidden_progress_claims`` bars counting that as coverage of the shipped
``format_factory.{format}`` namespace. GAP-018 measured this as the dominant
shape of the estate -- ubl and xliff are 91% shadow-only -- so ledgers for those
formats will legitimately open with large ``missing`` counts. That is the first
honest measurement they will have had, not a regression.

The capability-to-module mapping is human judgement about what implements what,
so it lives in a reviewable data file (``shared/format-contracts/ledger-maps/
{format}.yaml``) rather than buried in this script.

Every obligation is emitted ``partial`` at most. Mapping an obligation to
symbols is not proving it, and ``implemented`` requires the proof-requirement
audit that ``tools/ff6/audit_proof_requirements.py`` supports and a reader
completes.
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
MAP_DIR = REPO_ROOT / "shared" / "format-contracts" / "ledger-maps"
EVIDENCE_DIR = REPO_ROOT / "shared" / "format-contracts" / "implementation-evidence"
REGISTER_DIR = REPO_ROOT / "plans" / "strategic" / "ff6" / "obligations"

MAX_SYMBOLS = 4
MAX_SELECTORS = 3


class LedgerError(RuntimeError):
    """The register, map, or source tree could not be used."""


def _source_root(format_id: str) -> Path:
    return REPO_ROOT / "src" / "python" / format_id / "src" / "format_factory" / format_id


def _tests_root(format_id: str) -> Path:
    return REPO_ROOT / "tests" / "python" / format_id


def public_symbols(path: Path) -> list[str]:
    """Public top-level classes and functions actually defined in ``path``."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: list[str] = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            names.append(node.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                names.append(node.name)
    return names


def exercises_shipped_namespace(path: Path) -> bool:
    """True when the test file imports format_factory, not only the shadow package."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            modules.add(node.module.split(".")[0])
    return "format_factory" in modules


def test_functions(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    ]


def build(format_id: str, *, dry_run: bool = False) -> dict[str, Any]:
    """Build the ledger. Execution evidence comes from the map, not a guess.

    The reconciler compares an evidence entry's declared ``expected_result``
    against the ``result`` recorded in the artifact it points at, so the path
    must name something that actually carries a result -- a skill transcript,
    not a reconciliation report. Both are declared in the ledger map so the
    claim is reviewable rather than invented here.
    """
    map_path = MAP_DIR / f"{format_id}.yaml"
    register_path = REGISTER_DIR / f"{format_id}.yaml"
    for path in (map_path, register_path):
        if not path.exists():
            raise LedgerError(f"required input not found: {path}")

    capability_map = yaml.safe_load(map_path.read_bytes().decode("utf-8"))
    register = yaml.safe_load(register_path.read_bytes().decode("utf-8"))
    mapping = capability_map.get("capabilities") or {}
    execution = capability_map.get("execution_evidence") or {}
    evidence_path = execution.get("path")
    evidence_result = execution.get("result")
    evidence_boundary = execution.get("truth_boundary")
    if not (evidence_path and evidence_result and evidence_boundary):
        raise LedgerError(
            f"{map_path} must declare execution_evidence with path, result and "
            "truth_boundary; the reconciler validates the declared result "
            "against the artifact, so it cannot be guessed here"
        )
    if not (REPO_ROOT / evidence_path).exists():
        raise LedgerError(f"declared execution evidence does not exist: {evidence_path}")
    obligations = register.get("obligations") or []
    if not obligations:
        raise LedgerError(f"{register_path} declares no obligations")

    src_root = _source_root(format_id)
    tests_root = _tests_root(format_id)
    prefix = f"src/python/{format_id}/src/format_factory/{format_id}"

    entries: list[dict[str, Any]] = []
    unmapped: set[str] = set()
    shadow_excluded: set[str] = set()

    for obligation in obligations:
        capability = obligation.get("capability_id")
        spec = mapping.get(capability)
        if not spec:
            unmapped.add(capability)
            continue

        symbols: list[str] = []
        for module in spec.get("modules", []):
            module_path = src_root / module
            if not module_path.exists():
                raise LedgerError(f"mapped module does not exist: {module_path}")
            for name in public_symbols(module_path)[:MAX_SYMBOLS]:
                symbols.append(f"{prefix}/{module}::{name}")

        declared_tests = spec.get("tests", [])
        valid: list[str] = []
        excluded: list[str] = []
        for test_file in declared_tests:
            test_path = tests_root / test_file
            if not test_path.exists():
                raise LedgerError(f"mapped test file does not exist: {test_path}")
            if exercises_shipped_namespace(test_path):
                valid.append(test_file)
            else:
                excluded.append(test_file)
                shadow_excluded.add(test_file)

        selectors: list[str] = []
        for test_file in valid:
            for name in test_functions(tests_root / test_file)[:MAX_SELECTORS]:
                selectors.append(f"tests/python/{format_id}/{test_file}::{name}")

        required = obligation.get("required_tests") or []
        missing: list[str] = [
            "Not yet audited against this obligation's declared proof "
            "requirements: "
            + ("; ".join(required) if required else "none declared in the register.")
        ]
        if not valid:
            missing.append(
                "NO SHIPPED-NAMESPACE TEST COVERAGE. "
                + (
                    "The mapped test files ("
                    + ", ".join(excluded)
                    + ") import only the deprecated shadow package, not "
                    f"format_factory.{format_id}, so under "
                    "forbidden_progress_claims they cannot count as coverage of "
                    "the shipped namespace."
                    if excluded
                    else "No test file is mapped to this capability."
                )
            )
        elif excluded:
            missing.append(
                "Shadow-package test files excluded from evidence ("
                + ", ".join(excluded)
                + "): they exercise the deprecated package, not the shipped one."
            )

        # `missing` means no implementation EVIDENCE, and the schema enforces
        # that literally: no source symbols, no selectors, no execution ids.
        # Source that exists but is untested by the shipped namespace is not
        # evidence, so it is not cited here -- the mapped modules stay recorded
        # in the ledger map, which is where the reader will look for them.
        has_evidence = bool(valid)
        entries.append(
            {
                "obligation_id": obligation["obligation_id"],
                "capability_id": capability,
                "status": "partial" if has_evidence else "missing",
                "source_symbols": symbols if has_evidence else [],
                "positive_test_selectors": selectors,
                "negative_test_selectors": [],
                "execution_evidence_ids": (
                    [f"{format_id.upper()}-BASELINE-SUITE"] if has_evidence else []
                ),
                # A `missing` obligation must not claim implemented behavior --
                # the reconciler rejects that, correctly: saying "source exists
                # and the suite passes" about something with no valid evidence
                # is the overclaim the status exists to prevent.
                "implemented_behavior": (
                    [
                        "Production source implementing this capability exists at "
                        "the mapped symbols and the mapped shipped-namespace suite "
                        "passes."
                    ]
                    if has_evidence
                    else []
                ),
                "missing_behavior": missing,
                "proof_requirements": {
                    "positive": required or ["Derive from rule_text during the audit."],
                    "negative": [
                        "Selector-bound negative cases are not yet identified."
                    ],
                },
            }
        )

    document = {
        "schema": "format-contracts/implementation-evidence@1",
        "format_id": format_id,
        "visibility": "generated",
        "generated_by": "claude",
        "execution_evidence": [
            {
                "evidence_id": f"{format_id.upper()}-BASELINE-SUITE",
                "path": evidence_path,
                "expected_result": evidence_result,
                "granularity": "suite",
                "truth_boundary": evidence_boundary,
            }
        ],
        "obligations": entries,
    }

    summary = {
        "format_id": format_id,
        "obligations": len(entries),
        "partial": sum(1 for e in entries if e["status"] == "partial"),
        "missing": sum(1 for e in entries if e["status"] == "missing"),
        "unmapped_capabilities": sorted(unmapped),
        "shadow_files_excluded": sorted(shadow_excluded),
    }
    if unmapped:
        raise LedgerError(
            f"unmapped capabilities for {format_id}: {sorted(unmapped)}. "
            "Every capability must be mapped or explicitly excluded."
        )

    if not dry_run:
        EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
        (EVIDENCE_DIR / f"{format_id}.yaml").write_text(
            yaml.safe_dump(document, sort_keys=False, width=100, allow_unicode=True),
            encoding="utf-8",
        )
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tools.ff6.build_evidence_ledger",
        description="Build a format's implementation-evidence ledger.",
    )
    parser.add_argument("--format-id", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    try:
        summary = build(args.format_id, dry_run=args.dry_run)
    except LedgerError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(
        f"{summary['format_id']}: {summary['obligations']} obligations "
        f"({summary['partial']} partial, {summary['missing']} missing)"
    )
    if summary["shadow_files_excluded"]:
        print("  shadow-package files excluded from evidence:")
        for name in summary["shadow_files_excluded"]:
            print(f"    {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
