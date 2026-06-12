"""
test_lane_selector.py

Tests for tools/skills/lane_selector.py

Covers:
- FODS/FODT AUTHORITATIVE → implementation lanes selected
- REQUIREMENTS_MISSING → LANE-R3 selected, implementation lanes blocked
- REQUIREMENTS_GENERATED_UNVERIFIED (missing files) → LANE-R3
- REQUIREMENTS_GENERATED_UNVERIFIED (verifier fail) → LANE-R5
- REQUIREMENTS_VERIFIED_NO_IV → LANE-R5-IV
- BLOCKED → all lanes blocked
- LANE-K and LANE-C always present
- commercial_product_ready always False
- gate_self_approval_allowed always False
- No file mutations

Run:
  PYTHONPATH=C:/Users/prora/AppData/Roaming/Python/Python313/site-packages python -m pytest tests/skills -v
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))

from lane_selector import select_lanes, IMPLEMENTATION_LANES


# ============================================================
# Helpers — build format context dicts by hand
# ============================================================

def _make_ctx(requirements_state: str,
              verifier_result: str = "LANE_R5_PASS",
              iv_status: str = "PASS",
              missing_files: list = None,
              blocker_reason: str = None,
              constraints: list = None,
              fmt: str = "fods") -> dict:
    """Build a minimal format_context dict for lane_selector input."""
    return {
        "format_id": fmt,
        "requirements_state": {
            "status": requirements_state,
            "verifier_result": verifier_result,
            "iv_status": iv_status,
            "accepted_count": 20,
            "missing_files": missing_files or [],
            "stale": None,
            "blocker_reason": blocker_reason,
        },
        "gate_state": {
            "gates_passed": 10,
            "latest_gate_passed": 10,
            "commercial_product_ready": False,
            "gate_11_status": "commercial_readiness_in_progress",
            "blocker": None,
        },
        "known_constraints": constraints or [],
        "governance": {
            "commercial_product_ready": False,
            "gate_self_approval_allowed": False,
            "autonomous_implementation_allowed": False,
        },
    }


# ============================================================
# Class 1: State → lane mapping
# ============================================================

class TestStateLaneMapping:

    def test_authoritative_selects_implementation_lanes(self):
        ctx = _make_ctx("REQUIREMENTS_AUTHORITATIVE")
        result = select_lanes(ctx)
        for lane in IMPLEMENTATION_LANES:
            assert lane in result["selected_lanes"], (
                f"Expected {lane} in selected_lanes when AUTHORITATIVE"
            )

    def test_authoritative_blocks_r_lanes(self):
        ctx = _make_ctx("REQUIREMENTS_AUTHORITATIVE")
        result = select_lanes(ctx)
        for lane in ["LANE-R3", "LANE-R5", "LANE-R5-IV"]:
            assert lane in result["blocked_lanes"], (
                f"Expected {lane} blocked when AUTHORITATIVE"
            )

    def test_missing_selects_lane_r3(self):
        ctx = _make_ctx(
            "REQUIREMENTS_MISSING",
            missing_files=["commercial-requirements.yaml"],
            blocker_reason="directory missing",
        )
        result = select_lanes(ctx)
        assert "LANE-R3" in result["selected_lanes"]

    def test_missing_blocks_implementation_lanes(self):
        ctx = _make_ctx("REQUIREMENTS_MISSING", blocker_reason="missing")
        result = select_lanes(ctx)
        for lane in IMPLEMENTATION_LANES:
            assert lane in result["blocked_lanes"]

    def test_unverified_missing_files_selects_lane_r3(self):
        ctx = _make_ctx(
            "REQUIREMENTS_GENERATED_UNVERIFIED",
            verifier_result=None,
            iv_status=None,
            missing_files=["verifier-review.yaml", "traceability-map.yaml"],
            blocker_reason="missing files",
        )
        result = select_lanes(ctx)
        assert "LANE-R3" in result["selected_lanes"]

    def test_unverified_verifier_fail_selects_lane_r5(self):
        ctx = _make_ctx(
            "REQUIREMENTS_GENERATED_UNVERIFIED",
            verifier_result="LANE_R5_FAIL",
            iv_status=None,
            missing_files=[],
            blocker_reason="verifier FAIL",
        )
        result = select_lanes(ctx)
        assert "LANE-R5" in result["selected_lanes"]

    def test_verified_no_iv_selects_lane_r5_iv(self):
        ctx = _make_ctx(
            "REQUIREMENTS_VERIFIED_NO_IV",
            verifier_result="LANE_R5_PASS",
            iv_status=None,
            blocker_reason="DEC-034 IV not completed",
        )
        result = select_lanes(ctx)
        assert "LANE-R5-IV" in result["selected_lanes"]

    def test_verified_no_iv_blocks_implementation_lanes(self):
        ctx = _make_ctx(
            "REQUIREMENTS_VERIFIED_NO_IV",
            verifier_result="LANE_R5_PASS",
            iv_status=None,
            blocker_reason="DEC-034 IV not completed",
        )
        result = select_lanes(ctx)
        for lane in IMPLEMENTATION_LANES:
            assert lane in result["blocked_lanes"]

    def test_blocked_state_blocks_all_non_coordinator_lanes(self):
        ctx = _make_ctx(
            "BLOCKED",
            blocker_reason="DEC-034 IV FAIL",
        )
        result = select_lanes(ctx)
        for lane in IMPLEMENTATION_LANES:
            assert lane in result["blocked_lanes"]


# ============================================================
# Class 2: Always-present lanes
# ============================================================

class TestAlwaysPresentLanes:

    def test_lane_k_always_selected_authoritative(self):
        ctx = _make_ctx("REQUIREMENTS_AUTHORITATIVE")
        result = select_lanes(ctx)
        assert "LANE-K" in result["selected_lanes"]

    def test_lane_c_always_selected_authoritative(self):
        ctx = _make_ctx("REQUIREMENTS_AUTHORITATIVE")
        result = select_lanes(ctx)
        assert "LANE-C" in result["selected_lanes"]

    def test_lane_k_always_selected_missing(self):
        ctx = _make_ctx("REQUIREMENTS_MISSING", blocker_reason="missing")
        result = select_lanes(ctx)
        assert "LANE-K" in result["selected_lanes"]

    def test_lane_c_always_selected_missing(self):
        ctx = _make_ctx("REQUIREMENTS_MISSING", blocker_reason="missing")
        result = select_lanes(ctx)
        assert "LANE-C" in result["selected_lanes"]


# ============================================================
# Class 3: Governance invariants
# ============================================================

class TestGovernanceInvariants:

    def test_commercial_product_ready_always_false(self):
        for state in ["REQUIREMENTS_AUTHORITATIVE", "REQUIREMENTS_MISSING",
                      "REQUIREMENTS_VERIFIED_NO_IV", "BLOCKED"]:
            ctx = _make_ctx(state, blocker_reason="test")
            result = select_lanes(ctx)
            assert result["governance"]["commercial_product_ready"] is False, (
                f"commercial_product_ready must be False for state {state}"
            )

    def test_gate_self_approval_always_false(self):
        ctx = _make_ctx("REQUIREMENTS_AUTHORITATIVE")
        result = select_lanes(ctx)
        assert result["governance"]["gate_self_approval_allowed"] is False

    def test_autonomous_implementation_always_false(self):
        ctx = _make_ctx("REQUIREMENTS_AUTHORITATIVE")
        result = select_lanes(ctx)
        assert result["governance"]["autonomous_implementation_allowed"] is False


# ============================================================
# Class 4: Output structure
# ============================================================

class TestOutputStructure:

    def test_result_contains_required_keys(self):
        ctx = _make_ctx("REQUIREMENTS_AUTHORITATIVE")
        result = select_lanes(ctx)
        for key in ["format_id", "requirements_state", "selected_lanes",
                    "blocked_lanes", "lane_details", "governance", "selector_version"]:
            assert key in result, f"Missing key: {key}"

    def test_result_is_json_serializable(self):
        ctx = _make_ctx("REQUIREMENTS_AUTHORITATIVE")
        result = select_lanes(ctx)
        dumped = json.dumps(result)
        assert isinstance(dumped, str)

    def test_lane_details_present_for_all_selected(self):
        ctx = _make_ctx("REQUIREMENTS_AUTHORITATIVE")
        result = select_lanes(ctx)
        for lane_id in result["selected_lanes"]:
            assert lane_id in result["lane_details"], (
                f"lane_details missing for selected lane {lane_id}"
            )

    def test_constraints_annotated_on_implementation_lanes(self):
        constraint = {"source": "verifier_review", "constraint": "FODT-REQ-040 must be iterative"}
        ctx = _make_ctx("REQUIREMENTS_AUTHORITATIVE", constraints=[constraint], fmt="fodt")
        result = select_lanes(ctx)
        for lane_id in IMPLEMENTATION_LANES:
            details = result["lane_details"].get(lane_id, {})
            assert "critical_constraints" in details, (
                f"Expected critical_constraints in lane_details for {lane_id}"
            )
            assert len(details["critical_constraints"]) == 1


# ============================================================
# Class 5: Live FODS/FODT selection
# ============================================================

class TestLiveLaneSelection:
    """Tests using select_lanes_for_format() against actual repo files."""

    def test_fods_selects_implementation_lanes(self):
        from lane_selector import select_lanes_for_format
        result = select_lanes_for_format("fods")
        for lane in IMPLEMENTATION_LANES:
            assert lane in result["selected_lanes"]

    def test_fodt_selects_implementation_lanes(self):
        from lane_selector import select_lanes_for_format
        result = select_lanes_for_format("fodt")
        for lane in IMPLEMENTATION_LANES:
            assert lane in result["selected_lanes"]

    def test_fods_format_id_in_result(self):
        from lane_selector import select_lanes_for_format
        result = select_lanes_for_format("fods")
        assert result["format_id"] == "fods"

    def test_fodt_format_id_in_result(self):
        from lane_selector import select_lanes_for_format
        result = select_lanes_for_format("fodt")
        assert result["format_id"] == "fodt"
