"""Integration tests for autonomy routing — cross-module validation."""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))

from tools.supervisor.autonomy_route_models import (
    ALL_ROUTES,
    ALL_TASK_CATEGORIES,
    REQUIRED_DECISION_FIELDS,
    TASK_CATEGORIES_MACHINERY,
    TASK_CATEGORIES_PRODUCT,
)
from tools.supervisor.autonomy_route_decider import (
    decide_route,
    validate_route_decision,
    check_machinery_mutation_allowed,
)
from tools.supervisor.autonomy_route_ledger import (
    append_decision,
    read_ledger,
    get_decision_summary,
)


# ---------------------------------------------------------------------------
# Route schema validation
# ---------------------------------------------------------------------------

class TestRouteDecisionSchemaValidation:
    def test_schema_has_22_required_fields(self):
        schema_path = _REPO / "schemas" / "autonomy" / "execution-route.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        assert len(schema["required"]) == 21

    def test_schema_final_route_enum_matches_models(self):
        schema_path = _REPO / "schemas" / "autonomy" / "execution-route.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        schema_routes = set(schema["properties"]["final_route"]["enum"])
        assert schema_routes == ALL_ROUTES

    def test_schema_task_category_enum_matches_models(self):
        schema_path = _REPO / "schemas" / "autonomy" / "execution-route.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        schema_cats = set(schema["properties"]["task_category"]["enum"])
        assert schema_cats == ALL_TASK_CATEGORIES

    def test_product_mutation_evidence_schema_exists(self):
        schema_path = _REPO / "schemas" / "evidence" / "product-mutation-route-evidence.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        assert "mutation_id" in schema["required"]
        assert "route_decision_id" in schema["required"]


# ---------------------------------------------------------------------------
# Route ledger integration
# ---------------------------------------------------------------------------

class TestRouteLedger:
    def test_append_and_read(self, tmp_path, monkeypatch):
        ledger_path = tmp_path / "route-ledger.jsonl"
        monkeypatch.setattr(
            "tools.supervisor.autonomy_route_ledger.LEDGER_PATH", ledger_path
        )
        decision = {
            "task_id": "T-LEDGER-001",
            "task_category": "PRODUCT_IMPLEMENTATION",
            "final_route": "AUTONOMOUS_ACCELERATED_DEFAULT",
            "autonomous_allowed": True,
            "blocked": False,
            "reason": "test",
        }
        append_decision(decision)
        records = read_ledger()
        assert len(records) == 1
        assert records[0]["task_id"] == "T-LEDGER-001"

    def test_summary_counts(self, tmp_path, monkeypatch):
        ledger_path = tmp_path / "route-ledger.jsonl"
        monkeypatch.setattr(
            "tools.supervisor.autonomy_route_ledger.LEDGER_PATH", ledger_path
        )
        for i in range(3):
            append_decision({
                "task_id": f"T-SUM-{i}",
                "task_category": "PRODUCT_IMPLEMENTATION",
                "final_route": "AUTONOMOUS_ACCELERATED_DEFAULT",
            })
        append_decision({
            "task_id": "T-SUM-BLOCKED",
            "task_category": "UNKNOWN_OR_AMBIGUOUS",
            "final_route": "BLOCKED_UNSAFE_OR_UNCLASSIFIED",
        })
        summary = get_decision_summary()
        assert summary["total"] == 4
        assert summary["by_route"]["AUTONOMOUS_ACCELERATED_DEFAULT"] == 3
        assert summary["by_route"]["BLOCKED_UNSAFE_OR_UNCLASSIFIED"] == 1


# ---------------------------------------------------------------------------
# Machinery mutation check with disk-based decisions
# ---------------------------------------------------------------------------

class TestMachineryMutationWithDisk:
    def test_valid_decision_allows_mutation(self, tmp_path):
        decision = decide_route(
            "T-DISK-001", "SPEC_AUTHORITY_MACHINERY", "Update spec",
            hints={"governed_decision_present": True},
        )
        decision.write(output_dir=tmp_path)

        item = {
            "task_id": "T-DISK-001",
            "task_category": "SPEC_AUTHORITY_MACHINERY",
            "route_decision_id": "T-DISK-001",
        }
        allowed, reason = check_machinery_mutation_allowed(item, decisions_dir=tmp_path)
        assert allowed is True

    def test_missing_decision_blocks(self, tmp_path):
        item = {
            "task_id": "T-DISK-002",
            "task_category": "SPEC_AUTHORITY_MACHINERY",
            "route_decision_id": "NONEXISTENT",
        }
        allowed, reason = check_machinery_mutation_allowed(item, decisions_dir=tmp_path)
        assert allowed is False
        assert "not found" in reason

    def test_blocked_decision_blocks_mutation(self, tmp_path):
        decision = decide_route(
            "T-DISK-003", "UNKNOWN_OR_AMBIGUOUS", "Vague task",
        )
        decision.write(output_dir=tmp_path)

        item = {
            "task_id": "T-DISK-003",
            "task_category": "SPEC_AUTHORITY_MACHINERY",
            "route_decision_id": "T-DISK-003",
        }
        allowed, reason = check_machinery_mutation_allowed(item, decisions_dir=tmp_path)
        assert allowed is False


