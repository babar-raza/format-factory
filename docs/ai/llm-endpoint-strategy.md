# LLM Endpoint and Model Strategy

**Document type:** Policy — Phase 0 Foundation
**Last reviewed:** 2026-05-04 (run013: date updated; repeatable agentic workflow section added)
**Authority:** This document governs how LLM endpoints are used, configured, discovered, and secured across all project phases.

---

## Purpose

The format-factory project uses LLM agents as the backbone of its acquisition workflow. Claude in VS Code is the primary executor. Codex is an optional secondary reviewer. Remote and local LLM endpoints are used for specialized and batch tasks. This document defines the rules for using these endpoints correctly, safely, and reproducibly — without leaking credentials, contaminating commits, or producing irreproducible results.

No real LLM API calls are made in Phase 0. This document defines the strategy that governs all subsequent phases.

---

## Supported Endpoint Classes

### 1. Agent-Native: Claude (Primary Executor)

Claude in VS Code is the primary agent executor for all project phases. It is driven through AGENTS.md, project commands (`.claude/commands/`), taskcards, and gates. Claude handles spec analysis, evidence drafting, scoring, prototype review, oracle comparison analysis, and master plan maintenance.

Authentication: `ANTHROPIC_API_KEY` environment variable (from `.env`, gitignored).

### 2. Agent-Native: Codex (Optional Secondary)

Codex (OpenAI API or GitHub Copilot agent mode) is an optional secondary agent. It may be used for .NET code review, neutral model schema cross-check, or prototype code review. Codex is activated only when explicitly instructed. All Codex output that enters the repository must be tagged `generated_by: codex` in the artifact's front matter.

Authentication: `OPENAI_API_KEY` environment variable (from `.env`, gitignored).

### 3. Remote Endpoint: llm.professionalize.com

A remote specialized LLM endpoint for batch processing, format analysis, or domain-specific tasks. Useful for large-scale spec parsing or when a specialized model is available there that is better suited to a task than Claude.

Authentication: `PROFESSIONALIZE_API_KEY` environment variable (from `.env`, gitignored).

### 4. Local Discoverable Endpoints

Local LLM services (Ollama, LM Studio, or custom) running on the developer's machine. Used for privacy-sensitive tasks, offline work, or when large-context local models are preferred. No authentication key required for most local services.

Discovery: Probe well-known ports (see endpoint discovery section below). Results cached in `.local/discovered-models.yaml` (gitignored, not committed).

---

## Endpoint Configuration

All endpoint configuration is stored in `tools/llm/endpoints.yaml` (committed, no secrets). This file records endpoint IDs, base URLs, and the environment variable name for the auth key. It never contains actual key values.

The actual key values live in `.env` (gitignored). `.env.example` lists the required variable names with empty values and is committed as a template.

**Rule:** No API key, token, or credential value may ever appear in a committed file. If a key is found in a committed file, it must be treated as compromised and rotated immediately.

---

## Local Endpoint Discovery Strategy

Implementation of endpoint discovery is deferred to Phase 1 (TC-0005). The strategy is:

1. Read `tools/llm/endpoints.yaml` for configured endpoints.
2. For entries with `discovery: true`, probe the configured URL with a lightweight health-check request.
3. If the probe succeeds, record the available models from the local service to `.local/discovered-models.yaml`.
4. If the probe fails, log `ENDPOINT_UNAVAILABLE: <endpoint_id>` in the run record and skip.
5. Re-run discovery if `.local/discovered-models.yaml` is missing or older than 24 hours.

The discovery cache (`.local/discovered-models.yaml`) is local-only and gitignored. It is regenerated on the next run if lost.

---

## Model Selection Strategy

Implementation of model selection is deferred to Phase 1 (TC-0005). The strategy is:

| Task Type | Preferred Model | Fallback |
|---|---|---|
| Spec analysis, evidence drafting | Claude (large) | professionalize.com |
| Prototype code review | Claude or Codex | Claude |
| Oracle comparison analysis | Claude | local model |
| Scoring calculation | Claude | local model |
| Batch sample analysis | local model | professionalize.com |
| Privacy-sensitive tasks | local model only | none — do not use remote |

Model selection rules will be codified in `tools/llm/model-selection.yaml` (Phase 1, TC-0005 scope). Agents must read that file before any LLM API call once it exists.

---

## Fallback Strategy

If the preferred model is unavailable:

1. Try the next model in priority order for the task type.
2. Do not use an unapproved model (one not listed in `tools/llm/model-selection.yaml` for that task type).
3. If no approved model is available, stop the current task and log: `ENDPOINT_UNAVAILABLE: <task_id>` in `.local/llm-logs/`.
4. Record the failure in the run record (see AGENTS.md Section B8).
5. Do not attempt the task with an unknown or unapproved model.

---

## Prompt and Response Persistence

LLM prompts and responses that produce acquisition evidence must be persisted locally for traceability and reuse:

- **Location:** `.local/llm-cache/<format-id>/<task-id>.jsonl` (gitignored, not committed)
- **Format:** JSONL, one entry per request/response pair
- **Required fields per entry:** `prompt_id`, `task_id`, `model`, `endpoint_id`, `timestamp`, `prompt_hash` (SHA-256 of prompt text), `response_hash` (SHA-256 of response text), `artifact_produced` (relative path)

Full prompt and response text may optionally be stored in `.local/llm-cache/full/<task-id>.jsonl` (also gitignored). Storage of full text is subject to the retention and privacy policy below.

Committed artifacts reference `prompt_id` and `response_hash` in front matter for traceability. They never contain full prompt or response text.

---

## Spec Content in LLM Prompts

