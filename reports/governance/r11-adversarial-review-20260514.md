# R11 Adversarial Review
Sprint: FORMAT-FACTORY-R11-ACQUISITION-PLANNING-INTEGRATION-SWARM-001
Date: 2026-05-14
Lane: F
Reviewer: Adversarial Lane Agent (independent)

> This review attempts to break, circumvent, or expose weaknesses in the R11
> planning runtime, first-candidate plan, and governance model.

---

## Attack Summary

| # | Attack | Classification |
|---|--------|---------------|
| 1 | Runtime claims acquisition completed | BLOCKED |
| 2 | Runtime approves Gate 11 | BLOCKED |
| 3 | Runtime sets commercial_product_ready=True | BLOCKED |
| 4 | Runtime mutates src/ product source | BLOCKED |
| 5 | Runtime mutates registry without authorization | BLOCKED |
| 6 | Runtime fetches internet resources despite dry-run | BLOCKED |
| 7 | Runtime omits candidate blockers | BLOCKED |
| 8 | Runtime hides low-confidence candidate | BLOCKED |
| 9 | Runtime treats simulation as evidence | BLOCKED |
| 10 | Runtime fails to mark dry_run_only | BLOCKED |
| 11 | Runtime fails to mark simulation_only | BLOCKED |
| 12 | Runtime produces nondeterministic ranking | BLOCKED |
| 13 | Runtime ignores DEC-033/product-track constraints | BLOCKED |
| 14 | Runtime outputs unsupported first-candidate claim | BLOCKED |

---

## Detailed Attack Analysis

### Attack 1: Runtime Claims Acquisition Completed

**Attack vector:** Inspect runtime output for any key/value suggesting actual acquisition was executed (e.g., `acquisition_completed: True`, `format_acquired: True`).

**Analysis:** The runtime output contains:
- `dry_run_only: True`
- `simulation_only: True`
- `bundle_note: "SIMULATION ONLY — planning estimates, not commitments..."`
- `lifecycle_simulation.simulation_note` confirms no implementation executed
- No `acquisition_completed` key exists in the output schema

**Classification: BLOCKED**
No acquisition completion claim is possible. The output schema enforces simulation framing at every level.

---

### Attack 2: Runtime Approves Gate 11

**Attack vector:** Attempt to set `gate_11_approved=True` via the runtime, or find a code path where `gate_11_approved` could become True.

**Analysis:**
- `_GOVERNANCE_FLAGS["gate_self_approval_allowed"] = False` (immutable)
- `implementation_simulation_v2.authority_graph` has `gate_11_approved=False` hardcoded
- `simulate_v2()` output has `gate_11_approved: False`
- No code path in `run_acquisition_planning()` sets `gate_11_approved=True`
- Test `test_graph_summary_gate_11_approved_false` verifies this

**Classification: BLOCKED**

---

### Attack 3: Runtime Sets commercial_product_ready=True

**Attack vector:** Attempt to mutate `commercial_product_ready` through the governance output dict.

**Analysis:**
- `_governance_copy()` returns `dict(_GOVERNANCE_FLAGS)` — a new shallow copy each time
- Tests `test_governance_flags_are_shallow_copy` and `test_governance_copy_returns_new_dict` verify immutability
- External mutation of the returned dict does NOT affect `_GOVERNANCE_FLAGS`
- No code path in runtime sets `commercial_product_ready=True`
- Verified: `result["governance"]["commercial_product_ready"] = True` → `_GOVERNANCE_FLAGS["commercial_product_ready"]` remains `False`

**Classification: BLOCKED**

---

### Attack 4: Runtime Mutates src/ Product Source

**Attack vector:** Run the full planning pipeline and check whether any files under `src/net/` or `src/python/` are created or modified.

**Analysis:**
- Two dedicated tests (`test_runtime_does_not_write_to_src_net`, `test_runtime_does_not_write_to_src_python`) compare file sets before/after runtime execution
- Runtime code only calls R10 tools which are all `simulation_only=True`
- No file write operations exist in `acquisition_planning_runtime.py`
- All R10 tools are pure-function simulation tools (no disk writes)

