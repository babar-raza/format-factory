# Acquisition Graph Simulation Report
Sprint: FORMAT-FACTORY-R12-ACQUISITION-ENGINE-IV-AND-ZST-GOVERNED-READINESS-SWARM-001
Lane: E
Date: 2026-05-14
Status: COMPLETE

> **SIMULATION ONLY** — All graph outputs are planning artifacts, not acquisition authorizations.
> No implementation, no source mutation, no gate approval.

---

## New Tool: tools/skills/acquisition_graph_simulator.py

Produces 6 acquisition-layer graph types for any format candidate.
Designed to complement `implementation_simulation_v2.py` (which focuses on the implementation layer).

---

## Graph Types

### Graph 1: Acquisition Dependency Graph
Shows prerequisite state relationships for a format's 10-state acquisition lifecycle.
- **Nodes:** 12 (10 lifecycle states + BLOCKED + DEFERRED)
- **Edges:** 9 (sequential prerequisites)
- **Use:** Audit acquisition progression feasibility

### Graph 2: Onboarding Transition Graph
State machine view starting from current state — marks PAST/CURRENT/FUTURE states.
- **Use:** Sprint planning for next acquisition advance

### Graph 3: Stale Propagation Graph
Models how a stale spec or requirements document propagates downstream.
- **Key finding:** If `SPEC_NORMALIZATION` goes stale (spec version changes), 7 downstream states are affected (NORMALIZATION through EVIDENCE_READY)
- **Use:** Change-impact analysis for spec updates

### Graph 4: Evidence Dependency Graph
Maps required evidence artifacts to each lifecycle state.
- **Total evidence artifacts tracked:** varies by state; 23 total across 10 states
- **Use:** Evidence planning and sprint requirements generation

### Graph 5: Replay Lineage Graph
Sprint-to-sprint replay chain for audit trail.
- **Default chain:** R10-POC → R10-Closure → R11-Integration → R12-IV
- **Use:** Replay verification and audit trail

### Graph 6: Verification Dependency Graph
DEC-034 IV dependency tracking.
- **IV stages:** DEC034_IV (after requirements), human_review (after planning_ready), gate_11_sub_gates (after evidence_ready)
- **Use:** IV sprint sequencing

---

## ZST Simulation Results

### ZST Dependency Graph
- Current state: CANDIDATE
- Next required state: SUPPORT_MATRIX_AUDIT
- No active blockers

### ZST Stale Propagation (from SPEC_NORMALIZATION)
If ZST spec (RFC 8878) changes version:
- Affected states: SPEC_NORMALIZATION, REQUIREMENTS_GENERATION, VERIFIER_REVIEW, DEC034_IV, PLANNING_READY, IMPLEMENTATION_SIMULATION, EVIDENCE_READY (7 states)
- Stale trigger: `spec_version_changed`
- Recovery: Re-run spec normalization sprint + downstream

### ZST Evidence Summary

| State | Evidence Count | Key Evidence |
|-------|---------------|--------------|
| CANDIDATE | 2 | format_id_confirmed, backlog_entry_created |
| SUPPORT_MATRIX_AUDIT | 2 | audit_report, aspose_coverage_determined |
| SPEC_DISCOVERY | 2 | spec_location, legal_access_confirmed |
| SPEC_NORMALIZATION | 3 | cached_locally, hash_recorded, normalization_report |
| REQUIREMENTS_GENERATION | 3 | ai_reqs, schema_validation, evidence_bundle |
| VERIFIER_REVIEW | 2 | verifier_report, lane_r5_pass |
| DEC034_IV | 3 | iv_sprint_complete, iv_bundle, separate_session |
| PLANNING_READY | 2 | requirements_authoritative, human_review |
| IMPLEMENTATION_SIMULATION | 3 | vertical_slice_plan, oracle_confirmed, sim_report |
| EVIDENCE_READY | 3 | evidence_bundle, bundle_validation, gate_11_subgates |
| **TOTAL** | **25** | |

---

## Multi-Format Isolation Validation

Tested all 19 TIER_A format candidates for graph isolation:
- **Result:** PASS — 0 violations
- All format node IDs are namespaced by format_id
- No shared graph nodes across formats

---

## Test Results

**52 tests, all PASS**
- TestModuleImport (6)
- TestSimulateAcquisitionGraphs (9)
- TestAcquisitionDependencyGraph (6)
- TestOnboardingTransitionGraph (5)
- TestStalePropagationGraph (5)
- TestEvidenceDependencyGraph (5)
- TestReplayLineageGraph (5)
- TestVerificationDependencyGraph (4)
- TestMultiFormatIsolation (4)
- TestGraphDeterminism (3)

---

## Governance

All graph outputs include:
- `governance.commercial_product_ready: false`
- `governance.dry_run_only: true`
- `governance.simulation_only: true`
- `governance.acquisition_not_authorized: true`
- `simulation_note: "SIMULATION — [...] Not an acquisition authorization"`

**ACQUISITION_GRAPH_SIMULATION_STATUS: COMPLETE**
