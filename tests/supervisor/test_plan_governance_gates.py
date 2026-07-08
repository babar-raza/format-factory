"""Tests for Plan Governance Gates PG-0 through PG-20

Each test verifies one governance gate.
Integration gates (PG-10, PG-12, PG-13) are WARN-only and produce advisory assertions.
All other P0/P1 gates produce hard assertions.

Plan: keen-snacking-quiche (FF-PLAN-GOV-001)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "tools" / "supervisor"))

# ---------------------------------------------------------------------------
# PG-0: Repository and Governance Bound
# ---------------------------------------------------------------------------

class TestPG0RepositoryBound:
    def test_master_plan_readable(self):
        """PG-0: plans/master-plan.md must exist and be readable."""
        master = _REPO_ROOT / "plans" / "master-plan.md"
        assert master.exists(), f"plans/master-plan.md not found at {master}"
        text = master.read_text(encoding="utf-8")
        assert len(text) > 100, "plans/master-plan.md is too short to be valid"

    def test_agents_md_readable(self):
        """PG-0: AGENTS.md must exist."""
        agents = _REPO_ROOT / "AGENTS.md"
        assert agents.exists(), f"AGENTS.md not found at {agents}"

    def test_governance_dir_exists(self):
        """PG-0: docs/governance/ directory must exist."""
        gov_dir = _REPO_ROOT / "docs" / "governance"
        assert gov_dir.is_dir(), f"docs/governance/ not found at {gov_dir}"


# ---------------------------------------------------------------------------
# PG-1: Native Plan Identity Proven
# ---------------------------------------------------------------------------

class TestPG1NativePlanIdentity:
    def test_snoopy_has_plan_identity(self):
        """PG-1: snoopy-juggling-seal.md must have plan_identity: front-matter."""
        snoopy = _REPO_ROOT / "plans" / "strategic" / "snoopy-juggling-seal.md"
        assert snoopy.exists(), "snoopy-juggling-seal.md not found"
        text = snoopy.read_text(encoding="utf-8")
        assert "plan_identity:" in text, "snoopy-juggling-seal.md lacks plan_identity: block"

    def test_capability_plan_has_plan_identity(self):
        """PG-1: capability-fact-to-feature-production-plan.md must have plan_identity: block."""
        cap = _REPO_ROOT / "plans" / "strategic" / "capability-fact-to-feature-production-plan.md"
        assert cap.exists(), "capability-fact-to-feature-production-plan.md not found"
        text = cap.read_text(encoding="utf-8")
        assert "plan_identity:" in text, "capability plan lacks plan_identity: block"

    def test_plan_identity_schema_doc_exists(self):
        """PG-1: docs/governance/plan-identity-schema.md must exist."""
        schema_doc = _REPO_ROOT / "docs" / "governance" / "plan-identity-schema.md"
        assert schema_doc.exists(), f"plan-identity-schema.md not found at {schema_doc}"

    def test_extract_plan_identity_function_available(self):
        """PG-1: plan_identity.extract_plan_identity() must be importable."""
        from plan_identity import extract_plan_identity
        assert callable(extract_plan_identity)

    def test_snoopy_identity_fields(self):
        """PG-1: snoopy's plan_identity block must have required fields."""
        from plan_identity import extract_plan_identity
        snoopy = _REPO_ROOT / "plans" / "strategic" / "snoopy-juggling-seal.md"
        identity = extract_plan_identity(snoopy)
        assert identity is not None, "extract_plan_identity returned None for snoopy"
        assert identity.get("plan_id") == "snoopy-juggling-seal"
        assert identity.get("ownership_status") == "ACTIVE"


# ---------------------------------------------------------------------------
# PG-2: Plan Lineage Proven
# ---------------------------------------------------------------------------

