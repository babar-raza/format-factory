# Oracle System Investigation — Final Report
# Produced by: TC-ORA-012 (jaunty-whistling-meteor investigation)
# Generated: 2026-07-08
# Plan: plans/.claude/jaunty-whistling-meteor.md

---

## Completion Counters (Final Verification)

```
ORACLE_SURFACES_NOT_INVENTORIED:                 0
ORACLE_CLAIMS_WITHOUT_AUTHORITY:                 2  (SAL string comment + capability oracle absent)
ORACLE_RESULTS_WITHOUT_PERSISTENT_EVIDENCE:      0
ORACLE_RESULTS_WITHOUT_CONSUMERS:                0
ORACLE_GATES_WITH_FALSE_GREEN_PATHS:             2  (G2 fallback + synthetic D1 inflation)
CAPABILITIES_WITHOUT_FACT_PROOF:               398
PRODUCT_CERTIFICATIONS_WITHOUT_PRODUCT_ORACLE_PROOF: 0
UPSTREAM_CHANGES_WITHOUT_INVALIDATION:          20  (no product_source_hash on any format)
REFERENCE_IMPLEMENTATIONS_TREATED_AS_SPEC_AUTHORITY: 0
ORACLE_GAPS_WITHOUT_TASKS:                       0
REQUIRED_PILOTS_WITHOUT_DESIGN:                  0
MATERIAL_SECOND_RUN_CHANGES:                     0
```

---

## What Was Investigated

This investigation examined the Format Factory oracle system through direct code reading,
not documentation. Files read include:
- `tools/oracle/execute_oracle.py` (1,822 lines) — multiple sections
- `tools/supervisor/gate_executor.py` (423 lines) — complete
- `tools/supervisor/governance_validators_oracle.py` — relevant sections
- `oracle/formats/*/oracle-package.yaml` — all 20 formats
- `oracle/formats/*/reports/oracle-run-summary.json` — all 20 formats
- `oracle/oracle-authority-policy.md`
- `oracle/oracle-layer-inventory.yaml`

Oracle runs were executed for all 20 formats on 2026-07-08 to establish a fresh baseline.

---

## Root Causes Identified (Verified by Code)

### RC1: Synthetic property `loaded: true` inflates D1 depth
**File**: execute_oracle.py line 683-685, 713
**Impact**: dif, fodt, sylk report D1 on no real model property comparison

### RC2: Invalid/roundtrip cases not executed for 18/20 formats
**File**: execute_oracle.py lines 1737-1755 (csv/fods guard), 1724 (zst roundtrip)
**Impact**: 18 formats have invalid cases defined but never executed

### RC3: `assertion:` schema silently ignored
**File**: execute_oracle.py line ~751 (`case.get("expected_model_properties", [])`)
**Impact**: abw-valid-001 and abw-valid-002 run at D0 without comparison

### RC4: G2 gate has a test-suite fallback that bypasses oracle
**File**: gate_executor.py lines 119-136
**Impact**: Formats with 0 oracle PASS pass G2 via test file count

### RC5: No product_source_hash — stale evidence undetectable
**File**: oracle-run-summary.json schema (no source hash field)
**Impact**: Product regressions after last oracle run are invisible

---

## Structural Weaknesses Identified

### SW1: if/elif dispatch chain prevents uniform case type handling
Dispatch (lines 1638-1685) has per-format guards for each case type. Adding coverage requires
editing 3+ code sections per format.

### SW2: Two incompatible oracle-package schemas
`expected_model_properties:` (read by executor) and `assertion:` (ignored by executor).
No schema validation at load time catches the mismatch.

### SW3: Depth system has no enforcement below D1
D1 is satisfied by any non-empty `expected_props` list, even synthetic-only. V143 fires only
when ALL cases are D0.

### SW4: G2 fallback inverts gate purpose
The fallback was designed for LibreOffice-absent CI. It now applies to any format with
0 oracle PASS, making the oracle gate optional.

### SW5: Specification and capability oracle boundaries are broken
SAL facts lack provenance. Capability oracle is absent. Authority chain from spec → facts →
capabilities → product is broken at first two links.

---

## What Was Preserved

The following mechanisms are correct and must NOT be changed:

| Component | Reason Preserved |
|---|---|
| Authority class enforcement (check_authority) | Correctly blocks AI_DRAFT_UNVERIFIED, UNKNOWN, REJECTED |
| make_verdict() schema | Well-structured, all fields needed for governance consumers |
| oracle-package.yaml declarative approach | Correct separation of case definitions from execution |
| Per-case authority_refs (spec section citations) | Human-readable spec linkage — valuable for audit |
| ODF RelaxNG D2 validation (schema_validator.py) | Genuine spec-based verification |
| SKIPPED_MISSING_PROVIDER result | Correct handling for LibreOffice-absent environments |
| oracle-run-summary.json committed as evidence | Committed, reviewable, diff-able — keep |
| Acquisition oracle / product oracle boundary | LibreOffice ≠ spec authority — correct |
| SPEC_NORMATIVE vs VERIFIED_INTEROPERABILITY classes | Clear, correct hierarchy |

---

## What Must Be Fixed (6 Targeted Fixes)

