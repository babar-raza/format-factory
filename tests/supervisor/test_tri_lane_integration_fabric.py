"""
test_tri_lane_integration_fabric.py
Tests for the Tri-Lane Integration Fabric

Sprint: FORMAT-FACTORY-TRI-LANE-INTEGRATION-FABRIC-001

Required tests (15):
1.  contract schema parses
2.  valid tri-lane packet passes
3.  missing Supervisor block fails
4.  missing Skills block fails
5.  missing Acceleration block fails or degrades with limitation
6.  Acceleration authority misuse fails
7.  direct poc-targets mutation fails
8.  Netpbm missing fails
9.  SVG replacing Netpbm fails
10. Mainstream packet contains 3 families
11. FODS has all three lane inputs
12. FODT has all available lane inputs
13. Netpbm has all available lane inputs
14. dry-run produces no product source edits
15. review package created (or review package proof exists)
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict

import pytest

# Resolve project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "tools" / "supervisor"))

from validate_tri_lane_contract import validate_contract, load_contract
from tri_lane_integration import run_integration, _project_root
from generate_mainstream_execution_packet import generate_mainstream_execution_packet, build_markdown


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

def _valid_contract() -> Dict[str, Any]:
    """Return a minimal valid tri-lane contract for testing."""
    return {
        "contract_version": "1.0",
        "sprint_id": "TEST-SPRINT-001",
        "generated_at": "2026-06-04T00:00:00Z",
        "supervisor_routing": {
            "source": "reports/test/supervisor.json",
            "routing_decision": "CONTINUE",
            "authority_state": "routing_authority",
            "families": [
                {"family": "FODS", "active": True, "svg_replacement_rejected": False},
                {"family": "FODT", "active": True, "svg_replacement_rejected": False},
                {"family": "Netpbm", "active": True, "svg_replacement_rejected": True},
            ],
        },
        "skills_handoff": {
            "source": "reports/test/skills.json",
            "handoff_type": "mixed",
            "authority_state": "governed_execution_authority",
            "families": [
                {"family": "FODS", "packet_type": "full", "packet_path": "reports/test/fods.json"},
                {"family": "FODT", "packet_type": "shell", "packet_path": "reports/test/fodt.json"},
                {"family": "Netpbm", "packet_type": "shell", "packet_path": "reports/test/netpbm.json"},
            ],
        },
        "acceleration_advisory": {
            "source": "reports/test/acceleration",
            "authority_state": "ai_draft",
            "non_authoritative": True,
            "families": [
                {"family": "FODS", "packet_path": "reports/test/fods-accel.json", "authority_state": "ai_draft", "use_for": "advisory"},
                {"family": "FODT", "packet_path": "reports/test/fodt-accel.json", "authority_state": "ai_draft", "use_for": "advisory"},
                {"family": "Netpbm", "packet_path": "reports/test/netpbm-accel.json", "authority_state": "ai_draft", "use_for": "advisory"},
            ],
        },
        "mainstream_execution": {
            "allowed_files": ["src/net/fods/", "src/net/fodt/", "src/net/netpbm/"],
            "forbidden_files": ["src/python/", "registry/", "product-capability-matrix/"],
            "stop_conditions": ["no push without human authorization"],
            "rollback_requirements": ["all changes reversible via git revert"],
            "families": [
                {
                    "family": "FODS",
                    "capability": "dogfood_status.fods_to_csv_dotnet",
                    "allowed_files": ["src/net/fods/FodsDocument.cs"],
                    "forbidden_files": ["src/python/"],
                    "expected_tests": "8+ tests in FodsR114ExportToCsvTests",
                    "expected_dogfood_output": "CSV output from FODS",
                    "expected_transcript": "reports/sprint/transcript-fods.json",
                    "validation_commands": ["dotnet test --filter FodsR114"],
                },
                {
                    "family": "FODT",
                    "capability": "dogfood_status.fodt_to_markdown_dotnet",
                    "allowed_files": ["src/net/fodt/FodtDocument.cs"],
                    "forbidden_files": ["src/python/"],
                    "expected_tests": "8+ tests in FodtR114ExportToMarkdownTests",
                    "expected_dogfood_output": "Markdown output from FODT",
                    "expected_transcript": "reports/sprint/transcript-fodt.json",
                    "validation_commands": ["dotnet test --filter FodtR114"],
                },
                {
                    "family": "Netpbm",
                    "capability": "dotnet_status.netpbm_proof_dogfood",
                    "allowed_files": ["src/net/netpbm/Model/NetpbmImage.cs"],
                    "forbidden_files": ["src/python/"],
                    "expected_tests": "8+ tests in NetpbmR114Tests",
                    "expected_dogfood_output": "Dogfood output from Netpbm",
                    "expected_transcript": "reports/sprint/transcript-netpbm.json",
                    "validation_commands": ["dotnet test --filter NetpbmR114"],
                },
            ],
        },
        "evidence_expectations": {
            "minimum_passing_tests": 24,
            "minimum_governed_transcripts": 3,
            "minimum_source_diffs": 3,
            "required_for_clean_pass": {
                "families_touched": 3,
                "source_diffs": 3,
                "governed_transcripts": 3,
                "raw_logs": 3,
                "capability_matrix_deltas": 3,
            },
        },
        "capability_delta": {
            "proposed_only": True,
            "deltas": [
                {"family": "FODS", "capability_path": "fods.dogfood_status.fods_to_csv_dotnet", "proposed_status": "IMPLEMENTED", "requires_test_evidence": True},
                {"family": "FODT", "capability_path": "fodt.dogfood_status.fodt_to_markdown_dotnet", "proposed_status": "IMPLEMENTED", "requires_test_evidence": True},
                {"family": "Netpbm", "capability_path": "netpbm.dotnet_status.netpbm_proof_dogfood", "proposed_status": "IMPLEMENTED", "requires_test_evidence": True},
            ],
        },
        "validation": {
            "validator_tool": "tools/supervisor/validate_tri_lane_contract.py",
            "pass_criteria": ["supervisor_routing present", "skills_handoff present", "netpbm present"],
            "rejection_conditions": ["missing supervisor_routing", "acceleration as authority", "svg replacing netpbm"],
        },
        "authority_boundary": {
            "supervisor": "routing_authority",
            "skills": "governed_execution_authority",
            "acceleration": "ai_draft",
            "mainstream": "product_implementation_authority",
            "format_factory_gates": "human_authority",
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: Contract schema parses
# ─────────────────────────────────────────────────────────────────────────────

def test_contract_schema_parses():
    """Contract schema JSON is valid and parseable."""
    schema_path = _PROJECT_ROOT / "reports/tri-lane-integration-fabric/tri-lane-contract.schema.json"
    assert schema_path.exists(), f"Schema not found: {schema_path}"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert schema.get("$schema") is not None, "Schema missing $schema declaration"
    assert schema.get("type") == "object", "Schema must define an object type"
    required = schema.get("required", [])
    expected_blocks = [
        "supervisor_routing", "skills_handoff", "acceleration_advisory",
        "mainstream_execution", "evidence_expectations", "capability_delta",
        "validation", "authority_boundary",
    ]
    for block in expected_blocks:
        assert block in required, f"Schema required list missing '{block}'"


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: Valid tri-lane packet passes
# ─────────────────────────────────────────────────────────────────────────────

def test_valid_tri_lane_packet_passes():
    """A complete, valid tri-lane contract passes all validation checks."""
    contract = _valid_contract()
    result = validate_contract(contract)
    assert result.verdict() == "TRI_LANE_CONTRACT_VALID", (
        f"Expected TRI_LANE_CONTRACT_VALID, got {result.verdict()}. Errors: {result.errors}"
    )
    assert len(result.errors) == 0, f"Expected no errors, got: {result.errors}"


def test_real_contract_passes():
    """The real generated tri-lane contract passes validation.

    Updated in FORMAT-FACTORY-TRI-LANE-INTEGRATION-REFRESH-AND-MAINSTREAM-READINESS-GATE-001:
    Now validates the v2 contract. The v1 contract (tri-lane-integration-fabric) is stale
    (FODT/Netpbm shell packets) and correctly fails the updated validator.
    """
    # Prefer v2 contract (refresh sprint)
    contract_v2_path = _PROJECT_ROOT / "reports/tri-lane-integration-refresh/tri-lane-contract.v2.json"
    if contract_v2_path.exists():
        contract = load_contract(str(contract_v2_path))
        result = validate_contract(contract)
        assert result.verdict() in ("TRI_LANE_CONTRACT_VALID", "TRI_LANE_CONTRACT_VALID_WITH_LIMITATIONS"), (
            f"Contract v2 validation failed: {result.verdict()}. Errors: {result.errors}"
        )
        return

    # Fall back to v1 only if v2 not present (pre-refresh)
    contract_v1_path = _PROJECT_ROOT / "reports/tri-lane-integration-fabric/tri-lane-contract.json"
    if not contract_v1_path.exists():
        pytest.skip("No contract found (neither v2 nor v1)")
    contract = load_contract(str(contract_v1_path))
    result = validate_contract(contract)
    assert result.verdict() in ("TRI_LANE_CONTRACT_VALID", "TRI_LANE_CONTRACT_VALID_WITH_LIMITATIONS"), (
        f"Real contract validation failed: {result.verdict()}. Errors: {result.errors}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: Missing Supervisor block fails
# ─────────────────────────────────────────────────────────────────────────────

def test_missing_supervisor_block_fails():
    """Contract missing supervisor_routing block is rejected."""
    contract = _valid_contract()
    del contract["supervisor_routing"]
    result = validate_contract(contract)
    assert result.is_rejected, "Expected rejection when supervisor_routing missing"
    assert any("supervisor_routing" in e for e in result.errors), (
        f"Expected error about missing supervisor_routing. Errors: {result.errors}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 4: Missing Skills block fails
# ─────────────────────────────────────────────────────────────────────────────

def test_missing_skills_block_fails():
    """Contract missing skills_handoff block is rejected."""
    contract = _valid_contract()
    del contract["skills_handoff"]
    result = validate_contract(contract)
    assert result.is_rejected, "Expected rejection when skills_handoff missing"
    assert any("skills_handoff" in e for e in result.errors), (
        f"Expected error about missing skills_handoff. Errors: {result.errors}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 5: Missing Acceleration block fails or degrades
# ─────────────────────────────────────────────────────────────────────────────

def test_missing_acceleration_block_degrades():
    """Contract missing acceleration_advisory block degrades with limitation."""
    contract = _valid_contract()
    del contract["acceleration_advisory"]
    result = validate_contract(contract)
    # Missing acceleration_advisory is a top-level block, so it's an error
    assert result.is_rejected or result.is_degraded, (
        "Expected rejection or degradation when acceleration_advisory missing"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 6: Acceleration authority misuse fails
# ─────────────────────────────────────────────────────────────────────────────

def test_acceleration_authority_misuse_fails():
    """Contract with acceleration authority_state != ai_draft is rejected."""
    contract = _valid_contract()
    contract["acceleration_advisory"]["authority_state"] = "authoritative"
    result = validate_contract(contract)
    assert result.is_rejected, "Expected rejection when acceleration claims non-ai_draft authority"
    assert any("ACCELERATION_AUTHORITY_MISUSE" in e or "ACCELERATION_WRONG_AUTHORITY" in e or "authority" in e.lower()
               for e in result.errors), (
        f"Expected authority misuse error. Errors: {result.errors}"
    )


def test_acceleration_family_authority_misuse_fails():
    """Contract with per-family acceleration authority_state != ai_draft is rejected."""
    contract = _valid_contract()
    contract["acceleration_advisory"]["families"][0]["authority_state"] = "routing_authority"
    result = validate_contract(contract)
    assert result.is_rejected, "Expected rejection when family acceleration authority_state != ai_draft"


# ─────────────────────────────────────────────────────────────────────────────
# Test 7: Direct poc-targets mutation fails
# ─────────────────────────────────────────────────────────────────────────────

def test_direct_poc_targets_mutation_fails():
    """Contract with capability_delta.proposed_only != true is rejected."""
    contract = _valid_contract()
    contract["capability_delta"]["proposed_only"] = False
    result = validate_contract(contract)
    assert result.is_rejected, "Expected rejection when proposed_only != True"
    assert any("CAPABILITY_DELTA_NOT_PROPOSED_ONLY" in e for e in result.errors), (
        f"Expected poc-targets mutation error. Errors: {result.errors}"
    )


def test_poc_targets_mutation_pattern_fails():
    """Contract containing direct mutation patterns is rejected."""
    contract = _valid_contract()
    # Inject a mutation pattern
    contract["hack"] = {"mutate": True, "direct_write": True}
    result = validate_contract(contract)
    assert result.is_rejected, "Expected rejection for direct mutation pattern"


# ─────────────────────────────────────────────────────────────────────────────
# Test 8: Netpbm missing fails
# ─────────────────────────────────────────────────────────────────────────────

def test_netpbm_missing_fails():
    """Contract without Netpbm in mainstream execution is rejected."""
    contract = _valid_contract()
    # Remove Netpbm from mainstream execution families
    contract["mainstream_execution"]["families"] = [
        f for f in contract["mainstream_execution"]["families"]
        if f["family"] != "Netpbm"
    ]
    # Also remove from supervisor routing
    contract["supervisor_routing"]["families"] = [
        f for f in contract["supervisor_routing"]["families"]
        if f["family"] != "Netpbm"
    ]
    result = validate_contract(contract)
    assert result.is_rejected, "Expected rejection when Netpbm missing from mainstream execution"
    assert any("NETPBM_MISSING" in e for e in result.errors), (
        f"Expected NETPBM_MISSING error. Errors: {result.errors}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 9: SVG replacing Netpbm fails
# ─────────────────────────────────────────────────────────────────────────────

def test_svg_replacing_netpbm_fails():
    """Contract with SVG in mainstream families but Netpbm absent is rejected."""
    contract = _valid_contract()
    # Replace Netpbm with SVG in mainstream
    contract["mainstream_execution"]["families"] = [
        f for f in contract["mainstream_execution"]["families"]
        if f["family"] != "Netpbm"
    ] + [{
        "family": "SVG",
        "capability": "svg_export",
        "allowed_files": ["src/net/svg/"],
        "forbidden_files": ["src/python/"],
        "expected_tests": "8+ tests",
        "expected_dogfood_output": "SVG output",
        "expected_transcript": "reports/sprint/transcript-svg.json",
        "validation_commands": ["dotnet test --filter SvgR114"],
    }]
    contract["supervisor_routing"]["families"] = [
        f for f in contract["supervisor_routing"]["families"]
        if f["family"] != "Netpbm"
    ]
    result = validate_contract(contract)
    assert result.is_rejected, "Expected rejection when SVG replaces Netpbm"
    # Should see NETPBM_MISSING and/or SVG_REPLACING_NETPBM
    error_text = " ".join(result.errors)
    assert "NETPBM_MISSING" in error_text or "SVG_REPLACING_NETPBM" in error_text, (
        f"Expected SVG replacement error. Errors: {result.errors}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 10: Mainstream packet contains 3 families
# ─────────────────────────────────────────────────────────────────────────────

def test_mainstream_packet_contains_3_families():
    """Generated Mainstream execution packet has at least 3 families.

    Updated in FORMAT-FACTORY-TRI-LANE-INTEGRATION-REFRESH-AND-MAINSTREAM-READINESS-GATE-001:
    Packet v2 now includes 4 families (FODS, FODT, FODT_TXT, Netpbm).
    Test updated to accept 3+ families and require all 3 core families are present.
    """
    packet = generate_mainstream_execution_packet(_project_root())
    assert packet["family_count"] >= 3, (
        f"Expected 3+ families, got {packet['family_count']}"
    )
    family_names = {f["family"] for f in packet["families"]}
    # Core 3 must always be present
    assert "FODS" in family_names, f"FODS must be in families. Got: {family_names}"
    assert "FODT" in family_names or "FODT_TXT" in family_names or any("fodt" in f.lower() for f in family_names), \
        f"At least one FODT family must be present. Got: {family_names}"
    assert "Netpbm" in family_names, f"Netpbm must be in families. Got: {family_names}"


# ─────────────────────────────────────────────────────────────────────────────
# Test 11: FODS has all three lane inputs
# ─────────────────────────────────────────────────────────────────────────────

def test_fods_has_all_three_lane_inputs():
    """FODS family packet has supervisor_route, skills_handoff, and acceleration_advisory."""
    packet = generate_mainstream_execution_packet(_project_root())
    fods = next(f for f in packet["families"] if f["family"] == "FODS")

    assert "supervisor_route" in fods, "FODS missing supervisor_route"
    assert fods["supervisor_route"]["authority_state"] == "routing_authority"

    assert "skills_handoff" in fods, "FODS missing skills_handoff"
    assert fods["skills_handoff"]["authority_state"] == "governed_execution_authority"

    assert "acceleration_advisory" in fods, "FODS missing acceleration_advisory"
    assert fods["acceleration_advisory"]["authority_state"] == "ai_draft"
    assert fods["acceleration_advisory"]["non_authoritative"] is True


# ─────────────────────────────────────────────────────────────────────────────
# Test 12: FODT has all available lane inputs
# ─────────────────────────────────────────────────────────────────────────────

def test_fodt_has_all_available_lane_inputs():
    """FODT family packet has supervisor_route, skills_handoff, and acceleration_advisory."""
    packet = generate_mainstream_execution_packet(_project_root())
    fodt = next(f for f in packet["families"] if f["family"] == "FODT")

    assert "supervisor_route" in fodt, "FODT missing supervisor_route"
    assert fodt["supervisor_route"]["authority_state"] == "routing_authority"

    assert "skills_handoff" in fodt, "FODT missing skills_handoff"
    assert fodt["skills_handoff"]["authority_state"] == "governed_execution_authority"

    assert "acceleration_advisory" in fodt, "FODT missing acceleration_advisory"
    assert fodt["acceleration_advisory"]["authority_state"] == "ai_draft"


# ─────────────────────────────────────────────────────────────────────────────
# Test 13: Netpbm has all available lane inputs
# ─────────────────────────────────────────────────────────────────────────────

def test_netpbm_has_all_available_lane_inputs():
    """Netpbm family packet has supervisor_route, skills_handoff, and acceleration_advisory."""
    packet = generate_mainstream_execution_packet(_project_root())
    netpbm = next(f for f in packet["families"] if f["family"] == "Netpbm")

    assert "supervisor_route" in netpbm, "Netpbm missing supervisor_route"
    assert netpbm["supervisor_route"]["authority_state"] == "routing_authority"

    assert "skills_handoff" in netpbm, "Netpbm missing skills_handoff"
    assert netpbm["skills_handoff"]["authority_state"] == "governed_execution_authority"

    assert "acceleration_advisory" in netpbm, "Netpbm missing acceleration_advisory"
    assert netpbm["acceleration_advisory"]["authority_state"] == "ai_draft"

    # SVG replacement must be rejected
    assert netpbm["supervisor_route"].get("svg_replacement_rejected") is True or \
           netpbm.get("svg_rejection_note", "") != "" or \
           "SVG" not in {f["family"] for f in packet["families"]}, \
           "Netpbm SVG rejection not explicitly documented"


# ─────────────────────────────────────────────────────────────────────────────
# Test 14: Dry-run produces no product source edits
# ─────────────────────────────────────────────────────────────────────────────

def test_dry_run_no_product_source_edits():
    """The e2e dry-run proof confirms no product source edits in this sprint."""
    dry_run_path = _PROJECT_ROOT / "reports/tri-lane-integration-fabric/e2e-dry-run-result.json"
    assert dry_run_path.exists(), f"Dry-run result not found: {dry_run_path}"
    result = json.loads(dry_run_path.read_text(encoding="utf-8"))
    checks = result.get("checks", {})

    # This sprint made no product source edits
    assert checks.get("no_product_source_edits_this_sprint") == "PASS", (
        f"Dry-run failed: no_product_source_edits_this_sprint={checks.get('no_product_source_edits_this_sprint')}"
    )

    # Verify authority invariants
    auth_invariants = result.get("authority_invariants", {})
    assert auth_invariants.get("poc_targets_not_mutated") is True, "poc-targets must not be mutated"
    assert auth_invariants.get("acceleration_is_ai_draft_only") is True, "Acceleration must remain ai_draft"
    assert auth_invariants.get("supervisor_is_routing_authority") is True, "Supervisor must remain routing authority"


# ─────────────────────────────────────────────────────────────────────────────
# Test 15: Review package created (proof file exists)
# ─────────────────────────────────────────────────────────────────────────────

def test_review_package_proof_or_artifacts_exist():
    """Sprint artifacts exist as evidence of the review package being creatable."""
    # Check that all key Lane deliverables exist
    required_files = [
        "reports/tri-lane-integration-fabric/00-preflight.md",
        "reports/tri-lane-integration-fabric/tri-lane-contract.json",
        "reports/tri-lane-integration-fabric/tri-lane-contract.schema.json",
        "reports/tri-lane-integration-fabric/contract-validation-results.json",
        "reports/tri-lane-integration-fabric/mainstream-execution-packet.json",
        "reports/tri-lane-integration-fabric/mainstream-execution-packet.md",
        "reports/tri-lane-integration-fabric/e2e-dry-run-proof.md",
        "reports/tri-lane-integration-fabric/e2e-dry-run-result.json",
        "tools/supervisor/tri_lane_integration.py",
        "tools/supervisor/validate_tri_lane_contract.py",
        "tools/supervisor/generate_mainstream_execution_packet.py",
    ]
    missing = [f for f in required_files if not (_PROJECT_ROOT / f).exists()]
    assert not missing, f"Missing required sprint artifacts: {missing}"


# ─────────────────────────────────────────────────────────────────────────────
# Additional integration tests
# ─────────────────────────────────────────────────────────────────────────────

def test_integration_runs_without_error():
    """tri_lane_integration.run_integration() runs without exceptions."""
    result = run_integration(_project_root())
    assert result["status"] in ("OK", "OK_WITH_LIMITATIONS"), (
        f"Integration returned unexpected status: {result['status']}"
    )
    assert result.get("active_family_count", 0) >= 3, (
        f"Expected at least 3 families, got {result.get('active_family_count', 0)}"
    )


def test_integration_authority_boundaries_preserved():
    """Integration preserves all authority boundaries (no violations)."""
    result = run_integration(_project_root())
    violations = result.get("violations", [])
    assert len(violations) == 0, (
        f"Authority boundary violations detected: {violations}"
    )


def test_contract_validation_results_exist():
    """The contract-validation-results.json file exists and shows TRI_LANE_CONTRACT_VALID."""
    results_path = _PROJECT_ROOT / "reports/tri-lane-integration-fabric/contract-validation-results.json"
    assert results_path.exists(), "contract-validation-results.json not found"
    results = json.loads(results_path.read_text(encoding="utf-8"))
    assert results.get("verdict") in (
        "TRI_LANE_CONTRACT_VALID",
        "TRI_LANE_CONTRACT_VALID_WITH_LIMITATIONS"
    ), f"Unexpected verdict: {results.get('verdict')}"
    assert results.get("errors_count", 1) == 0, f"Errors found: {results.get('errors')}"


def test_mainstream_packet_has_stop_conditions():
    """Every family in the mainstream packet has stop_conditions defined."""
    packet = generate_mainstream_execution_packet(_project_root())
    for fam in packet["families"]:
        assert fam.get("stop_conditions"), (
            f"Family '{fam['family']}' missing stop_conditions"
        )
        assert len(fam["stop_conditions"]) >= 3, (
            f"Family '{fam['family']}' has fewer than 3 stop_conditions"
        )


def test_mainstream_packet_capability_deltas_proposed_only():
    """All capability deltas in the mainstream packet are proposed_only."""
    packet = generate_mainstream_execution_packet(_project_root())
    for fam in packet["families"]:
        cd = fam.get("proposed_capability_delta", {})
        if cd:
            assert cd.get("proposed_only") is True, (
                f"Family '{fam['family']}' capability_delta.proposed_only must be True"
            )
            assert cd.get("requires_test_evidence") is True, (
                f"Family '{fam['family']}' capability_delta.requires_test_evidence must be True"
            )


def test_markdown_packet_builds():
    """Markdown rendering of the mainstream packet builds without error."""
    packet = generate_mainstream_execution_packet(_project_root())
    md = build_markdown(packet)
    assert "# Mainstream Execution Packet" in md
    assert "FODS" in md
    assert "FODT" in md
    assert "Netpbm" in md
    assert "ai_draft" in md
    assert "routing_authority" in md
    assert "governed_execution_authority" in md
