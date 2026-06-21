# Specs Authority Layer — File Inventory
**Run ID:** spec-auth-inv-20260621-002
**Date:** 2026-06-21
**Branch:** main
**HEAD:** 827f5a52915f1ee3b285bf13965b5f65f3532a69
**Investigator:** Production-grade live investigation (fresh, not a replay of -001)

---

## Discovery Method

Live repo search using `git grep`, `Glob`, `Grep`, and direct file inspection.
Search terms: spec_authority, spec authority, cached spec, source hash, provenance,
normalized text, chunk index, lexical search, embedding, vector, verified fact,
acquisition, format spec, spec version, invalidation, authority, stale.

Previous investigation (`spec-auth-inv-20260621-001`) provided baseline findings.
This investigation validates, extends, and corrects those findings with live evidence.

---

## Layer 1 — Specification Cache (`tools/spec-cache/`)

| File | Role | Type | Status | Wired | Notes |
|------|------|------|--------|-------|-------|
| `tools/spec-cache/acquire_spec.py` | Downloads spec from URL under T3 authorization; computes SHA-256; writes spec-index.yaml | Tool | AUTHORITATIVE | PARTIAL — manual invocation only; no auto-trigger | T3 requires 6 conditions before download |
| `tools/spec-cache/spec_index.py` | Library for reading/writing spec-index.yaml entries | Library | AUTHORITATIVE | YES | Imported by acquire_spec.py |
| `tools/spec-cache/refresh_check.py` | Scans .local/spec-cache/ for stale/missing/hash-mismatch entries; exit 1 if stale | Tool | AUTHORITATIVE | NOT WIRED — no automated trigger in supervisor loop | Never re-downloads; requires manual follow-up |
| `tools/spec-cache/_readme.md` | Policy README | Docs | ADVISORY | N/A | |
| `.local/spec-cache/fods/1.3/spec-index.yaml` | FODS provenance: sha256, URL, legal category, download_date | Data (local-only) | AUTHORITATIVE | YES — referenced by workbench | sha256 populated: 92cfe64… |
| `.local/spec-cache/fods/1.3/normalized/text.txt` | Full normalized text of ODF 1.3 Part 3 (2.2MB, 57803 lines) | Data (local-only) | AUTHORITATIVE | YES — used by workbench build and extraction | |
| `.local/spec-cache/fods/1.3/normalized/sections.jsonl` | Section index | Data | AUTHORITATIVE | YES | |
| `.local/spec-cache/fods/1.3/normalized/chunks.jsonl` | Chunk index | Data | AUTHORITATIVE | YES | |
| `.local/spec-cache/fods/1.3/workbench/verified-facts-review.yaml` | 4,991 verified facts (78 hand-curated + 4,913 auto-extracted); 5.2MB | Data (local-only) | AUTHORITATIVE | YES — loaded by sal_master_runner.py | |
| `.local/spec-cache/zst/rfc8878/` | ZST RFC8878 cache | Data (local-only) | AUTHORITATIVE | YES | sha256 populated |
| `.local/spec-cache/zst/rfc9659/` | ZST RFC9659 cache | Data (local-only) | AUTHORITATIVE | YES | sha256 populated |
| `.local/spec-cache/fodt/odf-1.3/` | FODT ODF 1.3 workbench | Data (local-only) | AUTHORITATIVE | YES | |
| `.local/spec-cache/abw/`, `csv/`, `dif/`, `gnumeric/`, etc. | Source dirs for 8+ formats WITHOUT fetched spec text | Data (local-only) | STUB — registered but not fetched | NO | sha256_snapshot=null |
| `.local/spec-source-registry/sources.jsonl` | 10-entry source registry; FODS and ZST have sha256; 8 others null | Data | AUTHORITATIVE (schema) | PARTIAL | |

---

## Layer 2 — Spec Normalization (`tools/spec-normalize/`)