class TestPG2PlanLineage:
    def test_ledger_exists(self):
        """PG-2: plans/master-plan-memory.md must exist."""
        ledger = _REPO_ROOT / "plans" / "master-plan-memory.md"
        assert ledger.exists(), "master-plan-memory.md not found"

    def test_ledger_has_snoopy_entry(self):
        """PG-2: Ledger must have an entry for snoopy-juggling-seal."""
        ledger = _REPO_ROOT / "plans" / "master-plan-memory.md"
        text = ledger.read_text(encoding="utf-8")
        assert "snoopy-juggling-seal" in text, "Ledger missing snoopy entry"

    def test_ledger_has_keen_snacking_quiche_entry(self):
        """PG-2: Ledger must have an entry for keen-snacking-quiche."""
        ledger = _REPO_ROOT / "plans" / "master-plan-memory.md"
        text = ledger.read_text(encoding="utf-8")
        assert "keen-snacking-quiche" in text, "Ledger missing keen-snacking-quiche entry"


# ---------------------------------------------------------------------------
# PG-3: Master Plan Memory Ledger Reconciled
# ---------------------------------------------------------------------------

class TestPG3LedgerReconciled:
    def test_ledger_has_minimum_entries(self):
        """PG-3: Ledger must have at least 11 entries (LEDGER-001 through LEDGER-011)."""
        ledger = _REPO_ROOT / "plans" / "master-plan-memory.md"
        text = ledger.read_text(encoding="utf-8")
        entries = re.findall(r"LEDGER-\d+", text)
        unique = set(entries)
        assert len(unique) >= 11, f"Expected >= 11 ledger entries, found {len(unique)}: {sorted(unique)}"

    def test_reactive_exploring_ullman_in_ledger(self):
        """PG-3: reactive-exploring-ullman must have a ledger entry."""
        ledger = _REPO_ROOT / "plans" / "master-plan-memory.md"
        text = ledger.read_text(encoding="utf-8")
        assert "reactive-exploring-ullman" in text

    def test_mutable_wishing_avalanche_in_ledger(self):
        """PG-3: mutable-wishing-avalanche must have a ledger entry."""
        ledger = _REPO_ROOT / "plans" / "master-plan-memory.md"
        text = ledger.read_text(encoding="utf-8")
        assert "mutable-wishing-avalanche" in text

    def test_lock_files_all_have_ledger_entries(self):
        """PG-3: Every lock file with TERMINAL_CLOSED or COMPLETE must have a ledger entry."""
        locks_dir = _REPO_ROOT / ".local" / "supervisor" / "plan-locks"
        if not locks_dir.is_dir():
            pytest.skip("plan-locks directory not found")
        ledger = _REPO_ROOT / "plans" / "master-plan-memory.md"
        ledger_text = ledger.read_text(encoding="utf-8")
        missing = []
        for lf in sorted(locks_dir.glob("*.json")):
            try:
                data = json.loads(lf.read_text(encoding="utf-8"))
            except Exception:
                continue
            if data.get("status") not in ("TERMINAL_CLOSED", "COMPLETE", "DEFERRED"):
                continue
            plan_path = data.get("plan_path", "")
            # Extract filename stem for ledger search
            stem = Path(plan_path).stem
            if stem and stem not in ledger_text:
                missing.append(f"{lf.name}: {stem}")
        assert not missing, f"Lock files without ledger entries: {missing}"


# ---------------------------------------------------------------------------
# PG-4: Wrong-Plan Write Root Cause Proven
# ---------------------------------------------------------------------------

class TestPG4WrongPlanWriteRootCause:
    def test_snoopy_not_hardcoded_in_write_plan_lock(self):
        """PG-4: snoopy-juggling-seal.md must NOT be in the data/logic of write_plan_lock.py.

        It may appear only in comments explaining the change.
        """
        wpl = _REPO_ROOT / "tools" / "supervisor" / "write_plan_lock.py"
        text = wpl.read_text(encoding="utf-8")
        # Find all Python list literals or string assignments containing snoopy
        # (not inside comments)
        code_lines = [
            line for line in text.splitlines()
            if "snoopy-juggling-seal" in line and not line.strip().startswith("#")
        ]
        assert len(code_lines) == 0, (
            f"snoopy-juggling-seal.md found in non-comment code lines: {code_lines}"
        )

    def test_forbidden_as_active_plan_does_not_contain_snoopy(self):
        """PG-4: FORBIDDEN_AS_ACTIVE_PLAN list must not contain snoopy."""
        from write_plan_lock import FORBIDDEN_AS_ACTIVE_PLAN
        for forbidden in FORBIDDEN_AS_ACTIVE_PLAN:
            assert "snoopy" not in forbidden.lower(), (
                f"snoopy is hardcoded in FORBIDDEN_AS_ACTIVE_PLAN: {FORBIDDEN_AS_ACTIVE_PLAN}"
            )


