# Architecture — format-factory

**Document type:** Architecture Reference — Phase 0 Foundation
**Last reviewed:** 2026-05-04 (run014: folder tree updated — added specification-cache.md, TC-0007, TC-0008, memory/ folder)
**Authority:** This document is the architectural design reference for format-factory. For operational project state (current phase, gate history, active work), see `plans/master-plan.md`.

---

## Purpose

This document defines the structural design of the format-factory system: the folder layout, product tracks, acquisition pipeline, agent operations backbone, artifact model, and local persistence strategy. It is a living design reference — updated when architectural decisions change, not when day-to-day work progresses.

---

## System Overview

format-factory is a File Format Acquisition System. It produces legal parsers, converters, importers, exporters, validators, and compatibility tools for structured file formats. It is governed by a formal acquisition pipeline (11 gates), driven by agentic workflows (Claude as primary executor), and outputs to four distinct product tracks.

The system does not engage in unauthorized binary reverse engineering, bypass access controls, or violate intellectual property rights. Every format must pass legal review (Gate 2) before any prototype work begins.

---

## Product Tracks

Four tracks receive output from the acquisition pipeline:

| Track | Technology | License | Source Layout | Scope |
|---|---|---|---|---|
| Python FOSS | Python 3.11+ | Apache 2.0 | `src/python/{format}/` | Parsers, validators, converters — Tier 0-4 ceiling |
| .NET product | net8.0 / net10.0 | Commercial (FOSS subset TBD — DEC-033) | `src/net/{format}/` | Full-feature product — Tiers 0-6 |
| Acquisition layer | Python + CLI tools | Internal only | `tools/`, `acquisition-packs/` | Evidence, samples, schemas — never shipped |

**Format-first source layout:** Every format that reaches Phase 4 gets its own source directory within `src/python/` and `src/net/`. Example: `src/python/fods/`, `src/net/fods/`. There is no shared `open-source/` or `commercial/` subdirectory — the format subdirectory IS the product workspace.

The .NET commercial tiers (5-6) within `src/net/{format}/` are not created until Gate 10 has passed, Decision DD3 is resolved, commercial implementation taskcards exist, and an explicit commercial implementation execution prompt has been issued. Gate 11 is commercial release readiness, not creation authorization. The .NET FOSS packaging question is deferred (DEC-033). See `docs/product-tracks.md` for full track definitions.

**Obsolete paths (must not be created):** `src/python/open-source/`, `src/dotnet/open-source/`, `src/dotnet/commercial/` — these were the old layout and are replaced by the format-first structure above.

---

## Folder Tree — Committed State

