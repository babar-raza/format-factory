---
visibility: generated
generated_by: codex
sprint: FORMAT-FACTORY-R90-MAINSTREAM-POC-PRODUCT-ACCELERATION-GOVERNED-SKILLS-SUPERVISOR-REPAIR-MEGA-TRAIN-001
---

# Product Factory Acceleration Layer

## Purpose

The acceleration layer turns the POC matrix into bounded, repeatable product work. It does not
authorize gate approval, publication, or freeform source changes.

## Flow

1. `tools/supervisor/select_poc_gaps.py` reads `product-capability-matrix/poc-targets.yaml`.
2. The selector ranks missing load, edit, save, export, dogfood, package, example, and test gaps.
3. `.supervisor/skill-registry.yaml` maps a selected gap to a governed command.
4. If a skill exists, the worker follows that command's path limits, test contract, and ledger rule.
5. If no skill fits, `tools/supervisor/choose_skill_or_handoff.py` generates an execution-handoff
   recommendation. Product source remains unchanged until that handoff is authorized.
6. Every `src/*` edit is recorded in `reports/r90/product-code-change-ledger.json`.
7. `tools/supervisor/validate_product_code_ledger.py` rejects unledgered product-code changes.
8. `tools/supervisor/detect_product_progress.py` detects two consecutive sprints with no capability
   improvement.
9. The next-sprint generator consumes selected gaps, skill registry, ledger rules, dogfood lanes,
   and package/install proof requirements.

## Decision Tree

| Condition | Action |
|---|---|
| Governed skill exists and path scope fits | Execute skill, tests, ledger, and matrix update |
| Skill missing or scope unsafe | Generate taskcard and `/execution-handoff`; do not edit `src/*` |
| External approval required | Stop and report exact gate |
| Prior ungoverned source edit remains functional | Preserve, audit, and ledger as `BACKFILLED_PRE_GOVERNANCE` |

## Dogfood Exports

A dogfood export is implemented only when the source Format Factory library calls a target
Format Factory writer or model. Direct writes remain `GAP_DOGFOOD_EXTERNAL`.

## Capability Progress

Product progress means at least one truthful improvement in load, edit, save, export, dogfood,
package/install, examples/docs, tests, or matrix status. Evidence-only churn does not qualify.
