# Capability & Feature Understanding Layer — Investigation Report
# Sprint: FORMAT-FACTORY-CAPABILITY-FEATURE-UNDERSTANDING-LAYER-INVESTIGATIVE-HEALING-001
# Run ID: capability-feature-understanding-layer-healing-20260608-e382e5f
# Generated: 2026-06-08

## Executive Summary

The Format Factory project has a mature Format Understanding Layer (FUL) that is not yet integrated
into a unified, machine-readable capability map. The key gaps are:
1. No `capability_map_generator.py` exists — maps must be manually curated
2. `poc-targets.yaml` is stale (last R114/2026-06-04) — missing 3 FOSS formats and several capabilities
3. `product_task_selector.py` uses a hardcoded 5-task catalog — not driven by capability gaps
4. FODG codec has only probe/load — no write or export (the weakest active FOSS codec)
5. Gnumeric `set_cell_value` IS implemented (not as plan assumed) — 11/11 tests PASS

**Layer state: EXISTS IN PIECES — not yet unified or auto-generating**

---

## 1. Spec Authority Layer

**Location:** `tools/specification-authority-layer/` (13 Python files)
**Files:** context_pack_builder.py, requirement_extractor.py, requirement_graph.py, spec_digestor.py, spec_governance_runtime.py, spec_indexer.py, spec_normalizer.py, spec_parser.py, spec_source_registry.py, spec_vault_ingest.py, spec_verifier.py

**Status:** REAL SOURCE CODE — tools exist but spec cache not populated for most formats
**Evidence:** `acquisition-packs/` has per-format directories but actual spec downloads require authorization
**Contradiction:** Tools ready but no live spec facts generated for FODG, ABW, Gnumeric, TSV, NDJSON
**Risk:** HIGH — without spec facts, capability provenance is `schema_authority_available` or `human_goal` only
**FUL Integration:** FUL-001 COMPLETED (6 schemas). FUL-002 COMPLETED (FODS FUL package).

---

## 2. Requirement Authority Layer

**Location:** `tools/requirements_authority/` (15 Python files + `requirements-authority/` schemas)
**Schemas:** 8 JSON Schema files including proof_graph_node, proof_graph_edge, capability_claim, capability_delta, coverage_record
**Status:** REAL SOURCE CODE — mature, 6 fixture packs for testing
**Fixtures:** clean_fods_export, fodt_export_not_save_overclaim, netpbm_partial_variant_coverage, zst_roundtrip_clean, sylk_missing_dogfood, dif_empirical_only_caveated
**Contradiction:** Not wired into `product_task_selector.py` — gap selection still uses hardcoded catalog
**Risk:** MEDIUM — layer is ready but disconnected from task generation

---

## 3. Capability-Related Schemas

**Existing FUL schemas** (`schemas/format-understanding/`):
- format-profile.schema.yaml
- verified-facts.schema.yaml
- implementation-requirements.schema.yaml
- parser-strategy.schema.yaml
- security-surface.schema.yaml
- product-readiness.schema.yaml

**New capability schemas** (to be created by this sprint — `schemas/capability/`):
- capability_status_taxonomy.schema.json — **CREATED (Phase A)**
- capability_record.schema.json — PENDING
- capability_map.schema.json — PENDING
- capability_gap.schema.json — PENDING
- pilot_report.schema.json — PENDING

---

## 4. Product Capability Matrix Files

**Location:** `product-capability-matrix/`
**Files:**
- `poc-targets.yaml` — STALE (last updated R114/2026-06-04)
  - Missing FOSS formats: FODG, TSV, NDJSON
  - Missing ABW capability: export_to_csv
  - Missing Gnumeric capabilities: get_cell_value, get_sheet_names, set_cell_value
- `fods.yaml` — per-format commercial profile
- `fodt.yaml` — per-format commercial profile
- `netpbm.yaml` — per-format commercial profile
- `dotnet-fods-fodt.yaml` — dotnet combined profile

**Risk:** HIGH — stale matrix produces misleading capability maps

---

## 5. Product Task Selector

