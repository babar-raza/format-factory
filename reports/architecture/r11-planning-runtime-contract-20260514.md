# R11 Planning Runtime Integration Contract
Sprint: FORMAT-FACTORY-R11-ACQUISITION-PLANNING-INTEGRATION-SWARM-001
Date: 2026-05-14
Lane: B

## Entrypoint Contract

```python
def run_acquisition_planning(
    tier: str = "TIER_A",
    top_n: int = 5,
    dry_run: bool = True,
) -> dict:
    """
    Run the unified acquisition planning pipeline.

    Parameters
    ----------
    tier : str
        Tier to select candidates from: "TIER_A", "TIER_B", "TIER_C", "TIER_ACTIVE"
        Raises ValueError for unknown tier.
    top_n : int
        Maximum number of candidates to include in ranking output (1-51).
    dry_run : bool
        Must always be True (enforced). False raises ValueError.

    Returns
    -------
    dict — PlanningBundle with all required fields below.
    """
```

## PlanningBundle Output Contract

Required fields:

| Field | Type | Description |
|-------|------|-------------|
| `bundle_id` | str | SHA-256 hash (deterministic) |
| `tier` | str | Input tier string |
| `top_n` | int | Input top_n |
| `dry_run_only` | bool | Always True |
| `simulation_only` | bool | Always True |
| `candidate_ranking` | list[dict] | Ranked candidates [{format_id, score, readiness_tier}] |
| `selected_first_candidate` | str | format_id of top candidate |
| `first_candidate_readiness_score` | float | Composite readiness score |
| `first_candidate_rationale` | str | Why this candidate was selected |
| `first_candidate_blockers` | list[str] | Active blockers |
| `first_candidate_required_evidence` | list[str] | Required evidence to proceed |
| `first_candidate_proposed_acquisition_lanes` | list[str] | Proposed sprint lanes |
| `first_candidate_risks` | list[str] | Known risks |
| `first_candidate_non_goals` | list[str] | Explicit non-goals |
| `lifecycle_simulation` | dict | Lifecycle state simulation for first candidate |
| `simulation_graph_summary` | dict | v2 graph summary (node/edge counts per graph type) |
| `multi_format_plan` | dict | plan_all_groups() output |
| `governance` | dict | Governance flags (immutable) |
| `next_recommended_sprint` | str | Recommended next sprint name |

## Governance Invariants (Enforced)

```python
PLANNING_BUNDLE_GOVERNANCE = {
    "commercial_product_ready": False,
    "autonomous_execution_allowed": False,
    "gate_self_approval_allowed": False,
    "dry_run_only": True,
    "simulation_only": True,
    "no_internet_access": True,
    "no_source_mutation": True,
    "scores_are_estimates_not_decisions": True,
}
```

## Tier Mapping

| Input tier | Internal constant |
|------------|------------------|
| "TIER_A" | TIER_A_NEAR_TERM = "TIER_A_NEAR_TERM" |
| "TIER_B" | TIER_B_MEDIUM_TERM = "TIER_B_MEDIUM_TERM" |
| "TIER_C" | TIER_C_LONG_TERM = "TIER_C_LONG_TERM" |
| "TIER_ACTIVE" | TIER_ACTIVE = "TIER_ACTIVE" |
| unknown | Raises ValueError |

## Scoring for Non-STANDARD candidates

For TIER_A candidates not in STANDARD_CANDIDATE_SPECS, derive scorer inputs from backlog entry:
- `binary_format`: True if spec_type == "reverse_engineering"
- `sample_files_known`: True if spec_type in ("full_public", "partial_public", "community_documented")
- `legal_use_clear`: True if spec_type == "full_public"
- `open_source_reference`: False (unknown unless stated)
- `existing_parsers_known`: False (unknown unless stated)

## Error Handling

- Unknown tier: `raise ValueError(f"Unknown tier: {tier}. Valid: TIER_A, TIER_B, TIER_C, TIER_ACTIVE")`
- dry_run=False: `raise ValueError("dry_run must be True — runtime is simulation-only")`
- Empty candidates: Return bundle with empty ranking and `selected_first_candidate: None`

## Integration Sequence

1. Validate inputs (tier, top_n, dry_run)
2. Map tier string → internal tier constant
3. Get candidates from backlog: `get_candidates_by_tier(tier_constant)`
4. Build scoring specs from backlog entries (augmented with STANDARD_CANDIDATE_SPECS where available)
5. Score all candidates: `score_multiple_formats(specs)`
6. Take top_n from ranked list
7. Select first candidate (highest score)
8. Lookup lifecycle profile: `KNOWN_FORMAT_PROFILES.get(first_candidate, {})`
9. Simulate lifecycle: `simulate_format_acquisition(first_candidate, profile)`
10. Simulate v2 graphs: `simulate_v2(first_candidate)`
11. Get multi-format plan: `plan_all_groups()`
12. Build and return PlanningBundle

## Prohibited Actions

The runtime MUST NOT:
- Fetch internet resources
- Write to src/net/ or src/python/
- Approve gates
- Set commercial_product_ready=True
- Set gate_11_approved=True
- Persist tokens or credentials
- Execute real acquisition steps

## Lane B Verdict
LANE_B_PASS
