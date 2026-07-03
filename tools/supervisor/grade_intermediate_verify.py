"""
grade_intermediate_verify.py — Intermediate Evidence Content Verifier

Provides content-level evidence verification that is deeper than pure path-only checking
but does not require an LLM. Used when the LLM grader is unavailable (EXTERNAL_BLOCKER:
llm_grader_endpoint_credentials_not_configured).

This module is called from the sprint grading pipeline as a fallback between:
  Level 1: path-only (file exists at declared path)     ← current minimum
  Level 2: intermediate content check (THIS MODULE)     ← added by TC-HARD-008
  Level 3: LLM semantic verification (grade_declared_work.semantic_verify_item)

TC-HARD-008 authority: polished-hopping-glacier.md H5 taskcard TC-HARD-008
Integration note: grade_declared_work.py is at its baseline_loc_cap (820 LOC, write-once).
This module is a standalone companion. Integration via direct call or import.

Usage (standalone):
    python tools/supervisor/grade_intermediate_verify.py \
        --declaration .local/evidences/<run_id>/evidence-declaration.yaml

Usage (as library):
    from grade_intermediate_verify import intermediate_verify_item
    result = intermediate_verify_item(evidence_paths=["tests/python/fods/test_foo.py"], ...)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------------------------
# Core verification logic
# ---------------------------------------------------------------------------

def _check_file_nonzero(path: Path) -> tuple[bool, str]:
    """Return (ok, detail). True if file exists and has non-zero content."""
    if not path.exists():
        return False, f"missing: {path}"
    size = path.stat().st_size
    if size == 0:
        return False, f"empty (0 bytes): {path}"
    return True, f"non-empty ({size} bytes): {path}"


def _check_python_test_content(path: Path) -> tuple[bool, str, dict]:
    """Check Python test file using AST assertion-strength analysis (TC-FG-002b).

    Returns (ok: bool, detail: str, ast_info: dict) where ast_info contains
    strong_ratio, overall_classification, weak_tests, strong_tests from
    proof_adequacy_contract.assess_proof_level.

    Replaces the prior string-search fallback that returned adequate=True for
    any file containing 'def test_' and 'assert'.
    """
    try:
        _supervisor_dir = Path(__file__).resolve().parent
        import sys as _sys
        if str(_supervisor_dir) not in _sys.path:
            _sys.path.insert(0, str(_supervisor_dir))
        from proof_adequacy_contract import assess_proof_level, STRONG_RATIO_THRESHOLD
        assessment = assess_proof_level(str(path))
    except Exception as _import_err:
        # If AST analysis itself fails, fall back to conservative string-search
        # but return adequate=False to avoid false-green (safer than adequate=True)
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            has_test_fn = "def test_" in text
            has_assert = "assert " in text or "assertEqual" in text
            if not has_test_fn:
                return False, "no def test_ function found", {}
            if not has_assert:
                return False, "no assertion statements found", {}
            test_count = text.count("def test_")
            # Conservative: return adequate=False when AST unavailable
            return False, f"AST analysis unavailable ({_import_err}); {test_count} test functions found (manual review required)", {}
        except Exception as e:
            return False, f"read error: {e}", {}

    classification = assessment.get("overall_classification", "NO_PROOF")
    strong_ratio = assessment.get("strong_ratio", 0.0)
    test_count = assessment.get("test_count", 0)
    weak_tests = assessment.get("weak_tests", [])
    strong_tests = assessment.get("strong_tests", [])

    if test_count == 0:
        return False, "no test functions found", assessment

    weak_summary = ""
    if weak_tests:
        weak_summary = f"; weak: {', '.join(t['name'] for t in weak_tests[:3])}"

    detail = (
        f"{classification} ({test_count} tests, {len(strong_tests)} strong / "
        f"{len(weak_tests)} weak, strong_ratio={strong_ratio:.2f}{weak_summary})"
    )

    # adequate=True when classification is STRONG_PROOF or PARTIAL_PROOF (has some strong assertions)
    # adequate=False when WEAK_PROOF (all assertions are type/shape only) or NO_PROOF
    # TC-FG-002b: WEAK_PROOF (strong_ratio=0.0) must NOT be adequate — prevents false-green
    ok = classification in ("STRONG_PROOF", "PARTIAL_PROOF")
    return ok, detail, assessment


def _is_stub_test(text: str) -> bool:
    """Detect trivially-true stub tests."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    # Stub: every non-blank, non-decorator, non-def, non-class line is just 'pass' or 'assert True'
    content_lines = [ln for ln in lines
                     if not ln.startswith("#") and not ln.startswith("@")
                     and not ln.startswith("def ") and not ln.startswith("class ")
                     and not ln.startswith("import ") and not ln.startswith("from ")
                     and ln not in ("", "pass", "...", '"""', "'''")]
    if not content_lines:
        return True  # No content
    stub_markers = {"assert True", "assert true", "pass", "..."}
    real_content = [ln for ln in content_lines if ln not in stub_markers]
    return len(real_content) == 0


