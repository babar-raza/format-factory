# AI Usage Documentation Gap Audit

**Sprint:** AI-USAGE-LOCAL-DOC-SYNC-20260513
**Date:** 2026-05-13

---

## Existing AI-Related Docs Found

| File | Coverage | Assessment |
|------|----------|-----------|
| AGENTS.md §H | LLM endpoint rules, credential security, run records in .local/llm-logs/ | AI_GUIDANCE_ALREADY_CORRECT |
| AGENTS.md §T | Spec-cache LLM restrictions, remote endpoint prohibition | AI_GUIDANCE_ALREADY_CORRECT |
| AGENTS.md §V | DEC-034 independent verification requirement | AI_GUIDANCE_ALREADY_CORRECT |
| AGENTS.md §W | Spec normalization layer rules | AI_GUIDANCE_ALREADY_CORRECT |
| AGENTS.md §X | Hybrid spec retrieval, deterministic-first (Tier 1→2→3) | AI_GUIDANCE_ALREADY_CORRECT |
| docs/llm-endpoint-strategy.md | Complete endpoint config, model selection, spec content policy, secrets, Phase 0 restriction | AI_GUIDANCE_ALREADY_CORRECT |
| docs/llm-and-embedding-strategy.md | Allowed/prohibited LLM/embedding uses, secret policy, backlog taskcards | AI_GUIDANCE_ALREADY_CORRECT |
| docs/spec-retrieval-strategy.md | Three-tier retrieval hierarchy, format isolation, local-first, provenance | AI_GUIDANCE_ALREADY_CORRECT |
| docs/planning-methodology.md §8 | "LLMs may assist under governance; verified facts remain authority" | AI_GUIDANCE_ALREADY_CORRECT |
| docs/agent-execution-handoff-standard.md §17-18 | LLM run records in .local/llm-logs/ (JSONL), final declarations | AI_GUIDANCE_ALREADY_CORRECT |
| memory/14 | AI supervision rules, three-pilot direction, what AI may/must not do | AI_GUIDANCE_ALREADY_CORRECT |
| memory/15 | AI module architecture, embedding retrieval design (design only, not implemented) | AI_GUIDANCE_ALREADY_CORRECT |
| reports/ai/ai-acceleration-plan-commercial-load-save-20260513.md | Existing AI usage plan from prior sprint | AI_GUIDANCE_ALREADY_CORRECT |
| reports/ai/ai-usage-ledger-commercial-load-save-20260513.jsonl | Existing usage ledger from prior sprint | AI_GUIDANCE_ALREADY_CORRECT |

---

## Gaps Found

| Gap | Severity | How Filled |
|-----|----------|-----------|
| No single "AI is authorized accelerator" explicit statement | Medium | Created docs/ai-usage-operating-model.md |
| No AI swarm orchestration guide | Medium | Created docs/agent-swarm-ai-orchestration.md |
| No RAG-specific policy (extending retrieval strategy) | Medium | Created docs/spec-retrieval-and-rag-policy.md |
| No commercial implementation AI patterns | High | Created docs/ai-assisted-commercial-development.md |
| AGENTS.md missing "AI permitted/encouraged" explicit rule | Low | AF12 added |
| GOVERNANCE.md missing AI governance rule | Low | 26.10 added |
| No AI usage ledger template | Medium | AI-USAGE-LEDGER-AND-METRICS taskcard (not_started) |
| No AI validation gates document | Medium | AI-VALIDATION-GATES taskcard (not_started) |

---

## Over-Cautious Rules (Unnecessarily Blocking)

**NONE FOUND.** Existing AI rules are appropriate. The "AI may not" prohibitions are necessary for gate integrity and evidence quality. No existing rule unnecessarily blocks useful AI work.

---

## Unsafe Rules (Giving AI Too Much Authority)

**NONE FOUND.** Existing rules correctly require: DEC-034 IV, human gate approval, spec citations, validated evidence. No existing rule grants AI authority over gates, registries, or human decisions.

---

## Recommended Corrections

All corrections were applied during this sprint:
1. Created comprehensive operating model synthesizing scattered principles
2. Added explicit "AI is accelerator, not authority" statement to AGENTS.md (AF12) and GOVERNANCE.md (26.10)
3. Created commercial implementation patterns (A-F) for `src/net/{format}/`
4. Created RAG-specific policy extending existing retrieval strategy
5. Created swarm orchestration guide for AI lanes

---

## Applied Corrections

| Correction | Applied | File |
|-----------|---------|------|
| AI operating model | YES | docs/ai-usage-operating-model.md |
| AI as accelerator statement | YES | AGENTS.md AF12, GOVERNANCE.md 26.10 |
| Commercial implementation patterns | YES | docs/ai-assisted-commercial-development.md |
| RAG policy | YES | docs/spec-retrieval-and-rag-policy.md |
| Swarm orchestration guide | YES | docs/agent-swarm-ai-orchestration.md |
