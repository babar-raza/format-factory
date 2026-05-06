---
artifact_id: TC-0017-fods-gate4-parser-prototype-execution
artifact_type: taskcard
path: taskcards/TC-0017-fods-gate4-parser-prototype-execution.md
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
notes: "Gate 4 parser prototype execution taskcard for FODS. Created run028 (2026-05-05). EXECUTED run029 (2026-05-05): prototype created at prototypes/by-format/fods/fods_parser.py. Validation PT-001–PT-004 PASS (4/4). TC-0018 independent verification PASS run030 (2026-05-06). Status: COMPLETED. Gate 4 approved: false — human approval required."
---

# TC-0017: FODS Gate 4 — Parser Prototype Execution

**Taskcard ID:** TC-0017
**Phase:** 3 (Gate 4 execution)
**Gate:** Gate 4 (Parser Prototype)
**Status:** completed — prototype verified (TC-0018 PASS run030); human Gate 4 approval required
**Created:** 2026-05-05 (run028)
**Created by:** claude-sonnet-4-6 (run028)
**Executed:** 2026-05-05 (run029)
**Executed by:** claude-sonnet-4-6 (run029)
**Blocking:** Gate 4 approval
**Blocked by:** TC-0018 independent verification (DEC-034) + Gate 4 human approval

---

## Execution Status (run029)

**Authorization:** Explicit Gate 4 execution prompt issued by human (run029, 2026-05-05).

Execution state:
- Gate 3: PASSED (Babar Raza, 2026-05-05)
- TC-0014: planning_ready (Gate 4 planning package reviewed and authorized by run029 prompt)
- Gate 4: prototype_created_pending_independent_verification
- Prototype: `prototypes/by-format/fods/fods_parser.py` (created run029)
- Validation: PT-001 PASS, PT-002 PASS, PT-003 PASS, PT-004 PASS (4/4)
- Test plan discrepancies documented: PT-001 text prediction, PT-002 sheet name predictions, PT-003 date cell prediction — all noted in prototype-notes.md and parser-notes.md
- Next: TC-0018 independent verification (DEC-034), then Gate 4 human approval

---

## Objective

Implement the Gate 4 FODS parser prototype in `prototypes/by-format/fods/fods_parser.py`. The prototype must:
1. Read all 4 Gate 3 FODS samples correctly
2. Produce JSON output matching the expected values in `parser-test-plan.md`
3. Be documented in `parser-notes.md` with design decisions, limitations, and security baseline
4. Be independently verified (TC-0018 / DEC-034) before Gate 4 human approval is requested

---

## Prerequisites

- [x] Gate 3 PASSED — Babar Raza (2026-05-05, run028)
- [x] `parser-requirements.md` committed (run028)
- [x] `parser-scope.md` committed (run028)
- [x] `parser-test-plan.md` committed (run028)
- [x] `samples/by-format/fods/` — 4 samples with SHA-256 hashes (run026/run027)
- [x] Human reviews Gate 4 planning package (authorized by run029 execution prompt)
- [x] Explicit Gate 4 execution prompt issued by human (run029, 2026-05-05)

---

## Scope

### In scope

1. Create `prototypes/by-format/fods/` directory
2. Implement `prototypes/by-format/fods/fods_parser.py` (Python 3.11+, stdlib only)
3. Run prototype against all 4 Gate 3 samples; verify output matches test plan
4. Create `acquisition-packs/fods/parser-notes.md` with design decisions
5. Update registry `gate_4.status` to `prototype_created_pending_independent_verification`

### Out of scope — FORBIDDEN

- Gate 4 self-approval — FORBIDDEN (human-only)
- Neutral model schema (`schemas/neutral-model/`) — FORBIDDEN (Gate 5)
- Product source (`src/`) — FORBIDDEN (Gate 9+)
- Oracle comparison — FORBIDDEN (Gate 6)
- Formula evaluation — FORBIDDEN (out of prototype scope)
- Third-party XML libraries for parsing logic — FORBIDDEN (stdlib only for prototype)
- Any sample without gate 3 approval — FORBIDDEN

---

## Steps (to be executed after explicit Gate 4 execution prompt)

1. Read `AGENTS.md`, verify Gate 4 execution is authorized.
2. Read `plans/master-plan.md`, confirm Gate 3 PASSED and TC-0017 authorized.
3. Read `acquisition-packs/fods/parser-requirements.md`, `parser-scope.md`, `parser-test-plan.md`.
4. Read `docs/gates.md` Gate 4 criteria.
5. Use `query_normalized_spec.py` to query spec sections for any ambiguous requirements.
6. Create `prototypes/by-format/fods/` directory.
7. Implement `prototypes/by-format/fods/fods_parser.py`.
8. Run prototype against all 4 samples in `samples/by-format/fods/`.
9. Verify all PT-001 through PT-004 acceptance criteria pass.
10. Create `acquisition-packs/fods/parser-notes.md`.
11. Update registry `gate_4.status` → `prototype_created_pending_independent_verification`.
12. Request TC-0018 independent verification sprint (DEC-034).
13. After TC-0018 PASS: request Gate 4 human approval.

---

## Acceptance Criteria

- [x] `prototypes/by-format/fods/fods_parser.py` — reads all 4 Gate 3 samples (PASS, run029)
- [x] PT-001 through PT-004 all pass (4/4 PASS, run029)
- [x] `acquisition-packs/fods/parser-notes.md` — design decisions, limitations, security baseline (updated run029)
- [x] Registry `gate_4.status` updated — prototype_created_pending_independent_verification
- [ ] Independent verification sprint (TC-0018 / DEC-034) completed
- [ ] Gate 4 human approval recorded

---

## Related Files

- `acquisition-packs/fods/parser-requirements.md` — requirements (Gate 4 planning, run028)
- `acquisition-packs/fods/parser-scope.md` — scope and tier definition (Gate 4 planning, run028)
- `acquisition-packs/fods/parser-test-plan.md` — expected parse output (Gate 4 planning, run028)
- `samples/by-format/fods/` — Gate 3 sample corpus (run026)
- `tools/spec-normalize/query_normalized_spec.py` — use to query spec during implementation
- `.local/spec-cache/fods/1.3/normalized/` — normalized spec artifacts (local-only)
- `taskcards/TC-0014-fods-gate4-parser-prototype-planning.md` — planning parent
- `taskcards/TC-0018-fods-gate4-parser-prototype-verification.md` — DEC-034 verification (next)