# ---------------------------------------------------------------------------
# Governance validator 11 integration
# ---------------------------------------------------------------------------

class TestGovernanceValidatorIntegration:
    def test_run_all_returns_11_validators(self):
        from tools.supervisor.governance_validators import run_all_governance_validators
        decl = {
            "planned_work_items": [{
                "item_id": "TEST-001",
                "item_type": "GOVERNANCE_DOC",
                "title": "Test doc",
                "status": "completed",
            }],
        }
        result = run_all_governance_validators(decl)
        assert len(result["validators"]) == 13  # 12 original + V13 spec_fact_refs (SAL-VH-001)
        validator_names = [v["validator"] for v in result["validators"]]
        assert "route_decision_required_validator" in validator_names

    def test_validator_11_current_run_blocks(self):
        """Current-run PRODUCT_SOURCE without route_decision_id now FAILs."""
        from tools.supervisor.governance_validators import run_all_governance_validators
        decl = {
            "planned_work_items": [{
                "item_id": "PS-INT-001",
                "item_type": "PRODUCT_SOURCE",
                "title": "Missing route decision",
                "status": "completed",
            }],
        }
        result = run_all_governance_validators(decl)
        v11 = [v for v in result["validators"] if v["validator"] == "route_decision_required_validator"][0]
        assert v11["result"] == "FAIL"
        assert v11["blocks_sprint"] is True


# ---------------------------------------------------------------------------
# Constants consistency
# ---------------------------------------------------------------------------

class TestConstantsConsistency:
    def test_all_routes_count(self):
        assert len(ALL_ROUTES) == 5

    def test_all_categories_count(self):
        assert len(ALL_TASK_CATEGORIES) == 13

    def test_product_and_machinery_disjoint(self):
        assert TASK_CATEGORIES_PRODUCT & TASK_CATEGORIES_MACHINERY == set()

    def test_required_fields_count(self):
        assert len(REQUIRED_DECISION_FIELDS) == 21


# ---------------------------------------------------------------------------
# Product mutation route evidence validation
# ---------------------------------------------------------------------------

class TestProductMutationEvidence:
    def test_valid_evidence_passes(self):
        from tools.supervisor.autonomy_route_decider import validate_product_mutation_evidence
        ev = {
            "mutation_id": "MUT-INT-001",
            "task_id": "T-INT-001",
            "route_decision_id": "T-INT-001",
            "authorized_route": "AUTONOMOUS_ACCELERATED_DEFAULT",
            "allowed_paths_used": ["src/python/dif/dif_parser.py"],
            "forbidden_paths_checked": ["tools/supervisor/"],
            "tests_proving_mutation": ["tests/python/dif/test_r156.py"],
            "supervisor_verdict_accepted": True,
            "run_id": "test-run",
            "timestamp": "2026-06-10T00:00:00Z",
        }
        errors = validate_product_mutation_evidence(ev)
        assert errors == []

    def test_evidence_validates_against_schema(self):
        schema_path = _REPO / "schemas" / "evidence" / "product-mutation-route-evidence.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        ev = {
            "mutation_id": "MUT-INT-002",
            "task_id": "T-INT-002",
            "route_decision_id": "T-INT-002",
            "authorized_route": "AUTONOMOUS_ACCELERATED_DEFAULT",
            "allowed_paths_used": ["src/python/dif/dif_parser.py"],
            "forbidden_paths_checked": [],
            "tests_proving_mutation": ["tests/python/dif/test_r156.py"],
        }
        for field in schema["required"]:
            assert field in ev, f"Missing {field}"


# ---------------------------------------------------------------------------
# Route-aware work item enrichment integration
# ---------------------------------------------------------------------------

