---
document_type: cross_format_isolation_review
sprint: CONWAY-R9-GOVERNED-SIMULATION-AND-AUTHORITY-CONTINUITY-SWARM-001
lane: R9-4
date: "2026-05-14"
visibility: internal
---

# Cross-Format Isolation Review

**Sprint:** CONWAY-R9-GOVERNED-SIMULATION-AND-AUTHORITY-CONTINUITY-SWARM-001
**Lane:** R9-4 — Cross-Format Isolation Hardening
**Date:** 2026-05-14

---

## Section 1: Isolation Requirements

Cross-format isolation is a first-class governance requirement in the format-factory
orchestration layer. The governed simulation and authority continuity registry MUST
ensure that planning, simulation, and fingerprint state for FODS cannot contaminate
or influence FODT (and vice versa).

**Required isolation properties:**
1. Authority IDs are format-scoped — FODS and FODT entries always have different `authority_id` values
2. Format isolation markers are present and correct: `FORMAT:FODS` vs `FORMAT:FODT`
3. Simulation IDs are format-scoped — different formats produce different `simulation_id` values
4. Replay fingerprints are format-scoped — FODS fingerprints never equal FODT fingerprints for matching inputs
5. Registry entries are keyed by `format_id` — no cross-format key collision
6. Stale verdicts are evaluated independently per format
7. Gate state snapshots are per-format read-only copies — no shared mutable state
8. Constraint propagation operates within a lane/format scope — no cross-format leakage

---

## Section 2: authority_continuity_registry.py Isolation Verification

| Property | Mechanism | Status |
|----------|-----------|--------|
| `authority_id` is format-scoped | `format` included in hash inputs: `{"format": fmt, "req_hash": ..., ...}` | ISOLATED |
| `format_isolation_marker` present | `f"FORMAT:{fmt.upper()}"` always set | ISOLATED |
| Registry keyed by `format_id` | `{e["format_id"]: e for e in sorted_entries}` | ISOLATED |
| `all_authoritative` is per-format aggregate | `all(e["requirements_state"] == "REQUIREMENTS_AUTHORITATIVE" for e in ...)` | ISOLATED |
| `any_stale_blocked` is per-format aggregate | `any(e["stale_verdict"] == "STALE_BLOCKED" for e in ...)` | ISOLATED |
| `simulation_log` is per-entry append-only | `add_simulation_entry` returns new dict, never mutates original | ISOLATED |
| `governance` is a dict copy | `dict(_GOVERNANCE_FLAGS)` — new dict per entry | ISOLATED |

**ISOLATION_REGISTRY: CONFIRMED**

---

## Section 3: execution_simulator.py Isolation Verification

| Property | Mechanism | Status |
|----------|-----------|--------|
| `simulation_id` is format-scoped | `_stable_hash({"fmt": fmt, "req_ids": sorted(req_ids), ...})` | ISOLATED |
| Per-format context loaded independently | `resolve_format_context(fmt)` called per-format | ISOLATED |
| Per-format stale check | `detect_stale_state(fmt)` called per-format | ISOLATED |
| Per-format plan expansion | `expand_implementation_plan(fmt)` called per-format | ISOLATED |
| `simulate_all_formats` stores per-format results | `per_format[fmt] = simulate_format_sprint(fmt)` | ISOLATED |
| `completed_lanes` set is scoped to one format | Created fresh for each `simulate_format_sprint(fmt)` call | ISOLATED |
| `constraint_propagation` list is per-format | Built from `sim["constraint_violations"]` for that format's lanes only | ISOLATED |
| `gate_state_snapshot` is a new dict | Created as new dict per format call, `gate_11_approved: False` hardcoded | ISOLATED |
| Authority entry is per-format | `build_authority_entry(fmt=fmt, ...)` — format-scoped | ISOLATED |

**ISOLATION_SIMULATOR: CONFIRMED**

---

## Section 4: Format Isolation Marker Verification

All entries produced by `build_authority_entry()` include a `format_isolation_marker` field:

- FODS entries: `"format_isolation_marker": "FORMAT:FODS"`
- FODT entries: `"format_isolation_marker": "FORMAT:FODT"`

This marker:
- Is derived from `fmt.upper()` (deterministic, format-specific)
- Is included in schema validation (`pattern: "^FORMAT:[A-Z]+"`)
- Is verified in `test_authority_continuity_registry.py`:
  - `test_format_isolation_marker_correct_fods`
  - `test_format_isolation_marker_correct_fodt`
  - `test_cross_format_isolation_markers_differ`

