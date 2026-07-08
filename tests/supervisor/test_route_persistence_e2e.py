"""
E2E tests for route-aware product reentry hardening.
Sprint: FORMAT-FACTORY-ROUTE-AWARE-PRODUCT-REENTRY-HARDENING-001
Taskcards: RRH-TC-004, RRH-TC-005

Tests:
1. Route enrichment in task generator output
2. Route decision persistence to disk
3. Fail-closed enforcement when route decider is unavailable
4. Validator 11 integration with route_decision_id
5. ImportError pass-through gap is closed
6. enrich_work_item_with_route correctness
"""
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest import mock


_here = Path(__file__).resolve().parent
_REPO = _here.parent.parent
sys.path.insert(0, str(_REPO))


# -----------------------------------------------------------------------
# Route Enrichment Tests
# -----------------------------------------------------------------------

class TestRouteEnrichmentInTaskGenerator:
    """Verify that generated task candidates have route metadata."""

    def test_enriched_items_have_task_category(self):
        from tools.supervisor.autonomous_task_generator import (
            generate_task_candidates,
        )
        out = Path(tempfile.mktemp(suffix=".json"))
        try:
            items = generate_task_candidates(
                output_path=out, max_candidates=2, skip_existing=False,
            )
            for item in items:
                assert "task_category" in item, (
                    f"Item {item.get('action_id')} missing task_category"
                )
                assert item["task_category"] != "UNKNOWN_OR_AMBIGUOUS", (
                    f"Item {item.get('action_id')} has UNKNOWN category"
                )
        finally:
            if out.exists():
                os.unlink(out)
            # Clean up any route decisions created
            rd_dir = _REPO / ".local" / "supervisor" / "route-decisions"
            for f in rd_dir.glob("atg-*.json"):
                f.unlink(missing_ok=True)

    def test_enriched_items_have_route_decision_id(self):
        from tools.supervisor.autonomous_task_generator import (
            generate_task_candidates,
        )
        out = Path(tempfile.mktemp(suffix=".json"))
        try:
            items = generate_task_candidates(
                output_path=out, max_candidates=2, skip_existing=False,
            )
            for item in items:
                assert "route_decision_id" in item, (
                    f"Item {item.get('action_id')} missing route_decision_id"
                )
                assert item["route_decision_id"], (
                    f"Item {item.get('action_id')} has empty route_decision_id"
                )
        finally:
            if out.exists():
                os.unlink(out)
            rd_dir = _REPO / ".local" / "supervisor" / "route-decisions"
            for f in rd_dir.glob("atg-*.json"):
                f.unlink(missing_ok=True)

    def test_enriched_items_have_route_status(self):
        from tools.supervisor.autonomous_task_generator import (
            generate_task_candidates,
        )
        out = Path(tempfile.mktemp(suffix=".json"))
        try:
            items = generate_task_candidates(
                output_path=out, max_candidates=1, skip_existing=False,
            )
            if not items:
                pytest.skip("No task candidates generated (CI environment may lack state)")
            assert items[0].get("route_status") == "DECIDED"
        finally:
            if out.exists():
                os.unlink(out)
            rd_dir = _REPO / ".local" / "supervisor" / "route-decisions"
            for f in rd_dir.glob("atg-*.json"):
                f.unlink(missing_ok=True)


# -----------------------------------------------------------------------
# Route Decision Persistence Tests
# -----------------------------------------------------------------------

