# Machinery Layer Inventory
**Mission:** MACHINERY-TRUTH-PRODUCT-CONTRACT-20260624
**Generated:** 2026-06-24
**HEAD:** 1852a46d

---

## End-to-End Machinery Map

```
SPECIFICATION
  └─► tools/spec-cache/ (acquire_spec.py, refresh_check.py)
        └─► .local/spec-cache/{format}/ (PDF/HTML specs + spec-index.yaml)

SPECIFICATION NORMALIZATION
  └─► tools/spec-normalize/ (normalize_pdf, build_section_index, build_chunk_index,
                              build_spec_workbench, build_citation_map, etc.)
        └─► .local/spec-cache/{format}/workbench/ (sections.jsonl, chunks.jsonl,
                                                     verified-facts workbench)

AUTHORIZED FACTS (SAL)
  └─► tools/specification-authority-layer/ (sal_master_runner.py, run_spec_pipeline.py,
        spec_parser.py, spec_digestor.py, requirement_extractor.py, requirement_graph.py,
        spec_governance_runtime.py, spec_indexer.py, spec_normalizer.py,
        fact_coverage_report.py, fact_quality.py, migrate_sources_jsonl.py,
        qname_src_compliance_reporter.py, run_extraction_pipeline.py,
        run_fact_verification.py, context_pack_builder.py,
        extractor_to_workbench_adapter.py, spec_census.py)
        └─► .local/spec-cache/sal-facts-latest.json
              14,309 spec facts across 23 formats; generated 2026-06-21
              workbench_verified_fact_total: 14,284

QNAME / HIERARCHY
  └─► shared/qname-registry/{format}.yaml (21 files: 20 formats + schema)
        Status lifecycle: seeded → architecture_only → implementing → implemented → stable
        3 verified: abw, fods, fodt
        4 implementing: csv, ndjson, xcf, zst
        13 seeded: dif, fodg, fodp, gnumeric, ods, odt, pbm, pgm, ppm, qoi, sylk, toml, tsv
  └─► registry/python-qname-architecture.json (structural facts)

CAPABILITIES
  └─► tools/capability_layer/capability_map_generator.py
        └─► reports/capability-layer/unified-capability-map.json
        └─► reports/capability-layer/foss-reduced-capability-map.json
        └─► reports/capability-layer/commercial-capability-map.json
  └─► reports/capability-layer/gap-ledger.json
        1,003 gaps total; 969 closed, 30 DEFERRED_BY_DESIGN, 0 POC-blocking

FEATURES / WORK ITEMS
  └─► tools/capability_layer/capability_to_feature_compiler.py
  └─► tools/feature_compiler/gap_to_work_item.py
  └─► tools/capability_layer/gap_ledger_to_work_items.py
        └─► .local/supervisor/product/next-work-items.json (gap-driven work items)
        └─► .local/supervisor/next-work-items.json

PRODUCT DESIGN / ARCHITECTURE
  └─► plans/strategic/spec-to-feature-radical-correction-plan.md (Lane 7-8: architecture blueprints)
  └─► shared/qname-registry/ (canonical class hierarchy)
  └─► tools/spec/generate_canonical_stubs.py
        └─► src/python/{format}/spec/ (architecture_only spec skeleton stubs)
        └─► src/net/{format}/Spec/ (architecture_only .NET spec stubs)

SOURCE GENERATION / MIGRATION
  └─► Manual governed edits via skills (.supervisor/skill-registry.yaml)
  └─► No automated code generator for Python functional source (hand-crafted)
  └─► .NET functional source: hand-crafted in src/net/{format}/

TESTS
  └─► tests/python/{format}/ (Python format tests)
  └─► tests/supervisor/ (governance and machinery tests)
  └─► .venv/Scripts/pytest (test runner)
  └─► registry/known-failure-ledger.yaml (pre-existing failure catalog)

PACKAGE
  └─► src/python/{format}/setup.py or pyproject.toml
  └─► tools/packaging/build-local-packages.py
        └─► .local/package-builds/python-foss/ (wheel files)
  └─► src/net/{format}/FormatFactory.{Format}.csproj (.NET packages)

GOVERNANCE
  └─► tools/supervisor/governance_validators.py (50 validate_* functions)
  └─► tools/supervisor/governance_validators_signal.py (V67 maturity signal)
  └─► tools/supervisor/governance_validator_runner.py (runner + 148 validate_ refs)
  └─► tools/validators/source_structure_validator.py (LOC + function cap enforcement)
  └─► registry/source-structure-baseline.json (frozen baseline_loc_cap per file)

EVIDENCE
  └─► tools/supervisor/autonomous_cycle.py (172 supervisor scripts total)
  └─► tools/supervisor/sprint_executor_validate.py (declaration schema validator)
  └─► tools/supervisor/build_declaration_review_package.py (ZIP + SHA-256 builder)

AUTONOMOUS SUPERVISION
  └─► tools/supervisor/autonomous_cycle.py (main cycle: 2374 LOC)
  └─► tools/supervisor/check_continuation.py
  └─► tools/supervisor/generate_next_work_items.py → gap-ledger-driven work items
  └─► tools/supervisor/write_plan_lock.py (per-chat plan locking)
  └─► .local/supervisor/continuation-signal.json (current: autonomous=true, iter=8)

AUDIT AND HEALING
  └─► tools/supervisor/bounded_repair_engine.py
  └─► tools/supervisor/adversarial_check.py (LLM-powered contradiction detection)
  └─► tools/supervisor/stop_reason_adjudicator.py
```

