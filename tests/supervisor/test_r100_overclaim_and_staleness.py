"""
Tests for OverclaimDetector (10 patterns) and StalenessInvalidationEngine (12 triggers).
Sprint: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-MWP-001
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.requirements_authority.models import GraphNode, GraphEdge
from tools.requirements_authority.graph_store import GraphStore
from tools.requirements_authority.overclaim_detector import (
    detect_overclaims, REMEDIATION_ACTIONS
)
from tools.requirements_authority.staleness_invalidator import (
    StalenessInvalidationEngine, run_staleness_invalidation,
    INVALIDATION_TRIGGERS
)


def _build_store_from_fixture(fixture_name: str) -> GraphStore:
    fixtures_root = Path(__file__).parent.parent.parent / "requirements-authority" / "fixtures"
    return GraphStore.load_from_dir(fixtures_root / fixture_name)


class TestRemediationActionsEnum:
    def test_narrow_claim_present(self):
        assert "narrow_claim" in REMEDIATION_ACTIONS

    def test_split_claim_present(self):
        assert "split_claim" in REMEDIATION_ACTIONS

    def test_all_10_actions_present(self):
        expected = {
            "narrow_claim", "split_claim", "add_unsupported_feature", "require_dogfood",
            "require_tests", "require_implementation", "downgrade_status", "mark_empirical_only",
            "request_policy_decision", "reject_claim",
        }
        assert expected.issubset(REMEDIATION_ACTIONS)


class TestOverclaimPattern2SaveWithExport:
    def test_fodt_export_not_save_overclaim_detected(self):
        store = _build_store_from_fixture("fodt_export_not_save_overclaim")
        report = detect_overclaims(store)
        # Pattern 2: save claimed, export_only direction
        assert report.has_findings
        pattern2 = [f for f in report.findings if f.pattern_number == 2]
        assert len(pattern2) >= 1
        assert pattern2[0].remediation_action == "downgrade_status"

    def test_report_to_dict_structure(self):
        store = _build_store_from_fixture("fodt_export_not_save_overclaim")
        report = detect_overclaims(store)
        d = report.to_dict()
        assert "findings" in d
        assert "error_count" in d
        assert "has_overclaims" in d


class TestOverclaimPattern4AllVariants:
    def test_netpbm_partial_variant_overclaim_detected(self):
        store = _build_store_from_fixture("netpbm_partial_variant_coverage")
        report = detect_overclaims(store)
        pattern4 = [f for f in report.findings if f.pattern_number == 4]
        assert len(pattern4) >= 1
        assert pattern4[0].remediation_action == "narrow_claim"

    def test_clean_fods_no_overclaims(self):
        store = _build_store_from_fixture("clean_fods_export")
        report = detect_overclaims(store)
        assert report.error_count == 0


class TestOverclaimPattern9StaleRequirement:
    def test_stale_requirement_triggers_pattern9(self):
        store = GraphStore()
        # Stale requirement
        store.add_node(GraphNode("req:stale", "ProductRequirement", label="Stale req",
                                  status="stale", metadata={}))
        store.add_node(GraphNode("claim:1", "CapabilityClaim", label="C",
                                  status="accepted_for_poc",
                                  metadata={"operation": "export"}))
        store.add_edge(GraphEdge("e:c:r", "derives_from", "claim:1", "req:stale"))
        report = detect_overclaims(store)
        pattern9 = [f for f in report.findings if f.pattern_number == 9]
        assert len(pattern9) >= 1
        assert pattern9[0].remediation_action == "downgrade_status"


class TestStalenessInvalidationTriggers:
    def test_13_triggers_defined(self):
        assert len(INVALIDATION_TRIGGERS) == 12

    def test_spec_requirement_changed_trigger(self):
        assert "spec_requirement_changed" in INVALIDATION_TRIGGERS

    def test_dogfood_older_than_implementation_trigger(self):
        assert "dogfood_output_older_than_implementation" in INVALIDATION_TRIGGERS

    def test_stale_spec_node_detected(self):
        store = GraphStore()
        store.add_node(GraphNode("spec:stale", "SpecRequirementRef", label="Stale spec",
                                  status="stale", metadata={}))
        engine = StalenessInvalidationEngine(store)
        report = engine.run()
        assert len(report.stale_events) >= 1
        assert any(e.trigger == "spec_requirement_changed" for e in report.stale_events)

    def test_staleness_propagation_to_claim(self):
        store = GraphStore()
        # Stale spec → stale requirement → stale claim
        store.add_node(GraphNode("spec:1", "SpecRequirementRef", label="S", status="stale",
                                  metadata={}))
        store.add_node(GraphNode("req:1", "ProductRequirement", label="R", status="accepted",
                                  metadata={}))
        store.add_node(GraphNode("claim:1", "CapabilityClaim", label="C",
                                  status="accepted_for_poc", metadata={}))
        store.add_edge(GraphEdge("e:r:s", "derives_from", "req:1", "spec:1"))
        store.add_edge(GraphEdge("e:c:r", "derives_from", "claim:1", "req:1"))
        engine = StalenessInvalidationEngine(store)
        report = engine.run()
        # Claim should be propagated as stale
        all_stale_ids = {e.node_id for e in report.stale_events}
        assert "spec:1" in all_stale_ids

    def test_save_all_creates_4_artifacts(self):
        import tempfile
        store = GraphStore()
        engine = StalenessInvalidationEngine(store)
        report = engine.run()
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = report.save_all(Path(tmpdir))
        assert "stale-graph-report.json" in paths
        assert "stale-claims.md" in paths
        assert "recomputation-queue.json" in paths
        assert "blocked-poc-targets.json" in paths

    def test_clean_graph_no_stale_events(self):
        store = _build_store_from_fixture("clean_fods_export")
        report = run_staleness_invalidation(store)
        assert len(report.stale_claim_ids) == 0