class TestWorkItemEnrichmentIntegration:
    def test_enrichment_creates_route_decision_file(self, tmp_path):
        from tools.supervisor.autonomy_route_decider import enrich_work_item_with_route
        item = {
            "task_id": "T-ENRICH-INT-001",
            "task_summary": "Implement new gnumeric function",
            "required_tests": ["t.py"],
            "required_evidence": ["e.json"],
            "allowed_paths": ["src/python/gnumeric/"],
        }
        enriched = enrich_work_item_with_route(item, decisions_dir=tmp_path)
        assert enriched["executable"] is True
        assert (tmp_path / "T-ENRICH-INT-001.json").exists()
        loaded = json.loads((tmp_path / "T-ENRICH-INT-001.json").read_text())
        errors = validate_route_decision(loaded)
        assert errors == []

    def test_unclassified_item_not_executable(self):
        from tools.supervisor.autonomy_route_decider import enrich_work_item_with_route
        item = {
            "task_id": "T-ENRICH-INT-003",
            "task_summary": "completely unknown operation xyz qqq",
        }
        enriched = enrich_work_item_with_route(item)
        assert enriched["executable"] is False
        assert enriched["route_status"] == "ADVISORY_ONLY"


# ---------------------------------------------------------------------------
# Validator 11 FAIL vs WARN split integration
# ---------------------------------------------------------------------------

class TestValidator11Integration:
    def test_current_run_product_source_blocks_sprint(self):
        from tools.supervisor.governance_validators import run_all_governance_validators
        decl = {
            "planned_work_items": [{
                "item_id": "PS-V11-001",
                "item_type": "PRODUCT_SOURCE",
                "title": "Current-run product function",
                "status": "completed",
            }],
        }
        result = run_all_governance_validators(decl)
        v11 = [v for v in result["validators"] if v["validator"] == "route_decision_required_validator"][0]
        assert v11["result"] == "FAIL"
        assert v11["blocks_sprint"] is True

    def test_legacy_product_source_warns_only(self):
        from tools.supervisor.governance_validators import run_all_governance_validators
        decl = {
            "planned_work_items": [{
                "item_id": "PS-V11-002",
                "item_type": "PRODUCT_SOURCE",
                "title": "Legacy function",
                "status": "completed",
                "legacy_backfill_status": "BACKFILLED",
            }],
        }
        result = run_all_governance_validators(decl)
        v11 = [v for v in result["validators"] if v["validator"] == "route_decision_required_validator"][0]
        assert v11["result"] == "WARN"
        assert v11["blocks_sprint"] is False

    def test_routed_product_source_passes(self):
        from tools.supervisor.governance_validators import run_all_governance_validators
        decl = {
            "planned_work_items": [{
                "item_id": "PS-V11-003",
                "item_type": "PRODUCT_SOURCE",
                "title": "Routed product function",
                "status": "completed",
                "route_decision_id": "RD-V11-003",
            }],
        }
        result = run_all_governance_validators(decl)
        v11 = [v for v in result["validators"] if v["validator"] == "route_decision_required_validator"][0]
        assert v11["result"] == "PASS"


# ---------------------------------------------------------------------------
# Quarantine + Block Integration
# ---------------------------------------------------------------------------

class TestQuarantineIntegration:
    @staticmethod
    def _ensure_tools_path():
        _tools = _REPO / "tools" / "supervisor"
        if str(_tools) not in sys.path:
            sys.path.insert(0, str(_tools))

    def test_unsafe_prompt_fails_check9_and_quarantines(self, tmp_path):
        """Unsafe prompt fails Check 9 and writes a quarantine file."""
        self._ensure_tools_path()
        from tools.supervisor.validate_prompt_quality import validate_prompt_quality
        from tools.supervisor.autonomy_route_decider import quarantine_unsafe_prompt

        prompt = (
            "## Sprint Goal\n"
            "Implement the feature.\n\n"
            "## Steps\n"
            "1. Write the code.\n"
            "2. You must now run git push origin main to deploy.\n"
            "3. Verify results.\n"
        )
        result = validate_prompt_quality(prompt, "acceleration", has_advancement=True)
        assert result["valid"] is False

        check9 = next(
            (c for c in result["checks"] if c["check"] == "no_unauthorized_mutation_instructions"),
            None,
        )
        assert check9 is not None, "Check 9 not found in result"
        assert check9["pass"] is False

        qpath = quarantine_unsafe_prompt(prompt, reason="test-unsafe", quarantine_dir=tmp_path)
        md_files = list(tmp_path.glob("*.md"))
        assert len(md_files) == 1
        content = qpath.read_text(encoding="utf-8")
        assert "git push origin main" in content

    def test_safe_prompt_passes_check9(self, tmp_path):
        """Safe prompt passes Check 9 and does not quarantine."""
        self._ensure_tools_path()
        from tools.supervisor.validate_prompt_quality import validate_prompt_quality

        prompt = (
            "## Sprint Goal\n"
            "Implement the ABW codec function.\n\n"
            "## Steps\n"
            "1. Write src/python/abw/abw_codec.py.\n"
            "2. Add tests in tests/python/abw/.\n"
            "3. Run pytest.\n"
        )
        result = validate_prompt_quality(prompt, "acceleration", has_advancement=True)
        check9 = next(
            (c for c in result["checks"] if c["check"] == "no_unauthorized_mutation_instructions"),
            None,
        )
        assert check9 is not None
        assert check9["pass"] is True
        assert list(tmp_path.glob("*.md")) == []


