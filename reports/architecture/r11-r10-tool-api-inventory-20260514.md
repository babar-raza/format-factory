# R11 — R10 Tool API Inventory
Sprint: FORMAT-FACTORY-R11-ACQUISITION-PLANNING-INTEGRATION-SWARM-001
Date: 2026-05-14
Lane: B

## Tool 1: acquisition_lifecycle_simulator.py

### Public Functions
| Function | Signature | Returns |
|----------|-----------|---------|
| `simulate_lifecycle_state` | `(fmt, current_state, spec_available, spec_type, support_matrix_audited, aspose_supported, requirements_state, stale_verdict, gates_passed, blockers, deferred_reason) -> dict` | Lifecycle simulation dict |
| `simulate_format_acquisition` | `(fmt, profile=None) -> dict` | Lifecycle simulation using profile dict |
| `simulate_multi_format_acquisition` | `(format_profiles: dict[str, dict]) -> dict` | Aggregate simulation for multiple formats |
| `simulate_standard_formats` | `() -> dict` | Simulate all KNOWN_FORMAT_PROFILES |

### Public Constants
| Constant | Type | Value |
|----------|------|-------|
| `KNOWN_FORMAT_PROFILES` | `dict[str, dict]` | 7 profiles: fods, fodt, hwpx, hwp, alz, egg, hwt |
| `STATE_CANDIDATE` through `STATE_DEFERRED` | str constants | 12 lifecycle state strings |
| `STATE_ORDER` | dict | Maps state → ordering integer (0-9, -1, -2) |
| `_GOVERNANCE_FLAGS` | dict | Immutable governance invariants |

### Output Keys (simulate_lifecycle_state)
`format_id`, `current_state`, `state_order`, `next_state`, `is_terminal`, `is_blocked`,
`spec_available`, `spec_type`, `support_matrix_audited`, `aspose_supported`,
`requirements_state`, `stale_verdict`, `gates_passed`, `active_blockers`,
`deferred_reason`, `next_actions`, `evidence_requirements`, `required_gates`,
`simulation_id`, `simulation_note`, `governance`, `dry_run_only`,
`autonomous_execution_allowed`, `simulated_date`

### Governance
- `dry_run_only: True`
- `simulation_only: True`
- `autonomous_execution_allowed: False`
- `gate_self_approval_allowed: False`

---

## Tool 2: candidate_format_backlog.py

### Public Functions
| Function | Signature | Returns |
|----------|-----------|---------|
| `get_backlog` | `() -> list[dict]` | Full backlog (immutable copy) |
| `get_candidates_by_tier` | `(tier: str) -> list[dict]` | Candidates filtered by tier |
| `get_candidates_by_category` | `(category: str) -> list[dict]` | Candidates by category |
| `get_candidates_by_audit_status` | `(status: str) -> list[dict]` | Candidates by audit status |
| `get_candidates_by_spec_type` | `(spec_type: str) -> list[dict]` | Candidates by spec type |
| `get_format` | `(format_id: str) -> dict | None` | Single format lookup |
| `classify_backlog` | `() -> dict` | Full classification summary |
| `validate_backlog_integrity` | `() -> dict` | Integrity check (violations list) |

### Public Constants
| Constant | Type | Value |
|----------|------|-------|
| `ALL_BACKLOG` | list | 51 entries: 2 ACTIVE + 19 TIER_A + 16 TIER_B + 14 TIER_C |
| `ACTIVE_FORMATS` | list | [fods, fodt] |
| `TIER_A_CANDIDATES` | list | 19 near-term candidates |
| `TIER_B_CANDIDATES` | list | 16 medium-term candidates |
| `TIER_C_CANDIDATES` | list | 14 long-term candidates |
| `TIER_A_NEAR_TERM` | str | "TIER_A_NEAR_TERM" |
| `TIER_ACTIVE` | str | "TIER_ACTIVE" |

### Entry Dict Keys
`format_id`, `extension`, `category`, `tier`, `spec_type`, `notes`, `audit_status`,
`aspose_supported` (None until audited), `acquisition_state`

### Audit Safety
- `aspose_supported` is `None` for all `needs_audit` entries
- `AUDIT_STATUS_NEEDS_AUDIT` = "needs_audit" (default for all candidates)
- Violations detected by `validate_backlog_integrity()`

---

## Tool 3: public_spec_readiness_scorer.py

### Public Functions
| Function | Signature | Returns |
|----------|-----------|---------|
| `score_format` | `(fmt, spec_type, category, sample_files_known, legal_use_clear, open_source_reference, existing_parsers_known, binary_format) -> dict` | Single format score |
| `score_multiple_formats` | `(format_specs: list[dict]) -> dict` | Multi-format scoring, ranked |
| `score_standard_candidates` | `() -> dict` | Score all STANDARD_CANDIDATE_SPECS |

