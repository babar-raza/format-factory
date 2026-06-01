"""
evidence_declaration.py — Evidence Declaration Validator
Validates an evidence-declaration.yaml against the schema and checks
that declared evidence paths exist in the repo/worktree.

Exit codes:
  0 — valid
  1 — schema validation failed
  2 — declared paths missing
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
SCHEMA_DIR = REPO_ROOT / ".supervisor" / "schemas"

REQUIRED_FIELDS = [
    "run_id", "sprint_id", "evidence_root",
    "start_time", "end_time",
    "git_head_start", "git_head_end", "git_status_final",
    "declared_scope",
    "planned_work_items", "completed_work_items", "incomplete_work_items",
    "changed_files", "tests_run", "test_results",
    "evidence_artifacts", "reports_created",
    "worker_self_verdict", "worker_self_grade",
    "next_recommended_work",
]

VALID_WORK_ITEM_STATUSES = {"completed", "partial", "not_started", "blocked_external_gate"}
VALID_SELF_GRADES = {"PASS", "PARTIAL", "FAIL", "BLOCKED"}


def load_declaration(path: Path) -> dict:
    """Load a YAML declaration file."""
    text = path.read_text(encoding="utf-8")
    return yaml.safe_load(text) or {}


def _validate_jsonschema(decl: dict) -> list[str]:
    """Validate against JSON schema if jsonschema library is available."""
    schema_path = SCHEMA_DIR / "evidence-declaration.schema.json"
    if not schema_path.exists():
        return []
    try:
        import jsonschema
        import json as _json
        schema = _json.loads(schema_path.read_text(encoding="utf-8"))
        jsonschema.validate(decl, schema)
        return []
    except ImportError:
        return []  # graceful degradation
    except Exception as e:
        return [f"JSON schema validation: {e}"]


def validate_schema(decl: dict) -> list[str]:
    """Validate declaration against required fields and JSON schema. Returns list of errors."""
    errors = _validate_jsonschema(decl)
    for field in REQUIRED_FIELDS:
        if field not in decl:
            errors.append(f"Missing required field: {field}")

    if "planned_work_items" in decl:
        for i, item in enumerate(decl["planned_work_items"]):
            if not isinstance(item, dict):
                errors.append(f"planned_work_items[{i}] is not an object")
                continue
            for req in ("item_id", "title", "status"):
                if req not in item:
                    errors.append(f"planned_work_items[{i}] missing '{req}'")
            status = item.get("status", "")
            if status and status not in VALID_WORK_ITEM_STATUSES:
                errors.append(f"planned_work_items[{i}] invalid status: {status}")

    grade = decl.get("worker_self_grade", "")
    if grade and grade not in VALID_SELF_GRADES:
        errors.append(f"Invalid worker_self_grade: {grade}")

    return errors


def validate_paths(decl: dict, repo_root: Path) -> list[str]:
    """Check that evidence_root and declared artifact paths exist."""
    errors = []
    evidence_root = decl.get("evidence_root", "")
    if not evidence_root:
        errors.append("evidence_root is empty")
        return errors

    root_path = repo_root / evidence_root
    if not root_path.is_dir():
        errors.append(f"evidence_root does not exist: {root_path}")
        return errors

    for i, artifact in enumerate(decl.get("evidence_artifacts", [])):
        apath = artifact.get("path", "")
        if not apath:
            continue
        full = repo_root / apath
        if not full.exists():
            errors.append(f"evidence_artifacts[{i}].path does not exist: {apath}")

    return errors


def validate_declaration(path: Path, repo_root: Path, check_paths: bool = True) -> dict:
    """Full validation. Returns result dict."""
    result = {
        "declaration_path": str(path),
        "valid": False,
        "schema_errors": [],
        "path_errors": [],
        "timestamp": datetime.now().isoformat(),
    }

    try:
        decl = load_declaration(path)
    except Exception as e:
        result["schema_errors"] = [f"Failed to load YAML: {e}"]
        return result

    result["schema_errors"] = validate_schema(decl)

    if check_paths and not result["schema_errors"]:
        result["path_errors"] = validate_paths(decl, repo_root)

    result["valid"] = not result["schema_errors"] and not result["path_errors"]
    result["declaration"] = decl
    return result


def create_sample_declaration(out_path: Path) -> None:
    """Create a sample evidence-declaration.yaml template."""
    sample = {
        "run_id": "sample-run-001",
        "sprint_id": "FORMAT-FACTORY-SAMPLE-SPRINT-001",
        "evidence_root": ".local/evidences/sample-run-001/",
        "start_time": datetime.now().isoformat(),
        "end_time": datetime.now().isoformat(),
        "git_head_start": "abc1234",
        "git_head_end": "def5678",
        "git_status_final": "",
        "declared_scope": "Sample sprint scope description",
        "planned_work_items": [
            {
                "item_id": "ITEM-001",
                "title": "Sample work item",
                "status": "completed",
                "evidence_paths": ["path/to/evidence.txt"],
                "tests_supporting": ["tests/test_sample.py::test_one"],
                "acceptance_criteria": "Evidence file exists and tests pass",
            }
        ],
        "completed_work_items": ["ITEM-001"],
        "incomplete_work_items": [],
        "changed_files": ["src/sample.py"],
        "tests_run": 1,
        "test_results": {"passed": 1, "failed": 0, "skipped": 0, "errors": 0},
        "evidence_artifacts": [
            {"path": "path/to/evidence.txt", "type": "report", "description": "Sample evidence"}
        ],
        "reports_created": ["reports/sample-report.md"],
        "worker_self_verdict": "All work completed successfully",
        "worker_self_grade": "PASS",
        "next_recommended_work": ["Continue to next sprint"],
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(yaml.dump(sample, default_flow_style=False, sort_keys=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate evidence declaration")
    parser.add_argument("--declaration", type=Path, help="Path to evidence-declaration.yaml")
    parser.add_argument("--create-sample", type=Path, help="Create sample declaration at path")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--no-path-check", action="store_true", help="Skip path existence checks")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    if args.create_sample:
        create_sample_declaration(args.create_sample)
        print(f"Sample declaration created: {args.create_sample}")
        return 0

    if not args.declaration:
        parser.error("--declaration is required (or use --create-sample)")

    result = validate_declaration(args.declaration, args.repo_root, check_paths=not args.no_path_check)

    if args.json:
        out = {k: v for k, v in result.items() if k != "declaration"}
        print(json.dumps(out, indent=2))
    else:
        if result["valid"]:
            print(f"DECLARATION_VALID: {args.declaration}")
        else:
            print(f"DECLARATION_INVALID: {args.declaration}")
            for e in result["schema_errors"]:
                print(f"  SCHEMA_ERROR: {e}")
            for e in result["path_errors"]:
                print(f"  PATH_ERROR: {e}")

    if result["schema_errors"]:
        return 1
    if result["path_errors"]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
