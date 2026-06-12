"""
validate_tri_lane_contract.py
Tri-Lane Integration Contract Validator

Sprint: FORMAT-FACTORY-TRI-LANE-INTEGRATION-FABRIC-001
Updated: FORMAT-FACTORY-TRI-LANE-INTEGRATION-REFRESH-AND-MAINSTREAM-READINESS-GATE-001

Validates a tri-lane contract JSON document against required structure and authority rules.

Rejection conditions (hard fail):
- missing Supervisor routing block
- missing Skills handoff block
- missing Acceleration advisory block
- Acceleration output used as authority (not ai_draft)
- direct poc-targets mutation request detected
- missing allowed/forbidden files in mainstream execution block
- missing expected tests
- missing dogfood/output expectation
- missing transcript expectation
- missing proposed capability delta
- Netpbm omitted from families
- SVG declared as Netpbm replacement
- fewer than 3 families in mainstream execution
- invalid Python pytest command referencing .cs test file (added in refresh sprint)
- FODT shell packet when full finalization packet exists (added in refresh sprint)
- Netpbm shell packet when full finalization packet exists (added in refresh sprint)

Usage:
    python tools/supervisor/validate_tri_lane_contract.py <contract.json>

Exit codes:
    0  All checks pass (TRI_LANE_CONTRACT_VALID)
    1  Hard rejection (TRI_LANE_CONTRACT_REJECTED)
    2  Degraded pass with limitations (TRI_LANE_CONTRACT_VALID_WITH_LIMITATIONS)
"""

import json
import sys
import os
from typing import Any, Dict, List


REQUIRED_TOP_LEVEL_BLOCKS = [
    "supervisor_routing",
    "skills_handoff",
    "acceleration_advisory",
    "mainstream_execution",
    "evidence_expectations",
    "capability_delta",
    "validation",
    "authority_boundary",
]

REQUIRED_SUPERVISOR_FIELDS = ["source", "routing_decision", "families", "authority_state"]
REQUIRED_SKILLS_FIELDS = ["source", "handoff_type", "families", "authority_state"]
REQUIRED_ACCELERATION_FIELDS = ["source", "families", "authority_state", "non_authoritative"]
REQUIRED_MAINSTREAM_FIELDS = ["families", "allowed_files", "forbidden_files", "stop_conditions", "rollback_requirements"]
REQUIRED_MAINSTREAM_FAMILY_FIELDS = [
    "family", "capability", "allowed_files", "forbidden_files",
    "expected_tests", "expected_dogfood_output", "expected_transcript", "validation_commands"
]
REQUIRED_CAPABILITY_DELTA_FIELDS = ["proposed_only", "deltas"]
REQUIRED_VALIDATION_FIELDS = ["validator_tool", "pass_criteria", "rejection_conditions"]
REQUIRED_AUTHORITY_BOUNDARY_FIELDS = ["supervisor", "skills", "acceleration", "mainstream", "format_factory_gates"]

NETPBM_FAMILY_NAMES = {"Netpbm", "netpbm", "NETPBM"}
SVG_FAMILY_NAMES = {"SVG", "svg", "Svg"}


class ValidationResult:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.limitations: List[str] = []
        self.checks_passed: List[str] = []

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)

    def add_limitation(self, msg: str) -> None:
        self.limitations.append(msg)

    def add_pass(self, msg: str) -> None:
        self.checks_passed.append(msg)

    @property
    def is_rejected(self) -> bool:
        return len(self.errors) > 0

    @property
    def is_degraded(self) -> bool:
        return len(self.limitations) > 0 and not self.is_rejected

    def verdict(self) -> str:
        if self.is_rejected:
            return "TRI_LANE_CONTRACT_REJECTED"
        if self.is_degraded:
            return "TRI_LANE_CONTRACT_VALID_WITH_LIMITATIONS"
        return "TRI_LANE_CONTRACT_VALID"

    def exit_code(self) -> int:
        if self.is_rejected:
            return 1
        if self.is_degraded:
            return 2
        return 0


