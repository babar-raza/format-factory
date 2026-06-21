# Spec Authority Machinery — Executive Diagnosis

**Run ID:** `spec-authority-machinery-explosion-20260621-827f5a52`
**Plan target HEAD:** `827f5a52`
**Execution HEAD:** `ed51041f` (4 commits ahead; same sprint context)
**Branch:** main
**Investigation date:** 2026-06-21
**Scope:** End-to-end spec authority chain for all registered formats

---

## System Summary

Since the initial investigation plan was drafted, significant improvements have landed:

| Improvement | Status |
|-------------|--------|
| SAL idempotency fix — `from_cache_only=True` emits only workbench-verified facts | DONE (commit `827f5a52`) |
| TC-GUARD-001 — BLOCK mode; `gap_ledger_ref OR spec_fact_refs` required on PRODUCT_SOURCE | DONE (commit `83f062cf`) |
| FODS spec stubs — `src/python/fods/spec/` 12 architecture-only classes with `spec_fact_ref` | DONE (commit `8ca43a12`) |
| QName registry — `shared/qname-registry/fods.yaml` 12 QName→fact→canonical_class mappings | DONE |
| V45 validator — blocks format-prefixed class names outside Compat/ | DONE (commit `827f5a52`) |
| V46 validator — warns on PRODUCT_SOURCE items without skill_transcript | DONE (WARN-only) |
| V47 validator — `spec_fact_refs` field enforcement | DONE (commit `3024f68c`) |
| FODS/FODT Compat facades | DONE (commit `3024f68c`) |
| ABW/Gnumeric gap-ledger spec_facts cleaned (empty, not stale magic IDs) | DONE |

---

## Overall Ratings (as of 2026-06-21, HEAD ed51041f)

### Layer Existence: STRONG

- 19-20 SAL modules active
- 14,284+ total SAL facts across registered formats
- FODS: 4,987 workbench-verified + ~22 bootstrap-only template facts
- FODT: 4,933 workbench-verified; ZST: 94 workbench-verified
- FODP/FODG/ODS/ODT: 1,066 each workbench-verified
- 12 FODS spec stubs with `spec_fact_ref` on each class
- 12 QNames in `fods.yaml` registry with full chain: QName → fact → canonical class → Python/C# file

### Layer Correctness: MODERATE

**Correct:**
- `source: "workbench_verified"` field present on each workbench fact
- FODS workbench facts are deterministic (verified via test_sal_runner_idempotency.py)
- Stale magic IDs (ABW-FACT-MAGIC, GNUMERIC-FACT-MAGIC) have been cleaned from gap-ledger
- FODS spec stubs correctly reference `FACT-FODS-006` which EXISTS in SAL output

**Incorrect:**
- SAL daily output (`sal-facts-latest.json`) is still in DEFAULT mode (not `from_cache_only=True`): FODS has 5,009 total facts including ~22 bootstrap-only template facts. The "idempotency fix" controls `from_cache_only=True` path only; the default pipeline still mixes template and workbench facts.
- CSV gap-ledger entries (58 gaps) reference FACT-CSV-001 and FACT-CSV-002, which do NOT exist in current SAL output (CSV has 0 SAL facts). These are stale references (116 total stale refs).
- `authority_level` field absent from gap-ledger: 0/958 entries have this field.

### Pipeline Integration: MODERATE

- TC-GUARD-001: REAL BLOCK — requires `gap_ledger_ref` OR `spec_fact_refs` on PRODUCT_SOURCE items
- V47 validator: enforces `spec_fact_refs` field on declared items
- GAP-INT-002: scans ALL Python source for FACT-* refs; verifies all cited facts exist in SAL. Implicit improvement (workbench facts loaded into SAL index). BUT: no explicit `source == workbench_verified` check.
- Healing gate: ADVISORY — Lane 1 checks `fods_facts_gte_10` and `fodt_facts_gte_10` (counts SAL module-level facts, not workbench count per format). Passes even if Gnumeric/ABW have 0 facts.
- SAL pipeline: NOT READ by autonomous_cycle. Still parallel/advisory output.
- Action queue: `action_queue_not_advisory: False` — still advisory.

### Enforcement: MODERATE

- TC-GUARD-001 BLOCK: REAL enforcement. Cannot declare PRODUCT_SOURCE without gap reference or spec_fact_refs.
- V45 BLOCK: Prevents format-prefixed class names outside Compat/. Real enforcement.
- V47 BLOCK (newly added): Enforces spec_fact_refs field.
- V46 WARN-ONLY: skill_transcript requirement is advisory; not blocking.
- GAP-INT-002: implicitly stronger (workbench-only SAL if from_cache_only used), but no explicit authority check.

### Repeatability: WEAK

