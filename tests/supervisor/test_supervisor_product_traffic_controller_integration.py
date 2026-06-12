"""
Integration tests for the Supervisor Product Traffic Controller (TC-TEST-001).

Covers:
  - generate_stream_routing_packet.py: velocity scoring + stream decisions
  - check_cross_stream_consumption.py: bridge detection
  - continuation state integration with new states
  - external tool governance integration
  - Mainstream routing packet content validation
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "supervisor"))



class TestStreamRoutingPacketGenerator:

    def _make_replay(self, stream, breadth=2, overhead=0, skills_consumption="not_consumed",
                      acc_consumption="not_consumed", fp_risk="medium", fs_risk="low"):
        return [
            {
                "stream": stream,
                "sprint_id": f"test-{stream}-sprint",
                "product_velocity_score": {
                    "product_breadth_score": breadth,
                    "machinery_overhead_score": overhead,
                },
                "skills_consumption": skills_consumption,
                "acceleration_consumption": acc_consumption,
                "false_pass_risk": fp_risk,
                "false_stop_risk": fs_risk,
                "ai_output_status": "no_ai",
                "final_supervisor_decision": "CONTINUE_WITH_LIMITATIONS",
                "deterministic_verdict": "ACCEPTED",
            }
        ]

    def _make_gaps(self, stream="mainstream", count=3):
        return {
            "selected_gaps": [
                {
                    "format": f"Format{i}",
                    "stream": stream,
                    "priority_score": 100,
                    "external_gate": False,
                    "gap_id": f"gap-{i}",
                }
                for i in range(count)
            ]
        }

    def test_run_mainstream_produces_outputs(self, tmp_path):
        from generate_stream_routing_packet import run
        import json as _json

        replay = self._make_replay("mainstream", breadth=2)
        gaps = self._make_gaps("mainstream", 3)
        replay_path = tmp_path / "replay.json"
        gaps_path = tmp_path / "gaps.json"
        replay_path.write_text(_json.dumps(replay))
        gaps_path.write_text(_json.dumps(gaps))

        exit_code = run("mainstream", replay_path, gaps_path, tmp_path)
        assert exit_code == 0
        assert (tmp_path / "product_velocity_score.json").exists()
        assert (tmp_path / "stream_decision.json").exists()
        assert (tmp_path / "false_pass_false_stop_assessment.json").exists()
        assert (tmp_path / "product_velocity_summary.md").exists()

    def test_mainstream_partial_classification(self, tmp_path):
        from generate_stream_routing_packet import run
        import json as _json

        replay = self._make_replay("mainstream", breadth=1)
        gaps = self._make_gaps("mainstream", 8)
        replay_path = tmp_path / "replay.json"
        gaps_path = tmp_path / "gaps.json"
        replay_path.write_text(_json.dumps(replay))
        gaps_path.write_text(_json.dumps(gaps))

        run("mainstream", replay_path, gaps_path, tmp_path)
        decision = _json.loads((tmp_path / "stream_decision.json").read_text())
        # Breadth=1 → PARTIAL_FEW_FAMILIES → CONTINUE_WITH_LIMITATIONS
        assert decision["mainstream_classification"] != "CLEAN_PASS"

    def test_stream_decision_parses_as_json(self, tmp_path):
        from generate_stream_routing_packet import run
        import json as _json

        replay = self._make_replay("mainstream", breadth=2)
        gaps = self._make_gaps("mainstream")
        replay_path = tmp_path / "replay.json"
        gaps_path = tmp_path / "gaps.json"
        replay_path.write_text(_json.dumps(replay))
        gaps_path.write_text(_json.dumps(gaps))

        run("mainstream", replay_path, gaps_path, tmp_path)
        data = _json.loads((tmp_path / "stream_decision.json").read_text())
        assert "stream" in data
        assert "decision" in data
        assert "product_breadth_score" in data

    def test_false_pass_detection(self, tmp_path):
        from generate_stream_routing_packet import run
        import json as _json

        # breadth=0 for mainstream → PARTIAL_FEW_FAMILIES → false pass if claimed ACCEPTED
        replay = self._make_replay("mainstream", breadth=0, fp_risk="high")
        gaps = self._make_gaps("mainstream")
        replay_path = tmp_path / "replay.json"
        gaps_path = tmp_path / "gaps.json"
        replay_path.write_text(_json.dumps(replay))
        gaps_path.write_text(_json.dumps(gaps))

        run("mainstream", replay_path, gaps_path, tmp_path)
        assessment = _json.loads((tmp_path / "false_pass_false_stop_assessment.json").read_text())
        assert "false_pass_detected" in assessment
        assert "false_stop_detected" in assessment


class TestVelocityScorer:

    def test_12_dimensions_present(self):
        from product_velocity_scorer import score_stream_velocity
        result = score_stream_velocity("mainstream", {}, {}, {})
        expected_keys = {
            "poc_help_score", "product_breadth_score", "product_throughput_delta",
            "mainstream_blocker_removed", "reusable_accelerator_consumed",
            "ai_acceleration_consumed", "governed_execution_consumed",
            "false_pass_prevented", "false_stop_prevented", "human_handoff_reduced",
            "machinery_overhead_score", "semantic_drift_risk",
        }
        assert expected_keys.issubset(set(result.keys()))

    def test_mainstream_partial_few_families(self):
        from product_velocity_scorer import classify_mainstream_package
        result = classify_mainstream_package({"families_touched": 1})
        assert result == "PARTIAL_FEW_FAMILIES"

    def test_mainstream_clean_pass(self):
        from product_velocity_scorer import classify_mainstream_package
        result = classify_mainstream_package({
            "families_touched": 3, "source_diffs": 3, "governed_transcripts": 3,
            "raw_logs": 3, "capability_matrix_deltas": 3,
            "repair_items": 0, "product_items": 5,
        })
        assert result == "CLEAN_PASS"


class TestCrossStreamConsumptionBridge:

    def test_skills_missing_packet_in_real_replay(self, tmp_path):
        from check_cross_stream_consumption import run
        replay = [
            {"stream": "mainstream", "sprint_id": "ms-r113",
             "product_velocity_score": {"product_breadth_score": 2, "machinery_overhead_score": 0},
             "skills_consumption": "not_consumed", "acceleration_consumption": "not_consumed",
             "false_pass_risk": "medium", "false_stop_risk": "low", "ai_output_status": "no_ai"},
            {"stream": "skills", "sprint_id": "sk-r113",
             "product_velocity_score": {"product_breadth_score": 0, "machinery_overhead_score": 2},
             "ai_output_status": "no_ai"},
            {"stream": "acceleration", "sprint_id": "ac-r112",
             "product_velocity_score": {"product_breadth_score": 1, "machinery_overhead_score": 1},
             "ai_output_status": "no_ai"},
        ]
        replay_path = tmp_path / "replay.json"
        replay_path.write_text(json.dumps(replay))
        run(replay_path, tmp_path)
        status = json.loads((tmp_path / "cross-stream-consumption-status.json").read_text())
        assert "SKILLS_MISSING_PACKET" in status["all_flags"]

    def test_consumption_ok_when_consumed(self):
        from check_cross_stream_consumption import check_skills_consumption
        mainstream = {"skills_consumption": "consumed",
                      "product_velocity_score": {"product_breadth_score": 3, "machinery_overhead_score": 0}}
        skills = {"product_velocity_score": {"product_breadth_score": 2, "machinery_overhead_score": 1}}
        result = check_skills_consumption(mainstream, skills)
        assert result["verdict"] == "SKILLS_CONSUMPTION_OK"


class TestContinuationStateTrafficController:

    def test_no_product_floor_routes_correctly(self):
        from autonomous_cycle import classify_continuation_state
        result = classify_continuation_state(
            auto_continue_value=True, at_max_iterations=False,
            hard_stops=[], overclaimed=[], rework_items=[], review={},
            policies_path=Path("/dev/null"),
            product_output_floor_met=False,
        )
        assert result == "NO_PRODUCT_OUTPUT_FLOOR"

    def test_missing_artifacts_routes_correctly(self):
        from autonomous_cycle import classify_continuation_state
        result = classify_continuation_state(
            auto_continue_value=True, at_max_iterations=False,
            hard_stops=[], overclaimed=[], rework_items=[], review={},
            policies_path=Path("/dev/null"),
            required_artifacts_present=False,
        )
        assert result == "NO_MISSING_REQUIRED_ARTIFACTS"

    def test_dirty_unclassified_routes_correctly(self):
        from autonomous_cycle import classify_continuation_state
        result = classify_continuation_state(
            auto_continue_value=True, at_max_iterations=False,
            hard_stops=[], overclaimed=[], rework_items=[], review={},
            policies_path=Path("/dev/null"),
            dirty_state_classified=False,
        )
        assert result == "NO_UNCLASSIFIED_DIRTY_STATE"


class TestExternalToolGovernanceIntegration:

    def test_governance_verdict_has_required_fields(self):
        from external_tool_governance import build_external_tool_governance_verdict
        detections = {
            "claude_flow_ruflo": {"mcp_registered": True, "state_directory_present": False},
            "task_master_ai": {"mcp_registered": True},
            "superpowers": {"detected": False},
            "ghidra_mcp": {"detected": False, "mcp_registered": False},
        }
        verdict = build_external_tool_governance_verdict(detections)
        assert "overall_verdict" in verdict
        assert "deterministic_supervisor_retains_authority" in verdict
        assert verdict["deterministic_supervisor_retains_authority"] is True

    def test_ruflo_cannot_close_taskcards(self):
        from external_tool_governance import validate_external_tool_output_authority
        ruflo_output = {"closes_taskcard": True, "content": "task done"}
        assert validate_external_tool_output_authority(ruflo_output) is False

    def test_runtime_status_json_parses(self):
        """Verify the actual runtime status JSON produced by LANE F parses correctly."""
        status_path = Path("reports/supervisor-product-traffic-controller/external-tool-runtime-status.json")
        if status_path.exists():
            data = json.loads(status_path.read_text())
            assert "deterministic_supervisor_retains_authority" in data
            assert data["deterministic_supervisor_retains_authority"] is True

    def test_stream_routing_not_impacted_by_external_tools(self):
        """External tools are governed — they do not impact stream routing decisions."""
        decision_impact_path = Path("reports/supervisor-product-traffic-controller/external-tool-decision-impact.json")
        if decision_impact_path.exists():
            data = json.loads(decision_impact_path.read_text())
            assert data["decision_impact"] == "none"

    def test_mainstream_routing_packet_has_6_plus_gaps(self):
        """Mainstream routing packet must have 6+ product gaps."""
        packet_path = Path("reports/supervisor-streams/mainstream/routing-packet.json")
        if packet_path.exists():
            data = json.loads(packet_path.read_text())
            assert len(data.get("actionable_gaps", [])) >= 6
