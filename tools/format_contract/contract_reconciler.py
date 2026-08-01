"""Contract-to-implementation reconciler (L30 -> L03 handoff HO-010).

Compares a compiled format contract against observed product reality:
AST scan of src/python/{format}/ symbols, test-file presence, and the oracle
registry. Produces per-capability observed depth + proof status, applying
false-claim rules (a symbol is NOT proof; a test file name is NOT execution;
a skipped oracle is NOT a pass).

Observed-status ladder (subset of the L30 status taxonomy):
  NOT_STARTED -> IMPLEMENTED_UNPROVEN -> TESTED -> ORACLE_PROVEN

Output: reports/format-contract-layer/{format}-reconciliation.json
Exit codes: 0 report written · 1 error.
"""

from __future__ import annotations

import argparse
import ast
from collections import Counter
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator  # type: ignore[import-untyped]
from jsonschema.exceptions import SchemaError, ValidationError  # type: ignore[import-untyped]

sys.path.insert(0, str(Path(__file__).resolve().parent))

import stores  # type: ignore[import-not-found]
from canonical_io import load_yaml  # type: ignore[import-not-found]

REPORTS_DIR = stores.REPO_ROOT / "reports" / "format-contract-layer"
ORACLE_REGISTRY = stores.REPO_ROOT / "oracle" / "registry" / "format-oracle-registry.yaml"

# capability category -> function-name evidence patterns (probe, not proof).
# Every category used in compiled contracts MUST have an entry here — missing
# categories fall through to r"." which matches every function, inflating
# observed_status and hiding real gaps from the gap compiler.
_CATEGORY_SYMBOL_PATTERNS = {
    "parse": r"^(load|parse|read|from_|probe|detect|decode)",
    "model": r".",  # any class counts as model surface; refined below
    "edit": r"^(insert|add|remove|delete|update|set_|rename|append|move|clear)",
    "write": r"^(write|save|dump|serial|to_bytes|emit|encode)",
    "validate": r"^(validate|check|verify|lint)",
    "export": r"(_to_|^export|^convert)",
    "transform": r"^(convert|transform|detect_dialect|sniff)",
    "query": r"^(find|query|get_|select)",
    "lifecycle": r"^(load|save|parse|write)",
    "preserve": r"(roundtrip|preserve|lossless|unknown|extension|retain)",
    "security": r"(limit|max_|guard|safe|sanitize|restrict|traversal)",
    "performance": r"(stream|lazy|chunk|iter|mmap|buffer)",
    "calculate": r"(calc|total|sum|reconcil|amount|round|tax)",
    "resolve": r"(resolv|lookup|derefer|include|search_path|xinclude)",
    "advanced": r".",
}

_ORACLE_PROVABLE = {"parse", "write", "validate", "lifecycle"}

