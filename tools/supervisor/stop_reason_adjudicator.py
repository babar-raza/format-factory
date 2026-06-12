"""
stop_reason_adjudicator.py — Deterministic Stop Reason Adjudicator

Classifies every potential stop signal as one of:
- A continuation decision (never terminal, agent handles it)
- A release-approval-pending state (POC-ready but release is human-only)
- A TRUE_EXTERNAL_GATE (human must act)
- An UNSAFE_WORKSPACE (stop immediately, report condition)

The central rule: no component may output STOP, approval-blocked, human-required,
or blocked unless this adjudicator classifies that item as TRUE_EXTERNAL_GATE
or UNSAFE_WORKSPACE.

Exit codes (when used as CLI):
  0 — adjudication complete
  1 — invalid input
  9 — unexpected error
"""
from __future__ import annotations

import json
import sys
from typing import Any

# ─────────────────────────────────────────────────────────────
# Input signal categories
# ─────────────────────────────────────────────────────────────

class SignalCategory:
    SUPERVISOR_VERDICT = "SUPERVISOR_VERDICT"
    HUMAN_GATE = "HUMAN_GATE"
    RELEASE_GATE = "RELEASE_GATE"
    IMPLEMENTATION_GATE = "IMPLEMENTATION_GATE"
    EVIDENCE_QUALITY = "EVIDENCE_QUALITY"
    PROMPT_QUALITY = "PROMPT_QUALITY"
    MAX_ITERATION = "MAX_ITERATION"
    RUNTIME_LIMIT = "RUNTIME_LIMIT"
    WORKSPACE_SAFETY = "WORKSPACE_SAFETY"
    PRODUCT_GAP = "PRODUCT_GAP"
    GATE_11 = "GATE_11"
    GATE_8 = "GATE_8"
    MCP_MODE = "MCP_MODE"
    RUFLO_MODE = "RUFLO_MODE"
    PUSH_COMMIT = "PUSH_COMMIT"
    PUBLICATION = "PUBLICATION"
    CREDENTIAL = "CREDENTIAL"
    DESTRUCTIVE_OPERATION = "DESTRUCTIVE_OPERATION"
    BUSINESS_DECISION = "BUSINESS_DECISION"
    UNKNOWN = "UNKNOWN"


# ─────────────────────────────────────────────────────────────
# Output decisions
# ─────────────────────────────────────────────────────────────

class StopDecision:
    CONTINUE_NEXT_ITERATION = "CONTINUE_NEXT_ITERATION"
    LOCAL_REPAIR_CONTINUE = "LOCAL_REPAIR_CONTINUE"
    AGENT_OWNED_REVIEW_CONTINUE = "AGENT_OWNED_REVIEW_CONTINUE"
    AGENT_OWNED_RECOMMENDATION_CONTINUE = "AGENT_OWNED_RECOMMENDATION_CONTINUE"
    RELEASE_APPROVAL_PENDING_NOT_IMPLEMENTATION_BLOCKER = (
        "RELEASE_APPROVAL_PENDING_NOT_IMPLEMENTATION_BLOCKER"
    )
    CHECKPOINT_ROLLOVER_CONTINUE = "CHECKPOINT_ROLLOVER_CONTINUE"
    RUFLO_FALLBACK_LOCAL_CONTINUE = "RUFLO_FALLBACK_LOCAL_CONTINUE"
    POC_READY_CANDIDATE = "POC_READY_CANDIDATE"
    TRUE_EXTERNAL_GATE = "TRUE_EXTERNAL_GATE"
    UNSAFE_WORKSPACE = "UNSAFE_WORKSPACE"
    RUNTIME_LIMIT_CONTINUATION_REQUIRED = "RUNTIME_LIMIT_CONTINUATION_REQUIRED"
    STATE_CONTRADICTION_REPAIR_REQUIRED = "STATE_CONTRADICTION_REPAIR_REQUIRED"


# ─────────────────────────────────────────────────────────────
# Signal normalization maps
# ─────────────────────────────────────────────────────────────

