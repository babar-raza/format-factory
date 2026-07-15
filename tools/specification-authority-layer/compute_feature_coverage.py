"""Compute a spec feature coverage report for a format via static analysis.

Reads reports/spec-coverage/manifests/<format_id>-feature-manifest.json (see
enumerate_spec_features.py) and mechanically searches src/python/<format_id>/
for each feature's evidence_keywords, using real AST parsing (function/class/
method names) plus raw-text search (docstrings, comments, literals). This is
the repeatable, generic half of the Select-6 feature-completeness audit: it
turns "does the code actually implement this spec feature" into a scriptable
check instead of one-off agent research.

Status assignment:
  - No evidence_keyword found anywhere -> MISSING
  - Evidence found, feature_id NOT in --confirmed list -> PARTIAL
    (keyword presence proves an attempt exists; it does not prove correctness/
    completeness — that requires the confirming test suite, so a human/agent
    must explicitly confirm before a feature counts as IMPLEMENTED)
  - Evidence found, feature_id IS in --confirmed list -> IMPLEMENTED

gate_9_eligible is true only when every PARTIAL/MISSING item has a
deferred_reason (from --deferred-reasons), matching docs/gates.md's hardened
Gate 9 criterion: implementation_authorized may only flip to true when this
report shows no un-reasoned gaps.

Usage:
    python tools/specification-authority-layer/compute_feature_coverage.py \\
        --format safetensors \\
        [--confirmed path/to/confirmed_ids.json] \\
        [--deferred-reasons path/to/deferred_reasons.json]
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_DIR = REPO_ROOT / "reports" / "spec-coverage" / "manifests"
REPORT_DIR = REPO_ROOT / "reports" / "spec-coverage"


def _iter_source_files(format_id: str) -> list[Path]:
    src_dir = REPO_ROOT / "src" / "python" / format_id
    if not src_dir.is_dir():
        return []
    return sorted(
        p for p in src_dir.rglob("*.py")
        if "__pycache__" not in p.parts and "build" not in p.parts
    )


def _extract_names_and_text(path: Path) -> tuple[set[str], str]:
    """Return (all function/class/method/property names, raw file text)."""
    text = path.read_text(encoding="utf-8", errors="replace")
    names: set[str] = set()
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError:
        return names, text
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
    return names, text


def _find_evidence(keyword: str, corpus: list[tuple[Path, set[str], str]]) -> str | None:
    """Return 'relative/path.py:name_or_substring' for the first match, else None."""
    keyword_lower = keyword.lower()
    # Prefer exact/substring matches against real identifiers first (stronger evidence).
    for path, names, _text in corpus:
        for name in names:
            if keyword_lower in name.lower():
                rel = path.relative_to(REPO_ROOT).as_posix()
                return f"{rel}:{name}"
    # Fall back to raw-text search (docstrings, literals, comments).
    for path, _names, text in corpus:
        if keyword_lower in text.lower():
            rel = path.relative_to(REPO_ROOT).as_posix()
            return f"{rel}: (text match for '{keyword}')"
    return None


def compute_coverage(
    format_id: str,
    manifest: dict[str, Any],
    confirmed_ids: set[str],
    deferred_reasons: dict[str, str],
) -> dict[str, Any]:
    source_files = _iter_source_files(format_id)
    corpus = [(*_extract_names_and_text(p),) for p in source_files]
    corpus = [(p, names, text) for p, (names, text) in zip(source_files, corpus)]

    items: list[dict[str, Any]] = []
    counts = {"IMPLEMENTED": 0, "PARTIAL": 0, "MISSING": 0}
    missing_unreasoned = 0

    for feature in manifest["features"]:
        feature_id = feature["feature_id"]
        evidence: str | None = None
        for keyword in feature["evidence_keywords"]:
            evidence = _find_evidence(keyword, corpus)
            if evidence:
                break

        if evidence is None:
            status = "MISSING"
            evidence_str = "not found"
        elif feature_id in confirmed_ids:
            status = "IMPLEMENTED"
            evidence_str = evidence
        else:
            status = "PARTIAL"
            evidence_str = evidence

        counts[status] += 1
        deferred_reason = deferred_reasons.get(feature_id)
        if status != "IMPLEMENTED" and deferred_reason is None:
            missing_unreasoned += 1

        items.append({
            "feature_id": feature_id,
            "name": feature["name"],
            "requirement_level": feature["requirement_level"],
            "status": status,
            "evidence": evidence_str,
            "deferred_reason": deferred_reason,
        })

    return {
        "format_id": format_id,
        "generator": "compute_feature_coverage.py v1",
        "manifest_ref": f"reports/spec-coverage/manifests/{format_id}-feature-manifest.json",
        "coverage_summary": {
            "total": len(items),
            "implemented": counts["IMPLEMENTED"],
            "partial": counts["PARTIAL"],
            "missing": counts["MISSING"],
            "missing_unreasoned": missing_unreasoned,
        },
        "items": items,
        "gate_9_eligible": missing_unreasoned == 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", required=True, dest="format_id")
    parser.add_argument("--confirmed", type=Path, default=None, help="JSON list of feature_ids confirmed complete (tested)")
    parser.add_argument("--deferred-reasons", type=Path, default=None, help="JSON object mapping feature_id -> reason string")
    args = parser.parse_args()

    manifest_path = MANIFEST_DIR / f"{args.format_id}-feature-manifest.json"
    if not manifest_path.exists():
        print(f"ERROR: manifest not found: {manifest_path} (run enumerate_spec_features.py first)", file=sys.stderr)
        return 1
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    manifest_hash = hashlib.sha256(manifest_bytes).hexdigest()

    confirmed_ids: set[str] = set()
    if args.confirmed and args.confirmed.exists():
        confirmed_ids = set(json.loads(args.confirmed.read_text(encoding="utf-8")))

    deferred_reasons: dict[str, str] = {}
    if args.deferred_reasons and args.deferred_reasons.exists():
        deferred_reasons = json.loads(args.deferred_reasons.read_text(encoding="utf-8"))

    report = compute_coverage(args.format_id, manifest, confirmed_ids, deferred_reasons)
    report_ordered = {
        "format_id": report["format_id"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": report["generator"],
        "manifest_ref": report["manifest_ref"],
        "manifest_hash": f"sha256:{manifest_hash}",
        "coverage_summary": report["coverage_summary"],
        "items": report["items"],
        "gate_9_eligible": report["gate_9_eligible"],
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORT_DIR / f"{args.format_id}-coverage-report.json"
    out_path.write_text(json.dumps(report_ordered, indent=2) + "\n", encoding="utf-8")

    summary = report["coverage_summary"]
    print(
        f"{args.format_id}: {summary['implemented']} IMPLEMENTED, "
        f"{summary['partial']} PARTIAL, {summary['missing']} MISSING "
        f"(of {summary['total']}), missing_unreasoned={summary['missing_unreasoned']}, "
        f"gate_9_eligible={report['gate_9_eligible']}"
    )
    print(f"Report written to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
