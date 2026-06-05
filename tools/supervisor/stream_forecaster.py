"""Generate a 3-sprint forecast for each stream.

Examines current state (gaps, capabilities, lane history) and produces
a forward-looking plan for the next 3 sprints per stream.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent

STREAM_LABELS = ("mainstream", "acceleration", "skills", "supervisor")


def _load_json(path: Path) -> dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def _load_yaml(path: Path) -> dict[str, Any]:
    if path.exists():
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {}


def detect_narrow_stream(
    gaps: list[dict[str, Any]],
    stream: str,
    min_gaps: int = 2,
) -> dict[str, Any]:
    """Detect when a stream has too few gaps and needs scope expansion."""
    stream_gaps = [g for g in gaps if g.get("stream") == stream]
    is_narrow = len(stream_gaps) < min_gaps
    return {
        "stream": stream,
        "gap_count": len(stream_gaps),
        "is_narrow": is_narrow,
        "recommendation": (
            f"Stream '{stream}' has only {len(stream_gaps)} gaps. "
            "Consider expanding scope by adding capabilities from adjacent formats or tools."
            if is_narrow
            else f"Stream '{stream}' has {len(stream_gaps)} gaps — adequate scope."
        ),
    }


def forecast_stream(
    stream: str,
    gaps: list[dict[str, Any]],
    sprint_base: str = "R103",
) -> dict[str, Any]:
    """Generate a 3-sprint forecast for one stream."""
    stream_gaps = sorted(
        [g for g in gaps if g.get("stream") == stream],
        key=lambda g: -g.get("priority_score", 0),
    )

    sprints = []
    remaining = list(stream_gaps)

    for i in range(3):
        sprint_id = f"{sprint_base[:-3]}{int(sprint_base[-3:]) + i}" if sprint_base[-3:].isdigit() else f"{sprint_base}+{i}"
        batch = remaining[:3]
        remaining = remaining[3:]

        sprint_plan = {
            "sprint_id": sprint_id,
            "stream": stream,
            "planned_gaps": [g.get("gap_id", "") for g in batch],
            "planned_capabilities": [g.get("capability_path", "") for g in batch],
            "expected_tests": max(len(batch) * 8, 0),
            "expected_files_changed": max(len(batch) * 2, 0),
        }

        if not batch:
            sprint_plan["note"] = "No remaining gaps — stream may need scope expansion"

        sprints.append(sprint_plan)

    narrowness = detect_narrow_stream(gaps, stream)

    return {
        "stream": stream,
        "total_gaps": len(stream_gaps),
        "narrowness": narrowness,
        "forecast": sprints,
    }


def forecast_all_streams(
    gaps: list[dict[str, Any]],
    sprint_base: str = "R103",
) -> dict[str, Any]:
    """Generate forecasts for all streams."""
    forecasts = {}
    for stream in STREAM_LABELS:
        forecasts[stream] = forecast_stream(stream, gaps, sprint_base)
    return forecasts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gaps", type=Path, required=True)
    parser.add_argument("--sprint-base", default="R103")
    parser.add_argument("--stream", default=None)
    args = parser.parse_args()

    data = _load_json(args.gaps)
    gaps = data.get("selected_gaps", data if isinstance(data, list) else [])

    if args.stream:
        result = forecast_stream(args.stream, gaps, args.sprint_base)
    else:
        result = forecast_all_streams(gaps, args.sprint_base)

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