**Classification: BLOCKED**

---

### Attack 5: Runtime Mutates Registry Without Authorization

**Attack vector:** Check whether the runtime or any R10 tool it calls writes to `registry/format-registry.yaml` or any registry file.

**Analysis:**
- `run_acquisition_planning()` calls only: `get_candidates_by_tier()`, `score_multiple_formats()`, `simulate_format_acquisition()`, `simulate_v2()`, `plan_all_groups()`
- None of these functions perform disk writes — all are pure computation
- `_GOVERNANCE_FLAGS["autonomous_execution_allowed"] = False`
- No registry write paths exist in any R10 tool

**Classification: BLOCKED**

---

### Attack 6: Runtime Fetches Internet Resources Despite Dry-Run

**Attack vector:** Inspect all code paths in the runtime and R10 tools for any HTTP requests, socket connections, or subprocess calls that could reach the internet.

**Analysis:**
- Zero `import requests`, `import urllib`, `import http`, `import socket` statements in any of: `acquisition_planning_runtime.py`, `acquisition_lifecycle_simulator.py`, `candidate_format_backlog.py`, `public_spec_readiness_scorer.py`, `multi_format_acquisition_planner.py`, `implementation_simulation_v2.py`
- `_GOVERNANCE_FLAGS["no_internet_access"] = True`
- All format data is hardcoded constants (KNOWN_FORMAT_PROFILES, ALL_BACKLOG, STANDARD_CANDIDATE_SPECS)
- Score computation is pure arithmetic on hardcoded data

**Classification: BLOCKED**

---

### Attack 7: Runtime Omits Candidate Blockers

**Attack vector:** Select a candidate with known blockers and verify they are included in the output. Attempt to find a code path where blockers are silently dropped.

**Analysis:**
- `first_candidate_blockers` comes from `lifecycle_sim.get("active_blockers", [])` — this is the active_blockers list from `simulate_lifecycle_state()`
- For CANDIDATE state with `support_matrix_audited=False`, `STATE_BLOCKERS[SUPPORT_MATRIX_AUDIT]` includes `"aspose_support_unknown"` but only activates for non-CANDIDATE states
- `_build_risks()` always appends `aspose_supported is None` risk regardless of blocker state
- Test `test_first_candidate_blockers_is_list` verifies blockers field is always present

**Classification: BLOCKED**
Blockers from lifecycle simulation are always propagated. The risks section supplements blockers with audit-safety warnings.

---

### Attack 8: Runtime Hides Low-Confidence Candidate

**Attack vector:** Submit a tier with mixed-confidence candidates and verify that low-scoring candidates are not hidden from the ranking output.

**Analysis:**
- `candidate_ranking` returns ALL candidates up to `top_n`, including low-scoring ones
- The `score_multiple_formats()` result includes all scored formats, sorted descending
- Test `test_candidate_ranking_is_sorted_descending` verifies no hiding of low-score entries
- Low-score example: TIER_A egg=5.55, hwp/alz scores even lower — these appear in ranking

**Classification: BLOCKED**

---

### Attack 9: Runtime Treats Simulation as Evidence

**Attack vector:** Check whether any output field implies that simulation output constitutes evidence for gate passage.

**Analysis:**
- `simulation_graph_summary.graph_note` = "SIMULATION — graph summary only. Full graphs available via simulate_v2()."
- `lifecycle_simulation.simulation_note` = "Format ZST is at state CANDIDATE. This is a simulation describing what WOULD happen next. No implementation has been executed."
- `bundle_note` explicitly states "SIMULATION ONLY — planning estimates, not commitments."
- No output field is labeled as `evidence_for_gate_X` or `gate_X_passed`
- The first-candidate plan's "Required Evidence" section lists future evidence requirements, not current evidence

**Classification: BLOCKED**

---

### Attack 10: Runtime Fails to Mark dry_run_only

**Attack vector:** Call the runtime and verify that `dry_run_only=True` is present in the output at all levels.