- V46 requires skill_transcript going forward; legacy items and most current items lack transcripts.
- No governed skills for spec acquisition chain for non-FODS formats.
- TC-0021 review of FODS req-packs: pending. Traceability from req-pack entries to SAL fact IDs is unverified.
- Workbench expansion to non-FODS formats (FODP/FODG/ODS/ODT have 1,066 workbench facts each) is recent; acquisition chain for those formats is undocumented.

### AI/Embedding: CORRECTLY ISOLATED

- No LLM in extraction pipeline; deterministic text search methods
- Embedding is advisory-only (not gate)
- No AI contamination in workbench facts (9,974 deterministic_spec_text_search + 16 independent_agent_verifier methods documented)

---

## Proof Levels by Format

| Format | SAL Facts | Source Type | Proof Level | Notes |
|--------|-----------|-------------|-------------|-------|
| FODS | 4,987 wb + ~22 bootstrap | workbench_verified | **P5** | Spec stubs + QName registry + 4,987 wb facts + req-packs. Chain: spec→fact→stub→qname→product. |
| FODT | 4,933 | workbench_verified | **P4** | Spec stubs added (GAP-ARCH-005); no separate QName registry. |
| ZST | 94 | workbench_verified | **P4** | Workbench facts; req-graph in spec-artifacts; code+tests. |
| FODP/FODG/ODS/ODT | 1,066 each | workbench_verified | **P3-P4** | Large workbench fact counts, but no spec stubs or QName registry. |
| DIF/NETPBM | 2-present | workbench_verified | **P3** | Spec artifacts normalized; candidate reqs; code+tests exist. |
| Gnumeric | 0 | NONE | **P2** | Code+tests exist; 0 SAL facts; gap entries have empty spec_facts. |
| ABW | 0 | NONE | **P1** | Code+tests exist; DTD unreachable (ECONNREFUSED); 0 SAL facts; gap entries have empty spec_facts. |
| CSV | 0 | NONE | **P2** | Code+tests exist; 0 SAL facts; gap entries reference stale FACT-CSV-001/002. |
| TSV/SYLK/DIF/NDJSON/TOML | 0 | NONE | **P1-P2** | Code/tests exist; no spec-sourced facts. |

---

## Residual False-Confidence Mechanism (updated)

**Original mechanism (RESOLVED):** Template facts in SAL output were cited by GAP-INT-002, creating the appearance of spec-backed coverage for formats with no real workbench data. The SAL idempotency fix resolved this for the `from_cache_only=True` code path.

**Remaining mechanism (ACTIVE — lower severity):**

1. **SAL default mode still mixes template + workbench facts.** `sal-facts-latest.json` is generated in default mode. FODS has ~22 bootstrap-only template facts alongside 4,987 workbench facts. GAP-INT-002's `test_total_fact_refs_across_product_source` checks all cited FACT-* refs against the SAL index — this index includes template facts, so a product source citing a template-only fact ID would pass the test even if that fact has no workbench verification.

2. **CSV gap-ledger stale refs.** 58 CSV gap entries cite FACT-CSV-001 and FACT-CSV-002, which do not exist in SAL output (CSV has 0 workbench facts). TC-GUARD-001 accepts items citing these gaps — gap appears spec-backed but fact IDs are dead references.

3. **Healing gate depth gap.** Lane 1 checks `fods_facts_gte_10` — passes even if those 10 facts are all bootstrap-only. Does not verify `workbench_verified_fact_count > 0`.

4. **No authority_level in gap-ledger.** TC-GUARD-001 checks `gap_ledger_ref` presence only. A PRODUCT_SOURCE citing a CSV gap (with stale fact refs and 0 SAL workbench facts) satisfies TC-GUARD-001.

---

## Summary of Genuine Unresolved Issues

| Priority | Issue | Severity |
|----------|-------|---------|
| HIGH | SAL daily output in default mode; template facts still present alongside workbench | HIGH |
| HIGH | GAP-INT-002 has no explicit `source == workbench_verified` check | HIGH |
| HIGH | autonomous_cycle.py does NOT read SAL output | HIGH |
| HIGH | CSV gap-ledger stale FACT-CSV-001/002 refs (116 stale refs, 58 gaps) | MEDIUM-HIGH |
| MEDIUM | `authority_level` absent from gap-ledger (0/958 entries) | MEDIUM |
| MEDIUM | Healing gate Lane 1 checks `fods_facts_gte_10` not `workbench_verified_fact_count > 0` | MEDIUM |
| MEDIUM | V46 is WARN-only; legacy PRODUCT_SOURCE items lack skill_transcript | MEDIUM |
| MEDIUM | TC-0021 FODS req-pack traceability review: pending | MEDIUM |
| LOW | FODP/FODG/ODS/ODT: 1,066 workbench facts each — acquisition chain undocumented | LOW |
| LOW | Gate 11 criterion name: `min_spec_facts_cited` (should be `min_workbench_verified_facts_cited`) | LOW |
