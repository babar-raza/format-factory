"""
Tests for Phase 4: Unified Authority Integration Fabric.

Validates:
- SpecContextPackIndex detects present/missing spec artifacts
- AuthorityIntegrationContract verifies all critical invariants
- AuthoritativeGapQueue is deterministic and blocking-correct
- SupervisorVerdictAuthorityPacket has all required fields
- run_all() writes 4 JSON files to output_dir
- Integration with fixture-loaded GraphStore
"""
import json
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.supervisor.authority_integration_fabric import (
    AuthorityIntegrationFabric,
    SpecContextPackIndex,
    SpecContextPackEntry,
    AuthorityIntegrationContract,
    AuthoritativeGapQueue,
    AuthoritativeGapQueueEntry,
    EXPECTED_SPEC_FORMATS,
    FORMAT_TO_POC_TARGET,
)
from tools.requirements_authority.graph_store import GraphStore
from tools.requirements_authority.models import GraphNode, GraphEdge


SPEC_ARTIFACTS_DIR = REPO_ROOT / ".local" / "spec-artifacts"
FIXTURES_DIR = REPO_ROOT / "requirements-authority" / "fixtures"

REQUIRED_OUTPUT_FILES = [
    "spec-context-pack-index.json",
    "authority-integration-contract.json",
    "mainstream-gap-queue-authoritative.json",
    "supervisor-verdict-authority-packet.json",
]

REQUIRED_CONTRACT_FIELDS = [
    "contract_id", "generated_at", "spec_authority_status", "rca_status",
    "tri_lane_status", "netpbm_retained", "svg_replacement_rejected",
    "poc_targets_count", "required_targets_count", "prohibited_replacements",
    "invariants_verified", "invariants_violated", "stream_handoff_protocol",
]

REQUIRED_GAP_QUEUE_FIELDS = [
    "queue_id", "generated_at", "source_graph_hash",
    "total_gaps", "blocking_gaps", "entries",
]

REQUIRED_VERDICT_FIELDS = [
    "packet_id", "generated_at", "source_graph_hash", "claims_checked",
    "coverage_records", "overclaim_risks", "stale_claims", "unsupported_features",
    "poc_readiness_verdict", "mainstream_gap_queue_ref", "recommended_supervisor_decision",
    "false_pass_risks", "false_stop_risks", "stream_consumption_status",
    "external_tool_boundary", "evidence_package_refs",
]


def make_fabric(graph_store=None, tri_lane_status="READY"):
    return AuthorityIntegrationFabric(
        spec_artifacts_dir=SPEC_ARTIFACTS_DIR,
        graph_store=graph_store or GraphStore(),
        tri_lane_status=tri_lane_status,
    )


# ── SpecContextPackIndex Tests ────────────────────────────────────────────────

def test_spec_context_pack_index_has_entries():
    fabric = make_fabric()
    index = fabric.build_spec_context_pack_index()
    assert isinstance(index, SpecContextPackIndex)
    assert len(index.entries) > 0


def test_spec_context_pack_index_expected_formats():
    fabric = make_fabric()
    index = fabric.build_spec_context_pack_index()
    found_formats = {e.format_id for e in index.entries}
    for fmt in EXPECTED_SPEC_FORMATS:
        assert fmt.lower() in found_formats, f"Expected format {fmt} in spec context pack index"


def test_spec_context_pack_fods_complete():
    if not (SPEC_ARTIFACTS_DIR / "FODS-SPEC-001-digest.json").exists():
        pytest.skip("FODS spec artifacts not present")
    fabric = make_fabric()
    index = fabric.build_spec_context_pack_index()
    fods_entry = next((e for e in index.entries if e.format_id == "fods"), None)
    assert fods_entry is not None
    assert fods_entry.completeness == "COMPLETE"
    assert "fods" in index.formats_complete


def test_spec_context_pack_sylk_missing():
    """SYLK has no spec artifact yet — must be in formats_missing."""
    fabric = make_fabric()
    index = fabric.build_spec_context_pack_index()
    assert "sylk" in index.formats_missing


def test_spec_context_pack_to_dict():
    fabric = make_fabric()
    index = fabric.build_spec_context_pack_index()
    d = index.to_dict()
    assert "entries" in d
    assert "formats_complete" in d
    assert "formats_missing" in d
    assert "generated_at" in d


def test_spec_context_pack_entry_fields():
    fabric = make_fabric()
    index = fabric.build_spec_context_pack_index()
    for entry in index.entries:
        d = entry.to_dict()
        assert "source_id" in d
        assert "format_id" in d
        assert "poc_target_id" in d
        assert "completeness" in d


def test_spec_context_pack_poc_target_mapping():
    fabric = make_fabric()
    index = fabric.build_spec_context_pack_index()
    for entry in index.entries:
        if entry.format_id in FORMAT_TO_POC_TARGET:
            assert entry.poc_target_id == FORMAT_TO_POC_TARGET[entry.format_id.upper()]


# ── AuthorityIntegrationContract Tests ───────────────────────────────────────

def test_contract_has_required_fields():
    fabric = make_fabric()
    contract = fabric.build_contract()
    d = contract.to_dict()
    for f in REQUIRED_CONTRACT_FIELDS:
        assert f in d, f"Missing field: {f}"


def test_contract_netpbm_retained():
    fabric = make_fabric()
    contract = fabric.build_contract()
    assert contract.netpbm_retained is True
    assert "NETPBM_RETAINED" in contract.invariants_verified


def test_contract_svg_replacement_rejected():
    fabric = make_fabric()
    contract = fabric.build_contract()
    assert contract.svg_replacement_rejected is True
    assert "SVG_NOT_REPLACE_NETPBM" in contract.invariants_verified


