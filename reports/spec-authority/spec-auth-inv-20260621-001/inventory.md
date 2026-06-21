# Specs Authority Layer — File Inventory
**Run ID:** spec-auth-inv-20260621-001
**Date:** 2026-06-21
**Branch:** main
**HEAD:** 23d1333fdb51b8f07d517a29af311d46ffdd3eb9

---

## Discovery Method
Searched via `git grep`, `find`, `glob`, and direct file inspection for all spec-authority-related material.
Search terms covered: spec_authority, spec authority, cached spec, source hash, provenance, normalized text, chunk index, lexical search, embedding, vector, retrieval, verified fact, acquisition, format spec, authority, stale, invalidation, source version, evidence bundle, proof graph.

---

## Layer 1 — Specification Cache (`tools/spec-cache/`)

| File | Role | Type | Status | Wired |
|------|------|------|--------|-------|
| `tools/spec-cache/acquire_spec.py` | Downloads spec from URL, computes SHA-256, writes spec-index.yaml entry | Tool / executable | AUTHORITATIVE — implements T3 acquisition auth model | YES (via AGENTS.md T1/T6 rules; manual use) |
| `tools/spec-cache/spec_index.py` | Library for reading/writing spec-index.yaml entries | Library | AUTHORITATIVE | YES (imported by acquire_spec.py) |
| `tools/spec-cache/refresh_check.py` | Checks whether cached spec index entries are stale | Tool | AUTHORITATIVE | PARTIAL (manual use only; no automated trigger) |
| `tools/spec-cache/_readme.md` | Policy README for spec-cache tools | Docs | ADVISORY | N/A |
| `.local/spec-cache/<format>/<version>/spec-index.yaml` | Per-format provenance metadata (SHA-256, URL, legal, stale flag) | Data — local-only | AUTHORITATIVE (immutable per policy) | PARTIAL |
| `.local/spec-cache/fods/1.3/` | Only format with actual sha256_snapshot in registry | Data — local-only | ACTIVE | YES |
| `.local/spec-cache/fodt/odf-1.3/workbench/` | FODT workbench with 27 verified facts | Data — local-only | ACTIVE | YES |
| `.local/spec-cache/zst/rfc8878/workbench/` | ZST workbench with 15 verified facts | Data — local-only | ACTIVE | YES |

---

## Layer 2 — Spec Normalization (`tools/spec-normalize/`)

| File | Role | Type | Status | Wired |
|------|------|------|--------|-------|
| `tools/spec-normalize/normalize_pdf.py` | Converts cached PDF to plain text | Tool | AUTHORITATIVE | PARTIAL (manual/one-time use) |
| `tools/spec-normalize/build_section_index.py` | Builds section index from normalized text | Tool | AUTHORITATIVE | PARTIAL |
| `tools/spec-normalize/build_chunk_index.py` | Segments normalized text into searchable chunks | Tool | AUTHORITATIVE | PARTIAL |
| `tools/spec-normalize/build_citation_map.py` | Builds citation map linking chunks to sections | Tool | AUTHORITATIVE | PARTIAL |
| `tools/spec-normalize/build_spec_workbench.py` | One-shot workbench builder (calls normalize→index→chunk→cite) | Tool | AUTHORITATIVE | PARTIAL |
| `tools/spec-normalize/query_normalized_spec.py` | Queries normalized spec by section/element/keyword | Tool | AUTHORITATIVE | PARTIAL (manual use) |
| `tools/spec-normalize/validate_normalized_spec.py` | Validates normalized spec artifacts for consistency | Tool | AUTHORITATIVE | PARTIAL |
| `tools/spec-normalize/refresh_workbench.py` | Refreshes workbench when source hash changes | Tool | AUTHORITATIVE | NOT WIRED (no automated trigger) |
| `tools/spec-normalize/detect_coverage_gaps.py` | Detects sections without requirements mapped | Tool | AUTHORITATIVE | NOT WIRED |
| `tools/spec-normalize/export_sample_requirements.py` | Exports sample requirements from workbench | Tool | AUTHORITATIVE | NOT WIRED |
| `tools/spec-normalize/build_requirement_pack.py` | Builds requirement packs for specific tasks | Tool | AUTHORITATIVE | NOT WIRED |
| `tools/spec-normalize/validate_requirement_pack.py` | Validates requirement packs | Tool | AUTHORITATIVE | NOT WIRED |
| `tools/spec-normalize/export_task_packet.py` | Exports task-specific requirement packet | Tool | AUTHORITATIVE | NOT WIRED |
| `tools/spec-normalize/requirements.txt` | Python deps for normalization (pdfminer, etc.) | Deps | AUTHORITATIVE | N/A |
| `tools/spec-normalize/_readme.md` | README for normalization tools | Docs | ADVISORY | N/A |

