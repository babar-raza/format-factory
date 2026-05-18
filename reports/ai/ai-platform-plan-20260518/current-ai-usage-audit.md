# Current AI Usage Audit

**Date:** 2026-05-18

## Current AI Usage in Format Factory

### Active AI-Governed Work
- **Claude/Codex agents:** Used for sprint execution, code generation, evidence review. Governed by AGENTS.md, GOVERNANCE.md, DEC-034.
- **ChatGPT supervision:** Used for project analysis, sprint planning, prompt generation. Governed by docs/assistant-supervision-methodology.md.
- **No LLM endpoint calls to llm.professionalize.com** — zero calls made to date.
- **No embeddings created** — no vector stores exist.
- **No AI-generated code in product source** — all product code human/agent-written.

### Existing AI Governance Infrastructure
| Document | Purpose | Status |
|----------|---------|--------|
| docs/ai-usage-operating-model.md | Core operating model | Active |
| docs/ai-assisted-commercial-development.md | Commercial patterns A-F | Active |
| docs/spec-retrieval-and-rag-policy.md | RAG guardrails, tier 1-3 | Active |
| docs/agent-swarm-ai-orchestration.md | Lane governance | Active |
| docs/llm-endpoint-strategy.md | Endpoint policy (Phase 0) | Active |
| docs/llm-and-embedding-strategy.md | Backlog strategy | Superseded by docs/ai/ |
| AGENTS.md H, AF12-AF16 | Agent rules | Active |
| GOVERNANCE.md 26.10-26.14 | Governance rules | Active |

### AI Artifacts Currently in Repository
- Generated requirements: `generated-requirements/fods/`, `generated-requirements/fodt/` (schema-validated, verifier-reviewed, pending IV)
- Format understanding packages: FUL-001 (schemas), FUL-002 (FODS), FUL-003 (FODT)
- AI usage ledger: `reports/ai/ai-usage-ledger-commercial-load-save-20260513.jsonl`
- No LLM run logs in `.local/llm-logs/` (no calls made)
- No vector stores in `.local/ai/vector-stores/` (none created)

### Gaps Identified
1. No model discovery infrastructure
2. No role-based routing
3. No synthesis pipeline with citation verification
4. No embedding/retrieval infrastructure
5. No Agent Metrics integration
6. No runtime AI-free guard implementation
7. No golden evaluation framework
8. LLM-001 and EMB-001 taskcards stale (superseded)