def check_required_blocks(contract: Dict[str, Any], result: ValidationResult) -> None:
    """Check all required top-level blocks are present."""
    for block in REQUIRED_TOP_LEVEL_BLOCKS:
        if block not in contract:
            result.add_error(f"MISSING_REQUIRED_BLOCK: '{block}' not found in contract")
        else:
            result.add_pass(f"BLOCK_PRESENT: {block}")


def check_supervisor_routing(contract: Dict[str, Any], result: ValidationResult) -> None:
    """Check supervisor routing block structure and authority state."""
    sup = contract.get("supervisor_routing")
    if not sup:
        return  # Already caught by check_required_blocks

    for field in REQUIRED_SUPERVISOR_FIELDS:
        if field not in sup:
            result.add_error(f"SUPERVISOR_MISSING_FIELD: '{field}' not in supervisor_routing")

    # Authority state must be routing_authority
    if sup.get("authority_state") != "routing_authority":
        result.add_error(
            f"SUPERVISOR_WRONG_AUTHORITY: authority_state='{sup.get('authority_state')}' must be 'routing_authority'"
        )
    else:
        result.add_pass("SUPERVISOR_AUTHORITY_STATE_CORRECT: routing_authority")

    # Must have at least one family
    families = sup.get("families", [])
    if not families:
        result.add_error("SUPERVISOR_NO_FAMILIES: families list is empty")
    else:
        result.add_pass(f"SUPERVISOR_FAMILIES_PRESENT: {len(families)} families")


def check_skills_handoff(contract: Dict[str, Any], result: ValidationResult) -> None:
    """Check skills handoff block structure and authority state."""
    skills = contract.get("skills_handoff")
    if not skills:
        return

    for field in REQUIRED_SKILLS_FIELDS:
        if field not in skills:
            result.add_error(f"SKILLS_MISSING_FIELD: '{field}' not in skills_handoff")

    # Authority state must be governed_execution_authority
    if skills.get("authority_state") != "governed_execution_authority":
        result.add_error(
            f"SKILLS_WRONG_AUTHORITY: authority_state='{skills.get('authority_state')}' must be 'governed_execution_authority'"
        )
    else:
        result.add_pass("SKILLS_AUTHORITY_STATE_CORRECT: governed_execution_authority")

    families = skills.get("families", [])
    if not families:
        result.add_error("SKILLS_NO_FAMILIES: skills_handoff families list is empty")
    else:
        result.add_pass(f"SKILLS_FAMILIES_PRESENT: {len(families)} families")


def check_acceleration_advisory(contract: Dict[str, Any], result: ValidationResult) -> None:
    """Check acceleration advisory block — must be ai_draft and non_authoritative."""
    accel = contract.get("acceleration_advisory")
    if not accel:
        result.add_limitation("ACCELERATION_MISSING: acceleration_advisory block absent — degraded pass")
        return

    for field in REQUIRED_ACCELERATION_FIELDS:
        if field not in accel:
            result.add_error(f"ACCELERATION_MISSING_FIELD: '{field}' not in acceleration_advisory")

    # authority_state must be ai_draft
    auth_state = accel.get("authority_state")
    if auth_state != "ai_draft":
        result.add_error(
            f"ACCELERATION_AUTHORITY_MISUSE: authority_state='{auth_state}' must be 'ai_draft' "
            f"— acceleration output cannot be used as authority"
        )
    else:
        result.add_pass("ACCELERATION_AUTHORITY_STATE_CORRECT: ai_draft")

    # non_authoritative must be True
    if accel.get("non_authoritative") is not True:
        result.add_error("ACCELERATION_NON_AUTHORITATIVE_MISSING: non_authoritative must be true")
    else:
        result.add_pass("ACCELERATION_NON_AUTHORITATIVE: true")

    # Check per-family authority state
    for fam_entry in accel.get("families", []):
        fam_auth = fam_entry.get("authority_state")
        if fam_auth != "ai_draft":
            result.add_error(
                f"ACCELERATION_FAMILY_AUTHORITY_MISUSE: family '{fam_entry.get('family')}' "
                f"authority_state='{fam_auth}' must be 'ai_draft'"
            )


