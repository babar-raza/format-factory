# AI Usage Operating Model

**Document type:** Normative operating model
**Authority level:** Authoritative — referenced by AGENTS.md and GOVERNANCE.md
**Created:** 2026-05-13
**Human authorization:** Explicit (Babar Raza, 2026-05-13) — AI acceleration authorized for commercial product work

---

## Core Philosophy

**AI is an accelerator, not authority.**

Repository authority comes from:
- Specifications (cached, provenance-verified)
- Verified local facts (schema-validated)
- Source code (in `src/`)
- Deterministic tests (passing, reproducible)
- Evidence bundles (built, validated)
- Gates (human-approved, 1-11)
- Human decisions (recorded in registry, master-plan, taskcards)

AI may contribute speed and quality to: retrieval, synthesis, design proposals, code drafting, test generation, adversarial review, gap analysis, summarization, sprint planning, and orchestration.

**AI output becomes authority only after validation, testing, and human or evidence-bundle acceptance.**

---

## Existing AI Governance (Do Not Duplicate)

The following files contain binding rules — reference them, do not restate:

| File | Covers |
|------|--------|
| AGENTS.md §H | LLM endpoint rules, credential security, run records |
| AGENTS.md §T | Spec-cache LLM restrictions, remote endpoint prohibition |
| AGENTS.md §V | Independent verification (DEC-034) — AI output must be verified |
| AGENTS.md §W | Spec normalization layer rules |
| AGENTS.md §X | Hybrid spec retrieval — deterministic-first hierarchy |
| docs/ai/llm-endpoint-strategy.md | Endpoint config, model selection, spec content in prompts, secrets |
| docs/ai/llm-and-embedding-strategy.md | Allowed/prohibited LLM/embedding uses, secret policy |
| docs/ai/spec-retrieval-strategy.md | Three-tier retrieval (deterministic → lexical → vector) |
| docs/planning-methodology.md §8 | LLMs under governance; verified facts remain authority |
| docs/agent-execution-handoff-standard.md §17-18 | LLM run records, declarations |

---

## Allowed AI Uses

AI may be used for all of the following (subject to validation):

**Retrieval and analysis:**
- Local spec search and retrieval (Tier 1-3 per docs/ai/spec-retrieval-strategy.md)
- Embeddings over normalized local artifacts
- Requirement extraction from spec sections
- Gap analysis against capability model or neutral model

**Design and drafting:**
- Object model design proposals (types, relationships, schemas)
- Save/serialization strategy proposals
- Conversion/export strategy proposals
- C# code drafting for `src/net/{format}/`
- Python code drafting for `src/python/{format}/`
- Test drafting (unit, round-trip, fuzz, export)
- Fixture generation ideas
- Documentation drafting

**Review and quality:**
- Adversarial review of proposed designs or code
- Security review (threat modeling, injection risk analysis)
- Evidence summarization for human review packets
- Taskcard and sprint planning generation

**Orchestration:**
- Lane planning for controlled swarm execution
- Dependency analysis for implementation order
- AI lane outputs fed to coordinator for validation

---

## Prohibited AI Uses

AI must NOT be used for:

| Prohibited Use | Why |
|---------------|-----|
| Gate approval | Gates 1-11 require human approval only |
| Human approval simulation | AI cannot substitute for Babar Raza's decisions |
| Unverified commercial readiness claims | Capability model requires test evidence |
| Final source-of-truth decisions | AI proposes; authority files decide |
| Secret handling | No API keys, tokens, or credentials through AI |
| Token logging/printing in committed files | Secrets must stay in `.env` and `.local/` |
| Hidden remote mutation | All AI calls must be logged |
| Unsourced spec claims | Every spec claim needs file path + page/section citation |
| Undocumented model calls for repo-changing work | Log format per AGENTS.md §H5 |
| Committing raw embeddings or vector DB files | Local working artifacts only |
| Committing raw long LLM transcripts | Sanitized summaries only |
| Using LLM output as proof without tests | AI proposals → tests → evidence |
| Broad refactors without evidence | Scope-controlled implementation sprints only |
| Replacing deterministic validation | Oracle, fuzz, round-trip tests are not replaceable |

---

## Model and Endpoint Policy

