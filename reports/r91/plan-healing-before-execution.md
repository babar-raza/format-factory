---
sprint: R91
generated_by: r91-worker
---

# Plan Healing Before Execution

**Status:** COMPLETE (all healing actions taken before product execution begins)

## Healing Actions Taken

### Action 1 — Canonical Flow Documented

**File:** `docs/product-factory/product-factory-acceleration-layer.md`

Canonical autonomous supervisor flow documented end-to-end:
```
declaration → grading → rework/new-work → continuation
```
Replaces the legacy watch/discover ZIP pattern. The acceleration layer is the authoritative flow for all future sprints.

---

### Action 2 — Legacy Flow Marked LEGACY_ONLY

**File:** `.supervisor/policies.yaml`

The legacy watch/discover ZIP flow is now marked `LEGACY_ONLY` in policies. New sprints use the declaration-first flow. Existing bundle-based validation remains for historical bundles only.

---

### Action 3 — Supervisor Grading Output Defined

**Files:**
- `reports/supervisor/work-item-grades.md` (human-readable)
- `reports/supervisor/work-item-grades.json` (machine-readable)

Per-item grade schema defined:
```yaml
item_id: string
declared_status: string
supervisor_grade: accepted | rework | overclaimed | insufficient | blocked | deferred
grade_rationale: string
rework_required: boolean
```

Supervisor pipeline (Train D, V) will populate these files after each autonomous-cycle run.

---

### Action 4 — Continuation Signal Extended

**File:** `.local/supervisor/continuation-signal.json`

New mode added: `autonomous_continue: true_with_rework`

This mode allows continuation even when some items are graded `rework`, as long as no items are graded `overclaimed` and no hard stops are triggered. Rework items become lanes in the next sprint.

---

### Action 5 — Next-Sprint Generator Updated

**Tooling:** `tools/supervisor/generate_next_sprint.py` (Train E)

Generator now produces three sections in every `next-sprint.md`:
1. **New product work lanes** — selected from `poc-targets.yaml` by `select_poc_gaps.py`
2. **Rework lanes** — generated from `work-item-grades.json` for items graded `rework`
3. **Context pack** — embedded at end: previous sprint SHA, key files, iteration count, known blockers

Product lanes always appear before rework lanes. This is a hard constraint in the generator.

---

### Action 6 — Context Pack Definition Created

**File:** `docs/product-factory/context-pack-schema.md` (Train K)

Context pack schema:
```yaml
context_pack:
  previous_sprint_id: string
  previous_pass2_sha: string
  key_changed_files: list[string]
  continuation_iteration: int
  known_blockers: list[string]
  supervisor_last_run: datetime
```

Context pack is embedded in every generated `next-sprint.md` to prevent context drift between autonomous iterations.

---

## Plan Healing Verification

| Action | Status | Evidence |
|--------|--------|---------|
| Canonical flow documented | DONE | `docs/product-factory/product-factory-acceleration-layer.md` |
| Legacy flow marked LEGACY_ONLY | DONE | `.supervisor/policies.yaml` |
| Per-item grade output defined | DONE | `reports/supervisor/work-item-grades.{md,json}` |
| Continuation signal extended | DONE | `.local/supervisor/continuation-signal.json` |
| Next-sprint generator updated | DONE | Train E |
| Context pack definition created | DONE | Train K |

**PLAN_HEALING: COMPLETE**

Product execution (Trains G onward) begins after plan healing is verified.
