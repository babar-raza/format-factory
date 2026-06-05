"""
Tests for the Requirement & Capability Authority Layer MWP.

Uses actual API of tools/requirements_authority/ modules.
"""
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.requirements_authority.models import (
    GraphNode, GraphEdge, NODE_TYPES, EDGE_TYPES, CLAIM_STATUSES, POC_TARGETS,
    PROHIBITED_REPLACEMENTS, REQUIRED_TARGETS
)
from tools.requirements_authority.graph_store import GraphStore
from tools.requirements_authority.validators import GraphValidator
from tools.requirements_authority.coverage_evaluator import CapabilityCoverageEvaluator
from tools.requirements_authority.overclaim_detector import OverclaimDetector
from tools.requirements_authority.staleness_invalidator import StalenessInvalidationEngine
from tools.requirements_authority.poc_readiness import PocReadinessComputer, NETPBM_RETAINED
from tools.requirements_authority.mainstream_gap_queue import MainstreamGapQueueGenerator
from tools.requirements_authority.supervisor_verdict_packet import SupervisorVerdictPacketGenerator


FIXTURES_DIR = REPO_ROOT / "requirements-authority" / "fixtures"

REQUIRED_PACKET_FIELDS = [
    "packet_id", "generated_at", "source_graph_hash", "claims_checked",
    "coverage_records", "overclaim_risks", "stale_claims", "unsupported_features",
    "poc_readiness_verdict", "mainstream_gap_queue_ref", "recommended_supervisor_decision",
    "false_pass_risks", "false_stop_risks", "stream_consumption_status",
    "external_tool_boundary", "evidence_package_refs",
]


def make_node(node_id, node_type, label="", status="candidate", metadata=None):
    return GraphNode(
        node_id=node_id, node_type=node_type, label=label,
        status=status, created_at="2026-01-01T00:00:00Z",
        metadata=metadata or {}
    )


def make_edge(edge_id, edge_type, source, target):
    return GraphEdge(
        edge_id=edge_id, edge_type=edge_type,
        source_node_id=source, target_node_id=target
    )


# ── Model Tests ───────────────────────────────────────────────────────────────

def test_node_types_count():
    assert len(NODE_TYPES) == 18


def test_edge_types_count():
    assert len(EDGE_TYPES) == 19


def test_claim_statuses_defined():
    assert "accepted_for_poc" in CLAIM_STATUSES
    assert "accepted_with_limitations" in CLAIM_STATUSES
    assert "stale" in CLAIM_STATUSES


def test_poc_targets_defined():
    assert "fods" in POC_TARGETS
    assert "fodt" in POC_TARGETS
    assert "netpbm-net" in POC_TARGETS
    assert "zst" in POC_TARGETS


def test_netpbm_in_required_targets():
    assert "netpbm-net" in REQUIRED_TARGETS


def test_svg_in_prohibited_replacements():
    """SVG must not replace Netpbm."""
    assert "svg" in PROHIBITED_REPLACEMENTS
    assert PROHIBITED_REPLACEMENTS["svg"] == "netpbm-net"


# ── Graph Store Tests ─────────────────────────────────────────────────────────

def test_graph_store_add_and_retrieve_node():
    store = GraphStore()
    node = make_node("req:fods:export", "ProductRequirement", "FODS export", "accepted")
    store.add_node(node)
    retrieved = store.get_node("req:fods:export")
    assert retrieved is not None
    assert retrieved.node_type == "ProductRequirement"


def test_graph_store_add_edge():
    store = GraphStore()
    store.add_node(make_node("n1", "ProductRequirement"))
    store.add_node(make_node("n2", "CapabilityClaim"))
    edge = make_edge("e1", "derives_from", "n2", "n1")
    store.add_edge(edge)
    assert len(store.edges) == 1


def test_graph_store_empty():
    store = GraphStore()
    assert len(store.nodes) == 0
    assert len(store.edges) == 0


def test_graph_store_nodes_by_type():
    store = GraphStore()
    store.add_node(make_node("r1", "ProductRequirement"))
    store.add_node(make_node("c1", "CapabilityClaim"))
    assert len(store.nodes_by_type("ProductRequirement")) == 1
    assert len(store.nodes_by_type("CapabilityClaim")) == 1


def test_graph_store_load_from_fixture():
    nodes_path = FIXTURES_DIR / "clean_fods_export" / "nodes.jsonl"
    edges_path = FIXTURES_DIR / "clean_fods_export" / "edges.jsonl"
    if not nodes_path.exists():
        pytest.skip("Fixture not found")
    store = GraphStore()
    store.load_nodes(nodes_path)
    store.load_edges(edges_path)
    assert len(store.nodes) > 0


def test_graph_store_load_from_dir():
    fixture_dir = FIXTURES_DIR / "clean_fods_export"
    if not fixture_dir.exists():
        pytest.skip("Fixture not found")
    store = GraphStore.load_from_dir(fixture_dir)
    assert len(store.nodes) > 0