def check_poc_targets_mutation(contract: Dict[str, Any], result: ValidationResult) -> None:
    """Detect any direct poc-targets mutation requests in the contract."""
    contract_str = json.dumps(contract)

    # These patterns indicate a direct mutation request rather than a proposed delta
    mutation_patterns = [
        '"mutate": true',
        '"direct_write": true',
        '"update_poc_targets": true',
        '"write_poc_targets": true',
    ]
    for pattern in mutation_patterns:
        if pattern in contract_str:
            result.add_error(
                f"POC_TARGETS_MUTATION_DETECTED: Contract contains direct mutation request: '{pattern}'. "
                f"Only proposed deltas are allowed."
            )

    # capability_delta proposed_only must be true
    cap_delta = contract.get("capability_delta", {})
    if cap_delta and cap_delta.get("proposed_only") is not True:
        result.add_error(
            "CAPABILITY_DELTA_NOT_PROPOSED_ONLY: capability_delta.proposed_only must be true. "
            "Direct poc-targets.yaml write is prohibited."
        )
    elif cap_delta:
        result.add_pass("CAPABILITY_DELTA_PROPOSED_ONLY: true")


def check_mainstream_execution(contract: Dict[str, Any], result: ValidationResult) -> None:
    """Check mainstream execution block — families, files, tests, outputs."""
    ms = contract.get("mainstream_execution")
    if not ms:
        return

    for field in REQUIRED_MAINSTREAM_FIELDS:
        if field not in ms:
            result.add_error(f"MAINSTREAM_MISSING_FIELD: '{field}' not in mainstream_execution")

    families = ms.get("families", [])

    # Must have at least 3 families
    if len(families) < 3:
        result.add_error(
            f"MAINSTREAM_TOO_FEW_FAMILIES: {len(families)} families found, minimum 3 required"
        )
    else:
        result.add_pass(f"MAINSTREAM_FAMILY_COUNT_OK: {len(families)} >= 3")

    for fam in families:
        fname = fam.get("family", "<unknown>")
        for field in REQUIRED_MAINSTREAM_FAMILY_FIELDS:
            if field not in fam or not fam[field]:
                result.add_error(
                    f"MAINSTREAM_FAMILY_MISSING_FIELD: family='{fname}' missing or empty field '{field}'"
                )

    # Check stop_conditions and rollback_requirements present
    if not ms.get("stop_conditions"):
        result.add_error("MAINSTREAM_MISSING_STOP_CONDITIONS: stop_conditions is empty or missing")
    else:
        result.add_pass("MAINSTREAM_STOP_CONDITIONS_PRESENT")

    if not ms.get("rollback_requirements"):
        result.add_error("MAINSTREAM_MISSING_ROLLBACK: rollback_requirements is empty or missing")
    else:
        result.add_pass("MAINSTREAM_ROLLBACK_REQUIREMENTS_PRESENT")


def check_netpbm_present(contract: Dict[str, Any], result: ValidationResult) -> None:
    """Netpbm must be present in mainstream execution families."""
    ms = contract.get("mainstream_execution", {})
    families = ms.get("families", [])
    family_names = {f.get("family", "") for f in families}

    has_netpbm = bool(NETPBM_FAMILY_NAMES & family_names)
    if not has_netpbm:
        result.add_error(
            f"NETPBM_MISSING: Netpbm not found in mainstream execution families. "
            f"Found: {sorted(family_names)}. Netpbm is required."
        )
    else:
        result.add_pass("NETPBM_PRESENT: Netpbm found in mainstream execution")

    # Also check supervisor routing has Netpbm
    sup = contract.get("supervisor_routing", {})
    sup_families = {f.get("family", "") for f in sup.get("families", [])}
    if not (NETPBM_FAMILY_NAMES & sup_families):
        result.add_error("NETPBM_MISSING_IN_SUPERVISOR: Netpbm not routed by Supervisor")
    else:
        result.add_pass("NETPBM_IN_SUPERVISOR_ROUTING: present")


