"""R28 Lane D — AI end-to-end pilot tests."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.ai.pipeline.e2e_pilot import (
    PilotConfig,
    PilotResult,
    run_pilot,
    stage_1_load_chunks,
    stage_2_retrieval,
    stage_3_synthesis,
    stage_4_evaluate,
)


class TestE2EPilot:
    def test_full_pilot_fixture_mode(self):
        config = PilotConfig(format_id="fods", fixture_mode=True)
        result = run_pilot(config)
        assert result.format_id == "fods"
        assert result.final_authority_state == "ai_draft"
        assert "1_load_chunks" in result.stage_results
        assert "2_retrieval" in result.stage_results
        assert "3_synthesis" in result.stage_results
        assert "4_evaluation" in result.stage_results

    def test_stage_1_fixture_chunks(self):
        config = PilotConfig(format_id="fods", fixture_mode=True)
        chunks, errors = stage_1_load_chunks(config)
        assert len(chunks) == 3
        assert not errors
        assert all(c.format_id == "fods" for c in chunks)

    def test_stage_2_retrieval_returns_all(self):
        config = PilotConfig(fixture_mode=True)
        chunks, _ = stage_1_load_chunks(config)
        retrieved, meta = stage_2_retrieval(chunks)
        assert len(retrieved) == len(chunks)
        assert meta["mode"] == "fixture"

    def test_stage_3_synthesis_produces_valid(self):
        config = PilotConfig(format_id="fods", fixture_mode=True)
        chunks, _ = stage_1_load_chunks(config)
        result = stage_3_synthesis(chunks, config)
        assert result.is_valid
        assert result.authority_state.value == "ai_draft"

    def test_stage_4_evaluation_passes(self):
        config = PilotConfig(format_id="fods", fixture_mode=True)
        chunks, _ = stage_1_load_chunks(config)
        synthesis = stage_3_synthesis(chunks, config)
        eval_result = stage_4_evaluate(synthesis)
        assert eval_result["passed"]

    def test_pilot_never_escalates_authority(self):
        result = run_pilot(PilotConfig(fixture_mode=True))
        assert result.final_authority_state == "ai_draft"
        synth = result.stage_results.get("3_synthesis", {})
        assert synth.get("authority_state") == "ai_draft"

    def test_pilot_fodt_format(self):
        config = PilotConfig(format_id="fodt", fixture_mode=True)
        result = run_pilot(config)
        assert result.format_id == "fodt"
        assert result.stage_results["1_load_chunks"]["chunk_count"] == 3

    def test_pilot_result_to_dict(self):
        result = run_pilot(PilotConfig(fixture_mode=True))
        d = result.to_dict()
        assert "format_id" in d
        assert "stage_results" in d
        assert "final_authority_state" in d
        assert "all_stages_passed" in d
