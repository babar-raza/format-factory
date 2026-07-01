# Capability-to-Feature Compiler — Design Specification

**Status:** DESIGN (TC-CAPABILITY-REPAIR-001)
**Lane:** Machinery
**Author:** Agent-generated, 2026-06-23

---

## 1. Purpose

The capability-to-feature compiler reads `reports/capability-layer/gap-ledger.json`
and emits `reports/supervisor/next-work-items.json`, translating gap-layer priorities
into actionable work items for the autonomous sprint loop.

Today this pipeline does not exist. The `next-work-items.json` file is produced directly
by `generate_next_work_items.py` using heuristics, without consulting gap-ledger entries.
This results in advisory-only capability data that never feeds product deepening.

---

## 2. Input Schema — gap-ledger.json

```
{
  "schema_version": "1.0",
  "generated_at": "<ISO timestamp>",
  "sprint_id": "<run_id>",
  "run_id": "<run_id>",
  "total_gaps": <int>,
  "gaps": [ <GapEntry>, ... ]
}
```

**GapEntry fields (all present per current schema_version=1.0):**

| Field | Type | Description |
|-------|------|-------------|
| `gap_id` | string | Unique ID, e.g. `GAP-FODS-COMM-LOAD-001` |
| `format` | string | Format name, e.g. `FODS`, `NDJSON` |
| `product_type` | string | `commercial` or `foss` |
| `capability_name` | string | Human-readable capability, e.g. `Load` |
| `current_state` | string | `not_started`, `architecture_only`, `implementation_verified`, etc. |
| `gap_type` | string | `missing_test_coverage`, `missing_implementation`, `spec_parity_gap`, etc. |
| `status` | string | `open` or `closed` |
| `blocks_poc` | bool | Whether this gap blocks PoC gate |
| `blocks_readiness` | bool | Whether this gap blocks release readiness |
| `commercial_impact` | string | `HIGH`, `MEDIUM`, `LOW`, `NONE` |
| `foss_impact` | string | `HIGH`, `MEDIUM`, `LOW`, `NONE` |
| `priority` | string | `P0`–`P8` maturity gate level |
| `owning_lane` | int | Lane number 1–15 from spec-to-feature plan |
| `suggested_taskcard` | string | Free-text suggestion for next taskcard |
| `suggested_pilot` | string | Suggested pilot format or approach |
| `suggested_verification` | string | Suggested verification command |
| `recurrence_prevention` | string | Notes on preventing recurrence |
| `blockers` | list | Upstream blockers (gap_ids or string descriptions) |
| `related_capability_id` | string | Reference to capability registry entry |
| `notes` | string | Additional context |
| `spec_facts` | list | Spec fact IDs (e.g. `FACT-FODS-001`) |

---

## 3. Output Schema — next-work-items.json

```json
{
  "items": [ <WorkItem>, ... ],
  "work_selection_mode": "CAPABILITY_COMPILER",
  "stream": "mainstream",
  "compiler_run_id": "<ISO timestamp>",
  "gap_ledger_version": "<schema_version>",
  "total_input_gaps": <int>,
  "open_gaps_processed": <int>
}
```

**WorkItem fields:**

| Field | Type | Description |
|-------|------|-------------|
| `item_id` | string | Derived from `gap_id`, e.g. `WI-GAP-FODS-COMM-LOAD-001` |
| `title` | string | `<capability_name> for <format>` |
| `lane` | string | `product` or `machinery` (derived from `owning_lane`) |
| `priority` | int | Integer priority (see §4) |
| `description` | string | Constructed from gap fields |
| `acceptance_criteria` | string | From `suggested_verification` or default |
| `verification_command` | string | From `suggested_verification` |
| `evidence_expected` | string | Default based on `gap_type` |
| `source` | string | `gap_ledger` |
| `stop_reason_adjudication` | string | `agent-owned` |
| `human_required` | bool | `true` only if blockers contain external gate |
| `blocked_by` | null or list | From `blockers` field if non-empty |
| `external_gate` | bool | `true` only if `blocks_readiness=true` and `product_type=commercial` |
| `gap_id` | string | Original `gap_id` for traceability |
| `spec_facts` | list | Passthrough from gap entry |
| `gap_ref` | string | Same as `gap_id` for guard-001 compliance |

---

## 4. Priority Scoring Algorithm

Each open gap receives a numeric priority score (lower = higher priority):

```
score = base_priority + impact_penalty + blocker_bonus
```

**base_priority** — from `priority` field:
```
P0 → 0
P1 → 10
P2 → 20
P3 → 30
P4 → 40
P5 → 50
P6 → 60
P7 → 70
P8 → 80
```

**impact_penalty** — from impact fields (lower is more impactful):
```
commercial_impact=HIGH  AND foss_impact=HIGH  → -10
commercial_impact=HIGH  AND foss_impact=LOW   → -5
commercial_impact=LOW   AND foss_impact=HIGH  → -3
otherwise                                      →  0
```