| File | Role | Type | Status | Wired |
|------|------|------|--------|-------|
| `tools/spec-normalize/normalize_pdf.py` | PDF → plain text extraction | Tool | AUTHORITATIVE | PARTIAL — run once for FODS; not automated |
| `tools/spec-normalize/build_section_index.py` | Builds section-index.yaml | Tool | AUTHORITATIVE | PARTIAL |
| `tools/spec-normalize/build_chunk_index.py` | Segments text into chunk-index.jsonl | Tool | AUTHORITATIVE | PARTIAL |
| `tools/spec-normalize/build_citation_map.py` | Citation map linking chunks → sections | Tool | AUTHORITATIVE | PARTIAL |
| `tools/spec-normalize/build_spec_workbench.py` | One-shot pipeline (normalize → index → chunk → cite) | Tool | AUTHORITATIVE | PARTIAL — run manually for FODS, ZST, FODT |
| `tools/spec-normalize/query_normalized_spec.py` | Lexical query against normalized spec | Tool | AUTHORITATIVE | PARTIAL — manual use only |
| `tools/spec-normalize/validate_normalized_spec.py` | Validates normalized artifacts | Tool | AUTHORITATIVE | NOT WIRED |
| `tools/spec-normalize/refresh_workbench.py` | Refreshes workbench when source hash changes | Tool | AUTHORITATIVE | NOT WIRED — no auto-trigger |
| `tools/spec-normalize/detect_coverage_gaps.py` | Detects spec sections without requirement mappings | Tool | AUTHORITATIVE | NOT WIRED |
| `tools/spec-normalize/export_sample_requirements.py` | Exports sample requirements from workbench | Tool | AUTHORITATIVE | NOT WIRED |
| `tools/spec-normalize/build_requirement_pack.py` | Builds task-specific requirement packs | Tool | AUTHORITATIVE | NOT WIRED |
| `tools/spec-normalize/export_task_packet.py` | Exports task-specific requirement packet | Tool | AUTHORITATIVE | NOT WIRED |
| `tools/spec-normalize/validate_requirement_pack.py` | Validates requirement packs | Tool | AUTHORITATIVE | NOT WIRED |

---

## Layer 3 — Specification Authority Layer (`tools/specification-authority-layer/`)

| File | Role | Type | Status | Wired | Notes |
|------|------|------|--------|-------|-------|
| `tools/specification-authority-layer/sal_master_runner.py` | SAL orchestrator — produces spec-facts per format | Tool | ACTIVE | YES (Step 0a of autonomous_cycle.py) | Uses hardcoded templates for formats without workbench; loads workbench for FODS/FODT/ZST/ODF-family. CRITICAL: still has hardcoded `_SPEC_FACT_TEMPLATES` for OASIS/IETF families. |
| `tools/specification-authority-layer/spec_source_registry.py` | Source registry library | Library | AUTHORITATIVE | PARTIAL | |
| `tools/specification-authority-layer/spec_parser.py` | Parses spec text → sections | Library | AUTHORITATIVE | NOT CALLED by sal_master_runner | |
| `tools/specification-authority-layer/spec_indexer.py` | Indexes parsed spec | Library | AUTHORITATIVE | NOT CALLED by sal_master_runner | |
| `tools/specification-authority-layer/spec_normalizer.py` | Normalizes parsed sections | Library | AUTHORITATIVE | NOT CALLED by sal_master_runner | |
| `tools/specification-authority-layer/spec_digestor.py` | Computes spec digest | Library | AUTHORITATIVE | NOT CALLED | |
| `tools/specification-authority-layer/spec_verifier.py` | Anti-bypass: rejects facts with no source_id, unregistered sources, ai_summary-only | Library | AUTHORITATIVE | NOT CALLED by sal_master_runner (but used in tests) | All 14 adversarial tests PASS |
| `tools/specification-authority-layer/requirement_extractor.py` | Extracts candidate requirements from spec sections | Library | AUTHORITATIVE | NOT CALLED by sal_master_runner | |
| `tools/specification-authority-layer/requirement_graph.py` | Builds requirement dependency graph | Library | AUTHORITATIVE | NOT CALLED | |
| `tools/specification-authority-layer/spec_vault_ingest.py` | Ingests spec into vault with provenance | Tool | AUTHORITATIVE | NOT CALLED | |
| `tools/specification-authority-layer/spec_governance_runtime.py` | Runtime governance checks | Library | AUTHORITATIVE | NOT CALLED | |
| `tools/specification-authority-layer/fact_coverage_report.py` | Reports fact coverage | Tool | AUTHORITATIVE | PARTIAL — manual | |
| `tools/specification-authority-layer/run_extraction_pipeline.py` | Full extraction pipeline runner | Tool | AUTHORITATIVE | NOT WIRED to automation | |
| `tools/specification-authority-layer/run_fact_verification.py` | Text-search-based fact verification | Tool | AUTHORITATIVE | PARTIAL — manual | |
| `tools/specification-authority-layer/context_pack_builder.py` | Builds context packs with manifest SHA | Tool | AUTHORITATIVE | NOT WIRED | |
| `tools/specification-authority-layer/qname_src_compliance_reporter.py` | Reports QName-to-source compliance | Tool | AUTHORITATIVE | PARTIAL | |
| `.local/sal-output/sal-facts-latest.json` | **DEGRADED** — currently has only 94 ZST facts (test run overwrote it) | Data (local-only) | DEGRADED | YES — V37 reads this | **CRITICAL PATH BUG**: test ran with `--format zst` and overwrote the all-format file |
| `.local/spec-cache/sal-facts-latest.json` | Full 22-format / 14,284-fact output | Data (local-only) | AUTHORITATIVE | YES — V47 reads this | The governance-authoritative copy |
| `.local/sal-output/sal-facts-20260619.json` | Full 22-format / 14,428-fact output (prior day) | Data (local-only) | ADVISORY | NO | Backup snapshot |