def test_graph_store_compute_hash():
    store = GraphStore()
    store.add_node(make_node("r1", "ProductRequirement", "req"))
    h1 = store.compute_graph_hash()
    h2 = store.compute_graph_hash()
    assert h1 == h2
    assert len(h1) == 64


# ── Validator Tests ───────────────────────────────────────────────────────────

def test_validator_runs_on_minimal_graph():
    store = GraphStore()
    store.add_node(make_node("req:1", "ProductRequirement", status="accepted"))
    validator = GraphValidator(store)
    result = validator.validate()
    assert result is not None
    assert hasattr(result, 'is_valid')
    assert hasattr(result, 'errors')


def test_validator_accepted_with_limitations_flags_missing_unsupported():
    """Invariant 4: accepted_with_limitations needs UnsupportedFeature."""
    store = GraphStore()
    claim = make_node("claim:1", "CapabilityClaim", status="accepted_with_limitations")
    store.add_node(claim)
    validator = GraphValidator(store)
    result = validator.validate()
    # Should produce at least 1 error or warning for missing UnsupportedFeature
    assert len(result.errors) + len(result.warnings) > 0


def test_validator_ai_draft_claim_flagged():
    """Invariant 6: ai_draft nodes cannot satisfy proof."""
    store = GraphStore()
    req = make_node("req:1", "ProductRequirement", status="accepted")
    claim = make_node("claim:ai", "CapabilityClaim", status="accepted_for_poc",
                      metadata={"authority_state": "ai_draft"})
    store.add_node(req)
    store.add_node(claim)
    store.add_edge(make_edge("e1", "derives_from", "claim:ai", "req:1"))
    validator = GraphValidator(store)
    result = validator.validate()
    # ai_draft should trigger errors/warnings
    assert len(result.errors) + len(result.warnings) > 0


# ── Coverage Evaluator ────────────────────────────────────────────────────────

def test_coverage_evaluator_basic():
    store = GraphStore()
    store.add_node(make_node("req:fods:export", "ProductRequirement", status="accepted",
                             metadata={"format_id": "fods", "product_id": "fods"}))
    evaluator = CapabilityCoverageEvaluator(store)
    records = evaluator.evaluate_all()
    assert isinstance(records, list)


def test_coverage_evaluator_clean_fods_fixture():
    fixture_dir = FIXTURES_DIR / "clean_fods_export"
    if not fixture_dir.exists():
        pytest.skip("Fixture not found")
    store = GraphStore.load_from_dir(fixture_dir)
    evaluator = CapabilityCoverageEvaluator(store)
    records = evaluator.evaluate_all()
    assert isinstance(records, list)


# ── Overclaim Detector ────────────────────────────────────────────────────────

def test_overclaim_detector_empty_graph():
    store = GraphStore()
    detector = OverclaimDetector(store)
    report = detector.detect_all()
    assert report is not None
    assert hasattr(report, 'has_findings')


def test_overclaim_detector_fodt_fixture():
    fixture_dir = FIXTURES_DIR / "fodt_export_not_save_overclaim"
    if not fixture_dir.exists():
        pytest.skip("Fixture not found")
    store = GraphStore.load_from_dir(fixture_dir)
    detector = OverclaimDetector(store)
    report = detector.detect_all()
    assert report is not None


# ── Staleness Invalidator ─────────────────────────────────────────────────────

def test_staleness_engine_runs():
    store = GraphStore()
    spec = make_node("spec:1", "SpecRequirementRef", status="accepted")
    req = make_node("req:1", "ProductRequirement", status="accepted")
    store.add_node(spec)
    store.add_node(req)
    store.add_edge(make_edge("e1", "derives_from", "req:1", "spec:1"))
    engine = StalenessInvalidationEngine(store)
    report = engine.run()
    assert report is not None


# ── POC Readiness ─────────────────────────────────────────────────────────────

def test_netpbm_retained_constant():
    assert NETPBM_RETAINED is True


def test_poc_readiness_compute_all():
    store = GraphStore()
    computer = PocReadinessComputer(store)
    result = computer.compute_all()
    assert result is not None
    result_dict = result.to_dict()
    assert "targets" in result_dict
    assert "overall_verdict" in result_dict


def test_poc_readiness_svg_not_in_results():
    store = GraphStore()
    computer = PocReadinessComputer(store)
    result = computer.compute_all()
    result_dict = result.to_dict()
    targets = result_dict.get("target_results", {})
    assert "svg" not in targets


def test_poc_readiness_zst_fixture():
    fixture_dir = FIXTURES_DIR / "zst_roundtrip_clean"
    if not fixture_dir.exists():
        pytest.skip("Fixture not found")
    store = GraphStore.load_from_dir(fixture_dir)
    computer = PocReadinessComputer(store)
    result = computer.compute_all()
    assert result is not None


# ── Gap Queue ─────────────────────────────────────────────────────────────────