Full specification documents must not be sent to remote LLM endpoints by default. The following rules govern use of spec content in prompts:

1. **Remote endpoint restriction:** Transmitting a full specification document to a remote LLM endpoint (including `llm.professionalize.com` and the Anthropic API) may implicate the spec's copyright and privacy terms. Full spec transmission requires: (a) legal review of the spec's redistribution and transmission terms, (b) explicit human authorization in the execution prompt, and (c) local-only storage of the resulting response.
2. **Prefer local LLM for spec analysis:** For tasks that require extensive spec content in the prompt, prefer a local LLM endpoint (Ollama, LM Studio) to avoid potential copyright or data transmission concerns. Local endpoints do not transmit data to third parties.
3. **Minimal excerpts only:** When citing spec content in prompts sent to remote endpoints, include only the minimum necessary excerpt (a specific clause, definition, or table). Do not include entire sections or chapters.
4. **Responses containing spec text:** If an LLM response quotes or paraphrases substantial spec content, that response defaults to `visibility: evidence-only` and must not be committed without legal review.
5. **Phase 0 restriction:** No LLM API calls are made in Phase 0. This applies to spec-related prompts as much as any other prompt.

---

## Prompt/Response Retention and Privacy Policy

1. **Retention period:** LLM prompt/response cache files in `.local/llm-cache/` are retained for the duration of the project phase in which they were produced. They may be deleted after the phase is complete and all artifacts have been validated.
2. **Privacy:** Prompts and responses may contain spec text, sample content, or other information that could have copyright or confidentiality implications. They must never be committed.
3. **LLM content with spec text:** Prompts or responses that contain substantial quoted spec text default to `evidence-only` visibility and may not be published without legal review. Large spec excerpts in prompt/response cache files must never be extracted and committed.
4. **No PII:** Prompts and responses must never contain personal data. If a sample being analyzed contains PII, it must be redacted before it is included in any prompt.
5. **Reproducibility:** A reviewer can verify artifact correctness using the `prompt_hash`, `response_hash`, the committed prompt template (in `.claude/commands/`), and the committed input artifact — without needing the full prompt text.

---

## Credential Security Rules

1. All API keys and tokens are stored in `.env` (gitignored). `.env` must never be committed.
2. `.env.example` lists required variable names with empty placeholder values. It is committed.
3. `tools/llm/endpoints.yaml` uses `auth_env` to reference the environment variable name, never the value.
4. Pre-commit inspection (manual in Phase 0; automated via hook in Phase 4+) must verify no key pattern appears in committed files before any commit is made.
5. If a key is accidentally committed, it is treated as compromised and must be rotated immediately. The commit must not be pushed.
6. CI workflows (Phase 4+) use GitHub Secrets for authentication, not `.env` files.

---

## Reproducibility Without Leaking Private Data

Reproducibility of LLM-assisted artifacts is achieved through:

1. `prompt_id` and `response_hash` in the artifact's front matter (traceability without content).
2. Prompt template committed in `.claude/commands/` (the template structure is public; the actual inputs are traceable via hashes).
3. Model ID and endpoint ID recorded in the run record (`.local/llm-logs/`).
4. Input artifacts (spec documents, sample files) committed with their own `source_hash`.

A reviewer can independently verify: "Given this model, this prompt template, and these input artifacts, is this output plausible?" without needing the raw prompt or response text.

---

## Phase 0 Deliverables

Phase 0 creates the following to avoid redesign:

| File | Purpose | Status |
|---|---|---|
| `docs/ai/llm-endpoint-strategy.md` | This document — strategy and policy | Created |
| `tools/llm/endpoints.yaml` | Endpoint config template, no secrets | Phase 0 |
| `.env.example` | Required variable name list | Created |
| TC-0005 taskcard | Governs Phase 1 implementation | Phase 0 |

No real API calls are made in Phase 0. No `tools/llm/` client scripts are created in Phase 0.

---

## Repeatable Agentic Workflow Requirement

Every agentic workflow route — regardless of which executor or endpoint is used — must produce reproducible, comparable results. This is a core design principle, not an implementation detail.

**Repeatability rules:**

1. **All routes follow the same AGENTS.md contract.** Claude, Codex, and any other executor must obey `AGENTS.md` without exception. There is no "Codex mode" or "offline mode" that bypasses gate rules, forbidden paths, evidence bundle requirements, or the no-commit rule.

2. **All routes produce the same artifact types.** Whether a task is run via Claude, Codex, Ollama, or llm.professionalize.com, the output must conform to the same evidence bundle structure, artifact-index schema, and run record format.

3. **Planning before implementation.** The correct order is: read master plan → read AGENTS.md → read memory → read taskcards → do the task → produce evidence → self-challenge → produce bundle. Speed must never be traded for correctness.

4. **Keys from system environment only.** No API key may be hard-coded, committed, or embedded in any command file. All keys are environment variables from `.env` (gitignored). See Credential Security Rules above.

5. **No endpoint calls in Phase 0.** This rule applies equally to Claude native mode, Codex, Ollama, and llm.professionalize.com. Phase 0 is governance-only. Real LLM API calls and endpoint probes begin in Phase 1.

---

## Implementation Deferral (TC-0005)

All implementation is deferred to Phase 1 via TC-0005:
- LLM endpoint client code in `tools/llm/`
- `tools/llm/model-selection.yaml`
- Artifact index bootstrap (`bootstrap-artifact-index.py` or equivalent)
- Local model discovery probe
- Run record writer

See [TC-0005](../taskcards/TC-0005-llm-endpoint-impl.md) for scope and acceptance criteria.
