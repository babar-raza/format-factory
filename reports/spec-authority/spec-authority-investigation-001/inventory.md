# Specs Authority Layer — Inventory
# Sprint: SPEC-AUTHORITY-LAYER-PRODUCTION-INVESTIGATION-001
# Generated: 2026-06-06
# Branch: main | HEAD: f76d845bd3b1d61d53619fadd0f5a34a1832c8d1

---

## Summary

The specs authority layer exists as **real implemented code**, not only prose.
However, it is **partially deployed**: only FODS has full normalization; other
formats have spec-index.yaml metadata only. Integration into the acquisition
and product workflow is **advisory** rather than enforced.

---

## Category A — Policy / Governance Documents

| File | Role | Authority Status | In Workflow |
|------|------|-----------------|-------------|
| docs/specification-cache.md | Spec cache policy, T3 authorization model, index schema | Authoritative policy | YES — referenced by tools |
| docs/specification-normalization.md | Normalization pipeline design | Authoritative design doc | PARTIAL — tools exist |
| docs/spec-retrieval-strategy.md | Three-tier retrieval hierarchy (deterministic → lexical → vector) | Authoritative design | PARTIAL — Tier 3 not implemented |
| docs/spec-retrieval-and-rag-policy.md | RAG guardrails, provenance requirements, embedding policy | Authoritative policy | DESIGN ONLY for Tier 3 |
| docs/llm-and-embedding-strategy.md | LLM and embedding operating model | Policy doc | NOT CONNECTED to spec authority |
| docs/ai-generated-format-requirements-pipeline.md | AI requirements pipeline design | Advisory | Design-only, not implemented |
| docs/format-understanding-layer.md | Format understanding layer design | Advisory | Partial integration |
| docs/ai-usage-operating-model.md | AI operating model | Authoritative policy | Referenced by RAG policy |
| AGENTS.md | Agent rules including §T9 (no spec text to remote endpoints) | Authoritative | ENFORCED via policy |

---

## Category B — Tool Implementations

### B1 — Spec Cache Tools (`tools/spec-cache/`)

| File | Role | Status |
|------|------|--------|
| tools/spec-cache/acquire_spec.py | Downloads spec files; DRY-RUN by default; T3 auth required for live | IMPLEMENTED |
| tools/spec-cache/spec_index.py | Reads/writes spec-index.yaml; provenance library | IMPLEMENTED |
| tools/spec-cache/refresh_check.py | Detects stale cached specs by comparing source hash | IMPLEMENTED |
| tools/spec-cache/_readme.md | Documentation | Advisory |

### B2 — Spec Normalization Tools (`tools/spec-normalize/`)

| File | Role | Status |
|------|------|--------|
| tools/spec-normalize/normalize_pdf.py | Converts PDF to normalized text pages | IMPLEMENTED — not run for most formats |
| tools/spec-normalize/build_section_index.py | Builds section index from normalized text | IMPLEMENTED |
| tools/spec-normalize/build_chunk_index.py | Builds chunk index for retrieval | IMPLEMENTED |
| tools/spec-normalize/build_citation_map.py | Builds citation map (element/section → page) | IMPLEMENTED |
| tools/spec-normalize/build_requirement_pack.py | Builds requirement packs from facts | IMPLEMENTED |
| tools/spec-normalize/build_spec_workbench.py | Orchestrates full normalization pipeline | IMPLEMENTED |
| tools/spec-normalize/export_sample_requirements.py | Exports sample requirements for review | IMPLEMENTED |
| tools/spec-normalize/export_task_packet.py | Exports task packets for acquisition | IMPLEMENTED |
| tools/spec-normalize/query_normalized_spec.py | Queries normalized spec by section/element/page | IMPLEMENTED |
| tools/spec-normalize/validate_normalized_spec.py | Validates normalization output schema | IMPLEMENTED |
| tools/spec-normalize/validate_requirement_pack.py | Validates requirement pack schema | IMPLEMENTED |
| tools/spec-normalize/requirements.txt | Python dependencies | Present |
| tools/spec-normalize/_readme.md | Documentation | Advisory |

### B3 — Specification Authority Layer (`tools/specification-authority-layer/`)