---

## Layer 4 — AI / Embeddings (`tools/ai/`)

| File | Role | Type | Status | Wired |
|------|------|------|--------|-------|
| `tools/ai/retrieval/lexical_retriever.py` | TF-based lexical search (ranked, filtered, explainable; no vector DB) | Library | IMPLEMENTED | PARTIAL — callable from pipeline |
| `tools/ai/retrieval/namespace_manager.py` | Vector store namespace design (format-segregated; stale detection via chunk hash + model fingerprint) | Library | DESIGNED (not instantiated) | NO — `.local/ai/` does not exist |
| `tools/ai/pipeline/e2e_pilot.py` | End-to-end AI pipeline pilot | Tool | IMPLEMENTED | PARTIAL |
| `tools/ai/pipeline/runner.py` | AI pipeline runner | Library | IMPLEMENTED | PARTIAL |
| `tools/ai/synthesis/citation_verifier.py` | Verifies AI-synthesized facts have spec citations | Library | IMPLEMENTED | PARTIAL |
| `tools/ai/synthesis/contradiction_detector.py` | Detects contradictions in AI output | Library | IMPLEMENTED | PARTIAL |
| `tools/ai/validators/authority_lifecycle.py` | 12-state machine: ai_draft → authoritative_after_gate | Library | IMPLEMENTED | NOT WIRED to product workflow |
| `tools/ai/contracts/artifact-authority-states.yaml` | State machine contract (12 states) | Contract | AUTHORITATIVE | YES — enforced by authority_lifecycle.py |
| `tools/ai/run_ai_checks.py` | Standardized AI verification CLI | Tool | IMPLEMENTED | NOT WIRED to main supervisor loop |
| `tools/ai/control_plane/model_router.py` | Model routing (includes embedding support) | Library | IMPLEMENTED | PARTIAL |
| `docs/llm-and-embedding-strategy.md` | AI usage strategy (backlog-only; no LLM calls active) | Docs | ADVISORY | N/A |

---

## Layer 5 — Governance Validators (spec-authority related)

| Validator | Rule ID | Type | blocks_sprint |
|-----------|---------|------|--------------|
| `validate_spec_fact_refs_wired` | V13 | PRODUCT_SOURCE spec_fact_refs enforcement | YES (if violations) |
| `validate_spec_fact_count` | V14 | Min spec_fact count per declaration | WARN-only |
| `validate_min_spec_facts_per_format` | V19 | Per-format minimum | YES |
| `validate_spec_qname_refs` | V26 | QName ref format check | WARN |
| `validate_spec_parity_gate` | V28 | Gate 11 parity criteria | YES |
| `validate_spec_fact_authority_chain` | V37 | ODF PRODUCT_SOURCE → SAL trace | WARN-only |
| `validate_spec_fact_refs_in_sal_output` | V47 | spec_fact_refs must exist in `.local/spec-cache/sal-facts-latest.json` | YES |

