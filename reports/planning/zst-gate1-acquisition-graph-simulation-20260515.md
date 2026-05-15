# ZST Gate 1 Acquisition Graph Simulation
Sprint: FORMAT-FACTORY-R13-ZST-SUPPORT-MATRIX-AUDIT-SIMULATION-AND-GATE1-PACKET-SWARM-001
Lane: G (Acquisition Graph Simulation)
Date: 2026-05-15

## SIMULATION ONLY — No Acquisition Authorized — acquisition_not_authorized=true

All graphs are deterministic simulation outputs. No graph is an authorization.
Commercial_product_ready: false. Gate self-approval: not allowed.

---

## Simulation Parameters

Tool: tools/skills/acquisition_graph_simulator.py (R12 Lane E deliverable)
Formats simulated: zst (primary), ora (fallback), gnumeric (fallback)
Graph types: 6 (dependency, onboarding, stale_propagation, evidence_dependency, replay_lineage, verification_dependency)

## Path 1: ZST Candidate-Only (Current State)

**State: CANDIDATE**
**Gate 1 status: NOT_STARTED**

```
ZST Onboarding Transition Graph (CANDIDATE → path not yet taken):
  zst:CANDIDATE
    │
    ▼  [requires: Gate 1 human approval + support-matrix audit authorization]
  zst:SUPPORT_MATRIX_AUDIT
    │
    ▼  [requires: spec retrieval authorization]
  zst:SPEC_DISCOVERY
    │
    ▼  [requires: spec cached, legal notes complete]
  zst:SPEC_NORMALIZATION
    │
    ▼  [requires: human authorization for AI req gen]
  zst:REQUIREMENTS_GENERATION
    │
    ▼  [requires: verifier review]
  zst:VERIFIER_REVIEW
    │
    ▼  [requires: DEC-034 IV sprint]
  zst:DEC034_IV
    │
    ▼  [requires: planning sprint]
  zst:PLANNING_READY
    │
    ▼  [requires: implementation authorization]
  zst:IMPLEMENTATION_SIMULATION
    │
    ▼  [requires: evidence review]
  zst:EVIDENCE_READY
```

Simulator output:
- nodes: 10
- edges: 9
- current_state: CANDIDATE
- governance.acquisition_not_authorized: true
- governance.dry_run_only: true

**The ZST path is BLOCKED at CANDIDATE until Gate 1 is approved by Babar Raza.**
All downstream nodes exist in the simulation but are NOT authorized.

---

## Path 2: ZST Gate 1 Approved-But-Not-Acquired (Hypothetical)

**State: Hypothetical — Gate 1 has NOT been approved. This path shows what WOULD happen.**

If Babar approves Gate 1, the next authorized state is SUPPORT_MATRIX_AUDIT.

```
[HYPOTHETICAL: if Gate 1 approved]
  zst:CANDIDATE → GATE_1_APPROVED (human record in registry)
                → zst:SUPPORT_MATRIX_AUDIT (R13B sprint authorized)
```

The acquisition dependency graph for ZST shows:
- 12 nodes representing the full acquisition lifecycle
- 9 edges showing sequential dependencies
- governance.simulation_only: true at every node
- No implementation authorized until PLANNING_READY state is reached

---

## Path 3: ZST Deferred

**State: DEFERRED (if Babar chooses to defer ZST)**

```
  zst:CANDIDATE → zst:DEFERRED
    │
    └── ORA or GNUMERIC becomes next candidate
        ora:CANDIDATE → [Gate 1 authorization required for ORA]
```

Simulator output:
- build_onboarding_transition_graph('zst', STATE_DEFERRED)
- current_state: DEFERRED
- nodes: 10 (all present but current_state shows DEFERRED)
- ZST can be re-activated at a future sprint by human decision

---

## Path 4: Alternative Candidate (ORA as next)

**If ZST is deferred, ORA becomes the default next candidate.**

ORA acquisition dependency graph:
- 12 nodes (same lifecycle structure as ZST)
- Format-specific data: category=image, spec_type=full_public
- governance.acquisition_not_authorized: true (same constraint)

ORA Onboarding from CANDIDATE would follow the same path:
```
  ora:CANDIDATE → ora:SUPPORT_MATRIX_AUDIT → ora:SPEC_DISCOVERY → ...
```

**ORA has a strategic advantage: ZIP+XML package format → reuses FODS/FODT pipeline infrastructure.**

---

## Path 5: ZST Blocked (If Support-Matrix Reveals Contradiction)

**State: BLOCKED**

If the real support-matrix audit (R13B) reveals:
- RFC 8878 has unexpected IP restriction
- Aspose support model creates commercial conflict
- Sample availability proves insufficient

```
  zst:SUPPORT_MATRIX_AUDIT → zst:BLOCKED
    │
    └── Blocking reason recorded in acquisition pack
    └── ORA or GNUMERIC activated as next candidate
```

Simulator output:
- build_onboarding_transition_graph('zst', STATE_BLOCKED)
- nodes: 10 (all present; current_state: BLOCKED)

---

## Path 6: acquisition_not_authorized=false Attempted Without Human Approval

**This path is FORBIDDEN. The graph simulator confirms it is blocked.**

If any agent attempts to set acquisition_not_authorized=False without human approval:
```
  GOVERNANCE BLOCK:
    gate_self_approval_allowed: false
    autonomous_execution_allowed: false
    dry_run_only: true
    acquisition_not_authorized: true
```

The acquisition_planning_runtime.py enforces this via ValueError on dry_run=False.
The graph simulator reflects governance state: graphs_are_simulation_outputs_not_authorizations=true.

---

## Path 7: Multi-Format Isolation Proof

**Confirms ZST, ORA, and Gnumeric tracks are isolated (no cross-contamination).**

```python
simulate_multi_format_isolation(['zst', 'ora', 'gnumeric'])
Result:
  checked_formats: ['zst', 'ora', 'gnumeric']
  total_nodes: 36  (12 per format × 3)
  violations: []
  isolation_valid: True
```

**ISOLATION_VALID: True — all three candidate tracks are independent.**
No shared nodes. No cross-contamination between acquisition paths.
Gate approval for one format does not affect any other format's state.

---

## Simulation Summary

| Path | Graph Type | Nodes | Edges | Current State | Authorized |
|------|-----------|-------|-------|---------------|-----------|
| 1: ZST candidate-only | onboarding_transition | 10 | 9 | CANDIDATE | NO |
| 2: ZST Gate 1 approved (hypothetical) | dependency | 12 | 9 | SUPPORT_MATRIX_AUDIT | NOT YET |
| 3: ZST deferred | onboarding_transition | 10 | — | DEFERRED | N/A |
| 4: ORA alternative | dependency | 12 | 9 | CANDIDATE | NO |
| 5: ZST blocked | onboarding_transition | 10 | — | BLOCKED | N/A |
| 6: unauthorized attempt | governance-blocked | — | — | BLOCKED | FORBIDDEN |
| 7: multi-format isolation | isolation | 36 | — | ISOLATED | — |

Full ZST simulation (simulate_acquisition_graphs):
- simulation_id: 0795349d9caa2bec
- graph_count: 6
- total_nodes: 77
- total_edges: 55
- governance.commercial_product_ready: False
- governance.acquisition_not_authorized: True

## Governance Confirmation
All 6 governance flags confirmed across all simulation paths:
- commercial_product_ready: False
- autonomous_execution_allowed: False
- gate_self_approval_allowed: False
- dry_run_only: True
- simulation_only: True
- acquisition_not_authorized: True