| File | Role | Status |
|------|------|--------|
| spec_source_registry.py | Register/manage spec sources; anti-bypass enforcement | IMPLEMENTED |
| spec_vault_ingest.py | Ingest raw text snapshots; SHA-256 binding | IMPLEMENTED |
| spec_digestor.py | Compute content digest; staleness check | IMPLEMENTED |
| spec_parser.py | Parse spec sections from text fixture | IMPLEMENTED |
| spec_indexer.py | Build section index from parsed spec | IMPLEMENTED |
| spec_normalizer.py | Normalize spec text | IMPLEMENTED |
| requirement_extractor.py | Extract candidate requirements using RFC 2119 keywords | IMPLEMENTED |
| requirement_graph.py | Build requirement graph from candidates | IMPLEMENTED |
| context_pack_builder.py | Build deterministic context packs with SHA-256 manifest | IMPLEMENTED |
| spec_governance_runtime.py | Anti-bypass enforcement; usage ledger | IMPLEMENTED |
| spec_verifier.py | Spec verification utilities | IMPLEMENTED |
| spec_parser.py | Parse spec sources | IMPLEMENTED |

### B4 — Requirements Authority (`tools/requirements_authority/`)

| File | Role | Status |
|------|------|--------|
| models.py | Data models (POC targets, etc.) | IMPLEMENTED |
| graph_store.py | Proof graph store | IMPLEMENTED |
| coverage_evaluator.py | Capability coverage evaluation | IMPLEMENTED |
| overclaim_detector.py | Detects overclaimed capabilities | IMPLEMENTED |
| staleness_invalidator.py | Staleness invalidation engine | IMPLEMENTED |
| poc_readiness.py | POC readiness computation | IMPLEMENTED |
| mainstream_gap_queue.py | Gap queue for mainstream pipeline | IMPLEMENTED |
| supervisor_verdict_packet.py | Supervisor verdict generation | IMPLEMENTED |
| capability_delta.py | Capability delta proposals | IMPLEMENTED |
| coverage_records.py (inferred) | Coverage records management | IMPLEMENTED |
| validators.py | Validation utilities | IMPLEMENTED |
| validate_requirements_authority.py | Top-level validation | IMPLEMENTED |

### B5 — Requirements Validation (`tools/requirements/`)

| File | Role | Status |
|------|------|--------|
| validate_generated_requirements.py | Validates generated requirements YAML; blocks AI-only acceptance | IMPLEMENTED |

### B6 — Supervisor Integration

| File | Role | Status |
|------|------|--------|
| tools/supervisor/authority_integration_fabric.py | Ties spec auth + RCA + tri-lane; generates contract JSON | IMPLEMENTED |
| tools/supervisor/build_proof_graph_iter001.py | Builds proof graph; references spec_auth test node | IMPLEMENTED |

---

## Category C — Local Data / Artifacts

### C1 — Spec Cache (`.local/spec-cache/`)

| Format | Version | Has spec-index.yaml | Has Normalized Output | Has Verified Facts |
|--------|---------|--------------------|-----------------------|-------------------|
| fods | 1.3 | YES (SHA-256: 92cfe6..., 24.27 MB PDF) | YES (partial: citations, page-map, parser-requirements-draft, sample-requirements, source-manifest) | YES (10 facts in verified-facts.yaml) |
| abw | awml-1.0 | YES | NO | NO |
| csv | rfc4180 | YES | NO | NO |
| dif | v1 | YES | NO | NO |
| gnumeric | v10 | YES | NO | NO |
| pbm | netpbm-spec | YES | NO | NO |
| pgm | netpbm-spec | YES | NO | NO |
| tsv | informal | YES | NO | NO |
| zst | rfc8878 + rfc9659 | YES (section-index.yaml present) | NO | NO |

**Critical finding:** Only fods/1.3 has been normalized. All other formats have metadata only.

### C2 — Spec Artifacts (`.local/spec-artifacts/`)

30 files present for: DIF, FODS, FODT, GNUMERIC, NETPBM, ZST, SYLK (5 files each):
- `<FORMAT>-SPEC-001-digest.json`
- `<FORMAT>-SPEC-001-index.json`
- `<FORMAT>-SPEC-001-normalized.json`
- `<FORMAT>-SPEC-001-req-graph.json`
- `<FORMAT>-SPEC-001-requirements.json`

**Critical finding:** These are seed/fixture data generated by `build_proof_graph_iter001.py` with simplified synthetic text (e.g., "Document root SHALL be office:document element."), NOT extracted from actual spec PDFs. Requirements have status "candidate" only.