```
format-factory/
|
+-- .gitignore                              [Phase 0]
+-- .env.example                           [Phase 0] Variable name template
+-- README.md                              [Phase 0]
+-- AGENTS.md                              [Phase 0] Agent operating contract
+-- GOVERNANCE.md                          [Phase 0] Human governance rules
+-- ROADMAP.md                             [Phase 0] Milestone map
|
+-- .claude/
|   +-- settings.json                      [Phase 0] Claude Code project config
|   +-- commands/
|       +-- _readme.md                     [Phase 0] Planned commands description
|
+-- docs/
|   +-- architecture.md                    [Phase 0] This file
|   +-- product-tracks.md                  [Phase 0] Four track definitions
|   +-- acquisition-workflow.md            [Phase 0] Pipeline and reuse policy
|   +-- gates.md                           [Phase 0] 11 gate definitions
|   +-- security.md                        [Phase 0] Parser threat model
|   +-- legal-and-licensing.md             [Phase 0] Legal policy
|   +-- release-control.md                 [Phase 0] Visibility and release policy
|   +-- llm-endpoint-strategy.md           [Phase 0] LLM endpoint and credentials policy
|   +-- specification-cache.md            [Phase 0] Spec cache policy and authorization model (added run008)
|
+-- memory/
|   +-- README.md                          [Phase 0] Memory package orientation
|   +-- 00-index.md                        [Phase 0] Memory index
|   +-- (11 numbered memory files)         [Phase 0] Historical context and rationale (context only, not authority)
|
+-- plans/
|   +-- master-plan.md                     [Phase 0] Single living project authority
|
+-- taskcards/
|   +-- _template.md                       [Phase 0]
|   +-- TC-0001-pilot-selection.md         [Phase 0]
|   +-- TC-0002-schema-language.md         [Phase 0]
|   +-- TC-0003-sdk-baseline.md            [Phase 0]
|   +-- TC-0004-commands-skills.md         [Phase 0]
|   +-- TC-0005-llm-endpoint-impl.md       [Phase 0]
|   +-- TC-0006-release-manifest.md        [Phase 0]
|   +-- TC-0007-specification-cache.md    [Phase 0] Generic spec-cache tooling (added run008)
|   +-- TC-0008-memory-sync-command.md    [Phase 0] Memory sync command planning (added run010)
|
+-- registry/
|   +-- format-registry.yaml              [Phase 0] Empty skeleton
|   +-- scoring/
|       +-- _scoring-model.md             [Phase 0]
|
+-- acquisition-packs/
|   +-- _template/
|       +-- pack.yaml                     [Phase 0]
|       +-- spec-evidence.md              [Phase 0]
|       +-- legal-notes.md                [Phase 0]
|       +-- sample-sources.md             [Phase 0]
|       +-- parser-notes.md               [Phase 0]
|
+-- samples/
|   +-- _policy.md                        [Phase 0]
|   +-- _provenance.yaml                  [Phase 0] Empty skeleton
|   +-- by-format/<format-id>/            [Phase 2+]
|
+-- schemas/
|   +-- _readme.md                        [Phase 0]
|   +-- neutral-model/                    [Phase 3+]
|
+-- prototypes/
|   +-- _readme.md                        [Phase 0]
|   +-- by-format/<format-id>/            [Phase 3+]
|
+-- src/
|   +-- python/
|   |   +-- _readme.md                    [Phase 0] Directory orientation (see note below)
|   |   +-- {format}/                     [Phase 4+] Python FOSS product per format (e.g. src/python/fods/)
|   +-- net/                              [Phase 4+] .NET product — not created until Phase 4
|   |   +-- {format}/                     [Phase 4+] .NET product workspace per format (e.g. src/net/fods/)
|   +-- dotnet/
|       +-- _readme.md                    [Phase 0] Transitional orientation — see note below
|
| NOTE: src/dotnet/ is a Phase 0 placeholder. The production .NET source will be created under
| src/net/{format}/ in Phase 4+. The src/dotnet/ directory will not contain product source.
| src/python/open-source/, src/dotnet/open-source/, src/dotnet/commercial/ are OBSOLETE target
| paths — they must not be created. Use format-first layout above.
|
+-- tests/
|   +-- _readme.md                        [Phase 0]
|   +-- fixtures/, oracle/, fuzz/         [Phase 3+]
|
+-- tools/
|   +-- _readme.md                        [Phase 0]
|   +-- llm/
|   |   +-- endpoints.yaml               [Phase 0] Config template
|   |   +-- (client scripts)             [Phase 1+ via TC-0005]
|   +-- spec-cache/
|   |   +-- _readme.md                   [Phase 0] Directory orientation
|   |   +-- (acquisition scripts)        [Phase 1+ via TC-0007]
|   +-- acquisition/                      [Phase 1+]
|   +-- scoring/                          [Phase 1+]
|   +-- validation/                       [Phase 2+]
|
+-- reports/
    +-- _readme.md                        [Phase 0]
    +-- security/, legal/                 [Phase 2+]
```

---

## Local-Only State — .local/ (Never Committed)

`.local/` is gitignored. It holds local-only artifacts that support reproducibility without committing transient state.

```
.local/
+-- llm-logs/                     JSONL agent run records (one per session)
+-- llm-cache/
|   +-- <format-id>/<task-id>.jsonl   Prompt/response pairs (hash only in committed files)
|   +-- full/<task-id>.jsonl          Full prompt/response text (privacy-sensitive)
+-- artifact-index.yaml           Index of all known artifacts with hashes and staleness
+-- discovered-models.yaml        Local LLM discovery cache (rebuilt after 24h)
+-- evidence-bundles/             Phase completion ZIP bundles for human upload
+-- spec-cache/                   Downloaded format specification files (local-only, never committed)
    +-- <format-id>/
        +-- <version>/
            +-- spec.pdf (or .html/.xml)
            +-- spec-index.yaml   Provenance, SHA-256, legal category, staleness flag
            +-- schemas/          Normative schema files if part of the spec
```

