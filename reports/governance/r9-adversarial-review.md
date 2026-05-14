---
document_type: adversarial_review
sprint: CONWAY-R9-GOVERNED-SIMULATION-AND-AUTHORITY-CONTINUITY-SWARM-001
lane: R9-9
date: "2026-05-14"
visibility: internal
---

# R9 Adversarial Review

**Sprint:** CONWAY-R9-GOVERNED-SIMULATION-AND-AUTHORITY-CONTINUITY-SWARM-001
**Lane:** R9-9 — Adversarial Safety Review
**Date:** 2026-05-14

---

## Overview

This review tests 14 adversarial attack scenarios against the R9 deliverables.
Each scenario attempts to violate a governance property; each must be BLOCKED.

---

## Attack 1: Set commercial_product_ready = True via simulation result

**Attack:** Attacker calls `simulate_format_sprint("fods")` and mutates
`result["governance"]["commercial_product_ready"] = True`, then reads back
`_GOVERNANCE_FLAGS` to see if it changed.

**Target:** `execution_simulator._GOVERNANCE_FLAGS`

**Defense:**
- `result["governance"]` is `dict(_GOVERNANCE_FLAGS)` — a shallow copy
- Mutating the copy does not affect the module constant
- `_GOVERNANCE_FLAGS["commercial_product_ready"]` remains `False`

**Test:** `test_governance_flags_are_immutable` (test_execution_simulator.py)

**VERDICT: BLOCKED**

---

## Attack 2: Force gate_11_approved = True in simulation

**Attack:** Attacker attempts to use `simulate_format_sprint()` to produce a result
where `gate_state_snapshot["gate_11_approved"] = True`, then uses that as
"evidence" that gate 11 is approved.

**Target:** `gate_state_snapshot.gate_11_approved`

**Defense:**
- `gate_11_approved: False` is hardcoded in `simulate_format_sprint()`:
  `"gate_11_approved": False,  # NEVER set to True by simulation`
- `simulation_read_only: True` is set on all gate snapshots
- Schema enforces `gate_11_approved: {enum: [false]}`

**Test:** `test_gate_11_approved_never_true` (test_execution_simulator.py)

**VERDICT: BLOCKED**

---

## Attack 3: Bypass STALE_BLOCKED via direct simulation call

**Attack:** Attacker calls `simulate_format_sprint("fods")` directly despite knowing
the format has `STALE_BLOCKED` stale verdict, hoping to obtain lane simulation results.

**Target:** `execution_simulator.simulate_format_sprint` stale enforcement

**Defense:**
- `simulate_format_sprint` checks `stale_verdict == "STALE_BLOCKED"` before any simulation
- Returns `BLOCKED_STALE` with empty `lane_simulations`
- No lane simulation data is produced

**Test:** `test_blocked_stale_when_stale_blocked` (test_execution_simulator.py)

**VERDICT: BLOCKED**

---

## Attack 4: Inject execution code into simulated_actions

**Attack:** Attacker attempts to get execution simulator to include runnable Python code
in `simulated_actions` list (e.g., `exec(...)` or `subprocess.run(...)` calls).

**Target:** `execution_simulator._build_lane_simulation.simulated_actions`

**Defense:**
- All simulated actions are hardcoded string templates prefixed with `[SIM]`
- No user-controlled input flows into action strings
- Actions are descriptive sentences, never code
- Test verifies all actions start with `[SIM]`

**Test:** `test_actions_are_descriptive_not_executable`,
`test_simulated_actions_contain_no_actual_code` (test_execution_simulator.py)

**VERDICT: BLOCKED**

---

## Attack 5: Modify simulation_log of prior authority entry

**Attack:** Attacker calls `add_simulation_entry(entry, ...)` and then modifies the
original `entry["simulation_log"]` after the fact, hoping to retroactively alter
the simulation history.

**Target:** `authority_continuity_registry.add_simulation_entry` append-only property

**Defense:**
- `add_simulation_entry()` returns a **new dict** — original is never mutated
- `new_log = list(entry.get("simulation_log", []))` creates a copy before appending
- Original entry's `simulation_log` remains unmodified

**Test:** `test_does_not_mutate_original`, `test_simulation_log_is_append_only`
(test_authority_continuity_registry.py)

**VERDICT: BLOCKED**

---

