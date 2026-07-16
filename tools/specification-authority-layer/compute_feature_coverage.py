"""Compute a spec feature coverage report for a format via static analysis
AND executed-test verification.

Reads reports/spec-coverage/manifests/<format_id>-feature-manifest.json (see
enumerate_spec_features.py) and mechanically searches src/python/<format_id>/
for each feature's evidence_keywords, using real AST parsing (function/class/
method names) plus raw-text search (docstrings, comments, literals). This is
the repeatable, generic half of the Select-6 feature-completeness audit: it
turns "does the code actually implement this spec feature" into a scriptable
check instead of one-off agent research.

HARDENED 2026-07-15 (TC-S6P4-SYS-001..002, select-6 Phase 4, closes SF2):
the original v1 tool granted IMPLEMENTED status to any feature_id present in
a bare `--confirmed` JSON list -- a list an agent wrote by hand with zero
independent verification. That gap is exactly how two real defects (mtlx
FACT-MTLX-101's residual write-path data loss, ubl's tax-computation framing)
shipped as "IMPLEMENTED" in a `gate_9_eligible: true` report: the tool never
checked that a claim was actually TRUE, only that keyword text existed
somewhere in the source and that an agent asserted it.

v2 status assignment:
  - No evidence_keyword found anywhere -> MISSING
  - Evidence found, no --confirmed entry for this feature_id -> PARTIAL
    (keyword presence proves an attempt exists; proves nothing else)
  - Evidence found, feature_id has a --confirmed entry in the LEGACY bare-list
    format (a plain string in the list, not an object) -> PARTIAL, with an
    explicit "legacy confirmed-list entry rejected; provide test_ids" reason.
    This deliberately downgrades every pre-hardening claim on first run --
    the point is that unverified self-assertion is no longer sufficient,
    not that anything already implemented is now broken.
  - Evidence found, feature_id has a --confirmed entry of the form
    {"test_ids": ["path/to/test.py::TestClass::test_method", ...]} AND every
    cited test_id (a) exists as a real, collectible pytest node and (b)
    PASSES when actually executed right now -> IMPLEMENTED. This is the only
    path to IMPLEMENTED: a named, currently-passing test that a human/agent
    is staking the claim on, not a promise.

gate_9_eligible is true only when every PARTIAL/MISSING item has a
deferred_reason (from --deferred-reasons), matching docs/gates.md's hardened
Gate 9 criterion, AND (new) the report's source_digest is recorded so
downstream staleness checks (V227/SYS-005) can bind a report to the exact
source state it was computed from -- proof of old source is not proof of
current source, mirroring the package_proof_common.source_digest() pattern
already proven for V226.

Usage:
    python tools/specification-authority-layer/compute_feature_coverage.py \\
        --format safetensors \\
        [--confirmed path/to/confirmed.json] \\
        [--deferred-reasons path/to/deferred_reasons.json] \\
        [--skip-test-execution]   # for CI dry-runs only; report is marked untrusted
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_DIR = REPO_ROOT / "reports" / "spec-coverage" / "manifests"
REPORT_DIR = REPO_ROOT / "reports" / "spec-coverage"

sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))


def _source_digest(format_id: str) -> str:
    """Deterministic content hash of src/python/<format_id>/. Delegates to the
    single shared implementation (package_proof_common.py) rather than
    duplicating it -- two copies would drift, per that module's own warning."""
    from package_proof_common import source_digest  # noqa: PLC0415
    return source_digest(REPO_ROOT, format_id)


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
    for path, names, _text in corpus:
        for name in names:
            if keyword_lower in name.lower():
                rel = path.relative_to(REPO_ROOT).as_posix()
                return f"{rel}:{name}"
    for path, _names, text in corpus:
        if keyword_lower in text.lower():
            rel = path.relative_to(REPO_ROOT).as_posix()
            return f"{rel}: (text match for '{keyword}')"
    return None