---

## Layer 6 — Tests (`tests/specification-authority-layer/`)

| File | Purpose | Result |
|------|---------|--------|
| `test_gap_int_002_product_source_fact_refs.py` | Source→SAL traceability (FODS/FODT/ZST) | 12/13 PASS; 1 FAIL (PBM refs not in overwritten all-format latest) |
| `test_sal_verifier_adversarial.py` | Anti-bypass: paraphrase, negation, stale version, AI summary rejection | 14/14 PASS |
| `test_qname_structure_validator.py` | FODS/FODT QName spec stubs | 6/6 PASS |
| `test_sal_bootstrap_vs_verified.py` | Bootstrap vs workbench-verified distinction | PASS (in 245s run) |
| `test_sal_master_runner.py` | SAL runner output format/structure | PASS |
| `test_sal_from_cache_only.py` | Cache-only mode | TIMED OUT (writes 5MB to disk) |
| `test_sal_runner_from_cache.py` | QName prefix correctness | Pending |
| `test_sal_runner_idempotency.py` | Idempotency | Pending |
| `test_plan_readiness_verdict.py` | Plan readiness check | Pending |
| `test_spec_authority_mwp.py` | Pilot (ZST, Netpbm, DIF) | Pending |
| `test_sal_qname_prefix_correctness.py` | QName prefix format | Pending |
| `test_fodt_qname_spec_chain.py` | FODT QName → spec chain | Pending |
| `test_qname_src_compliance_reporter.py` | QName compliance | Pending |
| Total: 191 tests collected | | |

---

## Layer 7 — Acquisition Packs

| Path | Status | Notes |
|------|--------|-------|
| `acquisition-packs/fods/verified-facts.yaml` | 20 facts, spec_citation present, confidence=deterministic | ACTIVE and spec-cited |
| `acquisition-packs/fods/implementation-requirements.yaml` | Detailed requirements | ACTIVE |
| `acquisition-packs/_template/` | Template with `source_hash: null` placeholder | source_hash NOT auto-populated |
| `acquisition-packs/fodg/`, `fodp/` | parser-notes.md has `source_hash: null` | NOT FILLED |
| `acquisition-packs/_candidate-shortlists/fodt-gate1-human-review-packet.md` | source_hash: null | NOT FILLED |

---

## Layer 8 — Product Source (spec_fact_refs in code)

| Path | Fact IDs cited | In SAL? |
|------|---------------|---------|
| `src/python/fods/constants.py` | FACT-FODS-001 | YES |
| `src/python/fods/neutral_model.py` | FACT-FODS-001 (multiple) | YES |
| `src/python/fods/Compat/fods_cell.py` | FACT-FODS-006 | YES |
| `src/python/fods/Compat/fods_document.py` | FACT-FODS-001 | YES |
| `src/python/fods/Compat/fods_sheet.py` | FACT-FODS-004 | YES |
| `src/python/fods/fods/spec/spreadsheet/*.py` | FACT-FODS-001, 004, 005, 006 | YES |
| `src/python/pbm/pbm_parser.py` | FACT-PBM-001, FACT-PBM-002 | FAIL — not in overwritten latest |
| `src/python/abw/abw_codec.py` | ABW-FOSS-LOAD-001 (non-FACT- prefix) | NOT IN SAL (custom prefix) |

---

## Missing Expected Files (Absence is a Finding)

| Expected | Status | Impact |
|----------|--------|--------|
| `.local/capability-proof-graph/` | DOES NOT EXIST | Proof graph designed but not instantiated |
| `.local/ai/` | DOES NOT EXIST | Vector store not instantiated (correct per policy) |
| `tools/traceability/fact_product_linker.py` | DOES NOT EXIST | No bidirectional FACT-ID→product→test linker |
| Automated staleness gate in supervisor loop | DOES NOT EXIST | `refresh_check.py` never called automatically |
| Cross-format contamination test | DOES NOT EXIST | No test verifies ZST fact doesn't appear in FODS output |
| `run_extraction_pipeline.py` wired to SAL runner | NOT WIRED | spec_parser/indexer/verifier bypassed in main path |