### Rebuilding .local/ After a Fresh Clone

If `.local/` is lost (fresh clone, machine migration):

1. `artifact-index.yaml` — rebuild by scanning committed file tree and computing hashes. An agent can do this by reading all committed artifacts and constructing index entries.
2. `discovered-models.yaml` — re-run endpoint discovery probe against well-known local ports.
3. `llm-logs/` and `llm-cache/` — these contain session-specific data. They cannot be fully rebuilt, but their loss does not block work. New sessions create new run records.
4. `evidence-bundles/` — bundles were already uploaded or handed off. They can be recreated by re-bundling committed artifacts.

The `.local/` directory is documented in Section F of the master plan and in `docs/llm-endpoint-strategy.md`.

---

## Agent Operations Backbone

### Primary Executor: Claude in VS Code

Claude is driven by:
- `AGENTS.md` — the non-negotiable operating contract
- Project commands in `.claude/commands/` — canonical behavior for recurring tasks
- Taskcards (`taskcards/TC-NNNN-*.md`) — atomic work units
- Gate definitions (`docs/gates.md`) — mandatory checkpoints
- The master plan (`plans/master-plan.md`) — current project state

### Governance Stack

```
AGENTS.md (non-negotiable rules)
  |
  +-- docs/gates.md (gate definitions and pass criteria)
  |
  +-- plans/master-plan.md (current operational state)
  |
  +-- taskcards/ (atomic work units)
  |
  +-- .claude/commands/ (consistent task invocation)
  |
  +-- .local/llm-logs/ (run record persistence)
```

### Phase Model

| Phase | Scope | Entry Condition |
|---|---|---|
| Phase 0 | Foundation: governance, policy, structure | First execution |
| Phase 1 | Gate 1 (scoring), endpoint implementation, commands | Phase 0 complete |
| Phase 2 | Gates 2-3 (evidence, samples) | Gate 1 passed for pilot |
| Phase 3 | Gates 4-9 (prototype through security review) | Gate 3 passed |
| Phase 4+ | Gates 10-11 (product build, release) | Gate 9 passed |

---

## Acquisition Pipeline Summary

Every format progresses through 11 gates before any product code is written. See `docs/gates.md` for full gate definitions and `docs/acquisition-workflow.md` for the stage-by-stage workflow.

| Gate | Name | Key Artifact |
|---|---|---|
| 1 | Candidate Accepted | Registry entry, scoring sheet |
| 2 | Evidence Complete | spec-evidence.md, legal-notes.md |
| 3 | Sample Corpus Ready | Samples with confirmed provenance |
| 4 | Prototype Complete | Working parser prototype |
| 5 | Neutral Model Defined | neutral-model schema |
| 6 | Oracle Comparison Complete | Comparison report |
| 7 | Fuzz Testing Complete | Fuzz report, fuzz seeds |
| 8 | Security Review Complete | Security report, sign-off |
| 9 | Product Mapping Complete | Tier mapping, delivery plan |
| 10 | OSS Readiness Complete | OSS product source, release manifest |
| 11 | Commercial Readiness Complete | Commercial product, commercial manifest |

---

## Artifact Model

### Committed vs. Local-Only vs. Never-Committed