def _check_yaml_content(path: Path) -> tuple[bool, str]:
    """Check YAML evidence file has non-trivial content."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return False, f"read error: {e}"
    if len(text.strip()) < 20:
        return False, f"trivially short YAML ({len(text)} chars)"
    # Check for expected evidence fields
    key_fields = ["sprint_id", "run_id", "completed_work_items", "tests_run",
                  "worker_self_verdict", "evidence_root"]
    found = [f for f in key_fields if f in text]
    if len(found) < 3:
        return False, f"few key fields found: {found} (expected >=3)"
    return True, f"YAML has {len(found)}/{len(key_fields)} expected fields"


def _check_json_content(path: Path) -> tuple[bool, str]:
    """Check JSON evidence file parses and has non-trivial content."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        data = json.loads(text)
    except json.JSONDecodeError as e:
        return False, f"invalid JSON: {e}"
    except Exception as e:
        return False, f"read error: {e}"
    if isinstance(data, dict):
        if len(data) == 0:
            return False, "empty JSON object {}"
        return True, f"JSON object with {len(data)} keys"
    if isinstance(data, list):
        if len(data) == 0:
            return False, "empty JSON array []"
        return True, f"JSON array with {len(data)} items"
    return True, f"JSON scalar: {type(data).__name__}"


