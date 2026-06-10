# Production Blocker Review — Specification Authority Layer
Sprint ID: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-BLOCKER-PLAN-HEALING-001

## Overview

The Specification Authority Layer addresses 10 production blockers in the current Format Factory
architecture. Each blocker prevents reliable, traceable spec access for agents and LLMs.

---

## Blocker 1 — No Deterministic Context-Pack Contract

**Symptom:** Specs retrieved differently each run; no stable manifest hash.
**Impact:** AI outputs cannot be reproduced, audited, or regression-tested against stable inputs.
**Required Fix:** ContextPackBuilder produces same manifest.sha256 for identical inputs.
**Healed By:** Section 6 deterministic contract; ContextPackBuilder subsystem.
**Status:** ADDRESSED

---

## Blocker 2 — No Lifecycle Model

**Symptom:** No formal state machine for spec artifacts.
**Impact:** Cannot determine which artifacts are fresh, stale, partial, or verified.
**Required Fix:** 13-state lifecycle (source_candidate through refresh_event) with enforced transitions.
**Healed By:** spec-data-lifecycle-model.md; SpecGovernanceRuntime enforcement.
**Status:** ADDRESSED

---

## Blocker 3 — No Staleness Chain

**Symptom:** Source SHA-256 changes not propagated downstream.
**Impact:** Downstream artifacts (parsed, normalized, indexed, digested, requirements, packs) become
silently stale without triggering refresh.
**Required Fix:** Staleness propagation: source sha256 change → D through J states marked stale
→ SpecGovernanceRuntime triggers refresh from B.
**Healed By:** staleness-refresh-invalidation-model.md.
**Status:** ADDRESSED

---

## Blocker 4 — No Regression Controls

**Symptom:** No test coverage for spec layer failures.
**Impact:** Regressions in parser, normalizer, verifier, or context pack determinism go undetected.
**Required Fix:** 9-category regression suite with 42+ tests covering schema, provenance, parser
round-trip, context pack, requirement verifier negatives, coverage, four-stream, refresh, anti-bypass.
**Healed By:** regression-control-suite.md.
**Status:** ADDRESSED

---

## Blocker 5 — No Usage Ledger Production Model

**Symptom:** No append-only tracking of spec usage.
**Impact:** Cannot audit which specs informed which AI outputs; no correction history.
**Required Fix:** Append-only JSONL ledger at .local/spec-usage-ledger/usage-YYYYMMDD.jsonl.
**Healed By:** spec-usage-ledger-production-model.md.
**Status:** ADDRESSED

---

## Blocker 6 — No Four-Stream Enforcement

**Symptom:** Spec handoffs not enforced at stream boundaries.
**Impact:** Agents can use unregistered specs; AI drafts bypass verification; coverage gaps hidden.
**Required Fix:** Mainstream/Acceleration/Skills/Supervisor each have explicit handoff gates requiring
context_pack_id, requirement_ids, source_snapshot_ids.
**Healed By:** four-stream-enforcement-model.md.
**Status:** ADDRESSED

---

## Blocker 7 — Shallow Execution Prompt

**Symptom:** Original prompt lacked architectural depth; 9 execution-safety defects.
**Impact:** Execution agent could not produce a correct, safe, portable healing sprint.
**Required Fix:** Phase 1 repair (9 defects) + Phase 2 hardening (10 fixes) = final-ready-to-send prompt.
**Healed By:** Repair sprint (FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-HEALING-PLAN-REPAIR-001).
**Status:** ADDRESSED (repair sprint complete)

---

## Blocker 8 — Taskcard Count Contradiction

**Symptom:** Original plan documented 19 taskcards but actual count differed.
**Impact:** Validation using hardcoded counts produced false failures.
**Required Fix:** Declared-vs-materialized validation; taskcard-state.json as source of truth.
**Healed By:** file-ownership-map.json + taskcard-state.json declared-vs-materialized approach.
**Status:** ADDRESSED

---

## Blocker 9 — Pilot Scope Too Broad

**Symptom:** 5 formats at shallow depth.
**Impact:** No format reaches production-depth lifecycle; all formats remain at candidate level.
**Required Fix:** 3 formats (ZST, Netpbm, DIF) at full lifecycle depth; Gnumeric and FODS/FODT
at source registration + fetch-plan depth only.
**Healed By:** pilot-zst.md, pilot-netpbm.md, pilot-dif.md, pilot-extended-prep.md.
**Status:** ADDRESSED

---

## Blocker 10 — Two Missing Subsystems

**Symptom:** SpecNormalizer and SpecSourceRegistry absent from original architecture.
**Impact:** Without SpecNormalizer, cross-format requirement comparison is impossible.
Without SpecSourceRegistry, source trust chain is unanchored.
**Required Fix:** Both subsystems added to 11-subsystem pipeline.
**Healed By:** production-architecture-redesign.md; tool-implementations.md (all 13 tools).
**Status:** ADDRESSED

---

## Summary

All 10 production blockers addressed. Architecture is production-ready for MWP execution.

| Blocker | Status |
|---------|--------|
| 1. No deterministic context-pack contract | ADDRESSED |
| 2. No lifecycle model | ADDRESSED |
| 3. No staleness chain | ADDRESSED |
| 4. No regression controls | ADDRESSED |
| 5. No usage ledger production model | ADDRESSED |
| 6. No four-stream enforcement | ADDRESSED |
| 7. Shallow execution prompt | ADDRESSED |
| 8. Taskcard count contradiction | ADDRESSED |
| 9. Pilot scope too broad | ADDRESSED |
| 10. Two missing subsystems | ADDRESSED |
