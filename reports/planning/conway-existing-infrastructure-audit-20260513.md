---
document_type: infrastructure_audit
sprint: CONWAY-REBASELINE-AND-INFRASTRUCTURE-RECONCILIATION-001
title: "Conway Existing Infrastructure Audit"
date: "2026-05-13"
visibility: internal
publish_allowed: false
---

# Conway Existing Infrastructure Audit

**Sprint:** CONWAY-REBASELINE-AND-INFRASTRUCTURE-RECONCILIATION-001
**Date:** 2026-05-13
**Reference plan:** `C:\Users\prora\.claude\plans\flickering-tumbling-conway.md` (v2.0)

---

## Section 1: Existing Authoritative Infrastructure

These components exist, are tested or validated, and are authoritative for Conway's use.

### 1.1 Generated Requirements Layer (Conway Phase 2/9 output — COMPLETE for FODS/FODT)

| File | Exists | Status |
|------|--------|--------|
| `generated-requirements/fods/commercial-requirements.yaml` | YES | PASS — 0 schema errors |
| `generated-requirements/fods/object-model-requirements.yaml` | YES | PASS — 0 schema errors |
| `generated-requirements/fods/save-edit-requirements.yaml` | YES | PASS — 0 schema errors |
| `generated-requirements/fods/conversion-requirements.yaml` | YES | PASS — 0 schema errors |
| `generated-requirements/fods/traceability-map.yaml` | YES | Present — not schema-validated (no schema) |
| `generated-requirements/fods/verifier-review.yaml` | YES | LANE_R5_PASS — not schema-validated (no schema) |
| `generated-requirements/fods/generation-report.md` | YES | Human-readable generation summary |
| `generated-requirements/fodt/` (same 7 files) | YES | Same status per format |

**Note:** Conway Phase 5 planned `generation-metadata.yaml` as a separate file. In practice, generation metadata is embedded in `commercial-requirements.yaml` (generator_version, model_tool, input_source_hashes, generation_timestamp). No standalone `generation-metadata.yaml` exists or is needed.

### 1.2 Schema Validation Layer (Conway Phase 2 — PARTIAL)

| Schema | Exists | Conway planned |
|--------|--------|---------------|
| `schemas/generated-requirements/commercial-format-requirements.schema.json` | YES | YES |
| `schemas/generated-requirements/object-model-requirements.schema.json` | YES | YES |
| `schemas/generated-requirements/save-edit-requirements.schema.json` | YES | YES |
| `schemas/generated-requirements/conversion-requirements.schema.json` | YES | YES |
| `schemas/generated-requirements/traceability-map.schema.json` | **NO** | YES |
| `schemas/generated-requirements/verifier-review.schema.json` | **NO** | YES |

4/6 schemas exist. 2 missing: traceability-map and verifier-review.

### 1.3 Validator Tool (Conway Phase 2 — EXISTS)

`tools/requirements/validate_generated_requirements.py` — EXISTS, operational, covers 4 schemas.
Fallback: manual_validate when jsonschema absent.
REQUIREMENTS_SCHEMA_VALIDATION: PASS confirmed this sprint.

### 1.4 Validator Tests (Conway Phase 2 — EXISTS WITHOUT FIXTURES)

`tests/requirements/test_validate_generated_requirements.py` — EXISTS, 9 tests total.
`tests/requirements/fixtures/` — **DOES NOT EXIST** (Conway planned 4 fixture files).
Tests runnable only when pytest installed (not currently installed).

### 1.5 Evidence Contract System (Conway Phase 7 — FULLY EXISTS, STRONGER THAN PLANNED)

| Component | Exists | Version |
|-----------|--------|---------|
| `tools/evidence/build_evidence_bundle.py` | YES | v1.4+ |
| `tools/evidence/validate_evidence_bundle.py` | YES | operational |
| `tools/evidence/check_current_state_consistency.py` | YES | PENDING-marker model |
| `tools/evidence/contracts/base-run.yaml` | YES | v1.4 |
| `tools/evidence/contracts/gate-approval.yaml` | YES | — |
| `tools/evidence/contracts/gate-execution.yaml` | YES | — |
| `tools/evidence/contracts/independent-verification.yaml` | YES | — |

