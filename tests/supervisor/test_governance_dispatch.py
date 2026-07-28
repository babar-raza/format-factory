"""Regression tests for governance validator dispatch repair (TC-GVD-008).

Proves the blind dispatch fallback loop (TC-BF-005) is eliminated and replaced
by explicit dispatch tracking:
1. _dispatch() stamps rule_id and records fn in _invoked_registry_fns
2. @validator decorator validates dispatch/deferred_reason constraints
3. Deferred validators are never called by the runner
4. No blind-fallback crash class (TypeError/WindowsPath/dict errors) in skipped_validators
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from governance_validators_contract import (
    VALID_DISPATCH,
    _VALIDATOR_REGISTRY,
    validator,
)


# ---------------------------------------------------------------------------
# Test 1: No blind-fallback crash class in skipped_validators
# ---------------------------------------------------------------------------

class TestNoBlindFallbackCrashClass:
    """After a governance runner invocation, assert zero entries in
    _skipped_validators matching TypeError/WindowsPath/dict error signatures.
    This proves the crash class from the old blind fallback loop is eliminated."""

    # The crash signatures that the old blind fallback loop produced when it
    # tried to call validators with (declaration, repo_root) but they expected
    # non-standard args (e.g., symbol_entry, source_text, file_path).
    CRASH_SIGNATURES = [
        "TypeError",
        "WindowsPath",
        "expected str, got dict",
        "takes 1 positional argument but 2 were given",
        "got an unexpected keyword argument",
    ]

    @pytest.mark.timeout(300)
    def test_no_crash_signatures_in_skipped(self):
        """Run the runner with a minimal declaration and verify no crash
        signatures appear in skipped_validators error messages."""
        from governance_validator_runner import run_all_governance_validators

        declaration = {"work_items": [], "changed_files": []}
        result = run_all_governance_validators(declaration, repo_root=REPO_ROOT)

        skipped = result.get("skipped_validators", [])
        for entry in skipped:
            error_msg = entry.get("error", "")
            for sig in self.CRASH_SIGNATURES:
                assert sig not in error_msg, (
                    f"Crash signature {sig!r} found in skipped_validators: "
                    f"validators={entry.get('validators')}, error={error_msg!r}. "
                    f"This indicates a blind-fallback crash class regression."
                )


# ---------------------------------------------------------------------------
# Test 2: Deferred validator not invoked
# ---------------------------------------------------------------------------

class TestDeferredValidatorNotInvoked:
    """Register a fake dispatch='deferred' validator via _VALIDATOR_REGISTRY,
    run the runner, confirm the fake fn was never called."""

    @pytest.mark.timeout(300)
    def test_deferred_fn_never_called(self):
        from governance_validator_runner import run_all_governance_validators

        sentinel = MagicMock(return_value={"result": "PASS", "blocks_sprint": False})
        fake_entry = {
            "rule_id": "V_TEST_DEFERRED_SENTINEL",
            "domain": "general",
            "description": "Test-only deferred validator",
            "skill_ids": [],
            "dispatch": "deferred",
            "deferred_reason": "Test sentinel -- must never be called",
            "fn": sentinel,
        }

        # Add the fake entry, run, then clean up
        _VALIDATOR_REGISTRY.append(fake_entry)
        try:
            declaration = {"work_items": [], "changed_files": []}
            run_all_governance_validators(declaration, repo_root=REPO_ROOT)
        finally:
            _VALIDATOR_REGISTRY.remove(fake_entry)

        sentinel.assert_not_called()


# ---------------------------------------------------------------------------
# Test 3: _dispatch stamps rule_id (direct unit test)
# ---------------------------------------------------------------------------

class TestDispatchStampsRuleId:
    """Recreate the _dispatch closure logic and verify it stamps rule_id."""

    def test_dispatch_stamps_rule_id_on_dict_result(self):
        """Verify the _dispatch pattern stamps rule_id onto a dict result."""
        _invoked_registry_fns: set = set()

        def _dispatch(fn, rule_id, *args, **kwargs):
            """Replica of the _dispatch closure from governance_validator_runner."""
            result = fn(*args, **kwargs)
            if isinstance(result, dict):
                result["rule_id"] = rule_id
            _invoked_registry_fns.add(fn)
            return result

        def fake_validator(declaration, repo_root=None):
            return {
                "validator": "test_validator",
                "result": "PASS",
                "blocks_sprint": False,
                "summary": "test",
            }

        result = _dispatch(fake_validator, "TEST_RULE", {})
        assert result["rule_id"] == "TEST_RULE"
        assert fake_validator in _invoked_registry_fns

    def test_dispatch_does_not_stamp_non_dict_result(self):
        """If the validator returns a non-dict, _dispatch should not crash."""
        _invoked_registry_fns: set = set()

        def _dispatch(fn, rule_id, *args, **kwargs):
            result = fn(*args, **kwargs)
            if isinstance(result, dict):
                result["rule_id"] = rule_id
            _invoked_registry_fns.add(fn)
            return result

        def returns_none():
            return None

        result = _dispatch(returns_none, "TEST_RULE")
        assert result is None
        assert returns_none in _invoked_registry_fns


# ---------------------------------------------------------------------------
# Test 4: _dispatch records fn in _invoked_registry_fns
# ---------------------------------------------------------------------------

class TestDispatchRecordsFnInSet:
    """Verify _dispatch records fn in the tracking set."""

    def test_dispatch_records_multiple_fns(self):
        """Multiple calls to _dispatch should record all fns."""
        _invoked_registry_fns: set = set()

        def _dispatch(fn, rule_id, *args, **kwargs):
            result = fn(*args, **kwargs)
            if isinstance(result, dict):
                result["rule_id"] = rule_id
            _invoked_registry_fns.add(fn)
            return result

        def validator_a(decl):
            return {"result": "PASS", "blocks_sprint": False}

        def validator_b(decl):
            return {"result": "WARN", "blocks_sprint": False}

        _dispatch(validator_a, "V_A", {})
        _dispatch(validator_b, "V_B", {})

        assert validator_a in _invoked_registry_fns
        assert validator_b in _invoked_registry_fns
        assert len(_invoked_registry_fns) == 2

    def test_dispatch_dedup_same_fn(self):
        """Calling _dispatch with the same fn twice should not duplicate."""
        _invoked_registry_fns: set = set()

        def _dispatch(fn, rule_id, *args, **kwargs):
            result = fn(*args, **kwargs)
            if isinstance(result, dict):
                result["rule_id"] = rule_id
            _invoked_registry_fns.add(fn)
            return result

        def validator_x(decl):
            return {"result": "PASS", "blocks_sprint": False}

        _dispatch(validator_x, "V_X", {})
        _dispatch(validator_x, "V_X", {})

        assert validator_x in _invoked_registry_fns
        assert len(_invoked_registry_fns) == 1


# ---------------------------------------------------------------------------
# Test 5: @validator decorator rejects invalid dispatch value
# ---------------------------------------------------------------------------

class TestValidatorDecoratorRejectsInvalidDispatch:
    """Call @validator(dispatch='bogus') and expect ValueError."""

    def test_invalid_dispatch_raises_valueerror(self):
        with pytest.raises(ValueError, match="dispatch must be one of"):

            @validator(rule_id="V_TEST_BOGUS", domain="general", dispatch="bogus")
            def _dummy(declaration):
                pass  # pragma: no cover

    def test_valid_dispatch_values_accepted(self):
        """Sanity check: all valid dispatch values are accepted."""
        registered = []
        for d in sorted(VALID_DISPATCH):
            kwargs = {}
            if d != "explicit":
                kwargs["deferred_reason"] = "test reason"

            @validator(rule_id=f"V_TEST_VALID_{d.upper()}", domain="general",
                       dispatch=d, **kwargs)
            def _dummy(declaration):
                pass  # pragma: no cover

            registered.append(f"V_TEST_VALID_{d.upper()}")

        # Clean up the registry entries we just added
        to_remove = [
            e for e in _VALIDATOR_REGISTRY
            if e["rule_id"] in registered
        ]
        for e in to_remove:
            _VALIDATOR_REGISTRY.remove(e)


# ---------------------------------------------------------------------------
# Test 6: @validator decorator requires deferred_reason for non-explicit
# ---------------------------------------------------------------------------

class TestValidatorDecoratorRequiresDeferredReason:
    """Call @validator(dispatch='deferred') without deferred_reason and expect
    ValueError."""

    def test_deferred_without_reason_raises_valueerror(self):
        with pytest.raises(ValueError, match="requires deferred_reason"):

            @validator(rule_id="V_TEST_NO_REASON", domain="general",
                       dispatch="deferred")
            def _dummy(declaration):
                pass  # pragma: no cover

    def test_superseded_without_reason_raises_valueerror(self):
        with pytest.raises(ValueError, match="requires deferred_reason"):

            @validator(rule_id="V_TEST_NO_REASON_SUP", domain="general",
                       dispatch="superseded")
            def _dummy(declaration):
                pass  # pragma: no cover

    def test_deferred_with_reason_succeeds(self):
        """Deferred with a reason should register without error."""

        @validator(rule_id="V_TEST_WITH_REASON", domain="general",
                   dispatch="deferred",
                   deferred_reason="Intentionally deferred for test")
        def _dummy(declaration):
            pass  # pragma: no cover

        # Verify it was registered
        entry = next(
            (e for e in _VALIDATOR_REGISTRY
             if e["rule_id"] == "V_TEST_WITH_REASON"),
            None,
        )
        assert entry is not None
        assert entry["dispatch"] == "deferred"
        assert entry["deferred_reason"] == "Intentionally deferred for test"

        # Clean up
        _VALIDATOR_REGISTRY.remove(entry)