Full policy: `docs/ai/llm-endpoint-strategy.md`. Summary:

| Task Risk | Model Guidance |
|-----------|---------------|
| Low (summarization, formatting) | Cheapest adequate local or remote model |
| Medium (code drafting, test generation) | Claude Sonnet or equivalent |
| High (architecture, spec interpretation, adversarial review) | Claude Opus or strongest available |
| Spec analysis | Local model preferred; remote requires legal review |
| Commercial code drafting | Remote OK if no spec text transmitted |

- `llm.professionalize.com` — for stronger reasoning, architecture review, hard gap analysis if configured
- VS Code agents — lane workers for implementation tasks
- Local Ollama — cheap repetitive review, summarization, draft generation

Every model call for repo-changing work must produce a log entry in `.local/llm-logs/` (JSONL format, per AGENTS.md §H5).

---

## AI Usage Ledger

For any sprint using AI for repo-changing work, maintain:

**Per-call log** at `.local/llm-logs/<sprint-id>.jsonl`:
```json
{
  "timestamp": "2026-05-13T12:00:00Z",
  "sprint_id": "SPRINT-ID",
  "lane_id": "LANE-K",
  "tool_model": "claude-sonnet-4-6",
  "endpoint_category": "remote_claude",
  "purpose": "draft commercial object model for FODS",
  "input_artifacts": ["docs/product-factory/commercial-product-capability-model.md"],
  "output_artifacts": ["src/net/fods/Model/FodsSheet.cs"],
  "token_usage": {"input": 1200, "output": 800},
  "status": "ACCEPTED_AFTER_VALIDATION",
  "validation": "dotnet test — 12/12 PASS",
  "secret_safety": "PASS",
  "provenance_cited": true
}
```

**Per-sprint summary** at `reports/ai/ai-usage-summary-<sprint-id>.md`.

**AI output status values:**
- `PROPOSED` — not yet validated
- `ACCEPTED_AFTER_VALIDATION` — tests passed, artifact committed
- `ACCEPTED_WITH_MODIFICATION` — modified before acceptance
- `REJECTED_FALSE_POSITIVE` — AI finding was incorrect
- `REJECTED_UNSOURCED` — missing citation/provenance
- `REJECTED_FAILED_TESTS` — tests failed
- `DEFERRED_FOLLOWUP` — valid but out of current scope
- `NEEDS_HUMAN_REVIEW` — escalate to coordinator/human

---

## AI Output Acceptance Workflow

```
AI suggestion
  → local source/spec citation or product decision mapping
  → schema or structured artifact if applicable
  → implementation or test artifact
  → deterministic validation (compile + test + oracle if relevant)
  → evidence bundle inclusion
  → coordinator acceptance
  → authority file update if needed
```

No AI output may be cited as authority without completing this workflow.

---

## Capability Model Alignment

All AI-assisted implementation work for `src/net/{format}/` must target the capability model defined in `docs/product-factory/commercial-product-capability-model.md`:

- AI must not claim C-level advancement without test evidence
- AI-generated code at C4+ must demonstrate: load → object model → edit → save
- AI-generated export code must produce valid target-format output
- AI-generated test proposals must be deterministic (not flaky)
- Opaque node preservation must be tested explicitly

---

## Gate and Readiness Safeguards

- AI cannot approve gates
- AI cannot set `commercial_product_ready: true` in registry
- Gate 11 cannot be approved from parser/count extraction alone
- Current C2 success is NOT commercial readiness
- C4-C7 vertical slices demonstrate progress, not full product readiness
- Export/convert (C9) must be tested separately
- All gate work requires DEC-034 independent verification (separate session)

---

## Cross-References

- Capability model: `docs/product-factory/commercial-product-capability-model.md`
- Architecture: `docs/product-factory/commercial-dotnet-architecture.md`
- Retrieval/RAG: `docs/ai/spec-retrieval-and-rag-policy.md`
- Commercial patterns: `docs/ai/ai-assisted-commercial-development.md`
- Swarm orchestration: `docs/ai/agent-swarm-ai-orchestration.md`
- Full endpoint policy: `docs/ai/llm-endpoint-strategy.md`
- Embedding strategy: `docs/ai/llm-and-embedding-strategy.md`
