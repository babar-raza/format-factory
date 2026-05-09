---
memory_package: format-factory-chat-memory
created_at: 2026-05-09
source: ChatGPT AI design and state-management conversation
visibility: internal
publish_allowed: false
authority: context_only
generated_by: codex
supersedes: none
must_cross_check:
  - plans/master-plan.md
  - registry/format-registry.yaml
  - taskcards/
  - evidence bundles
  - docs/llm-and-embedding-strategy.md
  - docs/current-state-and-evidence-authority.md
---

# 15 - AI Modules and State Management Architecture, 2026-05-09

## Purpose

This file captures the current AI module and state-management architecture direction for Format Factory. It records design direction only. It does not implement AI modules, embeddings, workflow orchestration, product source, or a state manager.

## Core Principle

- LLMs are governed acceleration, not authority.
- AI proposes. Deterministic evidence decides.
- Embeddings retrieve cited artifacts, not truth.
- Agents execute through prompts, taskcards, playbooks, validators, and evidence bundles.
- Accepted outputs must be structured, schema-validated, provenance-backed, and tested.

## LLM Module Design

The planned governed LLM layer should live conceptually under `tools/llm/`. These modules are design direction and must not be treated as implemented unless the files actually exist in the repository.

```text
tools/llm/
  endpoints.yaml
  endpoint_client.py
  model_discovery.py
  model_registry.py
  router.py
  prompt_runner.py
  prompt_templates/
  response_schemas/
  run_ledger.py
  cache.py
  safety.py
  provenance.py
```

Expected responsibilities:

- `endpoint_client.py`: access approved endpoints only, using configured environment variables and redacted logs.
- `model_discovery.py`: discover available local and remote models when explicitly authorized.
- `model_registry.py`: store model capabilities, limits, supported task types, and task suitability.
- `router.py`: choose models by governed task type, fallback order, budget, and safety constraints.
- `prompt_runner.py`: enforce prompt templates, response schemas, retry rules, cache checks, and run logging.
- `response_schemas/`: validate model output before it is used by any downstream artifact.
- `run_ledger.py`: record model, endpoint, template, input hashes, output artifact, validation status, and timestamps.
- `cache.py`: avoid repeated calls for identical inputs and record cache provenance.
- `safety.py`: block secrets, raw copyrighted spec text, unapproved endpoints, unsupported tasks, and unsafe outputs.
- `provenance.py`: connect model output to source artifacts, source hashes, citations, taskcards, and evidence bundles.

No product or evidence claim should depend on raw model output alone. Model output is a proposal until converted into a structured artifact and validated.

## Approved LLM Use Cases

Future governed LLM use may include:

- FUL compilation support
- candidate fact extraction
- implementation requirement drafting
- parser strategy review
- test generation
- malformed fixture suggestion
- failure analysis
- repair suggestion
- evidence contradiction review
- review queue generation
- product source drafting from approved FUL only

Each use requires explicit sprint authorization, approved endpoint policy, schema validation, provenance, and deterministic verification.

## Forbidden LLM Use Cases

LLMs must not be used for:

- approving gates
- replacing evidence
- inventing facts
- bypassing validators
- storing raw secrets
- embedding raw copyrighted specs into evidence bundles
- generating product source from imagination
- promoting prototypes directly into product source
- treating embeddings as authority
- silently changing scope

## Embedding and Retrieval Design

Retrieval must remain deterministic first, lexical second, and embeddings third.

Tier order:

1. Deterministic lookup by known section, page, element, artifact ID, taskcard, or schema key.
2. Lexical lookup by explicit keyword, requirement ID, fact ID, or source path.
3. Embedding lookup for broader discovery when deterministic and lexical routes are insufficient.

Good embedding targets:

- normalized spec chunks
- section/page maps
- `verified-facts.yaml`
- `implementation-requirements.yaml`
- `parser-strategy.yaml`
- `security-surface.yaml`
- `product-readiness.yaml`
- oracle comparison notes
- approved sample descriptions
- test failure summaries
- prior repair attempts

Bad embedding targets:

- raw copyrighted full specs in evidence bundles
- unverified LLM outputs
- unclassified web downloads
- secrets
- temporary chat transcripts
- agent scratch files