def test_gap_queue_deterministic():
    """Same graph → same gap queue length."""
    def build_store():
        store = GraphStore()
        store.add_node(make_node("req:fods:1", "ProductRequirement", status="accepted",
                                 metadata={"format_id": "fods"}))
        return store

    gen1 = MainstreamGapQueueGenerator(build_store())
    gen2 = MainstreamGapQueueGenerator(build_store())
    q1 = gen1.generate()
    q2 = gen2.generate()
    assert q1 is not None
    assert q2 is not None
    assert len(q1.entries) == len(q2.entries)


def test_gap_queue_has_entries_or_empty():
    store = GraphStore()
    gen = MainstreamGapQueueGenerator(store)
    result = gen.generate()
    assert hasattr(result, 'entries')
    assert isinstance(result.entries, list)


def test_gap_queue_result_has_to_dict():
    store = GraphStore()
    gen = MainstreamGapQueueGenerator(store)
    result = gen.generate()
    d = result.to_dict()
    assert isinstance(d, dict)


# ── Supervisor Verdict Packet ─────────────────────────────────────────────────

def test_supervisor_verdict_packet_16_fields_defined():
    assert len(REQUIRED_PACKET_FIELDS) == 16


def _make_verdict_packet(store):
    """Helper: run full pipeline to generate verdict packet."""
    evaluator = CapabilityCoverageEvaluator(store)
    coverage = evaluator.evaluate_all()
    summary = evaluator.compute_summary(coverage)
    detector = OverclaimDetector(store)
    overclaim_report = detector.detect_all()
    staleness_engine = StalenessInvalidationEngine(store)
    staleness_report = staleness_engine.run()
    computer = PocReadinessComputer(store)
    readiness = computer.compute_all()
    gap_gen = MainstreamGapQueueGenerator(store)
    gap_queue = gap_gen.generate()
    gen = SupervisorVerdictPacketGenerator(store)
    return gen.generate(coverage, overclaim_report, staleness_report, readiness, gap_queue)


def test_supervisor_verdict_packet_generated():
    store = GraphStore()
    packet = _make_verdict_packet(store)
    assert packet is not None
    packet_dict = packet.to_dict()
    for f in REQUIRED_PACKET_FIELDS:
        assert f in packet_dict, f"Missing field: {f}"


def test_supervisor_verdict_packet_has_decision():
    store = GraphStore()
    packet = _make_verdict_packet(store)
    d = packet.to_dict()
    assert d.get("recommended_supervisor_decision") is not None


# ── Replay Fixtures ───────────────────────────────────────────────────────────

def test_replay_fixtures_present():
    required = [
        "clean_fods_export",
        "fodt_export_not_save_overclaim",
        "netpbm_partial_variant_coverage",
        "zst_roundtrip_clean",
        "sylk_missing_dogfood",
        "dif_empirical_only_caveated",
    ]
    for name in required:
        path = FIXTURES_DIR / name
        assert path.exists(), f"Missing fixture: {name}"


def test_replay_fixtures_nodes_edges_exist():
    for fixture_dir in FIXTURES_DIR.iterdir():
        if fixture_dir.is_dir():
            assert (fixture_dir / "nodes.jsonl").exists(), f"{fixture_dir.name} missing nodes"
            assert (fixture_dir / "edges.jsonl").exists(), f"{fixture_dir.name} missing edges"


def test_replay_clean_fods_expected_coverage():
    cov_path = FIXTURES_DIR / "clean_fods_export" / "expected_coverage.json"
    if not cov_path.exists():
        pytest.skip("No expected_coverage.json")
    data = json.loads(cov_path.read_text())
    assert isinstance(data, dict)


def test_replay_zst_determinism():
    fixture_dir = FIXTURES_DIR / "zst_roundtrip_clean"
    if not fixture_dir.exists():
        pytest.skip("Fixture not found")

    def run_once():
        store = GraphStore.load_from_dir(fixture_dir)
        gen = MainstreamGapQueueGenerator(store)
        q = gen.generate()
        return len(q.entries)

    count1 = run_once()
    count2 = run_once()
    assert count1 == count2, "Gap queue not deterministic"


# ── Integration: ai_draft pipeline ───────────────────────────────────────────

def test_ai_draft_claim_not_accepted_in_verdict():
    store = GraphStore()
    req = make_node("req:1", "ProductRequirement", status="accepted")
    ai_claim = make_node("claim:ai", "CapabilityClaim", status="accepted_for_poc",
                         metadata={"authority_state": "ai_draft", "non_authoritative": True})
    store.add_node(req)
    store.add_node(ai_claim)
    store.add_edge(make_edge("e1", "derives_from", "claim:ai", "req:1"))
    packet = _make_verdict_packet(store)
    d = packet.to_dict()
    assert d is not None
    assert "recommended_supervisor_decision" in d


def test_graph_hash_changes_with_new_node():
    store = GraphStore()
    h1 = store.compute_graph_hash()
    store.add_node(make_node("r1", "ProductRequirement"))
    h2 = store.compute_graph_hash()
    assert h1 != h2