_EXACT_SCHEMA = "format-contracts/implementation-evidence@1"
_EXACT_STATUSES = {
    "implemented",
    "partial",
    "missing",
    "rejected",
    "unsupported",
    "preservation_only",
    "preview",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _document(path: Path, *, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise stores.StoreError(f"{label} does not exist: {path}")
    value = load_yaml(path)
    if not isinstance(value, dict):
        raise stores.StoreError(f"{label} must contain one mapping: {path}")
    return value


def _qualified_definitions(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="strict"))
    except (OSError, SyntaxError, UnicodeError) as exc:
        raise stores.StoreError(f"cannot inspect Python definitions in {path}: {exc}") from exc

    definitions: set[str] = set()

    class Visitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.parents: list[str] = []

        def _visit_definition(self, node: ast.AST, name: str) -> None:
            definitions.add("::".join([*self.parents, name]))
            self.parents.append(name)
            self.generic_visit(node)
            self.parents.pop()

        def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
            self._visit_definition(node, node.name)

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
            self._visit_definition(node, node.name)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: N802
            self._visit_definition(node, node.name)

    Visitor().visit(tree)
    return definitions


def _resolve_python_reference(reference: str, repo_root: Path, *, label: str) -> Path:
    if "::" not in reference:
        raise stores.StoreError(f"{label} must use path::qualified_name: {reference}")
    relative, qualified = reference.split("::", 1)
    path = repo_root / relative
    if not path.is_file():
        raise stores.StoreError(f"{label} path does not exist: {relative}")
    if qualified not in _qualified_definitions(path):
        raise stores.StoreError(f"{label} symbol does not exist: {reference}")
    return path


def _require_string_list(
    row: dict[str, Any], field: str, obligation_id: str
) -> list[str]:
    value = row.get(field)
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise stores.StoreError(f"{obligation_id}: {field} must be a list of non-empty strings")
    return value


def _validate_row_shape(row: dict[str, Any], obligation_id: str) -> None:
    status = row.get("status")
    if status not in _EXACT_STATUSES:
        raise stores.StoreError(f"{obligation_id}: invalid exact status {status!r}")
    source = _require_string_list(row, "source_symbols", obligation_id)
    positive = _require_string_list(row, "positive_test_selectors", obligation_id)
    negative = _require_string_list(row, "negative_test_selectors", obligation_id)
    executions = _require_string_list(row, "execution_evidence_ids", obligation_id)
    implemented = _require_string_list(row, "implemented_behavior", obligation_id)
    missing = _require_string_list(row, "missing_behavior", obligation_id)
    proof = row.get("proof_requirements")
    if not isinstance(proof, dict):
        raise stores.StoreError(f"{obligation_id}: proof_requirements must be a mapping")
    _require_string_list(proof, "positive", obligation_id)
    _require_string_list(proof, "negative", obligation_id)

    if status == "implemented":
        if not source or not positive or not executions or not implemented or missing:
            raise stores.StoreError(
                f"{obligation_id}: implemented requires source, positive tests, execution evidence, "
                "implemented behavior, and no missing behavior"
            )
    elif status == "partial":
        if not source or not positive or not executions or not implemented or not missing:
            raise stores.StoreError(
                f"{obligation_id}: partial requires implemented and missing behavior plus supporting evidence"
            )
    elif status == "missing":
        if source or positive or negative or executions or implemented or not missing:
            raise stores.StoreError(
                f"{obligation_id}: missing cannot claim implementation evidence and must name missing behavior"
            )
    elif not row.get("rationale"):
        raise stores.StoreError(f"{obligation_id}: {status} requires a rationale")


def reconcile_obligations(
    format_id: str,
    *,
    obligation_path: Path,
    evidence_path: Path,
    contract_path: Path | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Create an exact, curated, non-promoting obligation reconciliation."""
    root = (repo_root or stores.REPO_ROOT).resolve()
    contract_file = contract_path or (root / "shared" / "format-contracts" / f"{format_id}.yaml")
    contract = _document(contract_file, label="compiled contract")
    obligation_doc = _document(obligation_path, label="obligation register")
    evidence_doc = _document(evidence_path, label="implementation evidence")
    schema_file = root / "schemas" / "format-contracts" / "implementation-evidence.schema.json"
    schema = _document(schema_file, label="implementation evidence schema")
    try:
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(evidence_doc)
    except (SchemaError, ValidationError) as exc:
        location = ".".join(str(item) for item in exc.absolute_path) or "root"
        raise stores.StoreError(
            f"implementation evidence schema violation at {location}: {exc.message}"
        ) from exc

    if evidence_doc.get("schema") != _EXACT_SCHEMA:
        raise stores.StoreError(
            f"implementation evidence schema must be {_EXACT_SCHEMA}, got {evidence_doc.get('schema')!r}"
        )
    if obligation_doc.get("format_id") != format_id or evidence_doc.get("format_id") != format_id:
        raise stores.StoreError(f"foreign-format exact reconciliation input for {format_id}")

    canonical_rows = obligation_doc.get("obligations")
    mapped_rows = evidence_doc.get("obligations")
    if not isinstance(canonical_rows, list) or not isinstance(mapped_rows, list):
        raise stores.StoreError("obligation register and evidence must each contain an obligations list")
    if obligation_doc.get("obligation_count") != len(canonical_rows):
        raise stores.StoreError("obligation_count does not match canonical obligation rows")

    canonical_ids = [str(row.get("obligation_id", "")) for row in canonical_rows]
    mapped_ids = [str(row.get("obligation_id", "")) for row in mapped_rows]
    duplicate_canonical = sorted(key for key, count in Counter(canonical_ids).items() if count > 1)
    duplicate_mapped = sorted(key for key, count in Counter(mapped_ids).items() if count > 1)
    if duplicate_canonical or duplicate_mapped:
        raise stores.StoreError(
            f"duplicate obligation IDs: canonical={duplicate_canonical}, mapped={duplicate_mapped}"
        )
    missing_ids = sorted(set(canonical_ids) - set(mapped_ids))
    extra_ids = sorted(set(mapped_ids) - set(canonical_ids))
    if missing_ids or extra_ids:
        raise stores.StoreError(f"obligation set mismatch: missing={missing_ids}, extra={extra_ids}")

    contract_capabilities = {
        str(row.get("capability_id")) for row in contract.get("capabilities", [])
    }
    canonical_by_id = {row["obligation_id"]: row for row in canonical_rows}
    mapped_by_id = {row["obligation_id"]: row for row in mapped_rows}

    execution_rows = evidence_doc.get("execution_evidence", [])
    if not isinstance(execution_rows, list):
        raise stores.StoreError("execution_evidence must be a list")
    execution_by_id: dict[str, dict[str, Any]] = {}
    referenced_paths: set[Path] = set()
    for entry in execution_rows:
        evidence_id = str(entry.get("evidence_id", ""))
        if not evidence_id or evidence_id in execution_by_id:
            raise stores.StoreError(f"duplicate or empty execution evidence ID: {evidence_id!r}")
        relative = entry.get("path")
        if not isinstance(relative, str) or not relative:
            raise stores.StoreError(f"{evidence_id}: execution evidence path is required")
        evidence_file = root / relative
        executed = _document(evidence_file, label=f"execution evidence {evidence_id}")
        expected = entry.get("expected_result")
        if executed.get("result") != expected:
            raise stores.StoreError(
                f"{evidence_id}: declared result {expected!r} does not match {executed.get('result')!r}"
            )
        if entry.get("granularity") not in {"suite", "selector"}:
            raise stores.StoreError(f"{evidence_id}: granularity must be suite or selector")
        execution_by_id[evidence_id] = {**entry, "sha256": _sha256(evidence_file)}
        referenced_paths.add(evidence_file)

    output_rows: list[dict[str, Any]] = []
    for obligation_id in sorted(canonical_ids):
        canonical = canonical_by_id[obligation_id]
        mapped = mapped_by_id[obligation_id]
        if canonical.get("format_id") != format_id:
            raise stores.StoreError(f"{obligation_id}: canonical row has foreign format")
        if mapped.get("capability_id") != canonical.get("capability_id"):
            raise stores.StoreError(f"{obligation_id}: capability mismatch")
        if canonical.get("capability_id") not in contract_capabilities:
            raise stores.StoreError(f"{obligation_id}: capability is absent from compiled contract")
        _validate_row_shape(mapped, obligation_id)

        for reference in mapped["source_symbols"]:
            referenced_paths.add(
                _resolve_python_reference(reference, root, label=f"{obligation_id} source")
            )
        for field in ("positive_test_selectors", "negative_test_selectors"):
            for selector in mapped[field]:
                referenced_paths.add(
                    _resolve_python_reference(selector, root, label=f"{obligation_id} test")
                )
        for evidence_id in mapped["execution_evidence_ids"]:
            if evidence_id not in execution_by_id:
                raise stores.StoreError(f"{obligation_id}: unknown execution evidence {evidence_id}")

        status = mapped["status"]
        proof_status = {
            "implemented": "SUPPORTED_NONPROMOTING",
            "partial": "PARTIAL_NONPROMOTING",
            "missing": "MISSING",
            "rejected": "REJECTED_PROFILE",
            "unsupported": "UNSUPPORTED_PROFILE",
            "preservation_only": "PRESERVATION_ONLY",
            "preview": "PREVIEW_NONPROMOTING",
        }[status]
        output_rows.append({**mapped, "proof_status": proof_status})

    direct_inputs = {
        "compiled_contract": _sha256(contract_file),
        "implementation_evidence_schema": _sha256(schema_file),
        "obligation_register": _sha256(obligation_path),
        "implementation_evidence": _sha256(evidence_path),
        "reconciler": _sha256(Path(__file__)),
    }
    referenced_digests = {
        path.relative_to(root).as_posix(): _sha256(path)
        for path in sorted(referenced_paths, key=lambda item: item.as_posix())
    }
    statuses = Counter(row["status"] for row in output_rows)
    unresolved = sum(count for status, count in statuses.items() if status != "implemented")
    return {
        "schema": "format-contracts/obligation-reconciliation@1",
        "format_id": format_id,
        "contract_id": contract["contract_metadata"]["contract_id"],
        "input_digests": direct_inputs,
        "referenced_input_digests": referenced_digests,
        "execution_evidence": [execution_by_id[key] for key in sorted(execution_by_id)],
        "obligations": output_rows,
        "summary": {
            "total": len(output_rows),
            "by_status": {key: statuses[key] for key in sorted(statuses)},
            "unresolved": unresolved,
        },
        "proof_strength": "supporting_nonpromoting",
        "promotion_effect": "none",
        "truth_boundary": (
            "Exact source and test references plus declared executed evidence support characterization only; "
            "independent interoperability and certification proof remain separate obligations."
        ),
    }


def _scope_tests(tests: list[str], symbols: list[str], repo_root: Path) -> list[str]:
    """Narrow test files to those whose content references capability symbols.

    Falls back to the full test list if no symbols match (avoids false-negative
    penalty for capabilities whose symbols are only exercised indirectly).
    """
    if not symbols:
        return tests
    needle = re.compile("|".join(re.escape(s) for s in symbols[:30]))
    scoped: list[str] = []
    for rel in tests:
        try:
            text = (repo_root / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if needle.search(text):
            scoped.append(rel)
    return scoped if scoped else tests


def _scan_product(format_id: str) -> tuple[set[str], set[str]]:
    """(function names, class names) across src/python/{format}/ — read-only."""
    src = stores.REPO_ROOT / "src" / "python" / format_id
    functions: set[str] = set()
    classes: set[str] = set()
    if not src.is_dir():
        return functions, classes
    for path in sorted(src.rglob("*.py")):
        parts = path.parts
        if "build" in parts or "__pycache__" in parts:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.add(node.name.lower())
            elif isinstance(node, ast.ClassDef):
                classes.add(node.name)
    return functions, classes


def _scan_tests(format_id: str) -> list[str]:
    """Test files that reference the format package (presence, not execution)."""
    hits: list[str] = []
    for base in (stores.REPO_ROOT / "tests",):
        if not base.is_dir():
            continue
        for path in sorted(base.rglob(f"*{format_id}*.py")):
            if "__pycache__" not in path.parts:
                hits.append(str(path.relative_to(stores.REPO_ROOT)).replace("\\", "/"))
    return hits


def _oracle_status(format_id: str) -> str | None:
    data = load_yaml(ORACLE_REGISTRY) or {}
    for key in ("formats", "oracles", "entries"):
        seq = data.get(key)
        if isinstance(seq, list):
            for entry in seq:
                if str(entry.get("format_id", entry.get("format", ""))).lower() == format_id:
                    return str(entry.get("status", entry.get("verdict", "")))
        elif isinstance(seq, dict) and format_id in seq:
            entry = seq[format_id]
            return str(entry.get("status", entry.get("verdict", "")))
    return None


def _observe(cap: dict[str, Any], functions: set[str], classes: set[str],
             tests: list[str], oracle: str | None,
             repo_root: Path | None = None) -> dict[str, Any]:
    category = cap.get("category", "advanced")
    pattern = _CATEGORY_SYMBOL_PATTERNS.get(category, r".")
    if category == "model":
        symbols = sorted(classes)
    else:
        rx = re.compile(pattern)
        symbols = sorted(f for f in functions if rx.search(f))

    scoped_tests = tests
    if repo_root and symbols:
        scoped_tests = _scope_tests(tests, symbols, repo_root)

    if not symbols:
        status, observed_depth = "NOT_STARTED", 0
    elif not scoped_tests:
        status = "IMPLEMENTED_UNPROVEN"
        observed_depth = min(_impl_depth(category), cap.get("depth_required", 8))
    else:
        status = "TESTED"
        observed_depth = min(_impl_depth(category) + 1, cap.get("depth_required", 8), 6)
    if status == "TESTED" and category in _ORACLE_PROVABLE and oracle == "VERIFIED":
        status, observed_depth = "ORACLE_PROVEN", min(7, max(observed_depth, 7))

    return {
        "capability_id": cap["capability_id"],
        "category": category,
        "level": cap.get("level"),
        "depth_required": cap.get("depth_required"),
        "observed_status": status,
        "observed_depth": observed_depth,
        "gap_depth": max(0, int(cap.get("depth_required", 0)) - observed_depth),
        "product_symbols": symbols[:20],
        "test_files": scoped_tests[:10],
        "oracle_status": oracle,
        "false_claim_rules_applied": [
            "symbol presence is capability surface, not proof",
            "test-file presence marks TESTED at most; execution evidence belongs to the evidence layer",
            "oracle credit only for VERIFIED status and oracle-provable categories",
        ],
    }


def _impl_depth(category: str) -> int:
    return {
        "parse": 2, "model": 3, "edit": 4, "write": 4, "validate": 4,
        "export": 4, "transform": 3, "query": 3, "lifecycle": 3,
        "preserve": 2, "security": 2, "performance": 3, "advanced": 3,
        "calculate": 4, "resolve": 3,
    }.get(category, 2)


def reconcile(format_id: str) -> dict[str, Any]:
    doc = load_yaml(stores.contract_path(format_id))
    if not doc:
        raise stores.StoreError(f"no compiled contract for {format_id}")
    functions, classes = _scan_product(format_id)
    tests = _scan_tests(format_id)
    oracle = _oracle_status(format_id)
    observations = [
        _observe(cap, functions, classes, tests, oracle, stores.REPO_ROOT)
        for cap in doc.get("capabilities", [])
    ]
    gaps = [o for o in observations if o["gap_depth"] > 0 or o["observed_status"] == "NOT_STARTED"]
    return {
        "format_id": format_id,
        "contract_id": doc["contract_metadata"]["contract_id"],
        "contract_input_digests": doc["contract_metadata"]["input_digests"],
        "product_source_present": bool(functions or classes),
        "function_count": len(functions),
        "class_count": len(classes),
        "test_file_count": len(tests),
        "oracle_status": oracle,
        "capabilities": observations,
        "summary": {
            "total": len(observations),
            "with_gap": len(gaps),
            "by_status": {
                s: sum(1 for o in observations if o["observed_status"] == s)
                for s in ("NOT_STARTED", "IMPLEMENTED_UNPROVEN", "TESTED", "ORACLE_PROVEN")
            },
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format-id", required=True)
    parser.add_argument("--exact-obligations", action="store_true")
    parser.add_argument("--obligation-register", type=Path)
    parser.add_argument("--implementation-evidence", type=Path)
    args = parser.parse_args(argv)
    fmt = args.format_id.lower()
    try:
        if args.exact_obligations:
            if args.obligation_register is None or args.implementation_evidence is None:
                raise stores.StoreError(
                    "exact obligation mode requires --obligation-register and --implementation-evidence"
                )
            report = reconcile_obligations(
                fmt,
                obligation_path=args.obligation_register,
                evidence_path=args.implementation_evidence,
                repo_root=stores.REPO_ROOT,
            )
        else:
            report = reconcile(fmt)
    except stores.StoreError as exc:
        print(f"[fcl-reconciler] ERROR {exc}", file=sys.stderr)
        return 1
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    suffix = "obligation-reconciliation" if args.exact_obligations else "reconciliation"
    out = REPORTS_DIR / f"{fmt}-{suffix}.json"
    out.write_text(
        json.dumps(report, indent=2, sort_keys=args.exact_obligations) + "\n",
        encoding="utf-8",
    )
    if args.exact_obligations:
        print(
            f"[fcl-reconciler] {fmt}: {report['summary']['unresolved']}/"
            f"{report['summary']['total']} obligations unresolved; promotion=none -> {out}"
        )
        return 0
    print(f"[fcl-reconciler] {fmt}: {report['summary']['with_gap']}/{report['summary']['total']} "
          f"capabilities carry gaps -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