### Public Constants
| Constant | Type |
|----------|------|
| `STANDARD_CANDIDATE_SPECS` | list of 10 scoring specs |
| `DIMENSION_WEIGHTS` | dict (8 weights summing to 1.0) |
| `READINESS_NOT_READY` through `READINESS_ACQUISITION_READY` | str tier constants |

### Score Output Keys
`format_id`, `score_id`, `composite_score`, `readiness_tier`, `dimension_scores`,
`dimension_weights`, `spec_type`, `category`, `binary_format`, `sample_files_known`,
`legal_use_clear`, `open_source_reference`, `existing_parsers_known`,
`recommendations`, `score_note`, `governance`, `dry_run_only`

### Score Dimensions (weights)
`spec_availability` (0.20), `spec_completeness` (0.15), `complexity` (0.10),
`sample_availability` (0.10), `legal_clarity` (0.15), `parser_feasibility` (0.15),
`oracle_feasibility` (0.05), `requirements_gen_readiness` (0.10)

### Readiness Tiers
- NOT_READY: score ≤ 3.0
- NEEDS_INVESTIGATION: score ≤ 5.0
- CANDIDATE_READY: score ≤ 7.0
- ACQUISITION_READY: score > 7.0

---

## Tool 4: multi_format_acquisition_planner.py

### Public Functions
| Function | Signature | Returns |
|----------|-----------|---------|
| `plan_format_group` | `(group_name, formats=None, lifecycle_state=None, spec_type=None, parallelizable=None, sequencing=None, notes="") -> dict` | Single group plan |
| `plan_all_groups` | `(custom_overrides=None) -> dict` | All 5 predefined groups |
| `plan_active_and_candidate_groups` | `() -> dict` | Alias for plan_all_groups() |
| `get_group_definition` | `(group_name: str) -> dict | None` | Group definition copy |

### Group Names
`active_formats`, `korean_word_processing`, `archive`, `document`, `image`

### Plan Output Keys
`plan_id`, `group_name`, `formats`, `format_count`, `lifecycle_state`, `spec_type`,
`parallelizable`, `sequencing_recommendation`, `estimated_sprint_count`,
`gates_remaining`, `blockers`, `recommendations`, `notes`, `governance`,
`dry_run_only`, `plan_note`

### Key Behavior
- `parallelizable=False` for `korean_word_processing` (hwpx→hwp→hwt sequential)
- `blockers` includes `reverse_engineering_requires_legal_review` for archive group
- `plan_note`: "SIMULATION ESTIMATE — not a commitment or authorization to execute."

---

## Tool 5: implementation_simulation_v2.py

### Public Functions
| Function | Signature | Returns |
|----------|-----------|---------|
| `build_dependency_graph` | `(fmt, formats_in_group=None) -> dict` | Dependency graph |
| `build_taskcard_graph` | `(fmt, gates_completed=None) -> dict` | Task card graph |
| `build_evidence_graph` | `(fmt) -> dict` | Evidence artifact graph |
| `build_replay_lineage_graph` | `(fmt, sprint_ids=None) -> dict` | Hash-chained lineage |
| `build_stale_state_graph` | `(fmt) -> dict` | Stale propagation graph |
| `build_authority_graph` | `(fmt) -> dict` | Authority chain graph |
| `simulate_v2` | `(fmt, formats_in_group=None, gates_completed=None, sprint_ids=None) -> dict` | All 6 graphs |
| `simulate_v2_standard_formats` | `() -> dict` | All 6 graphs × 6 formats |

### Graph Output Keys (per graph)
`graph_id`, `graph_type`, `format`, `nodes`, `edges`, `node_count`, `edge_count`, `governance`, `dry_run_only`, `graph_note`

### simulate_v2 Output Keys
`simulation_id`, `format`, `graphs`, `graph_types`, `total_nodes`, `total_edges`,
`gate_11_approved` (False), `governance`, `dry_run_only`, `autonomous_execution_allowed`, `simulation_note`

---

## Cross-Tool Dependencies

```
candidate_format_backlog.ALL_BACKLOG
  → (tier filter) → candidates list
  → public_spec_readiness_scorer.score_multiple_formats()
  → ranked candidate list (top candidate selection)

KNOWN_FORMAT_PROFILES[top_candidate]
  → acquisition_lifecycle_simulator.simulate_format_acquisition()
  → lifecycle state simulation

multi_format_acquisition_planner.plan_all_groups()
  → multi-format planning context

implementation_simulation_v2.simulate_v2(top_candidate)
  → 6 simulation graphs

COMBINED → PlanningBundle
```

---

## Known Limitations

1. `aspose_supported` is `None` for all TIER_A+ candidates — audit not yet performed
2. `score_standard_candidates()` covers only 10 of 19 TIER_A candidates; rest scored with derived defaults
3. `simulate_v2` produces simulated graphs only — no real execution artifacts
4. `plan_all_groups()` plan estimates are not commitments; sprint counts are heuristic
5. All tools operate on `dry_run_only=True`; no internet access, no source mutation

---

## Lane B Verdict
LANE_B_PASS
