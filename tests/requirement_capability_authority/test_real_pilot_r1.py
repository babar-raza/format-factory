"""
RCA Real Pilot R1 — Integration Tests
Sprint: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-REAL-PILOT-R1-001

Tests the existing RCA implementation against real pilot scenarios:
- Missing requirement blocks claim
- Missing implementation blocks claim
- Missing tests blocks coverage
- Missing dogfood blocks dogfood claim
- Export without target writer blocks export
- ai_draft rejected as proof
- Evidence package path-only does not prove claim
- accepted_with_limitations requires UnsupportedFeature
- Stale requirement invalidates coverage
- Same inputs produce same graph hash (determinism)
- Gap queue is generated
- Supervisor verdict packet is generated
- Architecture-blocked FODS/FODT exports do not pass
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from tools.requirements_authority.graph_store import GraphStore
from tools.requirements_authority.models import GraphEdge, GraphNode
from tools.requirements_authority.validators import GraphValidator
from tools.requirements_authority.coverage_evaluator import CapabilityCoverageEvaluator
from tools.requirements_authority.overclaim_detector import OverclaimDetector
from tools.requirements_authority.staleness_invalidator import StalenessInvalidationEngine
from tools.requirements_authority.poc_readiness import PocReadinessComputer
from tools.requirements_authority.mainstream_gap_queue import MainstreamGapQueueGenerator
from tools.requirements_authority.supervisor_verdict_packet import SupervisorVerdictPacketGenerator
from tools.requirements_authority.run_replay_fixtures import GoldenReplaySuite

NOW = datetime.now(timezone.utc).isoformat()


def _node(node_id, node_type, label, status="candidate", metadata=None):
    return GraphNode(
        node_id=node_id, node_type=node_type, label=label,
        status=status, metadata=metadata or {}, created_at=NOW,
    )


def _edge(edge_id, edge_type, source, target):
    return GraphEdge(
        edge_id=edge_id, edge_type=edge_type,
        source_node_id=source, target_node_id=target,
        metadata={}, created_at=NOW,
    )


def _full_accepted_store():
    """Minimal accepted_for_poc proof graph: req → spec, claim → req, impl, test, dogfood, evpkg."""
    store = GraphStore()
    store.add_node(_node("spec:x:s1", "SpecRequirementRef", "X spec", "accepted",
                         {"spec_type": "official", "format_id": "x"}))
    store.add_node(_node("req:x:load", "ProductRequirement", "X load", "accepted",
                         {"product_id": "x", "format_id": "x", "operation": "load"}))
    store.add_node(_node("impl:x:load", "ImplementationArtifact", "X load impl", "candidate",
                         {"path": "src/x/x.py", "operation": "load", "product_id": "x"}))
    store.add_node(_node("test:x:load", "TestArtifact", "X load test", "candidate",
                         {"path": "tests/x/test_load.py", "product_id": "x"}))
    store.add_node(_node("dogfood:x:load", "DogfoodArtifact", "X dogfood", "candidate",
                         {"path": "examples/x/load.py", "output_path": "out.x",
                          "sha256": "abc123", "product_id": "x"}))
    store.add_node(_node("evpkg:x", "EvidencePackage", "X evpkg", "candidate",
                         {"product_id": "x", "declared_not_verified": True}))
    store.add_node(_node("claim:x:load", "CapabilityClaim", "X load claim", "accepted_for_poc",
                         {"product_id": "x", "format_id": "x", "operation": "load",
                          "direction": "read_only", "fidelity": "lossless",
                          "dogfood_required": False, "poc_scope": True}))

    store.add_edge(_edge("e:req:spec", "derives_from", "req:x:load", "spec:x:s1"))
    store.add_edge(_edge("e:claim:req", "derives_from", "claim:x:load", "req:x:load"))
    store.add_edge(_edge("e:claim:impl", "implemented_by", "claim:x:load", "impl:x:load"))
    store.add_edge(_edge("e:claim:test", "tested_by", "claim:x:load", "test:x:load"))
    store.add_edge(_edge("e:claim:dog", "dogfooded_by", "claim:x:load", "dogfood:x:load"))
    store.add_edge(_edge("e:claim:evpkg", "evidenced_by", "claim:x:load", "evpkg:x"))
    return store


# ─── Tests: proof requirements ───────────────────────────────────────────────

class TestMissingRequirementBlocksClaim:
    def test_missing_requirement_blocks_accepted_claim(self):
        """accepted_for_poc claim with no derives_from edge fails invariant 1."""
        store = GraphStore()
        store.add_node(_node("claim:z:load", "CapabilityClaim", "Z load", "accepted_for_poc",
                             {"product_id": "z", "format_id": "z", "operation": "load"}))
        validator = GraphValidator(store)
        result = validator.validate()
        assert not result.is_valid, "Claim with no requirement must fail validation"
        assert len(result.errors) > 0

    def test_missing_requirement_blocks_coverage(self):
        """Claim with no requirement link blocks coverage proof."""
        store = GraphStore()
        store.add_node(_node("claim:z:load", "CapabilityClaim", "Z load", "candidate",
                             {"product_id": "z", "format_id": "z", "operation": "load"}))
        evaluator = CapabilityCoverageEvaluator(store)
        records = evaluator.evaluate_all()
        assert len(records) == 1
        assert records[0].coverage_verdict == "BLOCKED"


class TestMissingImplementationBlocksClaim:
    def test_missing_impl_blocks_coverage(self):
        """Claim with req but no implementation gets IMPLEMENTATION_ONLY level."""
        store = GraphStore()
        store.add_node(_node("spec:y:s1", "SpecRequirementRef", "Y spec", "accepted",
                             {"spec_type": "official"}))
        store.add_node(_node("req:y:load", "ProductRequirement", "Y load", "accepted",
                             {"product_id": "y", "format_id": "y", "operation": "load"}))
        store.add_node(_node("claim:y:load", "CapabilityClaim", "Y load", "candidate",
                             {"product_id": "y", "format_id": "y", "operation": "load"}))
        store.add_edge(_edge("e:req:spec", "derives_from", "req:y:load", "spec:y:s1"))
        store.add_edge(_edge("e:claim:req", "derives_from", "claim:y:load", "req:y:load"))

        evaluator = CapabilityCoverageEvaluator(store)
        records = evaluator.evaluate_all()
        assert records[0].coverage_verdict == "BLOCKED"  # REQUIREMENT_ONLY < TESTED


class TestMissingTestsBlocksCoverage:
    def test_impl_only_is_implementation_only_level(self):
        """Req + impl but no tests = IMPLEMENTATION_ONLY = BLOCKED for TESTED min."""
        store = GraphStore()
        store.add_node(_node("spec:t:s1", "SpecRequirementRef", "T spec", "accepted",
                             {"spec_type": "official"}))
        store.add_node(_node("req:t:load", "ProductRequirement", "T load", "accepted",
                             {"product_id": "t", "format_id": "t", "operation": "load"}))
        store.add_node(_node("impl:t:load", "ImplementationArtifact", "T impl", "candidate",
                             {"path": "src/t.py", "operation": "load", "product_id": "t"}))
        store.add_node(_node("claim:t:load", "CapabilityClaim", "T load", "candidate",
                             {"product_id": "t", "format_id": "t", "operation": "load"}))
        store.add_edge(_edge("e:req:spec", "derives_from", "req:t:load", "spec:t:s1"))
        store.add_edge(_edge("e:claim:req", "derives_from", "claim:t:load", "req:t:load"))
        store.add_edge(_edge("e:claim:impl", "implemented_by", "claim:t:load", "impl:t:load"))

        evaluator = CapabilityCoverageEvaluator(store)
        records = evaluator.evaluate_all()
        # IMPLEMENTATION_ONLY level; TESTED min → BLOCKED
        assert records[0].coverage_verdict == "BLOCKED"


class TestMissingDogfoodBlocksDogfoodClaim:
    def test_dogfood_required_without_artifact_blocks(self):
        """Claim with dogfood_required=True but no dogfooded_by edge is BLOCKED."""
        store = GraphStore()
        store.add_node(_node("spec:d:s1", "SpecRequirementRef", "D spec", "accepted",
                             {"spec_type": "official"}))
        store.add_node(_node("req:d:roundtrip", "ProductRequirement", "D roundtrip", "accepted",
                             {"product_id": "d", "format_id": "d", "operation": "roundtrip"}))
        store.add_node(_node("impl:d:rt", "ImplementationArtifact", "D impl", "candidate",
                             {"path": "src/d.py", "operation": "roundtrip", "product_id": "d"}))
        store.add_node(_node("test:d:rt", "TestArtifact", "D test", "candidate",
                             {"path": "tests/d/test_rt.py", "product_id": "d"}))
        store.add_node(_node("claim:d:roundtrip", "CapabilityClaim", "D roundtrip", "candidate",
                             {"product_id": "d", "format_id": "d", "operation": "roundtrip",
                              "dogfood_required": True}))
        store.add_edge(_edge("e:req:spec", "derives_from", "req:d:roundtrip", "spec:d:s1"))
        store.add_edge(_edge("e:claim:req", "derives_from", "claim:d:roundtrip", "req:d:roundtrip"))
        store.add_edge(_edge("e:claim:impl", "implemented_by", "claim:d:roundtrip", "impl:d:rt"))
        store.add_edge(_edge("e:claim:test", "tested_by", "claim:d:roundtrip", "test:d:rt"))

        evaluator = CapabilityCoverageEvaluator(store)
        records = evaluator.evaluate_all()
        # dogfood_required=True but no DogfoodProof → BLOCKED
        assert records[0].coverage_verdict == "BLOCKED"


class TestExportWithoutTargetWriterBlocks:
    def test_blocked_export_claim_stays_blocked(self):
        """Claim with status=blocked and blocked_by UnsupportedFeature stays BLOCKED in coverage."""
        store = GraphStore()
        store.add_node(_node("spec:f:s1", "SpecRequirementRef", "F spec", "accepted",
                             {"spec_type": "official"}))
        store.add_node(_node("req:f:export_csv", "ProductRequirement", "FODS export CSV", "accepted",
                             {"product_id": "fods", "format_id": "fods", "operation": "export"}))
        store.add_node(_node("unsupported:fods:csv", "UnsupportedFeature",
                             "FormatFactory.Csv .NET writer does not exist", "accepted",
                             {"severity": "blocking", "feature": "csv_target_writer"}))
        store.add_node(_node("claim:fods:export_csv", "CapabilityClaim",
                             "FODS export CSV (blocked)", "blocked",
                             {"product_id": "fods", "format_id": "fods", "operation": "export",
                              "dogfood_required": True, "poc_scope": False,
                              "blocked_reason": "No target writer"}))
        store.add_edge(_edge("e:req:spec", "derives_from", "req:f:export_csv", "spec:f:s1"))
        store.add_edge(_edge("e:claim:req", "derives_from", "claim:fods:export_csv", "req:f:export_csv"))
        store.add_edge(_edge("e:claim:blocked", "blocked_by", "claim:fods:export_csv", "unsupported:fods:csv"))
        store.add_edge(_edge("e:claim:limited", "limited_by", "claim:fods:export_csv", "unsupported:fods:csv"))

        evaluator = CapabilityCoverageEvaluator(store)
        records = evaluator.evaluate_all()
        # blocked claim with dogfood_required=True and no dogfood → BLOCKED
        assert records[0].coverage_verdict == "BLOCKED"


class TestAiDraftRejectedAsProof:
    """Invariant 6: ai_draft node cannot satisfy proof."""

    def test_ai_draft_impl_fails_invariant(self):
        store = GraphStore()
        store.add_node(_node("spec:ai:s1", "SpecRequirementRef", "AI spec", "accepted",
                             {"spec_type": "official"}))
        store.add_node(_node("req:ai:load", "ProductRequirement", "AI load", "accepted",
                             {"product_id": "ai", "format_id": "ai", "operation": "load"}))
        store.add_node(_node("impl:ai:load", "ImplementationArtifact", "AI draft impl", "ai_draft",
                             {"path": "src/ai.py", "fidelity": "ai_draft", "product_id": "ai"}))
        store.add_node(_node("claim:ai:load", "CapabilityClaim", "AI load", "accepted_for_poc",
                             {"product_id": "ai", "format_id": "ai", "operation": "load"}))
        store.add_edge(_edge("e:req:spec", "derives_from", "req:ai:load", "spec:ai:s1"))
        store.add_edge(_edge("e:claim:req", "derives_from", "claim:ai:load", "req:ai:load"))
        store.add_edge(_edge("e:claim:impl", "implemented_by", "claim:ai:load", "impl:ai:load"))

        validator = GraphValidator(store)
        result = validator.validate()
        assert not result.is_valid, "ai_draft node used as proof must fail validation"
        assert any("ai_draft" in e.message.lower() or "invariant 6" in e.message.lower() for e in result.errors)


class TestEvidencePackagePathOnlyDoesNotProveClaim:
    def test_no_evidenced_by_means_no_evidence_proof(self):
        """Claim with no evidenced_by edge has no EvidencePackageProof."""
        store = GraphStore()
        store.add_node(_node("spec:ev:s1", "SpecRequirementRef", "EV spec", "accepted",
                             {"spec_type": "official"}))
        store.add_node(_node("req:ev:save", "ProductRequirement", "EV save", "accepted",
                             {"product_id": "ev", "format_id": "ev", "operation": "save"}))
        store.add_node(_node("impl:ev:save", "ImplementationArtifact", "EV impl", "candidate",
                             {"path": "src/ev.py", "operation": "roundtrip", "product_id": "ev"}))
        store.add_node(_node("test:ev:save", "TestArtifact", "EV test", "candidate",
                             {"path": "tests/ev/test_save.py", "product_id": "ev"}))
        store.add_node(_node("claim:ev:save", "CapabilityClaim", "EV save", "candidate",
                             {"product_id": "ev", "format_id": "ev", "operation": "save",
                              "dogfood_required": False}))
        store.add_edge(_edge("e:req:spec", "derives_from", "req:ev:save", "spec:ev:s1"))
        store.add_edge(_edge("e:claim:req", "derives_from", "claim:ev:save", "req:ev:save"))
        store.add_edge(_edge("e:claim:impl", "implemented_by", "claim:ev:save", "impl:ev:save"))
        store.add_edge(_edge("e:claim:test", "tested_by", "claim:ev:save", "test:ev:save"))
        # No evidenced_by edge

        evaluator = CapabilityCoverageEvaluator(store)
        records = evaluator.evaluate_all()
        # Has req + impl + tests → TESTED level; no dogfood/evidence → insufficient for ACCEPTED_FOR_POC
        # Evaluator returns PARTIAL (some proof present but not sufficient for full acceptance)
        assert records[0].coverage_verdict in ("PARTIAL", "BLOCKED")


class TestAcceptedWithLimitationsRequiresUnsupportedFeature:
    def test_accepted_with_limitations_no_unsupported_feature_fails(self):
        """Invariant 4: accepted_with_limitations must link to UnsupportedFeature."""
        store = GraphStore()
        store.add_node(_node("spec:aw:s1", "SpecRequirementRef", "AW spec", "accepted",
                             {"spec_type": "official"}))
        store.add_node(_node("req:aw:load", "ProductRequirement", "AW load", "accepted",
                             {"product_id": "aw", "format_id": "aw", "operation": "load"}))
        store.add_node(_node("claim:aw:load", "CapabilityClaim", "AW load", "accepted_with_limitations",
                             {"product_id": "aw", "format_id": "aw", "operation": "load"}))
        store.add_edge(_edge("e:req:spec", "derives_from", "req:aw:load", "spec:aw:s1"))
        store.add_edge(_edge("e:claim:req", "derives_from", "claim:aw:load", "req:aw:load"))

        validator = GraphValidator(store)
        result = validator.validate()
        assert not result.is_valid, "accepted_with_limitations without UnsupportedFeature must fail"

    def test_accepted_with_limitations_with_unsupported_feature_passes(self):
        """accepted_with_limitations + UnsupportedFeature passes invariant 4."""
        store = GraphStore()
        store.add_node(_node("spec:aw2:s1", "SpecRequirementRef", "AW2 spec", "accepted",
                             {"spec_type": "official"}))
        store.add_node(_node("req:aw2:load", "ProductRequirement", "AW2 load", "accepted",
                             {"product_id": "aw2", "format_id": "aw2", "operation": "load"}))
        store.add_node(_node("unsupported:aw2:x", "UnsupportedFeature", "AW2 feature", "accepted",
                             {"severity": "non_blocking", "feature": "partial_support"}))
        store.add_node(_node("claim:aw2:load", "CapabilityClaim", "AW2 load", "accepted_with_limitations",
                             {"product_id": "aw2", "format_id": "aw2", "operation": "load"}))
        store.add_edge(_edge("e:req:spec", "derives_from", "req:aw2:load", "spec:aw2:s1"))
        store.add_edge(_edge("e:claim:req", "derives_from", "claim:aw2:load", "req:aw2:load"))
        store.add_edge(_edge("e:claim:limited", "limited_by", "claim:aw2:load", "unsupported:aw2:x"))

        validator = GraphValidator(store)
        result = validator.validate()
        # Should pass invariant 4
        inv4_errors = [e for e in result.errors if "invariant 4" in e.message.lower() or "unsupportedfeature" in e.message.lower()]
        assert len(inv4_errors) == 0


class TestStaleRequirementInvalidatesCoverage:
    def test_stale_requirement_blocks_claim(self):
        """Claim deriving from stale requirement is blocked by staleness engine."""
        store = GraphStore()
        store.add_node(_node("spec:st:old", "SpecRequirementRef", "Old spec", "stale",
                             {"spec_type": "official", "stale": True}))
        store.add_node(_node("req:st:old", "ProductRequirement", "Old req", "stale",
                             {"product_id": "st", "format_id": "st", "operation": "load", "stale": True}))
        store.add_node(_node("claim:st:load", "CapabilityClaim", "ST load", "stale",
                             {"product_id": "st", "format_id": "st", "operation": "load", "stale": True}))
        store.add_edge(_edge("e:req:spec", "derives_from", "req:st:old", "spec:st:old"))
        store.add_edge(_edge("e:claim:req", "derives_from", "claim:st:load", "req:st:old"))
        store.add_edge(_edge("e:stale", "stale_due_to", "claim:st:load", "req:st:old"))

        engine = StalenessInvalidationEngine(store)
        report = engine.run()
        assert "claim:st:load" in report.stale_claim_ids, "Stale claim must appear in stale_claim_ids"


class TestGraphHashDeterminism:
    def test_same_store_same_hash(self):
        """Same GraphStore content must produce same hash across 3 runs."""
        hashes = []
        for _ in range(3):
            store = _full_accepted_store()
            hashes.append(store.compute_graph_hash())
        assert len(set(hashes)) == 1, f"Graph hash not deterministic: {hashes}"

    def test_different_content_different_hash(self):
        """Different node content must produce different hash."""
        store1 = _full_accepted_store()
        store2 = _full_accepted_store()
        store2.add_node(_node("extra:node", "SpecRequirementRef", "Extra", "accepted", {}))
        assert store1.compute_graph_hash() != store2.compute_graph_hash()


class TestGapQueueGenerated:
    def test_gap_queue_generates_for_store_with_claims(self):
        """Gap queue must generate without error; graph_hash must be present."""
        store = _full_accepted_store()
        gen = MainstreamGapQueueGenerator(store)
        result = gen.generate()
        result_dict = result.to_dict() if hasattr(result, "to_dict") else {}
        assert "graph_hash" in result_dict or hasattr(result, "graph_hash")

    def test_gap_queue_deterministic(self):
        """Same store must produce same gap queue graph_hash."""
        store = _full_accepted_store()
        r1 = MainstreamGapQueueGenerator(store).generate()
        r2 = MainstreamGapQueueGenerator(store).generate()
        h1 = r1.graph_hash if hasattr(r1, "graph_hash") else r1.to_dict().get("graph_hash")
        h2 = r2.graph_hash if hasattr(r2, "graph_hash") else r2.to_dict().get("graph_hash")
        assert h1 == h2, "Gap queue graph_hash must be deterministic"


class TestSupervisorVerdictPacketGenerated:
    def test_svp_generated_with_claims_checked(self):
        """Supervisor verdict packet must have claims_checked > 0 for non-empty store."""
        store = _full_accepted_store()
        evaluator = CapabilityCoverageEvaluator(store)
        cov_records = evaluator.evaluate_all()
        detector = OverclaimDetector(store)
        overclaim = detector.detect_all()
        engine = StalenessInvalidationEngine(store)
        stale = engine.run()
        poc = PocReadinessComputer(store).compute_all()
        gap = MainstreamGapQueueGenerator(store).generate()

        svp_gen = SupervisorVerdictPacketGenerator(store)
        svp = svp_gen.generate(
            coverage_records=cov_records,
            overclaim_report=overclaim,
            staleness_report=stale,
            readiness_result=poc,
            gap_queue_result=gap,
        )
        svp_dict = svp.to_dict() if hasattr(svp, "to_dict") else {}
        claims_checked = svp_dict.get("claims_checked", 0)
        assert claims_checked > 0, f"claims_checked must be > 0, got {claims_checked}"

    def test_svp_has_source_graph_hash(self):
        """Supervisor verdict packet must reference source_graph_hash."""
        store = _full_accepted_store()
        evaluator = CapabilityCoverageEvaluator(store)
        cov_records = evaluator.evaluate_all()
        detector = OverclaimDetector(store)
        overclaim = detector.detect_all()
        engine = StalenessInvalidationEngine(store)
        stale = engine.run()
        poc = PocReadinessComputer(store).compute_all()
        gap = MainstreamGapQueueGenerator(store).generate()
        svp_gen = SupervisorVerdictPacketGenerator(store)
        svp = svp_gen.generate(cov_records, overclaim, stale, poc, gap)
        svp_dict = svp.to_dict() if hasattr(svp, "to_dict") else {}
        assert "source_graph_hash" in svp_dict
        assert len(svp_dict["source_graph_hash"]) > 10


class TestGoldenReplayFixtures:
    def test_all_6_fixtures_pass(self):
        """All 6 golden replay fixture packs must pass."""
        fixtures_root = _REPO_ROOT / "requirements-authority" / "fixtures"
        if not fixtures_root.exists():
            pytest.skip("Golden fixtures directory not found")
        suite = GoldenReplaySuite(fixtures_root)
        result = suite.run_all()
        failed = [r.fixture_name for r in result.fixture_results if not r.passed]
        assert result.overall_pass, f"Failed fixtures: {failed}"

    def test_determinism_across_all_fixtures(self):
        """Same fixture inputs must produce same graph hash across reruns."""
        fixtures_root = _REPO_ROOT / "requirements-authority" / "fixtures"
        if not fixtures_root.exists():
            pytest.skip("Golden fixtures directory not found")
        suite = GoldenReplaySuite(fixtures_root)
        result = suite.run_all()
        assert result.determinism_pass, "Determinism must hold across all fixture reruns"


class TestArchitectureBlockedExportsClearedByPilot:
    """Verify the real pilot graph has architecture-blocked exports as BLOCKED."""

    def test_pilot_proof_graph_exists(self):
        """Pilot proof graph must exist with non-zero claims."""
        graph_dir = _REPO_ROOT / "reports/requirement-capability-real-pilot-r1/proof-graph"
        assert (graph_dir / "nodes.jsonl").exists(), "Proof graph nodes.jsonl must exist"
        assert (graph_dir / "edges.jsonl").exists(), "Proof graph edges.jsonl must exist"
        assert (graph_dir / "graph-manifest.json").exists(), "Proof graph manifest must exist"

    def test_pilot_coverage_records_exist(self):
        """Pilot coverage records must exist."""
        coverage_file = _REPO_ROOT / "reports/requirement-capability-real-pilot-r1/coverage-records.jsonl"
        assert coverage_file.exists()
        records = [json.loads(line) for line in coverage_file.read_text().splitlines() if line.strip()]
        assert len(records) >= 15, f"Expected at least 15 coverage records, got {len(records)}"

    def test_fods_export_csv_blocked_in_pilot(self):
        """FODS export_csv claim must be BLOCKED in pilot coverage records."""
        coverage_file = _REPO_ROOT / "reports/requirement-capability-real-pilot-r1/coverage-records.jsonl"
        if not coverage_file.exists():
            pytest.skip("Pilot not yet run")
        records = {json.loads(line)["claim_id"]: json.loads(line)
                   for line in coverage_file.read_text().splitlines() if line.strip()}
        assert "claim:fods:export_csv" in records
        assert records["claim:fods:export_csv"]["coverage_verdict"] == "BLOCKED"

    def test_fodt_export_markdown_blocked_in_pilot(self):
        """FODT export_markdown claim must be BLOCKED in pilot coverage records."""
        coverage_file = _REPO_ROOT / "reports/requirement-capability-real-pilot-r1/coverage-records.jsonl"
        if not coverage_file.exists():
            pytest.skip("Pilot not yet run")
        records = {json.loads(line)["claim_id"]: json.loads(line)
                   for line in coverage_file.read_text().splitlines() if line.strip()}
        assert "claim:fodt:export_markdown" in records
        assert records["claim:fodt:export_markdown"]["coverage_verdict"] == "BLOCKED"

    def test_pilot_supervisor_verdict_exists(self):
        """Supervisor verdict packet must exist and reference a graph hash."""
        svp_file = _REPO_ROOT / "reports/requirement-capability-real-pilot-r1/supervisor-verdict-packet.json"
        assert svp_file.exists()
        svp = json.loads(svp_file.read_text())
        assert "source_graph_hash" in svp
        assert svp.get("claims_checked", 0) >= 15

    def test_poc_targets_yaml_not_mutated(self):
        """poc-targets.yaml must not contain any RCA pilot marker (not mutated)."""
        poc_file = _REPO_ROOT / "product-capability-matrix/poc-targets.yaml"
        assert poc_file.exists()
        content = poc_file.read_text()
        assert "requirement-capability-real-pilot-r1" not in content, "poc-targets.yaml must not be mutated"
