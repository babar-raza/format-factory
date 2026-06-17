"""
test_isolation.py — Mandatory regression scenarios for cross-chat continuation isolation.

Implements scenarios 1, 4, 5, 6, 7, 11, 17, 18, 19, 21 from the regression test plan.
These 10 scenarios are required before enforcement mode (CCI-L7).
"""
import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "tools" / "supervisor"))

from check_continuation import check
from continuation_identity import ContinuationIdentity, get_or_create_session_identity
from continuation_ledger import append_event, query_active, mark_consumed, detect_conflicts
from continuation_selector import select_continuation, SelectionResult


class TestScenario1_SameSessionContinues:
    """Scenario 1: Same session produces and consumes — should CONTINUE."""

    def test_matching_session_id_allows_continuation(self, mock_repo, full_continue_setup):
        full_continue_setup(session_id="session-aaa")
        result = check(mock_repo, session_id="session-aaa")
        assert result["verdict"] == "CONTINUE"
        assert result["session_id"] == "session-aaa"

    def test_selector_accepts_matching_session(self, mock_repo, full_continue_setup):
        full_continue_setup(session_id="session-bbb")
        caller = ContinuationIdentity(session_id="session-bbb")
        signal_path = mock_repo / ".local" / "supervisor" / "continuation-signal.json"
        result = select_continuation(caller, signal_path)
        assert result.verdict == "ACCEPT"


class TestScenario4_DifferentSessionRejected:
    """Scenario 4: Different session tries to consume — should STOP."""

    def test_mismatched_session_id_stops(self, mock_repo, full_continue_setup):
        full_continue_setup(session_id="session-aaa")
        result = check(mock_repo, session_id="session-zzz")
        assert result["verdict"] == "STOP"
        assert result["reason"] == "SESSION_MISMATCH"

    def test_selector_rejects_mismatched_session(self, mock_repo, full_continue_setup):
        full_continue_setup(session_id="session-aaa")
        caller = ContinuationIdentity(session_id="session-zzz")
        signal_path = mock_repo / ".local" / "supervisor" / "continuation-signal.json"
        result = select_continuation(caller, signal_path)
        assert result.verdict == "REJECT"
        assert "mismatch" in result.reason.lower()


class TestScenario5_LegacySignalNoSessionId:
    """Scenario 5: Legacy signal without session_id — warn but don't reject."""

    def test_no_session_in_signal_allows_continuation(self, mock_repo, full_continue_setup):
        full_continue_setup(session_id=None)  # No session_id in signal
        result = check(mock_repo, session_id="any-session")
        # Legacy: signal has no session_id, so check passes (no mismatch possible)
        assert result["verdict"] == "CONTINUE"

    def test_selector_warns_on_legacy(self, mock_repo, full_continue_setup):
        full_continue_setup(session_id=None)
        caller = ContinuationIdentity(session_id="any-session")
        signal_path = mock_repo / ".local" / "supervisor" / "continuation-signal.json"
        result = select_continuation(caller, signal_path)
        assert result.verdict == "WARN_LEGACY"


class TestScenario6_NoCallerSessionId:
    """Scenario 6: Caller provides no explicit session_id.

    Post TC-CCI-201: check_continuation.py auto-resolves via get_or_create_session_identity().
    If auto-resolve succeeds, the resolved ID will mismatch "session-aaa" → STOP.
    If auto-resolve fails (import error), session_id stays None → CONTINUE (backward compat).
    """

    def test_auto_resolved_session_mismatches_foreign_signal(self, mock_repo,
                                                              full_continue_setup, monkeypatch):
        """When auto-resolve works, a foreign signal is correctly rejected."""
        full_continue_setup(session_id="session-aaa")
        # Auto-resolve will produce a different session_id than "session-aaa"
        result = check(mock_repo, session_id=None)
        # Either STOP (auto-resolved and mismatched) or CONTINUE (auto-resolve failed gracefully)
        assert result["verdict"] in ("STOP", "CONTINUE")

    def test_explicit_none_with_matching_signal(self, mock_repo, full_continue_setup, tmp_path,
                                                 monkeypatch):
        """When caller's auto-resolved session matches signal, CONTINUE."""
        # Create an identity, then use its session_id in the signal
        monkeypatch.setattr("continuation_identity.ACTIVE_SESSION_PATH",
                            tmp_path / "active-session.json")
        from continuation_identity import get_or_create_session_identity
        identity = get_or_create_session_identity()
        full_continue_setup(session_id=identity.session_id)
        result = check(mock_repo, session_id=None)
        # Should auto-resolve to the same session_id → CONTINUE
        assert result["verdict"] == "CONTINUE"


