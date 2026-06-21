# Skill Governance Bypass Audit

**Date:** 2026-06-18
**Authority:** `C:/Users/prora/.claude/plans/smooth-juggling-moler.md`
**Status:** Governance evidence document — no source changes

## Purpose

This document audits known bypass paths in the skill governance system, documents their
severity, and records whether each has been closed by this sprint or remains open.

## Bypass Audit Table

| Bypass | Severity | Mechanism | Closed This Sprint? | Closure Path |
|--------|----------|-----------|--------------------|-|
| `ledger_entry_id` makes `skill_id` advisory for src-editing tracks | HIGH | `validate_adoption_compliance.py`: when `ledger_id` present, `skill_id_recommended=True` (advisory only, never hard fail) | **PARTIALLY CLOSED** | TC-ENFORCE-001 file-based validator (V41) blocks analytics.py changes without skill_id regardless of ledger presence |
| Unknown-track bypass: items with no `product_track` or undeclared track → `transcript_recommended` only (soft), never hard fail | HIGH | Workers with `product_track: unknown` or absent → hit ELSE branch in adoption compliance → only soft advisory | **CLOSED** | TC-ENFORCE-001 file-based validator ignores `product_track` entirely — fires on changed_files pattern |
| `spec_qname_required: true` on ALL existing Python skills forces skill evasion for analytics work | HIGH | Analytics functions have no spec QNames; workers CANNOT use `add-python-api` or `add-python-object-model-feature` without fabricating refs | **CLOSED** | `add-analytics-function` skill has `spec_qname_required: false` |
| Pre-commit LOC cap check inert for non-committing autonomous loop | MEDIUM | `.pre-commit-config.yaml` runs `source_structure_validator.py` only at `stage: pre-commit`. 144+ files uncommitted; hook never fires | **ACCEPTABLE** | `monolith_detection_validator` in `autonomous_cycle.py` is the real enforcer for the running system |
| `GOV_BLOCK:monolith_detection_validator` with no registered rework skill | HIGH | FODG, XCF, ZST blocked by monolith validator with no governed path to resolve the block | **DESIGN CLOSED** | TC-REWORK-001/002 designed `decompose-monolithic-codec` skill; execution sprint is separate |
| TC-0004 zombie reference routing dead work in `next-sprint.md` TASK-011 | MEDIUM | TASK-011 references TC-0004 (stale 2026-05-03 taskcard about 7 unrelated commands); future agents may route work to dead taskcard | **CLOSED** | TC-ZOMBIE-001: TC-0004 marked `superseded`; TASK-011 annotated |
| Analytics work items can declare `exemption_reason: "analytics_no_spec_qname"` to bypass | LOW | Known exemption path; acceptable when `ledger_entry_id` AND `skill_id` are both present | **ACCEPTABLE** | No closure needed; exemption is correct behavior when properly attributed |
| `next-sprint.md` work items can reference any `product_track` string including made-up values | LOW | No validation of `product_track` values in work item generation | **NOT ADDRESSED** | File-based validator (V41) makes track value irrelevant for analytics attribution; low priority |
| Multiple analytics functions added in single sprint may share a prime (duplicate prime) | MEDIUM | `prime_collision_check` in skill Step 2 only checks one prime at a time | **ADDRESSED IN SKILL** | `add-analytics-function` Step 2 performs prime collision check before each function addition |

## Detailed Analysis of Key Bypasses

### Bypass 1: `ledger_entry_id` loophole (HIGH — Partially Closed)

**Mechanism:** In `validate_adoption_compliance.py`, when a work item has a `ledger_entry_id`,
the enforcement downgrades to advisory:
```python
if ledger_id:
    checks["transcript_recommended"] = True
    checks["skill_id_recommended"] = True  # advisory only
```
Deepening sprints always have `ledger_entry_id` (they write ledger entries). This made
`skill_id` permanently optional for the highest-volume work type.

**Closure (TC-ENFORCE-001):** The new `validate_analytics_skill_required` (V41) validator
operates on `changed_files`, not on `product_track` or `ledger_entry_id`. It fires on
`src/python/*/analytics.py` matches regardless of ledger status. The loophole is closed
for analytics.py changes. Codec file changes are covered by RULE-AM-001 (V40).

### Bypass 2: Unknown-track bypass (HIGH — CLOSED)

**Mechanism:** Workers that don't declare `product_track` or declare an unrecognized
value (e.g., `unknown`, `foss_python_analytics` before this sprint registered it) hit
the ELSE branch in adoption compliance: only `transcript_recommended` (soft), never hard fail.

**Closure:** V41 matches on file paths, completely bypassing `product_track` lookup.

### Bypass 3: spec_qname barrier (HIGH — CLOSED)

**Mechanism:** All existing Python product skills have `spec_qname_required: true`.
Analytics functions have no spec QName references. Workers rational incentive: skip
skill attribution entirely rather than fabricate QName refs.

**Closure:** `add-analytics-function` has `spec_qname_required: false`. Workers can
now use the skill without fabricated references.

### Bypass 5: Monolith block with no rework path (HIGH — Design Closed)

**Mechanism:** `GOV_BLOCK:monolith_detection_validator` fires for FODG (active), XCF,
ZST (latent). No registered skill existed to resolve the block in a governed way.

**Design closure:** `taskcards/skill-gaps/decompose-monolithic-codec-design.md` provides
the full skill design. Format-specific rework paths are in `taskcards/skill-gaps/`.
Actual execution is a separate dedicated sprint per format.

## Open Gaps After This Sprint

1. **`decompose-monolithic-codec` skill is designed but not yet registered or implemented**
   — execution sprint required per format (FODG first, then XCF, ZST)
2. **200+ existing analytics functions in codec files** have no `skill_id` in their
   ledger entries — grandfathered as `BACKFILLED_PRE_GOVERNANCE`; migration to `analytics.py`
   governed by future sprints per §24.7
3. **`next-sprint.md` `product_track` field not validated** against an allowlist
   — low priority; V41 makes this irrelevant for analytics attribution
