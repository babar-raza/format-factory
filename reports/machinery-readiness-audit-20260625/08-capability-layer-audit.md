# Lane F: Capability Layer Audit
# Sprint: ff-machinery-readiness-audit-20260625

## Summary Finding

The Capability Layer **generates output that nobody consumes.** It is operational but isolated:
- capability_map_generator.py runs and produces valid output
- gap-ledger.json is generated and populated (1,132+ gaps)
- But: autonomous task generation IGNORES all of this and uses a hardcoded list instead
- action-queue.json has `advisory_only: true` on ALL items — none are actionable

---

## Component Health Assessment

Source: spec-to-feature-radical-correction-plan.md §3

| Component | Status | Risk | Evidence |
|---|---|---|---|
| Capability map generation | OPERATIONAL | MEDIUM | capability_map_generator.py produces 500+ records per format |
| Capability map validation | DEFINED | MEDIUM | validate_capability_map.py: 10 validators (VAL-001..010) |
| Gap ledger generation | OPERATIONAL | **HIGH** | Generated (1,132+ gaps) but **NEVER CONSUMED** by task generation |
| Action queue | OPERATIONAL | **HIGH** | advisory_only: true on ALL items; not actionable |
| Feature Factory | OPERATIONAL | LOW | product_feature_factory.py: 6 patterns (A-F); manual-use only |
| Task generation | OPERATIONAL | **HIGH** | autonomous_task_generator.py uses **HARDCODED** _EXPANSION_GOALS |
| Requirements Authority proof graph | **DORMANT** | **CRITICAL** | 18 node types + 19 edge types defined; NO population; NO consumption |
| Capability verifier | OPERATIONAL | LOW | capability_verifier.py: 4-bucket sync check (read-only) |

---

## The Disconnection Chain (Verified from Source)

Source: autonomous_task_generator.py direct read (lines 29–200):

```
poc-targets.yaml ──► capability_map_generator.py ──► unified-capability-map.json ──► [DEAD END]
                                                   ──► gap-ledger.json ──────────► [DEAD END]
                                                   ──► action-queue.json ──────► [advisory_only: true]

autonomous_task_generator.py ──reads──► HARDCODED _EXPANSION_GOALS (20+ manual entries)
                              ──ignores──► unified-capability-map.json
                              ──ignores──► gap-ledger.json
```

**Proof from autonomous_task_generator.py:**
```python
# Line 29: _EXPANSION_GOALS: List[Dict[str, Any]] = [
#     {"format": "fodg", "function_name": "export_to_csv", ...},
#     {"format": "tsv", "function_name": "append_row", ...},
#     {"format": "ndjson", "function_name": "validate_schema", ...},
#     {"format": "abw", "function_name": "search_paragraph", ...},
#     {"format": "gnumeric", "function_name": "delete_sheet", ...},
#     ... (20+ more entries)
# ]
```

These are MANUALLY CURATED, not derived from gap-ledger or capability map.
The docstring says it reads from gap_ledger.json as source #2 — but the primary source
(_EXPANSION_GOALS) dominates and hardcodes specific function names without spec backing.

---

## Gap Ledger State

**Location:** reports/capability-layer/gap-ledger.json
**Total open gaps:** 1,132+ (as of 2026-06-25)
**Traceability:** 41.4% (192 gaps without spec_fact_refs per gap-sal-traceability-20260625.json)

### Gap Categories (sample)
- Load/read capability missing
- Write capability missing
- Analytics function missing
- Spec compliance gap
- Test coverage gap
- Documentation gap
- Export/conversion gap

### Gap Priority Distribution
- P0 (blocking POC): ~50 gaps
- P1 (high priority): ~200 gaps
- P2 (medium): ~400 gaps
- P3 (low): ~482 gaps

### Gap-to-Work-Item Linkage (REPAIRED 2026-06-24)
- gap_ledger_to_work_items.py: includes `gap_ledger_ref: gap_id` field in work items
- capability_feature_compiler.py: includes `gap_ledger_ref` field
- autonomous_cycle.py Step 3a-pre: merges gap_ledger_ref from next-work-items.json

