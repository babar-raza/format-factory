---
artifact_id: TC-0005
artifact_type: taskcard
path: taskcards/TC-0005-llm-endpoint-impl.md
format_id: null
product_family: null
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: 2026-05-03
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: Implements LLM endpoint client. Resolves G-005, G-006, G-007, G-010, DEC-022.
---

# TC-0005: LLM Endpoint Client Implementation

**Phase:** 1
**Status:** not_started
**Owner:** TBD (developer)
**Created:** 2026-05-03
**Last updated:** 2026-05-03
**Blocking:** All LLM-assisted evidence work (Phase 2+). Artifact index reuse. Run record persistence.
**Blocked by:** Phase 0 completion; TC-0004 (commands must exist to record their use in run records)
**Format:** none (infrastructure)
**Gate:** none (enables all LLM-assisted work)

---

## Objective

Implement the LLM endpoint client in `tools/llm/` as specified in `docs/llm-endpoint-strategy.md`. This includes: the endpoint discovery probe, model selection reader, run record writer, artifact index bootstrapper, and a simple prompt/response cache writer. This resolves Gaps G-005 (endpoint discovery), G-006 (model selection), G-007 (artifact index), and G-010 (reuse tooling), and updates Decision DEC-022 to "implemented."

---

## Context

Phase 0 defined the LLM endpoint strategy (`docs/llm-endpoint-strategy.md`) and created the endpoint configuration template (`tools/llm/endpoints.yaml`). No client code was written in Phase 0 — that was explicitly deferred here via DEC-022. Before any Phase 2 LLM-assisted evidence gathering, the client must exist.

The key requirement from `docs/llm-endpoint-strategy.md`: agents must read `tools/llm/endpoints.yaml` and `tools/llm/model-selection.yaml` before any LLM API call, and must persist a run record in `.local/llm-logs/` for every LLM-assisted execution.

---

## Scope

### In scope

1. `tools/llm/model-selection.yaml` — model selection rules by task type (spec in doc/llm-endpoint-strategy.md Section D4)
2. `tools/llm/endpoint_client.py` — Python client that reads `endpoints.yaml`, probes local endpoints, selects model by task type, handles fallback
3. `tools/llm/run_record.py` — Python module to write JSONL run records to `.local/llm-logs/`
4. `tools/llm/prompt_cache.py` — Python module to write/read prompt-response JSONL cache in `.local/llm-cache/`
5. `tools/llm/artifact_index.py` — Python module to bootstrap `.local/artifact-index.yaml` from committed repo state and update it
6. Local endpoint discovery probe (Ollama at localhost:11434, LM Studio at localhost:1234)
7. `.local/` directory structure creation on first run

### Out of scope

- Full LLM API integration for spec analysis tasks (that is Phase 2 acquisition work)
- Implementing project commands (TC-0004)
- Release manifest generator (TC-0006)

---

## Acceptance Criteria

- [ ] `tools/llm/model-selection.yaml` created with task-type → model mappings
- [ ] `tools/llm/endpoint_client.py` created; reads `endpoints.yaml`; selects model by task type; handles fallback
- [ ] `tools/llm/run_record.py` created; writes valid JSONL run records with all required fields
- [ ] `tools/llm/prompt_cache.py` created; writes prompt-response pairs with hash fields; never stores full text without explicit flag
- [ ] `tools/llm/artifact_index.py` created; bootstraps `.local/artifact-index.yaml` from repo scan; updates on artifact creation
- [ ] Local endpoint discovery probe works: detects Ollama at localhost:11434 if running, records result to `.local/discovered-models.yaml`
- [ ] No secrets in any committed file; all auth via environment variables
- [ ] All modules have docstrings and error handling for endpoint-unavailable case
- [ ] G-005, G-006, G-007, G-010 marked resolved in `plans/master-plan.md`
- [ ] DEC-022 updated to "Phase 1: Implemented"
- [ ] Self-challenge completed (AGENTS.md Section I)

---

## Artifacts Produced

| Artifact | Path | Visibility | Notes |
|---|---|---|---|
| Model selection config | `tools/llm/model-selection.yaml` | internal | |
| Endpoint client | `tools/llm/endpoint_client.py` | internal | |
| Run record writer | `tools/llm/run_record.py` | internal | |
| Prompt cache | `tools/llm/prompt_cache.py` | internal | |
| Artifact index | `tools/llm/artifact_index.py` | internal | |

---

## Artifacts Consumed (Inputs)

| Artifact | Path | Required? |
|---|---|---|
| LLM endpoint strategy | `docs/llm-endpoint-strategy.md` | Required |
| Endpoint config | `tools/llm/endpoints.yaml` | Required |
| Release control schema | `docs/release-control.md` | Required (artifact-index schema) |

---

## Security Requirements

- API keys must be loaded from environment variables. Never hardcoded. Never logged.
- `endpoint_client.py` must read `auth_env` from `endpoints.yaml` and call `os.environ.get(<auth_env>)`.
- If an API key environment variable is not set, log a warning and skip that endpoint. Do not crash.
- Prompt and response text must never be written to committed files. Only `prompt_hash` and `response_hash` are committed.

---

## Steps

1. Read `docs/llm-endpoint-strategy.md` Sections D1-D9 thoroughly.
2. Create `tools/llm/model-selection.yaml` with task-type → model priority mappings.
3. Implement `tools/llm/endpoint_client.py`:
   - Read `endpoints.yaml`
   - For each `discovery: true` endpoint, probe the health endpoint
   - Select model for task type from `model-selection.yaml`
   - Implement fallback logic
   - Return endpoint URL and auth header (auth from env var, never logged or committed)
4. Implement `tools/llm/run_record.py` to write JSONL run records.
5. Implement `tools/llm/prompt_cache.py` with hash-only mode and optional full-text mode.
6. Implement `tools/llm/artifact_index.py` to bootstrap and update artifact index.
7. Test local endpoint discovery (probe localhost:11434 and localhost:1234).
8. Resolve gaps and update decisions in `plans/master-plan.md`.
9. Complete self-challenge.

---

## Completion Record

**Completed by:** (to be filled)
**Completion date:** (to be filled)
**Artifacts produced:** (to be filled)
**Gaps discovered:** (to be filled)
**Notes:** (to be filled)
