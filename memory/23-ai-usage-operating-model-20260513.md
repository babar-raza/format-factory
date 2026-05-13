# Memory 23: AI Usage Operating Model (2026-05-13)

## Event

Human (Babar Raza) explicitly authorized AI acceleration for commercial product work on 2026-05-13. LANE K documented the AI usage operating model across local repo authority files.

## Core Directive

**AI is authorized as an accelerator, not as authority.**

- AI should be used confidently for retrieval, synthesis, test generation, code drafting, review, and orchestration
- Authority remains: specs, verified facts, source code, deterministic tests, evidence bundles, gates, human decisions
- AI output must be validated before it influences authority files

## Key Facts for Future Agents

- **AI acceleration is authorized** — use it to go faster
- **Embeddings and LLMs are allowed** when useful, with provenance and logging
- **Local-first retrieval** — spec PDFs stay local; Tier 3 RAG not yet authorized for gate evidence
- **AI usage must be logged** in `.local/llm-logs/` (JSONL format) for repo-changing work
- **Commercial product direction:** load-edit-save-convert remains the target (C7+)
- **No gate approval via AI** — Gates 1-11 require human approval only
- **No secrets to AI** — credentials stay in `.env` and `.local/` only

## Existing AI Governance (Already in Repo — Do Not Duplicate)

The following already exists and is binding:
- AGENTS.md §H (LLM endpoint rules, credential security, run records)
- AGENTS.md §T (spec content in LLM prompts — restricted)
- AGENTS.md §V (DEC-034 independent verification)
- docs/llm-endpoint-strategy.md (full endpoint policy)
- docs/llm-and-embedding-strategy.md (allowed/prohibited uses, secrets)
- docs/spec-retrieval-strategy.md (three-tier retrieval)

## New Files Created in LANE K

| File | Purpose |
|------|---------|
| docs/ai-usage-operating-model.md | Core philosophy, allowed/prohibited uses, ledger, workflow, gate safeguards |
| docs/ai-usage-operating-model.yaml | Machine-readable policy |
| docs/ai-assisted-commercial-development.md | Patterns A-F for `src/net/{format}/` implementation |
| docs/ai-assisted-commercial-development.yaml | Machine-readable patterns |
| docs/spec-retrieval-and-rag-policy.md | RAG guardrails, provenance, embedding policy |
| docs/spec-retrieval-and-rag-policy.yaml | Machine-readable |
| docs/agent-swarm-ai-orchestration.md | AI lane governance in controlled swarms |
| 5 AI taskcards (AI-USAGE-OPERATING-MODEL, AI-SPEC-RETRIEVAL-RAG-POLICY, AI-COMMERCIAL-DEVELOPMENT-PATTERNS, AI-USAGE-LEDGER-AND-METRICS, AI-VALIDATION-GATES) | Implementation taskcards |

## Updates to Existing Files

- AGENTS.md: AF12 added (AI permitted/encouraged within governance)
- GOVERNANCE.md: 26.10 added (AI governance rule)
- memory/00-index.md: entry for memory/23 added

## AI Patterns for Future Implementation Sprints

Use Pattern A-F from `docs/ai-assisted-commercial-development.md`:
- A: spec-to-requirements extraction (local RAG → validated YAML)
- B: requirements-to-object-model (typed C# classes)
- C: object-model-to-code (implementation drafting)
- D: test generation (deterministic, must fail on broken impl)
- E: adversarial review (classified findings only)
- F: evidence summarization (coordinator verifies all claims)

## Future Prompt Guidance

Future sprints should include AI lanes where useful:
- LANE-SPEC: spec retrieval and requirement extraction
- LANE-MODEL: object model design proposals
- LANE-CODE: implementation drafting
- LANE-TEST: test generation
- LANE-REVIEW: adversarial review
- LANE-K: AI documentation (this lane)

Each lane must report: models used, calls made, outputs accepted/rejected, validation results.