# ---------------------------------------------------------------------------
# ImportError Fallback Path Test
# ---------------------------------------------------------------------------

class TestImportErrorFallback:
    def _write_action(self, tmp_path, action_type, task_category="", legacy=False):
        import json
        action = {
            "action_id": "IEF-001",
            "action_type": action_type,
            "objective": "test action",
            "preferred_backend": "LOCAL_DETERMINISTIC",
            "task_category": task_category,
            "legacy_backfill": legacy,
        }
        p = tmp_path / "action.json"
        p.write_text(json.dumps(action), encoding="utf-8")
        return str(p)

    def test_source_mutating_non_legacy_blocked_on_import_error(self, tmp_path):
        """Source-mutating non-legacy action is blocked when route decider cannot be imported."""
        import sys
        from tools.supervisor.next_action_runner import run_action

        action_path = self._write_action(tmp_path, "IMPLEMENT_SMALL_PRODUCT_FEATURE")
        saved = sys.modules.get("tools.supervisor.autonomy_route_decider")
        sys.modules["tools.supervisor.autonomy_route_decider"] = None  # type: ignore
        try:
            result = run_action(action_path)
        finally:
            if saved is not None:
                sys.modules["tools.supervisor.autonomy_route_decider"] = saved
            else:
                sys.modules.pop("tools.supervisor.autonomy_route_decider", None)

        assert result["status"] == "BLOCKED"
        assert "import" in result.get("block_reason", "").lower() or "route" in result.get("block_reason", "").lower()

    def test_categorized_non_legacy_blocked_on_import_error(self, tmp_path):
        """Categorized non-legacy machinery action is blocked when route decider import fails."""
        import sys
        from tools.supervisor.next_action_runner import run_action

        action_path = self._write_action(
            tmp_path, "UPDATE_STATE", task_category="SPEC_AUTHORITY_MACHINERY"
        )
        saved = sys.modules.get("tools.supervisor.autonomy_route_decider")
        sys.modules["tools.supervisor.autonomy_route_decider"] = None  # type: ignore
        try:
            result = run_action(action_path)
        finally:
            if saved is not None:
                sys.modules["tools.supervisor.autonomy_route_decider"] = saved
            else:
                sys.modules.pop("tools.supervisor.autonomy_route_decider", None)

        assert result["status"] == "BLOCKED"
        assert "import" in result.get("block_reason", "").lower() or "route" in result.get("block_reason", "").lower()

    def test_legacy_action_not_blocked_by_import_error(self, tmp_path):
        """Legacy action is not blocked by route decider ImportError (backward compat)."""
        import sys
        from tools.supervisor.next_action_runner import run_action

        action_path = self._write_action(
            tmp_path, "UPDATE_STATE", task_category="SPEC_AUTHORITY_MACHINERY", legacy=True
        )
        saved = sys.modules.get("tools.supervisor.autonomy_route_decider")
        sys.modules["tools.supervisor.autonomy_route_decider"] = None  # type: ignore
        try:
            result = run_action(action_path)
        finally:
            if saved is not None:
                sys.modules["tools.supervisor.autonomy_route_decider"] = saved
            else:
                sys.modules.pop("tools.supervisor.autonomy_route_decider", None)

        # Legacy action must NOT be blocked by route decider import failure
        block_reason = result.get("block_reason", "")
        assert "Route decider import failed" not in block_reason, (
            f"Legacy action was incorrectly blocked by import error: {block_reason}"
        )
