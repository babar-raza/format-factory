"""
Tests for CapabilityCoverageEvaluator: binary PASS/FAIL per claim, proof sufficiency levels.
Sprint: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-MWP-001
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from tools.requirements_authority.models import GraphNode, GraphEdge
from tools.requirements_authority.graph_store import GraphStore
from tools.requirements_authority.coverage_evaluator import (
    CapabilityCoverageEvaluator, evaluate_coverage, OPERATION_MIN_PROOF
)


def _build_store_from_fixture(fixture_name: str) -> GraphStore:
    """Load from a golden fixture pack."""
    fixtures_root = Path(__file__).parent.parent.parent / "requirements-authority" / "fixtures"
    fixture_dir = fixtures_root / fixture_name
    return GraphStore.load_from_dir(fixture_dir)


class TestCoverageEvaluatorBasic:
    def test_empty_store_no_records(self):
        store = GraphStore()
        records = evaluate_coverage(store)
        assert records == []

    def test_summary_empty_gives_blocked(self):
        store = GraphStore()
        evaluator = CapabilityCoverageEvaluator(store)
        records = evaluator.evaluate_all()
        summary = evaluator.compute_summary(records)
        assert summary["total_claims"] == 0
        assert summary["overall_verdict"] == "COVERAGE_BLOCKED"

    def test_missing_requirement_blocks(self):
        store = GraphStore()
        store.add_node(GraphNode("claim:1", "CapabilityClaim", label="C",
                                  status="candidate",
                                  metadata={"operation": "export"}))
        evaluator = CapabilityCoverageEvaluator(store)
        records = evaluator.evaluate_all()
        assert len(records) == 1
        assert "RequirementProof" in records[0].missing_proof_types

    def test_missing_tests_blocks(self):
        store = GraphStore()
        store.add_node(GraphNode("spec:1", "SpecRequirementRef", label="S", status="accepted",
                                  metadata={}))
        store.add_node(GraphNode("req:1", "ProductRequirement", label="R", status="accepted",
                                  metadata={"product_id": "test"}))
        store.add_edge(GraphEdge("e:r:s", "derives_from", "req:1", "spec:1"))
        store.add_node(GraphNode("claim:1", "CapabilityClaim", label="C",
                                  status="candidate",
                                  metadata={"product_id": "test", "operation": "export"}))
        store.add_edge(GraphEdge("e:c:r", "derives_from", "claim:1", "req:1"))
        store.add_node(GraphNode("impl:1", "ImplementationArtifact", label="I", status="candidate",
                                  metadata={}))
        store.add_edge(GraphEdge("e:impl", "implemented_by", "claim:1", "impl:1"))
        # No tests linked
        evaluator = CapabilityCoverageEvaluator(store)
        records = evaluator.evaluate_all()
        assert any("TestProof" in r.missing_proof_types for r in records)


class TestFixtureCleanFodsExport:
    def test_clean_fods_export_passes(self):
        store = _build_store_from_fixture("clean_fods_export")
        evaluator = CapabilityCoverageEvaluator(store)
        records = evaluator.evaluate_all()
        summary = evaluator.compute_summary(records)
        # Clean fixture: claim is accepted_for_poc with all proof satisfied
        assert summary["overall_verdict"] == "COVERAGE_CLEAN"
        assert summary["passed"] >= 1

    def test_clean_fods_export_deterministic(self):
        hashes = []
        for _ in range(3):
            store = _build_store_from_fixture("clean_fods_export")
            hashes.append(store.compute_graph_hash())
        assert len(set(hashes)) == 1, f"Hash not deterministic: {hashes}"


class TestFixtureSylkMissingDogfood:
    def test_sylk_missing_dogfood_blocked(self):
        store = _build_store_from_fixture("sylk_missing_dogfood")
        evaluator = CapabilityCoverageEvaluator(store)
        records = evaluator.evaluate_all()
        summary = evaluator.compute_summary(records)
        # Blocked: dogfood_required=true but no dogfood artifact
        assert summary["overall_verdict"] == "COVERAGE_BLOCKED"


class TestOperationMinProof:
    def test_edit_requires_dogfooded(self):
        assert OPERATION_MIN_PROOF["edit"] == "DOGFOODED"

    def test_export_requires_tested(self):
        assert OPERATION_MIN_PROOF["export"] == "TESTED"

    def test_roundtrip_requires_dogfooded(self):
        assert OPERATION_MIN_PROOF["roundtrip"] == "DOGFOODED"

    def test_dogfood_requires_coverage_validated(self):
        assert OPERATION_MIN_PROOF["dogfood"] == "COVERAGE_VALIDATED"


class TestCoverageSummary:
    def test_summary_overall_verdicts(self):
        store = _build_store_from_fixture("clean_fods_export")
        evaluator = CapabilityCoverageEvaluator(store)
        records = evaluator.evaluate_all()
        summary = evaluator.compute_summary(records)
        assert "overall_verdict" in summary
        assert summary["overall_verdict"] in (
            "COVERAGE_CLEAN", "COVERAGE_PARTIAL_WITH_CAVEATS", "COVERAGE_BLOCKED"
        )
