"""
generate_sample_outputs.py — Generate sample outputs for supervisor evidence packages.

Produces 5 required sample outputs:
1. sample-grades.json — Item grades from the current sprint
2. sample-continuation.json — Continuation signal state
3. sample-prompt.md — Generated next-worker prompt (truncated)
4. sample-wrong-stream-warning.json — Stream identity warning example
5. sample-replay.json — Package replay validation result

These are placed in <evidence_root>/sample-outputs/ for anti-skip verification.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def generate_sample_grades(review: dict[str, Any]) -> dict[str, Any]:
    """Generate a sample grades output from a review."""
    grades = review.get("item_grades", [])
    return {
        "sample_type": "grades",
        "generated_at": datetime.now().isoformat(),
        "overall_verdict": review.get("overall_verdict", "UNKNOWN"),
        "item_count": len(grades),
        "grades_summary": [
            {
                "item_id": g["item_id"],
                "grade": g["supervisor_grade"],
                "has_rework": bool(g.get("required_rework")),
            }
            for g in grades[:10]
        ],
        "accepted_count": len(review.get("accepted_items", [])),
        "rework_count": len(review.get("rework_items", [])),
    }


def generate_sample_continuation(signal: dict[str, Any]) -> dict[str, Any]:
    """Generate a sample continuation signal output."""
    return {
        "sample_type": "continuation",
        "generated_at": datetime.now().isoformat(),
        "autonomous_continue": signal.get("autonomous_continue", False),
        "continuation_state": signal.get("continuation_state", "UNKNOWN"),
        "iteration": signal.get("iteration", 0),
        "max_iterations": signal.get("max_iterations", 5),
        "hard_stops": signal.get("hard_stops_detected", []),
        "stop_reason": signal.get("stop_reason"),
    }


def generate_sample_prompt(prompt_text: str, max_lines: int = 30) -> dict[str, Any]:
    """Generate a sample prompt output (truncated)."""
    lines = prompt_text.split("\n")
    return {
        "sample_type": "prompt",
        "generated_at": datetime.now().isoformat(),
        "total_lines": len(lines),
        "truncated": len(lines) > max_lines,
        "first_lines": lines[:max_lines],
        "contains_stream_markers": any(
            m in prompt_text.lower()
            for m in ("supervisor", "mainstream", "acceleration", "skills")
        ),
    }


def generate_sample_wrong_stream_warning(
    target_stream: str,
    state_files_checked: list[str] | None = None,
    warnings_found: list[str] | None = None,
) -> dict[str, Any]:
    """Generate a sample wrong-stream warning output."""
    return {
        "sample_type": "wrong_stream_warning",
        "generated_at": datetime.now().isoformat(),
        "target_stream": target_stream,
        "state_files_checked": state_files_checked or [],
        "warnings_found": warnings_found or [],
        "is_clean": len(warnings_found or []) == 0,
    }


def generate_sample_replay(
    package_path: str,
    replay_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Generate a sample replay validation result."""
    return {
        "sample_type": "replay",
        "generated_at": datetime.now().isoformat(),
        "package_path": package_path,
        "replay_attempted": replay_result is not None,
        "replay_result": replay_result or {"status": "not_attempted", "reason": "no package available"},
    }


def generate_all_samples(
    output_dir: Path,
    review: dict[str, Any] | None = None,
    continuation_signal: dict[str, Any] | None = None,
    prompt_text: str = "",
    target_stream: str = "supervisor",
    package_path: str = "",
    replay_result: dict[str, Any] | None = None,
    state_files_checked: list[str] | None = None,
    stream_warnings: list[str] | None = None,
) -> list[Path]:
    """Generate all 5 sample outputs to the output directory.

    Returns list of written file paths.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    written = []

    # 1. Grades
    grades_data = generate_sample_grades(review or {})
    p = output_dir / "sample-grades.json"
    p.write_text(json.dumps(grades_data, indent=2), encoding="utf-8")
    written.append(p)

    # 2. Continuation
    cont_data = generate_sample_continuation(continuation_signal or {})
    p = output_dir / "sample-continuation.json"
    p.write_text(json.dumps(cont_data, indent=2), encoding="utf-8")
    written.append(p)

    # 3. Prompt
    prompt_data = generate_sample_prompt(prompt_text or "No prompt generated yet.")
    p = output_dir / "sample-prompt.json"
    p.write_text(json.dumps(prompt_data, indent=2), encoding="utf-8")
    written.append(p)

    # 4. Wrong-stream warning
    warning_data = generate_sample_wrong_stream_warning(
        target_stream, state_files_checked, stream_warnings
    )
    p = output_dir / "sample-wrong-stream-warning.json"
    p.write_text(json.dumps(warning_data, indent=2), encoding="utf-8")
    written.append(p)

    # 5. Replay
    replay_data = generate_sample_replay(package_path, replay_result)
    p = output_dir / "sample-replay.json"
    p.write_text(json.dumps(replay_data, indent=2), encoding="utf-8")
    written.append(p)

    return written