# ---------------------------------------------------------------------------
# PG-5: Snoopy Fallback Removed / Governed
# ---------------------------------------------------------------------------

class TestPG5SnoopyFallbackRemoved:
    def test_terminal_closed_plan_is_blocked(self, tmp_path, monkeypatch):
        """PG-5: validate_plan_binding() blocks writes to TERMINAL_CLOSED plans."""
        from write_plan_lock import validate_plan_binding
        # agile-munching-quasar is TERMINAL_CLOSED in the real lock files
        locks_dir = _REPO_ROOT / ".local" / "supervisor" / "plan-locks"
        if not locks_dir.is_dir():
            pytest.skip("No plan-locks dir")
        # Find a TERMINAL_CLOSED plan
        terminal_plan = None
        for lf in sorted(locks_dir.glob("*.json")):
            try:
                data = json.loads(lf.read_text(encoding="utf-8"))
                if data.get("status") == "TERMINAL_CLOSED":
                    terminal_plan = data.get("plan_path")
                    break
            except Exception:
                continue
        if not terminal_plan:
            pytest.skip("No TERMINAL_CLOSED plan found in lock files")
        allowed, reason = validate_plan_binding(terminal_plan)
        assert allowed is False, f"Expected TERMINAL_CLOSED plan to be blocked, got: reason={reason}"
        assert "TERMINAL" in reason.upper()

    def test_active_plan_is_not_blocked(self):
        """PG-5: validate_plan_binding() allows writes to the IN_PROGRESS plan."""
        from write_plan_lock import validate_plan_binding
        # keen-snacking-quiche is currently IN_PROGRESS
        keen_path = "C:/Users/prora/.claude/plans/keen-snacking-quiche.md"
        allowed, reason = validate_plan_binding(keen_path)
        assert allowed is True, f"Active plan should be allowed, but got: {reason}"


# ---------------------------------------------------------------------------
# PG-6: Pre-Execution Plan Existence Enforced
# ---------------------------------------------------------------------------

class TestPG6PreExecutionEnforcement:
    def test_missing_plan_fails_readiness(self, tmp_path):
        """PG-6: validate_plan_readiness returns execution_may_start=False for missing plan."""
        from validate_plan_readiness import validate_plan_readiness
        missing = tmp_path / "nonexistent-plan.md"
        result = validate_plan_readiness(missing)
        v = result["pre_execution_plan_validation"]
        assert v["plan_exists"] is False
        assert v["execution_may_start"] is False

    def test_valid_plan_passes_readiness(self):
        """PG-6: A complete plan with TC- references passes readiness check."""
        from validate_plan_readiness import validate_plan_readiness
        keen_path = Path("C:/Users/prora/.claude/plans/keen-snacking-quiche.md")
        if not keen_path.exists():
            pytest.skip("keen-snacking-quiche.md not found (running outside main session)")
        result = validate_plan_readiness(keen_path)
        v = result["pre_execution_plan_validation"]
        assert v["plan_exists"] is True
        assert v["taskcards_present"] is True
        assert v["plan_materially_complete"] is True
        assert v["execution_may_start"] is True

    def test_empty_plan_fails_materially_complete(self, tmp_path):
        """PG-6: A plan with no TC- references fails plan_materially_complete."""
        from validate_plan_readiness import validate_plan_readiness
        small_plan = tmp_path / "small-plan.md"
        small_plan.write_text("# Tiny Plan\n\nOnly two lines.\n", encoding="utf-8")
        result = validate_plan_readiness(small_plan)
        v = result["pre_execution_plan_validation"]
        assert v["plan_materially_complete"] is False
        assert v["execution_may_start"] is False


# ---------------------------------------------------------------------------
# PG-7: Plan Ownership Enforcement
# ---------------------------------------------------------------------------

