"""Select and rank product-factory POC gaps from the capability matrix."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml

from choose_skill_or_handoff import choose_skill_or_handoff


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
DEFAULT_MATRIX = REPO_ROOT / "product-capability-matrix" / "poc-targets.yaml"
DEFAULT_JSON = REPO_ROOT / ".local" / "supervisor" / "selected-product-gaps.json"
DEFAULT_REPORT = REPO_ROOT / "reports" / "supervisor" / "product-gap-selection.md"

GAP_STATUSES = {
    "GAP_DOGFOOD_EXTERNAL",
    "NOT_IMPLEMENTED",
    "NOT_STARTED",
    "NOT_YET",
    "PARTIAL",
    "R85_TARGET",
}

ACTION_SCORE = {
    "NOT_IMPLEMENTED": 100,
    "GAP_DOGFOOD_EXTERNAL": 95,
    "R85_TARGET": 90,
    "NOT_YET": 85,
    "PARTIAL": 80,
    "NOT_STARTED": 30,
}

DECISION_BONUS = {
    "GOVERNED_SKILL_REQUIRED": 20,
    "GOVERNED_HANDOFF_REQUIRED": 10,
    "EXTERNAL_GATE_ESCALATION": 0,
}


def _status_name(value: Any) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def _walk_statuses(value: Any, prefix: str = "") -> Iterable[tuple[str, str]]:
    if not isinstance(value, dict):
        return
    for key, child in value.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(child, dict):
            yield from _walk_statuses(child, path)
        elif _status_name(child) in GAP_STATUSES:
            yield path, _status_name(child)


def _gap(
    *,
    track: str,
    product: dict[str, Any],
    capability_path: str,
    current_status: str,
    description: str,
) -> dict[str, Any]:
    gap = {
        "product_track": track,
        "format": product["format"],
        "capability_path": capability_path,
        "current_status": current_status,
        "description": description,
    }
    decision = choose_skill_or_handoff(gap)
    base_score = ACTION_SCORE.get(current_status, 70)
    gap.update(decision)
    gap["poc_impact_score"] = base_score
    gap["priority_score"] = base_score + DECISION_BONUS[decision["decision"]]
    gap["gap_id"] = (
        f"{track}-{product['format']}-{capability_path}"
        .lower()
        .replace(".", "-")
        .replace("_", "-")
        .replace(" ", "-")
    )
    return gap


def select_gaps(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    """Return ranked gaps from confirmed commercial and reduced/FOSS products."""
    gaps: list[dict[str, Any]] = []
    for track, products in (
        ("commercial_net", matrix.get("commercial_net_products", [])),
        ("foss_reduced", matrix.get("foss_reduced_products", [])),
    ):
        for product in products:
            for path, status in _walk_statuses(product):
                gaps.append(
                    _gap(
                        track=track,
                        product=product,
                        capability_path=path,
                        current_status=status,
                        description=f"{product['format']} capability {path} is {status}.",
                    )
                )
            for index, blocker in enumerate(product.get("blockers", []), start=1):
                gaps.append(
                    _gap(
                        track=track,
                        product=product,
                        capability_path=f"blockers.{index}",
                        current_status="BLOCKED",
                        description=str(blocker),
                    )
                )
    return sorted(
        gaps,
        key=lambda item: (
            -item["priority_score"],
            item["product_track"],
            item["format"].lower(),
            item["capability_path"],
        ),
    )


def build_payload(matrix_path: Path, matrix: dict[str, Any]) -> dict[str, Any]:
    gaps = select_gaps(matrix)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_matrix": matrix_path.as_posix(),
        "matrix_version": matrix.get("poc_matrix_version"),
        "sprint": matrix.get("sprint"),
        "selection_policy": (
            "Rank POC capability impact first, then favor governed-skill execution over "
            "handoff; retain external gates as visible non-autonomous blockers."
        ),
        "selected_gap_count": len(gaps),
        "selected_gaps": gaps,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "---",
        "visibility: generated",
        "generated_by: codex",
        "---",
        "",
        "# Product Gap Selection",
        "",
        f"Source matrix: `{payload['source_matrix']}`",
        f"Selected gaps: {payload['selected_gap_count']}",
        "",
        "| Rank | Track | Format | Capability | Status | POC impact | Decision | Skill |",
        "|---:|---|---|---|---|---:|---|---|",
    ]
    for rank, gap in enumerate(payload["selected_gaps"], start=1):
        skill = gap["governed_skill"] or "-"
        lines.append(
            f"| {rank} | {gap['product_track']} | {gap['format']} | "
            f"`{gap['capability_path']}` | `{gap['current_status']}` | "
            f"{gap['poc_impact_score']} | `{gap['decision']}` | `{skill}` |"
        )
    lines.extend(
        [
            "",
            "External-gate entries remain visible but are not autonomous implementation work.",
            "",
        ]
    )
    return "\n".join(lines)


def write_selection(matrix_path: Path, json_path: Path, report_path: Path) -> dict[str, Any]:
    matrix = yaml.safe_load(matrix_path.read_text(encoding="utf-8")) or {}
    payload = build_payload(matrix_path, matrix)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(render_markdown(payload), encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank POC product gaps from the matrix.")
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    payload = write_selection(args.matrix, args.json_output, args.report_output)
    print(f"SELECTED_PRODUCT_GAPS: {payload['selected_gap_count']}")
    print(f"JSON_OUTPUT: {args.json_output}")
    print(f"REPORT_OUTPUT: {args.report_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