_SIGNAL_KEYWORDS: dict[str, str] = {
    # Supervisor verdicts
    "supervisor_accepted": SignalCategory.SUPERVISOR_VERDICT,
    "accepted_with_rework": SignalCategory.SUPERVISOR_VERDICT,
    "accepted_with_limitations": SignalCategory.SUPERVISOR_VERDICT,
    "overall_verdict_accepted": SignalCategory.SUPERVISOR_VERDICT,
    "sprint_accepted": SignalCategory.SUPERVISOR_VERDICT,
    # Evidence/prompt quality
    "evidence_quality_zero": SignalCategory.EVIDENCE_QUALITY,
    "evidence_quality_score_zero": SignalCategory.EVIDENCE_QUALITY,
    "missing_sample_outputs": SignalCategory.EVIDENCE_QUALITY,
    "missing_raw_logs": SignalCategory.EVIDENCE_QUALITY,
    "evidence_package_built": SignalCategory.EVIDENCE_QUALITY,
    "review_package_created": SignalCategory.EVIDENCE_QUALITY,
    "prompt_quality_failure": SignalCategory.PROMPT_QUALITY,
    "wrong_stream_next_sprint": SignalCategory.PROMPT_QUALITY,
    "anti_skip_false_positive": SignalCategory.PROMPT_QUALITY,
    # Iteration / runtime
    "max_iterations_reached": SignalCategory.MAX_ITERATION,
    "max_iterations": SignalCategory.MAX_ITERATION,
    "iteration_limit_reached": SignalCategory.MAX_ITERATION,
    "runtime_limit": SignalCategory.RUNTIME_LIMIT,
    "context_limit": SignalCategory.RUNTIME_LIMIT,
    # Gate 11 / release
    "gate_11_pending": SignalCategory.GATE_11,
    "gate_11_required": SignalCategory.GATE_11,
    "gate11_approval_required": SignalCategory.GATE_11,
    "commercial_release_approval_required": SignalCategory.RELEASE_GATE,
    "nuget_publish_required": SignalCategory.PUBLICATION,
    "pypi_publish_required": SignalCategory.PUBLICATION,
    # Gate 8
    "gate_8_required": SignalCategory.GATE_8,
    "gate_8_pending": SignalCategory.GATE_8,
    # MCP/Ruflo/mode
    "mode_5_approval_pending": SignalCategory.MCP_MODE,
    "autonomous_sprint_loop_approval_required": SignalCategory.MCP_MODE,
    "mcp_daemon_required": SignalCategory.MCP_MODE,
    "ruflo_unavailable": SignalCategory.RUFLO_MODE,
    "claude_flow_unavailable": SignalCategory.RUFLO_MODE,
    "superpowers_unavailable": SignalCategory.RUFLO_MODE,
    "ghidra_disabled": SignalCategory.RUFLO_MODE,
    # Push/commit
    "git_push_required": SignalCategory.PUSH_COMMIT,
    "git_commit_required": SignalCategory.PUSH_COMMIT,
    "git_merge_required": SignalCategory.PUSH_COMMIT,
    "commit_required": SignalCategory.PUSH_COMMIT,
    "push_required": SignalCategory.PUSH_COMMIT,
    # Publication
    "publication_required": SignalCategory.PUBLICATION,
    "package_publish_required": SignalCategory.PUBLICATION,
    "external_distribution_required": SignalCategory.PUBLICATION,
    # Credentials
    "credentials_required": SignalCategory.CREDENTIAL,
    "secrets_required": SignalCategory.CREDENTIAL,
    "api_key_required": SignalCategory.CREDENTIAL,
    # Destructive
    "destructive_cleanup_required": SignalCategory.DESTRUCTIVE_OPERATION,
    "git_reset_hard_required": SignalCategory.DESTRUCTIVE_OPERATION,
    "git_clean_required": SignalCategory.DESTRUCTIVE_OPERATION,
    # Business decision
    "business_decision_required": SignalCategory.BUSINESS_DECISION,
    "poc_targets_mutation_required": SignalCategory.BUSINESS_DECISION,
    # Workspace safety
    "source_corruption": SignalCategory.WORKSPACE_SAFETY,
    "repeated_foundational_failure_3x": SignalCategory.WORKSPACE_SAFETY,
    "unrecoverable_local_failure": SignalCategory.WORKSPACE_SAFETY,
    "unsafe_workspace": SignalCategory.WORKSPACE_SAFETY,
    # Product gaps (never terminal)
    "poc_targets_proposed_delta": SignalCategory.PRODUCT_GAP,
    "dif_reconsideration": SignalCategory.PRODUCT_GAP,
    "sylk_promotion": SignalCategory.PRODUCT_GAP,
    "zst_promotion": SignalCategory.PRODUCT_GAP,
    "dogfood_gap_pending": SignalCategory.PRODUCT_GAP,
    "target_writer_missing": SignalCategory.PRODUCT_GAP,
    # Human gate (generic)
    "human_required": SignalCategory.HUMAN_GATE,
    "human_approval_required": SignalCategory.HUMAN_GATE,
    "babar_approval_required": SignalCategory.HUMAN_GATE,
    "approval_blocked": SignalCategory.HUMAN_GATE,
    "blocked": SignalCategory.HUMAN_GATE,
}


def _normalize_signal(signal: str) -> str:
    """Normalize signal string to a known category."""
    if not signal:
        return SignalCategory.UNKNOWN
    s = signal.lower().strip().replace("-", "_").replace(" ", "_")
    # Direct lookup
    if s in _SIGNAL_KEYWORDS:
        return _SIGNAL_KEYWORDS[s]
    # Substring matching
    for keyword, category in _SIGNAL_KEYWORDS.items():
        if keyword in s or s in keyword:
            return category
    return SignalCategory.UNKNOWN


def _make_decision(
    input_signal: str,
    normalized: str,
    decision: str,
    terminal: bool,
    blocks_implementation: bool,
    blocks_poc_candidate: bool,
    blocks_release: bool,
    agent_can_handle: bool,
    human_required: bool,
    allowed_next_action: str,
    reason: str,
    evidence_refs: list[str] | None = None,
    remediation: str = "",
) -> dict[str, Any]:
    return {
        "input_signal": input_signal,
        "normalized_signal": normalized,
        "decision": decision,
        "terminal": terminal,
        "blocks_implementation": blocks_implementation,
        "blocks_poc_candidate": blocks_poc_candidate,
        "blocks_release": blocks_release,
        "agent_can_handle": agent_can_handle,
        "human_required": human_required,
        "allowed_next_action": allowed_next_action,
        "reason": reason,
        "evidence_refs": evidence_refs or [],
        "remediation": remediation,
    }