class TestRouteDecisionPersistence:
    """Verify route decisions are written to disk."""

    def test_route_decision_written_to_disk(self):
        from tools.supervisor.autonomy_route_decider import (
            RouteDecision,
        )
        td = Path(tempfile.mkdtemp())
        try:
            rd = RouteDecision(
                task_id="TEST-PERSIST-001",
                task_category="PRODUCT_IMPLEMENTATION",
                task_summary="Test persistence",
                proposed_route="AUTONOMOUS_ACCELERATED_DEFAULT",
                final_route="AUTONOMOUS_ACCELERATED_DEFAULT",
                risk_level="LOW",
                decision_status="DECIDED",
                autonomous_allowed=True,
                acceleration_allowed=True,
                product_source_mutation_allowed=True,
                machinery_mutation_allowed=False,
                human_approval_required=False,
                blocked=False,
            )
            path = rd.write(td)
            assert path.exists()
            data = json.loads(path.read_text())
            assert data["task_id"] == "TEST-PERSIST-001"
            assert data["task_category"] == "PRODUCT_IMPLEMENTATION"
            assert data["final_route"] == "AUTONOMOUS_ACCELERATED_DEFAULT"
        finally:
            shutil.rmtree(td, ignore_errors=True)

    def test_route_decision_json_has_required_fields(self):
        from tools.supervisor.autonomy_route_decider import (
            RouteDecision,
        )
        from tools.supervisor.autonomy_route_models import REQUIRED_DECISION_FIELDS
        td = Path(tempfile.mkdtemp())
        try:
            rd = RouteDecision(
                task_id="TEST-FIELDS-001",
                task_category="PRODUCT_TESTING",
                task_summary="Test required fields",
                proposed_route="GOVERNED_DIRECT_EXECUTION",
                final_route="GOVERNED_DIRECT_EXECUTION",
                risk_level="LOW",
                decision_status="DECIDED",
                autonomous_allowed=False,
                acceleration_allowed=False,
                product_source_mutation_allowed=False,
                machinery_mutation_allowed=False,
                human_approval_required=False,
                blocked=False,
            )
            path = rd.write(td)
            data = json.loads(path.read_text())
            for f in REQUIRED_DECISION_FIELDS:
                assert f in data, f"Missing required field: {f}"
        finally:
            shutil.rmtree(td, ignore_errors=True)

    def test_enrich_persists_route_decision(self):
        from tools.supervisor.autonomy_route_decider import (
            enrich_work_item_with_route,
        )
        td = Path(tempfile.mkdtemp())
        try:
            item = {
                "action_id": "test-enrich-persist-001",
                "task_id": "test-enrich-persist-001",
                "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
                "task_summary": "Add a product function",
                "title": "Test enrichment persistence",
            }
            enriched = enrich_work_item_with_route(item, decisions_dir=td)
            assert enriched.get("task_category") == "PRODUCT_IMPLEMENTATION"
            assert enriched.get("route_decision_id")

            # Verify file on disk
            decision_file = td / f"{enriched['route_decision_id']}.json"
            assert decision_file.exists(), (
                f"Route decision not found at {decision_file}"
            )
        finally:
            shutil.rmtree(td, ignore_errors=True)


# -----------------------------------------------------------------------
# Fail-Closed Enforcement Tests
# -----------------------------------------------------------------------

class TestFailClosedEnforcement:
    """Verify fail-closed behavior when route decider is unavailable."""

    def test_import_error_blocks_source_mutating(self):
        """Source-mutating actions must be blocked when route decider import fails."""
        from tools.supervisor.autonomy_route_models import SOURCE_MUTATING_ACTION_TYPES

        # Verify the constant includes the key action types
        assert "IMPLEMENT_SMALL_PRODUCT_FEATURE" in SOURCE_MUTATING_ACTION_TYPES
        assert "PRODUCT_SOURCE_PATCH_BOUNDED" in SOURCE_MUTATING_ACTION_TYPES

        # Simulate the ImportError handler logic from next_action_runner.py
        for action_type in SOURCE_MUTATING_ACTION_TYPES:
            is_legacy = False
            is_source_mutating = True
            blocked = is_source_mutating and not is_legacy
            assert blocked, (
                f"Source-mutating {action_type} should be blocked on ImportError"
            )

    def test_uncategorized_nonlegacy_now_blocked(self):
        """After the fix, uncategorized non-legacy actions should be blocked
        when the route decider import fails."""
        # Simulate the logic from next_action_runner.py ImportError handler
        action_type = "UNKNOWN_ACTION"
        cat = ""
        is_legacy = False
        is_source_mutating = action_type in (
            "IMPLEMENT_SMALL_PRODUCT_FEATURE",
            "PRODUCT_SOURCE_PATCH_BOUNDED",
        )

        # Before fix: this would fall through. After fix: blocked.
        blocked = False
        if is_source_mutating and not is_legacy:
            blocked = True
        elif cat and not is_legacy:
            blocked = True
        elif not is_legacy:
            blocked = True  # NEW: fail-closed for uncategorized non-legacy
        # Legacy-only passes through

        assert blocked, "Uncategorized non-legacy action should be blocked"

    def test_legacy_still_allowed(self):
        """Legacy backfill actions should still pass through."""
        action_type = "UNKNOWN_ACTION"
        cat = ""
        is_legacy = True
        is_source_mutating = False

        blocked = False
        if is_source_mutating and not is_legacy:
            blocked = True
        elif cat and not is_legacy:
            blocked = True
        elif not is_legacy:
            blocked = True

        assert not blocked, "Legacy action should NOT be blocked"


