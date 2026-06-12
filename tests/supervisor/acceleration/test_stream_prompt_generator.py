"""Tests for stream_prompt_generator.py — R102 Wave 1."""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor"))

from stream_prompt_generator import (
    generate_stream_prompt,
    generate_all_stream_prompts,
    STREAM_BOUNDARIES,
    STREAM_QUOTAS,
)


def _forecast(stream="mainstream"):
    return {
        "stream": stream,
        "forecast": [
            {"sprint_id": "R103", "planned_capabilities": ["api.save", "api.export"]},
            {"sprint_id": "R104", "planned_capabilities": ["api.edit"]},
            {"sprint_id": "R105", "planned_capabilities": []},
        ],
        "narrowness": {"is_narrow": False, "recommendation": "ok"},
    }


def _actions():
    return [
        {"action_type": "implement_capability", "target": "g1", "rationale": "FODS save needed"},
        {"action_type": "generate_handoff", "target": "g2", "rationale": "SYLK export needed"},
    ]


def test_generate_stream_prompt_has_sections():
    prompt = generate_stream_prompt("mainstream", _forecast(), _actions(), sprint_id="R103")
    assert "MAINSTREAM" in prompt
    assert "File Boundaries" in prompt
    assert "3-Sprint Forecast" in prompt
    assert "Hard Quota" in prompt
    assert "Priority Actions" in prompt
    assert "Anti-Skip Checks" in prompt
    assert "Self-Decision Rules" in prompt


def test_generate_stream_prompt_has_boundaries():
    prompt = generate_stream_prompt("mainstream", _forecast(), _actions())
    assert "src/net/" in prompt or "src/python/" in prompt


def test_generate_stream_prompt_acceleration():
    prompt = generate_stream_prompt("acceleration", _forecast("acceleration"), _actions())
    assert "tools/supervisor/" in prompt
    assert "src/net/" in prompt  # in forbidden


def test_generate_stream_prompt_narrow_warning():
    forecast = _forecast()
    forecast["narrowness"] = {"is_narrow": True, "recommendation": "Expand scope!"}
    prompt = generate_stream_prompt("mainstream", forecast, _actions())
    assert "WARNING" in prompt
    assert "Expand scope" in prompt


def test_generate_all_stream_prompts():
    forecasts = {s: _forecast(s) for s in STREAM_BOUNDARIES}
    actions = {s: _actions() for s in STREAM_BOUNDARIES}
    prompts = generate_all_stream_prompts(forecasts, actions, sprint_id="R103")
    assert len(prompts) == 4
    for stream in STREAM_BOUNDARIES:
        assert stream in prompts
        assert len(prompts[stream]) > 100


def test_stream_boundaries_complete():
    assert "mainstream" in STREAM_BOUNDARIES
    assert "acceleration" in STREAM_BOUNDARIES
    assert "skills" in STREAM_BOUNDARIES
    assert "supervisor" in STREAM_BOUNDARIES


def test_stream_quotas_complete():
    assert "mainstream" in STREAM_QUOTAS
    assert "acceleration" in STREAM_QUOTAS
    assert "skills" in STREAM_QUOTAS
    assert "supervisor" in STREAM_QUOTAS


def test_generate_stream_prompt_negative_empty_actions():
    """Negative: empty actions still produce valid prompt."""
    prompt = generate_stream_prompt("mainstream", _forecast(), [], sprint_id="R103")
    assert "MAINSTREAM" in prompt
    assert "Anti-Skip" in prompt
