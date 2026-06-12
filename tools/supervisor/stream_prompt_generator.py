"""Generate stream-specific next prompts with forecasts, quotas, and anti-skip checks.

Each generated prompt includes:
- 3-sprint forecast for its stream
- Hard quota specific to the stream
- Self-decision rules
- Anti-skip checks
- Stream-specific file boundaries
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent

STREAM_BOUNDARIES = {
    "mainstream": {
        "allowed_src": ["src/net/", "src/python/"],
        "allowed_tests": ["tests/net/", "tests/python/"],
        "forbidden": ["tools/supervisor/"],
        "focus": "Product capability implementation: save, export, dogfood, package",
    },
    "acceleration": {
        "allowed_src": ["tools/supervisor/"],
        "allowed_tests": ["tests/supervisor/acceleration/"],
        "forbidden": ["src/net/", "src/python/"],
        "focus": "Acceleration tooling: gap selection, routing, handoff generation, learning",
    },
    "skills": {
        "allowed_src": [".claude/commands/", ".supervisor/skill-registry.yaml"],
        "allowed_tests": ["tests/supervisor/"],
        "forbidden": ["src/net/", "src/python/"],
        "focus": "Skill registry expansion: new governed skills, command templates",
    },
    "supervisor": {
        "allowed_src": ["tools/supervisor/"],
        "allowed_tests": ["tests/supervisor/"],
        "forbidden": ["src/net/", "src/python/"],
        "focus": "Supervisor pipeline: grading, materialization, continuation logic",
    },
}

STREAM_QUOTAS = {
    "mainstream": {
        "min_capabilities_implemented": 3,
        "min_tests_per_capability": 8,
        "required_package_proof": True,
        "required_capability_matrix_update": True,
    },
    "acceleration": {
        "min_tools_improved": 4,
        "min_tools_with_pos_neg_tests": 3,
        "min_sample_outputs": 3,
        "required_raw_logs": True,
    },
    "skills": {
        "min_skills_registered": 2,
        "min_skills_with_command_files": 2,
        "required_registry_validation": True,
    },
    "supervisor": {
        "min_pipeline_improvements": 2,
        "min_tests": 10,
        "required_dry_run": True,
    },
}


def generate_stream_prompt(
    stream: str,
    forecast: dict[str, Any],
    actions: list[dict[str, Any]],
    anti_skip_result: dict[str, Any] | None = None,
    sprint_id: str = "unknown",
) -> str:
    """Generate a markdown prompt for one stream."""
    boundaries = STREAM_BOUNDARIES.get(stream, STREAM_BOUNDARIES["mainstream"])
    quotas = STREAM_QUOTAS.get(stream, {})

    lines = [
        f"# Next Sprint Prompt: {stream.upper()} Stream",
        f"Sprint: {sprint_id}",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Focus",
        f"{boundaries['focus']}",
        "",
        "## File Boundaries",
        f"- Allowed source: {', '.join(boundaries['allowed_src'])}",
        f"- Allowed tests: {', '.join(boundaries['allowed_tests'])}",
        f"- Forbidden: {', '.join(boundaries['forbidden'])}",
        "",
        "## 3-Sprint Forecast",
    ]

    for sprint_plan in forecast.get("forecast", []):
        caps = ", ".join(sprint_plan.get("planned_capabilities", [])[:5]) or "(scope expansion needed)"
        lines.append(f"- **{sprint_plan['sprint_id']}**: {caps}")

    if forecast.get("narrowness", {}).get("is_narrow"):
        lines.append(f"\nWARNING: {forecast['narrowness']['recommendation']}")

    lines.extend(["", "## Hard Quota"])
    for key, value in quotas.items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Priority Actions"])
    for action in actions[:5]:
        lines.append(f"- [{action['action_type']}] {action.get('target', '')} — {action.get('rationale', '')}")

    lines.extend([
        "",
        "## Anti-Skip Checks",
        "Before closing this sprint, verify:",
        "- [ ] No stale selected gaps (sprint_id matches)",
        "- [ ] Raw test logs captured",
        "- [ ] No generic next prompt (stream-specific content required)",
        "- [ ] Test content verified (not path-only acceptance)",
    ])

    if anti_skip_result and anti_skip_result.get("violations", 0) > 0:
        lines.append(f"\nWARNING: {anti_skip_result['violations']} anti-skip violation(s) from prior sprint")

    lines.extend([
        "",
        "## Self-Decision Rules",
        "1. If all quota items met and tests pass -> PASS",
        "2. If quota partially met -> PARTIAL (list what's missing)",
        "3. If blocked by external gate -> BLOCKED (state gate)",
        "4. Continue-if-fast: if finished early, pick next action from forecast",
    ])

    return "\n".join(lines) + "\n"


def generate_all_stream_prompts(
    forecasts: dict[str, Any],
    all_actions: dict[str, list[dict[str, Any]]],
    anti_skip_result: dict[str, Any] | None = None,
    sprint_id: str = "unknown",
) -> dict[str, str]:
    """Generate prompts for all streams."""
    prompts = {}
    for stream in STREAM_BOUNDARIES:
        forecast = forecasts.get(stream, {"forecast": []})
        actions = all_actions.get(stream, [])
        prompts[stream] = generate_stream_prompt(
            stream, forecast, actions, anti_skip_result, sprint_id
        )
    return prompts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--forecasts", type=Path, required=True)
    parser.add_argument("--actions", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--sprint-id", default="unknown")
    args = parser.parse_args()

    forecasts = json.loads(args.forecasts.read_text(encoding="utf-8"))
    all_actions = json.loads(args.actions.read_text(encoding="utf-8"))

    prompts = generate_all_stream_prompts(forecasts, all_actions, sprint_id=args.sprint_id)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for stream, content in prompts.items():
        path = args.output_dir / f"next-{stream}-prompt.md"
        path.write_text(content, encoding="utf-8")
        print(f"Written: {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
