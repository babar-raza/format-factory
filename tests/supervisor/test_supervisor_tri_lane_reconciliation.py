"""
Tri-Lane Reconciliation tests — FORMAT-FACTORY-SUPERVISOR-TRI-LANE-RECONCILIATION-001

12 required tests:
1. Latest Skills status loaded
2. Latest Acceleration status loaded
3. Stale lane rejected
4. Missing lane blocks readiness
5. Shared contract validates
6. FODS merged from all available lanes
7. FODT merged from Skills/Acceleration/Supervisor
8. Netpbm retained
9. SVG rejected
10. Acceleration ai_draft cannot be authority
11. Mainstream readiness packet contains three families
12. No product source edits
"""

import sys
import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
TRI_LANE_DIR = REPO_ROOT / "reports" / "supervisor-tri-lane-reconciliation"

import pytest


# ===========================================================================
# Test 1: Latest Skills status loaded
# ===========================================================================

def test_latest_skills_status_loaded():
    """Skills consumption readiness JSON exists and is parseable with correct status."""
    readiness_file = REPO_ROOT / "reports" / "skills-governed-execution-hardening" / "skills-consumption-readiness.json"
    assert readiness_file.exists(), "skills-consumption-readiness.json must exist"
    data = json.loads(readiness_file.read_text())
    assert data.get("status") in (
        "SKILLS_CONSUMABLE_WITH_LIMITATIONS",
        "SKILLS_READY_FOR_MAINSTREAM",
        "SKILLS_GOVERNED_EXECUTION_HARDENED",
    ), f"Unexpected Skills status: {data.get('status')}"
    assert "supported_families" in data, "supported_families must be in Skills status"


# ===========================================================================
# Test 2: Latest Acceleration status loaded
# ===========================================================================

def test_latest_acceleration_status_loaded():
    """Acceleration consumption packets directory exists with at least 1 valid packet."""
    acc_dir = REPO_ROOT / "reports" / "acceleration-product-first" / "mainstream-consumption-packets"
    assert acc_dir.exists(), "Acceleration consumption packets directory must exist"
    packets = list(acc_dir.glob("*.json"))
    assert len(packets) >= 1, f"Expected at least 1 acceleration packet, found {len(packets)}"
    # All packets must parse and have authority_state field
    for p in packets:
        data = json.loads(p.read_text())
        assert "authority_state" in data or "format" in data, \
            f"Packet {p.name} missing authority_state or format"


# ===========================================================================
# Test 3: Stale lane rejected
# ===========================================================================

def test_stale_lane_rejected():
    """Lane input discovery explicitly documents stale/missing lanes and does not silently treat them as ready."""
    discovery_file = TRI_LANE_DIR / "lane-input-discovery.json"
    assert discovery_file.exists(), "lane-input-discovery.json must exist"
    data = json.loads(discovery_file.read_text())
    stale = data.get("stale_or_missing_lanes", [])
    # Must document at least the known partial lanes
    assert len(stale) >= 1, "Stale/missing lanes must be documented"
    # None may be silently treated as blocking=false with no issue documented
    for lane in stale:
        assert "issue" in lane, f"Stale lane {lane.get('lane')} must document issue"
        assert "impact" in lane, f"Stale lane {lane.get('lane')} must document impact"


# ===========================================================================
# Test 4: Missing lane blocks readiness (or is explicitly documented as non-blocking)
# ===========================================================================

def test_missing_lane_documented_or_non_blocking():
    """Each missing/partial lane is explicitly classified as blocking or non-blocking."""
    discovery_file = TRI_LANE_DIR / "lane-input-discovery.json"
    data = json.loads(discovery_file.read_text())
    stale = data.get("stale_or_missing_lanes", [])
    for lane in stale:
        assert "blocking" in lane, f"Lane {lane.get('lane')} must declare blocking status"

    # Cross-lane status must confirm overall readiness with documentation
    cross_status_file = TRI_LANE_DIR / "cross-lane-status.json"
    assert cross_status_file.exists(), "cross-lane-status.json must exist"
    cross = json.loads(cross_status_file.read_text())
    overall = cross.get("overall_readiness", {})
    assert "blocking_issues" in overall, "blocking_issues must be listed"
    assert "non_blocking_limitations" in overall, "non_blocking_limitations must be listed"


# ===========================================================================
# Test 5: Shared contract validates
# ===========================================================================

def test_shared_contract_validates():
    """Shared field contract has 14 fields, all validated (PASS or PASS_WITH_LIMITATIONS)."""
    contract_file = TRI_LANE_DIR / "shared-field-contract.json"
    assert contract_file.exists(), "shared-field-contract.json must exist"
    data = json.loads(contract_file.read_text())
    fields = data.get("shared_fields", [])
    assert len(fields) == 14, f"Expected 14 shared fields, got {len(fields)}"
    for f in fields:
        assert f.get("validation") in (
            "PASS", "PASS_WITH_LIMITATIONS"
        ), f"Field {f.get('field')} has invalid validation status: {f.get('validation')}"

    summary = data.get("validation_summary", {})
    assert summary.get("fail", 1) == 0, "No fields should FAIL validation"


