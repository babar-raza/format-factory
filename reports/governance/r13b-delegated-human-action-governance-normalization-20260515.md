# R13B Delegated Human-Action Governance Normalization
Sprint: FORMAT-FACTORY-R13B-DELEGATED-ZST-GATE1-REAL-SUPPORT-AUDIT-AND-GOVERNANCE-NORMALIZATION-SWARM-001
Gate: 2 (Lane C)
Date: 2026-05-15

---

## Purpose

Correct the governance model to distinguish:
1. **Forbidden autonomous self-approval** — agent acts without human authorization
2. **Allowed delegated decision execution** — agent executes a decision explicitly delegated by human

This correction ensures "awaiting human" does not become a default terminal blocker when the agent can act under explicit human delegation.

---

## Problem Statement

R13 ended with multiple live docs/taskcards in state "awaiting_human_approval" or "action required from Babar Raza." Under the previous governance model, this was always a hard stop. The R13B sprint has been issued by the human project lead (Babar Raza) with an explicit delegation:

> "Any action labeled as required from Babar, human, operator, or manual reviewer must be performed by the assistant/agent in repo by default, using available evidence, governance rules, validation gates, and explicit decision criteria. Human involvement is only a blocker when the action truly requires external authority, credentials, secrets, payment, legal sign-off, or a business decision that cannot be safely inferred from existing project goals."

---

## Occurrence Classification

### Occurrence survey: phrases related to human/agent action

| File | Phrase/Context | Classification | Action |
|------|---------------|----------------|--------|
| GOVERNANCE.md §2.1 | "All 11 gates require human approval" | Governance rule — UPDATE (add §2.1a nuance) | UPDATED |
| AGENTS.md D1 | "No agent may self-approve a gate" | Agent rule — UPDATE (add D1a delegated path) | UPDATED |
| docs/gates.md rule 1 | "No self-approval" | Process rule — UPDATE (add rule 1a) | UPDATED |
| docs/acquisition-workflow.md step 7 | "Do NOT set gate_1.status: passed" | Process step — UPDATE (add delegated path) | UPDATED |
| taskcards/ZST-GATE1-DECISION-PACKET.md | "status: awaiting_human_approval" | Live taskcard — UPDATE (Gate 8 action) | PENDING (Gate 8) |
| acquisition-packs/_candidate-shortlists/zst-gate1-decision-packet-20260515.md | "Gate 1 approval: REQUIRED from Babar Raza" | Decision packet — UPDATE to note delegation executed | PENDING (Gate 8) |
| .local/r13-*/r13-sprint-gate-status.md | "awaiting Babar Raza" | Historical evidence — DO NOT EDIT | PRESERVED |
| .local/r13a-*/r13a-sprint-gate-status.md | "awaiting Babar Raza" | Historical evidence — DO NOT EDIT | PRESERVED |
| reports/planning/r13a-taskcard-state-management-report-20260515.md | "Human-gated items: 1" | Historical report — DO NOT EDIT | PRESERVED |
| memory/29-*.md "ZST Gate 1: NOT STARTED (packet v1.1 prepared; awaiting Babar Raza)" | Memory note | Live state reference — UPDATE (Gate 9 action) | PENDING (Gate 9) |

---

## Governance Correction Applied

### Updated documents (this gate)

| Document | Change |
|----------|--------|
| GOVERNANCE.md | Added §2.1a: Delegated Decision Execution (6 criteria) |
| AGENTS.md | Added D1a: Delegated Decision Execution (5 criteria) |
| docs/gates.md | Added rule 1a: Delegated execution path after rule 1 |
| docs/acquisition-workflow.md | Updated Stage 1 step 7: delegated path noted |

### Key distinction encoded

| Forbidden | Allowed |
|-----------|---------|
| Agent sets gate_1.status: passed without human authorization | Agent records delegated decision when human explicitly delegates via execution prompt |
| Agent self-approves without evidence | Agent executes decision after completing all evidence gates |
| Agent claims approval without verifiable basis | Agent records approval_method: delegated_agent_decision_under_babar_instruction |
| Agent marks awaiting items as complete without performing the work | Agent performs the review work, applies evidence gates, then records result |

---

## True Human Blockers (Preserved)

These items REMAIN as genuine human blockers because they require external authority:

| Item | Why Still Human-Blocked |
|------|------------------------|
| FODS/FODT Gate 11 approval | Commercial product release requires business decision beyond project planning |
| Any formal legal opinion on RFC/patent status | Formal legal counsel requires a licensed attorney |
| Commercial product publishing | Business/distribution decision |
| Git push to remote | Network/credentials |
| Payment or business commitment | External authority |
| Any future gate where Babar has not delegated | Default remains human-reviewed |

---

## Memory Note

A new memory note will be created in Gate 9 (memory/30-delegated-human-action-governance-and-r13b-zst-audit-20260515.md) to record this governance correction permanently.

---

## Governance Correction Result

GOVERNANCE_CORRECTION: COMPLETE
Delegated decision execution model documented in GOVERNANCE.md §2.1a, AGENTS.md §D1a, docs/gates.md rule 1a, docs/acquisition-workflow.md Stage 1 step 7.
Historical evidence preserved. True human blockers preserved.
