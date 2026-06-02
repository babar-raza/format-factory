---
sprint: R91
generated_by: r91-worker
---

# Rework + New Work Generation

## Summary

The next-sprint generator has been updated so `reports/supervisor/next-sprint.md` always contains two distinct sections: a REWORK section and a NEW WORK section. This ensures agents always have both repair obligations and forward-progress work in every sprint.

## Output Structure: reports/supervisor/next-sprint.md

### Section 1: REWORK

Contains all items graded as `REWORK_REQUIRED`, `OVERCLAIMED`, or `INSUFFICIENT_EVIDENCE` from the previous sprint's work-item grades.

Each rework lane includes:
- Original `work_item_id` from the failed item
- Exact `rework_instruction` text from the grader
- Evidence paths that need to be updated or created
- Test names that must pass to close the rework
- Acceptance criteria restated verbatim from the original declaration

If no rework exists, the section reads: `REWORK: none — all items accepted`.

### Section 2: NEW WORK

Contains selected POC gaps, master-plan-aligned work, dogfood advances, and package/install proof work.

New work is selected from:
- `.local/supervisor/selected-product-gaps.json` (ranked by POC gap selector)
- `master-plan.md` next tasks
- Dogfood strategy gaps where `dogfood_status != IMPLEMENTED`
- Package/install proof gaps where Gate 10 not yet proven for format

### Parallel Lane Structure

```
LANE-CRITICAL-REWORK:   (must complete before continuation signal can be true)
  - rework items with may_continue_parallel_work=false

LANE-SAFE-PRODUCT-A:    (can proceed in parallel with rework)
  - POC gap advance #1

LANE-SAFE-PRODUCT-B:
  - POC gap advance #2

LANE-DOGFOOD:
  - dogfood bridge implementation

LANE-PACKAGE-INSTALL:
  - package install proof for changed products

LANE-CLOSEOUT:          (always last)
  - evidence-declaration + autonomous-cycle
```

Hard stop (no safe lanes at all) only when:
- All source/product work depends on a blocked external gate, OR
- Test baseline is broken in a way that makes product truth unverifiable

### Evidence-Declaration Closeout Footer

Every generated `next-sprint.md` ends with the mandatory closeout footer:

```
## Sprint Closeout (MANDATORY)

After completing all lanes above:
1. Write evidence-declaration.yaml at .local/evidences/<run_id>/evidence-declaration.yaml
2. Run: python tools/supervisor/supervisor_loop.py autonomous-cycle \
     --declaration .local/evidences/<run_id>/evidence-declaration.yaml
3. Check exit code and continuation signal per CLAUDE.md.
```

## Generator Implementation

`tools/supervisor/generate_next_sprint.py` reads `work-item-grades.json` and `selected-product-gaps.json` to produce the two-section output. The generator is called by `autonomous_cycle.py` Step 4.
