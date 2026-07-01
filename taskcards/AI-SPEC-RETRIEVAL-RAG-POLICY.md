# Taskcard: AI-SPEC-RETRIEVAL-RAG-POLICY

**Status:** completed
**Created:** 2026-05-13
**Sprint:** AI-USAGE-LOCAL-DOC-SYNC-20260513

## Purpose

Define embeddings/RAG use over local specs and normalized artifacts, extending the existing three-tier retrieval strategy with AI-specific guardrails.

## Scope

- Create `docs/ai/spec-retrieval-and-rag-policy.md` (RAG guardrails, provenance requirements, embedding policy)
- Create `docs/ai/spec-retrieval-and-rag-policy.yaml` (machine-readable)
- Extend (not replace) docs/ai/spec-retrieval-strategy.md
- Document Tier 3 vector/RAG as NOT YET AUTHORIZED for gate evidence

## Non-Goals

- Implementing embedding infrastructure (authorized separately via taskcards TC-0015/TC-0016)
- Changing existing retrieval hierarchy
- Authorizing Tier 3 RAG for gate evidence

## Acceptance Criteria

- [x] docs/ai/spec-retrieval-and-rag-policy.md exists
- [x] docs/ai/spec-retrieval-and-rag-policy.yaml exists
- [x] Tier authorization table documented (T1 YES, T2 YES, T3 NO for gate evidence)
- [x] Local spec artifacts documented (path, provenance, immutability)
- [x] RAG guardrails documented (7 rules)
- [x] Provenance requirements documented (required YAML fields)
- [x] Embedding policy documented (allowed sources, prohibited, local storage)
- [x] RAG output lifecycle documented

## Evidence Requirements

- Files exist and consistent with docs/ai/spec-retrieval-strategy.md
- No contradiction with AGENTS.md §T9

## Files Allowed

- docs/ai/spec-retrieval-and-rag-policy.md (create)
- docs/ai/spec-retrieval-and-rag-policy.yaml (create)

## Prohibited Actions

- No authorizing Tier 3 RAG for gate evidence
- No committing vector indexes
- No code creation

## Validation Required

- Consistency check with AGENTS.md §T9 (no spec to remote without authorization)
- Consistency check with docs/ai/spec-retrieval-strategy.md (tier hierarchy preserved)

## Next Dependency

- Embedding infrastructure taskcards (TC-0015, TC-0016) — separate human authorization