def check_svg_not_replacing_netpbm(contract: Dict[str, Any], result: ValidationResult) -> None:
    """SVG cannot replace Netpbm — format class mismatch (vector vs raster)."""
    ms = contract.get("mainstream_execution", {})
    families = ms.get("families", [])
    family_names = {f.get("family", "") for f in families}

    # SVG should not appear as a substitute for Netpbm
    if SVG_FAMILY_NAMES & family_names:
        # SVG present but also Netpbm absent = replacement attempt
        has_netpbm = bool(NETPBM_FAMILY_NAMES & family_names)
        if not has_netpbm:
            result.add_error(
                "SVG_REPLACING_NETPBM: SVG found in families but Netpbm absent. "
                "SVG cannot replace Netpbm — format class mismatch (vector vs raster)."
            )
        else:
            result.add_warning("SVG_PRESENT_WITH_NETPBM: SVG is present alongside Netpbm — verify intent")
    else:
        result.add_pass("SVG_NOT_REPLACING_NETPBM: no SVG in mainstream execution families")

    # Check supervisor routing SVG rejection
    sup = contract.get("supervisor_routing", {})
    for fam in sup.get("families", []):
        if fam.get("family", "") in NETPBM_FAMILY_NAMES:
            if fam.get("svg_replacement_rejected") is not True:
                result.add_warning(
                    "SUPERVISOR_SVG_REJECTION_NOT_EXPLICIT: Netpbm entry does not explicitly set svg_replacement_rejected=true"
                )
            else:
                result.add_pass("SUPERVISOR_SVG_REJECTION_CONFIRMED: svg_replacement_rejected=true on Netpbm")


def check_evidence_expectations(contract: Dict[str, Any], result: ValidationResult) -> None:
    """Check evidence expectations block."""
    ev = contract.get("evidence_expectations", {})
    if not ev:
        result.add_error("EVIDENCE_EXPECTATIONS_MISSING: evidence_expectations block absent")
        return

    for field in ["minimum_passing_tests", "minimum_governed_transcripts", "minimum_source_diffs", "required_for_clean_pass"]:
        if field not in ev:
            result.add_error(f"EVIDENCE_EXPECTATIONS_MISSING_FIELD: '{field}' absent")

    result.add_pass("EVIDENCE_EXPECTATIONS_PRESENT")


def check_capability_delta(contract: Dict[str, Any], result: ValidationResult) -> None:
    """Check capability delta block — must be proposed only."""
    cd = contract.get("capability_delta", {})
    if not cd:
        result.add_error("CAPABILITY_DELTA_MISSING: capability_delta block absent")
        return

    for field in REQUIRED_CAPABILITY_DELTA_FIELDS:
        if field not in cd:
            result.add_error(f"CAPABILITY_DELTA_MISSING_FIELD: '{field}' absent in capability_delta")

    deltas = cd.get("deltas", [])
    if not deltas:
        result.add_error("CAPABILITY_DELTA_NO_DELTAS: deltas list is empty")
    else:
        result.add_pass(f"CAPABILITY_DELTA_DELTAS_PRESENT: {len(deltas)} deltas")


def check_validation_block(contract: Dict[str, Any], result: ValidationResult) -> None:
    """Check validation block."""
    val = contract.get("validation", {})
    if not val:
        return

    for field in REQUIRED_VALIDATION_FIELDS:
        if field not in val:
            result.add_error(f"VALIDATION_BLOCK_MISSING_FIELD: '{field}' absent in validation")


