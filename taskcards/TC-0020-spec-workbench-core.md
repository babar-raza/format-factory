---
artifact_id: TC-0020-spec-workbench-core
artifact_type: taskcard
path: taskcards/TC-0020-spec-workbench-core.md
format_id: null
product_family: null
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: "2026-05-06"
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "Spec Workbench core taskcard. Created run030 (2026-05-06). Governs the reusable Spec Consumption Workbench layer applicable to all formats. FODS v1 seeded in run030. TC-0021 handles FODS quality review independently."
---

# TC-0020: Spec Workbench Core (All Formats)

**Taskcard ID:** TC-0020
**Phase:** 3+ (applicable to all formats)
**Gate:** N/A — cross-gate infrastructure
**Status:** not_started
**Created:** run030 (2026-05-06)
**Format:** all formats (generic layer)
**Blocked by:** none — generic layer, format-independent

---

## Purpose

This taskcard governs the reusable Spec Consumption Workbench layer. The workbench converts large spec documents into structured, agent-consumable knowledge artifacts. It is format-independent infrastructure used by every gate that requires spec consultation.

The workbench architecture is documented in `docs/spec-consumption-workbench.md` (created run030).

---

## Scope

This taskcard covers the **generic** (cross-format) workbench infrastructure:

1. Workbench architecture document (`docs/spec-consumption-workbench.md`)
2. Core tooling (`tools/spec-normalize/`):
   - `build_spec_workbench.py` — builds workbench from normalized artifacts
   - `build_requirement_pack.py` — builds requirement packs (parser/sample/model)
   - `validate_requirement_pack.py` — validates provenance completeness
   - `export_task_packet.py` — exports concise gate-scoped task packets
3. Provenance schema (embedded in `docs/spec-consumption-workbench.md`)
4. Size rules for task packets (<200 lines per packet)
5. Refresh policy (re-seed from normalized artifacts on spec version change)
6. Gate mapping table (Gates 2-9 each have a packet type)

---

## Format-Specific Workbench Work

Format-specific workbench creation is NOT in this taskcard's scope. Each format gets its own workbench taskcard:

| Format | Workbench Taskcard | Status |
|---|---|---|
| fods | TC-0021 | not_started (quality review of v1 seeded run030) |
| (future formats) | TC-NNNN | not created yet |

---

## What Was Completed in run030

The following generic workbench infrastructure was created in run030 as part of the FODS Gate 4 sprint:

| Artifact | Status |
|---|---|
| `docs/spec-consumption-workbench.md` | CREATED — run030 |
| `tools/spec-normalize/build_spec_workbench.py` | CREATED — run030 |
| `tools/spec-normalize/build_requirement_pack.py` | CREATED — run030 |
| `tools/spec-normalize/validate_requirement_pack.py` | CREATED — run030 |
| `tools/spec-normalize/export_task_packet.py` | CREATED — run030 |

FODS workbench artifacts (local-only) also seeded in run030 — see TC-0021.

---

## Remaining Work (Scope of TC-0020 future execution)

1. **Multi-format validation**: Run workbench build for a second format (e.g., xlsx) to verify tools are not FODS-specific.
2. **Refresh tooling**: Implement `refresh_workbench.py` to detect spec version changes and re-seed affected artifacts.
3. **Coverage gap detection**: Implement automated detection of spec sections not covered by any requirement pack.
4. **Tier 3 retrieval integration**: When TC-0016 (vector index) is executed, integrate Tier 3 retrieval into `query_normalized_spec.py` and expose via workbench query tools.
5. **AGENTS.md Section Y**: Add workbench consumption rules (how agents use task packets vs raw spec text).

---

## Not in Scope

- FODS-specific workbench quality review (TC-0021)
- Gate approval decisions (human-only)
- Vector index (TC-0016)
- Spec retrieval evaluation (TC-0015)

---

## Status

**Current status:** in_progress (items 2 and 3 completed 2026-06-18; items 1 and 4 blocked)

### Completed Items
- Item 2: `refresh_workbench.py` implemented (TC0020-REFRESH-COVERAGE-TOOLS-20260618)
- Item 3: `detect_coverage_gaps.py` implemented (TC0020-REFRESH-COVERAGE-TOOLS-20260618)
- Item 5: AGENTS.md Section AH added (workbench consumption rules — TC-0020-AGENTS-AH-NDJSON-PROOF-20260618)

### Blocked Items
- Item 1: Multi-format validation — blocked by lack of normalized spec PDF for a second format
- Item 4: Tier 3 retrieval integration — blocked by TC-0016 (vector index, awaiting TC-0015)

---

## Revision History

| Run | Change |
|---|---|
| run030 | Taskcard created; generic workbench tooling and docs created as part of FODS Gate 4 sprint |
| 2026-06-18 | Items 2+3 completed: refresh_workbench.py + detect_coverage_gaps.py; Item 5 completed: AGENTS.md Section AH |
