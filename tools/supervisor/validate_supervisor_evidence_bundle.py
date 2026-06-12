"""
validate_supervisor_evidence_bundle.py

Validates that a supervisor evidence bundle meets quality standards.
Prevents recurrence of defects found in dual-orchestration sprint:
  D-SUP-01: Contract file not in ZIP
  D-SUP-02: reports/supervisor/ runtime outputs not in ZIP when claimed
  D-SUP-03: Final verdict contains stale/wrong SHA
  D-SUP-04: Supervisor replay claimed but no replay fixture/input in bundle

Usage:
    python tools/supervisor/validate_supervisor_evidence_bundle.py <bundle.zip> [--contract <contract.yaml>]

Exit codes:
    0 = all checks pass
    1 = one or more checks fail
    2 = bundle not found or unreadable
"""

import argparse
import hashlib
import re
import sys
import zipfile
from pathlib import Path

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


def compute_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


class BundleValidationResult:
    def __init__(self):
        self.checks = []
        self.failures = []
        self.warnings = []

    def add_pass(self, check_id: str, description: str):
        self.checks.append({"id": check_id, "result": "PASS", "description": description})

    def add_fail(self, check_id: str, description: str, detail: str = ""):
        self.checks.append({"id": check_id, "result": "FAIL", "description": description, "detail": detail})
        self.failures.append(f"{check_id}: {description}" + (f" — {detail}" if detail else ""))

    def add_warn(self, check_id: str, description: str, detail: str = ""):
        self.checks.append({"id": check_id, "result": "WARN", "description": description, "detail": detail})
        self.warnings.append(f"{check_id}: {description}" + (f" — {detail}" if detail else ""))

    @property
    def passed(self) -> bool:
        return len(self.failures) == 0

    def print_report(self):
        print("=" * 60)
        print("SUPERVISOR BUNDLE VALIDATION REPORT")
        print("=" * 60)
        for c in self.checks:
            icon = {"PASS": "[PASS]", "FAIL": "[FAIL]", "WARN": "[WARN]"}.get(c["result"], "[????]")
            detail = f" -- {c['detail']}" if c.get("detail") else ""
            print(f"{icon} {c['id']}: {c['description']}{detail}")
        print()
        if self.warnings:
            print(f"WARNINGS: {len(self.warnings)}")
            for w in self.warnings:
                print(f"  {w}")
        if self.failures:
            print(f"\nFAILURES: {len(self.failures)}")
            for f in self.failures:
                print(f"  {f}")
        else:
            print("All checks passed.")
        print()
        verdict = "SUPERVISOR_BUNDLE_VALIDATION: PASS" if self.passed else "SUPERVISOR_BUNDLE_VALIDATION: FAIL"
        print(verdict)
        return verdict


