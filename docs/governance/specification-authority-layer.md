# Specification Authority Layer

**Added:** 2026-06-04
**Authority:** plans/master-plan.md Section 44.2
**Source:** memory/67-local-memory-governance-sync-20260604.md Sections 2–3
**Status:** PLAN_NEEDS_REPAIR

## Purpose

Make huge file-format specs reliably usable by agents and LLMs without:
- Whole-spec prompt stuffing
- Ad-hoc browsing
- Memory-only claims
- Random snippets

## 11 Required Subsystems

| # | Subsystem | Purpose |
|---|---|---|
| 1 | SpecSourceRegistry | Register and version format spec sources |
| 2 | SpecVault | Store raw spec snapshots with provenance/checksum/license |
| 3 | SpecParser | Parse spec structure into section trees |
| 4 | SpecNormalizer | Normalize across spec formats |
| 5 | SpecIndexer | Index for retrieval |
| 6 | SpecDigestor | Generate summaries and digests |
| 7 | RequirementExtractor | Extract candidate requirements from specs |
| 8 | SpecVerifier | Verify requirements against source |
| 9 | RequirementGraph | Graph of requirements and relationships |
| 10 | ContextPackBuilder | Build deterministic context packs |
| 11 | SpecGovernanceRuntime | Enforce anti-bypass, staleness, authority rules |

## 13 Lifecycle States

```
source_candidate → registered_source → raw_snapshot → parsed_artifact →
normalized_artifact → indexed_artifact → digest_artifact →
candidate_requirement → verified_requirement → context_pack →
usage_record → coverage_record → refresh_event
```

## Deterministic Context Pack Contract

Same input → same output:
- Same source snapshots
- Same request
- Same index version
- Deterministic ranking/tie-breaks
- Timestamp isolation

Context packs must include a `manifest.sha256`. Context pack without `manifest.sha256` is rejected.

## Context Pack Multi-Resolution Structure

| Level | Content | Stuffed into Prompt |
|---|---|---|
| Raw snapshots | Full spec text | NEVER |
| Parsed section tree | Section hierarchy | Selectively |
| Chunks/tables | Spec subsections | Task-specific |
| Section summaries | Compressed overviews | Default |
| Subsystem summaries | Format-specific digests | Always |
| Format capsule | Minimal format descriptor | ALWAYS |
| Task context pack | Task-specific pack | ALWAYS |
| Implementation/test handoff | Code/test-ready pack | For implementation |

## Complete-Picture Policy

Every context pack includes:
1. Format capsule (ALWAYS — never dropped)
2. Spec/subtree outline
3. Task-specific requirements
4. Direct source chunks for critical rules
5. Unsupported/ambiguous areas
6. Edge cases
7. Open uncertainties
8. Retrieval log
9. Manifest hash

**If token budget exceeded:** Drop optional adjacent chunks first. NEVER drop requirement IDs, source refs, or format capsule.

## Usage Ledger

- Location: `.local/spec-usage-ledger/usage-YYYYMMDD.jsonl`
- Append-only
- Every context-pack build logs a row
- Every AI consumption logs a row
- Required fields: stream, task, context_pack_id, context_pack_hash, source_snapshots, requirement_ids, model, mode, prompt_path, output_path, validation_status, authority_state, stale_at_use
- Corrections use `correction_of` field

## Four-Stream Enforcement

| Stream | Required |
|---|---|
| Mainstream | handoffs must include `context_pack_id`, `requirement_ids`, `source_snapshot_ids` |
| Acceleration | outputs remain `ai_draft`, log `context_pack_id` and `usage_id` |
| Skills | templates/transcripts must include `context_pack_id`, `requirement_ids`, `usage_id` |
| Supervisor | validates claim support, stale packs, `ai_draft` misuse, false PASS prevention |

## Anti-Bypass Rules

| Bypass Attempt | Response |
|---|---|
| Ad-hoc URL citation (unregistered source) | REJECTED until source registered in SpecSourceRegistry |
| Memory-only spec claim | REJECTED |
| Raw AI summary without `source_refs` | Must run SpecVerifier |
| Unverified requirement used as fact | Remains `candidate_requirement` |
| Context pack without `manifest.sha256` | REJECTED |

## Pilot Scope

**Minimum (Phase 1):** ZST, Netpbm, DIF
**Extended (Phase 2):** Gnumeric, FODS/FODT/ODF

Rationale: Strong 3-format pilot is better than 5 shallow ingestions.
DIF/Gnumeric/ODF source licensing must be verified during execution. If unclear → raw snapshot quarantined + fetch-blocker documented.

## Current Plan Status

**Plan:** `ticklish-dancing-lobster(1).md`
**Review verdict:** PLAN_NEEDS_REPAIR
**Repair prompt:** `FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-HEALING-PLAN-REPAIR-001`

See memory/67-local-memory-governance-sync-20260604.md Section 3 for full repair checklist.
