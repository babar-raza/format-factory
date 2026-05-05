---
artifact_id: TC-0014-fods-gate4-parser-prototype-planning
artifact_type: taskcard
path: taskcards/TC-0014-fods-gate4-parser-prototype-planning.md
format_id: fods
product_family: cells
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: "2026-05-05"
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "Gate 4 parser prototype planning taskcard for FODS. Created run026 (2026-05-05). NOT_STARTED — awaiting Gate 3 human approval and explicit Gate 4 execution prompt."
---

# TC-0014: FODS Gate 4 — Parser Prototype Planning

**Taskcard ID:** TC-0014
**Phase:** 4 (Gate 4 execution)
**Gate:** Gate 4 (Parser Prototype)
**Status:** not_started
**Created:** 2026-05-05 (run026)
**Created by:** claude-sonnet-4-6 (run026)
**Blocking:** Gate 4 approval
**Blocked by:** Gate 3 human approval (must pass first); then explicit Gate 4 execution prompt

---

## STOP — Authorization Required

**This taskcard must not be executed until:**
1. Gate 3 human approval is recorded in `registry/format-registry.yaml`
2. A human issues an explicit Gate 4 execution prompt naming TC-0014

Current state (as of run026):
- Gate 3: sample_corpus_created_pending_independent_verification
- Gate 4: not_started
- parser-requirements-draft.yaml: EXISTS (local-only, `.local/spec-cache/fods/1.3/normalized/`)

---

## Objective

Create a parser prototype for the FODS format that demonstrates correct reading of the 4 Gate 3 sample files. Gate 4 is the first gate where parser/prototype code is authorized. The prototype must read all sample files correctly and produce a normalized representation suitable for comparison with an oracle tool.

---

## Prerequisites

- [ ] Gate 3 PASSED — human approval recorded in registry/format-registry.yaml
- [ ] parser-requirements-draft.yaml reviewed and approved (local artifact upgraded to committed)
- [x] TC-0013 executed — 4 FODS samples exist in samples/by-format/fods/ (run026)
- [x] Spec Navigation Layer complete — sections.jsonl, chunks.jsonl, query tooling available (run026)
- [ ] Explicit Gate 4 execution prompt issued by human

---

## Context

Parser requirements draft (10 requirements) was produced in run026 at:
`.local/spec-cache/fods/1.3/normalized/parser-requirements-draft.yaml`

Key requirements for the parser prototype (from parser-requirements-draft.yaml):

| Req ID | Capability | Priority |
|---|---|---|
| PR-001 | Parse root `<office:document>` element | MUST |
| PR-002 | Validate FODS mimetype | MUST |
| PR-003 | Navigate `office:body > office:spreadsheet` | MUST |
| PR-004 | Enumerate `table:table` elements (sheets) | MUST |
| PR-005 | Read `table:table-row` elements | MUST |
| PR-006 | Read `table:table-cell` and typed values | MUST |
| PR-007 | Handle `table:number-columns-repeated` | MUST |
| PR-008 | Read string cell text from `<text:p>` | MUST |
| PR-009 | Read `table:formula` attribute | SHOULD |
| PR-010 | Register required XML namespaces | MUST |

All requirements are cited against ODF 1.3 spec sections.

---

## Scope

### In scope

1. Review and finalize `parser-requirements-draft.yaml` as a committed artifact
2. Create `prototypes/by-format/fods/` directory with Python parser prototype
3. Parser reads all 4 Gate 3 samples and produces JSON output
4. Validation: parser output matches expected cell values for all 4 samples
5. Document parser design decisions in `acquisition-packs/fods/parser-notes.md`

### Out of scope — FORBIDDEN

- Gate 4 self-approval — FORBIDDEN (human-only)
- Neutral model schema — FORBIDDEN (Gate 5)
- Product source (`src/`) — FORBIDDEN (Gate 9+)
- Oracle comparison — FORBIDDEN (Gate 6)
- Any parser work before Gate 3 is approved — FORBIDDEN

---

## Steps (to be executed after explicit Gate 4 prompt)

1. Read `AGENTS.md`, verify Gate 4 execution is authorized.
2. Read `plans/master-plan.md`, confirm Gate 3 PASSED.
3. Read `parser-requirements-draft.yaml` (local-only) and `docs/gates.md` Gate 4 criteria.
4. Create `acquisition-packs/fods/parser-notes.md` with parser design.
5. Commit `parser-requirements-draft.yaml` as a committed evidence artifact.
6. Create `prototypes/by-format/fods/` directory.
7. Write Python parser prototype in `prototypes/by-format/fods/fods_parser.py`.
8. Run prototype against all 4 Gate 3 samples. Document results.
9. Update registry gate_4 status to `prototype_created_pending_independent_verification`.
10. Request independent verification (DEC-034), then Gate 4 human approval.

---

## Acceptance Criteria

- [ ] `acquisition-packs/fods/parser-notes.md` — parser design document
- [ ] `parser-requirements.yaml` committed (finalized from draft)
- [ ] `prototypes/by-format/fods/fods_parser.py` — reads all 4 Gate 3 samples
- [ ] Parser output for each sample matches expected cell values
- [ ] Gate 4 stage in registry updated
- [ ] Independent verification sprint completed (DEC-034)
- [ ] Gate 4 human approval recorded

---

## Related Files

- `.local/spec-cache/fods/1.3/normalized/parser-requirements-draft.yaml` — draft requirements (local-only)
- `samples/by-format/fods/` — Gate 3 sample corpus (run026)
- `acquisition-packs/fods/sample-sources.md` — corpus plan
- `tools/spec-normalize/query_normalized_spec.py` — use to query spec during parser development
- `taskcards/TC-0013-fods-gate3-sample-corpus-execution.md` — Gate 3 parent