---

## Layer-by-Layer Inventory

```yaml
machinery_layer:
  layer_id: L01-SPEC-ACQUISITION
  title: Specification Acquisition
  source_paths:
    - tools/spec-cache/acquire_spec.py
    - tools/spec-cache/refresh_check.py
    - tools/spec-cache/spec_index.py
    - tools/spec-cache/propagate_source_hash.py
  entry_points:
    - tools/spec-cache/acquire_spec.py (CLI: --format {format})
    - tools/spec-cache/refresh_check.py (called from autonomous_cycle.py Step 0a-refresh)
  inputs:
    - registry/format-registry.yaml (format metadata + spec URLs)
  outputs:
    - .local/spec-cache/{format}/spec-index.yaml
    - .local/spec-cache/{format}/*.pdf (or .html)
  current_status: ACTIVE — refresh_check.py wired into autonomous_cycle.py Step 0a
  current_proof_level: PROOF_LEVEL_3 — real pipeline execution confirmed (13 formats in .local/spec-cache)
  known_gaps:
    - 7 formats have no spec cache yet (ods, odt, pbm, pgm, ppm, qoi, xcf)
    - No automated acquisition; manual download for most specs
```

```yaml
machinery_layer:
  layer_id: L02-SPEC-NORMALIZATION
  title: Specification Normalization
  source_paths:
    - tools/spec-normalize/normalize_pdf.py
    - tools/spec-normalize/build_section_index.py
    - tools/spec-normalize/build_chunk_index.py
    - tools/spec-normalize/build_spec_workbench.py
    - tools/spec-normalize/build_citation_map.py
    - tools/spec-normalize/build_requirement_pack.py
    - tools/spec-normalize/detect_coverage_gaps.py
    - tools/spec-normalize/export_task_packet.py
    - tools/spec-normalize/export_sample_requirements.py
  entry_points:
    - tools/specification-authority-layer/run_spec_pipeline.py (chains normalization steps)
  inputs:
    - .local/spec-cache/{format}/*.pdf
  outputs:
    - .local/spec-cache/{format}/sections.jsonl
    - .local/spec-cache/{format}/chunks.jsonl
    - .local/spec-cache/{format}/workbench/ (verified-facts workbench)
  current_status: IMPLEMENTED_AND_CONSUMED (for ODF formats)
  current_proof_level: PROOF_LEVEL_3 — known to have run for fods, fodt, zst, abw, gnumeric
  known_gaps:
    - run_spec_pipeline.py only lists 9 formats in KNOWN_FORMATS
    - Normalization not proven for image formats (PBM, PGM, PPM, QOI, XCF)
```

