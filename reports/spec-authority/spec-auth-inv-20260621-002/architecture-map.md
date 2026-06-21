# Specs Authority Layer — Architecture Map
**Run ID:** spec-auth-inv-20260621-002
**Date:** 2026-06-21

---

## 1. Intended Flow (design baseline)

```
Official Spec (PDF/HTML/RFC)
        │
        ▼  [T3 Authorization — 6 conditions; Babar Raza approval]
  acquire_spec.py ──► .local/spec-cache/<format>/<version>/
        │                     │
        │              spec-index.yaml (SHA-256 + provenance + legal_category)
        │
        ▼  [Hash verification before normalization]
  normalize_pdf.py ──► text.txt (plain text extraction)
        │
        ▼
  build_section_index.py ──► sections.jsonl (deterministic section IDs)
  build_chunk_index.py   ──► chunks.jsonl   (stable chunk IDs + SHA)
  build_citation_map.py  ──► citations.yaml (chunk→section mapping)
        │
        ▼  [Lexical search — TF-based, ranked, explainable]
  query_normalized_spec.py ──► spec excerpts with page/section/SHA citation
        │
        ▼  [Fact extraction with source_id → requirement_extractor]
  run_extraction_pipeline.py ──► CandidateRequirements (source_id, section, text_fragment)
        │
        ▼  [Anti-bypass verification]
  spec_verifier.py ──► VerifiedFacts (VERIFIED | UNVERIFIABLE | ANTI_BYPASS_REJECTED)
        │
        ▼  [Workbench storage with full provenance]
  workbench/verified-facts-review.yaml
        │                 ├── claim_id, claim, section, spec_sha256
        │                 ├── extraction_method, page_start, verification_evidence
        │                 └── validated_by, validated_at
        │
        ▼  [SAL aggregation]
  sal_master_runner.py ──► .local/spec-cache/sal-facts-latest.json
        │                   (facts WITH source_id, sha256, section citation)
        │
        ▼  [Governance enforcement]
  autonomous_cycle.py ──► governance_validators.py (V13, V19, V37, V47)
        │
        ▼  [Acquisition/Product integration]
  Declaration spec_fact_refs ──► TC-GUARD-001 ──► Product taskcards
  Source code `# FACT-FODS-001` comments ──► traceability
  Tests cite spec sections ──► Gate evidence
