"""Validate a skill invocation transcript for completeness and correctness.

A transcript must include:
- invocation_id: unique ID for this invocation
- skill_id: must match a registered skill
- mode: "dry-run" or "live"
- inputs: dict of handoff field values
- allowed_files: list of paths the skill was allowed to touch
- actual_files_changed: list of paths actually changed
- tests_run: list of test identifiers or commands
- ledger_entry_id: ID of the ledger entry (null for non-src-editing)
- result: "PASS" or "FAIL"
- timestamp: ISO 8601 timestamp
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

REQUIRED_FIELDS = {
    "invocation_id",
    "skill_id",
    "mode",
    "inputs",
    "allowed_files",
    "actual_files_changed",
    "tests_run",
    "result",
}

VALID_MODES = {"dry-run", "live", "anti-bypass-demo"}
VALID_RESULTS = {"PASS", "FAIL"}

# Tracks that require a ledger entry
SRC_EDITING_TRACKS = {
    "commercial_dotnet",
    "foss_python",
    "cross_product_export",
    "cross_product",
}


def _load_yaml(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        return yaml.safe_load(text)
    raise ImportError("PyYAML is required")


def _load_registry_skill_ids(registry_path: Path) -> dict[str, dict]:
    """Load registry and return {skill_id: skill_entry}."""
    if not registry_path.exists():
        return {}
    data = _load_yaml(registry_path)
    skills = data.get("skills", [])
    return {s["skill_id"]: s for s in skills if "skill_id" in s}


def validate_transcript(
    transcript: dict,
    registry_path: Path = DEFAULT_REGISTRY,
) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    # Required fields
    missing = REQUIRED_FIELDS - set(transcript.keys())
    if missing:
        errors.append(f"missing required fields: {sorted(missing)}")

    # Mode
    mode = transcript.get("mode", "")
    if mode and mode not in VALID_MODES:
        errors.append(f"invalid mode: {mode} (must be one of {sorted(VALID_MODES)})")

    # Result
    result = transcript.get("result", "")
    if result and result not in VALID_RESULTS:
        errors.append(f"invalid result: {result} (must be one of {sorted(VALID_RESULTS)})")

    # Skill ID must be registered
    skill_id = transcript.get("skill_id", "")
    registry = _load_registry_skill_ids(registry_path)
    if skill_id and skill_id not in registry:
        errors.append(f"skill_id '{skill_id}' not found in registry")
    elif skill_id and registry:
        skill_entry = registry[skill_id]
        track = skill_entry.get("product_track", "")

        # Check ledger requirement for src-editing tracks in live mode
        if track in SRC_EDITING_TRACKS and mode == "live":
            ledger_id = transcript.get("ledger_entry_id")
            if not ledger_id:
                errors.append(
                    f"live invocation of src-editing skill '{skill_id}' "
                    f"(track: {track}) requires ledger_entry_id"
                )

        # Check inputs contain required handoff fields
        inputs = transcript.get("inputs", {})
        if isinstance(inputs, dict):
            required_fields = skill_entry.get("required_handoff_fields", [])
            missing_inputs = set(required_fields) - set(inputs.keys())
            if missing_inputs:
                warnings.append(
                    f"inputs missing required handoff fields: {sorted(missing_inputs)}"
                )

    # Actual files must be subset of allowed files
    allowed = set(transcript.get("allowed_files", []))
    actual = set(transcript.get("actual_files_changed", []))
    if actual and allowed:
        outside = actual - allowed
        if outside:
            errors.append(f"files changed outside allowed paths: {sorted(outside)}")

    # Invocation ID format
    inv_id = transcript.get("invocation_id", "")
    if inv_id and len(inv_id) < 5:
        warnings.append("invocation_id is very short (< 5 chars)")

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "skill_id": skill_id,
        "mode": mode,
        "result": result,
    }


def validate_directory(
    directory: Path,
    registry_path: Path = DEFAULT_REGISTRY,
) -> dict:
    """Validate all transcript JSON files in a directory."""
    results = {}
    for f in sorted(directory.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception as exc:
            data = {"error": str(exc)}
        results[f.name] = validate_transcript(data, registry_path)
    pass_count = sum(1 for r in results.values() if r["valid"])
    fail_count = len(results) - pass_count
    return {
        "total": len(results),
        "pass": pass_count,
        "fail": fail_count,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("transcript", type=Path, nargs="?", help="Path to transcript JSON file")
    parser.add_argument("--dir", type=Path, help="Validate all transcripts in a directory")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.dir:
        summary = validate_directory(args.dir, args.registry)
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print(f"TRANSCRIPT_DIR_VALIDATION: {summary['pass']}/{summary['total']} PASS, {summary['fail']} FAIL")
            for name, result in summary["results"].items():
                status = "PASS" if result["valid"] else "FAIL"
                print(f"  {name}: {status}")
                for e in result["errors"]:
                    print(f"    ERROR: {e}")
                for w in result["warnings"]:
                    print(f"    WARNING: {w}")
        return 0 if summary["fail"] == 0 else 1

    if not args.transcript:
        parser.error("either transcript path or --dir is required")

    try:
        data = json.loads(args.transcript.read_text(encoding="utf-8"))
    except Exception as exc:
        data = {"error": str(exc)}

    result = validate_transcript(data, args.registry)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"TRANSCRIPT_VALIDATION: {'PASS' if result['valid'] else 'FAIL'}")
        for e in result["errors"]:
            print(f"  ERROR: {e}")
        for w in result["warnings"]:
            print(f"  WARNING: {w}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