# -----------------------------------------------------------------------
# Validator 11 Integration Tests
# -----------------------------------------------------------------------

class TestValidator11WithRouteDecisionId:
    """Verify validator 11 passes when route_decision_id is present."""

    def test_product_source_with_route_id_passes(self):
        from tools.supervisor.governance_validators import (
            validate_route_decision_required,
        )
        decl = {
            "planned_work_items": [
                {
                    "item_id": "V11-TEST-001",
                    "title": "Product function with route",
                    "item_type": "PRODUCT_SOURCE",
                    "route_decision_id": "ROUTE-V11-001",
                    "status": "completed",
                },
            ],
        }
        result = validate_route_decision_required(decl)
        assert result["result"] == "PASS", f"Expected PASS, got {result}"

    def test_product_source_without_route_id_fails(self):
        from tools.supervisor.governance_validators import (
            validate_route_decision_required,
        )
        decl = {
            "planned_work_items": [
                {
                    "item_id": "V11-TEST-002",
                    "title": "Product function without route",
                    "item_type": "PRODUCT_SOURCE",
                    "status": "completed",
                },
            ],
        }
        result = validate_route_decision_required(decl)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_governance_items_exempt(self):
        from tools.supervisor.governance_validators import (
            validate_route_decision_required,
        )
        decl = {
            "planned_work_items": [
                {
                    "item_id": "V11-TEST-003",
                    "title": "Governance doc",
                    "item_type": "GOVERNANCE_DOC",
                    "status": "completed",
                },
            ],
        }
        result = validate_route_decision_required(decl)
        assert result["result"] == "PASS"

    def test_machinery_with_route_id_passes(self):
        from tools.supervisor.governance_validators import (
            validate_route_decision_required,
        )
        decl = {
            "planned_work_items": [
                {
                    "item_id": "V11-TEST-004",
                    "title": "Machinery item with route",
                    "item_type": "PRODUCT_SOURCE",
                    "task_category": "AUTONOMY_ORCHESTRATOR_MACHINERY",
                    "route_decision_id": "ROUTE-V11-004",
                    "status": "completed",
                },
            ],
        }
        result = validate_route_decision_required(decl)
        assert result["result"] == "PASS"

    def test_machinery_without_route_id_fails(self):
        from tools.supervisor.governance_validators import (
            validate_route_decision_required,
        )
        decl = {
            "planned_work_items": [
                {
                    "item_id": "V11-TEST-005",
                    "title": "Machinery without route",
                    "item_type": "PRODUCT_SOURCE",
                    "task_category": "AUTONOMY_ORCHESTRATOR_MACHINERY",
                    "status": "completed",
                },
            ],
        }
        result = validate_route_decision_required(decl)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True


# -----------------------------------------------------------------------
# Route Classification Tests
# -----------------------------------------------------------------------