**blocker_bonus** — from blocking flags:
```
blocks_poc=true       → -8
blocks_readiness=true → -5
(cumulative)
```

**Tie-breaking** (applied in order):
1. gaps with `blocks_poc=true` before those without
2. gaps with `blocks_readiness=true` before those without
3. alphabetical by `gap_id`

The final output `items` list is sorted by score ascending and truncated to the
top `MAX_ITEMS` (default: 20).

---

## 5. Filtering Rules

The compiler applies these filters before scoring:

1. **Skip closed gaps:** `status == "closed"` → excluded
2. **Skip machinery-owned gaps:** `owning_lane >= 14` → excluded (handled by supervisor)
3. **Skip gaps with unresolved external blockers:** if any blocker string matches
   `TRUE_EXTERNAL_GATE` pattern → mark `external_gate=true`, include but deprioritize
4. **Deduplicate by format+capability:** if two gaps share `format` + `capability_name`,
   keep only the highest-priority one

---

## 6. Field Mapping — Gap → WorkItem

| Gap field | WorkItem field | Transform |
|-----------|----------------|-----------|
| `gap_id` | `item_id` | prepend `WI-` |
| `gap_id` | `gap_id`, `gap_ref` | passthrough |
| `capability_name` + `format` | `title` | `"{capability_name} for {format}"` |
| `owning_lane` | `lane` | lanes 1–13 → `product`; lanes 14–15 → `machinery` |
| score (computed) | `priority` | integer 0–100 |
| `suggested_taskcard` or default | `description` | use `suggested_taskcard` if non-empty, else construct from gap fields |
| `suggested_verification` | `verification_command` | passthrough or default `""` |
| `suggested_verification` | `acceptance_criteria` | passthrough or `"Verification passes"` |
| `gap_type` | `evidence_expected` | mapping (see §7) |
| `blockers` | `blocked_by` | `null` if empty, else list |
| `blocks_readiness` AND `product_type=commercial` | `external_gate` | bool |
| `spec_facts` | `spec_facts` | passthrough |

---

## 7. Gap Type → Evidence Expected Mapping

| `gap_type` | `evidence_expected` |
|------------|---------------------|
| `missing_test_coverage` | `"Tests added and passing"` |
| `missing_implementation` | `"Implementation committed, tests pass"` |
| `spec_parity_gap` | `"spec_qname on class, spec fact referenced"` |
| `architecture_only` | `"Behavioral implementation replacing stub"` |
| `missing_qname_registration` | `"QName registry entry with python_file"` |
| `missing_capability_annotation` | `"capability_ref in declaration"` |
| (default) | `"Work item accepted by supervisor pipeline"` |

---

## 8. Deduplication

After scoring and filtering, if two work items have the same `format` + `capability_name`,
the compiler keeps the entry with the lower score. The other entry is written to a
`deduplicated_items` list in the output for audit purposes.

---

## 9. Output File Locations

| File | Description |
|------|-------------|
| `reports/supervisor/next-work-items.json` | Primary output consumed by `check_continuation.py` |
| `reports/capability-layer/compiler-run-{timestamp}.json` | Audit log of each compiler run |

---

## 10. CLI Interface

```bash
python tools/supervisor/capability_feature_compiler.py \
    --gap-ledger reports/capability-layer/gap-ledger.json \
    --output reports/supervisor/next-work-items.json \
    [--max-items 20] \
    [--dry-run]
```

- `--dry-run`: print compiled items to stdout without writing files
- `--max-items N`: limit output to N items (default 20)
- Exit 0: success
- Exit 1: gap-ledger not found or invalid schema
- Exit 2: output write failure

---

## 11. Integration Points

| Component | Current | After Compiler |
|-----------|---------|----------------|
| `generate_next_work_items.py` | Produces next-work-items.json from heuristics | Calls compiler as fallback when gap-ledger exists |
| `check_continuation.py` | Reads next-work-items.json | Unchanged |
| `autonomous_cycle.py` | Reads next-work-items.json | Unchanged |
| `gap-ledger.json` | Advisory only | Input to compiler |
| TC-GUARD-001 | Enforces gap_ledger_ref on work items | Work items from compiler always have `gap_ref` |

---

## 12. Implementation Sequence (Phased)

**Phase 1 (this design — TC-CAPABILITY-REPAIR-001):**
- [x] Design document at `docs/code-quality/capability-feature-compiler-spec.md`
- [x] Input/output schema fully specified
- [x] Priority scoring algorithm documented

**Phase 2 (TC-CAPABILITY-REPAIR-002 — future):**
- [ ] Implement `tools/supervisor/capability_feature_compiler.py` per this spec
- [ ] Add unit tests in `tests/supervisor/test_capability_feature_compiler.py`
- [ ] Wire into `generate_next_work_items.py` as primary source

**Phase 3 (TC-FEATURE-COMPILER-001 — future):**
- [ ] Feature-level work items (per spec feature, not just capability)
- [ ] Spec fact → feature mapping
- [ ] Traceability chain: SAL fact → QName → gap → work item → declaration