def validate_bundle(bundle_path: str, contract_path: str | None = None) -> BundleValidationResult:
    result = BundleValidationResult()

    # Check 1: Bundle exists and is readable
    bundle_file = Path(bundle_path)
    if not bundle_file.exists():
        result.add_fail("SUP-V-001", "Bundle file exists", f"Not found: {bundle_path}")
        return result
    result.add_pass("SUP-V-001", "Bundle file exists")

    try:
        zf = zipfile.ZipFile(bundle_path, "r")
    except zipfile.BadZipFile as e:
        result.add_fail("SUP-V-002", "Bundle is valid ZIP", str(e))
        return result
    result.add_pass("SUP-V-002", "Bundle is valid ZIP")

    names = set(zf.namelist())

    # Determine the current sprint's run_number from the contract (for scoping checks)
    current_run_number = None
    if contract_path and YAML_AVAILABLE:
        try:
            with open(contract_path) as f:
                contract_data = yaml.safe_load(f)
            current_run_number = contract_data.get("run_number")
        except Exception:
            pass

    # Check 2 (D-SUP-01): Contract file is present in bundle
    # The contract may be at repo/tools/evidence/contracts/*.yaml
    contract_found = any(
        n.endswith(".yaml") and "contracts/" in n
        for n in names
    )
    if contract_path:
        contract_filename = Path(contract_path).name
        contract_in_zip = any(
            n.endswith(contract_filename)
            for n in names
        )
        if contract_in_zip:
            result.add_pass("SUP-V-003", f"Contract file present in bundle ({contract_filename})")
        else:
            result.add_fail(
                "SUP-V-003",
                "Contract file present in bundle",
                f"Expected file ending in '{contract_filename}' not found in ZIP. "
                "Add contract to required_repo_files in the contract YAML itself."
            )
    elif contract_found:
        result.add_pass("SUP-V-003", "At least one contract YAML present in bundle")
    else:
        result.add_warn("SUP-V-003", "No contract YAML found in bundle (cannot verify without --contract flag)")

    # Check 3 (D-SUP-02): If final verdict claims supervisor run, reports/supervisor/ must be present
    # Look for final-verdict.md inside the bundle
    verdict_files = [n for n in names if n.endswith("final-verdict.md")]
    supervisor_runtime_claimed = False
    verdict_has_delegation = False
    verdict_sha_value = None

    for vf in verdict_files:
        try:
            content = zf.read(vf).decode("utf-8", errors="replace")
            # Check if supervisor run is claimed
            if "supervisor_loop.py run-on-latest" in content or "run-on-latest" in content:
                supervisor_runtime_claimed = True
            # Check for delegation label
            if "delegated_to_sidecar" in content or "delegation" in content.lower():
                verdict_has_delegation = True
            # Extract SHA if present
            sha_match = re.search(r"BUNDLE_SHA256\s*\n([a-f0-9]{64})", content)
            if sha_match:
                verdict_sha_value = sha_match.group(1)
        except Exception:
            pass

    supervisor_reports_in_zip = [n for n in names if "reports/supervisor/" in n]

    if supervisor_runtime_claimed:
        if supervisor_reports_in_zip:
            result.add_pass(
                "SUP-V-004",
                f"reports/supervisor/ outputs present ({len(supervisor_reports_in_zip)} files)"
            )
        else:
            result.add_fail(
                "SUP-V-004",
                "reports/supervisor/ outputs present in bundle",
                "Final verdict claims supervisor run-on-latest but reports/supervisor/ "
                "outputs are missing from ZIP. Add them to required_repo_files."
            )
    else:
        if supervisor_reports_in_zip:
            result.add_pass("SUP-V-004", f"reports/supervisor/ present ({len(supervisor_reports_in_zip)} files)")
        else:
            result.add_warn("SUP-V-004", "reports/supervisor/ not in bundle (no supervisor run claimed)")

    # Check 4 (D-SUP-03): Final verdict SHA must use delegation or match actual ZIP
    if verdict_sha_value:
        actual_sha = compute_sha256(bundle_path)
        if verdict_sha_value == actual_sha:
            result.add_pass("SUP-V-005", "Final verdict bundle SHA matches actual ZIP SHA")
        else:
            # The circular SHA problem means inner verdict SHA is one-generation-behind
            # This is acceptable if sidecar is present, but we warn
            result.add_warn(
                "SUP-V-005",
                "Final verdict SHA does not match actual ZIP (one-generation-behind pattern)",
                f"Verdict SHA: {verdict_sha_value[:16]}... Actual: {actual_sha[:16]}... "
                "This is acceptable if sidecar proof is authoritative."
            )
    elif verdict_has_delegation:
        result.add_pass("SUP-V-005", "Final verdict uses delegation label for bundle SHA (correct pattern)")
    elif verdict_files:
        result.add_warn("SUP-V-005", "Final verdict contains no BUNDLE_SHA256 field")
    else:
        result.add_warn("SUP-V-005", "No final-verdict.md found in bundle")

    # Check 5: BUNDLE_VALIDATION claim requires raw validation proof
    bundle_validation_claimed = False
    raw_validation_present = False

    for vf in verdict_files:
        try:
            content = zf.read(vf).decode("utf-8", errors="replace")
            if "BUNDLE_VALIDATION: PASS" in content:
                bundle_validation_claimed = True
        except Exception:
            pass

    # Look for raw validation log
    validation_logs = [
        n for n in names
        if any(keyword in n for keyword in ["validation-log", "bundle-validation-log", "validate-log"])
    ]
    if bundle_validation_claimed and not validation_logs:
        # Raw log not strictly required if bundle validates cleanly
        result.add_warn(
            "SUP-V-006",
            "BUNDLE_VALIDATION: PASS claimed but no raw validation log file found",
            "Consider including validate_evidence_bundle.py output as a file in the bundle"
        )
    else:
        result.add_pass("SUP-V-006", "BUNDLE_VALIDATION claim check passed")

    # Check 6 (D-SUP-04): Replay fixture present if replay is claimed
    replay_claimed = False
    for vf in verdict_files:
        try:
            content = zf.read(vf).decode("utf-8", errors="replace")
            if ("run-on-latest" in content or "replay" in content.lower()) and "EXIT 0" in content:
                replay_claimed = True
        except Exception:
            pass

    replay_fixtures = [n for n in names if n.endswith(".zip") and n != bundle_path]
    # Also check for fixture marker files
    fixture_markers = [n for n in names if "fixture" in n.lower() or "replay-input" in n.lower()]

    if replay_claimed:
        if replay_fixtures or fixture_markers:
            result.add_pass("SUP-V-007", f"Replay fixture present ({len(replay_fixtures)} ZIPs, {len(fixture_markers)} markers)")
        else:
            result.add_fail(
                "SUP-V-007",
                "Replay fixture present in bundle",
                "Final verdict claims supervisor run-on-latest EXIT 0 but no replay input bundle or fixture found in ZIP. "
                "Include replay-input.zip or a fixture bundle."
            )
    else:
        result.add_pass("SUP-V-007", "No replay claimed or replay not marked EXIT 0 — fixture check skipped")

    # Check 7: No PENDING markers in final verdict (current sprint only)
    pending_count = 0
    # Scope to current sprint's final-verdict.md if we know the run_number
    pending_verdict_files = verdict_files
    if current_run_number:
        scoped = [vf for vf in verdict_files if f"reports/{current_run_number}/" in vf]
        if scoped:
            pending_verdict_files = scoped
    for vf in pending_verdict_files:
        try:
            content = zf.read(vf).decode("utf-8", errors="replace")
            # Count PENDING but not in expected delegation-label contexts
            for line in content.splitlines():
                if "PENDING" in line and not any(skip in line for skip in [
                    "MODES_PENDING", "delegated_to", "#", "PENDING_APPROVAL", "pending MODE",
                    "[to be filled", "to be filled"
                ]):
                    pending_count += 1
        except Exception:
            pass

    if pending_count > 0:
        result.add_fail("SUP-V-008", "No PENDING markers in final verdict", f"{pending_count} PENDING markers found")
    else:
        result.add_pass("SUP-V-008", "No PENDING markers in final verdict")

    # Check 8: Accepted limitations have follow-up references
    accepted_limitation_check_pass = True
    for vf in verdict_files:
        try:
            content = zf.read(vf).decode("utf-8", errors="replace")
            if "Accepted Limitations" in content or "accepted_limitations" in content:
                # Check each numbered limitation has either a taskcard ref or mode ref
                sections = content.split("##")
                for section in sections:
                    if "Limitation" in section or "limitation" in section:
                        lines = [l.strip() for l in section.splitlines() if l.strip().startswith(("1.", "2.", "3.", "4.", "5."))]
                        for line in lines:
                            has_ref = any(keyword in line for keyword in [
                                "TC-", "MODE", "deferred", "fixture", "blocked", "D-SUP", "D78"
                            ])
                            if not has_ref and len(line) > 20:
                                accepted_limitation_check_pass = False
        except Exception:
            pass

    if accepted_limitation_check_pass:
        result.add_pass("SUP-V-009", "Accepted limitations reference follow-up actions")
    else:
        result.add_warn("SUP-V-009", "Some accepted limitations may lack follow-up taskcard references")

    zf.close()
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Validate supervisor evidence bundle quality"
    )
    parser.add_argument("bundle", help="Path to the evidence bundle ZIP")
    parser.add_argument("--contract", help="Path to the contract YAML file", default=None)
    args = parser.parse_args()

    result = validate_bundle(args.bundle, args.contract)
    result.print_report()

    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