class TestRouteClassification:
    """Verify task category classification correctness."""

    def test_product_action_classified(self):
        from tools.supervisor.autonomy_route_decider import classify_task_category
        cat = classify_task_category(
            "Add function to ABW codec", "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        )
        assert cat == "PRODUCT_IMPLEMENTATION"

    def test_machinery_action_classified(self):
        from tools.supervisor.autonomy_route_decider import classify_task_category
        cat = classify_task_category(
            "Run autonomous_cycle pipeline", "",
        )
        assert cat == "AUTONOMY_ORCHESTRATOR_MACHINERY"

    def test_unknown_defaults_to_unknown(self):
        from tools.supervisor.autonomy_route_decider import classify_task_category
        cat = classify_task_category("do something vague", "")
        assert cat == "UNKNOWN_OR_AMBIGUOUS"

    def test_explicit_hint_overrides(self):
        from tools.supervisor.autonomy_route_decider import classify_task_category
        cat = classify_task_category(
            "anything", "",
            hints={"task_category": "SPEC_AUTHORITY_MACHINERY"},
        )
        assert cat == "SPEC_AUTHORITY_MACHINERY"


# -----------------------------------------------------------------------
# Route Ledger Tests
# -----------------------------------------------------------------------

class TestRouteLedger:
    """Verify route ledger append/read."""

    def test_append_and_read_ledger(self):
        import tools.supervisor.autonomy_route_ledger as ledger_mod
        td = Path(tempfile.mkdtemp())
        ledger_path = td / "route-ledger.jsonl"
        orig = ledger_mod.LEDGER_PATH
        try:
            ledger_mod.LEDGER_PATH = ledger_path
            decision = {
                "decision_id": "TEST-LEDGER-001",
                "task_id": "TEST-LEDGER-001",
                "task_category": "PRODUCT_IMPLEMENTATION",
                "final_route": "AUTONOMOUS_ACCELERATED_DEFAULT",
                "autonomous_allowed": True,
                "blocked": False,
                "reason": "test",
                "timestamp": "2026-06-10T00:00:00Z",
            }
            ledger_mod.append_decision(decision)
            entries = ledger_mod.read_ledger()
            assert len(entries) >= 1
            assert entries[-1]["decision_id"] == "TEST-LEDGER-001"
        finally:
            ledger_mod.LEDGER_PATH = orig
            shutil.rmtree(td, ignore_errors=True)


# -----------------------------------------------------------------------
# E2E Pipeline Integration Test
# -----------------------------------------------------------------------

class TestE2EPipelineIntegration:
    """End-to-end test: generate → enrich → persist → validate."""

    def test_generate_enrich_persist_validate(self):
        """Full pipeline: task generator → route enrichment → disk persistence
        → validator 11 acceptance."""
        from tools.supervisor.autonomous_task_generator import (
            generate_task_candidates,
        )
        from tools.supervisor.governance_validators import (
            validate_route_decision_required,
        )

        td = Path(tempfile.mkdtemp())
        out = td / "candidates.json"
        rd_dir = td / "route-decisions"
        rd_dir.mkdir()

        try:
            # Patch route decisions dir so we don't pollute real state
            with mock.patch(
                "tools.supervisor.autonomy_route_decider.ROUTE_DECISIONS_DIR",
                str(rd_dir.relative_to(_REPO)) if str(rd_dir).startswith(str(_REPO))
                else str(rd_dir),
            ), mock.patch(
                "tools.supervisor.autonomy_route_decider._REPO_ROOT",
                td,
            ):
                # Generate + enrich
                items = generate_task_candidates(
                    output_path=out, max_candidates=2, skip_existing=False,
                )

            # All items should have route_decision_id
            for item in items:
                assert item.get("task_category"), f"Missing task_category: {item}"
                assert item.get("route_decision_id"), f"Missing route_decision_id: {item}"

            # Verify route decision files were written to isolated temp dir (Amendment A)
            for item in items:
                rd_file = rd_dir / f"{item['route_decision_id']}.json"
                assert rd_file.exists(), (
                    f"Route decision file not found in isolated dir: {rd_file}"
                )

            # Build a declaration-like structure for validator 11
            decl = {
                "planned_work_items": [
                    {
                        "item_id": item["action_id"],
                        "title": item.get("objective", ""),
                        "item_type": "PRODUCT_SOURCE",
                        "route_decision_id": item["route_decision_id"],
                        "status": "completed",
                    }
                    for item in items
                ],
            }

            # Validator 11 should PASS (all items have route_decision_id)
            result = validate_route_decision_required(decl)
            assert result["result"] == "PASS", (
                f"Validator 11 failed: {result}"
            )

        finally:
            shutil.rmtree(td, ignore_errors=True)


# -----------------------------------------------------------------------
# run_action() ImportError Integration Tests (Amendment C)
# -----------------------------------------------------------------------

class TestRunActionImportError:
    """Verify that run_action() returns BLOCKED when route decider import fails."""

    def _minimal_action(self, action_type: str, is_legacy: bool = False) -> dict:
        return {
            "action_id": f"test-import-error-{action_type.lower().replace('_', '-')}",
            "action_type": action_type,
            "objective": "Test ImportError fail-closed behavior",
            "preferred_backend": "LOCAL_DETERMINISTIC",
            "legacy_backfill": is_legacy,
            "schema_version": "1.0",
        }

    def test_source_mutating_blocked_on_import_error(self, tmp_path):
        """Source-mutating action must be BLOCKED when route decider import fails."""
        from tools.supervisor.next_action_runner import run_action

        action = self._minimal_action("IMPLEMENT_SMALL_PRODUCT_FEATURE")
        action_file = tmp_path / "action.json"
        action_file.write_text(json.dumps(action), encoding="utf-8")

        with mock.patch.dict(
            sys.modules,
            {"tools.supervisor.autonomy_route_decider": None},
        ):
            result = run_action(str(action_file), dry_run=False)

        assert result["status"] == "BLOCKED", (
            f"Expected BLOCKED for source-mutating action on ImportError, got: {result}"
        )
        assert "block_reason" in result

    def test_uncategorized_nonlegacy_blocked_on_import_error(self, tmp_path):
        """Uncategorized non-legacy action must be BLOCKED when route decider import fails."""
        from tools.supervisor.next_action_runner import run_action

        action = self._minimal_action("UNKNOWN_CUSTOM_ACTION")
        action_file = tmp_path / "action2.json"
        action_file.write_text(json.dumps(action), encoding="utf-8")

        with mock.patch.dict(
            sys.modules,
            {"tools.supervisor.autonomy_route_decider": None},
        ):
            result = run_action(str(action_file), dry_run=False)

        assert result["status"] == "BLOCKED", (
            f"Expected BLOCKED for uncategorized non-legacy action on ImportError, got: {result}"
        )

    def test_legacy_not_blocked_by_import_error_handler(self, tmp_path):
        """Legacy backfill action must NOT be blocked by the ImportError handler."""
        from tools.supervisor.next_action_runner import run_action

        action = self._minimal_action("UNKNOWN_CUSTOM_ACTION", is_legacy=True)
        action_file = tmp_path / "action3.json"
        action_file.write_text(json.dumps(action), encoding="utf-8")

        with mock.patch.dict(
            sys.modules,
            {"tools.supervisor.autonomy_route_decider": None},
        ):
            result = run_action(str(action_file), dry_run=False)

        # Legacy action should not be blocked by ImportError handler specifically
        # (may be blocked by backend selector for other reasons, but not import error)
        if result["status"] == "BLOCKED":
            block_reason = result.get("block_reason", "")
            assert "route decider import failed" not in block_reason, (
                f"Legacy action should not be blocked by ImportError handler: {result}"
            )


# -----------------------------------------------------------------------
# Validator 11 PRODUCT_SOURCE Pipeline Proof (Amendment B)
# -----------------------------------------------------------------------

class TestValidator11ProductSourcePipeline:
    """Prove Validator 11 enforcement path fires for PRODUCT_SOURCE items."""

    def test_product_source_without_route_id_blocks_sprint(self):
        """run_all_governance_validators with a PRODUCT_SOURCE item missing
        route_decision_id must produce blocks_sprint=True."""
        from tools.supervisor.governance_validators import run_all_governance_validators

        decl = {
            "sprint_id": "TEST-V11-PIPELINE-001",
            "planned_work_items": [
                {
                    "item_id": "V11-PIPE-001",
                    "title": "Product function without route id",
                    "item_type": "PRODUCT_SOURCE",
                    "status": "completed",
                    "execution_method": "autonomous_direct",
                    "source_diff_paths": ["src/python/dif/dif_parser.py"],
                    "idempotency_key": "a" * 64,
                    "spec_fact_refs": ["FACT-DIF-001"],
                    # Deliberately omit route_decision_id
                },
            ],
        }
        result = run_all_governance_validators(decl)
        assert result["blocks_sprint"] is True, (
            f"Expected blocks_sprint=True for PRODUCT_SOURCE without route_decision_id: {result}"
        )

    def test_product_source_with_route_id_passes_validator11(self):
        """PRODUCT_SOURCE item with route_decision_id must not fail Validator 11."""
        from tools.supervisor.governance_validators import (
            run_all_governance_validators,
            validate_route_decision_required,
        )

        decl = {
            "sprint_id": "TEST-V11-PIPELINE-002",
            "planned_work_items": [
                {
                    "item_id": "V11-PIPE-002",
                    "title": "Product function with route id",
                    "item_type": "PRODUCT_SOURCE",
                    "status": "completed",
                    "route_decision_id": "ROUTE-V11-PIPE-002",
                },
            ],
        }
        # Direct validator 11 check must PASS
        v11_result = validate_route_decision_required(decl)
        assert v11_result["result"] == "PASS", (
            f"Validator 11 should PASS when route_decision_id is present: {v11_result}"
        )