**BUT:** The linkage only activates when autonomous_task_generator is reading gaps.
Since it primarily reads _EXPANSION_GOALS, most work items lack actual gap backing.

---

## Feature Compiler Status

**Planned location:** tools/supervisor/capability_feature_compiler.py
**Design document:** docs/capability-feature-compiler-spec.md (if exists)
**Planned in:** plans/capability-fact-to-feature-production-plan.md

From MEMORY.md (2026-06-23):
> Capability-to-feature compiler spec (2026-06-23): Design at docs/capability-feature-compiler-spec.md.
> Input: gap-ledger.json. Output: next-work-items.json with priority scoring (P0→0, P8→80, impact/blocker adjustments).
> Phase 2 implementation tracked as TC-CAPABILITY-REPAIR-002.

**Status: DESIGN EXISTS; PHASE 2 UNIMPLEMENTED**
- Phase 1 (schema + gap priority scoring): DONE
- Phase 2 (gap → taskcard skeleton with spec_fact_refs): NOT STARTED
- Phase 3 (taskcard → code skeleton generation): NOT STARTED

---

## FeatureFactory Assessment (product_feature_factory.py)

Direct read (lines 1–100):

```python
class FeatureFactory:
    """Generate and insert Python FOSS product functions using repeatable patterns.

    6 patterns:
      Pattern A: Getter    — get_X(model, ...) -> T
      Pattern B: ExportCsv — export_to_csv(source, dest=None) -> str
      Pattern C: Roundtrip — test skeleton only
      Pattern D: Append    — append_row/append_record(source, row) -> bytes
      Pattern E: Probe     — probe_{format}(source) -> dict
      Pattern F: PackageProof — package import proof command
    """
```

**Key limitation:** The class is a code-generation HELPER. It:
1. Reads the target source file
2. Identifies insertion point
3. Generates function body
4. Writes modified source
5. Returns test skeleton string

**But it is NEVER CALLED by autonomous loops.** It requires manual invocation with explicit
source_path, function_name, return_type, docstring, and body_lines parameters.

**Assessment:** Professional implementation of 6 code generation patterns, but:
- Not connected to gap-ledger (no spec_fact_refs generated)
- Not connected to capability map (no capability_id referenced)
- Not connected to autonomous task generator (never auto-triggered)
- Not QName-aware (generates function bodies but doesn't enforce spec_qname hierarchy)

---

## Action Queue Analysis

**Location:** .local/supervisor/action-queue.jsonl (or reports/capability-layer/action-queue.json)

All items have `advisory_only: true`:
```json
{
  "action_id": "ACT-001",
  "format": "CSV",
  "capability": "Load",
  "advisory_only": true,  // ← ALL ITEMS
  "gap_ref": "GAP-CSV-FOSS-LOAD-001",
  "priority": "P0"
}
```

**Root cause:** The action queue is an advisory output of the capability layer. No component
consumes it to generate actual work items with execution instructions. It's a read-only
evidence artifact, not a work queue.

---

## Capability Layer Audit Verdict

| Dimension | Status | Proof |
|---|---|---|
| Capability map generated | YES | unified-capability-map.json populated |
| Gap ledger generated | YES | 1,132+ gaps in gap-ledger.json |
| Gap traceability to SAL | PARTIAL | 41.4% (192 without spec_fact_refs) |
| Feature compiler exists | PARTIAL | Phase 1 done; Phase 2 not started |
| Gap ledger consumed by tasks | NO | autonomous_task_generator uses _EXPANSION_GOALS |
| Action queue actionable | NO | advisory_only=true on all items |
| FeatureFactory called by loops | NO | Manual invocation only |
| Proof graph populated | NO | DORMANT — defined but never populated |
| Capability→feature pipeline complete | NO | Ends at gap-ledger with no downstream |
