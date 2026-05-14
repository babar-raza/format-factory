# R11 First-Candidate Acquisition Plan
Sprint: FORMAT-FACTORY-R11-ACQUISITION-PLANNING-INTEGRATION-SWARM-001
Date: 2026-05-14
Lane: D
Mode: DRY_RUN / SIMULATION_ONLY

> This plan is a SIMULATION ESTIMATE only. No acquisition has been executed.
> Human review and explicit authorization required at each gate.
> Gate 11 NOT APPROVED. commercial_product_ready: false.

---

## Selected First Candidate

**Format:** ZST (Zstandard compression)
**Format ID:** `zst`
**Extension:** `.zst`
**Category:** archive
**Readiness Score:** 8.95 / 10 (ACQUISITION_READY)
**Readiness Tier:** ACQUISITION_READY
**Spec Type:** full_public

---

## Why ZST is the First Candidate

| Criterion | Value | Notes |
|-----------|-------|-------|
| Spec availability | 10/10 | RFC 8878 — IETF publicly available spec |
| Spec completeness | 9/10 | Complete specification |
| Complexity | 7/10 | Archive category — simpler structure than word processing |
| Sample availability | 8/10 | Widely available test corpus |
| Legal clarity | 9/10 | Public RFC — clear legal provenance |
| Parser feasibility | 10/10 | zstd OSS reference implementation (Meta) |
| Oracle feasibility | 7/10 | Round-trip testing feasible with reference impl |
| Requirements gen readiness | 9/10 | Full public spec with legal clarity |
| **Composite** | **8.95/10** | **ACQUISITION_READY** |

---

## Current Lifecycle State

**State:** CANDIDATE
**Next State:** SUPPORT_MATRIX_AUDIT
**Is Blocked:** No
**Active Blockers:** None
**Aspose Supported:** None (not yet audited — `needs_audit`)

---

## Acquisition Lane Plan

Proposed sequential lanes for ZST acquisition (simulation only):

| Lane | Action | Gate |
|------|--------|------|
| 1 | Support-matrix audit for ZST against current Aspose libraries | Gate 1+2 |
| 2 | Spec discovery — cache RFC 8878 locally (AGENTS.md Section T) | Gate 3 |
| 3 | Legal clearance review for ZST spec access | Gate 3 blocker |
| 4 | Spec normalization — extract structure and encoding rules | Gate 4 |
| 5 | Requirements generation from normalized spec (AI-assisted) | Gate 5+6 |
| 6 | Verifier review (LANE_R5) | Gate 7 |
| 7 | DEC-034 independent verification sprint (separate session) | Gate 8 |
| 8 | Planning bundle + implementation simulation | Gate 9+10 |
| 9 | Evidence bundle build and validation | EVIDENCE_READY |
| 10 | Gate 11 sub-gate preparation (human review required) | Gate 11 |

---

## Required Evidence Before Proceeding

1. `BUNDLE_VALIDATION: PASS` — evidence bundle for ZST support-matrix audit sprint
2. `METADATA_IDENTITY: CONSISTENT (sprint_id matching)` — all artifacts match sprint ID
3. `No src/net/ or src/python/ mutations` — product source untouched
4. Aspose support matrix audit result documented in backlog
5. Spec discovery result: RFC 8878 URI + download verification

---

## Blockers

None active at CANDIDATE state. Potential blockers at downstream gates:

| Gate | Potential Blocker |
|------|------------------|
| SPEC_DISCOVERY | `spec_format_unknown` — if RFC format not parseable by tooling |
| REQUIREMENTS_GENERATION | `ai_synthesis_failed` — if spec normalization is incomplete |
| DEC034_IV | `separate_session_required` — IV sprint must run in separate session |
| PLANNING_READY | `requirements_not_authoritative` — if DEC-034 IV not passed |

---

## Risks

1. `[RISK] aspose_supported is None` — audit required before DEC-033 compatibility is known. ZST may or may not be in Aspose's current product matrix.
2. `[RISK] Requirements generation has not started` — REQUIREMENTS_AUTHORITATIVE state not yet reached for ZST.
3. `[RISK] RFC 8878 is the spec authority, but frame format extensions may require additional discovery` — partial spec completeness risk.
4. `[RISK] Zstandard has multiple versions (v0.1–v1.5.5)` — versioned format may complicate round-trip oracle design.

---

## Non-Goals

1. `[NON-GOAL]` Do NOT begin ZST implementation until PLANNING_READY state is reached
2. `[NON-GOAL]` Do NOT approve Gate 11 for any format (requires human review)
3. `[NON-GOAL]` Do NOT set commercial_product_ready=True
4. `[NON-GOAL]` Do NOT fetch RFC 8878 from internet during this sprint (requires separate spec-cache sprint)
5. `[NON-GOAL]` Do NOT execute autonomous rollout
6. `[NON-GOAL]` Do NOT modify src/net/ or src/python/ product sources

---

## Simulation Graph Summary

Produced by: `simulate_v2("zst")`

| Graph Type | Nodes | Edges |
|-----------|-------|-------|
| dependency_graph | 12 | 11 |
| taskcard_graph | 40 | 59 |
| evidence_graph | 20 | 19 |
| replay_lineage_graph | 5 | 4 |
| stale_state_graph | 5 | 4 |
| authority_graph | 8 | 7 |
| **Total** | **90** | **104** |

Gate 11 NOT APPROVED. All graphs are simulation planning estimates.

---

## Second Choice Candidates

If ZST acquisition is blocked or deferred, the recommended second choice is:
- **gnumeric** (score=8.75, full_public XML spec, FOSS, spreadsheet category)
- **abw** (score=8.75, full_public XML spec, FOSS, word_processing category)

---

## Next Human Decision Required

> **ACTION REQUIRED:** Review this acquisition plan before authorizing ZST acquisition sprint.
>
> 1. Confirm ZST is within scope for format acquisition (no business objection)
> 2. Confirm Aspose support matrix audit is the correct first step
> 3. Authorize R12 acquisition evidence pack sprint in a new session

---

## Governance State

| Flag | Value |
|------|-------|
| `commercial_product_ready` | false |
| `gate_11_approved` | false |
| `autonomous_execution_allowed` | false |
| `dry_run_only` | true |
| `simulation_only` | true |
| Actual acquisition executed | NO |
| Internet resources fetched | NO |

---

## Lane D Verdict

**LANE_D_PASS_PLAN_CREATED**

*This document is a SIMULATION POC artifact. All assessments are estimates.*
*Authority: FORMAT-FACTORY-R11-ACQUISITION-PLANNING-INTEGRATION-SWARM-001*
