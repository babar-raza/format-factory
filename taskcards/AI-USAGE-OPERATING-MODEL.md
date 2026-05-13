# Taskcard: AI-USAGE-OPERATING-MODEL

**Status:** completed
**Created:** 2026-05-13
**Sprint:** AI-USAGE-LOCAL-DOC-SYNC-20260513

## Purpose

Define durable repo rules for using AI safely and effectively as an accelerator for commercial product implementation.

## Scope

- Create `docs/ai-usage-operating-model.md` (philosophy, allowed/prohibited uses, ledger, acceptance workflow, gate safeguards)
- Create `docs/ai-usage-operating-model.yaml` (machine-readable policy)
- Ensure rules reference existing AGENTS.md §H/T/V/W/X and llm-endpoint-strategy.md without duplication
- Ensure capability model alignment (C0-C10)

## Non-Goals

- Implementing AI tools or infrastructure
- Replacing existing AGENTS.md/GOVERNANCE.md rules
- Defining pricing or model access contracts

## Acceptance Criteria

- [x] docs/ai-usage-operating-model.md exists
- [x] docs/ai-usage-operating-model.yaml exists
- [x] AI-as-accelerator philosophy documented
- [x] Allowed uses documented (12+ categories)
- [x] Prohibited uses documented (12+ categories)
- [x] Model endpoint policy documented (references llm-endpoint-strategy.md)
- [x] AI usage ledger format documented (JSONL)
- [x] AI output acceptance workflow documented (PROPOSED → ACCEPTED)
- [x] Gate safeguards documented (no AI gate approval)
- [x] Capability model aligned (C7+ for commercial readiness)

## Evidence Requirements

- Files exist and are internally consistent
- Cross-references to existing governance files verified
- No duplication of existing AGENTS.md/GOVERNANCE.md rules

## Files Allowed

- docs/ai-usage-operating-model.md (create)
- docs/ai-usage-operating-model.yaml (create)

## Prohibited Actions

- No code creation
- No gate status changes
- No removal of existing rules from AGENTS.md or GOVERNANCE.md

## Validation Required

- File existence
- Cross-reference consistency with AGENTS.md §H, §T, §V

## Next Dependency

- AI-COMMERCIAL-DEVELOPMENT-PATTERNS (parallel)
- AI-SPEC-RETRIEVAL-RAG-POLICY (parallel)
- Future implementation swarms reference this document
