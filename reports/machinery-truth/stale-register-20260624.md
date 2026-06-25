# Stale Document and Claim Register
**Mission:** MACHINERY-TRUTH-PRODUCT-CONTRACT-20260624
**Generated:** 2026-06-24

This register tracks documents and claims that have been superseded, contradicted,
or made stale by current HEAD state. Do not overwrite history — mark as stale here.

---

## Stale Documents

### docs/architecture.md
- **Status:** STALE (Phase 0 content in a Phase 4+ system)
- **Last Reviewed:** 2026-05-04
- **Stale Sections:**
  - Folder tree (missing src/net/, tools/supervisor/ 172 files, shared/qname-registry/, etc.)
  - "11 validators" in governance validators section (actual: 50+)
  - `src/dotnet/` as .NET target (actual: `src/net/`)
  - Pipeline architecture (simple 11-step; actual: multi-layer SAL+capability+governance)
- **Fix Applied:** Phase 4+ Current State addendum appended (2026-06-24)
- **Action Required:** Full architecture.md rewrite to reflect Phase 4 reality

### plans/spec-to-feature-radical-correction-plan.md
- **Status:** PARTIALLY_STALE (written 2026-06-12; many failure items since addressed)
- **Stale Claims:**
  - "SAL is ghost infrastructure (3/20 tools active)" — CONTRADICTED (14,309 facts, 22 tools)
  - "No capability-to-feature compiler exists" — CONTRADICTED (exists and wired)
  - "Capability Layer generates output nobody consumes" — SUPERSEDED
- **Current Claims (still valid):**
  - "ZERO durable learning" — STILL CURRENT
  - "Lane ownership not enforced by code" — STILL CURRENT (SUP-GAP-001)
  - "DAG ordering not enforced by code" — STILL CURRENT (SUP-GAP-002)
  - Gate 11 criteria C1-C20, P1-P11 — STILL CURRENT
- **Action Required:** Audit and update the "6 systemic failures" section to reflect current state

### plans/master-plan.md
- **Status:** CURRENT (v5.7, Section 49 CLOSED — no new open section)
- **Stale Claim:** No current open section for active work (work drives from next-sprint.md)
- **Action Required:** Open Section 50 when next major mission begins

### docs/code-quality/machinery-proof-20260623.md
- **Status:** REQUIRES_VERIFICATION — written 2026-06-23; some claims about machinery
  completeness predate the correction plan audit findings
- **Action Required:** Compare against current HEAD before relying on it

---

## Stale Ledger Claims

### registry/product-deepening-ledger.yaml
- **Status:** CURRENT (last updated 2026-06-23/24)
- **Note:** qname_evidence.entry_count is 0 for all formats — this field is not being
  populated from the QName registry YAML files. The ledger entry_count should reflect
  the count from shared/qname-registry/{format}.yaml entries.
- **Action Required:** Wire qname_evidence.entry_count to count entries in qname-registry YAMLs

### registry/source-structure-baseline.json
- **Status:** CURRENT (baseline_loc_cap is frozen write-once; loc is mutable)
- **Note:** Some analytics.py files (ndjson_analytics.py at 923 LOC) added as known_violations
  with their current size as baseline_loc_cap

### reports/capability-layer/gap-ledger.json
- **Status:** CURRENT (generated 2026-06-24, 1,003 gaps)
- **File Size:** 29MB — likely contains full spec text embedded in gap descriptions
- **Note:** All gaps are either closed or DEFERRED_BY_DESIGN; 0 POC-blocking; new gaps
  require spec analysis to add

---

## CONTRADICTED Claims to Propagate

The following CONTRADICTED claims in spec-to-feature-radical-correction-plan.md should
be acknowledged when that plan is referenced:

| Claim in Plan | Current Truth | Resolution |
|---------------|--------------|-----------|
| "SAL is ghost infrastructure" | SAL has 14,309 facts, 22 tools, runs in autonomous_cycle | CONTRADICTED — plan claim is stale |
| "No capability-to-feature compiler" | Exists at tools/capability_layer/capability_to_feature_compiler.py | CONTRADICTED |
| "Capability Layer output unconsumed" | autonomous_cycle.py Step 3a-pre consumes gap_ledger | SUPERSEDED |
| "11 validators" (architecture.md) | 50 validate_* functions + V67 | CONTRADICTED |
| ".NET at src/dotnet/" (architecture.md) | .NET product at src/net/ | CONTRADICTED |

---

## REQUIRES_MORE_EVIDENCE

| Claim | Gap |
|-------|-----|
| Overclaim detector (10 patterns) fully wired | TC-GUARD-001/002 exist but full 10-pattern claim from correction plan needs verification |
| FODS Compat/ facades are thin delegation wrappers | Inspection shows they are empty shells (architecture markers) — behavior is in models.py |
| xcf_layer_name_list returns real XCF layer names | CONTRADICTED — returns synthetic "Layer N" names |
| All .NET tests pass (618 for FODS) | Recorded in poc-targets.yaml; not re-verified at current HEAD |
