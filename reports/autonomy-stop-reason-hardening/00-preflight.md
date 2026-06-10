# Preflight — FORMAT-FACTORY-PERMANENT-AUTONOMY-STOP-REASON-HARDENING-001

## Sprint

- **ID:** FORMAT-FACTORY-PERMANENT-AUTONOMY-STOP-REASON-HARDENING-001
- **Date:** 2026-06-05
- **Type:** Machinery hardening — no product source changes
- **Prior sprint:** unified-poc-authority-reconciliation-r118 (ACCEPTED, exit 0, 9/9 ACCEPTED)

## Environment

- Python: 3.13.2
- Branch: main
- HEAD: 3a86a05295cb4b82ed40a3408b0612a90f93643c
- VENV: .local/venv/Scripts/python

## Purpose

Fix the systemic reason the Format Factory autonomous train keeps stopping without a valid
terminal reason. Implement a deterministic Stop Reason Adjudicator that classifies every
potential stop signal as either a TRUE_EXTERNAL_GATE, UNSAFE_WORKSPACE, or a continuation
decision. Prevent false stops from approval-gates.md, evidence package built, max_iterations,
and Gate 11 pending from blocking implementation.

## File Ownership This Sprint

- **NEW:** tools/supervisor/stop_reason_adjudicator.py
- **UPDATED:** tools/supervisor/autonomous_poc_controller.py
- **UPDATED:** tools/supervisor/generate_next_worker_prompt.py
- **NEW TESTS:** tests/supervisor/test_stop_reason_adjudicator.py
- **NEW TESTS:** tests/supervisor/test_human_gate_policy.py
- **NEW TESTS:** tests/supervisor/test_next_sprint_false_stop_regression.py
- **NEW TESTS:** tests/supervisor/test_supervisor_loop_continuation_contract.py
- **UPDATED TESTS:** tests/supervisor/test_autonomous_poc_controller.py
- **NEW DOCS:** docs/governance/autonomous-stop-reason-policy.md
- **NEW DOCS:** docs/governance/human-gate-classification-policy.md
- **NEW DOCS:** docs/governance/agent-owned-review-policy.md
- **NEW SCHEMAS:** .supervisor/schemas/stop-reason-decision.schema.json
- **NEW SCHEMAS:** .supervisor/schemas/human-gate-classification.schema.json
- **REPORTS:** reports/autonomy-stop-reason-hardening/**

## Hard Prohibitions Confirmed

- No git commit/push
- No Gate 8/11 approval
- No publication
- No product source edit (src/net/, src/python/, tests/net/, tests/python/)
- No poc-targets.yaml direct mutation
- No registry/format-registry.yaml mutation
- No Netpbm removal
- No SVG as Netpbm replacement
