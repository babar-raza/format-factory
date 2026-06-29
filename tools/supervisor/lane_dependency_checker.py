"""Lane Dependency Checker — checks feature prerequisites against DOM maturity.

When a feature requires D4 but format is at D2, returns allowed=False.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPS_PATH = REPO_ROOT / "reports" / "dual-lane-deepening" / "lane-dependencies.yaml"
DEFAULT_LEDGER = REPO_ROOT / "registry" / "product-deepening-ledger.yaml"

_MATURITY_ORDER = {"D0": 0, "D1": 1, "D2": 2, "D3": 3, "D4": 4, "D5": 5}


def check_feature_prerequisites(
    feature_capability: str,
    format_name: str,
    ledger_path: Path | None = None,
) -> dict:
    """Check if a feature's DOM prerequisites are met.

    Returns {allowed, blocked_reason, required_dom_level}.
    """
    deps_path = DEPS_PATH
    if not deps_path.exists():
        return {"allowed": True, "reason": "no_dependency_graph"}

    deps = yaml.safe_load(deps_path.read_text(encoding="utf-8"))
    dep_list = deps.get("dependencies", [])

    # Find matching dependency
    match = None
    for dep in dep_list:
        if dep["feature_capability"] == feature_capability:
            if format_name.lower() in [f.lower() for f in dep.get("applicable_formats", [])]:
                match = dep
                break

    if match is None:
        return {"allowed": True, "reason": "no_dom_dependency_for_this_feature"}

    required_level = match["requires_dom_level"]
    required_val = _MATURITY_ORDER.get(required_level, 0)

    # Get current maturity from ledger
    path = ledger_path or DEFAULT_LEDGER
    if not path.exists():
        return {"allowed": True, "reason": "ledger_not_found"}

    ledger = yaml.safe_load(path.read_text(encoding="utf-8"))
    entry = next((e for e in ledger if e.get("format") == format_name.lower()
                  and e.get("runtime", "python") == "python"), None)

    if entry is None:
        return {"allowed": True, "reason": "format_not_in_ledger"}

    current = entry.get("lane_b_maturity", "D0")
    current_val = _MATURITY_ORDER.get(current, 0)

    if current_val >= required_val:
        return {"allowed": True, "current_dom_level": current,
                "required_dom_level": required_level}

    return {
        "allowed": False,
        "blocked_reason": f"{feature_capability} requires {required_level} but {format_name} is at {current}",
        "required_dom_level": required_level,
        "current_dom_level": current,
        "feature_capability": feature_capability,
        "format": format_name,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Lane Dependency Checker")
    parser.add_argument("--feature", required=True)
    parser.add_argument("--format", required=True)
    args = parser.parse_args()
    result = check_feature_prerequisites(args.feature, args.format)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["allowed"] else 1)