```yaml
machinery_layer:
  layer_id: L03-SAL-FACT-EXTRACTION
  title: Specification Authority Layer — Fact Extraction
  source_paths:
    - tools/specification-authority-layer/sal_master_runner.py
    - tools/specification-authority-layer/run_spec_pipeline.py
    - tools/specification-authority-layer/spec_parser.py
    - tools/specification-authority-layer/spec_digestor.py
    - tools/specification-authority-layer/requirement_extractor.py
    - tools/specification-authority-layer/requirement_graph.py
    - tools/specification-authority-layer/spec_governance_runtime.py
    - tools/specification-authority-layer/spec_indexer.py
    - tools/specification-authority-layer/spec_normalizer.py
    - tools/specification-authority-layer/fact_coverage_report.py
    - tools/specification-authority-layer/fact_quality.py
    - tools/specification-authority-layer/run_extraction_pipeline.py
    - tools/specification-authority-layer/run_fact_verification.py
    - tools/specification-authority-layer/spec_census.py
    - tools/specification-authority-layer/context_pack_builder.py
    - tools/specification-authority-layer/migrate_sources_jsonl.py
    - tools/specification-authority-layer/qname_src_compliance_reporter.py
    - tools/specification-authority-layer/extractor_to_workbench_adapter.py
  entry_points:
    - sal_master_runner.py --format {FORMAT} (single format)
    - sal_master_runner.py --all (all formats)
    - run_spec_pipeline.py --format {format} (full pipeline with normalization)
  inputs:
    - registry/format-registry.yaml
    - .local/spec-cache/{format}/workbench/ (for workbench-verified facts)
    - .local/spec-cache/{format}/verified-facts-review.yaml (manual fact verification)
  outputs:
    - .local/spec-cache/sal-facts-latest.json (14,309 facts across 23 formats)
  schemas:
    - fact entry: {qname, claim, section, description, authority, verification_status, source}
  current_status: IMPLEMENTED_AND_CONSUMED
  current_proof_level: PROOF_LEVEL_3 — 14,309 verified facts produced; generated 2026-06-21
  known_gaps:
    - sal_master_runner.py uses hardcoded spec-fact templates for most formats (not full PDF parsing)
    - True workbench-verified facts only for ODF family; other formats use template facts
    - Not regenerated automatically on spec updates; refresh_check.py provides staleness detection
```

```yaml
machinery_layer:
  layer_id: L04-QNAME-REGISTRY
  title: QName / Hierarchy Registry
  source_paths:
    - shared/qname-registry/schema.yaml
    - shared/qname-registry/{format}.yaml (20 format files)
    - registry/python-qname-architecture.json
  entry_points:
    - Manual + skill-guided population (qname-backfill skill)
    - tools/specification-authority-layer/qname_src_compliance_reporter.py
  inputs:
    - SAL facts (FACT-{FORMAT}-NNN qname refs)
    - spec QNames from format specifications
  outputs:
    - shared/qname-registry/{format}.yaml (canonical class mappings per format element)
  schemas:
    - qname, namespace_uri, local_name, canonical_class, spec_fact_ref, status, source_layer,
      facade_names, python_file, dotnet_file
  current_status: PARTIALLY_IMPLEMENTED
  current_proof_level: PROOF_LEVEL_2 — 3 formats at 'verified', 4 'implementing', 13 'seeded'
  known_gaps:
    - 17/20 formats not 'verified' → product deepening blocked for these formats
    - No automated QName derivation from SAL facts (manual workflow)
    - QName verification gate (continuation_allowed) enforced in product-deepening-ledger
```

```yaml
machinery_layer:
  layer_id: L05-CAPABILITY-LAYER
  title: Capability Extraction and Gap Ledger
  source_paths:
    - tools/capability_layer/capability_map_generator.py
    - tools/capability_layer/capability_to_feature_compiler.py
    - tools/capability_layer/validate_capability_map.py
    - tools/capability_layer/gap_ledger_to_work_items.py
    - tools/capability_layer/_write_pilots.py
  entry_points:
    - capability_map_generator.py (generates capability maps from gap ledger)
    - capability_to_feature_compiler.py (used by autonomous_cycle.py)
  inputs:
    - reports/capability-layer/gap-ledger.json (1,003 gaps)
  outputs:
    - reports/capability-layer/unified-capability-map.json
    - reports/capability-layer/foss-reduced-capability-map.json
    - reports/capability-layer/commercial-capability-map.json
    - .local/supervisor/product/next-work-items.json
  current_status: IMPLEMENTED_AND_CONSUMED
  current_proof_level: PROOF_LEVEL_3 — capability_feature_compiler imported and called
    in autonomous_cycle.py (line 1481); gap_ledger_ref injected into work items (Step 3a-pre)
  known_gaps:
    - gap_ledger.json is at 29MB — likely containing full spec text, not just gaps
    - Gap statuses: 969 closed, 30 DEFERRED_BY_DESIGN, 0 open/POC-blocking
    - Most actionable gaps are already closed; new gaps require spec analysis
```

