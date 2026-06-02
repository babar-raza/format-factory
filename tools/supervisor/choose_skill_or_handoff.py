"""Classify a product gap for governed skill execution, handoff, or escalation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


EXTERNAL_GATE_TERMS = (
    "approval",
    "babar raza",
    "credential",
    "gate 8",
    "gate 11",
    "gate_11",
    "g11-g",
    "g11g",
    "publish",
    "push",
)

SKILL_RULES = (
    (
        "dogfood-export",
        ("dogfood", "export"),
        "governed-dogfood-export",
    ),
    (
        "dependency-resolution",
        ("dependency", "offline resolution"),
        "governed-dependency-resolution-review",
    ),
    (
        "capability-implementation",
        ("writer not implemented", "write_ppm"),
        "governed-product-capability-implementation",
    ),
    (
        "installed-workflow",
        ("installed_workflow", "installed workflow", "self-contained install"),
        "governed-installed-workflow-verification",
    ),
)


def _gap_text(gap: dict[str, Any]) -> str:
    values = (
        gap.get("capability_path", ""),
        gap.get("description", ""),
        gap.get("current_status", ""),
    )
    return " ".join(str(value).lower() for value in values)


def choose_skill_or_handoff(gap: dict[str, Any]) -> dict[str, Any]:
    """Return a deterministic governed execution decision for one normalized gap."""
    text = _gap_text(gap)
    if any(term in text for term in EXTERNAL_GATE_TERMS):
        return {
            "decision": "EXTERNAL_GATE_ESCALATION",
            "governed_skill": None,
            "handoff_required": True,
            "external_gate": True,
            "reason": "The gap requires human authority or an external action.",
        }

    for category, terms, skill in SKILL_RULES:
        if any(term in text for term in terms):
            return {
                "decision": "GOVERNED_SKILL_REQUIRED",
                "governed_skill": skill,
                "handoff_required": False,
                "external_gate": False,
                "reason": f"Repeatable {category} work must run through a governed skill.",
            }

    return {
        "decision": "GOVERNED_HANDOFF_REQUIRED",
        "governed_skill": None,
        "handoff_required": True,
        "external_gate": False,
        "reason": "No governed skill rule covers this product gap.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Choose governed skill execution or handoff for a normalized product gap."
    )
    parser.add_argument("--gap-json", type=Path, required=True)
    args = parser.parse_args()
    gap = json.loads(args.gap_json.read_text(encoding="utf-8"))
    print(json.dumps(choose_skill_or_handoff(gap), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
