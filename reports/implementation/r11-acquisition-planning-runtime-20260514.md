# R11 Acquisition Planning Runtime — Implementation Report
Sprint: FORMAT-FACTORY-R11-ACQUISITION-PLANNING-INTEGRATION-SWARM-001
Date: 2026-05-14
Lane: C

## Runtime Created

**File:** `tools/skills/acquisition_planning_runtime.py`
**Tests:** `tests/skills/test_acquisition_planning_runtime.py`

---

## Entrypoint

```python
run_acquisition_planning(
    tier: str = "TIER_A",
    top_n: int = 5,
    dry_run: bool = True,
) -> dict  # PlanningBundle
```

---

## R10 Tools Consumed

| Tool | How Used |
|------|----------|
| `acquisition_lifecycle_simulator.KNOWN_FORMAT_PROFILES` | Profile lookup for first candidate lifecycle simulation |
| `acquisition_lifecycle_simulator.simulate_format_acquisition` | Lifecycle state simulation for first candidate |
| `candidate_format_backlog.get_candidates_by_tier` | Candidate selection by tier |
| `public_spec_readiness_scorer.score_multiple_formats` | Candidate ranking by readiness score |
| `public_spec_readiness_scorer.STANDARD_CANDIDATE_SPECS` | Known scoring specs (augments backlog entries) |
| `multi_format_acquisition_planner.plan_all_groups` | Multi-format planning context |
| `implementation_simulation_v2.simulate_v2` | 6-graph simulation for first candidate |

---

## Integration Sequence

1. Validate inputs (tier, top_n, dry_run=True enforced)
2. Map tier string → internal tier constant
3. `get_candidates_by_tier(tier_constant)` → candidates list
4. Build scoring specs from backlog entries (STANDARD_CANDIDATE_SPECS used where available)
5. `score_multiple_formats(specs)` → ranked scores
6. Select top_n from ranking; first candidate = highest score
7. `simulate_format_acquisition(first_candidate, profile)` → lifecycle state
8. `simulate_v2(first_candidate)` → 6-graph simulation
9. `_build_graph_summary(sim_v2)` → concise graph node/edge counts
10. `plan_all_groups()` → multi-format planning context
11. Assemble PlanningBundle with all outputs

---

## TIER_A Default Result

With default inputs (tier="TIER_A", top_n=5):

| Rank | Format | Score | Readiness Tier |
|------|--------|-------|---------------|
| 1 | zst | 8.95 | ACQUISITION_READY |
| 2 | gnumeric | 8.75 | ACQUISITION_READY |
| 3 | abw | 8.75 | ACQUISITION_READY |
| 4 | zpaq | 8.70 | ACQUISITION_READY |
| 5 | qoi | 8.60 | ACQUISITION_READY |

Selected first candidate: **zst** (Zstandard compression, archive category, full_public spec, score=8.95)

---

## Governance Enforcement

All governance invariants are hardcoded and verified by tests:

| Flag | Value |
|------|-------|
| `dry_run_only` | True (raises ValueError if dry_run=False) |
| `simulation_only` | True |
| `commercial_product_ready` | False |
| `autonomous_execution_allowed` | False |
| `gate_self_approval_allowed` | False |
| `no_internet_access` | True |
| `no_source_mutation` | True |

---

## Tests

**File:** `tests/skills/test_acquisition_planning_runtime.py`
**Count:** 80 tests
**Categories:** import integration, input validation, output structure, first candidate,
lifecycle simulation, graph summary, multi-format plan, governance invariants,
source mutation check, determinism, tier-specific behavior, candidate blockers,
next recommended sprint

**Result: 80 PASS**

---

## Prohibited Actions Confirmed

- No internet fetches
- No src/net/ or src/python/ mutations
- No gate approvals
- dry_run=False raises ValueError
- Unknown tier raises ValueError
- _GOVERNANCE_FLAGS immutable to external mutation

---

## Lane C Verdict

**LANE_C_PASS_RUNTIME_IMPLEMENTED**
