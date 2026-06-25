# Inventory — Spec Authority Machinery
## Run ID: spec-authority-machinery-explosion-20260625-c6b2470

---

## Tool Inventory

| Path | Type | Role | Status | Category | Active | Bypass Risk | Notes |
|------|------|------|--------|----------|--------|-------------|-------|
| `tools/spec-cache/acquire_spec.py` | python_script | Download + hash spec files after T3 authorization | active | authoritative | manual | LOW | Default DRY_RUN. T3 auth = 6 conditions. Only ODF completed T3. |
| `tools/spec-cache/spec_normalizer.py` | python_script | Text/section/chunk extraction from cached PDF | active | authoritative | manual | LOW | Only run for FODS/ODF. Not run for CSV/NDJSON/TOML/ZST despite accessible specs. |
| `tools/spec-cache/spec_verifier.py` | python_script | Verify candidate facts against spec text | active | authoritative | manual | LOW | Used for FODS (4348 verified). Not run for other formats. |
| `tools/spec-cache/requirement_extractor.py` | python_script | Extract formal requirements from verified facts | active | authoritative | manual | MODERATE | Req packs exist for FODS but NOT injected into worker prompts. |
| `tools/spec-cache/run_extraction_pipeline.py` | python_script | Orchestrate full spec acquisition pipeline | active | authoritative | NOT_CALLED | HIGH | NOT a registered skill. Manual execution only. |
| `tools/spec-cache/refresh_check.py` | python_script | Detect stale/missing spec cache entries | active | advisory | non-blocking | LOW | Non-blocking call in autonomous_cycle Step 0a-refresh. Found 4 stale entries. |
| `tools/spec-cache/authority_conveyor.py` | python_script | Plan P-level advancement for a format | active | advisory | NOT_CALLED | LOW | Not called from autonomous loop. Useful manual pilot tool. |
| `tools/supervisor/authority_gate_validation.py` | python_script | P0-P6 classification; product expansion gate | active | authoritative | NOT_CALLED | **CRITICAL** | BUG: `rglob("*.py")` includes build/. NOT called from product_task_selector. MIN_PRODUCT_EXPANSION_LEVEL=4 never checked in autonomous path. |
| `tools/supervisor/validate_spec_fact_refs.py` | python_script | Validate spec_fact_refs in evidence | active | authoritative | advisory_only | **CRITICAL** | Only fires if spec_fact_refs PROVIDED AND INVALID. Absent = no enforcement. Called advisory-only. |
| `tools/supervisor/authority_integration_fabric.py` | python_script | Connect sprints to requirements_authority layer | exists_but_unwired | advisory | NEVER | **CRITICAL** | NOT imported by autonomous_cycle.py. Entire requirements_authority/ dormant. |
| `tools/supervisor/product_task_selector.py` | python_script | Select next product tasks from gap ledger | active | authoritative | YES | **CRITICAL** | Checks poc-targets ONLY. _BLOCKED_AUTHORITY_STATES never populated. Hard-coded catalog bypasses authority gate. |
| `tools/supervisor/generate_next_worker_prompt.py` | python_script | Generate worker prompts for product sprints | active | authoritative | YES | HIGH | sal-facts-{format}.json NOT in READ_BEFORE_EXECUTION. No spec facts injected. |
| `tools/supervisor/autonomous_cycle.py` | python_script | Main autonomous sprint execution loop | active | authoritative | YES | HIGH | TC-GUARD-001 Step 2d3: OR logic — gap_ledger_ref alone bypasses spec_fact_refs. authority_integration_fabric NOT imported. |
| `tools/supervisor/governance_validators.py` | python_script | 48 governance validators for sprint evidence | active | authoritative | YES | MODERATE | V13 only fires if spec_fact_refs present+invalid. Absent+exception_classification = PASS. |
| `tools/supervisor/anti_skip_checker.py` | python_script | 19 detectors for skipped/inadequate work | active | authoritative | YES | MODERATE | Detector 19 (ODF spec linkage) HIGH severity — downgrades verdict, does NOT block. |
| `tools/requirements_authority/graph_store.py` | python_module | Store spec→fact→code→test proof graph | dormant | advisory | NEVER | LOW | Dormant — authority_integration_fabric.py (its caller) is unwired. |
| `tools/requirements_authority/coverage_evaluator.py` | python_module | Evaluate spec coverage by code+tests | dormant | advisory | NEVER | LOW | Dormant. Would provide overclaim detection if wired. |
| `tools/requirements_authority/overclaim_detector.py` | python_module | Detect product readiness overclaims | dormant | advisory | NEVER | LOW | Dormant. If wired, would catch MODERATE/HIGH overclaim risks for 15+ formats. |

---

## Spec Cache Workbench Inventory