```

---

## 2. Actual Discovered Flow (as of 2026-06-21)

```
Official Spec (PDF/HTML/RFC)
        │
        ▼  [T3 Authorization — COMPLETED for FODS (2026-05-04), ZST]
  acquire_spec.py ──► .local/spec-cache/fods/1.3/
        │             └── spec-index.yaml (sha256: 92cfe64…, VERIFIED)
        │
        │  ⚠ NOT DONE for: CSV, DIF, GNUMERIC, ABW, FODP, FODG, ODS, ODT
        │     (sources.jsonl sha256_snapshot=null for these)
        │
        ▼  [Normalization — COMPLETED for FODS only at this scale]
  normalize_pdf.py ──► .local/spec-cache/fods/1.3/normalized/text.txt
        │              (2.2MB, 57,803 lines, sha256 verified)
        │
        ▼  [Section/Chunk indexing — COMPLETED for FODS]
  sections.jsonl, chunks.jsonl, citations.yaml, pages.jsonl
        │
        ▼  [Fact extraction — TWO PATHS EXIST]
        │
        ├─── Path A: Hand-curated (78 FACT-FODS-001 to FACT-FODS-078)
        │     verification_evidence = exact spec text line citations
        │     validated_by = independent_agent_verifier
        │     confidence = high
        │     extraction_method = tier1_section
        │     ✓ STRONG PROVENANCE
        │
        └─── Path B: Automated extraction (4,913 FACT-FODS-EX-*)
              extraction_method = automated_extraction / xml_element_scan
              spec_id = fods-normalized (not original PDF)
              validated_by = deterministic_spec_text_se[arch]
              ⚠ WEAKER PROVENANCE — derived from normalized text, not PDF

        │
        ▼  [Anti-bypass verification — spec_verifier.py]
        │  NOT CALLED in sal_master_runner.py (called only in tests)
        │  ⚠ WIRED IN TESTS ONLY — production pipeline skips verifier
        │
        ▼  [sal_master_runner.py — ACTUAL LOGIC]
        │
        │  if from_cache_only mode:
        │    load workbench facts → emit FACT-<FORMAT>-* QNames
        │  else:
        │    load hardcoded _SPEC_FACT_TEMPLATES (OASIS/IETF/DEFAULT families)
        │    + load workbench facts (additive merge)
        │
        ▼  [Output — TWO CONFLICTING PATHS]
        │
        ├─── .local/spec-cache/sal-facts-latest.json  ← V47 uses this (CORRECT)
        │     22 formats, 14,284 facts (generated 2026-06-21T14:44)
        │
        └─── .local/sal-output/sal-facts-latest.json  ← V37 uses this (DEGRADED)
              1 format, 94 facts (test run overwrote at 2026-06-21T21:16)
              ⚠ CRITICAL GAP: split-brain between V37 and V47

        │
        ▼  [Supervisor Step 0a: SAL regeneration check]
  autonomous_cycle.py checks .local/sal-output/sal-facts-latest.json age
        ├── if > 7 days stale OR missing → runs sal_master_runner.py --all
        └── Output: .local/sal-output/ (per-format + latest)
              ⚠ RACE: if test runs --format zst, latest is overwritten

        │
        ▼  [Governance validators — WIRED AND ACTIVE]
  V13: spec_fact_refs required on PRODUCT_SOURCE items (BLOCKING)
  V47: spec_fact_refs must exist in .local/spec-cache/sal-facts-latest.json (BLOCKING)
  V37: ODF items need SAL trace (WARN-ONLY)

        │
        ▼  [Source code — PARTIAL TRACEABILITY]
  src/python/fods/constants.py: # FACT-FODS-001
  src/python/fods/neutral_model.py: FACT-FODS-001 (multiple references)
  src/python/fods/Compat/fods_*.py: spec_fact_ref = "FACT-FODS-001/004/006"
  src/python/fods/fods/spec/spreadsheet/*.py: spec_fact_ref fields
        │
        │  ⚠ NO BIDIRECTIONAL LINKER — comments are not validated by any tool
        │    test_gap_int_002 tests FODS/FODT/ZST but FAILS for PBM
        │
        ▼  [Proof graph — DESIGNED, NOT INSTANTIATED]
  tools/requirements_authority/graph_store.py  ← implementation exists
  .local/capability-proof-graph/               ← DOES NOT EXIST
```

---

## 3. Authority Entry Points

| Entry Point | Mechanism | Strength |
|-------------|-----------|----------|
| T3 Authorization for spec download | 6-condition check; human approval | STRONG — enforced policy |
| SHA-256 source hash in spec-index.yaml | Computed at download time | STRONG — immutable |
| Workbench verified-facts-review.yaml | 78 hand-curated facts with line citations | STRONG for 78 facts |
| Auto-extracted EX facts | xml_element_scan against normalized text | MODERATE — deterministic but indirect |
| V47 governance validator | Blocks sprint if spec_fact_refs not in SAL | STRONG for ODF in declarations |
| V13 governance validator | Requires spec_fact_refs on PRODUCT_SOURCE | STRONG |
| Source code FACT-* comments | Manual discipline; no automated enforcement | WEAK — advisory only |
| acquisition-packs verified-facts.yaml | 20 hand-specified facts with spec_citation | MODERATE — not auto-linked to SAL |

---

## 4. Authority Bypass Points (Where Authority Can Be Bypassed)

| Bypass Point | Mechanism | Risk |
|-------------|-----------|------|
| sal_master_runner.py skips spec_verifier.py | spec_verifier is not called in production path | MEDIUM — verifier works but is unused |
| spec_parser/indexer/extractor not called by runner | SAL runner loads pre-built workbench; doesn't re-run extraction | LOW currently (workbench is source-backed) |
| `.local/sal-output/sal-facts-latest.json` overwrite | Any `--format X` run overwrites the all-format file | HIGH — operational gap causing test failures |
| V37 is WARN-only (not blocking) | Non-ODF formats can proceed without SAL trace | MEDIUM |
| source code comments not mechanically validated | No tool parses `# FACT-*` and verifies in SAL | MEDIUM |
| acquisition-packs verified-facts.yaml not linked to SAL | Two parallel fact systems; no cross-validation | MEDIUM |
| `spec_fact_refs: ABW-FOSS-LOAD-001` non-standard prefix | V47 only looks for FACT-* pattern | LOW-MEDIUM |

---

## 5. AI/Embeddings Position in Architecture

```
CURRENT STATE (2026-06-21):

  AI platform (tools/ai/) is DESIGNED and IMPLEMENTED but NOT ACTIVATED

  ┌─────────────────────────────────────────────────────────────┐
  │  tools/ai/retrieval/lexical_retriever.py                    │
  │  (TF-based, ranked, explainable) ──► callable but not in   │
  │  main acquisition workflow                                  │
  ├─────────────────────────────────────────────────────────────┤
  │  tools/ai/retrieval/namespace_manager.py                    │
  │  (vector store design: format-segregated, chunk-hash        │
  │  invalidation, model-fingerprint tracking)                  │
  │  ──► .local/ai/ DOES NOT EXIST                              │
  ├─────────────────────────────────────────────────────────────┤
  │  tools/ai/validators/authority_lifecycle.py                 │
  │  (12-state machine: ai_draft → authoritative_after_gate)    │
  │  ──► NOT wired to product workflow                          │
  └─────────────────────────────────────────────────────────────┘

POLICY (from AGENTS.md, GOVERNANCE.md):
  - AI is authorized for candidate fact extraction, summarization,
    requirement drafting — NEVER as final authority
  - Embeddings: TC-0015 evaluation must complete before TC-0016
    implementation; human approval required
  - Vector search evidence excluded from Gate evidence until TC-0016 verified
  - AI output must flow through 12-state lifecycle to reach "authoritative"
```

---

## 6. Missing Flows

| Flow | Required By | Missing Element | Impact |
|------|------------|----------------|--------|
| Automated staleness detection | Design baseline #7 | `refresh_check.py` not called by supervisor | Stale specs not detected automatically |
| spec_verifier in production path | Design baseline #7,12 | `spec_verifier.py` bypassed by sal_master_runner | No anti-bypass protection in production |
| run_extraction_pipeline.py as primary | Design baseline #5,6 | sal_master_runner uses pre-built workbench | Extraction not re-runnable from CI |
| Bidirectional fact-product linker | Design baseline #11 | No `tools/traceability/` | Fact comments are advisory only |
| Proof graph instantiated | Design baseline #15 | `.local/capability-proof-graph/` absent | Traceability matrix not machine-readable |
| Cross-format contamination test | Design baseline #7 | No such test | Format isolation not tested |
| Acquisition planning → SAL gate | Design baseline #15 | Format acquisition can proceed without spec | Most formats have no spec text fetched |
