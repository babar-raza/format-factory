"""
inspect_declared_evidence.py — Declared Evidence Inspector
Inspects a worker-declared evidence directory by walking declared paths,
extracting facts, and assessing per-item evidence presence.

Exit codes:
  0 — inspection complete
  1 — declaration invalid
  9 — unexpected error
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent

# R107: Lazy import for transcript validation enrichment
_validate_transcript_fn = None


def _get_validate_transcript():
    """Lazily import validate_transcript to avoid circular imports."""
    global _validate_transcript_fn
    if _validate_transcript_fn is None:
        try:
            prev_path = list(sys.path)
            if str(SCRIPT_DIR) not in sys.path:
                sys.path.insert(0, str(SCRIPT_DIR))
            from validate_skill_transcript import validate_transcript
            _validate_transcript_fn = validate_transcript
        except ImportError:
            _validate_transcript_fn = False  # Mark as unavailable
    return _validate_transcript_fn if _validate_transcript_fn is not False else None


def _is_transcript_json(data: dict) -> bool:
    """Check if a parsed JSON dict looks like a skill invocation transcript."""
    transcript_fields = {"invocation_id", "skill_id", "mode", "result"}
    return transcript_fields.issubset(set(data.keys()))


def check_transcript_in_evidence(evidence_paths: list, repo_root: Path) -> dict | None:
    """R107: Detect and validate transcript JSON files in evidence_paths.

    Returns a dict with validation results if any transcript found, else None.
    """
    validator = _get_validate_transcript()
    if validator is None:
        return None

    transcripts_found = []
    transcripts_valid = []
    transcripts_invalid = []

    for p in evidence_paths:
        if not p.endswith(".json"):
            continue
        full = repo_root / p
        if not full.exists():
            continue
        try:
            data = json.loads(full.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict) or not _is_transcript_json(data):
            continue

        # This is a transcript — validate it
        transcripts_found.append(p)
        result = validator(data)
        if result["valid"]:
            transcripts_valid.append({
                "path": p,
                "skill_id": result.get("skill_id", ""),
                "mode": result.get("mode", ""),
                "result": result.get("result", ""),
            })
        else:
            transcripts_invalid.append({
                "path": p,
                "errors": result.get("errors", []),
                "warnings": result.get("warnings", []),
            })

    if not transcripts_found:
        return None

    return {
        "transcripts_found": len(transcripts_found),
        "transcripts_valid": len(transcripts_valid),
        "transcripts_invalid": len(transcripts_invalid),
        "valid_transcripts": transcripts_valid,
        "invalid_transcripts": transcripts_invalid,
        "all_valid": len(transcripts_invalid) == 0,
    }


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def check_test_file_content(test_path: Path) -> dict:
    """Check if a test file contains actual test methods (D92-03 deep grading)."""
    if not test_path.exists():
        return {"has_content": False, "reason": "file not found"}

    try:
        text = test_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return {"has_content": False, "reason": "read error"}

    # Check for common test patterns
    is_cs = test_path.suffix.lower() == ".cs"
    is_py = test_path.suffix.lower() == ".py"

    if is_cs:
        # C#: [Fact], [Theory], void Test*, Task Test*
        has_tests = bool(
            "[Fact]" in text or "[Theory]" in text or
            ("void " in text and ("Test" in text or "test" in text)) or
            ("Task " in text and "Test" in text)
        )
        method_count = text.count("[Fact]") + text.count("[Theory]")
    elif is_py:
        # Python: def test_
        import re
        methods = re.findall(r"^\s*def test_\w+", text, re.MULTILINE)
        has_tests = len(methods) > 0
        method_count = len(methods)
    else:
        has_tests = len(text.strip()) > 0
        method_count = 0

    if not has_tests:
        return {"has_content": False, "reason": "no test methods found", "method_count": method_count}

    return {"has_content": True, "method_count": method_count}


def inspect_item(item: dict, repo_root: Path) -> dict:
    """Inspect a single planned work item for evidence presence."""
    item_id = item.get("item_id", "unknown")
    status = item.get("status", "not_started")
    evidence_paths = item.get("evidence_paths", [])
    # R103: Accept both schema field name and common alias
    tests = item.get("tests_supporting", []) or item.get("test_references", [])
    acceptance_criteria = item.get("acceptance_criteria", "")

    found_paths = []
    missing_paths = []
    for p in evidence_paths:
        full = repo_root / p
        if full.exists():
            found_paths.append(p)
        else:
            missing_paths.append(p)

    has_evidence = len(found_paths) > 0
    has_tests = len(tests) > 0

    # D92-03 deep grading: check test file content
    # R98 fix: Distinguish actual file paths from summary strings.
    # A test entry is a file path if it contains a path separator or ends with
    # a known test file extension (.py, .cs). Otherwise it is a summary string
    # and should NOT be treated as a missing/empty test file.
    tests_with_content = []
    tests_empty_or_stub = []
    test_summaries = []
    for t in tests:
        is_file_path = (
            "/" in t or "\\" in t or
            t.endswith(".py") or t.endswith(".cs") or
            t.startswith("tests/") or t.startswith("tests\\")
        )
        if not is_file_path:
            # This is a summary string like "8 new tests, all passed"
            test_summaries.append(t)
            continue
        # R105: Strip pytest node ID suffix (::test_function) to get the file path
        file_part = t.split("::")[0] if "::" in t else t
        full_t = repo_root / file_part
        check = check_test_file_content(full_t)
        if check["has_content"]:
            tests_with_content.append(t)
        else:
            tests_empty_or_stub.append(t)

    # Check acceptance criteria pattern in evidence files
    criteria_verified = False
    criteria_pattern = ""
    if acceptance_criteria and found_paths:
        # Extract a key phrase from acceptance criteria for pattern check
        import re
        # Take up to first 80 chars, find key technical term
        crit_text = str(acceptance_criteria)[:120]
        # Look for quoted strings or capitalized terms as patterns
        quoted = re.findall(r'"([^"]{3,40})"', crit_text)
        if quoted:
            criteria_pattern = quoted[0]
        elif "PASS" in crit_text:
            criteria_pattern = "PASS"

        if criteria_pattern:
            for fp in found_paths[:3]:  # Check first 3 evidence files
                full_fp = repo_root / fp
                if full_fp.exists():
                    try:
                        content = full_fp.read_text(encoding="utf-8", errors="replace")
                        if criteria_pattern.lower() in content.lower():
                            criteria_verified = True
                            break
                    except Exception:
                        pass

    # R98 fix: If only summary strings were provided in tests_supporting,
    # check evidence_paths for test files and verify their content instead.
    if not tests_with_content and not tests_empty_or_stub and test_summaries:
        for fp in found_paths:
            fp_path = repo_root / fp
            is_test = (
                fp.startswith("tests/") or fp.startswith("tests\\") or
                "test" in fp.lower()
            ) and (fp.endswith(".py") or fp.endswith(".cs"))
            if is_test:
                check = check_test_file_content(fp_path)
                if check["has_content"]:
                    tests_with_content.append(fp)
                else:
                    tests_empty_or_stub.append(fp)

    # R107: Transcript enrichment — detect and validate transcript JSON in evidence
    transcript_validation = check_transcript_in_evidence(found_paths, repo_root)

    return {
        "item_id": item_id,
        "declared_status": status,
        "evidence_paths_declared": evidence_paths,
        "evidence_paths_found": found_paths,
        "evidence_paths_missing": missing_paths,
        "has_evidence": has_evidence,
        "has_tests": has_tests,
        "tests_declared": tests,
        # D92-03: deep content checks
        "tests_with_content": tests_with_content,
        "tests_empty_or_stub": tests_empty_or_stub,
        "test_summaries": test_summaries,
        "acceptance_criteria_verified": criteria_verified,
        "acceptance_criteria_pattern": criteria_pattern,
        # R107: Transcript validation enrichment
        "transcript_validation": transcript_validation,
    }


def inspect_declaration(decl: dict, repo_root: Path) -> dict:
    """Full inspection of a declaration."""
    evidence_root = decl.get("evidence_root", "")
    root_path = repo_root / evidence_root if evidence_root else None

    inspection = {
        "run_id": decl.get("run_id", "unknown"),
        "sprint_id": decl.get("sprint_id", "unknown"),
        "evidence_root": evidence_root,
        "evidence_root_exists": root_path.is_dir() if root_path else False,
        "timestamp": datetime.now().isoformat(),
        "item_inspections": [],
        "artifact_inspections": [],
        "test_results": decl.get("test_results", {}),
        "tests_run": decl.get("tests_run", 0),
        "zip_declared": bool(decl.get("zip_export_path")),
        "zip_path": decl.get("zip_export_path"),
    }

    # Inspect each work item
    for item in decl.get("planned_work_items", []):
        inspection["item_inspections"].append(inspect_item(item, repo_root))

    # Inspect declared artifacts
    for artifact in decl.get("evidence_artifacts", []):
        apath = artifact.get("path", "")
        full = repo_root / apath if apath else None
        inspection["artifact_inspections"].append({
            "path": apath,
            "exists": full.exists() if full else False,
            "type": artifact.get("type", "unknown"),
            "related_work_items": artifact.get("related_work_items", []),
        })

    return inspection


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect declared evidence directory")
    parser.add_argument("--declaration", type=Path, required=True, help="Path to evidence-declaration.yaml")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--output", type=Path, help="Write inspection JSON to file")
    args = parser.parse_args()

    if not args.declaration.exists():
        print(f"ERROR: Declaration not found: {args.declaration}", file=sys.stderr)
        return 1

    decl = load_yaml(args.declaration)
    inspection = inspect_declaration(decl, args.repo_root)

    output_json = json.dumps(inspection, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output_json, encoding="utf-8")
        print(f"INSPECTION_COMPLETE: {args.output}")
    else:
        print(output_json)

    return 0


if __name__ == "__main__":
    sys.exit(main())
