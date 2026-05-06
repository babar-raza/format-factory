---
artifact_id: TC-0021-fods-workbench-quality-review
artifact_type: taskcard
path: taskcards/TC-0021-fods-workbench-quality-review.md
format_id: fods
product_family: cells
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
notes: "FODS Spec Workbench quality review taskcard. Created run030 (2026-05-06). Reviews the v1 workbench seeded from gate artifacts. Blocked by Gate 4 human approval (to ensure Gate 5 direction is confirmed before investing in richer extraction)."
---

# TC-0021: FODS Spec Workbench Quality Review

**Taskcard ID:** TC-0021
**Phase:** 3 (post-Gate 4 approval)
**Gate:** N/A — workbench quality review; feeds Gate 5
**Status:** not_started
**Created:** run030 (2026-05-06)
**Format:** fods
**Blocked by:** Gate 4 human approval (required before Gate 5 scope is confirmed)

---

## Purpose

The FODS Spec Workbench v1 was seeded in run030 using existing gate artifacts (`seeded_from_gate_artifacts` method). This taskcard governs an independent quality review of the v1 workbench to:

1. Verify that all 10 parser requirement claims in `requirement-packs/parser-requirements.yaml` are accurate and well-provenienced.
2. Verify that the 4 sample requirement claims in `requirement-packs/sample-requirements.yaml` match the actual sample files.
3. Identify gaps where the workbench does not yet cover required spec areas.
4. Propose richer extraction methods for future improvement (TC-0020 scope).

---

## Current Workbench State (run030 v1 Seed)

All workbench artifacts are local-only at `.local/spec-cache/fods/1.3/workbench/`:

| Artifact | State | Quality |
|---|---|---|
| `verified-facts.yaml` | 10 facts (FODS core facts) | v1 — seeded from spec knowledge |
| `requirement-packs/parser-requirements.yaml` | 10 requirements (PR-001..PR-010) | v1 — seeded from parser-requirements-draft.yaml |
| `requirement-packs/sample-requirements.yaml` | 4 requirements (SR-001..SR-004) | v1 — seeded from sample-requirements.yaml |
| `requirement-packs/model-requirements-draft.yaml` | 3 requirements (MR-001..MR-003-DRAFT) | v1 — placeholder draft |
| `task-packets/gate4-parser-packet.yaml` | 10 reqs (120 lines) | v1 — auto-generated from parser pack |
| `task-packets/gate3-sample-packet.yaml` | 4 samples (59 lines) | v1 — auto-generated from sample pack |
| `task-packets/gate5-model-packet-draft.yaml` | 3 draft reqs (44 lines) | v1 — draft only |
| `coverage/parser-coverage-matrix.yaml` | 10 × 4 matrix | v1 — auto-generated |
| `coverage/sample-coverage-matrix.yaml` | 4 × 4 matrix | v1 — auto-generated |

**Validation summary (run030):**
- `validate_requirement_pack.py` parser: 116/116 checks PASS
- `validate_requirement_pack.py` sample: 50/50 checks PASS
- `validate_requirement_pack.py` model: 39/39 checks PASS

---

## Quality Review Scope

### Phase A — Requirement Accuracy Review (independent agent)

For each of PR-001..PR-010:

1. Query the actual spec text using `query_normalized_spec.py` with the cited section and page.
2. Compare the requirement claim against the actual spec text.
3. Mark each requirement as: `verified_against_spec`, `needs_correction`, or `spec_text_absent`.
4. Update `requirement-packs/parser-requirements.yaml` verification_status for each requirement.

### Phase B — Sample Requirement Review

For each of SR-001..SR-004:

1. Read the actual sample file.
2. Compare the requirement claim against the actual sample XML structure.
3. Mark each requirement as: `verified_against_sample`, `needs_correction`, or `claim_too_vague`.

### Phase C — Coverage Gap Analysis

1. Identify spec sections in `sections.jsonl` that are not referenced by any requirement pack.
2. Identify ODF 1.3 element types in `chunks.jsonl` that are present in the spec but not covered by requirements.
3. Document gaps in a `coverage/gap-analysis.md` file (local-only).

### Phase D — Richer Extraction Proposal

1. Propose improved extraction methods for claims that are currently `seeded_from_gate_artifacts`.
2. Document proposed extraction methods in `coverage/gap-analysis.md`.
3. Create follow-up tasks (new taskcards) for any richer extraction work.

---

## Preconditions

1. Gate 4 approved by human (Babar Raza). TC-0021 should not invest in Gate 5 prep if Gate 4 is not confirmed.
2. FODS workbench v1 artifacts exist at `.local/spec-cache/fods/1.3/workbench/` (built run030).
3. Normalized spec artifacts exist at `.local/spec-cache/fods/1.3/normalized/` (built run025/run026).
4. `query_normalized_spec.py` is functional (verified run027).

---

## Deliverables

1. Updated `requirement-packs/parser-requirements.yaml` — verification_status upgraded from `draft` to `verified_against_spec` for confirmed requirements (local-only).
2. Updated `requirement-packs/sample-requirements.yaml` — verification_status upgraded similarly.
3. `coverage/gap-analysis.md` (local-only) — list of uncovered spec sections and proposed remediation.
4. Run030 (or later) update to `docs/spec-consumption-workbench.md` noting quality review complete.

---

## Not in Scope

- Gate 5 neutral model design (TC-0019)
- Vector index (TC-0016)
- Product source (`src/python/fods/`)
- Schema creation (`schemas/neutral-model/`)

---

## Status

**Current status:** not_started

Blocked by Gate 4 human approval. The v1 workbench seeded in run030 is usable for Gate 4 evidence but should be quality-reviewed before being used to drive Gate 5 requirements.

---

## Revision History

| Run | Change |
|---|---|
| run030 | Taskcard created; FODS workbench v1 seeded (local-only) |