| Format | Cache Path | State | Facts | Proof Graph | Next Step |
|--------|-----------|-------|-------|-------------|-----------|
| FODS | `.local/spec-cache/fods/1.3/` | FULL | 4988 (4348 verified) | FACT-FODS-001 only | Extend proof graph to FACT-FODS-002..010 |
| FODT | `.local/spec-cache/fodt/` | STALE_MISSING_FILE | 4936 | NONE | Re-acquire FODT spec PDF |
| ODS | `.local/spec-cache/ods/` | PARTIAL | 1069 | NONE | Create proof graph for key facts |
| ODT | `.local/spec-cache/odt/` | PARTIAL | 1066 | NONE | Create proof graph for key facts |
| FODG | `.local/spec-cache/fodg/` | PARTIAL | 1066 | NONE | Create proof graph for key facts |
| FODP | `.local/spec-cache/fodp/` | PARTIAL | 1066 | NONE | Create proof graph for key facts |
| ZST | `.local/spec-cache/zst/` | PARTIAL | 94 | FACT-ZST-001 | Advance 92 remaining RFC8878 facts |
| PBM | `.local/spec-cache/pbm/` | PARTIAL | 2 | NONE | Expand Netpbm spec coverage |
| PGM | `.local/spec-cache/pgm/` | PARTIAL | 2 | NONE | Expand Netpbm spec coverage |
| PPM | `.local/spec-cache/ppm/` | PARTIAL | 2 | NONE | Expand Netpbm spec coverage |
| Gnumeric | `.local/spec-cache/gnumeric/v10/` | METADATA_ONLY | 3 (structural) | NONE | P1 ceiling. XSD-only. |
| ABW | `.local/spec-cache/abw/` | METADATA_ONLY | 5 (structural) | NONE | P1 ceiling. No public spec. |
| SYLK | `.local/spec-cache/sylk/` | METADATA_ONLY | 3 (structural) | NONE | P1 ceiling. No public spec. |
| DIF | `.local/spec-cache/dif/` | METADATA_ONLY | 3 (structural) | NONE | P1 ceiling. No public spec. |
| CSV | `.local/spec-cache/csv/` | UNKNOWN | 2 | NONE | RFC4180 available. Run normalization. |
| TSV | `.local/spec-cache/tsv/` | METADATA_ONLY | 2 | NONE | P1 ceiling. No formal RFC. |
| NDJSON | `.local/spec-cache/ndjson/` | METADATA_ONLY | 2 | NONE | ndjson.org spec accessible. P2. |
| TOML | `.local/spec-cache/toml/` | UNKNOWN | 2 | NONE | spec-toml.io accessible. Run normalization. |
| XCF | `.local/spec-cache/xcf/` | METADATA_ONLY | 2 | NONE | GIMP internal format. P2. |
| QOI | `.local/spec-cache/qoi/` | UNKNOWN | 2 | NONE | qoi.phoboslab.org spec available. P2. |

---

## Documentation Inventory

| Path | Role | Status | Notes |
|------|------|--------|-------|
| `docs/automation/supervisor-worker-contract.md` | Evidence declaration required fields | ACTIVE | **CRITICAL GAP**: spec_fact_refs NOT in required fields |
| `docs/specification-cache.md` | T3 authorization model | ACTIVE | Defines 6 T3 conditions. Authoritative. |
| `docs/specification-normalization.md` | Normalization pipeline policy | ACTIVE | Describes pipeline; only run for ODF. |
| `docs/spec-retrieval-strategy.md` | Retrieval design doc | ADVISORY | Design exists; no active retrieval code in production. |
| `docs/spec-retrieval-and-rag-policy.md` | RAG policy | ADVISORY | Policy sound; not runtime-enforced. |
| `docs/llm-and-embedding-strategy.md` | LLM/embedding strategy | ADVISORY | Policy: AI cannot be authority. Not runtime-enforced. |
| `docs/governance/ai-authority-boundary.md` | AI authority boundary rules | ADVISORY | Correct policy. No runtime enforcement of ai_draft labels. |
| `product-capability-matrix/poc-targets.yaml` | Format capability registry | ACTIVE | Missing: authority_level column per format. |
| `shared/qname-registry/` | QName→class mapping (20 formats) | ACTIVE | V53 validates. Not connected to spec_fact_refs enforcement. |
| `.supervisor/skill-registry.yaml` | Governed skill registry | ACTIVE | **MISSING**: acquire-spec-t3, normalize-spec, extract-spec-facts, authority-gate-validation, pilot-rerun-authority |

---

## Key Findings Summary

- **24 tools/artifacts inventoried**
- **3 CRITICAL bypass paths** (product_task_selector, TC-GUARD-001, validate_spec_fact_refs)
- **1 CRITICAL dormant integration** (authority_integration_fabric.py)
- **1 CRITICAL schema gap** (supervisor-worker-contract.md missing spec_fact_refs)
- **15/20 formats at P1-P2** (metadata-only or legacy_backfill)
- **5/20 formats at P5-P6** (ODF family + ZST with genuine spec coverage)
- **0 formats have authority_level recorded in poc-targets.yaml**
- **5 minimum skills NOT registered** (spec acquisition pipeline ungoverned)
