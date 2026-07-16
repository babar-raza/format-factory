"""Contract quality scorer (L30) — deterministic 0-100 score over 8 dimensions.

Identical contract + identical policy revision -> identical score (tested).
Scores are VOLATILE state (registry), never written into contract bodies.
Thresholds come from shared/format-contracts/policy/quality-policy.yaml:
below `blocking` the contract is not acceptable; below `review` it needs
independent review before use.

Exit codes: 0 scored (>= blocking) · 1 error · 4 below blocking threshold.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import contract_registry
import stores
from canonical_io import load_yaml

_DIM_WEIGHTS = {
    "source_coverage": 10,
    "format_specificity": 20,
    "depth_coverage": 15,
    "api_concreteness": 10,
    "validation_layer_coverage": 10,
    "security_coverage": 10,
    "test_specificity": 15,
    "provenance_strength": 10,
}


def _ratio(n: float, d: float) -> float:
    return 0.0 if d <= 0 else min(1.0, n / d)


def score_contract(doc: dict) -> dict:
    caps = doc.get("capabilities", [])
    must_caps = [c for c in caps if c.get("level") == "MUST"]
    dims: dict[str, float] = {}

    sources = doc.get("authoritative_sources", [])
    ok_sources = [s for s in sources
                  if s.get("authority_class") in ("AUTHORITATIVE", "VERIFIED_DERIVATION")
                  and s.get("acquisition_status") != "NEEDS_AUTHORITY"]
    dims["source_coverage"] = _ratio(len(ok_sources), max(1, len(sources)))

    specific = [c for c in caps
                if c.get("normative_rules")
                or any(p.startswith(("SAL-", "RF-")) for p in c.get("provenance", []))]
    dims["format_specificity"] = _ratio(len(specific), len(caps))

    deep = [c for c in must_caps if int(c.get("depth_required", 0)) >= 4]
    has_validate_depth = any(int(c.get("depth_required", 0)) >= 5 for c in caps)
    dims["depth_coverage"] = 0.7 * _ratio(len(deep), max(1, len(must_caps))) + (0.3 if has_validate_depth else 0.0)

    api = doc.get("public_api_contract") or {}
    op_count = sum(len(v) for v in api.values() if isinstance(v, list))
    dims["api_concreteness"] = _ratio(op_count, 6)

    layers = (doc.get("validation_contract") or {}).get("layers", [])
    dims["validation_layer_coverage"] = _ratio(len(layers), 4)

    sec = doc.get("security_contract") or {}
    sec_caps = [c for c in caps if c.get("category") == "security"]
    dims["security_coverage"] = (
        (0.4 if sec.get("attack_surfaces") else 0.0)
        + (0.3 if sec.get("safe_defaults") else 0.0)
        + (0.3 if sec_caps else 0.0)
    )

    test_lines = sum(len(c.get("required_tests", [])) for c in must_caps)
    dims["test_specificity"] = _ratio(test_lines, 1.5 * max(1, len(must_caps)))

    all_prov = [p for c in caps for p in c.get("provenance", [])]
    strong = [p for p in all_prov if p.startswith(("SAL-", "RF-"))]
    dims["provenance_strength"] = _ratio(len(strong), max(1, len(all_prov)) * 0.4)

    total = round(sum(_DIM_WEIGHTS[k] * v for k, v in dims.items()), 1)
    policy = stores.load_quality_policy()
    thresholds = policy["score_thresholds"]
    return {
        "score": total,
        "dimensions": {k: round(v, 3) for k, v in sorted(dims.items())},
        "policy_revision": policy.get("policy_revision"),
        "blocking_threshold": thresholds["blocking"],
        "review_threshold": thresholds["review"],
        "verdict": ("PASS" if total >= thresholds["review"]
                    else "NEEDS_REVIEW" if total >= thresholds["blocking"]
                    else "BLOCKED"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format-id", required=True)
    args = parser.parse_args(argv)
    fmt = args.format_id.lower()
    doc = load_yaml(stores.contract_path(fmt))
    if not doc:
        print(f"[fcl-score] ERROR no contract for {fmt}", file=sys.stderr)
        return 1
    report = score_contract(doc)
    contract_registry.update_entry(fmt, quality_score=report["score"],
                                   quality_verdict=report["verdict"],
                                   quality_policy_revision=report["policy_revision"])
    print(json.dumps(report, indent=2))
    return 0 if report["verdict"] != "BLOCKED" else 4


if __name__ == "__main__":
    sys.exit(main())
