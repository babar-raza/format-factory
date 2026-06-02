---
sprint: R91
generated_by: r91-worker
---

# Supervisor Context Pack

## Summary

A context pack definition has been created. Every generated `next-sprint.md` now includes a context pack header that directs the agent to read a defined set of files before beginning work.

## Context Pack Definition: .supervisor/context-pack.yaml

```yaml
context_pack:
  version: 1
  description: "Mandatory reads before starting any sprint"
  read_order:
    - path: plans/master-plan.md
      reason: "Overall direction and open work items"
    - path: reports/supervisor/session-resume.md
      reason: "Last sprint outcome and continuation status"
    - path: product-capability-matrix/poc-targets.yaml
      reason: "POC gap priority rankings"
    - path: registry/format-registry.yaml
      reason: "Gate authority and format status"
    - path: .supervisor/skill-registry.yaml
      reason: "Available skills and governance rules"
    - path: tools/evidence/product-code-ledger.yaml
      reason: "Governed src changes — required before any src edit"
    - path: reports/supervisor/work-item-grades.json
      reason: "Per-item grades from last sprint — drives rework lanes"
    - path: .local/supervisor/selected-product-gaps.json
      reason: "Pre-selected gaps for new work lanes"
    - path: docs/automation/dogfood-strategy.md
      reason: "Dogfood bridge implementation targets"
    - path: docs/automation/evidence-declaration-schema.md
      reason: "Declaration schema for sprint closeout"
```

## Context Pack Header in next-sprint.md

Every generated `next-sprint.md` begins with:

```markdown
## Context Pack (read before starting)

Before executing any lane below, read the following files in order:
1. plans/master-plan.md
2. reports/supervisor/session-resume.md
3. product-capability-matrix/poc-targets.yaml
4. registry/format-registry.yaml
5. .supervisor/skill-registry.yaml
6. tools/evidence/product-code-ledger.yaml
7. reports/supervisor/work-item-grades.json
8. .local/supervisor/selected-product-gaps.json
9. docs/automation/dogfood-strategy.md
10. docs/automation/evidence-declaration-schema.md

These reads are MANDATORY. Do not begin lane work before completing all reads.
```

## Output: reports/supervisor/context-pack.md

A human-readable version of the context pack is written to `reports/supervisor/context-pack.md` after each autonomous-cycle run. It shows which files were read during the last cycle and their modification timestamps at the time of reading, providing an audit trail.

## Purpose

The context pack prevents agents from making decisions without the current state of:
- Product ledger (preventing ungoverned src changes)
- Work-item grades (preventing repetition of failed work without repair)
- Selected gaps (ensuring new work is pre-ranked, not ad-hoc)
- Dogfood strategy (ensuring dogfood lanes are driven by strategy, not impulse)

## Integration

`generate_next_sprint.py` reads `.supervisor/context-pack.yaml` and prepends the context pack header to every `next-sprint.md` it generates. The header is static text — it does not vary by sprint.