Expected conceptual module layout:

```text
tools/retrieval/
  build_index.py
  query_index.py
  index_registry.yaml
  chunk_manifest.yaml
  provenance_map.yaml
  retrieval_report.py
```

Retrieval must always return source artifact path, source hash, chunk ID, retrieval method, and provenance. A retrieval hit is a pointer to evidence, not evidence by itself.

## Agent Design

Controlled agent roles:

- planning agent
- verification agent
- implementation agent
- repair agent
- memory-sync agent
- playbook agent
- review-queue agent

Agents must not roam freely. They must receive bounded sprint prompts, allowed and forbidden paths, taskcards, validation commands, evidence contracts, and stop conditions. Each sprint must produce an evidence bundle when execution mode creates or modifies artifacts.

## Source Generation Design

Source generation should use the Format Understanding Layer as prompt substrate.

For FODS Python, the substrate should include:

- `acquisition-packs/fods/format-profile.yaml`
- `acquisition-packs/fods/verified-facts.yaml`
- `acquisition-packs/fods/implementation-requirements.yaml`
- `acquisition-packs/fods/parser-strategy.yaml`
- `acquisition-packs/fods/security-surface.yaml`
- `acquisition-packs/fods/product-readiness.yaml`
- `schemas/neutral-model/fods/model.schema.json`
- approved samples and fixture summaries
- approved scope, such as Tiers 0-2
- forbidden behaviors
- test requirements

Acceptance chain:

1. LLM draft
2. static checks
3. unit tests
4. sample tests
5. malformed fixture tests
6. neutral model validation
7. security checks
8. evidence bundle
9. independent verification

## State Management Need

Format Factory needs a state manager. The current governance model is strong, but state is spread across registry entries, master-plan text, taskcards, FUL files, evidence bundles, docs, local metadata, and generated reports. Without a first-class state manager, agents can drift, stale claims can survive, and derived summaries can fall out of sync.

State management must cover five categories.

### 1. Authority State

- registry gate states
- master-plan phase state
- taskcard state
- product-source status
- FUL status

### 2. Execution State

- sprint ID
- stream ID
- current step
- completed steps
- failed steps
- resume points
- evidence outputs

### 3. Agent State

- agent role
- prompt ID
- files read
- decisions
- blocked items
- review queues

### 4. Retrieval State

- specs
- chunks
- verified facts
- embeddings
- indexes
- provenance maps

### 5. Evidence State

- bundles
- metadata
- validation results
- command outputs
- fingerprints
- final verdicts

## Format Factory State Manager

The subsystem name is:

```text
Format Factory State Manager
FFSM
```

FFSM is the repo-native domain state layer. It should not replace existing authority files. It should read, validate, snapshot, compare, and coordinate them.

Expected conceptual layout:

```text
tools/state/
  state_model.py
  state_snapshot.py
  state_transition.py
  state_fingerprint.py
  key_document_registry.py
  claim_linter.py
  derived_mirror_refresh.py
  state_ledger.py
```

Committed config:

```text
tools/state/key_document_registry.yaml
tools/state/state_transition_rules.yaml
tools/state/authority_model.yaml
```

Local runtime state:

```text
.local/state/current-state-snapshot.json
.local/state/state-transition-ledger.jsonl
.local/state/run-state/
```

Evidence outputs:

```text
bundle-metadata/current-state-snapshot-report.md
bundle-metadata/state-transition-report.md
bundle-metadata/key-document-registry-validation-report.md
bundle-metadata/no-drift-final-verdict.md
```

This is design direction, not implementation status.

## Minimum State Model

Conceptual entities:

### FormatState

Core fields: `format_id`, `family`, `current_gate`, `gate_statuses`, `approval_records`, `ful_status`, `product_source_status`, `blocked_by`, `next_allowed_action`.

### SprintState

Core fields: `sprint_id`, `stream_id`, `sprint_type`, `authorized_scope`, `forbidden_scope`, `status`, `started_at`, `completed_at`, `evidence_bundle`, `commit_hash`, `validation_results`.

### TaskcardState

Core fields: `taskcard_id`, `status`, `format_id`, `sprint`, `blocked_on`, `acceptance_criteria`, `validation_commands`, `completion_record`, `evidence_bundle`.