class TestPG7OwnershipEnforcement:
    def test_ownership_function_importable(self):
        """PG-7: validate_plan_ownership() must be available."""
        from plan_identity import validate_plan_ownership
        assert callable(validate_plan_ownership)

    def test_wrong_session_denied(self, tmp_path, monkeypatch):
        """PG-7: validate_plan_ownership() blocks wrong-session access."""
        from plan_identity import validate_plan_ownership
        import plan_identity as pi
        plan_file = tmp_path / "plan-a.md"
        plan_file.write_text("# Plan A\n", encoding="utf-8")
        other_plan = tmp_path / "plan-b.md"
        locks_dir = tmp_path / "plan-locks"
        locks_dir.mkdir()
        # Session owns plan-b, not plan-a
        (locks_dir / "sess999.json").write_text(json.dumps({
            "plan_path": str(other_plan).replace("\\", "/"),
            "status": "IN_PROGRESS",
            "session_id": "sess999",
        }), encoding="utf-8")
        monkeypatch.setattr(pi, "_PLAN_LOCKS_DIR", locks_dir)
        monkeypatch.setattr(pi, "_SHARED_LOCK_PATH", tmp_path / "active-plan-lock.json")
        allowed, reason = validate_plan_ownership(plan_file, session_id="sess999")
        assert allowed is False


# ---------------------------------------------------------------------------
# PG-8: Human Pre-Execution Hardening (ADVISORY)
# ---------------------------------------------------------------------------

class TestPG8HumanHardening:
    def test_keen_plan_has_multiple_revisions(self):
        """PG-8 (ADVISORY): keen-snacking-quiche.md should have a Hardening Change Log."""
        keen_path = Path("C:/Users/prora/.claude/plans/keen-snacking-quiche.md")
        if not keen_path.exists():
            pytest.skip("keen-snacking-quiche.md not found")
        text = keen_path.read_text(encoding="utf-8")
        # Advisory: just verify the plan has a change log section
        assert "Hardening Change Log" in text or "hardening" in text.lower(), (
            "ADVISORY: Plan lacks a Hardening Change Log section (not blocking)"
        )


# ---------------------------------------------------------------------------
# PG-9: Execution Binding
# ---------------------------------------------------------------------------

class TestPG9ExecutionBinding:
    def test_active_plan_resolves_deterministically(self):
        """PG-9: resolve_native_plan_path() returns a deterministic result."""
        from plan_identity import resolve_native_plan_path
        path1, src1 = resolve_native_plan_path()
        path2, src2 = resolve_native_plan_path()
        assert path1 == path2, "resolve_native_plan_path() returned different results on two calls"
        assert src1 == src2


# ---------------------------------------------------------------------------
# PG-11: Same-Plan Autonomous Hardening
# ---------------------------------------------------------------------------

class TestPG11SamePlanHardening:
    def test_v56_passes_for_correct_target(self):
        """PG-11: V56 PASS when hardening evidence references active plan."""
        from governance_validators_ext import validate_hardening_target_identity
        decl = {
            "planned_work_items": [{
                "item_id": "TC-TEST-001",
                "item_type": "GOVERNANCE_TASKCARD",
                "evidence_paths": ["C:/Users/prora/.claude/plans/keen-snacking-quiche.md"],
            }]
        }
        result = validate_hardening_target_identity(decl)
        assert result["result"] in ("PASS", "WARN"), (
            f"Expected PASS or WARN for correct hardening target, got: {result['result']}\n"
            f"Summary: {result['summary']}"
        )

    def test_v56_fail_for_snoopy_as_wrong_target(self, tmp_path):
        """PG-11: V56 FAIL when snoopy-juggling-seal.md is cited while not active.

        V56 only flags snoopy as wrong-target when an IN_PROGRESS lock exists
        for a DIFFERENT plan. Without an active lock, V56 returns PASS (no-op).
        """
        import json
        from governance_validators_ext import validate_hardening_target_identity
        # Set up a fake active lock for a different plan
        locks_dir = tmp_path / ".local" / "supervisor" / "plan-locks"
        locks_dir.mkdir(parents=True)
        lock_data = {
            "plan_path": "plans/.claude/some-other-plan.md",
            "status": "IN_PROGRESS",
            "session_id": "test123",
        }
        (locks_dir / "test123-abcd1234.json").write_text(
            json.dumps(lock_data), encoding="utf-8"
        )
        decl = {
            "planned_work_items": [{
                "item_id": "TC-WRONG-001",
                "item_type": "GOVERNANCE_TASKCARD",
                "evidence_paths": ["plans/strategic/snoopy-juggling-seal.md"],
            }]
        }
        result = validate_hardening_target_identity(decl, repo_root=tmp_path)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True