def check_authority_boundary(contract: Dict[str, Any], result: ValidationResult) -> None:
    """Check authority boundary block."""
    ab = contract.get("authority_boundary", {})
    if not ab:
        result.add_error("AUTHORITY_BOUNDARY_MISSING: authority_boundary block absent")
        return

    for field in REQUIRED_AUTHORITY_BOUNDARY_FIELDS:
        if field not in ab:
            result.add_error(f"AUTHORITY_BOUNDARY_MISSING_FIELD: '{field}' absent in authority_boundary")

    result.add_pass("AUTHORITY_BOUNDARY_PRESENT")


def check_invalid_pytest_commands(contract: Dict[str, Any], result: ValidationResult) -> None:
    """Reject validation_commands that use Python pytest for .cs (C#) test files.

    .NET tests must use 'dotnet test', not 'python -m pytest'.
    This was a known validator gap in the original tri-lane contract.
    Added in FORMAT-FACTORY-TRI-LANE-INTEGRATION-REFRESH-AND-MAINSTREAM-READINESS-GATE-001.
    """
    ms = contract.get("mainstream_execution", {})
    families = ms.get("families", [])

    for fam in families:
        fname = fam.get("family", "<unknown>")
        for cmd in fam.get("validation_commands", []):
            cmd_lower = cmd.lower()
            # Detect: python -m pytest ... *.cs
            if ("python" in cmd_lower and "pytest" in cmd_lower and ".cs" in cmd_lower):
                result.add_error(
                    f"INVALID_PYTEST_CS_COMMAND: family='{fname}' has command "
                    f"'{cmd}' — Python pytest cannot run .cs files. "
                    f"Use 'dotnet test --filter ...' for .NET tests."
                )
            # Detect: python -m pytest referencing tests/net/ paths
            elif ("python" in cmd_lower and "pytest" in cmd_lower
                  and "tests/net/" in cmd_lower):
                result.add_error(
                    f"INVALID_PYTEST_DOTNET_PATH: family='{fname}' has command "
                    f"'{cmd}' — Python pytest cannot run .NET tests in tests/net/. "
                    f"Use 'dotnet test --filter ...' for .NET tests."
                )
            elif "dotnet test" in cmd_lower:
                result.add_pass(f"VALID_DOTNET_TEST_COMMAND: family='{fname}' has 'dotnet test' command")


def check_skills_packet_freshness(contract: Dict[str, Any], result: ValidationResult) -> None:
    """Reject shell packets for FODT and Netpbm when finalization packets exist.

    Added in FORMAT-FACTORY-TRI-LANE-INTEGRATION-REFRESH-AND-MAINSTREAM-READINESS-GATE-001.
    """
    skills = contract.get("skills_handoff", {})
    if not skills:
        return

    stale_shell_paths = [
        "reports/skills-governed-execution-hardening/fodt-packet-shell.json",
        "reports/skills-governed-execution-hardening/netpbm-packet-shell.json",
    ]

    for fam in skills.get("families", []):
        fname = fam.get("family", "")
        pkt_path = fam.get("packet_path", "")
        pkt_type = fam.get("packet_type", "")

        # FODT shell rejected when finalization exists
        if fname in ("FODT", "FODT Markdown", "FODT TXT") and pkt_type == "shell":
            if pkt_path in stale_shell_paths or "shell" in pkt_path.lower():
                result.add_error(
                    f"FODT_SHELL_PACKET_STALE: family='{fname}' uses shell packet '{pkt_path}'. "
                    f"Full finalization packet available at "
                    f"reports/skills-product-breadth-finalization/fodt-markdown-packet.json — use it."
                )
        # Netpbm shell rejected when finalization exists
        elif fname == "Netpbm" and pkt_type == "shell":
            if pkt_path in stale_shell_paths or "shell" in pkt_path.lower():
                result.add_error(
                    f"NETPBM_SHELL_PACKET_STALE: family='Netpbm' uses shell packet '{pkt_path}'. "
                    f"Full finalization packet available at "
                    f"reports/skills-product-breadth-finalization/netpbm-proof-packet.json — use it."
                )

    # Check if FODT is present as "full" type
    fodt_families = [f for f in skills.get("families", []) if "FODT" in f.get("family", "")]
    for f in fodt_families:
        if f.get("packet_type") in ("full", "FULL"):
            result.add_pass(f"FODT_FULL_PACKET_PRESENT: family='{f.get('family')}'")

    # Check if Netpbm is present as "full" type
    netpbm_families = [f for f in skills.get("families", []) if f.get("family") == "Netpbm"]
    for f in netpbm_families:
        if f.get("packet_type") in ("full", "FULL"):
            result.add_pass("NETPBM_FULL_PACKET_PRESENT")