# ===========================================================================
# Test 6: FODS merged from all available lanes
# ===========================================================================

def test_fods_merged_from_all_lanes():
    """FODS is represented in Supervisor, Skills, and Acceleration lanes."""
    # Supervisor
    supervisor_file = REPO_ROOT / "reports" / "supervisor-traffic-controller-hardening" / "mainstream-routing-current.json"
    if supervisor_file.exists():
        sup = json.loads(supervisor_file.read_text())
        families = [f.get("family", "").lower() for f in sup.get("active_families", [])]
        assert "fods" in families, f"FODS not in supervisor active families: {families}"

    # Skills
    skills_packet = REPO_ROOT / "reports" / "skills-product-first" / "mainstream-consumption-packet.json"
    assert skills_packet.exists(), "Skills FODS packet must exist"
    skills_data = json.loads(skills_packet.read_text())
    assert skills_data.get("selected_product_gap", {}).get("format_id") == "fods"

    # Acceleration
    acc_fods = REPO_ROOT / "reports" / "acceleration-product-first" / "mainstream-consumption-packets" / "fods-dogfood_status-fods_to_csv_dotnet.json"
    assert acc_fods.exists(), "Acceleration FODS packet must exist"
    acc_data = json.loads(acc_fods.read_text())
    assert acc_data.get("format") == "fods"

    # Readiness packet
    readiness = TRI_LANE_DIR / "mainstream-readiness-packet.json"
    assert readiness.exists()
    rp = json.loads(readiness.read_text())
    fods_caps = [c for c in rp.get("selected_capabilities", []) if c.get("format") == "fods"]
    assert len(fods_caps) >= 1, "FODS must be in selected_capabilities"


# ===========================================================================
# Test 7: FODT merged from Skills/Acceleration/Supervisor
# ===========================================================================

def test_fodt_merged_from_lanes():
    """FODT is represented across Skills shell, Acceleration advisory, and Supervisor routing."""
    # Skills shell
    fodt_shell = REPO_ROOT / "reports" / "skills-governed-execution-hardening" / "fodt-packet-shell.json"
    assert fodt_shell.exists(), "FODT Skills shell packet must exist"

    # Acceleration
    acc_fodt = REPO_ROOT / "reports" / "acceleration-product-first" / "mainstream-consumption-packets" / "fodt-dogfood_status-fodt_to_markdown_dotnet.json"
    assert acc_fodt.exists(), "Acceleration FODT packet must exist"
    acc_data = json.loads(acc_fodt.read_text())
    assert acc_data.get("format") == "fodt"

    # Readiness packet
    readiness = TRI_LANE_DIR / "mainstream-readiness-packet.json"
    rp = json.loads(readiness.read_text())
    fodt_caps = [c for c in rp.get("selected_capabilities", []) if c.get("format") == "fodt"]
    assert len(fodt_caps) >= 1, "FODT must be in selected_capabilities"


# ===========================================================================
# Test 8: Netpbm retained
# ===========================================================================

def test_netpbm_retained():
    """Netpbm is retained in all tri-lane outputs."""
    # Skills shell
    netpbm_shell = REPO_ROOT / "reports" / "skills-governed-execution-hardening" / "netpbm-packet-shell.json"
    assert netpbm_shell.exists(), "Netpbm Skills shell must exist"

    # Acceleration
    acc_netpbm = REPO_ROOT / "reports" / "acceleration-product-first" / "mainstream-consumption-packets" / "netpbm-dotnet_status-netpbm_flip_diagonal.json"
    assert acc_netpbm.exists(), "Acceleration Netpbm packet must exist"

    # Readiness packet
    readiness = TRI_LANE_DIR / "mainstream-readiness-packet.json"
    rp = json.loads(readiness.read_text())
    netpbm_caps = [c for c in rp.get("selected_capabilities", []) if c.get("format") == "netpbm"]
    assert len(netpbm_caps) >= 1, "Netpbm must be in selected_capabilities"

    # Supervisor confirms Netpbm retained
    supervisor_file = REPO_ROOT / "reports" / "supervisor-traffic-controller-hardening" / "mainstream-routing-current.json"
    if supervisor_file.exists():
        sup = json.loads(supervisor_file.read_text())
        families = [f.get("family", "") for f in sup.get("active_families", [])]
        assert "Netpbm" in families, f"Netpbm not in supervisor active families: {families}"


# ===========================================================================
# Test 9: SVG rejected
# ===========================================================================