def test_contract_node_edge_type_counts():
    fabric = make_fabric()
    contract = fabric.build_contract()
    assert "18_NODE_TYPES" in contract.invariants_verified
    assert "19_EDGE_TYPES" in contract.invariants_verified


def test_contract_graph_hash_deterministic():
    fabric = make_fabric()
    contract = fabric.build_contract()
    assert "GRAPH_HASH_DETERMINISTIC" in contract.invariants_verified


def test_contract_gap_queue_deterministic():
    fabric = make_fabric()
    contract = fabric.build_contract()
    assert "GAP_QUEUE_DETERMINISTIC" in contract.invariants_verified


def test_contract_no_violations_on_clean_store():
    fabric = make_fabric()
    contract = fabric.build_contract()
    assert len(contract.invariants_violated) == 0


def test_contract_poc_target_counts():
    fabric = make_fabric()
    contract = fabric.build_contract()
    assert contract.poc_targets_count == 8
    assert contract.required_targets_count >= 6


def test_contract_stream_handoff_protocol():
    fabric = make_fabric()
    contract = fabric.build_contract()
    protocol = contract.stream_handoff_protocol
    assert "spec_authority_to_rca" in protocol
    assert "rca_to_mainstream" in protocol
    assert "mainstream_to_supervisor" in protocol


def test_contract_prohibited_replacements():
    fabric = make_fabric()
    contract = fabric.build_contract()
    assert "svg" in contract.prohibited_replacements
    assert contract.prohibited_replacements["svg"] == "netpbm-net"


# ── AuthoritativeGapQueue Tests ───────────────────────────────────────────────

def test_gap_queue_has_required_fields():
    fabric = make_fabric()
    gap_queue = fabric.build_authoritative_gap_queue()
    d = gap_queue.to_dict()
    for f in REQUIRED_GAP_QUEUE_FIELDS:
        assert f in d, f"Missing field: {f}"


def test_gap_queue_deterministic():
    store = GraphStore()
    fabric1 = make_fabric(graph_store=store)
    fabric2 = make_fabric(graph_store=store)
    q1 = fabric1.build_authoritative_gap_queue()
    q2 = fabric2.build_authoritative_gap_queue()
    assert q1.total_gaps == q2.total_gaps
    assert q1.source_graph_hash == q2.source_graph_hash


def test_gap_queue_blocking_targets_count():
    """Non-stretch targets with gaps must be blocking."""
    fabric = make_fabric()
    gap_queue = fabric.build_authoritative_gap_queue()
    assert gap_queue.blocking_gaps <= gap_queue.total_gaps


def test_gap_queue_entries_have_priority():
    fabric = make_fabric()
    gap_queue = fabric.build_authoritative_gap_queue()
    valid_priorities = {"HIGH", "MEDIUM", "LOW"}
    for entry in gap_queue.entries:
        assert entry.priority in valid_priorities


def test_gap_queue_with_fixture():
    fixture_dir = FIXTURES_DIR / "clean_fods_export"
    if not fixture_dir.exists():
        pytest.skip("Fixture not found")
    store = GraphStore.load_from_dir(fixture_dir)
    fabric = make_fabric(graph_store=store)
    gap_queue = fabric.build_authoritative_gap_queue()
    assert gap_queue is not None
    assert isinstance(gap_queue.entries, list)


# ── Supervisor Verdict Authority Packet Tests ─────────────────────────────────

def test_verdict_packet_has_required_fields():
    fabric = make_fabric()
    packet = fabric.build_supervisor_verdict_packet()
    for f in REQUIRED_VERDICT_FIELDS:
        assert f in packet, f"Missing field: {f}"


def test_verdict_packet_authority_augmented():
    """Packet must include authority_integration_version and tri_lane_status."""
    fabric = make_fabric()
    packet = fabric.build_supervisor_verdict_packet()
    assert "authority_integration_version" in packet
    assert "tri_lane_status" in packet
    assert packet["tri_lane_status"] == "READY"


def test_verdict_packet_has_decision():
    fabric = make_fabric()
    packet = fabric.build_supervisor_verdict_packet()
    assert packet.get("recommended_supervisor_decision") is not None


# ── run_all() Tests ───────────────────────────────────────────────────────────

def test_run_all_returns_four_keys():
    fabric = make_fabric()
    result = fabric.run_all()
    assert "spec_context_pack_index" in result
    assert "authority_integration_contract" in result
    assert "mainstream_gap_queue_authoritative" in result
    assert "supervisor_verdict_authority_packet" in result


def test_run_all_writes_four_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        fabric = make_fabric()
        fabric.run_all(output_dir=output_dir)
        for fname in REQUIRED_OUTPUT_FILES:
            fpath = output_dir / fname
            assert fpath.exists(), f"Missing output file: {fname}"


def test_run_all_output_files_valid_json():
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        fabric = make_fabric()
        fabric.run_all(output_dir=output_dir)
        for fname in REQUIRED_OUTPUT_FILES:
            fpath = output_dir / fname
            data = json.loads(fpath.read_text(encoding="utf-8"))
            assert isinstance(data, dict), f"Expected dict in {fname}"


def test_run_all_with_fods_fixture():
    fixture_dir = FIXTURES_DIR / "clean_fods_export"
    if not fixture_dir.exists():
        pytest.skip("Fixture not found")
    store = GraphStore.load_from_dir(fixture_dir)
    with tempfile.TemporaryDirectory() as tmpdir:
        fabric = make_fabric(graph_store=store)
        result = fabric.run_all(output_dir=Path(tmpdir))
        assert result is not None
        for fname in REQUIRED_OUTPUT_FILES:
            assert (Path(tmpdir) / fname).exists()
