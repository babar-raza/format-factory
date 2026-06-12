"""End-to-end route pipeline tests — 5-stage chain: classify→decide→write→validate→dispatch."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))

from tools.supervisor.autonomy_route_decider import (
    classify_task_category,
    decide_route,
    validate_route_decision,
    check_action_route_allowed,
)
from tools.supervisor.autonomy_route_models import TASK_CATEGORY_UNKNOWN


class TestE2ERoutePipeline:
    def test_product_task_full_pipeline(self, tmp_path):
        """Full 5-stage pipeline for a product task qualifies for autonomous execution."""
        # Stage 1: classify
        category = classify_task_category("Implement new gnumeric function")
        assert category == "PRODUCT_IMPLEMENTATION"

        # Stage 2: decide route (with required fields for autonomous acceleration)
        decision = decide_route(
            task_id="E2E-PROD-001",
            task_category=category,
            task_summary="Implement new gnumeric function",
            hints={
                "required_tests": ["tests/python/gnumeric/test_e2e.py"],
                "required_evidence": ["src/python/gnumeric/gnumeric_codec.py"],
                "allowed_paths": ["src/python/gnumeric/"],
            },
        )
        assert decision.final_route == "AUTONOMOUS_ACCELERATED_DEFAULT"
        assert decision.autonomous_allowed is True

        # Stage 3: write to disk
        written_path = decision.write(output_dir=tmp_path)
        assert written_path.exists()

        # Stage 4: validate the written decision
        import json
        loaded = json.loads(written_path.read_text(encoding="utf-8"))
        errors = validate_route_decision(loaded)
        assert errors == []

        # Stage 5: dispatch — action with matching route_decision_id is allowed
        action = {
            "action_id": "E2E-PROD-001",
            "task_id": "E2E-PROD-001",
            "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
            "task_category": "PRODUCT_IMPLEMENTATION",
            "route_decision_id": "E2E-PROD-001",
        }
        allowed, reason = check_action_route_allowed(action, decisions_dir=tmp_path)
        assert allowed is True, f"Expected allowed but got: {reason}"

    def test_machinery_task_blocked_without_decision(self, tmp_path):
        """Machinery task with no route decision on disk is blocked at dispatch."""
        # Stage 1: classify
        category = classify_task_category("Update autonomous_cycle orchestrator")
        assert category == "AUTONOMY_ORCHESTRATOR_MACHINERY"

        # Stage 2+3: skip decide_route — no decision written to disk

        # Stage 5: dispatch — machinery with no decision on disk → blocked
        action = {
            "action_id": "E2E-MACH-001",
            "task_id": "E2E-MACH-001",
            "action_type": "UPDATE_STATE",
            "task_category": category,
            "route_decision_id": "E2E-MACH-001",
        }
        allowed, reason = check_action_route_allowed(action, decisions_dir=tmp_path)
        assert allowed is False, f"Expected blocked but got: {reason}"
        assert "not found" in reason.lower() or "blocked" in reason.lower()

    def test_unknown_category_blocked(self, tmp_path):
        """Action with UNKNOWN_OR_AMBIGUOUS task category is blocked at dispatch."""
        action = {
            "action_id": "E2E-UNK-001",
            "task_id": "E2E-UNK-001",
            "action_type": "UPDATE_STATE",
            "task_category": TASK_CATEGORY_UNKNOWN,
        }
        allowed, reason = check_action_route_allowed(action, decisions_dir=tmp_path)
        assert allowed is False, f"Expected blocked but got: {reason}"
        assert "unknown" in reason.lower() or "ambiguous" in reason.lower() or "blocked" in reason.lower()