---

## Layer 3 — Specification Authority Layer (`tools/specification-authority-layer/`)

| File | Role | Type | Status | Wired |
|------|------|------|--------|-------|
| `tools/specification-authority-layer/sal_master_runner.py` | Main SAL orchestrator — produces spec-facts per format | Tool / executable | **CRITICAL GAP** — Uses HARDCODED fact templates, not parsed specs. Facts have no source_id. | YES (triggered by autonomous_cycle.py step 0a) |
| `tools/specification-authority-layer/spec_source_registry.py` | Manages canonical source list with status lifecycle | Library | AUTHORITATIVE (schema sound) | PARTIAL (10 sources, 9 without sha256) |
| `tools/specification-authority-layer/spec_parser.py` | Parses spec text into sections | Library | AUTHORITATIVE | UNUSED in master runner |
| `tools/specification-authority-layer/spec_indexer.py` | Indexes parsed spec into section lookup | Library | AUTHORITATIVE | UNUSED in master runner |
| `tools/specification-authority-layer/spec_normalizer.py` | Normalizes parsed sections | Library | AUTHORITATIVE | UNUSED in master runner |
| `tools/specification-authority-layer/spec_digestor.py` | Computes spec digest (hash of content) | Library | AUTHORITATIVE | UNUSED in master runner |
| `tools/specification-authority-layer/spec_verifier.py` | Anti-bypass: rejects facts with no source_id or unregistered sources | Library | AUTHORITATIVE | NOT CALLED by master runner |
| `tools/specification-authority-layer/requirement_extractor.py` | Extracts candidate requirements from spec sections | Library | AUTHORITATIVE | NOT CALLED by master runner |
| `tools/specification-authority-layer/requirement_graph.py` | Builds requirement dependency graph | Library | AUTHORITATIVE | NOT CALLED |
| `tools/specification-authority-layer/spec_vault_ingest.py` | Ingests spec into vault with provenance | Tool | AUTHORITATIVE | NOT CALLED |
| `tools/specification-authority-layer/spec_governance_runtime.py` | Runtime governance checks for spec ops | Library | AUTHORITATIVE | NOT CALLED |
| `tools/specification-authority-layer/fact_coverage_report.py` | Reports fact coverage vs. registered facts | Tool | AUTHORITATIVE | PARTIAL (manual) |
| `tools/specification-authority-layer/extractor_to_workbench_adapter.py` | Adapts extracted facts to workbench format | Tool | AUTHORITATIVE | NOT CALLED |
| `tools/specification-authority-layer/context_pack_builder.py` | Builds deterministic context packs with manifest SHA | Tool | AUTHORITATIVE | NOT WIRED (sample output only) |
| `tools/specification-authority-layer/run_extraction_pipeline.py` | Runs full extraction pipeline | Tool | AUTHORITATIVE | NOT WIRED (manual only) |
| `tools/specification-authority-layer/run_fact_verification.py` | Text-search-based fact verification against cached spec | Tool | AUTHORITATIVE | PARTIAL (manual + some automation) |
| `tools/specification-authority-layer/migrate_sources_jsonl.py` | Migrates sources.jsonl format | Tool | HOUSEKEEPING | USED ONCE |
| `tools/specification-authority-layer/spec_census.py` | Census of all formats and spec state | Tool | ADVISORY | PARTIAL |
| `.local/spec-source-registry/sources.jsonl` | Persistent source registry (10 entries) | Data — local-only | AUTHORITATIVE | PARTIAL |
| `.local/sal-output/sal-facts-latest.json` | Latest generated spec facts | Data — local-only | **DEGRADED** — facts have no source_id | YES (consumed by capability_compiler.py) |
| `.local/sal-output/fact-coverage-report.json` | Coverage per format | Report | ADVISORY | PARTIAL |