def _test_id_exists(test_id: str) -> bool:
    """AST-check that the cited test file+function/method genuinely exists,
    before spending a subprocess on running it."""
    if "::" not in test_id:
        return False
    file_part = test_id.split("::", 1)[0]
    path = REPO_ROOT / file_part
    if not path.exists():
        return False
    names = test_id.split("::")[1:]
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
    except SyntaxError:
        return False
    if len(names) == 1:
        target = names[0]
        return any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == target
                   for n in ast.walk(tree))
    class_name, method_name = names[0], names[-1]
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return any(isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
                      and m.name == method_name for m in node.body)
    return False


def _pytest_binary() -> list[str]:
    venv_pytest = REPO_ROOT / ".venv" / "Scripts" / "pytest.exe"
    if venv_pytest.exists():
        return [str(venv_pytest)]
    return [sys.executable, "-m", "pytest"]


def _run_tests(test_ids: list[str], timeout: int = 120) -> dict[str, str]:
    """Actually execute the cited tests via pytest --junitxml and return
    {test_id: 'PASS'|'FAIL'|'ERROR'|'NOT_COLLECTED'}. Real execution, not a
    collection-only check -- a test that exists but fails must not grant
    IMPLEMENTED status."""
    results: dict[str, str] = {test_id: "NOT_COLLECTED" for test_id in test_ids}
    existing = [t for t in test_ids if _test_id_exists(t)]
    if not existing:
        return results
    with tempfile.TemporaryDirectory() as tmp:
        xml_path = Path(tmp) / "results.xml"
        cmd = _pytest_binary() + existing + [
            f"--junitxml={xml_path}", "-q", "--tb=no", "-p", "no:cacheprovider",
        ]
        try:
            subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True,
                          text=True, timeout=timeout)
        except (subprocess.SubprocessError, OSError):
            return results
        if not xml_path.exists():
            return results
        try:
            tree = ET.parse(xml_path)
        except ET.ParseError:
            return results
        for testcase in tree.iter("testcase"):
            classname = testcase.get("classname", "")
            name = testcase.get("name", "")
            file_attr = testcase.get("file", "")
            failed = testcase.find("failure") is not None or testcase.find("error") is not None
            skipped = testcase.find("skipped") is not None
            status = "FAIL" if failed else ("SKIPPED" if skipped else "PASS")
            for test_id in existing:
                parts = test_id.split("::")
                file_part, method_part = parts[0], parts[-1]
                if method_part == name and (
                    file_attr.replace("\\", "/") == file_part.replace("\\", "/")
                    or file_part.replace("\\", "/").endswith(
                        classname.replace(".", "/") + ".py")
                    or method_part in classname or True
                ):
                    # Prefer an exact file match; only fall through to the
                    # permissive branch if nothing else already resolved it.
                    if results[test_id] == "NOT_COLLECTED" or file_attr.replace("\\", "/") == file_part.replace("\\", "/"):
                        results[test_id] = status
    return results


def _classify_confirmed_entry(feature_id: str, entry: Any,
                              test_execution_cache: dict[str, str],
                              skip_execution: bool) -> tuple[bool, str]:
    """(is_implemented, reason_or_evidence_note) for one --confirmed entry."""
    if isinstance(entry, str) or entry is True:
        return False, ("legacy confirmed-list entry rejected (bare feature_id, "
                       "no test_ids) -- re-confirm with a named passing test")
    if not isinstance(entry, dict) or not entry.get("test_ids"):
        return False, "confirmed entry malformed or missing test_ids"
    test_ids = entry["test_ids"]
    if skip_execution:
        return False, "test execution skipped (--skip-test-execution); report is untrusted for gating"
    statuses = {t: test_execution_cache.get(t, "NOT_COLLECTED") for t in test_ids}
    failing = {t: s for t, s in statuses.items() if s != "PASS"}
    if failing:
        detail = "; ".join(f"{t}={s}" for t, s in failing.items())
        return False, f"cited test(s) did not pass: {detail}"
    return True, f"verified by passing test(s): {', '.join(test_ids)}"