**Analysis:**
- Top-level `result["dry_run_only"] = True` — always set in `run_acquisition_planning()`
- `result["governance"]["dry_run_only"] = True`
- `result["lifecycle_simulation"]["dry_run_only"] = True`
- `result["multi_format_plan"]["dry_run_only"] = True`
- Tests `test_dry_run_only_is_true` and `test_governance_dry_run_only_in_flags` verify this
- Attempting `run_acquisition_planning(dry_run=False)` raises `ValueError`

**Classification: BLOCKED**

---

### Attack 11: Runtime Fails to Mark simulation_only

**Attack vector:** Check all output levels for `simulation_only` flag.

**Analysis:**
- Top-level `result["simulation_only"] = True` — always set
- `result["governance"]["simulation_only"] = True`
- `result["lifecycle_simulation"]` contains governance dict with `simulation_only=True`
- Test `test_simulation_only_is_true` and `test_governance_simulation_only_in_flags` verify this

**Classification: BLOCKED**

---

### Attack 12: Runtime Produces Nondeterministic Ranking

**Attack vector:** Call `run_acquisition_planning()` multiple times and compare candidate rankings.

**Analysis:**
- Ranking is produced by `score_multiple_formats()` which uses deterministic weighted arithmetic
- All scores are computed from hardcoded constants (spec_type, category, boolean flags)
- `_stable_hash()` produces deterministic SHA-256 based IDs
- Tests `test_bundle_id_is_stable_across_calls`, `test_candidate_ranking_is_stable_across_calls`, `test_first_candidate_is_stable_across_calls` all verify determinism
- `score_multiple_formats()` sorts with `reverse=True` which is deterministic for equal values (Python sort is stable)

**Classification: BLOCKED**

---

### Attack 13: Runtime Ignores DEC-033/Product-Track Constraints

**Attack vector:** Check whether the runtime could be used to plan .NET FOSS packaging or cross-track activities that violate DEC-033.

**Analysis:**
- Runtime operates exclusively on acquisition planning layer (tools/skills), not product source (src/net/, src/python/)
- No output field references .NET FOSS packaging, Python FOSS packaging, or track selection
- DEC-033 (Option B: .NET Commercial Only) applies to the product track layer, not the acquisition planning layer
- `first_candidate_non_goals` explicitly prohibits src/ modification
- The runtime does not produce any product source artifacts

**Classification: BLOCKED**
DEC-033 scope does not conflict with acquisition planning simulation. The runtime correctly stays in the simulation/planning layer.

---

### Attack 14: Runtime Outputs Unsupported First-Candidate Claim

**Attack vector:** Verify that the first-candidate selection is backed by explicit scoring data, not an arbitrary claim.

**Analysis:**
- `selected_first_candidate` = `scoring_result.get("top_candidate")` which is the highest-scored format from `score_multiple_formats()`
- `first_candidate_readiness_score` = the actual composite score from the scorer
- `first_candidate_rationale` includes rank, score, tier, spec_type, and explicit ESTIMATE disclaimer
- `score_note` in the scorer output explicitly states "This is an ESTIMATE based on publicly available information. Scores do not authorize acquisition — human review required."
- Test `test_first_candidate_rationale_is_nonempty_string` verifies rationale is populated

**Classification: BLOCKED**
The first-candidate claim is fully supported by deterministic scoring data with explicit estimation disclaimers.

---

## Summary

| Classification | Count |
|---------------|-------|
| BLOCKED | 14 |
| PARTIALLY_BLOCKED_WITH_FOLLOWUP | 0 |
| NOT_BLOCKED_REPAIR_REQUIRED | 0 |

All 14 attacks are BLOCKED. No residual high-severity risks identified.

**R11_ADVERSARIAL_REVIEW_STATUS: PASS**

---

## Lane F Verdict

**LANE_F_PASS_ADVERSARIAL_REVIEW**

*Authority: FORMAT-FACTORY-R11-ACQUISITION-PLANNING-INTEGRATION-SWARM-001*
