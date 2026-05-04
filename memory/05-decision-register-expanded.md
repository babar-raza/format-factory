---
memory_package: format-factory-chat-memory
version: 1.0
created_at: 2026-05-03
intended_location: /memory
source: ChatGPT conversation memory plus inspected Phase 0 evidence bundles through run013
visibility: internal
publish_allowed: false
notes: Place this folder at repo root as /memory. These files are for agent context and must not supersede plans/master-plan.md.
---

# 05 — Expanded Decision Register

This decision log preserves the rationale behind major choices.

| ID | Decision | Status | Why |
|---|---|---|---|
| D-001 | “File format hacking” means legal parser/converter/acquisition work | Decided | Avoids unsafe interpretation. |
| D-002 | Build repeatable acquisition system, not one-off format hacks | Decided | Scales minor format support. |
| D-003 | Acquisition layer remains product-neutral | Decided | Reusable across Python OSS, .NET OSS, .NET commercial. |
| D-004 | Open-source Python product is required | Decided | Public adoption and minimal useful features. |
| D-005 | Open-source .NET product is required | Decided | .NET ecosystem adoption and shared base. |
| D-006 | Commercial .NET product is required | Decided | Full fidelity and enterprise features. |
| D-007 | Python commercial product deferred | Deferred | Avoid over-expansion before .NET commercial path proves itself. |
| D-008 | Feature tiers 0-4 are OSS ceiling by default | Decided | OSS should be useful but not full commercial fidelity. |
| D-009 | Feature tiers 5-6 are commercial by default | Decided | Full fidelity, edge cases, repair, optimization. |
| D-010 | Python package baseline is 3.11+ | Decided | Durable adoption; installed 3.13 is only local dev environment. |
| D-011 | .NET target strategy is net8.0/net10.0, not net9.0 | Decided | net9.0 near EOL; net8.0 and net10.0 are LTS strategy. |
| D-012 | Monorepo now, extraction-ready later | Decided | Keeps early work simple while allowing commercial split. |
| D-013 | Commercial folder deferred | Decided | Prevents public repo from implicitly becoming commercial repo. |
| D-014 | `plans/master-plan.md` is single living authority | Decided | Prevents operational state fragmentation. |
| D-015 | Claude in VS Code is primary executor | Decided | User’s main execution environment. |
| D-016 | Codex is optional reviewer/executor | Decided | Useful cross-check but not default driver. |
| D-017 | Endpoint support includes native Claude/Codex, `llm.professionalize.com`, local LLMs | Decided | Supports flexible agent/LLM workflows. |
| D-018 | Everything useful persists on disk | Decided | Enables reuse and prevents repeated work. |
| D-019 | `.local/` is local-only and gitignored | Decided | Stores caches, logs, bundles, discovered models. |
| D-020 | Visibility classification required for artifacts | Decided | Controls what can become open source. |
| D-021 | Phase 0 may use hybrid classification via artifact index | Decided | Avoids breaking syntax with front matter in config files. |
| D-022 | SQLite deferred | Decided | YAML sufficient for early artifact index. |
| D-023 | Commands directory exists in Phase 0, real commands Phase 1 | Decided | Establishes structure without overbuilding. |
| D-024 | LLM endpoint implementation is Phase 1 | Decided | Phase 0 is policy only. |
| D-025 | Release manifest generator is Phase 3+ | Decided | Needed before releases, not before acquisition. |
| D-026 | First pilot candidate is FODS | Decided as default | Formal scoring still pending. |
| D-027 | Specification Acquisition and Local Cache Layer required | Decided | Specs/materials must be fetched once, saved locally, indexed, and reused. |
| D-028 | Downloaded specs default to local-only | Decided | Avoids committing copyrighted/restricted standards. |
| D-029 | Spec-cache tooling is Phase 1 | Decided | Policy now, implementation later. |
| D-030 | No spec downloads in Phase 0 | Decided | Phase 0 is governance only. |
| D-031 | Gate 9 authorizes implementation planning, not source creation | Decided | Resolves Gate 9/Gate 10 contradiction. |
| D-032 | Gate 10 is OSS release readiness | Decided | Source exists before Gate 10; Gate 10 approves readiness. |
| D-033 | Gate 11 is commercial release readiness | Decided | Commercial source exists before Gate 11; Gate 11 approves readiness. |
| D-034 | Evidence bundle must be inspected before next prompt | Decided | Agent summaries repeatedly overstated completion. |
| D-035 | No commit unless human explicitly requests | Decided | Allows review before permanent repo history. |
| D-036 | /memory is context only, not operational authority | Decided (run010) | Prevents agents from overriding master-plan.md with stale memory. |
| D-037 | AGENTS.md must require agents to read /memory before complex tasks | Decided (run010) | Without explicit guidance, agents silently ignore memory. |
| D-038 | Memory updates or taskcards required after major project events | Decided (run010) | Prevents memory from diverging from repo state after transitions. |
| D-039 | Product source layout: src/net/{format} and src/python/{format} | Decided (propagated run011, confirmed run013) | Human stated flat format-keyed layout replaces old dotnet/python/open-source nesting. Propagated to master-plan.md v2.8 in run011; verified in run013. |
| D-040 | Repeatability over speed: every format must traverse the same 11-gate pipeline | Decided (run012) | Rushing a format skips gates and undermines the acquisition system's correctness guarantees. |
| D-041 | Spec-cache authorization model: downloads require explicit prompt authorization | Decided (run009) | Agents must never self-authorize a spec download. Missing specs create a gap, not an automatic fetch. |

## Pending decisions

| ID | Pending decision | Blocks |
|---|---|---|
| PD-001 | Neutral model schema language | Gate 5 |
| PD-002 | Commercial repo isolation model DD3 | Commercial source creation |
| PD-003 | Test frameworks | Phase 4 product tests |
| PD-004 | Versioning and release cadence | First release |
| PD-005 | Spec-cache implementation details | Phase 1 TC-0007 |
| PD-006 | Model selection config details | Phase 1 TC-0005 |
| PD-007 | .NET FOSS packaging: is it a separate OSS product or part of the commercial package? | Must resolve before Gate 10 .NET release (DEC-033 deferred) |
| PD-008 | ~~Exact source layout paths~~ | ~~run011 product source layout reconciliation~~ **RESOLVED run011**: src/net/{format}/ and src/python/{format}/ propagated to master-plan.md v2.8. |