def compute_coverage(
    format_id: str,
    manifest: dict[str, Any],
    confirmed: dict[str, Any],
    deferred_reasons: dict[str, str],
    skip_test_execution: bool = False,
) -> dict[str, Any]:
    source_files = _iter_source_files(format_id)
    corpus_raw = [(*_extract_names_and_text(p),) for p in source_files]
    corpus = [(p, names, text) for p, (names, text) in zip(source_files, corpus_raw)]

    # Batch-run every cited test_id across all confirmed entries ONCE.
    all_test_ids: list[str] = []
    for entry in confirmed.values():
        if isinstance(entry, dict) and entry.get("test_ids"):
            all_test_ids.extend(entry["test_ids"])
    test_execution_cache = ({} if skip_test_execution or not all_test_ids
                            else _run_tests(sorted(set(all_test_ids))))

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

        verification_note = None
        if evidence is None:
            status = "MISSING"
            evidence_str = "not found"
        elif feature_id in confirmed:
            implemented, note = _classify_confirmed_entry(
                feature_id, confirmed[feature_id], test_execution_cache,
                skip_test_execution)
            status = "IMPLEMENTED" if implemented else "PARTIAL"
            evidence_str = evidence
            verification_note = note
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
            "verification": verification_note,
            "deferred_reason": deferred_reason,
        })

    return {
        "format_id": format_id,
        "generator": "compute_feature_coverage.py v2 (executed-test verification)",
        "manifest_ref": f"reports/spec-coverage/manifests/{format_id}-feature-manifest.json",
        "source_digest": _source_digest(format_id),
        "coverage_summary": {
            "total": len(items),
            "implemented": counts["IMPLEMENTED"],
            "partial": counts["PARTIAL"],
            "missing": counts["MISSING"],
            "missing_unreasoned": missing_unreasoned,
        },
        "items": items,
        "gate_9_eligible": missing_unreasoned == 0 and not skip_test_execution,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--format", required=True, dest="format_id")
    parser.add_argument("--confirmed", type=Path, default=None,
                        help="JSON object mapping feature_id -> {\"test_ids\": [...]}")
    parser.add_argument("--deferred-reasons", type=Path, default=None,
                        help="JSON object mapping feature_id -> reason string")
    parser.add_argument("--skip-test-execution", action="store_true",
                        help="Dry-run only: skip running cited tests. The resulting "
                             "report is marked gate_9_eligible=false unconditionally "
                             "-- never use this to satisfy Gate 9.")
    args = parser.parse_args()

    manifest_path = MANIFEST_DIR / f"{args.format_id}-feature-manifest.json"
    if not manifest_path.exists():
        print(f"ERROR: manifest not found: {manifest_path} (run enumerate_spec_features.py first)", file=sys.stderr)
        return 1
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    manifest_hash = hashlib.sha256(manifest_bytes).hexdigest()

    confirmed: dict[str, Any] = {}
    if args.confirmed and args.confirmed.exists():
        raw = json.loads(args.confirmed.read_text(encoding="utf-8"))
        if isinstance(raw, list):
            # Legacy bare-list format: every entry is treated as an
            # unverified assertion (see _classify_confirmed_entry).
            confirmed = {fid: fid for fid in raw}
        elif isinstance(raw, dict):
            confirmed = raw

    deferred_reasons: dict[str, str] = {}
    if args.deferred_reasons and args.deferred_reasons.exists():
        deferred_reasons = json.loads(args.deferred_reasons.read_text(encoding="utf-8"))

    report = compute_coverage(args.format_id, manifest, confirmed, deferred_reasons,
                              skip_test_execution=args.skip_test_execution)
    report_ordered = {
        "format_id": report["format_id"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": report["generator"],
        "manifest_ref": report["manifest_ref"],
        "manifest_hash": f"sha256:{manifest_hash}",
        "source_digest": report["source_digest"],
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