### ArtifactState

Core fields: `path`, `artifact_type`, `visibility`, `source_hash`, `generated_by`, `created_at`, `updated_at`, `dependencies`, `stale`, `validity_conditions`.

### AgentRunState

Core fields: `run_id`, `agent`, `role`, `prompt_id`, `files_read`, `commands_used`, `decisions`, `blocked_items`, `outputs`, `llm_calls`, `self_challenge`.

### RetrievalState

Core fields: `index_id`, `format_id`, `source_artifacts`, `source_hashes`, `chunk_ids`, `embedding_model`, `created_at`, `refresh_policy`, `query_log`, `provenance_map`.

## Transition Transactions

Important changes should go through transactions. A transaction should validate all related authority and mirror files before and after the change.

Example transition:

```text
gate_9 planning_ready to passed
```

Must update or verify:

- registry
- master plan
- taskcard
- `pack.yaml`
- `format-profile.yaml`
- `product-readiness.yaml`
- ROADMAP
- README if needed
- memory/09
- settings.json
- current-state snapshot
- state fingerprint
- evidence contract
- no-drift checks

This must not remain manual long term.

## Community Components

Use community-tested components around the repo-native state core.

Recommended usage:

- LangGraph for agent state, checkpointed flows, repair loops, review queues, and human-in-the-loop checkpoints.
- Prefect as the lighter early workflow orchestrator for Python jobs, validations, scheduling, and retries.
- Temporal later for durable long-running, distributed, retryable workflows.
- Dagster later if artifact lineage and asset dependency tracking become central.
- SQLite or JSONL for local state ledgers initially.
- Local retrieval index registry for embeddings and chunk provenance.

External components must not replace the authority model. Registry, master plan, taskcards, FUL, schemas, evidence bundles, and tests remain the explicit local authority layer.

## Practical Sequencing

Recommended sequence:

1. Format Factory State Core
2. key document registry
3. current-state snapshot generator
4. state transition dry-run tool
5. current-state claim linter
6. derived mirror refresh verifier
7. base no-drift evidence contract
8. LangGraph for agent state
9. Prefect or Temporal for workflow orchestration
10. retrieval and embedding registry
11. LLM run ledger


## Always-Updated Enforcement Model

Every execution sprint must include a mandatory closeout phase. The closeout phase is not
optional. It runs after all sprint work is complete and before the evidence bundle is built.

**Mandatory closeout steps for every execution sprint:**

1. Update all Level 6 session hint files to reflect the sprint's actual final state:
   - memory/09-current-state-before-phase1.md
   - .claude/settings.json
   - docs/fresh-chat-continuity-brief.md

2. If gate status changed: update registry/format-registry.yaml, plans/master-plan.md header,
   and all pack.yaml files for the affected format. All three must agree before bundle build.

3. If a new taskcard was created or completed: update plans/master-plan.md (taskcards table).

4. If ROADMAP.md or README.md are stale: update or create a pending-propagation report at
   reports/propagation/{sprint-id}-propagation-pending.md.

5. Run python tools/evidence/check_current_state_consistency.py before building the bundle.
   Expected: CURRENT_STATE_CONSISTENCY: PASS

6. If CURRENT_STATE_CONSISTENCY fails: fix the failing check before bundle build.

**Dirty-file classification labels for mixed-stream sprints:**

| Label | Meaning | Staging allowed? |
|---|---|---|
| MEMORY_SPRINT_OWNED | In scope for this memory sprint | Yes |
| MAIN_SPRINT_OWNED | Owned by active main sprint | No |
| SECONDARY_SPRINT_OWNED | Owned by active secondary sprint | No |
| UNKNOWN_REQUIRES_STOP | Cannot be classified | Stop immediately |

**FFSM role (future -- design only now):** When FFSM is operational, it will enforce the
always-updated model automatically. Until then, enforcement is manual through the sprint
closeout steps above and the CURRENT_STATE_CONSISTENCY check.

## Current Position

The project has strong governance and evidence controls. The next architecture step is to add a state manager and governed AI modules so AI accelerates work without causing drift or inconsistent outputs.