# ─────────────────────────────────────────────────────────────
# Core adjudication function
# ─────────────────────────────────────────────────────────────

def adjudicate_stop_reason(
    signal: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Adjudicate a potential stop reason.

    Args:
        signal: The stop signal string (e.g., "supervisor_accepted", "gate_11_required").
        context: Optional context dict with keys like:
            - poc_ready: bool — whether POC candidate is complete
            - materialization_verified: bool — evidence artifacts verified
            - safe_lanes_available: bool — other work available
            - autonomous_continue: bool — continuation signal
            - rework_is_repairable: bool — for ACCEPTED_WITH_REWORK
            - evidence_system_corrupted: bool — for evidence_quality_zero edge case
            - requires_external_daemon: bool — for MCP/Ruflo signals
            - prompt_would_cause_unsafe_edit: bool — for prompt_quality edge case

    Returns:
        Decision dict with fields: input_signal, normalized_signal, decision, terminal,
        blocks_implementation, blocks_poc_candidate, blocks_release, agent_can_handle,
        human_required, allowed_next_action, reason, evidence_refs, remediation.
    """
    ctx = context or {}
    normalized = _normalize_signal(signal)

    # ── Rule 1: Supervisor ACCEPTED ────────────────────────────────────────
    if normalized == SignalCategory.SUPERVISOR_VERDICT:
        poc_ready = ctx.get("poc_ready", False)
        gate_11_pending = ctx.get("gate_11_pending", False)
        if poc_ready and gate_11_pending:
            return _make_decision(
                signal, normalized,
                StopDecision.RELEASE_APPROVAL_PENDING_NOT_IMPLEMENTATION_BLOCKER,
                terminal=True,
                blocks_implementation=False,
                blocks_poc_candidate=False,
                blocks_release=True,
                agent_can_handle=True,
                human_required=False,
                allowed_next_action="Prepare Gate 11 readiness packet; do not stop implementation",
                reason="Supervisor ACCEPTED + POC-ready + Gate 11 pending = release-approval-pending only",
                remediation="Prepare Gate 11 packet. Release approval requires human; implementation does not.",
            )
        if poc_ready:
            return _make_decision(
                signal, normalized,
                StopDecision.POC_READY_CANDIDATE,
                terminal=True,
                blocks_implementation=False,
                blocks_poc_candidate=False,
                blocks_release=False,
                agent_can_handle=True,
                human_required=False,
                allowed_next_action="POC candidate is complete. Prepare release packet.",
                reason="Supervisor ACCEPTED with POC-ready confirmed",
            )
        return _make_decision(
            signal, normalized,
            StopDecision.CONTINUE_NEXT_ITERATION,
            terminal=False,
            blocks_implementation=False,
            blocks_poc_candidate=False,
            blocks_release=False,
            agent_can_handle=True,
            human_required=False,
            allowed_next_action="Continue to next sprint iteration",
            reason="Supervisor ACCEPTED alone is NOT terminal. Continue.",
            remediation="Read next-sprint.md and execute next iteration.",
        )

    # ── Rule 2: ACCEPTED_WITH_REWORK ───────────────────────────────────────
    # (handled by SUPERVISOR_VERDICT above, additional nuance here)

    # ── Rule 4: Evidence quality zero ──────────────────────────────────────
    if normalized == SignalCategory.EVIDENCE_QUALITY:
        signal_lower = signal.lower()
        # evidence_package_built is never terminal
        if any(k in signal_lower for k in ("package_built", "review_package", "package_created")):
            return _make_decision(
                signal, normalized,
                StopDecision.CONTINUE_NEXT_ITERATION,
                terminal=False,
                blocks_implementation=False,
                blocks_poc_candidate=False,
                blocks_release=False,
                agent_can_handle=True,
                human_required=False,
                allowed_next_action="Continue to next sprint; evidence package existence is not terminal",
                reason="Evidence/review package built is NOT a terminal stop reason",
            )
        # evidence_quality_zero
        evidence_corrupted = ctx.get("evidence_system_corrupted", False)
        if evidence_corrupted:
            return _make_decision(
                signal, normalized,
                StopDecision.UNSAFE_WORKSPACE,
                terminal=True,
                blocks_implementation=True,
                blocks_poc_candidate=True,
                blocks_release=True,
                agent_can_handle=False,
                human_required=True,
                allowed_next_action="Stop; report exact corruption condition",
                reason="Evidence system corrupted and cannot be repaired — UNSAFE_WORKSPACE",
                remediation="Investigate and report exact corruption. Do not continue.",
            )
        mat_verified = ctx.get("materialization_verified", False)
        if mat_verified or not evidence_corrupted:
            return _make_decision(
                signal, normalized,
                StopDecision.LOCAL_REPAIR_CONTINUE,
                terminal=False,
                blocks_implementation=False,
                blocks_poc_candidate=False,
                blocks_release=False,
                agent_can_handle=True,
                human_required=False,
                allowed_next_action="Add tests_supporting fields; repair declaration; rerun autonomous_cycle",
                reason="evidence_quality_zero is repairable — add tests_supporting to declaration",
                remediation="Repair: add tests_supporting with real test file paths to work items.",
            )
        return _make_decision(
            signal, normalized,
            StopDecision.STATE_CONTRADICTION_REPAIR_REQUIRED,
            terminal=False,
            blocks_implementation=False,
            blocks_poc_candidate=False,
            blocks_release=False,
            agent_can_handle=True,
            human_required=False,
            allowed_next_action="Inspect and repair evidence declaration",
            reason="Evidence quality issue — inspect and repair declaration before continuing",
        )

    # ── Rule 5: Prompt quality failure ─────────────────────────────────────
    if normalized == SignalCategory.PROMPT_QUALITY:
        unsafe_edit = ctx.get("prompt_would_cause_unsafe_edit", False)
        if unsafe_edit:
            return _make_decision(
                signal, normalized,
                StopDecision.UNSAFE_WORKSPACE,
                terminal=True,
                blocks_implementation=True,
                blocks_poc_candidate=True,
                blocks_release=True,
                agent_can_handle=False,
                human_required=True,
                allowed_next_action="Stop; report unsafe prompt condition",
                reason="Prompt would cause unsafe/destructive/forbidden edit",
            )
        return _make_decision(
            signal, normalized,
            StopDecision.LOCAL_REPAIR_CONTINUE,
            terminal=False,
            blocks_implementation=False,
            blocks_poc_candidate=False,
            blocks_release=False,
            agent_can_handle=True,
            human_required=False,
            allowed_next_action="Repair prompt quality issue; regenerate next-sprint prompt",
            reason="Prompt quality failures are always locally repairable",
            remediation="Check wrong_stream_next_sprint, regenerate prompt, or continue without template.",
        )

    # ── Rule 6: Max iterations reached ─────────────────────────────────────
    if normalized == SignalCategory.MAX_ITERATION:
        return _make_decision(
            signal, normalized,
            StopDecision.CHECKPOINT_ROLLOVER_CONTINUE,
            terminal=False,
            blocks_implementation=False,
            blocks_poc_candidate=False,
            blocks_release=False,
            agent_can_handle=True,
            human_required=False,
            allowed_next_action="Write continuation package; reset iteration counter; continue",
            reason="max_iterations is NOT terminal — use checkpoint rollover",
            remediation=(
                "Increment iteration field in continuation-signal.json. "
                "Write continuation handoff. Continue with next iteration."
            ),
        )

    # ── Rule 7: MODE 5 / MCP daemon ────────────────────────────────────────
    if normalized == SignalCategory.MCP_MODE:
        requires_external_daemon = ctx.get("requires_external_daemon", False)
        if requires_external_daemon:
            return _make_decision(
                signal, normalized,
                StopDecision.TRUE_EXTERNAL_GATE,
                terminal=True,
                blocks_implementation=True,
                blocks_poc_candidate=False,
                blocks_release=False,
                agent_can_handle=False,
                human_required=True,
                allowed_next_action="Request external MCP daemon activation from user",
                reason="Actual external daemon activation required — TRUE_EXTERNAL_GATE",
            )
        return _make_decision(
            signal, normalized,
            StopDecision.RUFLO_FALLBACK_LOCAL_CONTINUE,
            terminal=False,
            blocks_implementation=False,
            blocks_poc_candidate=False,
            blocks_release=False,
            agent_can_handle=True,
            human_required=False,
            allowed_next_action="Use local coordinator; continue without external daemon",
            reason="MODE 5 / autonomous sprint loop approval does NOT block local continuation",
            remediation="Fall back to local coordinator. Continue autonomous implementation cycle.",
        )

    # ── Rule 8: Ruflo / claude-flow unavailable ────────────────────────────
    if normalized == SignalCategory.RUFLO_MODE:
        return _make_decision(
            signal, normalized,
            StopDecision.RUFLO_FALLBACK_LOCAL_CONTINUE,
            terminal=False,
            blocks_implementation=False,
            blocks_poc_candidate=False,
            blocks_release=False,
            agent_can_handle=True,
            human_required=False,
            allowed_next_action="Proceed as local coordinator; Ruflo is not required",
            reason="Ruflo/claude-flow unavailable is NOT terminal — fall back to local",
            remediation="Continue as local coordinator. All implementation proceeds locally.",
        )

    # ── Rule 9: Gate 11 pending ────────────────────────────────────────────
    if normalized == SignalCategory.GATE_11:
        poc_ready = ctx.get("poc_ready", False)
        if poc_ready:
            return _make_decision(
                signal, normalized,
                StopDecision.RELEASE_APPROVAL_PENDING_NOT_IMPLEMENTATION_BLOCKER,
                terminal=True,
                blocks_implementation=False,
                blocks_poc_candidate=False,
                blocks_release=True,
                agent_can_handle=True,
                human_required=False,
                allowed_next_action=(
                    "Prepare Gate 11 readiness packet; present to Babar Raza. "
                    "Agent prepares packet; human executes approval."
                ),
                reason=(
                    "Gate 11 pending + POC-ready: release-approval-pending. "
                    "NOT an implementation blocker. Implementation is complete."
                ),
                remediation="Agent action: prepare/refresh Gate 11 readiness packet. Human action: approve release.",
            )
        return _make_decision(
            signal, normalized,
            StopDecision.CONTINUE_NEXT_ITERATION,
            terminal=False,
            blocks_implementation=False,
            blocks_poc_candidate=False,
            blocks_release=True,
            agent_can_handle=True,
            human_required=False,
            allowed_next_action="Continue implementation work; Gate 11 is not yet relevant",
            reason="Gate 11 pending with POC not yet complete — continue implementation",
            remediation="Complete POC candidate before Gate 11 considerations.",
        )

    # ── Rule 10: Gate 8 pending ────────────────────────────────────────────
    if normalized == SignalCategory.GATE_8:
        poc_ready = ctx.get("poc_ready", False)
        if poc_ready:
            return _make_decision(
                signal, normalized,
                StopDecision.RELEASE_APPROVAL_PENDING_NOT_IMPLEMENTATION_BLOCKER,
                terminal=True,
                blocks_implementation=False,
                blocks_poc_candidate=False,
                blocks_release=True,
                agent_can_handle=True,
                human_required=False,
                allowed_next_action="Prepare Gate 8 readiness assessment; present to reviewer",
                reason="Gate 8 pending + POC-ready: release-approval-pending only",
            )
        return _make_decision(
            signal, normalized,
            StopDecision.CONTINUE_NEXT_ITERATION,
            terminal=False,
            blocks_implementation=False,
            blocks_poc_candidate=False,
            blocks_release=True,
            agent_can_handle=True,
            human_required=False,
            allowed_next_action="Continue implementation; Gate 8 is not yet relevant",
            reason="Gate 8 pending with implementation incomplete — continue",
        )

    # ── Rule 11: Commit/push/merge ─────────────────────────────────────────
    if normalized == SignalCategory.PUSH_COMMIT:
        safe_lanes = ctx.get("safe_lanes_available", False)
        return _make_decision(
            signal, normalized,
            StopDecision.TRUE_EXTERNAL_GATE,
            terminal=True,
            blocks_implementation=not safe_lanes,
            blocks_poc_candidate=False,
            blocks_release=True,
            agent_can_handle=True,
            human_required=True,
            allowed_next_action=(
                "Agent: prepare commit candidate summary and changed-file manifest. "
                "Human: execute commit/push with explicit authorization."
            ),
            reason="git commit/push/merge requires explicit human authorization",
            remediation=(
                "Agent prepares commit summary. Wait for explicit user authorization "
                "before executing commit or push."
            ),
        )

    # ── Rule 12: Publication ───────────────────────────────────────────────
    if normalized == SignalCategory.PUBLICATION:
        return _make_decision(
            signal, normalized,
            StopDecision.TRUE_EXTERNAL_GATE,
            terminal=True,
            blocks_implementation=False,
            blocks_poc_candidate=False,
            blocks_release=True,
            agent_can_handle=True,
            human_required=True,
            allowed_next_action=(
                "Agent: prepare publication checklist and release packet. "
                "Human: execute publication."
            ),
            reason="NuGet/PyPI publication requires human execution",
            remediation="Prepare publication packet. Wait for human to execute publication.",
        )

    # ── Rule 13: Credentials/secrets ──────────────────────────────────────
    if normalized == SignalCategory.CREDENTIAL:
        safe_fallback = ctx.get("safe_fallback_exists", False)
        if safe_fallback:
            return _make_decision(
                signal, normalized,
                StopDecision.LOCAL_REPAIR_CONTINUE,
                terminal=False,
                blocks_implementation=False,
                blocks_poc_candidate=False,
                blocks_release=False,
                agent_can_handle=True,
                human_required=False,
                allowed_next_action="Use safe fallback; continue without credentials",
                reason="Credentials needed but safe fallback exists — continue with fallback",
            )
        return _make_decision(
            signal, normalized,
            StopDecision.TRUE_EXTERNAL_GATE,
            terminal=True,
            blocks_implementation=True,
            blocks_poc_candidate=True,
            blocks_release=True,
            agent_can_handle=False,
            human_required=True,
            allowed_next_action="Request credentials from user; do not continue without them",
            reason="Credentials required with no safe fallback — TRUE_EXTERNAL_GATE",
        )

    # ── Rule 14: Destructive cleanup ──────────────────────────────────────
    if normalized == SignalCategory.DESTRUCTIVE_OPERATION:
        non_destructive_alt = ctx.get("non_destructive_alternative_exists", True)
        if non_destructive_alt:
            return _make_decision(
                signal, normalized,
                StopDecision.LOCAL_REPAIR_CONTINUE,
                terminal=False,
                blocks_implementation=False,
                blocks_poc_candidate=False,
                blocks_release=False,
                agent_can_handle=True,
                human_required=False,
                allowed_next_action="Use non-destructive alternative; continue without destructive op",
                reason="Destructive op requested but non-destructive alternative exists",
                remediation="Use non-destructive approach (stash, branch, copy) instead.",
            )
        return _make_decision(
            signal, normalized,
            StopDecision.TRUE_EXTERNAL_GATE,
            terminal=True,
            blocks_implementation=True,
            blocks_poc_candidate=True,
            blocks_release=True,
            agent_can_handle=False,
            human_required=True,
            allowed_next_action="Request destructive cleanup authorization from user",
            reason="Destructive cleanup required with no safe alternative — TRUE_EXTERNAL_GATE",
        )

    # ── Rule 15: Business decision ─────────────────────────────────────────
    if normalized == SignalCategory.BUSINESS_DECISION:
        policy_can_infer = ctx.get("policy_can_infer_safely", True)
        if policy_can_infer:
            return _make_decision(
                signal, normalized,
                StopDecision.AGENT_OWNED_RECOMMENDATION_CONTINUE,
                terminal=False,
                blocks_implementation=False,
                blocks_poc_candidate=False,
                blocks_release=False,
                agent_can_handle=True,
                human_required=False,
                allowed_next_action="Apply project policy default; document recommendation",
                reason="Business decision can be inferred from project policy — agent-owned",
                remediation="Apply project-level policy. Document as recommendation for human review.",
            )
        return _make_decision(
            signal, normalized,
            StopDecision.TRUE_EXTERNAL_GATE,
            terminal=True,
            blocks_implementation=False,
            blocks_poc_candidate=False,
            blocks_release=True,
            agent_can_handle=False,
            human_required=True,
            allowed_next_action="Present options to user; wait for business decision",
            reason="Business decision required and project policy cannot infer safe default",
        )

    # ── Rule 16: DIF/SYLK/ZST promotion / poc-targets delta ───────────────
    if normalized == SignalCategory.PRODUCT_GAP:
        return _make_decision(
            signal, normalized,
            StopDecision.AGENT_OWNED_RECOMMENDATION_CONTINUE,
            terminal=False,
            blocks_implementation=False,
            blocks_poc_candidate=False,
            blocks_release=False,
            agent_can_handle=True,
            human_required=False,
            allowed_next_action="Produce proposed delta document; do not mutate poc-targets.yaml directly",
            reason="Product gap / POC-targets delta is agent-owned recommendation — never terminal",
            remediation=(
                "Generate proposed-delta YAML. Present to user. Direct mutation is gated; "
                "proposal is always agent-owned."
            ),
        )

    # ── Rule 17: poc-targets direct mutation (BUSINESS_DECISION) ──────────
    # (handled above via BUSINESS_DECISION/PRODUCT_GAP)

    # ── Rule 18: Dirty git state ───────────────────────────────────────────
    if normalized == SignalCategory.WORKSPACE_SAFETY:
        signal_lower = signal.lower()
        # Source corruption — truly unsafe
        if any(k in signal_lower for k in ("source_corruption", "repeated_foundational", "unrecoverable")):
            return _make_decision(
                signal, normalized,
                StopDecision.UNSAFE_WORKSPACE,
                terminal=True,
                blocks_implementation=True,
                blocks_poc_candidate=True,
                blocks_release=True,
                agent_can_handle=False,
                human_required=True,
                allowed_next_action="Stop immediately; report exact unsafe condition to user",
                reason="Source corruption / unrecoverable failure — UNSAFE_WORKSPACE",
                remediation="Report exact error. Do not continue. Investigate with user.",
            )
        # Dirty git state that's classified as sprint work
        dirty_classified = ctx.get("dirty_state_classified", False)
        if dirty_classified:
            return _make_decision(
                signal, normalized,
                StopDecision.CONTINUE_NEXT_ITERATION,
                terminal=False,
                blocks_implementation=False,
                blocks_poc_candidate=False,
                blocks_release=False,
                agent_can_handle=True,
                human_required=False,
                allowed_next_action="Continue; dirty state is classified as sprint work",
                reason="Dirty git state classified as SPRINT_WORK_IN_PROGRESS_AUTHORIZED",
            )
        # Unclassified dirty state
        return _make_decision(
            signal, normalized,
            StopDecision.LOCAL_REPAIR_CONTINUE,
            terminal=False,
            blocks_implementation=False,
            blocks_poc_candidate=False,
            blocks_release=False,
            agent_can_handle=True,
            human_required=False,
            allowed_next_action="Classify dirty state; add dirty_state_classification to declaration",
            reason="Dirty git state — classify it and continue; not terminal unless corrupted",
            remediation="Add dirty_state_classification field to evidence declaration.",
        )

    # ── Generic HUMAN_GATE (unclassified "human required") ─────────────────
    if normalized == SignalCategory.HUMAN_GATE:
        # Generic "approval-blocked" / "blocked" / "human required" strings
        # are NEVER sufficient to stop — must be reclassified
        signal_lower = signal.lower()
        # Check if it maps to a known release gate
        release_keywords = ["gate_11", "g11", "babar", "commercial_release", "release_approval"]
        if any(k in signal_lower for k in release_keywords):
            poc_ready = ctx.get("poc_ready", False)
            if poc_ready:
                return _make_decision(
                    signal, normalized,
                    StopDecision.RELEASE_APPROVAL_PENDING_NOT_IMPLEMENTATION_BLOCKER,
                    terminal=True,
                    blocks_implementation=False,
                    blocks_poc_candidate=False,
                    blocks_release=True,
                    agent_can_handle=True,
                    human_required=False,
                    allowed_next_action="Prepare Gate 11 packet; implementation is complete",
                    reason="Human gate classified as release-approval-only",
                )
            return _make_decision(
                signal, normalized,
                StopDecision.CONTINUE_NEXT_ITERATION,
                terminal=False,
                blocks_implementation=False,
                blocks_poc_candidate=False,
                blocks_release=True,
                agent_can_handle=True,
                human_required=False,
                allowed_next_action="Continue implementation; Gate 11 is not yet relevant",
                reason="Release gate while POC not complete — continue implementation",
            )
        # Check if it maps to mode/ruflo
        mode_keywords = ["mode_5", "ruflo", "claude_flow", "mcp_daemon"]
        if any(k in signal_lower for k in mode_keywords):
            return _make_decision(
                signal, normalized,
                StopDecision.RUFLO_FALLBACK_LOCAL_CONTINUE,
                terminal=False,
                blocks_implementation=False,
                blocks_poc_candidate=False,
                blocks_release=False,
                agent_can_handle=True,
                human_required=False,
                allowed_next_action="Fall back to local coordinator; continue without daemon",
                reason="Mode/Ruflo gate — fall back to local; not terminal",
            )
        # Generic "approval-blocked" or "blocked" — reclassify as agent-owned review
        return _make_decision(
            signal, normalized,
            StopDecision.AGENT_OWNED_REVIEW_CONTINUE,
            terminal=False,
            blocks_implementation=False,
            blocks_poc_candidate=False,
            blocks_release=False,
            agent_can_handle=True,
            human_required=False,
            allowed_next_action=(
                "Reclassify: determine if this is agent-owned, release-only, or true external. "
                "Do not stop based on generic 'human required' label."
            ),
            reason=(
                "Generic 'human required' / 'approval-blocked' / 'blocked' label is NOT sufficient "
                "to stop. Must be reclassified by Stop Reason Adjudicator."
            ),
            remediation=(
                "Run adjudicator with specific signal. Replace 'approval-blocked' label with "
                "correct classification: agent-owned prep vs human-only execution."
            ),
        )

    # ── Unknown signals — default to agent-owned review ────────────────────
    if normalized == SignalCategory.UNKNOWN:
        return _make_decision(
            signal, normalized,
            StopDecision.AGENT_OWNED_REVIEW_CONTINUE,
            terminal=False,
            blocks_implementation=False,
            blocks_poc_candidate=False,
            blocks_release=False,
            agent_can_handle=True,
            human_required=False,
            allowed_next_action="Classify unknown signal; default to continue unless true external gate",
            reason="Unknown signal — defaulting to agent-owned review. Must be explicitly classified to stop.",
            remediation="Identify the specific signal and rerun adjudicator with known signal type.",
        )

    # ── Fallback (should not reach here) ───────────────────────────────────
    return _make_decision(
        signal, normalized,
        StopDecision.CONTINUE_NEXT_ITERATION,
        terminal=False,
        blocks_implementation=False,
        blocks_poc_candidate=False,
        blocks_release=False,
        agent_can_handle=True,
        human_required=False,
        allowed_next_action="Continue; signal not recognized as terminal",
        reason=f"Unhandled signal category: {normalized}",
    )


# ─────────────────────────────────────────────────────────────
# Batch adjudication
# ─────────────────────────────────────────────────────────────

def adjudicate_batch(
    signals: list[str],
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Adjudicate a list of signals and return a combined result.

    Returns:
    - decisions: list of individual decisions
    - overall_terminal: True if ANY decision is terminal
    - overall_decision: most severe terminal decision (or CONTINUE if all non-terminal)
    - has_true_external_gate: bool
    - has_unsafe_workspace: bool
    - all_agent_owned: bool
    """
    decisions = [adjudicate_stop_reason(s, context) for s in signals]

    has_unsafe = any(d["decision"] == StopDecision.UNSAFE_WORKSPACE for d in decisions)
    has_external = any(d["decision"] == StopDecision.TRUE_EXTERNAL_GATE for d in decisions)
    has_release_pending = any(
        d["decision"] == StopDecision.RELEASE_APPROVAL_PENDING_NOT_IMPLEMENTATION_BLOCKER
        for d in decisions
    )
    has_poc_ready = any(d["decision"] == StopDecision.POC_READY_CANDIDATE for d in decisions)

    # Determine overall decision (priority order)
    if has_unsafe:
        overall = StopDecision.UNSAFE_WORKSPACE
    elif has_external:
        overall = StopDecision.TRUE_EXTERNAL_GATE
    elif has_release_pending:
        overall = StopDecision.RELEASE_APPROVAL_PENDING_NOT_IMPLEMENTATION_BLOCKER
    elif has_poc_ready:
        overall = StopDecision.POC_READY_CANDIDATE
    else:
        # Pick best continuation decision
        continuation_priority = [
            StopDecision.STATE_CONTRADICTION_REPAIR_REQUIRED,
            StopDecision.LOCAL_REPAIR_CONTINUE,
            StopDecision.CHECKPOINT_ROLLOVER_CONTINUE,
            StopDecision.RUFLO_FALLBACK_LOCAL_CONTINUE,
            StopDecision.AGENT_OWNED_RECOMMENDATION_CONTINUE,
            StopDecision.AGENT_OWNED_REVIEW_CONTINUE,
            StopDecision.CONTINUE_NEXT_ITERATION,
        ]
        for candidate in continuation_priority:
            if any(d["decision"] == candidate for d in decisions):
                overall = candidate
                break
        else:
            overall = StopDecision.CONTINUE_NEXT_ITERATION

    overall_terminal = overall in (
        StopDecision.UNSAFE_WORKSPACE,
        StopDecision.TRUE_EXTERNAL_GATE,
        StopDecision.RELEASE_APPROVAL_PENDING_NOT_IMPLEMENTATION_BLOCKER,
        StopDecision.POC_READY_CANDIDATE,
    )

    return {
        "decisions": decisions,
        "overall_terminal": overall_terminal,
        "overall_decision": overall,
        "has_true_external_gate": has_external,
        "has_unsafe_workspace": has_unsafe,
        "has_release_pending": has_release_pending,
        "all_agent_owned": not has_unsafe and not has_external,
        "terminal_signals": [
            d["input_signal"] for d in decisions if d["terminal"]
        ],
        "continuation_signals": [
            d["input_signal"] for d in decisions if not d["terminal"]
        ],
    }


# ─────────────────────────────────────────────────────────────
# Task label reclassification
# ─────────────────────────────────────────────────────────────

_FALSE_STOP_LABELS = frozenset({
    "approval-blocked",
    "blocked",
    "human-required",
    "stop",
    "approval_blocked",
})

_AGENT_OWNED_LABEL = "agent-owned"
_EXTERNAL_GATE_LABEL = "external-gate"
_RELEASE_PENDING_LABEL = "release-approval-pending"


def reclassify_task_label(
    label: str,
    task_title: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Reclassify a task label from a next-sprint prompt.

    Returns:
    - original_label: str
    - new_label: str
    - is_false_stop: bool
    - agent_can_execute: bool
    - adjudication: dict from adjudicate_stop_reason
    """
    label_normalized = label.lower().strip().lstrip("[").rstrip("]")
    is_false_stop = label_normalized in _FALSE_STOP_LABELS

    # Derive signal from task title
    title_lower = task_title.lower()

    # Determine signal from task title
    if any(k in title_lower for k in ["gate 11", "gate11", "g11", "commercial readiness"]):
        signal = "gate_11_pending"
    elif any(k in title_lower for k in ["commit", "push", "merge"]):
        signal = "git_push_required"
    elif any(k in title_lower for k in ["publish", "nuget", "pypi", "release"]):
        signal = "publication_required"
    elif any(k in title_lower for k in ["mode 5", "mode5", "ruflo", "claude-flow", "mcp"]):
        signal = "mode_5_approval_pending"
    elif any(k in title_lower for k in ["readiness packet", "prepare packet", "gate readiness"]):
        signal = "poc_targets_proposed_delta"
    elif any(k in title_lower for k in ["dogfood", "target writer", "csv export", "html export"]):
        signal = "dogfood_gap_pending"
    elif any(k in title_lower for k in ["dif", "sylk", "zst", "reconsider", "promotion"]):
        signal = "dif_reconsideration"
    elif any(k in title_lower for k in ["poc-targets", "poc targets", "capability matrix"]):
        signal = "poc_targets_proposed_delta"
    elif is_false_stop:
        signal = "approval_blocked"
    else:
        signal = "unknown"

    adjudication = adjudicate_stop_reason(signal, context)

    if adjudication["decision"] == StopDecision.TRUE_EXTERNAL_GATE:
        new_label = _EXTERNAL_GATE_LABEL
        agent_can_execute = False
    elif adjudication["decision"] == StopDecision.RELEASE_APPROVAL_PENDING_NOT_IMPLEMENTATION_BLOCKER:
        new_label = _RELEASE_PENDING_LABEL
        agent_can_execute = True  # Agent prepares packet; human approves
    elif adjudication["decision"] == StopDecision.UNSAFE_WORKSPACE:
        new_label = "unsafe-stop"
        agent_can_execute = False
    else:
        new_label = _AGENT_OWNED_LABEL
        agent_can_execute = True

    return {
        "original_label": label,
        "new_label": new_label,
        "is_false_stop": is_false_stop,
        "agent_can_execute": agent_can_execute,
        "adjudication": adjudication,
    }


# ─────────────────────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────────────────────

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Adjudicate a stop reason signal")
    parser.add_argument("signal", nargs="?", default="supervisor_accepted",
                        help="Stop signal to adjudicate")
    parser.add_argument("--poc-ready", action="store_true", help="Set poc_ready=true in context")
    parser.add_argument("--gate-11-pending", action="store_true")
    parser.add_argument("--autonomous-continue", action="store_true")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    ctx = {
        "poc_ready": args.poc_ready,
        "gate_11_pending": args.gate_11_pending,
        "autonomous_continue": args.autonomous_continue,
    }

    result = adjudicate_stop_reason(args.signal, ctx)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Signal:    {result['input_signal']}")
        print(f"Normalized:{result['normalized_signal']}")
        print(f"Decision:  {result['decision']}")
        print(f"Terminal:  {result['terminal']}")
        print(f"Agent:     {result['agent_can_handle']}")
        print(f"Human:     {result['human_required']}")
        print(f"Reason:    {result['reason']}")
        print(f"Next:      {result['allowed_next_action']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