---

## Layer 4 — AI/Embeddings (`tools/ai/`)

| File | Role | Type | Status | Wired |
|------|------|------|--------|-------|
| `tools/ai/validators/authority_lifecycle.py` | Enforces ai_draft→schema_validated→source_cited→...→authoritative state machine | Validator | AUTHORITATIVE | YES (tests pass; not yet wired to product pipeline) |
| `tools/ai/validators/runtime_guard.py` | Blocks forbidden AI patterns (hallucination, ungrounded claims) | Validator | AUTHORITATIVE | PARTIAL |
| `tools/ai/validators/schema_validator.py` | Validates AI output against JSON schema | Validator | AUTHORITATIVE | PARTIAL |
| `tools/ai/validators/risk_controls.py` | Risk control checks for AI operations | Validator | AUTHORITATIVE | PARTIAL |
| `tools/ai/retrieval/lexical_retriever.py` | TF-based lexical scoring retriever | Tool | AUTHORITATIVE | PARTIAL |
| `tools/ai/retrieval/namespace_manager.py` | Vector store namespace manager (STUB — requires LanceDB, not authorized) | Stub | NOT IMPLEMENTED | NO |
| `tools/ai/schemas/models.py` | AI role, authority lifecycle, and model schemas | Schema | AUTHORITATIVE | YES |
| `tools/ai/control_plane/model_discovery.py` | Discovers available AI models | Tool | AUTHORITATIVE | PARTIAL |
| `tools/ai/control_plane/model_router.py` | Routes to appropriate AI model per role | Tool | AUTHORITATIVE | PARTIAL |
| `tools/ai/agentic/scoped_runner.py` | Scoped agentic runner for AI tasks | Tool | AUTHORITATIVE | NOT WIRED to SAL |
| `tools/ai/contracts/forbidden-runtime-imports.yaml` | Explicitly forbids qdrant, chromadb, pinecone | Contract | AUTHORITATIVE | YES (referenced by governance) |
| `tools/ai/contracts/roles.yaml` | Defines AI roles and capabilities | Contract | AUTHORITATIVE | YES |
| `tools/supervisor/embedding_retrieval.py` | Advisory-only lexical/embedding retrieval over prior evidences | Tool | ADVISORY_ONLY | PARTIAL (supervisor advisory use) |

---

## Layer 5 — Governance and Policy Docs

| File | Role | Type | Status | Wired |
|------|------|------|--------|-------|
| `AGENTS.md` §T1–T6, §W1–W5, §X1–X6 | Spec cache, normalization, provenance, anti-bypass rules | Policy | AUTHORITATIVE | ADVISORY (not enforced by code) |
| `GOVERNANCE.md` §16, §17, §22.3 | Spec artifact handling, provenance, LLM not authority | Policy | AUTHORITATIVE | ADVISORY |
| `docs/specification-cache.md` | Full spec cache policy, T3 auth model, storage rules | Policy | AUTHORITATIVE | ADVISORY |
| `docs/spec-retrieval-strategy.md` | Three-tier retrieval hierarchy (deterministic→lexical→vector) | Policy | PROPOSED — status "Proposed, awaiting human review" | ADVISORY |
| `docs/spec-consumption-workbench.md` | Spec consumption workbench design | Design | AUTHORITATIVE | ADVISORY |

---

## Layer 6 — Tests

