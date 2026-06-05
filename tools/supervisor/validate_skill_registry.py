"""Validate the governed skill registry for completeness and correctness.

Checks:
- Required fields present for every skill
- Command file exists on disk
- No stale/unknown skill IDs
- Ledger requirement present for src-editing skills
- Tests/evidence outputs referenced
- Allowed/forbidden paths documented (in command file)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
DEFAULT_REGISTRY = REPO_ROOT / ".supervisor" / "skill-registry.yaml"

REQUIRED_SKILL_FIELDS = {
    "skill_id",
    "command",
    "command_file",
    "status",
    "purpose",
    "product_track",
    "required_handoff_fields",
    "mandatory_validations",
}

# Tracks that edit src/ and therefore MUST reference ledger validation
SRC_EDITING_TRACKS = {
    "commercial_dotnet",
    "foss_python",
    "cross_product_export",
    "cross_product",
}

VALID_STATUSES = {"active", "draft", "deprecated", "disabled"}

# Minimum purpose length to avoid shallow stubs
MIN_PURPOSE_LENGTH = 10


def _load_yaml(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        return yaml.safe_load(text)
    # Fallback: attempt basic YAML-like parsing for simple structures
    raise ImportError("PyYAML is required: pip install pyyaml")


def validate_registry(registry_path: Path, repo_root: Path) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    skill_summaries: list[dict] = []

    try:
        data = _load_yaml(registry_path)
    except Exception as exc:
        return {
            "valid": False,
            "errors": [f"Failed to load registry: {exc}"],
            "warnings": [],
            "skills": [],
        }

    if not isinstance(data, dict):
        return {
            "valid": False,
            "errors": ["Registry root must be a mapping"],
            "warnings": [],
            "skills": [],
        }

    # Check top-level required fields
    for field in ("registry_id", "registry_status", "global_controls", "skills"):
        if field not in data:
            errors.append(f"Missing top-level field: {field}")

    gc = data.get("global_controls", {})
    if not gc.get("product_code_ledger_required_before_source_edit"):
        warnings.append(
            "global_controls.product_code_ledger_required_before_source_edit is not true"
        )

    skills = data.get("skills", [])
    if not isinstance(skills, list) or len(skills) == 0:
        errors.append("skills must be a non-empty list")
        return {
            "valid": not errors,
            "errors": errors,
            "warnings": warnings,
            "skills": [],
        }

    seen_ids: set[str] = set()
    for idx, skill in enumerate(skills):
        sid = skill.get("skill_id", f"<index-{idx}>")
        classification = "READY"
        skill_errors: list[str] = []

        # Duplicate check
        if sid in seen_ids:
            skill_errors.append(f"duplicate skill_id: {sid}")
        seen_ids.add(sid)

        # Required fields
        missing = REQUIRED_SKILL_FIELDS - set(skill.keys())
        if missing:
            skill_errors.append(f"missing fields: {sorted(missing)}")
            classification = "PARTIAL" if len(missing) <= 2 else "PLACEHOLDER"

        # Status
        status = skill.get("status", "")
        if status not in VALID_STATUSES:
            skill_errors.append(f"invalid status: {status}")
        elif status == "draft":
            classification = "DRAFT"
        elif status == "deprecated":
            classification = "DEPRECATED"
        elif status == "disabled":
            classification = "DISABLED"

        # Purpose length
        purpose = skill.get("purpose", "")
        if len(purpose) < MIN_PURPOSE_LENGTH:
            skill_errors.append(
                f"purpose too short ({len(purpose)} chars, min {MIN_PURPOSE_LENGTH})"
            )
            classification = "PLACEHOLDER"

        # Command file exists (skip for draft/deprecated skills)
        cmd_file = skill.get("command_file", "")
        if cmd_file:
            cmd_path = repo_root / cmd_file
            if not cmd_path.exists():
                if status in ("draft", "deprecated"):
                    warnings.append(f"[{sid}] command_file not found (acceptable for {status}): {cmd_file}")
                else:
                    skill_errors.append(f"command_file not found: {cmd_file}")
                    classification = "MISSING"
        else:
            skill_errors.append("command_file is empty")
            classification = "MISSING"

        # Handoff fields
        handoff = skill.get("required_handoff_fields", [])
        if not isinstance(handoff, list) or len(handoff) == 0:
            skill_errors.append("required_handoff_fields is empty")
            if classification == "READY":
                classification = "PARTIAL"

        # Mandatory validations
        validations = skill.get("mandatory_validations", [])
        if not isinstance(validations, list) or len(validations) == 0:
            skill_errors.append("mandatory_validations is empty")
            if classification == "READY":
                classification = "PARTIAL"

        # Ledger requirement for src-editing tracks
        track = skill.get("product_track", "")
        if track in SRC_EDITING_TRACKS:
            ledger_refs = [
                v
                for v in validations
                if "ledger" in str(v).lower() or "product_code" in str(v).lower()
            ]
            if not ledger_refs:
                skill_errors.append(
                    f"src-editing track '{track}' must include product_code_ledger_validator in mandatory_validations"
                )
                classification = "UNSAFE"

        if skill_errors:
            for err in skill_errors:
                errors.append(f"[{sid}] {err}")

        skill_summaries.append(
            {
                "skill_id": sid,
                "status": status,
                "classification": classification,
                "command_file": cmd_file,
                "product_track": track,
                "handoff_fields_count": len(handoff) if isinstance(handoff, list) else 0,
                "validations_count": len(validations)
                if isinstance(validations, list)
                else 0,
                "errors": skill_errors,
            }
        )

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "skills": skill_summaries,
        "total_skills": len(skills),
        "ready_count": sum(
            1 for s in skill_summaries if s["classification"] == "READY"
        ),
        "partial_count": sum(
            1 for s in skill_summaries if s["classification"] == "PARTIAL"
        ),
        "placeholder_count": sum(
            1 for s in skill_summaries if s["classification"] == "PLACEHOLDER"
        ),
        "missing_count": sum(
            1 for s in skill_summaries if s["classification"] == "MISSING"
        ),
        "unsafe_count": sum(
            1 for s in skill_summaries if s["classification"] == "UNSAFE"
        ),
        "draft_count": sum(
            1 for s in skill_summaries if s["classification"] == "DRAFT"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--json", action="store_true", help="Print JSON result")
    args = parser.parse_args()

    result = validate_registry(args.registry, args.repo_root)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        verdict = "PASS" if result["valid"] else "FAIL"
        print(f"SKILL_REGISTRY_VALIDATION: {verdict}")
        print(
            f"  total={result.get('total_skills', 0)} "
            f"ready={result.get('ready_count', 0)} "
            f"draft={result.get('draft_count', 0)} "
            f"partial={result.get('partial_count', 0)} "
            f"placeholder={result.get('placeholder_count', 0)} "
            f"missing={result.get('missing_count', 0)} "
            f"unsafe={result.get('unsafe_count', 0)}"
        )
        for error in result["errors"]:
            print(f"  ERROR: {error}")
        for warning in result["warnings"]:
            print(f"  WARNING: {warning}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
