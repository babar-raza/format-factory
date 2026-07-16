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
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import stores
from canonical_io import load_yaml

REPORTS_DIR = stores.REPO_ROOT / "reports" / "format-contract-layer"
ORACLE_REGISTRY = stores.REPO_ROOT / "oracle" / "registry" / "format-oracle-registry.yaml"

# capability category -> function-name evidence patterns (probe, not proof)
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
    "preserve": r"^(roundtrip|preserve)",
    "security": r"(limit|max_|guard|safe)",
    "performance": r"(stream|lazy|chunk|iter)",
    "advanced": r".",
}

_ORACLE_PROVABLE = {"parse", "write", "validate", "lifecycle"}


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


def _observe(cap: dict, functions: set[str], classes: set[str],
             tests: list[str], oracle: str | None) -> dict:
    category = cap.get("category", "advanced")
    pattern = _CATEGORY_SYMBOL_PATTERNS.get(category, r".")
    if category == "model":
        symbols = sorted(classes)
    else:
        rx = re.compile(pattern)
        symbols = sorted(f for f in functions if rx.search(f))

    if not symbols:
        status, observed_depth = "NOT_STARTED", 0
    elif not tests:
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
        "test_files": tests[:10],
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
    }.get(category, 2)


def reconcile(format_id: str) -> dict:
    doc = load_yaml(stores.contract_path(format_id))
    if not doc:
        raise stores.StoreError(f"no compiled contract for {format_id}")
    functions, classes = _scan_product(format_id)
    tests = _scan_tests(format_id)
    oracle = _oracle_status(format_id)
    observations = [
        _observe(cap, functions, classes, tests, oracle)
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
    args = parser.parse_args(argv)
    fmt = args.format_id.lower()
    try:
        report = reconcile(fmt)
    except stores.StoreError as exc:
        print(f"[fcl-reconciler] ERROR {exc}", file=sys.stderr)
        return 1
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORTS_DIR / f"{fmt}-reconciliation.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"[fcl-reconciler] {fmt}: {report['summary']['with_gap']}/{report['summary']['total']} "
          f"capabilities carry gaps -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
