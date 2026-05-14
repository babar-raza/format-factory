"""
lane_selector.py -- Phase R3 Deliverable (Lane C)

Deterministic lane selection based on format context state.

PURPOSE:
  Accept a format context (from format_context_resolver.py) and select the
  correct set of lanes from templates/commercial-sprint/lane-library.yaml.
  Returns a structured, JSON-serializable result indicating which lanes are
  applicable, blocked, or not-yet-applicable for the current format state.

STATE → LANE MAPPING:
  REQUIREMENTS_MISSING          → [LANE-R3, LANE-C, LANE-K]
  REQUIREMENTS_GENERATED_UNVERIFIED (files missing)  → [LANE-R3 (repair), LANE-C, LANE-K]
  REQUIREMENTS_GENERATED_UNVERIFIED (verifier fail)  → [LANE-R5 (rerun), LANE-C, LANE-K]
  REQUIREMENTS_VERIFIED_NO_IV   → [LANE-R5-IV (DEC-034 IV sprint), LANE-C, LANE-K]
  REQUIREMENTS_AUTHORITATIVE    → [LANE-I-LOAD, LANE-I-OBJECT-MODEL, LANE-I-EDIT,
                                    LANE-I-SAVE, LANE-I-TESTS, LANE-C, LANE-K]
  BLOCKED                       → [] (no lanes active; blocker must be resolved first)

ALLOWED:
  - Reading format context (dict or format_id string)
  - Deterministic state → lane mapping
  - Returning structured JSON-compatible result

NOT ALLOWED (governance boundary):
  - Autonomous execution
  - Gate self-approval
  - Prompt generation
  - Mutation of any file

Authority: AGENTS.md Section B, AF9-AF15 | GOVERNANCE.md 26.8-26.13
           templates/commercial-sprint/lane-library.yaml
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
LANE_LIBRARY_PATH = REPO_ROOT / "templates" / "commercial-sprint" / "lane-library.yaml"

# ---------------------------------------------------------------------------
# Lane definitions (stable; sourced from lane-library.yaml)
# ---------------------------------------------------------------------------

LANE_METADATA: dict[str, dict] = {
    "LANE-R3": {
        "name": "Requirements Generation",
        "type": "requirements",
        "phase": "R1",
        "purpose": "Synthesize format requirements from local sources.",
    },
    "LANE-R5": {
        "name": "Independent Verifier Challenge",
        "type": "verification",
        "phase": "R0",
        "purpose": "Adversarial challenge of generated requirements before implementation.",
    },
    "LANE-R5-IV": {
        "name": "DEC-034 Independent Verification",
        "type": "verification",
        "phase": "R0",
        "purpose": "Separate-session IV of verifier-reviewed requirements (DEC-034).",
    },
    "LANE-I-LOAD": {
        "name": "Load Pipeline Implementation",
        "type": "implementation",
        "phase": "R7",
        "capability_levels": ["C0", "C1", "C2", "C3"],
        "purpose": "Implement format loading: file → object model.",
    },
    "LANE-I-OBJECT-MODEL": {
        "name": "Object Model Implementation",
        "type": "implementation",
        "phase": "R7",
        "capability_levels": ["C4", "C5"],
        "purpose": "Implement format object model entities.",
    },
    "LANE-I-EDIT": {
        "name": "Edit Operations Implementation",
        "type": "implementation",
        "phase": "R7",
        "capability_levels": ["C6"],
        "purpose": "Implement mutation/edit operations.",
    },
    "LANE-I-SAVE": {
        "name": "Save Pipeline Implementation",
        "type": "implementation",
        "phase": "R7",
        "capability_levels": ["C7"],
        "purpose": "Implement format serialization: object model → file.",
    },
    "LANE-I-TESTS": {
        "name": "Test Suite Implementation",
        "type": "implementation",
        "phase": "R7",
        "capability_levels": ["C4", "C5", "C6", "C7"],
        "purpose": "Implement test coverage for all ACCEPTED_FOR_VERTICAL_SLICE requirements.",
    },
    "LANE-K": {
        "name": "AI Orchestration",
        "type": "orchestration",
        "phase": "all",
        "purpose": "AI accelerator coordination. AI is accelerator, NOT authority.",
    },
    "LANE-C": {
        "name": "Sprint Coordinator",
        "type": "coordinator",
        "phase": "all",
        "purpose": "Authority chain integrity, evidence contracts, state updates.",
    },
}

# Lanes that are always present regardless of state
ALWAYS_PRESENT = ["LANE-K", "LANE-C"]

# Implementation lanes (only when REQUIREMENTS_AUTHORITATIVE)
IMPLEMENTATION_LANES = [
    "LANE-I-LOAD",
    "LANE-I-OBJECT-MODEL",
    "LANE-I-EDIT",
    "LANE-I-SAVE",
    "LANE-I-TESTS",
]


def _load_lane_library() -> dict:
    """Load lane-library.yaml. Returns empty dict on failure."""
    try:
        import yaml
        return yaml.safe_load(LANE_LIBRARY_PATH.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def select_lanes(format_context: dict) -> dict:
    """
    Deterministically select applicable lanes based on format context.

    Parameters
    ----------
    format_context : dict
        Output of format_context_resolver.resolve_format_context().
        Must contain: format_id, requirements_state, gate_state, governance.

    Returns
    -------
    dict with:
      format_id: str
      requirements_state: str
      selected_lanes: list[str]   -- lane IDs to activate
      blocked_lanes: list[str]    -- lane IDs blocked (with reasons)
      lane_details: dict          -- per-lane metadata + reason
      blocker: str | None         -- overall blocker if any
      governance: dict            -- safety flags (always included)
      selector_version: str
    """
    fmt = format_context.get("format_id", "unknown")
    reqs_state = format_context.get("requirements_state", {})
    gate_state = format_context.get("gate_state", {})
    governance = format_context.get("governance", {})

    state = reqs_state.get("status", "REQUIREMENTS_MISSING")
    blocker_reason = reqs_state.get("blocker_reason")
    missing_files = reqs_state.get("missing_files", [])

    selected: list[str] = []
    blocked: list[str] = []
    lane_details: dict[str, dict] = {}

    def _add_lane(lane_id: str, reason: str):
        selected.append(lane_id)
        meta = LANE_METADATA.get(lane_id, {})
        lane_details[lane_id] = {**meta, "selection_reason": reason}

    def _block_lane(lane_id: str, reason: str):
        blocked.append(lane_id)
        meta = LANE_METADATA.get(lane_id, {})
        lane_details[lane_id] = {**meta, "blocked_reason": reason}

    # -----------------------------------------------------------------------
    # State-based lane selection
    # -----------------------------------------------------------------------

    if state == "REQUIREMENTS_MISSING":
        _add_lane("LANE-R3", "Requirements directory missing — generation required")
        for il in IMPLEMENTATION_LANES:
            _block_lane(il, "REQUIREMENTS_MISSING — requirements must be generated first")

    elif state == "REQUIREMENTS_GENERATED_UNVERIFIED":
        if missing_files:
            _add_lane(
                "LANE-R3",
                f"Requirements incomplete — missing files: {missing_files}",
            )
        else:
            # Files present but verifier failed or not run
            vr = reqs_state.get("verifier_result")
            _add_lane(
                "LANE-R5",
                f"All requirement files present but verifier result is {vr!r} — "
                "LANE_R5_PASS required",
            )
        for il in IMPLEMENTATION_LANES:
            _block_lane(
                il,
                f"REQUIREMENTS_GENERATED_UNVERIFIED — verifier review required first",
            )

    elif state == "REQUIREMENTS_VERIFIED_NO_IV":
        _add_lane(
            "LANE-R5-IV",
            "LANE_R5_PASS confirmed but DEC-034 IV not yet recorded — "
            "separate-session IV sprint required (AGENTS.md AF13)",
        )
        for il in IMPLEMENTATION_LANES:
            _block_lane(
                il,
                "REQUIREMENTS_VERIFIED_NO_IV — DEC-034 IV must be completed first (DEC-034)",
            )

    elif state == "REQUIREMENTS_AUTHORITATIVE":
        for il in IMPLEMENTATION_LANES:
            _add_lane(
                il,
                "REQUIREMENTS_AUTHORITATIVE — ready for implementation",
            )
        # Block R-lanes (requirements already authoritative)
        for rl in ["LANE-R3", "LANE-R5", "LANE-R5-IV"]:
            _block_lane(
                rl,
                "Requirements already AUTHORITATIVE — R-lanes not needed unless stale",
            )

    elif state == "BLOCKED":
        for il in IMPLEMENTATION_LANES:
            _block_lane(il, f"BLOCKED: {blocker_reason}")
        for rl in ["LANE-R3", "LANE-R5", "LANE-R5-IV"]:
            _block_lane(rl, f"BLOCKED: {blocker_reason}")

    else:
        for il in IMPLEMENTATION_LANES:
            _block_lane(il, f"Unknown state {state!r}")

    # Always-present lanes
    for lane_id in ALWAYS_PRESENT:
        _add_lane(lane_id, "Always active — all phases")

    # -----------------------------------------------------------------------
    # Critical constraint annotation on implementation lanes
    # -----------------------------------------------------------------------
    constraints = format_context.get("known_constraints", [])
    if constraints and state == "REQUIREMENTS_AUTHORITATIVE":
        for lane_id in IMPLEMENTATION_LANES:
            if lane_id in lane_details:
                lane_details[lane_id]["critical_constraints"] = constraints

    # -----------------------------------------------------------------------
    # Overall blocker
    # -----------------------------------------------------------------------
    overall_blocker = None
    if state == "BLOCKED":
        overall_blocker = blocker_reason
    elif state not in ("REQUIREMENTS_AUTHORITATIVE",):
        # Soft blocker — implementation not ready
        overall_blocker = (
            f"Implementation blocked: requirements state is {state!r}. "
            f"{blocker_reason or ''}"
        ).strip()

    return {
        "format_id": fmt,
        "requirements_state": state,
        "selected_lanes": selected,
        "blocked_lanes": blocked,
        "lane_details": lane_details,
        "blocker": overall_blocker,
        "governance": {
            "commercial_product_ready": False,
            "gate_self_approval_allowed": False,
            "autonomous_implementation_allowed": False,
        },
        "selector_version": "1.0",
    }


def select_lanes_for_format(fmt: str) -> dict:
    """
    Convenience wrapper: resolve format context then select lanes.

    Parameters
    ----------
    fmt : str
        Format ID (e.g. 'fods', 'fodt')

    Returns
    -------
    dict — same as select_lanes()
    """
    # Import here to avoid circular imports in test patching
    sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))
    from format_context_resolver import resolve_format_context
    ctx = resolve_format_context(fmt)
    return select_lanes(ctx)


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Lane selector — deterministic lane selection for format-factory skills"
    )
    parser.add_argument("format", nargs="?", default="all",
                        help="Format ID (fods, fodt) or 'all'")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    formats = ["fods", "fodt"] if args.format == "all" else [args.format]

    for fmt in formats:
        result = select_lanes_for_format(fmt)

        if args.json:
            print(json.dumps(result, indent=2))
            continue

        print(f"\n=== Lane Selection: {fmt.upper()} ===")
        print(f"  REQUIREMENTS_STATE: {result['requirements_state']}")
        print(f"  SELECTED_LANES:     {result['selected_lanes']}")
        print(f"  BLOCKED_LANES:      {result['blocked_lanes']}")
        if result.get("blocker"):
            print(f"  BLOCKER:            {result['blocker'][:100]}")
        print(f"  COMMERCIAL_READY:   {result['governance']['commercial_product_ready']}")


if __name__ == "__main__":
    main()