**FORMAT_ISOLATION_MARKER: VERIFIED**

---

## Section 5: Hash Isolation (Authority IDs, Simulation IDs, Fingerprints)

### authority_id isolation

`authority_id` is computed as:
```python
authority_id = _stable_hash({
    "format": fmt,          # ← format-scoped
    "req_hash": req_hash,
    "slice_hash": slice_hash,
    "gate_hash": gate_hash,
    "requirements_state": requirements_state,
    "stale_verdict": stale_verdict,
})
```

Even if two formats have identical req/slice/gate content, `"format": fmt` ensures different IDs.

**Verified by test:** `test_cross_format_isolation_different_authority_ids`

### simulation_id isolation

`simulation_id` is computed as:
```python
simulation_id = _stable_hash({
    "fmt": fmt,             # ← format-scoped
    "req_ids": sorted(req_ids),
    "date": str(date.today()),
    "lane_count": lane_count,
})
```

**Verified by test:** `test_cross_format_isolation_different_simulation_ids`

### Replay fingerprint isolation

Replay fingerprints from `replay_fingerprint.py` are computed from format-specific inputs.
Test `test_fods_fodt_different_fingerprints` (R7R8 suite) confirms cross-format isolation.

**HASH_ISOLATION: CONFIRMED**

---

## Section 6: Registry Isolation (Cross-Entry Non-Contamination)

The full registry produced by `build_full_registry()` uses:
```python
{e["format_id"]: e for e in sorted_entries}
```

This ensures:
- Dictionary keys are unique per format
- FODS entry is stored at `registry["formats"]["fods"]`
- FODT entry is stored at `registry["formats"]["fodt"]`
- No key collision is possible between formats
- `registry_id` is a hash of authority_ids, so cross-format changes cause registry_id to change

**REGISTRY_ISOLATION: CONFIRMED**

---

## Section 7: Stale State Isolation

Each format's stale verdict is evaluated independently:
- `detect_stale_state("fods")` and `detect_stale_state("fodt")` are independent calls
- FODS being `STALE_BLOCKED` does NOT block FODT simulation
- FODT being `STALE_BLOCKED` does NOT block FODS simulation
- `any_stale_blocked` in the full registry reflects the aggregate — it is a reporting field,
  not a cross-format enforcement gate

**STALE_ISOLATION: CONFIRMED**

---

## Section 8: Gate State Isolation

Gate state snapshots in simulation results are:
- Created as NEW dict per format call (not a shared reference)
- `gate_11_approved: False` is hardcoded in the snapshot (not read from live state)
- `simulation_read_only: True` is always set
- No mutable reference is shared between FODS and FODT gate snapshots

**GATE_STATE_ISOLATION: CONFIRMED**

---

## Section 9: Known Isolation Risks (Mitigated)

| Risk | Mitigation | Status |
|------|-----------|--------|
| Shared `_GOVERNANCE_FLAGS` dict | `dict(_GOVERNANCE_FLAGS)` creates a copy for each entry | MITIGATED |
| `simulation_log` mutation | `add_simulation_entry` returns new dict, original not mutated | MITIGATED |
| `completed_lanes` set shared between formats | Set is created fresh per `simulate_format_sprint(fmt)` call | MITIGATED |
| Format key collision in registry | `format_id` is validated against enum `["fods", "fodt"]` | MITIGATED |
| Cross-format constraint bleed | `_build_lane_simulation` filters by `scope in req_ids` — format-scoped | MITIGATED |

**ISOLATION_RISKS: ALL MITIGATED**

---

## Section 10: Test Coverage Summary

| Test | Location | Covers |
|------|----------|--------|
| `test_cross_format_isolation_different_authority_ids` | test_authority_continuity_registry.py | authority_id isolation |
| `test_cross_format_isolation_markers_differ` | test_authority_continuity_registry.py | isolation marker isolation |
| `test_formats_cross_isolated` | test_authority_continuity_registry.py | live registry cross-isolation |
| `test_cross_format_isolation_different_simulation_ids` | test_execution_simulator.py | simulation_id isolation |
| `test_fods_fodt_different_simulation_ids` | test_execution_simulator.py | live simulation isolation |
| `test_fods_fodt_different_fingerprints` | test_replay_fingerprint.py (R7R8) | fingerprint isolation |

---

## VERDICT

**CROSS_FORMAT_ISOLATION: CONFIRMED**
**CONTAMINATION_RISK: NONE IDENTIFIED**
**ISOLATION_HARDENING_STATUS: COMPLETE**
**LANE_R9_4_STATUS: COMPLETE**
