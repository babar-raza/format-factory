# Fresh Chat Continuity Brief

**Document type:** Fresh Chat Orientation Guide
**Created:** 2026-05-08 (memory-planning-methodology-and-agent-handoff sprint)
**Last updated:** 2026-06-02 (R90 Product Factory Acceleration Layer sync)
**Visibility:** internal
**Purpose:** Allow the human to open a fresh chat window and continue format-factory work without needing the full original conversation history.

---

## 1. What Format Factory Is

Format Factory is an 11-gate acquisition pipeline for legal file format parsers and converters. It produces two product tracks:

- Python FOSS: `src/python/{format}/`, Tier 0-4 features, open-source release path.
- .NET product: `src/net/{format}/`, Tier 0-6 features, commercial full-feature path.

The pipeline currently covers FODS, a flat XML spreadsheet format, and FODT, a flat XML text document format. Both are ODF 1.3 formats from OASIS. Format source is Category 1, royalty-free/open specification.

The pipeline has three streams:

- MAIN SPRINT: advances gates, produces artifacts, requires human approval at each gate.
- SECONDARY SPRINT: executes authorized secondary plans.
- MEMORY SPRINT: captures decisions, strategy, and architecture into durable local artifacts.

---

## 2. Current Strategic Direction

### R90 Product Factory Acceleration

R90 added `.supervisor/skill-registry.yaml`, POC gap selection, skill-or-handoff routing,
product-code ledger validation, capability-progress detection, and declaration-driven next-sprint
acceleration. New product source edits must use a governed skill or generated handoff and must update
the ledger. Gate 11 and publication remain unapproved.

### XML-First Focus

Current work focuses on XML-type formats (`text_xml`). The pipeline is validated for XML. Non-XML formats such as ZIP containers and binary records are planned but not started.

### Format Understanding Layer

Before Phase 4 product source begins, each format should produce compiled understanding artifacts:

- `format-profile.yaml`
- `verified-facts.yaml`
- `implementation-requirements.yaml`
- `parser-strategy.yaml`
- `security-surface.yaml`
- `product-readiness.yaml`

FUL-001, FUL-002, and FUL-003 are complete for the current FODS/FODT track. See [docs/format-understanding-layer.md](format-understanding-layer.md).

### Non-XML Adaptability

The pipeline architecture must avoid hardcoding XML-only assumptions. Non-XML adaptability is backlog only until explicitly authorized. See [docs/format-representation-model.md](format-representation-model.md).

### Controlled LLM and Embedding Strategy

Future governed use of LLMs via `llm.professionalize.com` is planned. LLMs are not gate authority. Embeddings are retrieval tools, not truth authority. See [docs/llm-and-embedding-strategy.md](llm-and-embedding-strategy.md).

### Non-Aspose Candidate Registry

A registry of formats underserved by Aspose products is planned but not created. See [docs/non-aspose-format-candidate-registry-plan.md](non-aspose-format-candidate-registry-plan.md).

---

## 3. Planning Style

1. Challenge first. Every plan must be hardened before execution.
2. Verify repo truth. Do not trust agent summaries without reading files and evidence bundles.
3. Evidence is necessary. Gates require evidence bundles and contracts.
4. Missing architecture must be captured in backlog, roadmap, taskcards, or memory.
5. Single-go execution prompts are preferred for complex plans.
6. No broad cleanup. Git stash, reset, and clean commands are not defaults.
7. No push unless explicitly authorized.

---

## 4. Files A New Chat Should Read First

Ask the agent to read these files before producing any prompt:

1. `plans/master-plan.md`, authoritative operational state
2. `registry/format-registry.yaml`, exact gate statuses
3. `AGENTS.md`, non-negotiable agent rules
4. `GOVERNANCE.md`, human governance rules
5. `ROADMAP.md`, phase model and milestones
6. `docs/agent-methodology-index.md`
7. `docs/planning-methodology.md`
8. `docs/agent-execution-handoff-standard.md`
9. `docs/format-understanding-layer.md`
10. `memory/00-index.md`
11. `memory/09-current-state-before-phase1.md`
12. Latest evidence bundle, if relevant

Also run:

```powershell
git log --oneline -10
git status --short
python tools/evidence/check_current_state_consistency.py
```

---

## 5. Current Gate Status Summary

Always verify this summary against `plans/master-plan.md` and `registry/format-registry.yaml`.

| Format | Gates Passed | Current State | Next |
|---|---|---|---|
| FODS | 1-10 | Gate 11 planning_ready; Python source created in `src/python/fods/` | Resolve DEC-033 before Gate 11/.NET/commercial movement |
| FODT | 1-9 | Gate 10 planning_verified; Python source implemented pending human review | Gate 10 human review and approval decision |

Current source status:

- FODS Python source exists in `src/python/fods/`.
- FODT Python source exists in `src/python/fodt/` and has passed 115/115 tests in the implementation sprint.
- .NET source has not been created.
- LLM modules, embeddings, vector DBs, state manager code, LangGraph, Prefect, Temporal, and Dagster have not been implemented.

---

## 6. How To Continue Safely

1. Read the required files before asking the agent to do anything.
2. Confirm the agent's orientation summary against repo files.
3. Ask for the next prompt only after confirming orientation.
4. Do not advance a gate without a passing evidence bundle and human approval.
5. Do not authorize .NET or commercial source until the required decisions and gates are complete.
6. If the agent produces a summary without reading files, ask it to read the files first.

---

## 7. AI-Direction Memory

The 2026-05-09 ChatGPT supervision session provided architectural direction for AI integration and the proof strategy.

Required reading for AI/LLM/embedding work, Phase 4 planning, three-pilot proof planning, and multi-stream sprint driving:

| File | Contents |
|---|---|
| [memory/13-chatgpt-initial-project-analysis-20260509.md](../memory/13-chatgpt-initial-project-analysis-20260509.md) | Project purpose, user requirement, strengths, gaps, bottom-line assessment |
| [memory/14-ai-supervision-and-three-pilot-direction-20260509.md](../memory/14-ai-supervision-and-three-pilot-direction-20260509.md) | AI supervision rules, three-pilot proof path, parallel sprint handling |
| [memory/15-ai-modules-and-state-management-architecture-20260509.md](../memory/15-ai-modules-and-state-management-architecture-20260509.md) | Governed LLM module, embedding retrieval, agent role, source generation, state manager direction |

Memory is context, not authority. Cross-check memory against `plans/master-plan.md` and `registry/format-registry.yaml` before acting.
