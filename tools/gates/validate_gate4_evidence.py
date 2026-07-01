"""Validate Gate 4 evidence completeness for all tracked formats.

Checks every format in format-registry.yaml against the Gate 4 evidence contract
defined in docs/gate4-evidence-contract.yaml.

Exit codes:
  0 — all formats have valid Gate 4 dispositions
  1 — one or more formats fail validation
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]
REGISTRY = REPO / "registry" / "format-registry.yaml"

NOT_APPLICABLE_FORMATS = {"odf-shared"}

# Evidence types that count as "passed"
EVIDENCE_WRAPPER_TYPES = {"STANDALONE_PROTOTYPE", "EVIDENCE_WRAPPER"}
BLOCKED_TYPES = {"BLOCKED_BEFORE_GATE4"}


def _check_file_exists(path_str: str | None) -> bool:
    if not path_str:
        return False
    return (REPO / path_str).exists()


def _validate_source_track_equivalent(fid: str, g4: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not g4.get("delegated_source_path"):
        errors.append(f"{fid}: SOURCE_TRACK_EQUIVALENT missing delegated_source_path")
    elif not _check_file_exists(g4["delegated_source_path"]):
        errors.append(f"{fid}: delegated_source_path '{g4['delegated_source_path']}' does not exist on disk")
    if not g4.get("tests"):
        errors.append(f"{fid}: SOURCE_TRACK_EQUIVALENT missing tests[]")
    if not g4.get("corpus"):
        errors.append(f"{fid}: SOURCE_TRACK_EQUIVALENT missing corpus[]")
    return errors


def _validate_standalone_prototype(fid: str, g4: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not g4.get("prototype_path"):
        errors.append(f"{fid}: STANDALONE_PROTOTYPE missing prototype_path")
    elif not _check_file_exists(g4["prototype_path"]):
        errors.append(f"{fid}: prototype_path '{g4['prototype_path']}' does not exist on disk")
    if not g4.get("tests"):
        errors.append(f"{fid}: STANDALONE_PROTOTYPE missing tests[]")
    else:
        for t in g4["tests"]:
            if not _check_file_exists(t):
                errors.append(f"{fid}: test '{t}' does not exist on disk")
    if not g4.get("corpus"):
        errors.append(f"{fid}: STANDALONE_PROTOTYPE missing corpus[]")
    if g4.get("delegated_source_path"):
        errors.append(f"{fid}: STANDALONE_PROTOTYPE must not have delegated_source_path (INV-G4-006)")
    return errors


def _validate_evidence_wrapper(fid: str, g4: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not g4.get("prototype_path"):
        errors.append(f"{fid}: EVIDENCE_WRAPPER missing prototype_path")
    elif not _check_file_exists(g4["prototype_path"]):
        errors.append(f"{fid}: prototype_path '{g4['prototype_path']}' does not exist on disk")
    if not g4.get("delegated_source_path"):
        errors.append(f"{fid}: EVIDENCE_WRAPPER missing delegated_source_path")
    elif not _check_file_exists(g4["delegated_source_path"]):
        errors.append(f"{fid}: delegated_source_path '{g4['delegated_source_path']}' does not exist on disk")
    if not g4.get("tests"):
        errors.append(f"{fid}: EVIDENCE_WRAPPER missing tests[]")
    if not g4.get("corpus"):
        errors.append(f"{fid}: EVIDENCE_WRAPPER missing corpus[]")
    return errors


def _validate_blocked(fid: str, g4: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not g4.get("reason"):
        errors.append(f"{fid}: BLOCKED_BEFORE_GATE4 missing reason")
    if not g4.get("blocker"):
        errors.append(f"{fid}: BLOCKED_BEFORE_GATE4 missing blocker")
    if not g4.get("next_gate"):
        errors.append(f"{fid}: BLOCKED_BEFORE_GATE4 missing next_gate")
    if g4.get("status") == "passed":
        errors.append(f"{fid}: BLOCKED_BEFORE_GATE4 must not have status=passed (INV-G4-005)")
    return errors


def validate_gate4(fid: str, fmt: dict[str, Any]) -> list[str]:
    """Validate Gate 4 block for a single format. Returns list of error strings."""
    errors: list[str] = []

    if fid in NOT_APPLICABLE_FORMATS:
        return []

    gates = fmt.get("gates", {})
    g4 = gates.get("gate_4")

    if g4 is None:
        return [f"{fid}: gate_4 block ABSENT (INV-G4-001)"]

    evidence_type = g4.get("evidence_type")
    if not evidence_type:
        errors.append(f"{fid}: gate_4 missing evidence_type (PROHIBITED-004)")
        return errors

    status = g4.get("status")

    if evidence_type == "SOURCE_TRACK_EQUIVALENT":
        errors.extend(_validate_source_track_equivalent(fid, g4))
        if status != "passed":
            errors.append(f"{fid}: SOURCE_TRACK_EQUIVALENT should have status=passed, got '{status}'")

    elif evidence_type == "STANDALONE_PROTOTYPE":
        errors.extend(_validate_standalone_prototype(fid, g4))
        if status != "passed":
            errors.append(f"{fid}: STANDALONE_PROTOTYPE should have status=passed, got '{status}'")

    elif evidence_type == "EVIDENCE_WRAPPER":
        errors.extend(_validate_evidence_wrapper(fid, g4))
        if status != "passed":
            errors.append(f"{fid}: EVIDENCE_WRAPPER should have status=passed, got '{status}'")

    elif evidence_type == "BLOCKED_BEFORE_GATE4":
        errors.extend(_validate_blocked(fid, g4))

    elif evidence_type == "NOT_APPLICABLE":
        if not g4.get("reason"):
            errors.append(f"{fid}: NOT_APPLICABLE missing reason")

    else:
        errors.append(f"{fid}: unknown evidence_type '{evidence_type}'")

    return errors


def main(argv: list[str] | None = None) -> int:
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    formats = data["formats"]

    all_errors: list[str] = []
    results: list[dict] = []

    for fmt in formats:
        fid = fmt["format_id"]
        errors = validate_gate4(fid, fmt)
        g4 = fmt.get("gates", {}).get("gate_4", {})
        et = g4.get("evidence_type", "ABSENT") if g4 else "ABSENT"
        status = g4.get("status", "?") if g4 else "ABSENT"

        result = {
            "format_id": fid,
            "evidence_type": et,
            "status": status,
            "errors": errors,
            "verdict": "PASS" if not errors else "FAIL",
        }
        results.append(result)
        all_errors.extend(errors)

    # Print results table
    print(f"{'FORMAT':<14} {'EVIDENCE_TYPE':<26} {'STATUS':<12} {'VERDICT'}")
    print("-" * 70)
    for r in results:
        verdict_marker = "PASS" if r["verdict"] == "PASS" else "FAIL"
        print(f"{r['format_id']:<14} {r['evidence_type']:<26} {r['status']:<12} {verdict_marker}")
        for err in r["errors"]:
            print(f"  ERROR: {err}")

    print()
    passed = sum(1 for r in results if r["verdict"] == "PASS")
    failed = sum(1 for r in results if r["verdict"] == "FAIL")
    print(f"Results: {passed} PASS, {failed} FAIL")

    if all_errors:
        print("\nFailed formats:")
        for err in all_errors:
            print(f"  - {err}")
        return 1

    print("\nAll Gate 4 dispositions valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
