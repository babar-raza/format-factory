"""Fail-closed contradiction gate for controller-state.yaml.

Detects disagreement between the promotion block, truth_boundary text,
and production_certifications count. Any inconsistency is a FAIL.

R3 of the production-system reconstruction plan.
Root cause: RC9 (controller-state unfalsifiable contradiction).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
STATE_PATH = REPO_ROOT / "plans" / "strategic" / "ff6" / "controller-state.yaml"

CERTIFIED = "CERTIFIED"
FORMAT_IDS = ("ipynb", "ora", "nrrd", "xliff", "safetensors", "ubl")


def validate(state_path: Path | None = None) -> dict:
    """Validate controller-state.yaml for internal consistency.

    Returns dict with 'valid' (bool), 'errors' (list of str), 'certified_by_promotion' (int).
    """
    state_path = state_path or STATE_PATH
    errors = []

    state = yaml.safe_load(state_path.read_text(encoding="utf-8"))

    promotion = state.get("promotion") or {}
    # production_certifications lives under current_gap_summary
    gap_summary = state.get("current_gap_summary") or {}
    prod_certs = gap_summary.get("production_certifications")
    # truth_boundary lives under acceleration_bootstrap
    accel = state.get("acceleration_bootstrap") or {}
    truth_boundary = accel.get("truth_boundary", "")

    # Count formats marked CERTIFIED in promotion block
    certified_count = sum(
        1 for fid in FORMAT_IDS
        if promotion.get(fid) == CERTIFIED
    )

    # Check 1: production_certifications must match promotion count
    if isinstance(prod_certs, int) and prod_certs != certified_count:
        errors.append(
            f"production_certifications ({prod_certs}) disagrees with "
            f"promotion block ({certified_count} CERTIFIED)"
        )

    # Check 2: truth_boundary must not contradict promotion
    if truth_boundary:
        tb_lower = truth_boundary.lower()
        # Look for "certification remains 0/6" type claims
        cert_match = re.search(r"certification\s+remains\s+(\d+)/(\d+)", tb_lower)
        if cert_match:
            tb_certified = int(cert_match.group(1))
            if tb_certified != certified_count:
                errors.append(
                    f"truth_boundary claims {tb_certified} certified but "
                    f"promotion block has {certified_count} CERTIFIED"
                )
        # Look for "UNASSESSED" claims
        if "unassessed" in tb_lower and certified_count > 0:
            errors.append(
                f"truth_boundary says products are UNASSESSED but "
                f"promotion block has {certified_count} CERTIFIED"
            )

    # Check 3: each format checkpoint's promotion_effect
    # Checkpoints are individual top-level keys like nrrd_checkpoint, xlf_checkpoint, etc.
    checkpoint_key_map = {
        "nrrd": "nrrd_checkpoint",
        "ipynb": "ipynb_checkpoint",
        "safetensors": "safetensors_checkpoint",
        "ubl": "ubl_checkpoint",
        "xliff": "xlf_checkpoint",
    }
    for fid, cp_key in checkpoint_key_map.items():
        cp = state.get(cp_key)
        if isinstance(cp, dict):
            effect = cp.get("promotion_effect")
            if effect == "none" and promotion.get(fid) == CERTIFIED:
                errors.append(
                    f"{cp_key} has promotion_effect=none but "
                    f"promotion block says {fid} is CERTIFIED"
                )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "certified_by_promotion": certified_count,
        "production_certifications": prod_certs,
    }


def main() -> int:
    result = validate()
    if result["valid"]:
        print("PASS: controller-state.yaml is internally consistent")
        print(f"  certified_by_promotion: {result['certified_by_promotion']}")
        print(f"  production_certifications: {result['production_certifications']}")
        return 0
    else:
        print("FAIL: controller-state.yaml has contradictions:")
        for error in result["errors"]:
            print(f"  - {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