The evidence contract system is MORE complete than Conway's Phase 7 assumed. Conway's Phase 7 planned to add `evidence_contract_generator.py` as a new tool; the existing system already handles contract-based bundle building.

### 1.6 AI Governance Documents (NEW since Conway v1.0, all present)

| Document | Status | Notes |
|----------|--------|-------|
| `docs/ai-usage-operating-model.md` | EXISTS | Core AI governance philosophy |
| `docs/ai-assisted-commercial-development.md` | EXISTS | Patterns A-F for .NET |
| `docs/agent-swarm-ai-orchestration.md` | EXISTS | LANE K governance |
| `docs/spec-retrieval-and-rag-policy.md` | EXISTS | RAG guardrails |
| `docs/commercial-product-capability-model.md` | EXISTS | C0-C10 levels |
| `docs/commercial-dotnet-architecture.md` | EXISTS | .NET architecture |

### 1.7 Authority Governance Chain (NEW since Conway v2.0, all present)

| Governance item | Location | Status |
|-----------------|----------|--------|
| Generated requirements mandatory rule | AGENTS.md AF13 | PRESENT (updated this sprint) |
| Generated requirements governance | GOVERNANCE.md 26.11 | PRESENT (updated this sprint) |
| TC-0053 pipeline governance contract | taskcards/TC-0053 | COMPLETED this sprint |
| DEC-034 IV of requirements | COMPLETED this sprint | ESTABLISHED |
| Authority chain documented | AGENTS.md AF13 + GOVERNANCE.md 26.11 | PRESENT |

### 1.8 Existing Command System (Conway Phase 8 — 4 commands, not the Conway 9)

| Command | Exists |
|---------|--------|
| `/plan-hardening` | YES |
| `/execution-handoff` | YES |
| `/evidence-review-next-prompt` | YES |
| `/memory-sprint` | YES |
| `/commercial-sprint` | **NO** |
| `/format-context` | **NO** |
| `/generate-format-requirements` | **NO** |
| `/verify-format-requirements` | **NO** |
| `/swarm-generate` | **NO** |
| `/evidence-contract-generate` | **NO** |
| `/sprint-verify` | **NO** |
| `/format-capability-check` | **NO** |
| `/skill-system-health-check` | **NO** |

4 of 13 commands exist. The 4 that exist are infrastructure commands, not Conway-specific skill commands.

### 1.9 Format Data Sources (PER FORMAT — FULLY EXISTS)

All format data sources that Conway Phase 4 (format context resolver) would read:

| Source | Exists |
|--------|--------|
| `registry/format-registry.yaml` | YES |
| `acquisition-packs/fods/pack.yaml` | YES |
| `acquisition-packs/fods/format-profile.yaml` | YES |
| `acquisition-packs/fods/tier-map.yaml` | YES |
| `schemas/neutral-model/fods/model.yaml` | YES |
| `src/net/fods/` (full vertical slice) | YES — C4-C6 |
| `tests/net/fods/` | YES |
| Same for fodt/ | YES |

All data that the format context resolver would consume exists.

---

## Section 2: Existing Partial Infrastructure

These components partially exist but are incomplete for Conway's purposes.

### 2.1 Requirements Schemas — 4/6 Complete

4 schemas exist. Missing: traceability-map.schema.json, verifier-review.schema.json.
Impact: traceability-map.yaml and verifier-review.yaml are unvalidated. Adversarial inputs could corrupt these files without detection.
**Recommendation:** Add the 2 missing schemas in the next tooling sprint.

### 2.2 Tests Without Fixtures

`test_validate_generated_requirements.py` exists with 9 tests. All use inline test data or calls to `validate_format()`.
`tests/requirements/fixtures/` does not exist.
**Impact:** No golden fixture tests. Only unit tests and integration validation (against live YAML files).
**Recommendation:** Add fixtures directory in the next tooling sprint.