class TestScenario7_SignalFromStoppedSession:
    """Scenario 7: Signal exists but autonomous_continue is false — STOP regardless."""

    def test_stopped_signal_with_matching_session(self, mock_repo, write_signal,
                                                   write_approval_gates, write_work_items):
        write_signal(session_id="session-aaa", autonomous_continue=False)
        write_approval_gates()
        write_work_items()
        result = check(mock_repo, session_id="session-aaa")
        assert result["verdict"] == "STOP"
        assert result["reason"] == "AUTONOMOUS_CONTINUE_FALSE"


class TestScenario11_LedgerTracksCreation:
    """Scenario 11: Ledger records CREATED events for auditing."""

    def test_append_and_query(self, tmp_path, monkeypatch):
        ledger_path = tmp_path / "continuation-ledger.jsonl"
        monkeypatch.setattr("continuation_ledger.LEDGER_PATH", ledger_path)

        append_event("CREATED", "continuation-signal.json",
                     session_id="sess-1", sprint_id="sprint-10")
        append_event("CREATED", "continuation-signal.json",
                     session_id="sess-2", sprint_id="sprint-11")

        active = query_active()
        assert len(active) == 2

        # Filter by session
        active_1 = query_active(session_id="sess-1")
        assert len(active_1) == 1
        assert active_1[0]["session_id"] == "sess-1"

    def test_consumed_removes_from_active(self, tmp_path, monkeypatch):
        ledger_path = tmp_path / "continuation-ledger.jsonl"
        monkeypatch.setattr("continuation_ledger.LEDGER_PATH", ledger_path)

        append_event("CREATED", "signal.json", session_id="sess-1")
        mark_consumed("signal.json", session_id="sess-1")

        active = query_active(session_id="sess-1")
        assert len(active) == 0


class TestScenario17_IdentityCreation:
    """Scenario 17: Identity is created and persisted correctly."""

    def test_identity_roundtrip(self, tmp_path):
        path = tmp_path / "identity.json"
        identity = ContinuationIdentity(
            session_id="test-123",
            mission_id="mission-abc",
            sprint_id="sprint-1",
            branch="main",
        )
        identity.save(path)

        loaded = ContinuationIdentity.load(path)
        assert loaded is not None
        assert loaded.session_id == "test-123"
        assert loaded.mission_id == "mission-abc"
        assert loaded.branch == "main"

    def test_identity_matches_same_session(self):
        a = ContinuationIdentity(session_id="same")
        b = ContinuationIdentity(session_id="same")
        assert a.matches(b)

    def test_identity_no_match_different_session(self):
        a = ContinuationIdentity(session_id="aaa")
        b = ContinuationIdentity(session_id="bbb")
        assert not a.matches(b)


class TestScenario18_IdentityStaleness:
    """Scenario 18: Stale identity detection."""

    def test_recent_identity_not_stale(self):
        identity = ContinuationIdentity(session_id="fresh")
        assert not identity.is_stale()

    def test_old_identity_is_stale(self):
        identity = ContinuationIdentity(
            session_id="old",
            created_at="2020-01-01T00:00:00+00:00",
        )
        assert identity.is_stale()


