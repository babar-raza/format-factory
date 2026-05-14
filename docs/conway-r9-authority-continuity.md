---
document_type: governance_doc
sprint: CONWAY-R9-GOVERNED-SIMULATION-AND-AUTHORITY-CONTINUITY-SWARM-001
lane: R9-8
title: "Conway R9 — Authority Continuity Registry"
date: "2026-05-14"
visibility: internal
---

# Conway R9 — Authority Continuity Registry

**Sprint:** CONWAY-R9-GOVERNED-SIMULATION-AND-AUTHORITY-CONTINUITY-SWARM-001
**Authority:** AGENTS.md AF9-AF15 | GOVERNANCE.md 26.8-26.13

---

## 1. Purpose

The authority continuity registry tracks **authoritative planning lineage** across sprints.
It provides a deterministic, cross-format-isolated, tamper-evident record of:

- Which requirements are accepted for a vertical slice
- What planning slices exist for each format
- What simulation runs have been performed
- Whether requirements are fresh or stale
- Gate state at the time of each planning artifact

**Why this matters:** Without a continuity registry, it is impossible to prove that the
planning artifacts in sprint N were derived from the same requirements and context as
sprint N-1. The registry makes this derivation chain explicit and verifiable.

---

## 2. Registry Structure

```
Registry
├── registry_id       (hash of all authority_ids)
├── format_count      (2 for FODS+FODT)
├── format_ids        (sorted: ["fods", "fodt"])
├── all_authoritative (bool: all formats have REQUIREMENTS_AUTHORITATIVE)
├── any_stale_blocked (bool: any format has STALE_BLOCKED)
├── governance        (immutable governance flags)
├── created_date
└── formats
    ├── fods
    │   ├── authority_id          (hash of all inputs)
    │   ├── format_id             "fods"
    │   ├── requirements_state    REQUIREMENTS_AUTHORITATIVE
    │   ├── accepted_requirement_ids  [sorted list]
    │   ├── stale_verdict         FRESH
    │   ├── planning_slice_ids    [sorted list]
    │   ├── gate_state            {gates_passed, gate_11_status, gate_11_approved: false}
    │   ├── source_hashes         {requirements_hash, slice_hash, gate_hash}
    │   ├── replay_fingerprint    (from replay_fingerprint module)
    │   ├── simulation_log        [append-only list]
    │   ├── dependency_lineage    []
    │   ├── format_isolation_marker  "FORMAT:FODS"
    │   └── governance            (copy of governance flags)
    └── fodt
        └── ... (same structure, FORMAT:FODT)
```

---

## 3. Determinism Properties

Every field in the registry is deterministic:

- `authority_id` = SHA-256 of `{format, req_hash, slice_hash, gate_hash, requirements_state, stale_verdict}`
- `registry_id` = SHA-256 of `[sorted authority_ids]`
- `source_hashes.requirements_hash` = SHA-256 of sorted accepted requirement IDs
- `source_hashes.slice_hash` = SHA-256 of sorted planning slice IDs
- `source_hashes.gate_hash` = SHA-256 of sorted gate_state dict

**Consequence:** Running `build_live_registry()` twice with identical inputs produces
identical output. Any change to requirements, slices, gate state, or stale verdict
produces a different `authority_id` and `registry_id`.

---

## 4. Cross-Format Isolation

Each format has a completely independent registry entry:

- `authority_id` includes `"format": fmt` — FODS and FODT always differ
- `format_isolation_marker` is `FORMAT:FODS` vs `FORMAT:FODT`
- `simulation_log` is per-format and per-entry
- No shared mutable state between FODS and FODT entries

**Test coverage:**
- `test_cross_format_isolation_different_authority_ids`
- `test_cross_format_isolation_markers_differ`
- `test_formats_cross_isolated`

---

## 5. Append-Only Simulation Log

The `simulation_log` field in each authority entry is append-only:

- `add_simulation_entry()` always returns a **new dict** — the original is never mutated
- Each appended entry includes `appended_at_index` (zero-based sequential integer)
- Prior entries are never modified after appending
- The log can be re-derived from the sequence of simulation runs

---

## 6. Governance Invariants

```python
# These are NEVER configurable:
entry["governance"]["commercial_product_ready"]           # always False
entry["governance"]["autonomous_execution_allowed"]       # always False
entry["governance"]["gate_self_approval_allowed"]         # always False
entry["governance"]["dry_run_only"]                       # always True
entry["governance"]["simulation_only"]                    # always True
entry["governance"]["implementation_requires_human_authorization"]  # always True
```

The governance dict is always a **copy** of `_GOVERNANCE_FLAGS` — mutating a returned
governance dict does not affect the module-level constant.

---

## 7. Schema Validation

Registry entries are validated against `schemas/skills/authority-continuity.schema.yaml`:

- `authority_id` must be a valid hex string (8-64 chars)
- `format_id` must be in `["fods", "fodt"]`
- `gate_state.gate_11_approved` must be `false` (schema enforced)
- All governance flags have schema-enforced values
- `format_isolation_marker` must match `FORMAT:[A-Z]+`

---

## 8. Entry Points

```bash
# Build and display live registry
python tools/skills/authority_continuity_registry.py

# JSON output
python tools/skills/authority_continuity_registry.py --json
```

---

**AUTHORITY_CONTINUITY_DOC: COMPLETE**
