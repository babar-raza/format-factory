---
espanso_provenance:
  source_triggers: [":ff-review-fix-layer-0", ":ffl0:", ":ff-review-fix-layer-1", ":ffl1:", ":ff-review-fix-layer-2", ":ffl2:", ":ff-review-fix-layer-3", ":ffl3:", ":ff-review-fix-layer-4", ":ffl4:", ":ff-review-fix-layer-5", ":ffl5:", ":ff-review-fix-layer-6", ":ffl6:", ":ff-review-fix-layer-7", ":ffl7:", ":ff-review-fix-all-layers", ":ffla:"]
  source_blocks: [71, 72, 73, 74, 75, 76, 77, 78, 79]
  source_line_range: [85215, 92462]
  gap_id: GAP-ESP-005
  extraction_date: "2026-07-03"
  capability_id: null
  note: "Parameterized template covering all 9 per-layer blocks"
prompt_id: ESP-PROMPT-7
title: "Per-Layer Production Hardening (Parameterized Template)"
version: "1.0"
status: ACTIVE
mutating: true
context_profile: full
---

# Per-Layer Production Hardening Protocol

**Parameter: `layer_id`** — one of: `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7`, `all`

## Layer Index

| layer_id | Layer Name | Key Scope |
|---|---|---|
| 0 | Governance and Gate Model | AGENTS.md, CLAUDE.md, policies.yaml, schemas, validators |
| 1 | SAL / Specification Authority | SAL facts, QName registry, oracle cases |
| 2 | Capability and Feature Routing | capability-routing-registry.yaml, skill-registry.yaml |
| 3 | Product Source | src/python/, src/net/ per-format implementations |
| 4 | Tests | tests/ directory, test coverage, oracle verification |
| 5 | Evidence and Proof | .local/evidences/, evidence-declaration.schema.json |
| 6 | State and Continuation | .local/supervisor/, continuation-signal.json, plan locks |
| 7 | Supervisor Pipeline | tools/supervisor/, autonomous_cycle.py, sprint_executor.py |
| all | All Layers | Run this protocol for each layer 0-7 in sequence |

## Short-Context View

**Layer `{layer_id}` Production Hardening:**
1. Reconstruct the actual layer from the current repository
2. Manually inspect every relevant implementation, configuration, test, and artifact
3. Build a gap ledger for this layer
4. Convert all actionable findings into taskcards
5. Execute the taskcards (do not stop after producing findings)
6. Verify the repaired layer at its interfaces
7. Continue until the layer is production-ready or a proven external blocker remains

---

## Execution Protocol

### Safety (always first)
```
→ Confirm HEAD, branch, working tree state
→ Read plans/master-plan.md and AGENTS.md
→ Read active plans, taskcards, and known failure ledger
→ Preserve unrelated local work
→ Never use: destructive reset, clean, force-push, bulk deletion, test weakening
```

### Phase 1: Reconstruct Actual Layer State
For the target `layer_id`:
```
→ List all files belonging to this layer
→ Read schemas, configs, and primary implementations
→ Read tests that cover this layer
→ Read any prior audit reports for this layer
→ Note: what claims have been made about this layer?
```

### Phase 2: Manual Inspection
Inspect EVERY component in the layer:
```
→ Implementations: correct? complete? production-grade?
→ Configurations: valid? referenced by correct consumers?
→ Schemas: cover all required fields? no bypass paths?
→ Tests: real behavior or synthetic? coverage breadth?
→ State transitions: correct sequence? all states handled?
→ Interfaces: producer-consumer boundaries clean?
→ Generated outputs: current? consumed by downstream?
→ Known failures: still present? fixed without evidence?
```

### Phase 3: Gap Ledger
Create `.local/evidences/<run_id>/layer-<layer_id>-gap-ledger.yaml`:
```yaml
layer_id: <0-7>
inspection_date: <ISO-8601>
gaps:
  - gap_id: L<layer_id>-GAP-001
    severity: BLOCKING | HIGH | MEDIUM | LOW
    category: implementation | config | schema | test | state | interface | output | governance
    description: <what is wrong>
    root_cause: <first failing boundary>
    affected_files: []
    fix_approach: <how to fix>
    acceptance_criteria: <how to verify fix>
```

### Phase 4: Hardening Plan
Convert BLOCKING and HIGH gaps to taskcards:
```yaml
taskcards:
  - id: TC-L<layer_id>-001
    title: <concise fix description>
    implementation_steps: []
    verification_steps: []
    done_check: <exact command or assertion>
    evidence_path: .local/evidences/<run_id>/
```

### Phase 5: Execute Taskcards
```
→ Execute each taskcard in dependency order
→ Apply fixes at root cause, not symptom
→ Run done-check after each taskcard
→ Do not mark DONE without passing the done-check
```

### Phase 6: Verification
```
→ Run all tests for this layer
→ Run applicable governance validators
→ Check layer interfaces (producer → consumer boundaries)
→ Confirm no new gaps were introduced
```

### Phase 7: Re-Audit
```
→ Re-read the gap ledger
→ Mark each gap: RESOLVED | PARTIALLY_RESOLVED | DEFERRED | BLOCKED
→ For PARTIALLY_RESOLVED: create a follow-up taskcard
→ For BLOCKED: classify the exact external blocker
```

### Completion Gate
Layer `{layer_id}` is production-ready when:
- All BLOCKING gaps resolved or proven externally blocked
- All HIGH gaps resolved or have tracked follow-up taskcards
- All layer tests pass
- No governance validator violations in this layer
- Gap ledger shows no unaddressed BLOCKING items

### For `layer_id=all`
Run Phases 1-7 for each layer 0-7 in sequence.
Each layer's gaps feed into the next layer's baseline.
Start with Layer 0 (Governance) as it governs all other layers.