All 6 fixes are specified in `plans/oracle/oracle-architecture-implementation-plan.md` with
exact function names, line numbers, code examples, tests, and regression controls.

| Fix | Addresses | File | Impact |
|---|---|---|---|
| Fix 1 | OGAP-001 | execute_oracle.py:713 | dif/fodt/sylk drop to D0 (correct) |
| Fix 2 | OGAP-002 | gate_executor.py:119-136 | G2 fallback removed |
| Fix 3 | OGAP-003 | execute_oracle.py:1757 | Source hash added to summaries |
| Fix 4 | OGAP-005 | execute_oracle.py:1638-1685 | Registry pattern + generic invalid executor |
| Fix 5 | OGAP-004 | execute_oracle.py:751 | assertion: schema read by executor |
| Fix 6 | OGAP-006 | governance_validators_oracle.py:14 | V143 fires on majority-D0 |

**Plus**: Oracle package upgrades for dif, fodt, sylk (required companion to Fix 1).

---

## Design Changes from Adversarial Review

**Design Change 1**: Fix 1 must be sequenced before G2 checks. The oracle package upgrades
for dif/fodt/sylk must be completed before G2 is evaluated, to avoid a visible pipeline failure.

**Design Change 2**: Fix 4 (registry) must include `execute_generic_invalid_case()` to deliver
actual invalid case coverage (not just structural refactoring). Without this, Fix 4 is cosmetic.

---

## Four Oracle Boundaries — Final Classification

| Oracle | Level | Classification | Priority |
|---|---|---|---|
| Specification (SAL) | 1 | AD_HOC — needs provenance fields | Low (not causing false-greens) |
| Capability | 0 | ABSENT — separate project required | Very Low (separate plan needed) |
| Product | 3 | GOVERNED_PARTIAL — 6 fixes authorized | HIGH (false-green paths documented) |
| Acquisition | 2 | BASIC_REPEATABLE — correctly scoped | Medium (LibreOffice version pinning) |

**Acquisition oracle classification**: `ACQUISITION_IS_SEPARATE_INTEROPERABILITY_ORACLE`
Evidence: oracle-package.yaml comment, `check_authority()` treating VERIFIED_INTEROPERABILITY
as non-blocked class, fods-lo-* cases carrying VERIFIED_INTEROPERABILITY (not SPEC_NORMATIVE).

---

## Honest Coverage Assessment (Pre-Fix State)

| Claim | Reality |
|---|---|
| "All 20 formats at D1+" | 17/20 have real D1 cases; 3 (dif, fodt, sylk) are synthetic-inflated D0 |
| "73/75 PASS" | 74/75 PASS (re-run 2026-07-08); all valid cases; invalid cases counted only for csv/fods |
| "20/20 CERTIFIED" | Present but based on partly synthetic D1 evidence |
| "No false-green paths in G2" | 2 false-green paths: fallback code + synthetic D1 |
| "Oracle-run-summary is current" | Current as of 2026-07-08 re-run; no staleness mechanism for future |

---

## Output Artifacts Produced

| Artifact | Path | Status |
|---|---|---|
| Oracle Surface Register | docs/oracle/oracle-surface-register.yaml | COMPLETE |
| Oracle Boundary Register | docs/oracle/oracle-boundary-register.yaml | COMPLETE |
| Oracle Baseline 2026 | docs/oracle/oracle-baseline-2026.yaml | COMPLETE |
| Oracle Readiness Assessment | docs/oracle/oracle-readiness-assessment.md | COMPLETE |
| Target Oracle Architecture | docs/oracle/target-oracle-architecture.md | COMPLETE |
| Oracle Artifact Schemas | oracle/schemas/oracle-artifact-schemas.yaml | COMPLETE |
| Oracle State Machines | docs/oracle/oracle-state-machines.md | COMPLETE |
| Oracle Gap Register | docs/oracle/oracle-gap-register.yaml | COMPLETE |
| Oracle Pilot Designs | docs/oracle/oracle-pilot-designs.md | COMPLETE |
| Adversarial Review | docs/oracle/adversarial-review.md | COMPLETE |
| Implementation Plan | plans/oracle/oracle-architecture-implementation-plan.md | COMPLETE |
| Investigation Final Report (this file) | docs/oracle/oracle-investigation-final-report.md | COMPLETE |

---

## Final Verdict

```
ORACLE_SYSTEM_PARTIAL_TARGET_ARCHITECTURE_AND_PLAN_COMPLETE

The investigation is complete. The architecture is sound — the authority class enforcement,
verdict schema, and oracle-package.yaml approach are correct. Six specific defects were
identified with code-level evidence, analyzed through adversarial review, and formalized
into a hardened implementation plan with exact change locations, tests, and regression controls.

3 of 20 formats (dif, fodt, sylk) claim D1 depth based on synthetic inflation only.
18 of 20 formats have defined but unexecuted invalid cases.
0 formats have product_source_hash — stale evidence is undetectable.
The G2 fallback code exists and could hide zero-oracle-evidence formats.

These are fixable within the existing architecture. No rebuild required.
Proceed with plans/oracle/oracle-architecture-implementation-plan.md.
```