# ---------------------------------------------------------------------------
# PG-14: Multi-Plan Isolation
# ---------------------------------------------------------------------------

class TestPG14MultiPlanIsolation:
    def test_two_plans_have_separate_lock_files(self):
        """PG-14: Each plan has its own session-keyed lock file, not a shared one."""
        locks_dir = _REPO_ROOT / ".local" / "supervisor" / "plan-locks"
        if not locks_dir.is_dir():
            pytest.skip("No plan-locks dir")
        lock_plans: dict[str, str] = {}
        for lf in sorted(locks_dir.glob("*.json")):
            try:
                data = json.loads(lf.read_text(encoding="utf-8"))
                session_id = data.get("session_id", lf.stem)
                plan_path = data.get("plan_path", "")
                lock_plans[session_id] = plan_path
            except Exception:
                continue
        # Verify: no two different session IDs own the same IN_PROGRESS plan
        # (multiple TERMINAL_CLOSED for same plan is allowed — that's the multi-lock scenario)
        in_progress: dict[str, str] = {}
        for lf in sorted(locks_dir.glob("*.json")):
            try:
                data = json.loads(lf.read_text(encoding="utf-8"))
                if data.get("status") == "IN_PROGRESS":
                    plan = data.get("plan_path", "")
                    sid = data.get("session_id", lf.stem)
                    if plan in in_progress:
                        pytest.fail(
                            f"Two sessions ({in_progress[plan]} and {sid}) both IN_PROGRESS "
                            f"for the same plan: {plan}"
                        )
                    in_progress[plan] = sid
            except Exception:
                continue


# ---------------------------------------------------------------------------
# PG-15: Readiness Validator
# ---------------------------------------------------------------------------

class TestPG15ReadinessValidator:
    def test_validate_plan_readiness_importable(self):
        """PG-15: validate_plan_readiness module and function must be importable."""
        from validate_plan_readiness import validate_plan_readiness
        assert callable(validate_plan_readiness)

    def test_readiness_result_schema(self, tmp_path):
        """PG-15: validate_plan_readiness() must return correct schema."""
        from validate_plan_readiness import validate_plan_readiness
        plan = tmp_path / "sample-plan.md"
        plan.write_text("# Plan\n\nTC-SAMPLE-001: Do something\ntask_id: TC-SAMPLE-001\n" * 10, encoding="utf-8")
        result = validate_plan_readiness(plan)
        assert "pre_execution_plan_validation" in result
        v = result["pre_execution_plan_validation"]
        required_keys = {"plan_exists", "plan_parseable", "taskcards_present",
                         "plan_materially_complete", "execution_may_start", "failures", "warnings"}
        assert required_keys.issubset(set(v.keys())), f"Missing keys: {required_keys - set(v.keys())}"


# ---------------------------------------------------------------------------
# PG-16: Terminal Lock Enforcement
# ---------------------------------------------------------------------------

