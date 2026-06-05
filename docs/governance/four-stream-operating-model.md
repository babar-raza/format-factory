# Four-Stream Operating Model

**Added:** 2026-06-04
**Authority:** plans/master-plan.md Section 43 + local-memory-sync sprint 2026-06-04

## Overview

Format Factory work is split into four streams. Each stream has a defined purpose, responsibilities, and output contract. Streams operate in parallel but each owns its own lane.

---

## Stream 1: Mainstream Product

**Purpose:** Build real product capability and drive POC readiness.

**Responsibilities:**
- Commercial .NET product progress (FODS, FODT, Netpbm)
- FOSS/reduced product progress (ZST, Python Netpbm, SYLK, DIF)
- Source code, tests, examples, dogfood, package proof
- POC readiness dashboard maintenance
- Iteration loop until POC_READY_CANDIDATE

**Hard rules:**
- Cannot pass on evidence repair alone
- Must produce measurable product capability in every PASS sprint
- Must cover multiple product tracks per sprint
- Must maintain hard PASS quota for product output breadth

**Primary output:** `src/net/`, `src/python/`, `tests/`, `examples/`, `product-capability-matrix/`

**Continuation signal:** POC_READY_CANDIDATE | CONTINUE_NEXT_ITERATION | CONTINUE_WITH_REROUTE | STOP_EXTERNAL_GATE | STOP_UNSAFE_WORKSPACE

---

## Stream 2: Acceleration Layer

**Purpose:** Non-authoritative AI cognitive operating layer.

**Sub-lanes:**

### 2A: Acceleration-A — Governance Harness
Safety work that prevents product harm:
- Anti-skip enforcement (prevents skipping required work)
- Prompt-quality validation (ensures sprint prompts are actionable)
- Evidence-quality checks (ensures work claims are honest)

Success criteria: measurable reduction in false PASS or false STOP.

### 2B: Acceleration-B — AI Product Acceleration
Legitimate product acceleration using AI/LLM:
- Spec understanding (LLM-assisted requirement extraction)
- Source-pattern mining (identify reusable code patterns)
- Code-generation handoffs (produce draft implementations for Mainstream)
- Test generation (produce test cases from spec requirements)
- Product gap ranking (prioritize most impactful capability gaps)
- AI usage ledger (track AI contribution per sprint)
- ai_draft authority labeling (all AI outputs labeled non-authoritative)

Success criteria: measurable increase in Mainstream product throughput.

**Hard rules:**
- AI output is never authority — labeled ai_draft always
- Cannot mark capability complete
- Cannot approve gates
- Cannot override tests or validators
- Must state whether sprint serves sub-lane A, B, or both

---

## Stream 3: Skills / Governed Execution

**Purpose:** Facilitate autonomous product work safely through governed skill wrappers.

**Responsibilities:**
- Local governed skill wrappers (`.supervisor/skill-registry.yaml` entries)
- Source-change contracts (allowed files, forbidden files per skill)
- Execution templates and transcripts
- Receiver fixtures (standardized handoff format for Mainstream consumption)
- Superpowers Marketplace intake and local normalization
- Mainstream consumption packets

**Hard rules:**
- Skills must be consumed by Mainstream or other lanes — no proof in isolation
- Every skill must have: allowed files, forbidden files, validation command, transcript schema, rollback, evidence rules, activation gate
- Superpowers skills must be normalized before use — no blind plugin install

---

## Stream 4: Autonomous Supervisor / Autonomous Continuation

**Purpose:** Deterministic traffic controller plus non-authoritative AI advisory observer.

**Responsibilities:**
- Stream-local state management
- Continuation decisions (continue/stop/reroute/downgrade)
- Product-output floors enforcement
- False PASS / false STOP detection
- Blocker routing to the right stream
- Ruflo/Superpowers/GhidraMCP runtime governance
- Final evidence/review package validation
- Sprint routing and health metrics

**Hard rules:**
- Deterministic authority for continuation decisions
- AI advisory layer is non-authoritative (labels advisory outputs)
- Cannot approve gates, push, publish, or write secrets
- Must flag any machinery sprint that lacks product-first justification

---

## Cross-Stream Interaction

| From | To | Mechanism |
|---|---|---|
| Acceleration-B | Mainstream | Code-generation handoffs, gap rankings, test drafts |
| Skills | Mainstream | Governed skill wrappers, execution transcripts |
| Supervisor | All streams | Continuation signals, blocker routing, health metrics |
| Mainstream | Supervisor | Evidence declarations, test results, capability matrix diffs |

---

## Stream Isolation Rules

- Each stream owns its evidence declaration separately.
- Streams do not share work-item credit.
- Mainstream receiving a handoff from Acceleration does not give Acceleration credit for the product output.
- Supervisor continuation decisions are deterministic, not AI-voted.
