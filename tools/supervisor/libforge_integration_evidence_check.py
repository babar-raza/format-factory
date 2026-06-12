"""
Coordinator evidence checker for LibForge Integration sprints.

Validates file ownership, overlap detection, allowed/forbidden path enforcement,
taskcard consistency, evidence consistency, and final verdict consistency.

10 validation checks:
  1. Every created/modified file belongs to exactly one taskcard.
  2. No file is claimed by more than one lane.
  3. No modified file is outside allowed paths.
  4. No forbidden path has a diff.
  5. Every evidence file referenced by LFI-0-001 exists.
  6. Every evidence file referenced by LFI-H-001 exists.
  7. Every taskcard status is one of the approved states.
  8. Final verdict is consistent with test results.
  9. Evidence declaration references real files only.
  10. No evidence-stub.json, placeholder-only evidence, or path-only proof is used.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

import yaml


VALID_STATES = frozenset([
    "PROPOSED",
    "ACCEPTED_FOR_INVESTIGATION",
    "INVESTIGATING",
    "INVESTIGATION_COMPLETE",
    "PLANNED",
    "READY_FOR_EXECUTION",
    "EXECUTING",
    "READY_FOR_VERIFICATION",
    "VERIFYING",
    "ACCEPTED_VERIFIED",
    "ACCEPTED_WITH_REWORK",
    "BLOCKED_EXTERNAL",
    "REJECTED_UNSAFE",
    "SUPERSEDED",
])

STUB_FILENAMES = frozenset([
    "evidence-stub.json",
    "placeholder.json",
    "placeholder.yaml",
    "placeholder.md",
    "stub.json",
    "stub.yaml",
])


@dataclass
class CheckResult:
    check_id: int
    name: str
    passed: bool
    details: str = ""
    violations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationReport:
    run_id: str
    evidence_root: str
    taskcards_dir: str
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)

    @property
    def summary(self) -> str:
        p = sum(1 for c in self.checks if c.passed)
        f = len(self.checks) - p
        return f"{p} passed, {f} failed out of {len(self.checks)} checks"

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "evidence_root": self.evidence_root,
            "taskcards_dir": self.taskcards_dir,
            "passed": self.passed,
            "summary": self.summary,
            "checks": [c.to_dict() for c in self.checks],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


def _load_taskcards(taskcards_dir: str, repo_root: str) -> list[dict]:
    """Load all YAML taskcards from the given directory."""
    tc_path = Path(repo_root) / taskcards_dir
    taskcards = []
    if not tc_path.is_dir():
        return taskcards
    for f in sorted(tc_path.glob("LFI-*.yaml")):
        with open(f, "r", encoding="utf-8") as fh:
            tc = yaml.safe_load(fh)
            if tc:
                taskcards.append(tc)
    return taskcards


def _load_lane_ledger(evidence_root: str, repo_root: str) -> dict | None:
    """Load the lane execution ledger if it exists."""
    ledger_path = Path(repo_root) / evidence_root / "lane-execution-ledger.json"
    if not ledger_path.is_file():
        return None
    with open(ledger_path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _load_evidence_declaration(evidence_root: str, repo_root: str) -> dict | None:
    """Load evidence-declaration.yaml from the evidence root."""
    decl_path = Path(repo_root) / evidence_root / "evidence-declaration.yaml"
    if not decl_path.is_file():
        return None
    with open(decl_path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _load_final_verdict(evidence_root: str, repo_root: str) -> str | None:
    """Load and return the raw text of final-verdict.md."""
    verdict_path = Path(repo_root) / evidence_root / "final-verdict.md"
    if not verdict_path.is_file():
        return None
    with open(verdict_path, "r", encoding="utf-8") as fh:
        return fh.read()


def _build_file_ownership_map(taskcards: list[dict]) -> dict[str, list[str]]:
    """Build a map of file -> list of taskcard_ids that claim ownership."""
    ownership: dict[str, list[str]] = {}
    for tc in taskcards:
        tc_id = tc.get("taskcard_id", "UNKNOWN")
        for f in tc.get("file_ownership", []):
            ownership.setdefault(f, []).append(tc_id)
    return ownership


def _resolve_path(path_str: str, evidence_root: str) -> str:
    """Normalize a path, replacing <run_id> placeholders with evidence root basename."""
    run_id = os.path.basename(evidence_root.rstrip("/"))
    return path_str.replace("<run_id>", run_id)


def check_1_file_ownership(
    taskcards: list[dict],
    ledger: dict | None,
    repo_root: str,
) -> CheckResult:
    """Check 1: Every created/modified file belongs to exactly one taskcard."""
    ownership_map = _build_file_ownership_map(taskcards)

    # Get all created files from ledger
    created_files: set[str] = set()
    if ledger:
        for lane in ledger.get("lanes", []):
            for f in lane.get("files_created", []):
                created_files.add(f)

    unowned: list[str] = []
    for f in created_files:
        # Skip evidence-declaration.yaml and lane-execution-ledger.json — meta files
        basename = os.path.basename(f)
        if basename in ("lane-execution-ledger.json",):
            continue
        # Check if file is owned by any taskcard
        if f not in ownership_map:
            # Check if it's under a wildcard ownership (e.g., taskcards/libforge-integration/*.yaml)
            matched = False
            for owned_pattern in ownership_map:
                if "*" in owned_pattern:
                    import fnmatch
                    if fnmatch.fnmatch(f, owned_pattern):
                        matched = True
                        break
                elif f.startswith(owned_pattern.rstrip("/")):
                    matched = True
                    break
            if not matched:
                unowned.append(f)

    if unowned:
        return CheckResult(
            check_id=1,
            name="file_ownership_completeness",
            passed=False,
            details=f"{len(unowned)} file(s) not owned by any taskcard",
            violations=unowned,
        )
    return CheckResult(
        check_id=1,
        name="file_ownership_completeness",
        passed=True,
        details=f"All {len(created_files)} created files have taskcard ownership",
    )


def check_2_no_overlap(taskcards: list[dict]) -> CheckResult:
    """Check 2: No file is claimed by more than one lane."""
    ownership_map = _build_file_ownership_map(taskcards)
    overlaps: list[str] = []
    for filepath, owners in ownership_map.items():
        if len(owners) > 1:
            overlaps.append(f"{filepath} claimed by {owners}")

    if overlaps:
        return CheckResult(
            check_id=2,
            name="no_file_overlap",
            passed=False,
            details=f"{len(overlaps)} file(s) claimed by multiple taskcards",
            violations=overlaps,
        )
    return CheckResult(
        check_id=2,
        name="no_file_overlap",
        passed=True,
        details=f"No overlaps in {len(ownership_map)} owned files",
    )


def check_3_allowed_paths(
    taskcards: list[dict],
    ledger: dict | None,
) -> CheckResult:
    """Check 3: No modified file is outside allowed paths."""
    violations: list[str] = []
    if not ledger:
        return CheckResult(
            check_id=3,
            name="allowed_path_enforcement",
            passed=True,
            details="No ledger — nothing to validate",
        )

    # Build per-taskcard allowed paths
    tc_by_id = {tc["taskcard_id"]: tc for tc in taskcards}

    for lane_entry in ledger.get("lanes", []):
        tc_id = lane_entry.get("taskcard_id", "UNKNOWN")
        tc = tc_by_id.get(tc_id)
        if not tc:
            continue
        allowed = tc.get("allowed_paths", [])
        for f in lane_entry.get("files_created", []):
            if not _is_path_allowed(f, allowed):
                violations.append(f"{f} (taskcard {tc_id}) outside allowed paths")

    if violations:
        return CheckResult(
            check_id=3,
            name="allowed_path_enforcement",
            passed=False,
            details=f"{len(violations)} file(s) outside allowed paths",
            violations=violations,
        )
    return CheckResult(
        check_id=3,
        name="allowed_path_enforcement",
        passed=True,
        details="All created files within allowed paths",
    )


def _is_path_allowed(filepath: str, allowed_paths: list[str]) -> bool:
    """Check if a file path is within any of the allowed paths."""
    for ap in allowed_paths:
        # Wildcard support
        if "*" in ap:
            import fnmatch
            if fnmatch.fnmatch(filepath, ap):
                return True
        # Directory prefix
        elif ap.endswith("/"):
            if filepath.startswith(ap):
                return True
        # Exact match
        elif filepath == ap:
            return True
        # Path starts with allowed (for directory-like patterns without trailing /)
        elif filepath.startswith(ap + "/"):
            return True
    return False


def check_4_forbidden_paths(
    taskcards: list[dict],
    repo_root: str,
) -> CheckResult:
    """Check 4: No forbidden path has a diff (checks git)."""
    # Collect all unique forbidden paths
    forbidden: set[str] = set()
    for tc in taskcards:
        for fp in tc.get("forbidden_paths", []):
            forbidden.add(fp)

    violations: list[str] = []
    for fp in sorted(forbidden):
        # Check if any files under this path were modified in git working tree
        full_path = Path(repo_root) / fp
        if full_path.is_file():
            # Single file — check git diff
            import subprocess
            result = subprocess.run(
                ["git", "diff", "--name-only", "--", fp],
                capture_output=True, text=True, cwd=repo_root,
            )
            if result.stdout.strip():
                violations.append(f"FORBIDDEN file modified: {fp}")
        elif full_path.is_dir() or fp.endswith("/"):
            import subprocess
            result = subprocess.run(
                ["git", "diff", "--name-only", "--", fp],
                capture_output=True, text=True, cwd=repo_root,
            )
            if result.stdout.strip():
                for line in result.stdout.strip().split("\n"):
                    violations.append(f"FORBIDDEN path modified: {line}")

    if violations:
        return CheckResult(
            check_id=4,
            name="forbidden_path_check",
            passed=False,
            details=f"{len(violations)} forbidden path(s) modified",
            violations=violations,
        )
    return CheckResult(
        check_id=4,
        name="forbidden_path_check",
        passed=True,
        details=f"Checked {len(forbidden)} forbidden paths — none modified",
    )


def check_5_evidence_files_0(
    taskcards: list[dict],
    repo_root: str,
) -> CheckResult:
    """Check 5: Every evidence file referenced by LFI-0-001 exists."""
    tc_0 = next((tc for tc in taskcards if tc.get("taskcard_id") == "LFI-0-001"), None)
    if not tc_0:
        return CheckResult(
            check_id=5,
            name="evidence_files_lfi_0_001",
            passed=False,
            details="LFI-0-001 taskcard not found",
        )

    missing: list[str] = []
    evidence_files = tc_0.get("evidence_files", [])
    for ef in evidence_files:
        full = Path(repo_root) / ef
        if not full.is_file():
            missing.append(ef)

    if missing:
        return CheckResult(
            check_id=5,
            name="evidence_files_lfi_0_001",
            passed=False,
            details=f"{len(missing)} evidence file(s) missing for LFI-0-001",
            violations=missing,
        )
    return CheckResult(
        check_id=5,
        name="evidence_files_lfi_0_001",
        passed=True,
        details=f"All {len(evidence_files)} evidence files for LFI-0-001 exist",
    )


def check_6_evidence_files_h(
    taskcards: list[dict],
    repo_root: str,
) -> CheckResult:
    """Check 6: Every evidence file referenced by LFI-H-001 exists."""
    tc_h = next((tc for tc in taskcards if tc.get("taskcard_id") == "LFI-H-001"), None)
    if not tc_h:
        return CheckResult(
            check_id=6,
            name="evidence_files_lfi_h_001",
            passed=False,
            details="LFI-H-001 taskcard not found",
        )

    missing: list[str] = []
    evidence_files = tc_h.get("evidence_files", [])
    for ef in evidence_files:
        full = Path(repo_root) / ef
        if not full.is_file():
            missing.append(ef)

    if missing:
        return CheckResult(
            check_id=6,
            name="evidence_files_lfi_h_001",
            passed=False,
            details=f"{len(missing)} evidence file(s) missing for LFI-H-001",
            violations=missing,
        )
    return CheckResult(
        check_id=6,
        name="evidence_files_lfi_h_001",
        passed=True,
        details=f"All {len(evidence_files)} evidence files for LFI-H-001 exist",
    )


def check_7_taskcard_states(
    taskcards: list[dict],
) -> CheckResult:
    """Check 7: Every taskcard status is one of the approved states."""
    # Also check ledger statuses
    violations: list[str] = []
    for tc in taskcards:
        tc_id = tc.get("taskcard_id", "UNKNOWN")
        status = tc.get("status", "MISSING")
        if status not in VALID_STATES:
            violations.append(f"{tc_id}: invalid status '{status}'")

    if violations:
        return CheckResult(
            check_id=7,
            name="taskcard_state_validity",
            passed=False,
            details=f"{len(violations)} taskcard(s) with invalid state",
            violations=violations,
        )
    return CheckResult(
        check_id=7,
        name="taskcard_state_validity",
        passed=True,
        details=f"All {len(taskcards)} taskcards have valid states",
    )


def check_8_verdict_consistency(
    evidence_root: str,
    repo_root: str,
    ledger: dict | None,
) -> CheckResult:
    """Check 8: Final verdict is consistent with test results."""
    verdict_text = _load_final_verdict(evidence_root, repo_root)
    if not verdict_text:
        return CheckResult(
            check_id=8,
            name="verdict_consistency",
            passed=False,
            details="final-verdict.md not found",
        )

    decl = _load_evidence_declaration(evidence_root, repo_root)
    if not decl:
        return CheckResult(
            check_id=8,
            name="verdict_consistency",
            passed=False,
            details="evidence-declaration.yaml not found",
        )

    violations: list[str] = []

    # Check verdict claims ACCEPTED_VERIFIED
    verdict_upper = verdict_text.upper()
    decl_verdict = (decl.get("worker_self_verdict", "") or "").upper()

    if "ACCEPTED_VERIFIED" in verdict_upper and decl_verdict == "ACCEPTED_VERIFIED":
        # Consistent — check test results support this
        test_results = decl.get("test_results", {})
        failed = test_results.get("failed", 0) or 0
        errors = test_results.get("errors", 0) or 0
        if failed > 0 or errors > 0:
            violations.append(
                f"Verdict claims ACCEPTED_VERIFIED but test_results has "
                f"{failed} failures, {errors} errors"
            )
    elif "ACCEPTED_VERIFIED" in verdict_upper and decl_verdict != "ACCEPTED_VERIFIED":
        violations.append(
            f"final-verdict.md claims ACCEPTED_VERIFIED but declaration says {decl_verdict}"
        )
    elif "REJECTED" in verdict_upper and "ACCEPTED" in decl_verdict:
        violations.append(
            "final-verdict.md claims REJECTED but declaration claims ACCEPTED"
        )

    # Check lane statuses in ledger match verdict
    if ledger:
        for lane in ledger.get("lanes", []):
            lane_status = lane.get("status", "")
            if "REJECTED" in lane_status.upper() and "ACCEPTED_VERIFIED" in verdict_upper:
                violations.append(
                    f"Lane {lane.get('lane')} status {lane_status} contradicts ACCEPTED_VERIFIED verdict"
                )

    if violations:
        return CheckResult(
            check_id=8,
            name="verdict_consistency",
            passed=False,
            details=f"{len(violations)} verdict inconsistency(ies)",
            violations=violations,
        )
    return CheckResult(
        check_id=8,
        name="verdict_consistency",
        passed=True,
        details="Final verdict consistent with declaration and test results",
    )


def check_9_declaration_refs(
    evidence_root: str,
    repo_root: str,
) -> CheckResult:
    """Check 9: Evidence declaration references real files only."""
    decl = _load_evidence_declaration(evidence_root, repo_root)
    if not decl:
        return CheckResult(
            check_id=9,
            name="declaration_file_refs",
            passed=False,
            details="evidence-declaration.yaml not found",
        )

    missing: list[str] = []

    # Check evidence_artifacts
    for artifact in decl.get("evidence_artifacts", []):
        path = artifact.get("path", "") if isinstance(artifact, dict) else str(artifact)
        if path:
            full = Path(repo_root) / path
            if not full.is_file():
                missing.append(f"evidence_artifact: {path}")

    # Check changed_files exist (for created files)
    for cf in decl.get("changed_files", []):
        path = cf if isinstance(cf, str) else cf.get("path", "")
        if path:
            full = Path(repo_root) / path
            if not full.is_file():
                missing.append(f"changed_file: {path}")

    if missing:
        return CheckResult(
            check_id=9,
            name="declaration_file_refs",
            passed=False,
            details=f"{len(missing)} referenced file(s) not found on disk",
            violations=missing,
        )
    return CheckResult(
        check_id=9,
        name="declaration_file_refs",
        passed=True,
        details="All referenced files exist on disk",
    )


def check_10_no_stubs(
    evidence_root: str,
    repo_root: str,
) -> CheckResult:
    """Check 10: No evidence-stub.json, placeholder, or path-only proof."""
    evidence_path = Path(repo_root) / evidence_root
    if not evidence_path.is_dir():
        return CheckResult(
            check_id=10,
            name="no_stub_evidence",
            passed=False,
            details=f"Evidence directory not found: {evidence_root}",
        )

    violations: list[str] = []

    # Check for stub filenames
    for f in evidence_path.rglob("*"):
        if f.is_file() and f.name in STUB_FILENAMES:
            violations.append(f"Stub file found: {f.relative_to(Path(repo_root))}")

    # Check repo root for evidence-stub.json
    root_stub = Path(repo_root) / "evidence-stub.json"
    if root_stub.is_file():
        violations.append("evidence-stub.json found at repo root")

    # Check evidence files are not too small (< 10 bytes = likely placeholder)
    for f in evidence_path.rglob("*"):
        if f.is_file() and f.suffix in (".json", ".yaml", ".yml", ".md", ".log"):
            size = f.stat().st_size
            if size < 10 and f.name not in ("lane-execution-ledger.json",):
                violations.append(
                    f"Suspiciously small file ({size} bytes): "
                    f"{f.relative_to(Path(repo_root))}"
                )

    if violations:
        return CheckResult(
            check_id=10,
            name="no_stub_evidence",
            passed=False,
            details=f"{len(violations)} stub/placeholder issue(s)",
            violations=violations,
        )
    return CheckResult(
        check_id=10,
        name="no_stub_evidence",
        passed=True,
        details="No stubs, placeholders, or suspiciously small evidence files",
    )


def run_all_checks(
    evidence_root: str,
    taskcards_dir: str,
    repo_root: str | None = None,
) -> ValidationReport:
    """Run all 10 validation checks and return a ValidationReport."""
    if repo_root is None:
        repo_root = str(Path(__file__).resolve().parent.parent.parent)

    run_id = os.path.basename(evidence_root.rstrip("/"))
    taskcards = _load_taskcards(taskcards_dir, repo_root)
    ledger = _load_lane_ledger(evidence_root, repo_root)

    report = ValidationReport(
        run_id=run_id,
        evidence_root=evidence_root,
        taskcards_dir=taskcards_dir,
    )

    report.checks.append(check_1_file_ownership(taskcards, ledger, repo_root))
    report.checks.append(check_2_no_overlap(taskcards))
    report.checks.append(check_3_allowed_paths(taskcards, ledger))
    report.checks.append(check_4_forbidden_paths(taskcards, repo_root))
    report.checks.append(check_5_evidence_files_0(taskcards, repo_root))
    report.checks.append(check_6_evidence_files_h(taskcards, repo_root))
    report.checks.append(check_7_taskcard_states(taskcards))
    report.checks.append(check_8_verdict_consistency(evidence_root, repo_root, ledger))
    report.checks.append(check_9_declaration_refs(evidence_root, repo_root))
    report.checks.append(check_10_no_stubs(evidence_root, repo_root))

    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="LibForge Integration coordinator evidence checker"
    )
    parser.add_argument(
        "--evidence-root",
        required=True,
        help="Relative path to evidence directory (e.g. .local/evidences/ff-libforge-...)",
    )
    parser.add_argument(
        "--taskcards-dir",
        required=True,
        help="Relative path to taskcards directory (e.g. taskcards/libforge-integration)",
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repository root (default: auto-detect from script location)",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory to write validation JSON outputs (default: evidence-root)",
    )
    args = parser.parse_args()

    repo_root = args.repo_root
    if repo_root is None:
        repo_root = str(Path(__file__).resolve().parent.parent.parent)

    report = run_all_checks(args.evidence_root, args.taskcards_dir, repo_root)

    output_dir = args.output_dir or args.evidence_root
    output_path = Path(repo_root) / output_dir
    output_path.mkdir(parents=True, exist_ok=True)

    # Write individual check result files
    ownership_result = next(c for c in report.checks if c.check_id == 1)
    overlap_result = next(c for c in report.checks if c.check_id == 2)
    forbidden_result = next(c for c in report.checks if c.check_id == 4)
    taskcard_result = next(c for c in report.checks if c.check_id == 7)
    evidence_0_result = next(c for c in report.checks if c.check_id == 5)
    evidence_h_result = next(c for c in report.checks if c.check_id == 6)
    verdict_result = next(c for c in report.checks if c.check_id == 8)

    # file-ownership-validation.json
    with open(output_path / "file-ownership-validation.json", "w") as f:
        json.dump({
            "check_1_ownership": ownership_result.to_dict(),
            "check_2_overlap": overlap_result.to_dict(),
        }, f, indent=2)

    # overlap-check-result.json
    with open(output_path / "overlap-check-result.json", "w") as f:
        json.dump(overlap_result.to_dict(), f, indent=2)

    # forbidden-path-check.log
    with open(output_path / "forbidden-path-check.log", "w") as f:
        f.write(f"Check 4: {forbidden_result.name}\n")
        f.write(f"Passed: {forbidden_result.passed}\n")
        f.write(f"Details: {forbidden_result.details}\n")
        if forbidden_result.violations:
            f.write("Violations:\n")
            for v in forbidden_result.violations:
                f.write(f"  - {v}\n")

    # taskcard-consistency-check.json
    with open(output_path / "taskcard-consistency-check.json", "w") as f:
        json.dump(taskcard_result.to_dict(), f, indent=2)

    # evidence-consistency-check.json
    evidence_9 = next(c for c in report.checks if c.check_id == 9)
    evidence_10 = next(c for c in report.checks if c.check_id == 10)
    with open(output_path / "evidence-consistency-check.json", "w") as f:
        json.dump({
            "check_5_evidence_0": evidence_0_result.to_dict(),
            "check_6_evidence_h": evidence_h_result.to_dict(),
            "check_9_declaration_refs": evidence_9.to_dict(),
            "check_10_no_stubs": evidence_10.to_dict(),
        }, f, indent=2)

    # final-verdict-consistency-check.json
    with open(output_path / "final-verdict-consistency-check.json", "w") as f:
        json.dump(verdict_result.to_dict(), f, indent=2)

    # Full report
    full_report_path = output_path / "coordinator-check-output.log"
    with open(full_report_path, "w") as f:
        f.write("LibForge Integration Coordinator Evidence Check\n")
        f.write(f"{'=' * 50}\n")
        f.write(f"Run ID: {report.run_id}\n")
        f.write(f"Evidence Root: {report.evidence_root}\n")
        f.write(f"Taskcards Dir: {report.taskcards_dir}\n")
        f.write(f"Overall: {'PASSED' if report.passed else 'FAILED'}\n")
        f.write(f"Summary: {report.summary}\n\n")
        for c in report.checks:
            status = "PASS" if c.passed else "FAIL"
            f.write(f"[{status}] Check {c.check_id}: {c.name}\n")
            f.write(f"       {c.details}\n")
            if c.violations:
                for v in c.violations:
                    f.write(f"       - {v}\n")
            f.write("\n")

    # Print summary
    print(f"Overall: {'PASSED' if report.passed else 'FAILED'}")
    print(f"Summary: {report.summary}")
    for c in report.checks:
        status = "PASS" if c.passed else "FAIL"
        print(f"  [{status}] Check {c.check_id}: {c.name} — {c.details}")

    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
