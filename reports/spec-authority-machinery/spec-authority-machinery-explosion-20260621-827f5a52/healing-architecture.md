# Spec Authority Machinery — Healing Architecture Audit

**Run ID:** `spec-authority-machinery-explosion-20260621-827f5a52`
**Date:** 2026-06-21

---

## Healing Architecture Components

### 1. Healing Gate (`check_system_healing_gate.py`)

| Lane | Name | Current State | Architecture Assessment |
|------|------|--------------|-------------------------|
| 1 | SAL Pipeline | PASS — `fods_facts_gte_10: true`, `fodt_facts_gte_10: true` | SHALLOW. Checks fact count existence, not workbench_verified depth. Architecture correct; criterion needs updating. |
| 2 | Capability Reintegration | PASS — gap_ledger, cap_map, action_queue exist | STRUCTURAL CHECK. `action_queue_not_advisory: false` — queue still advisory (not enforced). |
| 3 | Compiler | PASS — compiler exists, 513 lines | OK |
| 4 | Skills/Prompts | PASS — 44 skills | OK |
| 5 | Validators | PASS — governance_validators exists, 3,077 lines | OK |
| 6 | QName Ontology | PASS — 10 ontology YAMLs | OK |
| 14 | Supervision Audit | PASS — supervisor_loop, autonomous_cycle, governance_validators, lane_enforcement exist | INFRASTRUCTURE CHECK. Doesn't validate correctness. |
| 15 | Healing/Learning | PASS — ai_learning_loop, bounded_repair, anti_skip_checker exist | INFRASTRUCTURE CHECK. |

**Key architectural gap (Lane 1):** The `fods_facts_gte_10` criterion was sufficient when we had only 14 FODS format-specific facts. Now FODS has 4,987 workbench facts. The criterion is obsolete — it passes trivially. The architecture should advance to checking `workbench_verified_fact_count > 0` per format or per tier.

**Proposed Lane 1 criteria update:**
```yaml
fods_workbench_verified_count_positive: true  # workbench_verified_fact_count > 0 for FODS
fodt_workbench_verified_count_positive: true  # workbench_verified_fact_count > 0 for FODT
zst_workbench_verified_count_positive: true   # workbench_verified_fact_count > 0 for ZST
zero_fact_formats_documented: true            # formats with 0 wb facts have documented reason in authority-debt-ledger.json
```

---

### 2. SAL Pipeline Mode

The SAL pipeline supports two modes:
- **Default mode:** template + workbench merged (current daily output)
- **Clean mode (`from_cache_only=True`):** workbench only (used in idempotency tests)

**Architecture gap:** The daily output should use clean mode. The architecture's intent (evidenced by the `from_cache_only` parameter design) is to separate these modes. The daily pipeline defaulting to the mixed mode is an integration gap, not an architectural design flaw.

**Proposed fix:** Change daily SAL invocation to `from_cache_only=True`. This would:
- Remove template facts from the daily fact index
- Make GAP-INT-002's fact index workbench-only by default
- Enable meaningful `source == workbench_verified` checks

---

### 3. TC-GUARD-001 and Gap Ledger Architecture

The architecture envisions TC-GUARD-001 as the primary enforcement gate. It correctly blocks items without gap references. The missing architectural component is the quality dimension of the gap reference.

**Proposed addition:**
```python
# In autonomous_cycle.py Step 2d3 (after current BLOCK logic):
if gap_ledger_ref:
    gap = load_gap(gap_ledger_ref)
    format_id = gap.get('format')
    wb_count = get_sal_workbench_count(format_id)
    if wb_count == 0:
        warnings.append(f"TC-GUARD-ADVISORY: {gap_ledger_ref} format {format_id} has 0 workbench facts")
```

This would NOT block (per non-disruptive repair doctrine) but would emit a visible warning.

---

### 4. `source` Field vs `authority_level` Field

The plan assumed `authority_level` would be a per-fact field. Implementation uses `source: "workbench_verified"` instead. This is functionally equivalent:
- `source == "workbench_verified"` ↔ `authority_level == HIGH`
- `fact_status == "bootstrap_only"` ↔ `authority_level == LOW`

**Assessment:** Naming difference only. No architectural repair needed. Documentation should acknowledge the equivalence.

---

### 5. Failure Memory and Learning

`failure_memory.py` is referenced as wired in `autonomous_task_generator.py` (from plan evidence). This prevents recurring gap closures from spinning. However:
- No evidence of failure_memory handling spec acquisition failures for Gnumeric/ABW
- No automatic escalation when a format has 0 workbench facts for multiple consecutive sprints

**Architectural gap:** Persistent zero-fact formats should generate a documented entry in `authority-debt-ledger.json` after N sprints without progress.

---

### 6. Autonomous Cycle SAL Integration (Absent)

The most significant architectural gap: `autonomous_cycle.py` does not read `sal-facts-latest.json`. The entire SAL pipeline operates as a parallel advisory system. The architecture diagram shows SAL feeding into the gate layer, but no code implements this connection.

**Proposed integration:**
```python
# Step 1c (new): Load SAL workbench counts as advisory context
sal_facts = load_sal_facts()
per_format_wb_counts = {r['format_id']: r['workbench_verified_fact_count'] for r in sal_facts['results']}
# Use per_format_wb_counts in Step 2d3 (TC-GUARD-001 advisory depth check)
```

This is a targeted, non-blocking integration that adds advisory depth information without changing gate logic.

---

## Architecture Assessment Summary

| Component | Design Intent | Implementation Status | Gap |
|-----------|--------------|----------------------|-----|
| SAL daily output | workbench-only | DEFAULT MODE (mixed) | Switch to from_cache_only |
| Healing gate Lane 1 | workbench_count per format | exists_check only | Update criterion |
| TC-GUARD-001 | authority depth enforcement | presence-only | Add advisory depth check |
| Failure memory | persistent gap tracking | wired (basic) | Add spec-acquisition failure entries |
| SAL → autonomous_cycle | feed authority context | NOT CONNECTED | Add minimal integration |
| Gap ledger authority_level | per-gap quality field | ABSENT | Add field; derive from SAL counts |
