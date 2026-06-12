"""
Tests for cross-stream consumption bridge (TC-CONS-001).
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "supervisor"))



class TestSkillsConsumption:

    def _make_mainstream(self, skills_consumption="not_consumed"):
        return {
            "stream": "mainstream",
            "sprint_id": "test-sprint",
            "product_velocity_score": {"product_breadth_score": 2, "machinery_overhead_score": 0},
            "skills_consumption": skills_consumption,
            "acceleration_consumption": "not_consumed",
        }

    def _make_skills(self, overhead=2, breadth=0):
        return {
            "stream": "skills",
            "sprint_id": "test-sprint",
            "product_velocity_score": {"product_breadth_score": breadth, "machinery_overhead_score": overhead},
            "ai_output_status": "no_ai",
        }

    def test_skills_missing_packet_detected(self):
        from check_cross_stream_consumption import check_skills_consumption
        mainstream = self._make_mainstream("not_consumed")
        skills = self._make_skills(overhead=2, breadth=0)
        result = check_skills_consumption(mainstream, skills)
        assert "SKILLS_MISSING_PACKET" in result["flags"]

    def test_skills_no_product_output_flag(self):
        from check_cross_stream_consumption import check_skills_consumption
        mainstream = self._make_mainstream("not_consumed")
        skills = self._make_skills(overhead=0, breadth=0)
        result = check_skills_consumption(mainstream, skills)
        assert "SKILLS_NO_PRODUCT_OUTPUT" in result["flags"]

    def test_skills_consumed_no_gap(self):
        from check_cross_stream_consumption import check_skills_consumption
        mainstream = self._make_mainstream("consumed")
        skills = self._make_skills(overhead=1, breadth=2)
        result = check_skills_consumption(mainstream, skills)
        assert result["status"] == "consumed"
        assert result["action_required"] is False

    def test_skills_verdict_gap(self):
        from check_cross_stream_consumption import check_skills_consumption
        mainstream = self._make_mainstream("not_consumed")
        skills = self._make_skills(overhead=2, breadth=0)
        result = check_skills_consumption(mainstream, skills)
        assert result["verdict"] == "SKILLS_CONSUMPTION_GAP"

    def test_skills_verdict_ok(self):
        from check_cross_stream_consumption import check_skills_consumption
        mainstream = self._make_mainstream("consumed")
        skills = self._make_skills(overhead=1, breadth=2)
        result = check_skills_consumption(mainstream, skills)
        assert result["verdict"] == "SKILLS_CONSUMPTION_OK"


class TestAccelerationConsumption:

    def _make_mainstream(self, acc_consumption="not_consumed"):
        return {
            "stream": "mainstream",
            "product_velocity_score": {"product_breadth_score": 2},
            "skills_consumption": "not_consumed",
            "acceleration_consumption": acc_consumption,
        }

    def _make_acceleration(self, breadth=1, ai_status="no_ai"):
        return {
            "stream": "acceleration",
            "product_velocity_score": {"product_breadth_score": breadth},
            "ai_output_status": ai_status,
        }

    def test_acceleration_no_ai_output_flag(self):
        from check_cross_stream_consumption import check_acceleration_consumption
        mainstream = self._make_mainstream("not_consumed")
        acceleration = self._make_acceleration(breadth=1, ai_status="no_ai")
        result = check_acceleration_consumption(mainstream, acceleration)
        assert "ACCELERATION_NO_AI_OUTPUT" in result["flags"]

    def test_acceleration_not_consumed_flag(self):
        from check_cross_stream_consumption import check_acceleration_consumption
        mainstream = self._make_mainstream("not_consumed")
        acceleration = self._make_acceleration(breadth=1, ai_status="ai_draft")
        result = check_acceleration_consumption(mainstream, acceleration)
        assert "MAINSTREAM_NOT_CONSUMING_ACCELERATION" in result["flags"]

    def test_acceleration_consumed_no_gap(self):
        from check_cross_stream_consumption import check_acceleration_consumption
        mainstream = self._make_mainstream("consumed")
        acceleration = self._make_acceleration(breadth=2, ai_status="ai_draft")
        result = check_acceleration_consumption(mainstream, acceleration)
        assert result["status"] == "consumed"
        assert result["action_required"] is False


class TestCrossStreamConsumptionIntegration:

    def test_replay_file_detects_gaps(self, tmp_path):
        from check_cross_stream_consumption import run
        replay = [
            {"stream": "mainstream", "sprint_id": "ms-r113",
             "product_velocity_score": {"product_breadth_score": 2, "machinery_overhead_score": 0},
             "skills_consumption": "not_consumed", "acceleration_consumption": "not_consumed",
             "false_pass_risk": "medium", "false_stop_risk": "low",
             "ai_output_status": "no_ai"},
            {"stream": "skills", "sprint_id": "sk-r113",
             "product_velocity_score": {"product_breadth_score": 0, "machinery_overhead_score": 2},
             "ai_output_status": "no_ai"},
            {"stream": "acceleration", "sprint_id": "ac-r112",
             "product_velocity_score": {"product_breadth_score": 1, "machinery_overhead_score": 1},
             "ai_output_status": "no_ai"},
        ]
        replay_path = tmp_path / "replay.json"
        replay_path.write_text(json.dumps(replay))
        exit_code = run(replay_path, tmp_path)
        assert exit_code == 0
        status_path = tmp_path / "cross-stream-consumption-status.json"
        assert status_path.exists()
        data = json.loads(status_path.read_text())
        assert data["overall_verdict"] == "CROSS_STREAM_CONSUMPTION_GAPS_DETECTED"
        assert "SKILLS_MISSING_PACKET" in data["all_flags"]
