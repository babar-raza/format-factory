"""Lane Selection Engine for dual-lane product deepening.

Reads ledger state and policies to determine which deepening lane
(feature or dom) should be worked next for a given format.

Implements all 7 execution modes:
  FEATURE_ONLY, DOM_ONLY, SEQUENTIAL_FEATURE_THEN_DOM,
  SEQUENTIAL_DOM_THEN_FEATURE, PARALLEL, BALANCED, AUTO
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LEDGER = REPO_ROOT / "registry" / "product-deepening-ledger.yaml"
DEFAULT_POLICIES = REPO_ROOT / ".supervisor" / "policies.yaml"
DEFAULT_STARVATION_THRESHOLD = 3

# Maturity ordinals for comparison
_MATURITY_ORDER = {"D0": 0, "D1": 1, "D2": 2, "D3": 3, "D4": 4, "D5": 5}
_LANE_A_ORDER = {"A0": 0, "A1": 1, "A2": 2, "A3": 3, "A4": 4, "A5": 5}


def _mat_val(level: str) -> int:
    return _MATURITY_ORDER.get(level, 0)


def _lane_a_val(level: str) -> int:
    return _LANE_A_ORDER.get(level, 0)


def _load_ledger(ledger_path: Path | None = None) -> list[dict]:
    path = ledger_path or DEFAULT_LEDGER
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _load_policies(policies_path: Path | None = None) -> dict:
    path = policies_path or DEFAULT_POLICIES
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data.get("dual_lane_deepening", {})


def _find_entry(ledger: list[dict], format_name: str) -> dict | None:
    fmt_lower = format_name.lower()
    for entry in ledger:
        if entry.get("format", "").lower() == fmt_lower and entry.get("runtime", "python") == "python":
            return entry
    # Fall back to any runtime match
    for entry in ledger:
        if entry.get("format", "").lower() == fmt_lower:
            return entry
    return None


def check_starvation(format_name: str, ledger_path: Path | None = None,
                     policies_path: Path | None = None) -> dict:
    """Check if a lane is being starved.

    Returns dict with starved_lane, consecutive_count, threshold, must_switch.
    """
    ledger = _load_ledger(ledger_path)
    policies = _load_policies(policies_path)
    entry = _find_entry(ledger, format_name)
    if entry is None:
        return {"error": f"Format '{format_name}' not found in ledger", "must_switch": False}

    global_threshold = policies.get("default_starvation_threshold", DEFAULT_STARVATION_THRESHOLD)
    threshold = entry.get("lane_starvation_threshold", global_threshold)
    a_consec = entry.get("lane_a_consecutive", 0)
    b_consec = entry.get("lane_b_consecutive", 0)
    mode = entry.get("execution_mode", "AUTO")
    b_maturity = _mat_val(entry.get("lane_b_maturity", "D0"))
    b_ceiling = _mat_val(entry.get("lane_b_ceiling", "D0"))
    dom_applicability = entry.get("dom_applicability", "FULL")

    result = {
        "format": format_name,
        "lane_a_consecutive": a_consec,
        "lane_b_consecutive": b_consec,
        "threshold": threshold,
        "starved_lane": None,
        "must_switch": False,
        "advisory_only": False,
    }

    # Determine which lane is starved
    if a_consec >= threshold:
        result["starved_lane"] = "dom"
        result["consecutive_count"] = a_consec
    elif b_consec >= threshold:
        result["starved_lane"] = "feature"
        result["consecutive_count"] = b_consec
    else:
        return result

    # Exceptions: at-ceiling or non-DOM format → can't switch to dom
    if result["starved_lane"] == "dom":
        if b_maturity >= b_ceiling or dom_applicability in ("FLAT", "METRICS_ONLY"):
            result["must_switch"] = False
            result["advisory_only"] = True
            return result

    # FEATURE_ONLY / DOM_ONLY → starvation is advisory only
    if mode in ("FEATURE_ONLY", "DOM_ONLY"):
        result["advisory_only"] = True
        return result

    result["must_switch"] = True
    return result


def select_lane(
    format_name: str,
    mode: str | None = None,
    ledger_path: Path | None = None,
    policies_path: Path | None = None,
) -> dict[str, Any]:
    """Select deepening lane for a format.

    Returns {selected_lane, mode, reason, starvation_warning}.
    """
    ledger = _load_ledger(ledger_path)
    entry = _find_entry(ledger, format_name)
    if entry is None:
        return {
            "error": f"Format '{format_name}' not found in ledger",
            "selected_lane": None,
            "mode": mode or "AUTO",
            "reason": "format_not_found",
        }

    effective_mode = mode or entry.get("execution_mode", "AUTO")
    dom_applicability = entry.get("dom_applicability", "FULL")
    b_maturity = _mat_val(entry.get("lane_b_maturity", "D0"))
    b_ceiling = _mat_val(entry.get("lane_b_ceiling", "D0"))
    a_maturity = _lane_a_val(entry.get("lane_a_maturity", "A0"))

    result: dict[str, Any] = {
        "format": format_name,
        "mode": effective_mode,
        "selected_lane": None,
        "reason": "",
        "starvation_warning": None,
    }

    # Non-DOM formats → always feature
    if dom_applicability in ("FLAT", "METRICS_ONLY"):
        result["selected_lane"] = "feature"
        result["reason"] = f"dom_not_applicable ({dom_applicability})"
        return result

    # At or beyond DOM ceiling → always feature
    if b_maturity >= b_ceiling:
        result["selected_lane"] = "feature"
        result["reason"] = f"at_dom_ceiling ({entry.get('lane_b_maturity')}>={entry.get('lane_b_ceiling')})"
        return result

    # Mode-specific logic
    if effective_mode == "FEATURE_ONLY":
        result["selected_lane"] = "feature"
        result["reason"] = "mode_feature_only"
        return result

    if effective_mode == "DOM_ONLY":
        result["selected_lane"] = "dom"
        result["reason"] = "mode_dom_only"
        return result

    if effective_mode == "SEQUENTIAL_FEATURE_THEN_DOM":
        # Feature until A maturity target met, then dom
        a_target = _lane_a_val("A3")  # default target
        if a_maturity >= a_target:
            result["selected_lane"] = "dom"
            result["reason"] = "sequential_feature_done_switching_to_dom"
        else:
            result["selected_lane"] = "feature"
            result["reason"] = "sequential_feature_phase"
        return result

    if effective_mode == "SEQUENTIAL_DOM_THEN_FEATURE":
        if b_maturity >= b_ceiling:
            result["selected_lane"] = "feature"
            result["reason"] = "sequential_dom_done_switching_to_feature"
        else:
            result["selected_lane"] = "dom"
            result["reason"] = "sequential_dom_phase"
        return result

    if effective_mode == "PARALLEL":
        result["selected_lane"] = ["feature", "dom"]
        result["reason"] = "parallel_both_lanes"
        return result

    if effective_mode == "BALANCED":
        a_consec = entry.get("lane_a_consecutive", 0)
        b_consec = entry.get("lane_b_consecutive", 0)
        if a_consec >= b_consec:
            result["selected_lane"] = "dom"
            result["reason"] = "balanced_alternation_dom_turn"
        else:
            result["selected_lane"] = "feature"
            result["reason"] = "balanced_alternation_feature_turn"
        # Check starvation
        starvation = check_starvation(format_name, ledger_path)
        if starvation.get("must_switch"):
            result["selected_lane"] = starvation["starved_lane"]
            result["reason"] = f"starvation_override_{starvation['starved_lane']}"
            result["starvation_warning"] = starvation
        return result

    # AUTO mode (default)
    # Compute gap-to-ceiling ratio for each lane
    b_gap = b_ceiling - b_maturity
    a_ceiling_val = _lane_a_val("A5")  # default ceiling
    a_gap = a_ceiling_val - a_maturity

    # Check starvation first
    starvation = check_starvation(format_name, ledger_path)
    if starvation.get("must_switch"):
        result["selected_lane"] = starvation["starved_lane"]
        result["reason"] = f"starvation_override_{starvation['starved_lane']}"
        result["starvation_warning"] = starvation
        return result

    if starvation.get("starved_lane"):
        result["starvation_warning"] = starvation

    # Select lane with larger gap ratio
    if b_gap > a_gap:
        result["selected_lane"] = "dom"
        result["reason"] = f"auto_dom_gap_larger (b_gap={b_gap} > a_gap={a_gap})"
    elif a_gap > b_gap:
        result["selected_lane"] = "feature"
        result["reason"] = f"auto_feature_gap_larger (a_gap={a_gap} > b_gap={b_gap})"
    else:
        # Equal gaps — prefer dom (it has less historical work)
        result["selected_lane"] = "dom"
        result["reason"] = f"auto_equal_gaps_prefer_dom (a_gap={a_gap} == b_gap={b_gap})"

    return result


def main():
    parser = argparse.ArgumentParser(description="Lane Selection Engine")
    parser.add_argument("--format", required=True, help="Format name (e.g., fods)")
    parser.add_argument("--mode", default=None, help="Override execution mode")
    parser.add_argument("--ledger", default=None, help="Path to product-deepening-ledger.yaml")
    parser.add_argument("--policies", default=None, help="Path to policies.yaml")
    parser.add_argument("--dry-run", action="store_true", help="Print result without side effects")
    parser.add_argument("--check-starvation", action="store_true", help="Only check starvation")
    args = parser.parse_args()

    ledger_path = Path(args.ledger) if args.ledger else None
    policies_path = Path(args.policies) if args.policies else None

    if args.check_starvation:
        result = check_starvation(args.format, ledger_path)
    else:
        result = select_lane(args.format, args.mode, ledger_path, policies_path)

    print(json.dumps(result, indent=2, default=str))
    return 0 if not result.get("error") else 1


if __name__ == "__main__":
    sys.exit(main())
