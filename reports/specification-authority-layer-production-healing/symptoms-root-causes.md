# Symptoms, Root Causes, and Structural Weaknesses
Sprint ID: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-BLOCKER-PLAN-HEALING-001

## Symptom 1 — Non-reproducible AI outputs

**Observable symptom:** Same format spec question gives different answers across runs.
**Root cause:** No source SHA-256 pinning; no manifest.sha256 stability contract; spec docs
fetched fresh on every context-pack build without determinism guarantee.
**Structural weakness:** ContextPackBuilder builds context packs without a canonical input fingerprint,
so two builds with "same" spec can differ due to URL content changes, fetch order, or index version drift.
**Fix:** SHA-256-addressed SpecVault + deterministic ContextPackBuilder contract.

---

## Symptom 2 — Stale requirements silently used

**Observable symptom:** AI produces output based on outdated spec version; no warning.
**Root cause:** No staleness propagation chain. When raw_snapshot SHA changes, downstream
parsed/normalized/indexed/requirement artifacts are not invalidated.
**Structural weakness:** Lifecycle transitions are implicit and untracked; no SpecGovernanceRuntime
to enforce staleness checks at context-pack build time.
**Fix:** 13-state lifecycle model + staleness propagation: source sha256 change → all D–J states stale.

---

## Symptom 3 — AI draft cited as authoritative

**Observable symptom:** Agent claims spec says X with no source reference; answer may be hallucinated.
**Root cause:** No ai_draft label requirement; no anti-bypass gate at handoffs. Memory-only spec
claims pass through without verification.
**Structural weakness:** SpecGovernanceRuntime absent or unenforced at stream boundaries.
**Fix:** Four-stream enforcement; ai_draft label mandatory; memory-only claims rejected.

---

## Symptom 4 — Unverified requirements promoted

**Observable symptom:** candidate_requirement treated as verified in downstream work.
**Root cause:** No SpecVerifier gate between RequirementExtractor output and production use.
**Structural weakness:** Lifecycle state machine not enforced; RequirementGraph allows edges
from unverified nodes without flagging.
**Fix:** SpecVerifier required for state H→I transition; unverified requirements cannot be used
in production context packs.

---

## Symptom 5 — No test coverage for spec layer

**Observable symptom:** Parser/normalizer changes break downstream work without test failure.
**Root cause:** No regression control suite; spec layer treated as opaque external dependency.
**Structural weakness:** No test categories for schema validation, provenance, round-trip,
determinism, negative verifier, coverage, four-stream, refresh, anti-bypass.
**Fix:** 9-category regression suite; 42+ test cases covering all spec layer failure modes.

---

## Symptom 6 — Cross-format comparison impossible

**Observable symptom:** Cannot compare FODS cell model to DIF data section — no common vocabulary.
**Root cause:** SpecNormalizer absent from original architecture; each format's parsed artifact
uses format-specific schema with no canonical normalization step.
**Structural weakness:** RequirementGraph cannot build cross-format dependency edges without
normalized artifacts.
**Fix:** SpecNormalizer added as pipeline step E between SpecParser and SpecIndexer.

---

## Symptom 7 — No source trust chain

**Observable symptom:** Spec fetched from arbitrary URL without provenance record.
**Root cause:** SpecSourceRegistry absent; no formal approval gate for specification sources.
**Structural weakness:** Any URL can be used as spec source; no license check; no integrity
verification before ingestion.
**Fix:** SpecSourceRegistry as mandatory first pipeline stage; source_candidate → registered_source
approval required before SpecVault ingestion.

---

## Structural Weakness Summary

| ID | Weakness | Root Subsystem Gap |
|----|----------|-------------------|
| SW-01 | No source trust chain | SpecSourceRegistry missing |
| SW-02 | No content addressing | SpecVault absent or shallow |
| SW-03 | No cross-format normalization | SpecNormalizer missing |
| SW-04 | No staleness propagation | SpecGovernanceRuntime unenforced |
| SW-05 | No determinism guarantee | ContextPackBuilder lacks manifest.sha256 |
| SW-06 | No usage tracking | Usage ledger absent |
| SW-07 | No anti-bypass enforcement | SpecGovernanceRuntime absent at streams |
| SW-08 | No regression suite | Test infrastructure missing |