| File | Role | Type | Status | Pass/Fail |
|------|------|------|--------|-----------|
| `tests/ai/test_authority_lifecycle.py` | Tests AI artifact authority state machine | Unit | ACTIVE | 7/7 PASS |
| `tests/ai/test_r27_authority_lifecycle_integration.py` | Integration test for authority lifecycle | Integration | ACTIVE | PASS |
| `tests/capability_layer/test_sal_capability_wiring.py` | Tests SAL facts loading into capability compiler | Unit | ACTIVE | 6/6 PASS |
| `tests/python/fods/test_r169_sal_product_advancement.py` | FODS SAL product advancement tests | Integration | ACTIVE | PASS |
| `tests/python/dogfood/test_dogfood_fods_fodt_sal_fact_ndjson_export.py` | SAL facts dogfood/export tests | Integration | ACTIVE | 6/25 FAIL (JSON decode on format-specific files) |
| `tests/python/deepening/test_r1221_fods_spec_parity_deepening.py` | FODS spec parity deepening | Deepening | ACTIVE | UNKNOWN |
| `tests/python/deepening/test_r1222_fodt_spec_parity_deepening.py` | FODT spec parity deepening | Deepening | ACTIVE | UNKNOWN |
| `tests/python/fodt/test_spec_qname_stubs.py` | FODT QName spec stubs | Unit | ACTIVE | UNKNOWN |
| `tests/specification-authority-layer/test_sal_qname_prefix_correctness.py` | QName prefix correctness | Unit | ACTIVE | UNKNOWN |

---

## Layer 7 — Acquisition Packs (consumers of spec authority)

| File | Role | Type | Status | Wired |
|------|------|------|--------|-------|
| `acquisition-packs/_template/spec-evidence.md` | Template for spec evidence artifact | Template | AUTHORITATIVE | YES |
| `acquisition-packs/fods/spec-evidence.md` | FODS spec evidence artifact | Evidence | AUTHORITATIVE | YES |
| `acquisition-packs/fodt/spec-evidence.md` | FODT spec evidence artifact | Evidence | AUTHORITATIVE | YES |
| `acquisition-packs/_families/odf-flat/playbook.yaml` | ODF flat family playbook with provenance gates | Playbook | AUTHORITATIVE | YES |

---

## Layer 8 — Product Source (spec fact references)

| File | Role | Evidence | Wired |
|------|------|----------|-------|
| `src/python/fods/neutral_model.py` | References FACT-FODS-001–007 in docstrings | COMMENT only | PARTIAL (no enforcement) |
| `src/python/fods/constants.py` | Inline FACT-FODS-001 references on constants | COMMENT only | PARTIAL |
| `src/python/fodt/neutral_model.py` | References FACT-FODT-001 | COMMENT only | PARTIAL |
| `src/python/abw/abw_codec.py` | spec_fact_refs: ABW-FOSS-LOAD-001 in docstring | COMMENT only | PARTIAL |
| `src/python/zst/zst_codec.py` | spec_fact_refs: FACT-ZST-001 in comments | COMMENT only | PARTIAL |
| `src/python/fodg/fodg_analytics.py` | FACT-FODG-EX-0001–0004 in docstrings | COMMENT only | PARTIAL |

---

## Missing/Expected-But-Not-Found Files

| Expected File | Status | Impact |
|---------------|--------|--------|
| `.local/spec-cache/<format>/*/spec.pdf` for all formats | Only FODS confirmed sha256 | Cannot run text verification on most formats |
| `tools/spec-normalize/build_vector_index.py` | NOT PRESENT (planned only) | No vector indexing capability |
| `tests/specification-authority-layer/test_source_id_required.py` | NOT PRESENT | No enforcement that facts carry source_id |
| `tests/specification-authority-layer/test_stale_hash_detection.py` | NOT PRESENT | No test for cache staleness detection |
| `tests/specification-authority-layer/test_spec_to_product_traceability.py` | NOT PRESENT | No end-to-end traceability proof |
| `.local/sal-output/sal-facts-fods.json` (format-specific) | EMPTY/MISSING | Dogfood tests fail with JSONDecodeError |
| `.local/sal-output/sal-facts-fodt.json` (format-specific) | EMPTY/MISSING | Dogfood tests fail |