def validate_contract(contract: Dict[str, Any]) -> ValidationResult:
    """Run all validation checks on a tri-lane contract."""
    result = ValidationResult()

    check_required_blocks(contract, result)
    check_supervisor_routing(contract, result)
    check_skills_handoff(contract, result)
    check_acceleration_advisory(contract, result)
    check_poc_targets_mutation(contract, result)
    check_mainstream_execution(contract, result)
    check_netpbm_present(contract, result)
    check_svg_not_replacing_netpbm(contract, result)
    check_evidence_expectations(contract, result)
    check_capability_delta(contract, result)
    check_validation_block(contract, result)
    check_authority_boundary(contract, result)
    # v2 additions (refresh sprint)
    check_invalid_pytest_commands(contract, result)
    check_skills_packet_freshness(contract, result)

    return result


def load_contract(path: str) -> Dict[str, Any]:
    """Load a contract JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def print_result(result: ValidationResult, verbose: bool = True) -> None:
    """Print validation results to stdout."""
    print("\n=== Tri-Lane Contract Validation ===")
    print(f"Verdict: {result.verdict()}")
    print(f"Checks passed: {len(result.checks_passed)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Limitations: {len(result.limitations)}")
    print(f"Warnings: {len(result.warnings)}")

    if result.errors:
        print("\n--- ERRORS (hard fail) ---")
        for e in result.errors:
            print(f"  [ERROR] {e}")

    if result.limitations:
        print("\n--- LIMITATIONS (degraded pass) ---")
        for lim in result.limitations:
            print(f"  [LIMITATION] {lim}")

    if result.warnings:
        print("\n--- WARNINGS ---")
        for w in result.warnings:
            print(f"  [WARNING] {w}")

    if verbose and result.checks_passed:
        print("\n--- PASSED CHECKS ---")
        for p in result.checks_passed:
            print(f"  [PASS] {p}")


def build_results_json(result: ValidationResult, contract_path: str) -> Dict[str, Any]:
    """Build a JSON results document."""
    return {
        "validator": "validate_tri_lane_contract.py",
        "sprint_id": "FORMAT-FACTORY-TRI-LANE-INTEGRATION-FABRIC-001",
        "contract_path": contract_path,
        "verdict": result.verdict(),
        "exit_code": result.exit_code(),
        "checks_passed_count": len(result.checks_passed),
        "errors_count": len(result.errors),
        "limitations_count": len(result.limitations),
        "warnings_count": len(result.warnings),
        "errors": result.errors,
        "limitations": result.limitations,
        "warnings": result.warnings,
        "checks_passed": result.checks_passed,
    }


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: validate_tri_lane_contract.py <contract.json> [--output <results.json>]")
        return 1

    contract_path = sys.argv[1]
    output_path = None

    # Parse optional --output flag
    for i, arg in enumerate(sys.argv[2:], 2):
        if arg == "--output" and i + 1 < len(sys.argv):
            output_path = sys.argv[i + 1]

    if not os.path.exists(contract_path):
        print(f"ERROR: Contract file not found: {contract_path}")
        return 1

    contract = load_contract(contract_path)
    result = validate_contract(contract)
    print_result(result)

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(build_results_json(result, contract_path), f, indent=2)
        print(f"\nResults written to: {output_path}")

    return result.exit_code()


if __name__ == "__main__":
    sys.exit(main())