def _check_markdown_content(path: Path) -> tuple[bool, str]:
    """Check Markdown report has substantive content."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return False, f"read error: {e}"
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if len(lines) < 5:
        return False, f"too few lines ({len(lines)} non-blank lines)"
    has_header = any(ln.startswith("#") for ln in lines)
    return True, f"markdown with {len(lines)} lines, header={'yes' if has_header else 'no'}"


def _check_single_file(path: Path) -> dict:
    """Run appropriate content check based on file type."""
    ok_nonzero, detail_nonzero = _check_file_nonzero(path)
    if not ok_nonzero:
        return {"path": str(path), "exists": False, "content_ok": False,
                "detail": detail_nonzero, "check_type": "existence"}

    suffix = path.suffix.lower()
    _ast_info: dict = {}
    if suffix == ".py" and "test_" in path.name:
        ok, detail, _ast_info = _check_python_test_content(path)
        check_type = "python_test_content"
    elif suffix == ".yaml" or suffix == ".yml":
        ok, detail = _check_yaml_content(path)
        check_type = "yaml_content"
    elif suffix == ".json":
        ok, detail = _check_json_content(path)
        check_type = "json_content"
    elif suffix == ".md":
        ok, detail = _check_markdown_content(path)
        check_type = "markdown_content"
    else:
        # Generic: file exists and is non-zero (already confirmed above)
        ok, detail = True, detail_nonzero
        check_type = "nonzero_existence"

    result = {
        "path": str(path),
        "exists": True,
        "content_ok": ok,
        "detail": detail,
        "check_type": check_type,
    }
    if _ast_info:
        result["strong_ratio"] = _ast_info.get("strong_ratio", 0.0)
        result["overall_classification"] = _ast_info.get("overall_classification", "")
        result["weak_tests"] = _ast_info.get("weak_tests", [])
    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def intermediate_verify_item(
    evidence_paths: list[str],
    item_id: str = "",
    repo_root: "Path | None" = None,
) -> dict:
    """Run intermediate content verification on declared evidence paths.

    Returns a dict compatible with grade_declared_work.semantic_verify_item output:
        {
            "adequate": bool,
            "confidence": float,  # 0.0-1.0
            "stub_detected": bool,
            "deficiencies": [str],
            "llm_used": False,
            "intermediate_verified": True,
            "source": "intermediate_content_check",
            "checks": [per-file check results],
        }
    """
    _repo = repo_root or REPO_ROOT
    if not evidence_paths:
        return {
            "adequate": False, "confidence": 0.0, "stub_detected": False,
            "deficiencies": ["no_evidence_paths_provided"],
            "llm_used": False, "intermediate_verified": False,
            "source": "intermediate_content_check",
            "checks": [],
        }

    checks = []
    for ep in evidence_paths:
        full = _repo / ep
        checks.append(_check_single_file(full))

    ok_count = sum(1 for c in checks if c["content_ok"])
    fail_count = len(checks) - ok_count
    stub_detected = any(
        "stub test detected" in c.get("detail", "") for c in checks
    )

    deficiencies = [c["detail"] for c in checks if not c["content_ok"]]

    # TC-FG-002b: propagate AST-based strong_ratio from test file checks
    # Use the first test file's AST result if available
    _test_checks = [c for c in checks if c.get("check_type") == "python_test_content"]
    _strong_ratio = None
    _overall_classification = None
    _weak_tests = []
    if _test_checks:
        tc = _test_checks[0]
        _strong_ratio = tc.get("strong_ratio")
        _overall_classification = tc.get("overall_classification")
        _weak_tests = tc.get("weak_tests", [])

    if ok_count == 0:
        adequate = False
        confidence = 0.0
    elif fail_count == 0:
        # TC-FG-002b: confidence reflects assertion strength, not just file existence
        if _overall_classification == "STRONG_PROOF":
            adequate = True
            confidence = 0.75
        elif _overall_classification == "PARTIAL_PROOF":
            adequate = True
            confidence = 0.55
        else:
            adequate = True
            confidence = 0.7  # legacy: non-test evidence or no AST info available
    else:
        adequate = ok_count > fail_count
        confidence = ok_count / len(checks) * 0.7

    result: dict = {
        "adequate": adequate,
        "confidence": confidence,
        "stub_detected": stub_detected,
        "deficiencies": deficiencies,
        "llm_used": False,
        "intermediate_verified": True,
        "source": "intermediate_content_check",
        "checks": checks,
        "summary": f"{ok_count}/{len(checks)} evidence files passed content check",
    }
    # TC-FG-002b: expose AST classification at top level for grade_declared_work.py grade-cap
    if _strong_ratio is not None:
        result["strong_ratio"] = _strong_ratio
        result["overall_classification"] = _overall_classification
        result["weak_tests"] = _weak_tests
    return result


def verify_declaration(declaration_path: Path) -> dict:
    """Run intermediate verification on all items in a declaration file."""
    try:
        import yaml as _yaml  # type: ignore[import]
        decl = _yaml.safe_load(declaration_path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"error": str(e), "items": []}

    results = []
    for item in decl.get("planned_work_items", []):
        item_id = item.get("item_id", item.get("title", ""))
        eps = item.get("evidence_paths", [])
        result = intermediate_verify_item(eps, item_id=item_id)
        results.append({"item_id": item_id, "result": result})

    total = len(results)
    adequate = sum(1 for r in results if r["result"]["adequate"])
    return {
        "declaration": str(declaration_path),
        "total_items": total,
        "adequate_items": adequate,
        "inadequate_items": total - adequate,
        "items": results,
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Intermediate evidence content verifier (TC-HARD-008)"
    )
    parser.add_argument("--declaration", type=Path,
                        help="Path to evidence-declaration.yaml")
    parser.add_argument("--paths", nargs="*",
                        help="Individual evidence paths to check")
    parser.add_argument("--item-id", default="",
                        help="Item ID label for single-item check")
    args = parser.parse_args()

    if args.declaration:
        report = verify_declaration(args.declaration)
        print(json.dumps(report, indent=2))
        return 0 if report.get("inadequate_items", 0) == 0 else 1

    if args.paths:
        result = intermediate_verify_item(args.paths, item_id=args.item_id)
        print(json.dumps(result, indent=2))
        return 0 if result["adequate"] else 1

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