### C3 — Spec Source Registry (`.local/spec-source-registry/`)

Directory does not exist. Sources.jsonl not present. The registry exists only in-memory during test runs.

### C4 — Spec Normalize Output (`.local/spec-normalize/`)

Directory does not exist. Normalization pipeline has not been run against real spec PDFs for output.

### C5 — Embeddings (`.local/embeddings/`)

Directory does not exist. Not implemented.

### C6 — Usage Ledger (`.local/spec-usage-ledger/`)

Not verified as persisted. The ledger is written by `spec_governance_runtime.py` but persistence depends on runtime execution.

---

## Category D — Tests

| Test Suite | Location | Test Count | Pass Rate | Coverage |
|------------|----------|-----------|-----------|---------|
| spec_authority | tests/spec_authority/ | 163 | 100% | Source registration, citation validation, vault ingest, staleness, context packs, full pipeline (ZST/Netpbm/DIF) |
| specification-authority-layer | tests/specification-authority-layer/ | 28 | 100% | MWP: context pack verify, usage ledger, memory-only claim reject, pilot ZST/Netpbm/DIF |
| requirements | tests/requirements/ | 32 | 100% | Requirements schema validation, AI-proposal blocking, traceability, verifier review |
| requirement_capability_authority | tests/requirement_capability_authority/ | 80 (1 fail) | 99% | RCA layer, proof graph, coverage records, supervisor verdict packet |
| ai (authority lifecycle) | tests/ai/ | ~30 | Unknown | Authority lifecycle, requirements pipeline |
| skills (spec governance) | tests/skills/test_public_spec_governance.py | ~10 | Unknown | Spec governance |
| supervisor authority_integration_fabric | tests/supervisor/test_authority_integration_fabric.py | ~20 | Unknown | Integration fabric |

---

## Category E — Generated Requirements / Evidence (Acquisition Packs)

| Format | Requirements File | Spec-Backed | Verified Facts |
|--------|-----------------|-------------|---------------|
| fods | acquisition-packs/fods/implementation-requirements.yaml | PARTIAL (references spec sections) | YES (workbench verified-facts.yaml) |
| fodt | acquisition-packs/fodt/ | PARTIAL | NO separate verified-facts |
| abw | acquisition-packs/abw/ | NO spec-backed requirements file | NO |
| gnumeric | (not found in acquisition-packs) | NO | NO |
| zst | (zst/gate1-decision-packet exists) | RFC-cited only | NO |
| dif | acquisition-packs/dif/ | NO formal spec-backed requirements | NO |

---

## Category F — Sprint Reports Claiming Spec Authority Progress

| Sprint Report | Claim | Verified |
|---------------|-------|---------|
| reports/spec-authority-real-pilot-r1/ | Spec authority real pilot R1 | EXISTS |
| reports/spec-authority-real-pilot-r2/ | Spec authority real pilot R2 | EXISTS |
| reports/spec-authority-real-pilot-r3/ | Spec authority real pilot R3 closure repair | EXISTS |
| reports/spec-authority-r3-closure-repair/ | R3 closure repair | EXISTS |
| reports/specification-authority-layer-mwp/ | MWP sprint | EXISTS |
| reports/specification-authority-layer-production-healing/ | Production healing | EXISTS |
| reports/requirement-capability-authority-layer-production-healing/ | RCA layer healing | EXISTS |

---

## Missing Expected Items

| Expected Item | Status | Impact |
|---------------|--------|--------|
| `.local/spec-normalize/` directory | MISSING | No normalized text output for retrieval |
| `.local/embeddings/` directory | MISSING | No vector search (by design, not authorized) |
| `.local/spec-source-registry/sources.jsonl` | MISSING | Registry not persisted between runs |
| `.local/spec-usage-ledger/ledger.jsonl` | UNVERIFIED | Audit trail may not persist |
| Verified facts for non-FODS formats | MISSING | Facts are "candidate" only |
| Spec normalization for ABW, ZST, CSV, DIF, GNM, PBM, PGM, TSV | MISSING | Cannot do lexical retrieval |
| Source-backed requirements in parser/writer code | MISSING | Code lacks traceability to spec facts |
| Gate enforcement blocking work without verified facts | MISSING | No hard enforcement point |