| Category | Location | Committed | Rationale |
|---|---|---|---|
| Governance, plans, docs | Repo root + `docs/` + `plans/` | Yes | Authoritative, must be version-controlled |
| Registry | `registry/` | Yes | Authoritative project state |
| Taskcards | `taskcards/` | Yes | Work units, must be reproducible |
| Acquisition packs | `acquisition-packs/` | Yes | Evidence and notes |
| Samples (licensed) | `samples/by-format/` | Yes | Acquired artifacts |
| Schemas | `schemas/neutral-model/` | Yes | Authoritative design |
| Prototypes | `prototypes/by-format/` | Yes | Reference implementations |
| Product source | `src/` | Yes | Authoritative product |
| Tests | `tests/` | Yes | Authoritative test suite |
| LLM run records | `.local/llm-logs/` | No | Transient session state |
| Prompt/response cache | `.local/llm-cache/` | No | Privacy-sensitive, local-only |
| Artifact index | `.local/artifact-index.yaml` | No | Derived from committed state |
| Discovered models | `.local/discovered-models.yaml` | No | Transient, rebuilds automatically |
| Evidence bundles | `.local/evidence-bundles/` | No | Upload artifacts, regeneratable |
| Secrets | `.env` | Never | Credential security rule |

### Artifact Visibility

Every committed artifact must carry a YAML front matter block with a `visibility` field. Six classes: `public`, `internal`, `commercial`, `evidence-only`, `generated`, `blocked`. Default when uncertain: `internal`. Never default to `public`. See `docs/release-control.md` for the full schema and classification rules.

### Reuse-Before-Regenerate

Before creating any artifact, an agent checks `.local/artifact-index.yaml` for an existing entry. If the artifact exists and is current (source hash unchanged, not manually marked stale), the agent reuses it and logs `ARTIFACT_REUSED` in the run record. Only missing or stale artifacts are regenerated. See `docs/acquisition-workflow.md` for the full reuse policy.

---

## Security Architecture

All parsers produced by this system must conform to the threat model in `docs/security.md`. Eight threat categories apply: XXE, DTD entity expansion (billion laughs), zip bombs, path traversal, malformed file handling, memory limits, recursion limits, and binary parser safety. Security review (Gate 8) is mandatory before any format reaches product.

---

## Legal Architecture

All formats must be classified into one of six legal categories defined in `docs/legal-and-licensing.md`. Category 5 (reverse-engineered binary without permission) and Category 6 (blocked) are automatic rejects at Gate 1. All other categories require Gate 2 evidence review. Open-standard formats (Category 1) qualify for fast-path Gate 2 approval.

---

## LLM Architecture

Claude (VS Code) is the primary executor. `llm.professionalize.com`, local discoverable LLMs (Ollama, LM Studio), and Codex are secondary. All endpoint configuration is in `tools/llm/endpoints.yaml` (committed, no secrets). Secrets live in `.env` (gitignored). No LLM API calls are made in Phase 0. See `docs/llm-endpoint-strategy.md` for the full endpoint and model selection strategy.

---

## Commercial Isolation Architecture

The .NET commercial-tier source lives within `src/net/{format}/`. Commercial and FOSS tiers are isolated by:

1. Physical separation within the format workspace (mechanism defined at Phase 4 time — DEC-033 deferred).
2. Release manifests explicitly exclude `visibility: commercial` artifacts.
3. CI (Phase 4+) verifies no commercial namespace in the FOSS build output.
4. License headers distinguish commercial from FOSS files.

Commercial-tier source within `src/net/{format}/` is not created until Gate 10 has passed, Decision DD3 (commercial isolation) is resolved, commercial implementation taskcards exist, and an explicit commercial implementation execution prompt has been issued. Gate 11 is commercial release readiness, not creation authorization.

**Obsolete isolation model:** The old model used `src/dotnet/commercial/` and `src/dotnet/open-source/` as physically separate directories. This is replaced by the format-first layout. The exact isolation mechanism within `src/net/{format}/` is deferred to Phase 4 design.

---

## Autonomous Supervision Pipeline (Post-Phase-0)

The autonomous supervision system was built after Phase 0 to manage multi-sprint execution with bounded repair, evidence materialization, and governance enforcement.

### Pipeline Architecture

```
Sprint Start
  → Read session-resume.md (last sprint outcome)
  → Execute work items (format-specific code + tests)
  → Write evidence-declaration.yaml
  → Run autonomous_cycle.py:
      → Step 1: Validate declaration schema
      → Step 2: Inspect declared evidence
      → Step 2b: Generate/validate evidence manifest
      → Step 2c: Materialize declared evidence (SHA checksums)
      → Step 2d: Adoption compliance validation
      → Step 2e: Run governance validators (11 validators)
      → Step 3: Grade work items (ACCEPTED / ACCEPTED_WITH_REWORK / REJECTED)
      → Step 4: Generate next-sprint.md
      → Step 5: Update session-resume.md + approval-gates.md
      → Step 6: Write continuation-signal.json
  → Check continuation signal → repeat or stop
```

