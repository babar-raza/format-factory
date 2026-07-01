---
document_type: governance_doc
sprint: CONWAY-R9-GOVERNED-SIMULATION-AND-AUTHORITY-CONTINUITY-SWARM-001
lane: R9-8
title: "Conway R9 — Swarm Governance"
date: "2026-05-14"
visibility: internal
---

# Conway R9 — Swarm Governance

**Sprint:** CONWAY-R9-GOVERNED-SIMULATION-AND-AUTHORITY-CONTINUITY-SWARM-001
**Authority:** AGENTS.md AF9-AF15 | GOVERNANCE.md 26.8-26.13

---

## 1. R9 Sprint Scope

CONWAY-R9 adds the governed simulation and authority continuity layer to the
format-factory orchestration infrastructure. This is purely a **planning and
governance infrastructure sprint** — no source code implementation, no gate approval,
no commercial readiness claim.

### R9 Deliverables

| Lane | Deliverable | Purpose |
|------|-------------|---------|
| R9-0 | Preflight + overlap analysis | Confirm R9 prerequisites met |
| R9-1 | authority_continuity_registry.py + schema + tests | Track authoritative lineage |
| R9-2 | execution_simulator.py + tests | Simulate sprints without executing |
| R9-3 | planning-runtime-contract.schema.yaml | Schema for runtime contracts |
| R9-4 | cross-format-isolation-review.md | Verify isolation properties |
| R9-5 | stale_propagation.py + tests | Advanced stale severity tiers |
| R9-6 | format-governance-classification.schema.yaml | Classify formats in lifecycle |
| R9-7 | replay_lineage.py + tests | Hash-chained fingerprint history |
| R9-8 | Governance docs (this file + 2 others) | Governance documentation |
| R9-9 | Adversarial review (12+ cases) | Security/safety validation |

---

## 2. Governance Rules Applied in R9

### 2.1 No Source Implementation

R9 produces no source code in `src/net/` or `src/python/`. All deliverables are:
- Planning and governance tools (`tools/skills/`)
- Schemas (`schemas/skills/`)
- Reports (`reports/`)
- Documentation (`docs/`)
- Tests (`tests/skills/`)

### 2.2 No Gate Approval

R9 does NOT approve any gates. Gate 11 for FODS and FODT remains:
- Status: `commercial_readiness_in_progress`
- Approved: `false`
- `commercial_product_ready: false`

### 2.3 Dry-Run Only

All R9 tools enforce `dry_run_only: True` and `autonomous_execution_allowed: False`.
No subprocess calls. No file writes to src/.

### 2.4 Simulation Is Not Authorization

A simulation passing (`SIMULATION_PASS`) does not authorize implementation.
Implementation requires:
1. Human review of simulation results
2. Human authorization (explicit, in a separate session)
3. Execution by human-directed implementation sprint

### 2.5 Append-Only Records

- `simulation_log` in authority entries is append-only
- Replay lineage entries are append-only (new entries are built as new dicts)
- Prior records are never modified

---

## 3. No-Overlap Rules (R9 vs Prior Sprints)

| R9 Module | Prior Module | Relationship |
|-----------|-------------|--------------|
| authority_continuity_registry.py | None | NEW |
| execution_simulator.py | None | NEW |
| stale_propagation.py | stale_detection.py | EXTENSION — does NOT modify stale_detection.py |
| replay_lineage.py | replay_fingerprint.py | EXTENSION — does NOT modify replay_fingerprint.py |
| planning-runtime-contract.schema.yaml | None | NEW |
| authority-continuity.schema.yaml | None | NEW |
| format-governance-classification.schema.yaml | format-onboarding.schema.yaml | COMPLEMENTARY — separate schema |

**DUPLICATE_INFRASTRUCTURE: NONE**

---

## 4. Test Coverage Standards

R9 tests must follow the same standards as R7R8:

- Every new module has a corresponding test file
- All governance flags are tested for immutability
- Cross-format isolation is tested
- Append-only behavior is tested for simulation_log and lineage entries
- Governance invariants (no commercial_product_ready=True) are tested
- Live smoke tests use real dependencies where possible
- Mock-based tests verify blocked states (STALE_BLOCKED, BLOCKED_AUTHORITY)

---

## 5. Authority Chain for R9 Outputs

R9 outputs derive authority from:

1. **AGENTS.md AF9-AF15** — commercial readiness rules, AI usage policy, supervision methodology
2. **GOVERNANCE.md 26.8-26.13** — commercial readiness, gate discipline, AI governance
3. **R7R8 sprint outputs** — requirements authority (REQUIREMENTS_AUTHORITATIVE state)
4. **DEC-034** — IV sprint required before human gate review
5. **DEC-033 Option B** — .NET Commercial Only; no .NET FOSS packaging

R9 does NOT create new authority — it tracks and preserves existing authority continuity.

---

## 6. What R9 Does NOT Do

- Does NOT implement FODS or FODT parsers
- Does NOT change requirements authority state
- Does NOT approve Gate 11
- Does NOT claim commercial_product_ready = True
- Does NOT write to src/net/ or src/python/
- Does NOT modify stale_detection.py or replay_fingerprint.py
- Does NOT supersede or replace R7R8 deliverables
- Does NOT authorize autonomous implementation

---

## 7. R10 Readiness Considerations

R9 establishes the foundation for future sprints:

- Authority continuity registry enables R10 to track sprint-to-sprint lineage
- Execution simulator enables R10 to validate simulation before requesting human authorization
- Replay lineage enables R10 to detect unintended changes across sprints
- Format governance classification enables R10 to reason about expansion candidates
- Stale propagation tiers enable R10 to give actionable remediation guidance

**R9 does NOT make R10 decisions** — those remain human-authorized.

---

## 8. Governance Contact

For questions about this sprint's governance decisions:
- Primary authority: AGENTS.md, GOVERNANCE.md
- Sprint documentation: reports/governance/r9-preflight.md, r9-overlap-analysis.md
- Human review: Required before any implementation sprint

---

**SWARM_GOVERNANCE_DOC: COMPLETE**
**R9_8_STATUS: COMPLETE**