```yaml
machinery_layer:
  layer_id: L06-PRODUCT-DEEPENING-GATE
  title: Product Deepening Ledger and Gate
  source_paths:
    - registry/product-deepening-ledger.yaml (20 format entries)
    - tools/supervisor/autonomous_cycle.py (product deepening gate checks)
  entry_points:
    - autonomous_cycle.py Step 1 (reads ledger, gates deepening sprints)
  inputs:
    - shared/qname-registry/{format}.yaml (qname_compliance_status)
    - registry/source-structure-baseline.json (LOC/function caps)
  outputs:
    - .local/supervisor/continuation-signal.json (continuation_allowed per format)
    - reports/supervisor/next-sprint.md
  current_status: IMPLEMENTED_AND_CONSUMED
  current_proof_level: PROOF_LEVEL_4 — gate actively enforced; 3/20 formats pass
  known_gaps:
    - 17 formats blocked: 13 seeded, 4 implementing
    - Advancement path (seeded→verified) is manual/skill-guided with no automated pipeline
```

```yaml
machinery_layer:
  layer_id: L07-PYTHON-PRODUCT-SOURCE
  title: Python FOSS Product Source
  source_paths:
    - src/python/{format}/ (20 format directories)
  key_formats_locs:
    - zst: zst_codec.py (~1558 LOC), compression_metrics.py
    - xcf: xcf_parser.py (~1301 LOC), xcf_image_metrics.py
    - fodg: fodg_codec.py (~3176 LOC)
    - ndjson: ndjson_codec.py, ndjson_analytics.py (923 LOC)
    - fods: 11 Python files, 93 test files
    - fodt: 14 Python files, 130 test files
    - abw: 5 Python files, 148 test files (34 test files)
  current_status: IMPLEMENTED_AND_CONSUMED (all 20 formats packaged + installable)
  current_proof_level: PROOF_LEVEL_4 — end-to-end installed workflow verified for 11 POC targets
  known_gaps:
    - spec_qname attributes not systematically present across all source classes
    - Analytics functions in some formats lack GAP-ledger references (V42 enforcement)
    - architecture_only spec stubs present for fods, fodt (not behavioral implementations)
    - Compat/ facades for fods (FodsCell, FodsSheet, FodsDocument) are empty shells
```

```yaml
machinery_layer:
  layer_id: L08-DOTNET-PRODUCT-SOURCE
  title: .NET Commercial Product Source
  source_paths:
    - src/net/fods/ (FodsParser.cs, FodsDocument.cs, FodsWriter.cs, exporters, Model/, Spec/)
    - src/net/fodt/ (FodtParser.cs, FodtDocument.cs, FodtWriter.cs, exporters, Model/, Spec/)
    - src/net/netpbm/ (NetpbmParser.cs, NetpbmWriter.cs, NetpbmExporter.cs, Model/, Spec/)
    - src/net/csv/ (CSV library used by FODS/FODT exporters)
    - src/net/html/ (HTML export library)
    - src/net/markdown/ (Markdown export library)
    - src/net/ndjson/ (NDJSON spec stubs, seeded)
    - src/net/tsv/ (TSV spec stubs, seeded)
    - src/net/txt/ (text export library)
    - src/net/zst/ (ZST spec stubs, seeded)
  current_status: IMPLEMENTED_AND_CONSUMED (for fods, fodt, netpbm)
  current_proof_level: PROOF_LEVEL_4 — FODS/FODT all dotnet_status entries = PASS including
    dotnet_tests=618; dogfood exporters delegate to Format Factory libraries
  known_gaps:
    - NOT at src/dotnet/ (architecture.md is wrong — actual path is src/net/)
    - No .NET source for: abw, dif, fodg, fodp, gnumeric, ods, odt, qoi, sylk, toml, xcf
    - Spec/ subdirectories contain architecture_only stubs for ndjson, tsv, zst
    - Gate 11 full commercial release requires Babar Raza sign-off (TRUE_EXTERNAL_GATE)
```

