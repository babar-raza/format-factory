"""Tests for stream_forecaster.py — R102 Wave 1."""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor"))

from stream_forecaster import forecast_stream, forecast_all_streams, detect_narrow_stream


def _gap(stream="mainstream", gap_id="g1", cap="api.save", priority=100):
    return {
        "stream": stream,
        "gap_id": gap_id,
        "capability_path": cap,
        "priority_score": priority,
    }


def test_forecast_stream_returns_3_sprints():
    gaps = [_gap(gap_id=f"g{i}", cap=f"api.cap{i}") for i in range(5)]
    result = forecast_stream("mainstream", gaps, sprint_base="R103")
    assert len(result["forecast"]) == 3


def test_forecast_stream_distributes_gaps():
    gaps = [_gap(gap_id=f"g{i}", cap=f"api.cap{i}") for i in range(7)]
    result = forecast_stream("mainstream", gaps, sprint_base="R103")
    total_planned = sum(len(s["planned_gaps"]) for s in result["forecast"])
    assert total_planned == 7


def test_forecast_empty_stream():
    result = forecast_stream("acceleration", [], sprint_base="R103")
    assert result["total_gaps"] == 0
    assert all(len(s["planned_gaps"]) == 0 for s in result["forecast"])


def test_detect_narrow_stream_narrow():
    """Positive: stream with 0 gaps is narrow."""
    result = detect_narrow_stream([], "acceleration", min_gaps=2)
    assert result["is_narrow"] is True
    assert "expanding" in result["recommendation"].lower() or "expand" in result["recommendation"].lower()


def test_detect_narrow_stream_adequate():
    """Negative: stream with enough gaps is not narrow."""
    gaps = [_gap(stream="mainstream", gap_id=f"g{i}") for i in range(5)]
    result = detect_narrow_stream(gaps, "mainstream", min_gaps=2)
    assert result["is_narrow"] is False


def test_detect_narrow_stream_boundary():
    """Boundary: exactly min_gaps is not narrow."""
    gaps = [_gap(stream="mainstream", gap_id=f"g{i}") for i in range(2)]
    result = detect_narrow_stream(gaps, "mainstream", min_gaps=2)
    assert result["is_narrow"] is False


def test_forecast_all_streams():
    gaps = [_gap(stream="mainstream"), _gap(stream="supervisor", gap_id="g2")]
    result = forecast_all_streams(gaps, sprint_base="R103")
    assert "mainstream" in result
    assert "acceleration" in result
    assert "skills" in result
    assert "supervisor" in result


def test_forecast_includes_narrowness():
    result = forecast_stream("mainstream", [_gap()])
    assert "narrowness" in result