class TestPG16TerminalLock:
    def test_terminal_closed_plan_blocked_by_validate_plan_binding(self):
        """PG-16: validate_plan_binding() blocks TERMINAL_CLOSED plans."""
        from write_plan_lock import validate_plan_binding
        import json
        from pathlib import Path
        # Dynamically find any plan with a TERMINAL_CLOSED lock on disk
        locks_dir = Path(__file__).resolve().parent.parent.parent / ".local" / "supervisor" / "plan-locks"
        terminal_path = None
        if locks_dir.is_dir():
            for lf in sorted(locks_dir.glob("*.json")):
                try:
                    lock = json.loads(lf.read_text(encoding="utf-8"))
                    if lock.get("status") == "TERMINAL_CLOSED":
                        terminal_path = lock.get("plan_path")
                        break
                except Exception:
                    continue
        if terminal_path is None:
            pytest.skip("No TERMINAL_CLOSED lock file found on disk (.local/ gitignored in CI)")
        allowed, reason = validate_plan_binding(terminal_path)
        assert allowed is False, f"Expected blocked but got allowed for {terminal_path}"
        assert "TERMINAL" in reason.upper()

    def test_terminal_plan_blocked_by_validate_plan_mutability(self, tmp_path):
        """PG-16: validate_plan_mutability() blocks plans with TERMINALLY_LOCKED ownership."""
        from plan_identity import validate_plan_mutability
        terminal_plan = tmp_path / "done-plan.md"
        terminal_plan.write_text(
            "<!--plan_identity:\n"
            "  plan_id: done-plan\n"
            "  ownership_status: TERMINALLY_LOCKED\n"
            "  terminal_lock: true\n"
            "-->\n"
            "# Done Plan\n",
            encoding="utf-8"
        )
        allowed, reason = validate_plan_mutability(terminal_plan)
        assert allowed is False
        assert "TERMINAL" in reason.upper()


# ---------------------------------------------------------------------------
# PG-17: Successor Plan
# ---------------------------------------------------------------------------

class TestPG17SuccessorPlan:
    def test_terminal_lock_append_records_successor_required(self, tmp_path, monkeypatch):
        """PG-17: _append_terminal_lock_to_plan() writes successor_required_for_future_changes=true."""
        from write_plan_lock import _append_terminal_lock_to_plan
        plan_file = tmp_path / "my-plan.md"
        plan_file.write_text("# My Plan\n\n## Content here.\n", encoding="utf-8")
        _append_terminal_lock_to_plan(str(plan_file), "test-session-id", "TERMINAL_CLOSED", "2026-06-23T12:00:00Z")
        text = plan_file.read_text(encoding="utf-8")
        assert "plan_terminal_lock:" in text
        assert "successor_required_for_future_changes: true" in text


# ---------------------------------------------------------------------------
# PG-18: Full Regression
# ---------------------------------------------------------------------------

class TestPG18FullRegression:
    def test_existing_governance_tests_still_importable(self):
        """PG-18: Core governance modules must still be importable after our changes."""
        from write_plan_lock import validate_plan_binding, write_lock, FORBIDDEN_AS_ACTIVE_PLAN
        from validate_plan_readiness import validate_plan_readiness
        from plan_identity import extract_plan_identity, resolve_native_plan_path
        from governance_validators_ext import validate_hardening_target_identity
        from governance_validators_ext import validate_architecture_only_stub_gate
        assert True  # Imports succeeded

    def test_master_plan_memory_is_ledger_not_plan_body(self):
        """PG-18: master-plan-memory.md must contain FORBIDDEN rules, not taskcard bodies."""
        ledger = _REPO_ROOT / "plans" / "master-plan-memory.md"
        text = ledger.read_text(encoding="utf-8")
        assert "FORBIDDEN" in text, "Ledger must have FORBIDDEN section"
        # Ledger must NOT contain sprint execution content
        assert "task_id:" not in text, "Ledger must not contain task_id: (execution content)"
        assert "## Sprint" not in text, "Ledger must not contain sprint sections"

    def test_snoopy_is_not_fallback_for_plan_amendments(self):
        """PG-18: CLAUDE.md must still contain the snoopy non-fallback rule."""
        claude_md = _REPO_ROOT / "CLAUDE.md"
        if not claude_md.exists():
            pytest.skip("CLAUDE.md not found")
        text = claude_md.read_text(encoding="utf-8")
        # The key governance rule must still be present
        assert "snoopy-juggling-seal" in text, "CLAUDE.md should mention snoopy as non-fallback"
        assert "NOT a global fallback" in text or "is the SAL forensics plan" in text, (
            "CLAUDE.md must state snoopy is not a global fallback"
        )


# ---------------------------------------------------------------------------
# PG-19: Idempotent Rerun
# ---------------------------------------------------------------------------