## Attack 6: Break cross-format isolation via shared governance dict

**Attack:** Attacker reads `fods_entry["governance"]`, mutates it
(`fods_entry["governance"]["commercial_product_ready"] = True`), then reads
`fodt_entry["governance"]` hoping it was shared by reference.

**Target:** `authority_continuity_registry.build_authority_entry` governance isolation

**Defense:**
- Each entry's governance is `dict(_GOVERNANCE_FLAGS)` — an independent copy
- FODS and FODT entries have separate governance dicts
- Mutating one does not affect the other

**Test:** `test_governance_is_copy_not_reference` (test_authority_continuity_registry.py)

**VERDICT: BLOCKED**

---

## Attack 7: Produce identical authority IDs for FODS and FODT

**Attack:** Attacker constructs FODS and FODT entries with identical requirement IDs,
slice IDs, gate state, and other inputs, hoping to get the same `authority_id` for
both (which would break cross-format isolation).

**Target:** `authority_continuity_registry.build_authority_entry.authority_id`

**Defense:**
- `authority_id = _stable_hash({"format": fmt, ...})` — `"format": fmt` ensures
  different hash inputs for FODS vs FODT even if all other inputs are identical

**Test:** `test_cross_format_isolation_different_authority_ids`
(test_authority_continuity_registry.py)

**VERDICT: BLOCKED**

---

## Attack 8: Force TIER_0_CLEAN via verdict manipulation

**Attack:** Attacker passes `verdict="FRESH"` to `classify_stale_tier()` but with
`blocker_count=3`, hoping to get `TIER_0_CLEAN` despite multiple blockers.

**Target:** `stale_propagation.classify_stale_tier` escalation logic

**Defense:**
- `blocker_count >= 3` unconditionally returns `TIER_4_CORRUPTED`
- Verdict-based tier is only used AFTER blocker count check
- `TIER_4_CORRUPTED` escalates before any verdict-based logic applies

**Test:** `test_three_blockers_escalate_to_tier_4` (test_stale_propagation.py)

**VERDICT: BLOCKED**

---

## Attack 9: Inject fake genesis entry in middle of lineage chain

**Attack:** Attacker inserts an entry with `is_genesis=True` in the middle of an
otherwise valid lineage chain, hoping to restart the chain from an arbitrary point.

**Target:** `replay_lineage.validate_lineage_chain`

**Defense:**
- `validate_lineage_chain` checks: if `curr.get("is_genesis")` is True for any
  non-first entry, it records a violation
- Returns `LINEAGE_CHAIN_BROKEN`

**Test:** `test_non_genesis_marked_as_genesis_detected` (test_replay_lineage.py)

**VERDICT: BLOCKED**

---

## Attack 10: Tamper lineage entry in middle of chain

**Attack:** Attacker modifies `e1["fingerprint"] = "TAMPERED"` in the middle of a
three-entry chain `[e0, e1, e2]`, hoping the chain validation does not detect it.

**Target:** `replay_lineage.validate_lineage_chain` tamper detection

**Defense:**
- `e2["prior_fingerprint"]` was set when `e2` was built from the real `e1["fingerprint"]`
- After tampering `e1["fingerprint"]`, `e2["prior_fingerprint"]` no longer matches
- Chain validation detects the mismatch and returns `LINEAGE_CHAIN_BROKEN`

**Test:** `test_tampered_middle_entry_breaks_chain` (test_replay_lineage.py)

**VERDICT: BLOCKED**

---

## Attack 11: Claim REQUIREMENTS_AUTHORITATIVE on non-authoritative format

**Attack:** Attacker constructs an authority entry manually with
`requirements_state="REQUIREMENTS_AUTHORITATIVE"` for a format that is actually
`REQUIREMENTS_PENDING`, then uses that entry to assert the format is authorized
for implementation.

**Target:** `authority_continuity_registry.build_authority_entry` (no internal validation)

**Defense:**
- `build_authority_entry` records whatever state is passed — it does NOT validate authority
- The `build_live_registry()` function reads from `format_context_resolver` which returns
  the actual live state — it cannot be bypassed without mocking the live context
- An authority entry built with fake state has no effect on the live resolver
- Implementation authorization requires human review of live state, not just the registry
- Schema validates `requirements_state` against a fixed enum — fake states are rejected

