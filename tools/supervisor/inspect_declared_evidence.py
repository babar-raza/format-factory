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
    tests = item.get("tests_supporting", [])
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
    tests_with_content = []
    tests_empty_or_stub = []
    for t in tests:
        full_t = repo_root / t
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
        "acceptance_criteria_verified": criteria_verified,
        "acceptance_criteria_pattern": criteria_pattern,
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