```yaml
machinery_layer:
  layer_id: L09-GOVERNANCE-VALIDATORS
  title: Governance Validators
  source_paths:
    - tools/supervisor/governance_validators.py (V1-V49, 3179 LOC, 99.97% of cap)
    - tools/supervisor/governance_validators_ext.py (V50-V66, 14 extended validators)
    - tools/supervisor/governance_validators_signal.py (V67 maturity signal validator)
    - tools/supervisor/governance_validator_runner.py (runner, 148 validate_ refs)
    - tools/validators/source_structure_validator.py (LOC + function cap enforcement)
    - tools/validators/qname_structure_validator.py
    - tools/validators/validate_source_architecture.py
  entry_points:
    - governance_validator_runner.py run_all_governance_validators(declaration)
    - autonomous_cycle.py Step 2e (governance validation gate)
  current_status: IMPLEMENTED_AND_CONSUMED
  current_proof_level: PROOF_LEVEL_3 — validators run every sprint cycle; GOV_BLOCK
    enforcement documented; V48 blocks architecture_only stubs in RELEASE_GATE items;
    335 supervisor test files cover governance machinery; 92 governance validator tests pass
  known_gaps:
    - Overclaim detector (10 patterns) referenced in correction plan — verify wiring
    - grade_declared_work LLM verifier requires external API (GPT_OSS_ENDPOINT)
    - Without LLM verifier, PRODUCT_SOURCE items receive DEFERRED_WITH_REASON grade
```

```yaml
machinery_layer:
  layer_id: L10-AUTONOMOUS-SUPERVISION
  title: Autonomous Supervision Pipeline
  source_paths:
    - tools/supervisor/autonomous_cycle.py (2374 LOC, 172 supervisor files total)
    - tools/supervisor/check_continuation.py
    - tools/supervisor/sprint_executor_validate.py
    - tools/supervisor/build_declaration_review_package.py
    - tools/supervisor/write_plan_lock.py (temp-path guard, orphaned-tmp cleanup)
    - tools/supervisor/adversarial_check.py (LLM-powered contradiction detection)
    - tools/supervisor/bounded_repair_engine.py
    - tools/supervisor/stop_reason_adjudicator.py
    - tools/supervisor/generate_next_work_items.py (gap-ledger → work items)
  current_status: IMPLEMENTED_AND_CONSUMED
  current_proof_level: PROOF_LEVEL_5 — repeatable, evidenced multi-sprint execution;
    49 sections in master plan; multiple ACCEPTED sprint verdicts
  known_gaps:
    - Lane ownership / DAG ordering not enforced by code (SUP-GAP-001/002 from correction plan)
    - Signal unification patch has a known bug (latest_dir not defined — logged, non-blocking)
    - adversarial_check.py times out when LLM endpoint unavailable (SSL timeout in tests)
    - ZERO durable learning: no failure-memory.json; corrections don't auto-propagate
```

---

## Gap Summary — What Machinery Is Missing or Weak

| Gap | Severity | Impact |
|-----|----------|--------|
| 17/20 formats: qname_compliance_status not verified → product deepening blocked | HIGH | Blocks autonomous deepening for 17 formats |
| docs/architecture.md massively stale (Phase 0, last reviewed 2026-05-04) | HIGH | Misleads about system structure |
| No automated QName advancement pipeline | MEDIUM | Manual work required per format |
| ZERO durable learning / failure-memory.json | MEDIUM | Corrections must be re-applied |
| LLM verifier requires external API (no fallback grading) | MEDIUM | Sprint grades deferred without API |
| architecture_only spec stubs in fods/fodt Compat/ facades | LOW | V48 governance blocks false claims |
| src/net/ not in architecture.md (only src/dotnet/ mentioned) | LOW | Documentation confusion |
| adversarial_check.py SSL timeout in offline environments | LOW | Test suite needs mock/timeout |
