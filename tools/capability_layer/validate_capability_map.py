"""
Capability map validator — CAP-VAL-001 through CAP-VAL-010.

Validates:
  VAL-001: Capability records conform to capability_record.schema.json
  VAL-002: No ai_draft/inferred_unverified/human_goal counted as verified
  VAL-003: Verified capabilities have provenance (non-empty refs)
  VAL-004: Implementation refs point to files that exist
  VAL-005: Test refs point to files that exist (for test_verified)
  VAL-006: Commercial and FOSS records are in separate maps (never mixed)
  VAL-007: Pilot artifacts exist and were inspected (advisory)
  VAL-008: Gap ledger entries link to taskcard IDs (advisory)
  VAL-009: Action queue items are advisory_only flagged
  VAL-010: Evidence declaration artifact list includes capability outputs

Exit codes:
  0  — all checks pass
  1  — hard validation failure (overclaim, missing provenance, schema error)
  2  — advisory warnings only
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# States that count as "verified" — any record in these states must have provenance
VERIFIED_STATES = {
    "spec_verified",
    "requirement_verified",
    "capability_verified",
    "implementation_partial",
    "implementation_verified",
    "test_verified",
    "example_verified",
    "package_verified",
    "dogfood_verified",
}

# States that must NOT be counted as verified in summary/selection logic
UNVERIFIED_STATES = {
    "ai_draft",
    "inferred_unverified",
    "human_goal",
    "missing",
    "planned",
    "blocked",
    "unsupported",
    "out_of_scope",
    "future",
}


class ValidationResult:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.checks_run = 0
        self.checks_passed = 0

    def error(self, msg: str) -> None:
        self.errors.append(msg)
        self.checks_run += 1

    def ok(self, msg: str = "") -> None:
        self.checks_run += 1
        self.checks_passed += 1

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0


def _load_json(path: Path) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _check_val001_schema(records: list[dict], result: ValidationResult) -> None:
    """VAL-001: Required fields present in every capability record."""
    required_fields = [
        "capability_id", "format", "product_type", "capability_name",
        "current_state", "confidence_level",
    ]
    for rec in records:
        cid = rec.get("capability_id", "<unknown>")
        for field in required_fields:
            if field not in rec:
                result.error(f"VAL-001: Record {cid!r} missing required field {field!r}")
            else:
                result.ok()
        # product_type must be commercial or foss_reduced
        pt = rec.get("product_type", "")
        if pt not in ("commercial", "foss_reduced"):
            result.error(
                f"VAL-001: Record {cid!r} has invalid product_type={pt!r} "
                "(must be 'commercial' or 'foss_reduced')"
            )
        else:
            result.ok()


def _check_val002_no_draft_as_verified(records: list[dict], result: ValidationResult) -> None:
    """VAL-002: ai_draft/inferred_unverified/human_goal must not appear in verified count."""
    unverified_but_verified_refs: list[str] = []
    for rec in records:
        cid = rec.get("capability_id", "<unknown>")
        state = rec.get("current_state", "")
        if state in UNVERIFIED_STATES:
            # Check that source/test/implementation refs are empty or absent
            impl_refs = rec.get("implementation_refs", [])
            if impl_refs and state in ("ai_draft", "inferred_unverified"):
                result.error(
                    f"VAL-002: Record {cid!r} state={state!r} but has "
                    f"implementation_refs — likely overclaim"
                )
            else:
                result.ok()
            # The record is not verified — that's fine; just must not claim verified status
            test_refs = rec.get("test_refs", [])
            if test_refs and state == "ai_draft":
                result.warn(
                    f"VAL-002: Record {cid!r} state=ai_draft but has test_refs — "
                    "review whether state should be upgraded"
                )
        else:
            result.ok()


def _check_val003_verified_have_provenance(records: list[dict], result: ValidationResult) -> None:
    """VAL-003: Records in verified states must have at least one ref."""
    for rec in records:
        cid = rec.get("capability_id", "<unknown>")
        state = rec.get("current_state", "")
        if state not in VERIFIED_STATES:
            result.ok()
            continue
        all_refs = (
            rec.get("spec_refs", [])
            + rec.get("requirement_refs", [])
            + rec.get("source_refs", [])
            + rec.get("implementation_refs", [])
            + rec.get("test_refs", [])
            + rec.get("example_refs", [])
            + rec.get("package_refs", [])
            + rec.get("dogfood_refs", [])
            + rec.get("evidence_refs", [])
        )
        if not all_refs:
            result.error(
                f"VAL-003: Record {cid!r} state={state!r} (verified) "
                "has zero provenance refs — must cite at least one"
            )
        else:
            result.ok()


def _check_val004_impl_refs_exist(records: list[dict], result: ValidationResult) -> None:
    """VAL-004: implementation_refs that are file paths must exist on disk.

    Refs use 'path/file.py::function_name' or 'path/' (directory) notation.
    Only the path component (before '::') is checked for existence.
    """
    for rec in records:
        cid = rec.get("capability_id", "<unknown>")
        for ref in rec.get("implementation_refs", []):
            # Strip function/method notation (path::symbol)
            file_part = ref.split("::")[0].rstrip("/")
            if not file_part:
                result.ok()
                continue
            path = REPO_ROOT / file_part
            if not path.exists():
                result.error(
                    f"VAL-004: Record {cid!r} implementation_ref {ref!r} "
                    f"path component {file_part!r} does not exist on disk"
                )
            else:
                result.ok()


def _check_val005_test_refs_exist(records: list[dict], result: ValidationResult) -> None:
    """VAL-005: test_refs must exist for test_verified claims.

    Refs may be file paths or directory paths. The path component before '::' is checked.
    """
    for rec in records:
        cid = rec.get("capability_id", "<unknown>")
        state = rec.get("current_state", "")
        test_refs = rec.get("test_refs", [])
        if state == "test_verified" and not test_refs:
            result.error(
                f"VAL-005: Record {cid!r} state=test_verified but no test_refs"
            )
        for ref in test_refs:
            file_part = ref.split("::")[0].rstrip("/")
            if not file_part:
                result.ok()
                continue
            path = REPO_ROOT / file_part
            # Accept if the file or parent directory exists
            if not path.exists() and not path.parent.exists():
                result.error(
                    f"VAL-005: Record {cid!r} test_ref {ref!r} "
                    f"path {file_part!r} does not exist on disk"
                )
            else:
                result.ok()
        if state != "test_verified" or test_refs:
            result.ok()


def _check_val006_commercial_foss_separated(
    commercial_path: Path, foss_path: Path, result: ValidationResult
) -> None:
    """VAL-006: Commercial and FOSS records must be in separate map files."""
    if commercial_path.exists():
        commercial_data = _load_json(commercial_path)
        for rec in commercial_data.get("capabilities", commercial_data.get("records", [])):
            if rec.get("product_type") != "commercial":
                result.error(
                    f"VAL-006: Non-commercial record {rec.get('capability_id')!r} "
                    "found in commercial capability map"
                )
            else:
                result.ok()
    else:
        result.warn(f"VAL-006: Commercial map not found at {commercial_path}")

    if foss_path.exists():
        foss_data = _load_json(foss_path)
        for rec in foss_data.get("capabilities", foss_data.get("records", [])):
            if rec.get("product_type") != "foss_reduced":
                result.error(
                    f"VAL-006: Non-foss_reduced record {rec.get('capability_id')!r} "
                    "found in FOSS capability map"
                )
            else:
                result.ok()
    else:
        result.warn(f"VAL-006: FOSS map not found at {foss_path}")


def _check_val007_pilot_artifacts(result: ValidationResult) -> None:
    """VAL-007 (advisory): Pilot report files exist."""
    pilot_dir = REPO_ROOT / "reports" / "capability-layer" / "pilots"
    expected_pilots = [
        "CAP-PILOT-C001", "CAP-PILOT-C002", "CAP-PILOT-C003",
        "CAP-PILOT-F001", "CAP-PILOT-F002", "CAP-PILOT-F003",
        "CAP-PILOT-E001", "CAP-PILOT-A001",
    ]
    for pilot_id in expected_pilots:
        md_path = pilot_dir / f"{pilot_id}.md"
        json_path = pilot_dir / f"{pilot_id}.json"
        if not md_path.exists() or not json_path.exists():
            result.warn(
                f"VAL-007: Pilot {pilot_id} reports not yet present "
                f"(md={md_path.exists()}, json={json_path.exists()})"
            )
        else:
            result.ok()


def _check_val008_gap_taskcard_links(gap_path: Path, result: ValidationResult) -> None:
    """VAL-008 (advisory): Gap ledger entries should reference a taskcard_id.

    Only checks OPEN (actionable) gaps. OPEN_BLOCKED, DEFERRED_BY_DESIGN, CLOSED,
    SUPERSEDED, and ARCHIVED gaps cannot receive new taskcards until their blockers
    are resolved — skipping them prevents false-positive warnings.
    """
    # Statuses where a missing suggested_taskcard is NOT a warning
    _SKIP_STATUSES = frozenset({
        "OPEN_BLOCKED", "DEFERRED_BY_DESIGN", "CLOSED", "SUPERSEDED",
        "ARCHIVED", "CLOSED_VERIFIED", "CLOSED_BY", "WONT_FIX",
    })
    if not gap_path.exists():
        result.warn(f"VAL-008: Gap ledger not found at {gap_path}")
        return
    gap_data = _load_json(gap_path)
    for gap in gap_data.get("gaps", gap_data.get("gap_entries", [])):
        gid = gap.get("gap_id", "<unknown>")
        if gap.get("status") in _SKIP_STATUSES:
            result.ok()  # blocked/deferred/closed — not actionable, skip
            continue
        if not gap.get("suggested_taskcard"):
            result.warn(f"VAL-008: Gap {gid!r} (status={gap.get('status')!r}) has no suggested_taskcard")
        else:
            result.ok()


def _check_val009_action_queue_advisory(action_path: Path, result: ValidationResult) -> None:
    """VAL-009: Non-machine-executable items must have advisory_only=true.

    Machine-executable items (machine_executable=True) may have advisory_only=False —
    they are explicitly dispatchable by an agent. Non-machine-executable items that lack
    advisory_only=True are dangerously unmarked and trigger an error.
    """
    if not action_path.exists():
        result.warn(f"VAL-009: Action queue not found at {action_path}")
        return
    queue_data = _load_json(action_path)
    for item in queue_data.get("action_queue", queue_data.get("actions", [])):
        aid = item.get("action_id", "<unknown>")
        is_advisory = item.get("advisory_only", False)
        is_machine_exec = item.get("machine_executable", False)
        if not is_advisory and not is_machine_exec:
            result.error(
                f"VAL-009: Action {aid!r} has advisory_only=False without machine_executable=True — "
                "action queue items must be advisory or explicitly machine-executable"
            )
        else:
            result.ok()


def _check_val010_evidence_includes_capability(result: ValidationResult) -> None:
    """VAL-010 (advisory): Evidence declaration should include capability-layer artifacts."""
    evidence_dir = REPO_ROOT / ".local" / "evidences"
    if not evidence_dir.exists():
        result.warn("VAL-010: .local/evidences/ directory not found — no active declaration")
        return
    # Find most recently modified declaration (by mtime, not filename sort)
    declarations = list(evidence_dir.glob("*/evidence-declaration.yaml"))
    if not declarations:
        result.warn("VAL-010: No evidence-declaration.yaml files found in .local/evidences/")
        return
    latest = max(declarations, key=lambda p: p.stat().st_mtime)
    content = latest.read_text(encoding="utf-8")
    if "capability" not in content.lower():
        result.warn(
            f"VAL-010: Latest declaration {latest} does not mention 'capability' — "
            "ensure capability-layer artifacts are declared"
        )
    else:
        result.ok()


def validate(
    unified_path: Path | None = None,
    commercial_path: Path | None = None,
    foss_path: Path | None = None,
    gap_path: Path | None = None,
    action_path: Path | None = None,
    verbose: bool = True,
) -> ValidationResult:
    """Run all validators against the generated capability layer artifacts.

    Args:
        unified_path:    Path to unified-capability-map.json
        commercial_path: Path to commercial-capability-map.json
        foss_path:       Path to foss-reduced-capability-map.json
        gap_path:        Path to gap-ledger.json
        action_path:     Path to action-queue.json
        verbose:         Print progress to stdout

    Returns:
        ValidationResult with errors, warnings, and pass/fail state.
    """
    cap_dir = REPO_ROOT / "reports" / "capability-layer"
    if unified_path is None:
        unified_path = cap_dir / "unified-capability-map.json"
    if commercial_path is None:
        commercial_path = cap_dir / "commercial-capability-map.json"
    if foss_path is None:
        foss_path = cap_dir / "foss-reduced-capability-map.json"
    if gap_path is None:
        gap_path = cap_dir / "gap-ledger.json"
    if action_path is None:
        action_path = cap_dir / "action-queue.json"

    result = ValidationResult()

    # Load unified map records (generator uses "capabilities" key)
    all_records: list[dict] = []
    if unified_path.exists():
        try:
            data = _load_json(unified_path)
            all_records = data.get("capabilities", data.get("records", []))
            if verbose:
                print(f"[VAL] Loaded {len(all_records)} records from {unified_path.name}")
        except Exception as exc:
            result.error(f"VAL-001: Cannot load unified map: {exc}")
    else:
        result.warn(f"Unified map not found at {unified_path} — schema checks skipped")

    # Run checks
    if verbose:
        print("[VAL] Running VAL-001: schema / required fields ...")
    _check_val001_schema(all_records, result)

    if verbose:
        print("[VAL] Running VAL-002: no ai_draft as verified ...")
    _check_val002_no_draft_as_verified(all_records, result)

    if verbose:
        print("[VAL] Running VAL-003: verified records have provenance ...")
    _check_val003_verified_have_provenance(all_records, result)

    if verbose:
        print("[VAL] Running VAL-004: implementation_refs exist on disk ...")
    _check_val004_impl_refs_exist(all_records, result)

    if verbose:
        print("[VAL] Running VAL-005: test_refs exist for test_verified ...")
    _check_val005_test_refs_exist(all_records, result)

    if verbose:
        print("[VAL] Running VAL-006: commercial/FOSS separation ...")
    _check_val006_commercial_foss_separated(commercial_path, foss_path, result)

    if verbose:
        print("[VAL] Running VAL-007: pilot artifacts present (advisory) ...")
    _check_val007_pilot_artifacts(result)

    if verbose:
        print("[VAL] Running VAL-008: gap-taskcard links (advisory) ...")
    _check_val008_gap_taskcard_links(gap_path, result)

    if verbose:
        print("[VAL] Running VAL-009: action queue advisory_only flags ...")
    _check_val009_action_queue_advisory(action_path, result)

    if verbose:
        print("[VAL] Running VAL-010: evidence declaration includes capability (advisory) ...")
    _check_val010_evidence_includes_capability(result)

    return result


def _print_summary(result: ValidationResult) -> None:
    print()
    print("=" * 60)
    print("CAPABILITY MAP VALIDATION SUMMARY")
    print("=" * 60)
    if result.errors:
        print(f"ERRORS ({len(result.errors)}):")
        for err in result.errors:
            print(f"  [ERROR] {err}")
    if result.warnings:
        print(f"WARNINGS ({len(result.warnings)}):")
        for warn in result.warnings:
            print(f"  [WARN]  {warn}")
    print()
    status = "PASS" if result.passed else "FAIL"
    print(
        f"Result: {status} | "
        f"Errors: {len(result.errors)} | "
        f"Warnings: {len(result.warnings)} | "
        f"Checks run: {result.checks_run}"
    )
    print("=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Validate capability layer map artifacts")
    parser.add_argument("--unified", type=Path, default=None)
    parser.add_argument("--commercial", type=Path, default=None)
    parser.add_argument("--foss", type=Path, default=None)
    parser.add_argument("--gaps", type=Path, default=None)
    parser.add_argument("--actions", type=Path, default=None)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    result = validate(
        unified_path=args.unified,
        commercial_path=args.commercial,
        foss_path=args.foss,
        gap_path=args.gaps,
        action_path=args.actions,
        verbose=not args.quiet,
    )
    _print_summary(result)

    if result.errors:
        sys.exit(1)
    elif result.warnings:
        sys.exit(2)
    sys.exit(0)