### State Management

| File | Purpose | Persistence |
|------|---------|-------------|
| `reports/supervisor/session-resume.md` | Last sprint outcome, test counts, supervisor mode | Committed |
| `.local/supervisor/continuation-signal.json` | Autonomous/manual flag, iteration count, stop reason | Local only |
| `reports/supervisor/approval-gates.md` | AUTONOMOUS_CONTINUE flag | Committed |
| `reports/supervisor/next-sprint.md` | Generated sprint prompt for next iteration | Committed |

**Cross-window recovery:** Any new session reads session-resume.md, approval-gates.md, and next-sprint.md to restore full operational context without requiring prior conversation history.

### 4-Stream Architecture

| Stream | Purpose | Key Artifacts |
|--------|---------|---------------|
| Mainstream Product | Format acquisition, parser development, gate progression | src/python/, tests/python/ |
| Acceleration | Rapid product function expansion across formats | product-task-candidates.json |
| Skills/Governed Execution | Repeatable skill patterns, governance enforcement | tools/supervisor/product_feature_factory.py |
| Supervisor/Autonomous Continuation | Pipeline orchestration, evidence, continuation | tools/supervisor/autonomous_cycle.py |

### Governance Validators (`tools/supervisor/governance_validators.py`)

11 validators that programmatically enforce governance rules:

1. **Execution method required** — Every work item must declare how it was executed
2. **Source diff required** — Product source items must have evidence of code changes
3. **Idempotency key required** — Repeatable items must have idempotency keys
4. **Replay recipe required** — Items claiming replayability must have a replay recipe path
5. **Claim classification** — Claims must be one of 6 valid classifications
6. **Legacy backfill validation** — Backfilled items must have proper attribution
7. **Manual ungoverned rejection** — MANUAL_UNGOVERNED execution method is blocked
8. **Governed direct execution** — Validates governed execution has proper evidence
9. **Source marker or sidecar** — Product functions must have attribution markers
10. **Taskcard state transitions** — State changes must follow the 15-state machine
11. **Route decision required** — Items must have autonomy routing decisions

### Bounded Repair Engine (`tools/supervisor/bounded_repair_engine.py`)

Classifies test and build failures into 6 categories and applies targeted repairs:

| Category | Detection | Repair Strategy |
|----------|-----------|-----------------|
| IMPORT | `ModuleNotFoundError`, `ImportError` | Fix sys.path or install missing dependency |
| SYNTAX | `SyntaxError` | Locate and fix syntax issue |
| ATTRIBUTE | `AttributeError` | Fix incorrect attribute access |
| NAME | `NameError` | Fix undefined name references |
| ASSERTION | `AssertionError` | Investigate test logic |
| TIMEOUT | Test timeout exceeded | Optimize or mark as slow |

Repairs are bounded to a maximum of 3 attempts per error. Automatic rollback on failure.

### Evidence Auto-Packager (`tools/supervisor/evidence_auto_packager.py`)

Generates ~80% of evidence-declaration.yaml automatically from the lane-execution-ledger.json, reducing manual declaration effort and preventing transcription errors.

---

## Relationship to Other Documents

- `plans/master-plan.md` — operational state (current phase, gate history, WIP)
- `docs/gates.md` — gate pass criteria and artifacts required
- `docs/acquisition-workflow.md` — stage-by-stage acquisition process
- `docs/product-tracks.md` — four track definitions, contamination prevention
- `docs/security.md` — parser threat model
- `docs/legal-and-licensing.md` — format legal classification
- `docs/release-control.md` — artifact visibility and release policy
- `docs/llm-endpoint-strategy.md` — LLM endpoint and credentials policy
- `docs/specification-cache.md` — specification cache policy and schema
- `AGENTS.md` — agent operating contract