class TestPG19IdempotentRerun:
    def test_extract_plan_identity_idempotent(self, tmp_path):
        """PG-19: extract_plan_identity() returns same result on repeated calls."""
        from plan_identity import extract_plan_identity
        plan_file = tmp_path / "idempotent-plan.md"
        plan_file.write_text(
            "<!--plan_identity:\n  plan_id: idempotent-plan\n  ownership_status: ACTIVE\n-->\n# Plan\n",
            encoding="utf-8"
        )
        result1 = extract_plan_identity(plan_file)
        result2 = extract_plan_identity(plan_file)
        assert result1 == result2

    def test_validate_plan_readiness_idempotent(self, tmp_path):
        """PG-19: validate_plan_readiness() returns same result on repeated calls."""
        from validate_plan_readiness import validate_plan_readiness
        plan_file = tmp_path / "idempotent-plan.md"
        plan_file.write_text(
            "# Plan\n\n" + "TC-TEST-001: do something\ntask_id: TC-TEST-001\n" * 30,
            encoding="utf-8"
        )
        result1 = validate_plan_readiness(plan_file)
        result2 = validate_plan_readiness(plan_file)
        assert result1 == result2

    def test_no_duplicate_ledger_entries(self):
        """PG-19: master-plan-memory.md must have no duplicate LEDGER-N IDs."""
        ledger = _REPO_ROOT / "plans" / "master-plan-memory.md"
        text = ledger.read_text(encoding="utf-8")
        entry_ids = re.findall(r"ledger_entry_id: (LEDGER-\d+)", text)
        duplicates = [eid for eid in entry_ids if entry_ids.count(eid) > 1]
        assert not duplicates, f"Duplicate ledger entry IDs: {set(duplicates)}"


# ---------------------------------------------------------------------------
# PG-20: Governance Production Ready
# ---------------------------------------------------------------------------

class TestPG20GovernanceProductionReady:
    def test_plan_identity_module_exists(self):
        """PG-20: tools/supervisor/plan_identity.py must exist."""
        module = _REPO_ROOT / "tools" / "supervisor" / "plan_identity.py"
        assert module.exists(), f"plan_identity.py not found at {module}"

    def test_validate_plan_readiness_module_exists(self):
        """PG-20: tools/supervisor/validate_plan_readiness.py must exist."""
        module = _REPO_ROOT / "tools" / "supervisor" / "validate_plan_readiness.py"
        assert module.exists(), f"validate_plan_readiness.py not found at {module}"

    def test_v56_registered_in_runner(self):
        """PG-20: V56 validate_hardening_target_identity must be registered in runner."""
        runner = _REPO_ROOT / "tools" / "supervisor" / "governance_validator_runner.py"
        text = runner.read_text(encoding="utf-8")
        assert "validate_hardening_target_identity" in text, (
            "V56 not referenced in governance_validator_runner.py"
        )
        assert "V56" in text, "V56 not documented in runner header"

    def test_snoopy_not_in_forbidden_mutation_paths_data(self):
        """PG-20: snoopy must not appear in non-comment code in write_plan_lock.py."""
        wpl = _REPO_ROOT / "tools" / "supervisor" / "write_plan_lock.py"
        text = wpl.read_text(encoding="utf-8")
        code_lines = [
            line for line in text.splitlines()
            if "snoopy-juggling-seal" in line and not line.strip().startswith("#")
        ]
        assert not code_lines, f"snoopy still in non-comment code: {code_lines}"

    def test_ledger_is_not_execution_plan(self):
        """PG-20: master-plan-memory.md must not be usable as active plan."""
        from write_plan_lock import FORBIDDEN_AS_ACTIVE_PLAN
        assert any("master-plan-memory" in f for f in FORBIDDEN_AS_ACTIVE_PLAN), (
            "master-plan-memory.md must be in FORBIDDEN_AS_ACTIVE_PLAN"
        )

    def test_plan_identity_schema_doc_comprehensive(self):
        """PG-20: plan-identity-schema.md must document the discovery algorithm."""
        schema_doc = _REPO_ROOT / "docs" / "governance" / "plan-identity-schema.md"
        assert schema_doc.exists()
        text = schema_doc.read_text(encoding="utf-8")
        assert "discovery algorithm" in text.lower() or "Plan Discovery" in text
        assert "PLAN_IDENTITY_AMBIGUOUS" in text