### 2.3 Conway Phase 5 — Lane Library

`docs/agent-swarm-ai-orchestration.md` exists with LANE K governance and swarm principles.
No `templates/commercial-sprint/lane-library.yaml` exists.
No `templates/commercial-sprint/coordinator-template.md` exists.
**Impact:** Swarm prompts for commercial sprints are written ad hoc rather than from a template library.
**Recommendation:** Conway Phase 5 (lane library) is the most valuable unbuilt component.

---

## Section 3: Missing Infrastructure

Components Conway planned that do not exist and are not yet needed:

| Component | Conway phase | Status | Notes |
|-----------|-------------|--------|-------|
| `tools/requirements/generate_format_requirements.py` | Phase 3 | NOT BUILT | Needed for future formats; FODS/FODT outputs already exist |
| `tools/requirements/requirements_retriever.py` | Phase 3 | NOT BUILT | Same |
| `tools/requirements/requirements_normalizer.py` | Phase 3 | NOT BUILT | Same |
| `tools/requirements/requirements_verifier.py` | Phase 3 | NOT BUILT | Same |
| `tools/requirements/requirements_traceability_builder.py` | Phase 3 | NOT BUILT | Same |
| `tools/skills/format_context_resolver.py` | Phase 4 | NOT BUILT | No tools/skills/ directory |
| `tools/skills/swarm_prompt_generator.py` | Phase 6 | NOT BUILT | Same |
| `tools/skills/evidence_contract_generator.py` | Phase 7 | NOT BUILT | Same |
| `tools/skills/lane_selector.py` | Phase 5 | NOT BUILT | Same |
| `templates/commercial-sprint/lane-library.yaml` | Phase 5 | NOT BUILT | No templates/ directory |
| `templates/commercial-sprint/coordinator-template.md` | Phase 6 | NOT BUILT | Same |
| `schemas/skills/format-config.schema.yaml` | Phase 4 | NOT BUILT | No schemas/skills/ directory |
| All 9 `.claude/commands/` skill commands | Phase 8 | NOT BUILT | — |
| `tests/requirements/fixtures/` (4 files) | Phase 2 | NOT BUILT | — |
| `tests/skills/` (all test files) | Phase 10 | NOT BUILT | — |

---

## Section 4: Duplicate-Risk Areas

Where Conway components could introduce duplication or conflict with existing infrastructure:

### DR-1: generate_format_requirements.py vs integrated Lane R3

**Risk:** Conway Phase 3 plans to create `generate_format_requirements.py` as a standalone tool.
But in practice, requirements generation happened as an integrated swarm lane (Lane R3/R4 within COMMERCIAL-LOAD-SAVE-VERTICAL-SLICE-SWARM-001). The tool would replicate behavior already proven in that sprint.
**Recommendation:** Conway Phase 3 tool must be built as a WRAPPER around the lane pattern, not as a replacement. It should read the same input sources (acquisition-pack, neutral-model, verified-facts, tier-map, existing source/tests) and produce the same output schema.

### DR-2: generation-metadata.yaml vs commercial-requirements.yaml embedded metadata

**Risk:** Conway planned `generation-metadata.yaml` as a separate provenance file. Current repo embeds generation metadata in commercial-requirements.yaml (generator_version, model_tool, input_source_hashes, generation_timestamp).
**Recommendation:** Do NOT create generation-metadata.yaml as a separate file. Instead, enhance commercial-requirements.yaml's input_source_hashes to include all planned fields (spec_normalized_path, retrieval_tier_used). GOVERNANCE.md 26.11 and TC-0053 already document the stale-detection rule; the data field simply needs more fields.

### DR-3: evidence_contract_generator.py vs existing contract system

**Risk:** Conway Phase 7 plans to create `tools/skills/evidence_contract_generator.py`. The existing contract system (build_evidence_bundle.py + base-run.yaml + per-sprint contracts) is already mature and functional.
**Recommendation:** Conway Phase 7 should produce a CONTRACT TEMPLATE for commercial-sprint-type bundles, not a new generator tool. The contract template reads from the existing base-run.yaml (inherit: base-run) and adds commercial-sprint-specific semantic checks.