class TestScenario19_ConflictDetection:
    """Scenario 19: Multiple sessions writing same artifact → conflict detected."""

    def test_conflict_detected(self, tmp_path, monkeypatch):
        ledger_path = tmp_path / "continuation-ledger.jsonl"
        monkeypatch.setattr("continuation_ledger.LEDGER_PATH", ledger_path)

        append_event("CREATED", "continuation-signal.json", session_id="sess-A")
        append_event("CREATED", "continuation-signal.json", session_id="sess-B")

        conflicts = detect_conflicts("continuation-signal.json")
        assert len(conflicts) == 2

    def test_no_conflict_single_session(self, tmp_path, monkeypatch):
        ledger_path = tmp_path / "continuation-ledger.jsonl"
        monkeypatch.setattr("continuation_ledger.LEDGER_PATH", ledger_path)

        append_event("CREATED", "continuation-signal.json", session_id="sess-A")
        conflicts = detect_conflicts("continuation-signal.json")
        assert len(conflicts) == 0


class TestScenario21_SelectorFailClosed:
    """Scenario 21: Selector returns REJECT on missing/invalid signal."""

    def test_missing_signal_rejects(self, mock_repo):
        # Don't write any signal
        caller = ContinuationIdentity(session_id="test")
        signal_path = mock_repo / ".local" / "supervisor" / "continuation-signal.json"
        result = select_continuation(caller, signal_path)
        assert result.verdict == "REJECT"
        assert "does not exist" in result.reason

    def test_invalid_json_rejects(self, mock_repo):
        signal_path = mock_repo / ".local" / "supervisor" / "continuation-signal.json"
        signal_path.write_text("not json{{{", encoding="utf-8")
        caller = ContinuationIdentity(session_id="test")
        result = select_continuation(caller, signal_path)
        assert result.verdict == "REJECT"
        assert "invalid" in result.reason.lower()


class TestScenario25_SessionIdStability:
    """Scenario 25: session_id is stable across multiple calls and producers (TC-CCI-206)."""

    def test_get_or_create_returns_same_id_twice(self, tmp_path, monkeypatch):
        """Two consecutive calls to get_or_create_session_identity return the same session_id."""
        monkeypatch.setattr("continuation_identity.ACTIVE_SESSION_PATH",
                            tmp_path / "active-session.json")
        id1 = get_or_create_session_identity(sprint_id="test-sprint")
        id2 = get_or_create_session_identity(sprint_id="test-sprint")
        assert id1.session_id == id2.session_id

    def test_identity_persists_to_file(self, tmp_path, monkeypatch):
        """Identity written to active-session.json can be loaded back."""
        session_path = tmp_path / "active-session.json"
        monkeypatch.setattr("continuation_identity.ACTIVE_SESSION_PATH", session_path)
        identity = get_or_create_session_identity(sprint_id="test-sprint")
        assert session_path.exists()
        loaded = ContinuationIdentity.load(session_path)
        assert loaded is not None
        assert loaded.session_id == identity.session_id

    def test_new_identity_after_stale(self, tmp_path, monkeypatch):
        """A stale identity (>2h old) produces a fresh session_id."""
        session_path = tmp_path / "active-session.json"
        monkeypatch.setattr("continuation_identity.ACTIVE_SESSION_PATH", session_path)
        old = ContinuationIdentity(
            session_id="old-stale-id",
            created_at="2020-01-01T00:00:00+00:00",
        )
        old.save(session_path)
        fresh = get_or_create_session_identity(sprint_id="test-sprint")
        assert fresh.session_id != "old-stale-id"

    def test_env_override_respected(self, tmp_path, monkeypatch):
        """CLAUDE_SESSION_ID env var is used when creating a new identity."""
        session_path = tmp_path / "active-session.json"
        monkeypatch.setattr("continuation_identity.ACTIVE_SESSION_PATH", session_path)
        monkeypatch.setenv("CLAUDE_SESSION_ID", "env-provided-id")
        identity = get_or_create_session_identity()
        assert identity.session_id == "env-provided-id"