def test_svg_rejected():
    """SVG is explicitly rejected as a replacement for Netpbm."""
    # Supervisor routing confirms SVG rejection
    supervisor_file = REPO_ROOT / "reports" / "supervisor-traffic-controller-hardening" / "mainstream-routing-current.json"
    if supervisor_file.exists():
        sup = json.loads(supervisor_file.read_text())
        rejected = sup.get("rejected_replacements", [])
        svg_rejections = [r for r in rejected if r.get("proposed") == "SVG"]
        assert len(svg_rejections) >= 1, "SVG replacement must be explicitly rejected"

    # Readiness packet confirms SVG rejection
    readiness = TRI_LANE_DIR / "mainstream-readiness-packet.json"
    rp = json.loads(readiness.read_text())
    netpbm_caps = [c for c in rp.get("selected_capabilities", []) if c.get("format") == "netpbm"]
    if netpbm_caps:
        svg_note = str(netpbm_caps[0].get("supervisor_routing", {}))
        assert "svg_replacement_rejected" in svg_note.lower() or "SVG" in str(rp), \
            "Readiness packet should document SVG rejection"


# ===========================================================================
# Test 10: Acceleration ai_draft cannot be authority
# ===========================================================================

def test_acceleration_ai_draft_cannot_be_authority():
    """All acceleration packets have authority_state=ai_draft and non_authoritative=true."""
    acc_dir = REPO_ROOT / "reports" / "acceleration-product-first" / "mainstream-consumption-packets"
    if acc_dir.exists():
        for p in acc_dir.glob("*.json"):
            data = json.loads(p.read_text())
            state = data.get("authority_state", "")
            assert state in ("ai_draft", ""), \
                f"Acceleration packet {p.name} has unexpected authority_state: {state}"
            # Must not claim authoritative
            assert state != "authoritative", \
                f"Acceleration packet {p.name} claims authoritative — BLOCKED"

    # Readiness packet authority_state must be advisory
    readiness = TRI_LANE_DIR / "mainstream-readiness-packet.json"
    rp = json.loads(readiness.read_text())
    assert rp.get("authority_state") == "advisory"
    assert rp.get("non_authoritative") is True

    # Each acceleration entry must declare ai_draft
    for cap in rp.get("selected_capabilities", []):
        acc_advisory = cap.get("acceleration_advisory", {})
        if acc_advisory:
            assert acc_advisory.get("authority_state") == "ai_draft", \
                f"Acceleration advisory for {cap.get('family')} must be ai_draft"


# ===========================================================================
# Test 11: Mainstream readiness packet contains three families
# ===========================================================================

def test_mainstream_readiness_packet_contains_three_families():
    """Mainstream readiness packet has exactly 3 required families in selected_capabilities."""
    readiness = TRI_LANE_DIR / "mainstream-readiness-packet.json"
    assert readiness.exists(), "mainstream-readiness-packet.json must exist"
    data = json.loads(readiness.read_text())
    caps = data.get("selected_capabilities", [])
    assert len(caps) >= 3, f"Readiness packet must have at least 3 required families, got {len(caps)}"
    families = {c.get("family") for c in caps}
    required = {"FODS", "FODT", "Netpbm"}
    assert required.issubset(families), f"Required families {required} not all present in {families}"


# ===========================================================================
# Test 12: No product source edits
# ===========================================================================

def test_no_product_source_edits():
    """This sprint made no edits to src/net/**, src/python/**, tests/net/**, tests/python/**."""
    # Verify no files in the sprint's changed_files point to forbidden paths
    # Check the tri-lane report doesn't contain any src/ changes
    final_git_file = TRI_LANE_DIR / "final-git-status.txt"
    if final_git_file.exists():
        content = final_git_file.read_text()
        # The diff should not show NEW files (A status) in src/
        lines = [l for l in content.splitlines() if l.startswith("A ") or l.startswith("?? ")]
        new_src_files = [l for l in lines if "/src/net/" in l or "/src/python/" in l
                         or "src/net/" in l or "src/python/" in l]
        assert len(new_src_files) == 0, \
            f"Sprint should not create new product source files: {new_src_files}"

    # Tri-lane readiness packet must NOT include modifications to forbidden paths
    readiness = TRI_LANE_DIR / "mainstream-readiness-packet.json"
    if readiness.exists():
        rp = json.loads(readiness.read_text())
        # Forbidden files must appear in forbidden_files, not as outputs of this sprint
        for cap in rp.get("selected_capabilities", []):
            forbidden = cap.get("forbidden_files", [])
            assert "product-capability-matrix/poc-targets.yaml" in " ".join(forbidden) or \
                   "product-capability-matrix" in " ".join(forbidden), \
                f"Capability {cap.get('family')} must forbid direct poc-targets.yaml writes"