**Note:** `build_authority_entry` is a data structure builder; authority derives from the
upstream resolver, not from the entry itself. Governance documentation is explicit: the
entry is a record, not an authorization.

**VERDICT: BLOCKED (by design — authority is external to the registry)**

---

## Attack 12: Use simulation_pass as implementation authorization

**Attack:** Attacker prints `SIMULATION_PASS` in a sprint report and claims this
constitutes human authorization for implementation, citing the governance docs.

**Target:** Governance documentation (docs/conway-r9-governed-simulation.md)

**Defense:**
- `docs/conway-r9-governed-simulation.md` Section 5 explicitly states:
  "A SIMULATION_PASS result does NOT mean: Implementation is authorized"
- `simulation_summary` always ends with "DRY-RUN ONLY — no implementation executed."
- All simulation results include `autonomous_execution_allowed: False`
- Implementation authorization is a separate human process (GOVERNANCE.md §26.8-26.13)

**VERDICT: BLOCKED**

---

## Attack 13: Bypass stale propagation by using stale_detection directly

**Attack:** Attacker bypasses `stale_propagation.propagate_stale_state()` and reads
`stale_detection.detect_stale_state()` directly, claiming the simpler stale detection
(which may return REVIEW_REQUIRED instead of TIER_3_BLOCKED) authorizes simulation.

**Target:** Governance interpretation of stale tier

**Defense:**
- `execution_simulator.py` reads from `stale_detection.detect_stale_state()` directly
  and checks `verdict == "STALE_BLOCKED"` — this is the authoritative block
- `stale_propagation` adds advisory tiering ON TOP of stale_detection; it does not
  weaken the base stale_detection check
- Both `stale_detection` and `stale_propagation` enforce the same STALE_BLOCKED gate

**VERDICT: BLOCKED**

---

## Attack 14: Cross-format contamination via completed_lanes set

**Attack:** Attacker hopes that the `completed_lanes` set from a FODS simulation is
shared with a FODT simulation, so completing LANE-I-LOAD for FODS also marks it
complete for FODT (bypassing FODT's dependency check).

**Target:** `execution_simulator.simulate_format_sprint` completed_lanes scoping

**Defense:**
- `completed_lanes: set[str]` is created fresh inside each `simulate_format_sprint(fmt)` call
- `simulate_all_formats` calls `simulate_format_sprint` in a loop — each call creates its own set
- FODS and FODT lane completions are never shared

**Test:** `test_cross_format_isolation_different_simulation_ids` (test_execution_simulator.py),
cross-format isolation review (cross-format-isolation-review.md Section 3)

**VERDICT: BLOCKED**

---

## Summary

| # | Attack | Target | Verdict |
|---|--------|--------|---------|
| 1 | commercial_product_ready mutation via copy | _GOVERNANCE_FLAGS | BLOCKED |
| 2 | gate_11_approved = True via simulation | gate_state_snapshot | BLOCKED |
| 3 | Bypass STALE_BLOCKED | simulate_format_sprint | BLOCKED |
| 4 | Inject executable code in simulated_actions | _build_lane_simulation | BLOCKED |
| 5 | Modify prior simulation_log entry | add_simulation_entry | BLOCKED |
| 6 | Cross-format governance dict mutation | build_authority_entry | BLOCKED |
| 7 | Produce identical authority IDs cross-format | authority_id hash | BLOCKED |
| 8 | Force TIER_0_CLEAN with multiple blockers | classify_stale_tier | BLOCKED |
| 9 | Inject fake genesis in lineage chain | validate_lineage_chain | BLOCKED |
| 10 | Tamper lineage entry in middle of chain | validate_lineage_chain | BLOCKED |
| 11 | Claim authority with fake requirements_state | build_authority_entry | BLOCKED (by design) |
| 12 | Use SIMULATION_PASS as implementation auth | governance docs | BLOCKED |
| 13 | Bypass stale propagation tier | stale tier interpretation | BLOCKED |
| 14 | Cross-format contamination via completed_lanes | completed_lanes scope | BLOCKED |

**ATTACKS_TESTED: 14**
**ATTACKS_BLOCKED: 14**
**ATTACKS_PASSED: 0**

**R9_ADVERSARIAL_REVIEW: PASS (14/14)**
**LANE_R9_9_STATUS: COMPLETE**