**Location:** `tools/supervisor/product_task_selector.py`
**Status:** HARDCODED 5-task catalog (h8-probe-abw-001, h8-probe-gnumeric-001, h9-gnumeric-create-001, h9-gnumeric-write-001, h9-abw-txt-export-001)
**Authority gate:** `_get_format_authority_status()` reads poc-targets.yaml — REPAIRED in spec-authority healing sprint
**Gap:** Cannot dynamically generate tasks from capability gap data
**Risk:** MEDIUM — selector works but cannot grow without manual catalog updates

---

## 6. Existing Action Queues & Continuation

**Location:** `.local/supervisor/`
**Files:**
- `next-action.json` — post-closeout verification check (trivial)
- `active-continuation.json` — ACTIVE
- `continuation-signal.json` — present
- `action-queue.jsonl` — present
- `selected-product-gaps.json` — present

**Status:** System is in valid state for autonomous continuation
**AUTONOMOUS_CONTINUE: YES**

---

## 7. Python FOSS Product Implementations

| Format | Functions | Write | Export | Tests | POC Status |
|--------|-----------|-------|--------|-------|------------|
| ABW | 13 (load, probe, create, write, edit, export_to_txt/html/json/csv, metadata) | YES | TXT/HTML/JSON/CSV | 9 files | P0 |
| Gnumeric | 13 (load, probe, create, write, export_csv/json, get_sheet_names, get_cell_value, set_cell_value) | YES | CSV/JSON | 6 files | P1 |
| TSV | 6 (load, probe, write, parse, get_capabilities) | YES | Native | 8 files | P0 |
| NDJSON | 7 (probe, load, write, append, filter, get_field_names, get_record_count) | YES | Native | 3+ files | P0 |
| FODG | 6 (load, probe, get_page_count, get_shape_count, extract_text, get_page_metadata) | **NO** | **NO** | 2 files | **NEEDS WRITE** |
| SYLK | parse, write, csv_export, installed_workflow | YES | CSV | many | P0 |
| ZST | compress/decompress | YES | N/A | many | P0 |
| DIF | stats | NO | NO | few | ON_HOLD |

---

## 8. Commercial .NET Products

| Format | .NET Functions | Tests | Gate Status |
|--------|---------------|-------|-------------|
| FODS | 40+ (full load/edit/save/export suite) | 547 | Gate 11 APPROVED |
| FODT | 35+ (full load/edit/save/export suite) | 520 | Gate 11 APPROVED |
| Netpbm | 30+ (image manipulation suite) | 423 | Gate 11 APPROVED |

---

## 9. Contradictions Found

| ID | Type | Description | Resolution |
|----|------|-------------|------------|
| CONT-001 | STALE | poc-targets.yaml missing FODG, TSV, NDJSON from FOSS | Update poc-targets.yaml |
| CONT-002 | STALE | poc-targets.yaml missing ABW.export_to_csv | Update poc-targets.yaml |
| CONT-003 | STALE | poc-targets.yaml missing Gnumeric.get_cell_value/get_sheet_names/set_cell_value | Update poc-targets.yaml |
| CONT-004 | PLAN | Plan said Gnumeric.set_cell_value missing — IT'S IMPLEMENTED | Plan corrected in Phase A |
| CONT-005 | GAP | No unified capability map generator — capabilities tracked manually in YAML | Create capability_map_generator.py |
| CONT-006 | GAP | product_task_selector.py hardcoded catalog — cannot grow from gap data | Integrate with capability map |

---

## 10. Overall Layer Readiness Assessment

**Pre-sprint verdict:** `CAPABILITY_LAYER_PARTIAL_WITH_LIMITATIONS`

Components ready: FUL schemas, acquisition-pack structure, requirements authority schemas/tools,
poc-targets.yaml (stale), spec authority tools

Components missing: unified capability map generator, capability record schema (capability/ namespace),
gap ledger, action queue from capability data, product task selector integration

After this sprint: Expected `CAPABILITY_LAYER_PARTIAL_WITH_LIMITATIONS` (cannot be VERIFIED_READY
without live spec cache for all formats — spec downloads require authorization)
