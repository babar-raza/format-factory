# Preflight State Report

**Sprint/Run ID:** ff-archaeology-20260625
**Timestamp:** 2026-06-25

---

## Repository State

| Field | Value |
|-------|-------|
| Branch | main |
| Remote | origin/main |
| HEAD | c6b24706 |
| HEAD message | feat(knowledge): Phase 3 — TC-P3-001/002/003/004 all-green, hidden-puzzling-rain closure |
| Working tree | Clean at audit time (git status from session start shows ~130 modified/untracked) |

## Recent Commits

```
c6b24706 feat(knowledge): Phase 3 — TC-P3-001/002/003/004 all-green
4225a87c fix(governance): cheeky-moseying-teapot — GLOBAL_EXEMPT_PATHS + README + gap-ledger closure
4009385f fix(governance): SKILL-GOVERNANCE-REPAIR-001 closure — rollback-and-recovery stub + Section 56
53ad2edb feat(closure): PDEP-2026-06-25-001 governed task closure — master-plan Section 54, grade matrix
168896db feat(governance): TC-R008 write-time skill entry preflight validator + ALL-GREEN criteria
```

---

## Dirty File Classification (Session Start Context)

~130 files in git status. Classified by category:

### Product Source (src/) — Modified
- `src/net/csv/CsvDocument.cs` — behavioral query methods (sprint artifact)
- `src/net/fods/FodsDocumentExporter.cs` — export enhancement
- `src/net/fodt/FodtDocument.cs` — domain model update
- `src/net/ndjson/NdjsonDocument.cs` — filter/query methods
- `src/net/tsv/TsvDocument.cs` — query methods
- `src/net/zst/ZstDocument.cs` — computed properties
- `src/python/abw/__init__.py`, `spec/document/` — sprint artifacts
- `src/python/csv/__init__.py` — API pollution fix
- `src/python/dif/__init__.py`, `dif_parser.py` — sprint artifacts
- `src/python/fods/Compat/__init__.py`, multiple new Compat/ files — sprint artifacts
- `src/python/fodt/Compat/__init__.py`, multiple new Compat/ files — sprint artifacts
- `src/python/gnumeric/__init__.py`, `gnumeric_codec.py`, `spec/workbook/` — sprint artifacts
- `src/python/ndjson/__init__.py`, `ndjson_codec.py` — sprint artifacts
- `src/python/ods/__init__.py`, `ods_parser.py` — sprint artifacts
- `src/python/odt/__init__.py`, `odt_parser.py` — sprint artifacts
- `src/python/pbm/__init__.py`, `pgm/__init__.py`, `ppm/__init__.py` — sprint artifacts
- `src/python/qoi/__init__.py` — sprint artifact
- `src/python/sylk/__init__.py`, `sylk_parser.py` — sprint artifacts
- `src/python/toml/__init__.py`, `config_document.py`, `exceptions.py` — sprint artifacts
- `src/python/tsv/__init__.py` — sprint artifact
- `src/python/xcf/__init__.py`, `xcf_image_metrics.py`, `xcf_parser.py` — sprint artifacts
- `src/python/zst/__init__.py` — sprint artifact

### Machinery Source (tools/) — Modified
- `tools/capability_layer/capability_map_generator.py`
- `tools/supervisor/anti_skip_checker.py`
- `tools/supervisor/autonomous_cycle.py`
- `tools/supervisor/autonomous_loop_runner.py`
- `tools/supervisor/autonomous_task_generator.py`
- `tools/supervisor/capability_feature_compiler.py`
- `tools/supervisor/capability_queue_consumer.py`
- `tools/supervisor/failure_memory.py`
- `tools/supervisor/gap_ledger_to_work_items.py`
- `tools/supervisor/generate_next_worker_prompt.py`
- `tools/supervisor/generate_supervisor_packet.py`
- `tools/supervisor/governance_validators.py`
- `tools/supervisor/knowledge_freshness_validator.py`
- `tools/supervisor/product_feature_factory.py`
- `tools/supervisor/sprint_executor.py`
- `tools/supervisor/stop_reason_adjudicator.py`
- `tools/supervisor/write_plan_lock.py`

### Generated Evidence / Reports — Modified
- `reports/capability-layer/` — 6+ files (capability map regenerations)
- `reports/supervisor/` — 15+ files (sprint summaries, grades, next-sprint)
- `reports/acceleration-product-first/ai-usage-ledger.jsonl`
- `reports/r90/product-code-change-ledger.json`
- `reports/qname-coverage-*.json`
- `reports/sal-qname-gap-*.json`

### Registry / Configuration — Modified
- `.claude/commands/command-registry.yaml`
- `.supervisor/context-pack.yaml`
- `.supervisor/knowledge/contracts/python-domain-model.yaml`
- `.supervisor/project-memory.md`
- `.supervisor/residual-bypass-report.yaml`
- `.supervisor/skill-registry.yaml`
- `registry/parity-matrix.yaml`
- `registry/product-deepening-ledger.yaml`
- `registry/source-structure-baseline.json`
- `shared/qname-registry/*.yaml` — 19 format YAML files modified

### Plans — Modified
- `plans/strategic/capability-fact-to-feature-production-plan.md`
- `plans/master-plan-memory.md`