### DR-4: validator duplicate-run risk

**Risk:** validate_generated_requirements.py exists. Conway Phase 2 was "Create validate_generated_requirements.py." This is already done. Conway should not recreate this tool.
**Recommendation:** Extend the existing tool with stale-detection and the 2 missing schema references (traceability-map, verifier-review) when those schemas are added.

---

## Section 5: Governance-Risk Areas

### GR-1: Conway state machine assumes fresh state

Conway's `/commercial-sprint` orchestrator state machine assumes formats have not been processed. For FODS and FODT, the state is "requirements established and IV'd." The state machine needs a "READY_FOR_IMPLEMENTATION" state that routes to implementation sprint prompt generation rather than requirements generation.

### GR-2: Conway authority chain was weaker than actual

Conway v2.0 planned: AI_PROPOSAL → ACCEPTED_FOR_VERTICAL_SLICE (after verifier review).
Actual authority chain after this sprint: AI_PROPOSAL → ACCEPTED_FOR_VERTICAL_SLICE (verifier review) → AUTHORITATIVE (DEC-034 IV).
The Conway command system must enforce the stronger chain: DEC-034 IV is mandatory before implementation, not optional.

### GR-3: Conway's AI ledger requirement

Conway plans LANE-AI with JSONL logging. AGENTS.md Section H requires LLM logs in `.local/llm-logs/`. The ledger mechanism is documented but not implemented. Conway Phase implementation must hook into this existing requirement, not create a parallel logging system.

---

## Section 6: Tooling-Risk Areas

### TR-1: pytest not installed

Tests exist but pytest is not installed. Conway's Phase 10 requires a full test suite run. This must be resolved before Phase 10.

### TR-2: jsonschema not installed

Full JSON Schema Draft7 validation falls back to manual_validate. Conway's schemas will be validated at reduced fidelity. Must be resolved before adding the 2 missing schemas.

### TR-3: format_context_resolver.py has no context YAML schema

Conway Phase 4 outputs a "structured context block." There is no defined schema for this block. Risk: context blocks become format-specific blobs that the prompt generator cannot reliably consume.
**Recommendation:** Define `schemas/skills/format-context-output.schema.yaml` before implementing the resolver.

---

## Section 7: Authority-Chain-Risk Areas

### AR-1: Command files have no authority enforcement today

Existing command files (.claude/commands/) do not have AUTHORITY headers linking to AGENTS.md and GOVERNANCE.md. Conway's planned commands should include this header. The plan specifies it (Section 23, item 6: "Every command file begins with 'AUTHORITY: This command is governed by AGENTS.md and GOVERNANCE.md'").

### AR-2: Generated prompts are unvalidated

Conway's `/swarm-generate` plans a 10-criterion quality gate for generated prompts. This gate does not exist as a tool. Generated implementation prompts currently receive no automated quality check (no forbidden git command scan, no overclaim scan, no 20-component completeness check). This is the highest-value missing component for safe autonomous operation.

### AR-3: Stale detection code is missing

TC-0053 documents the rule. GOVERNANCE.md 26.11 documents the rule. No code enforces it. An agent processing a stale requirements set would not be blocked automatically.

---

## Summary

| Category | Complete | Partial | Missing |
|----------|---------|---------|---------|
| Requirements layer (FODS/FODT) | 14 files | 0 | 0 |
| Schemas | 4 | 0 | 2 |
| Validator tool | 1 | 0 | 0 |
| Tests | 1 file (no fixtures) | 1 | 0 |
| Evidence contracts | Fully operational | 0 | 0 |
| AI governance docs | 6 docs | 0 | 0 |
| Authority chain governance | Full (this sprint) | 0 | 0 |
| Commands (4 existing / 9 Conway) | 4 infra | 0 | 9 Conway-specific |
| Skills tools | 0 | 0 | All |
| Templates | 0 | 0 | All |
| Skill schemas | 0 | 0 | All |