### Tests — Modified/Untracked
- `tests/python/sylk/test_r115_sylk_write_roundtrip.py`
- `tests/python/toml_format/test_r261_toml_sprint47_gaps.py`
- `tests/python/zst/test_r198_zst_g11_readiness.py`
- `tests/supervisor/acceleration/` — 3 test files
- `tests/supervisor/test_governance_validators.py`
- 20+ new untracked test files across formats

### Untracked New Files (Notable)
- `docs/api/pbm.md`, `pgm.md`, `ppm.md` — API docs
- `docs/publication/` — publication docs
- `docs/release/pbm-v0.1.0.md`, `pgm-v0.1.0.md`, `ppm-v0.1.0.md`
- `examples/python/csv/read_and_inspect.py`
- `examples/python/odt/` — new ODT examples
- `examples/python/pbm/pbm_analytics_example.py`
- `examples/python/pgm/`, `ppm/` — new examples
- `src/net/fodt/Exceptions/` — new exception types
- `src/net/fodt/FodtDocumentAccessor.cs`
- `src/net/netpbm/Exceptions/` — new exception types
- `src/net/netpbm/NetpbmDocument.cs`
- `src/python/fods/Compat/` — 10 new files
- `src/python/fodt/Compat/` — 4 new files
- `tests/net/csv/CsvR117DocumentQueryTests.cs`
- `tests/net/fods/FodsR117XmlExportTests.cs`, `FodsR118TsvExportTests.cs`
- `tests/net/ndjson/NdjsonR117DocumentQueryTests.cs`
- `tests/net/netpbm/NetpbmR117DocumentTests.cs`, `NetpbmR118DocumentPropertiesTests.cs`
- `tests/net/tsv/TsvR117DocumentQueryTests.cs`
- `tests/net/zst/ZstR117DocumentPropertiesTests.cs`
- `tests/python/abw/test_abw_document_model.py`
- `tests/python/csv_format/` — 4 new test files
- `tests/python/dif/test_dif_spec_qname.py`
- `tests/python/gnumeric/test_gnumeric_document_model.py`
- `tests/python/ndjson/test_ndjson_document_model.py`, `test_ndjson_spec_qname.py`
- `tests/python/odt/test_odt_spec_qname.py`, `test_odt_writer.py`
- 15+ additional new test files

---

## Existing Plans

| Plan File | Status |
|-----------|--------|
| `plans/master-plan.md` | Active (v4.1+, Section 54+ closed) |
| `plans/strategic/spec-to-feature-radical-correction-plan.md` | Active (27 sections, master authority) |
| `plans/master-plan-memory.md` | Active ledger (LEDGER-001 through LEDGER-021) |
| `plans/strategic/capability-fact-to-feature-production-plan.md` | Modified (capability gap closure) |

---

## Evidence Directories

- `.local/evidences/` — 200+ run directories (June 3 – June 25)
- Most recent: `immutable-percolating-forest-TC-PUB-20260625`
- Evidence schema: evidence-declaration.yaml per run

---

## Key Ledgers

| File | Entries | Status |
|------|---------|--------|
| `reports/capability-layer/gap-ledger.json` | 1,132 | 87.9% closed |
| `reports/r90/product-code-change-ledger.json` | ~200+ | v2.0, SHA-256 tracked |
| `registry/source-structure-baseline.json` | 47 violations | write-once caps |
| `registry/known-failure-ledger.yaml` | ~30 entries | pre-existing failures catalogued |

---

## Governance Documentation

| File | Purpose |
|------|---------|
| `docs/code-quality/production-readiness-standard.md` | Binding quality contract |
| `docs/automation/supervisor-worker-contract.md` | Declaration schema |
| `docs/automation/autonomous-supervision-replication-guide.md` | Architecture guide |
| `AGENTS.md` | Human-free autonomy doctrine |
| `CLAUDE.md` | Session instructions |

---

## Skill Directories

- `.claude/commands/` — 37 command files
- `.supervisor/skill-registry.yaml` — 51.8 KB skill registry
- `.supervisor/knowledge/` — KC-PYTHON-001, KC-PYTHON-002 contracts

---

## SAL Files

- `.local/spec-cache/` — 23 format JSON files
- `.local/spec-cache/sal-facts-20260621.json` — consolidated (14,284 facts)
- `.local/spec-cache/sal-output-latest.json` — latest output

---

## Capability Layer Files

- `reports/capability-layer/capability_summary.json` — 1,909 records
- `reports/capability-layer/unified-capability-map.json` — SAL-enriched map
- `reports/capability-layer/gap-closure-log.json` — gap closure history
- `reports/capability-layer/commercial-capability-map.json`
- `reports/capability-layer/foss-reduced-capability-map.json`
- `reports/capability-layer/analytics-classification.json`

---

## Autonomous Supervisor Files

- `tools/supervisor/autonomous_cycle.py` — 2,406+ LOC main orchestrator
- `tools/supervisor/check_continuation.py` — deterministic verdict engine
- `tools/supervisor/governance_validators.py` — 50 validators, 3,178+ LOC
- `.local/supervisor/continuation-signal.json` — session state
- `reports/supervisor/session-resume.md` — last sprint summary
- `reports/supervisor/approval-gates.md` — AUTONOMOUS_CONTINUE gate
- `reports/supervisor/next-sprint.md` — next work items
