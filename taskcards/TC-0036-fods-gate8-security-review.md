---
artifact_id: TC-0036-fods-gate8-security-review
artifact_type: taskcard
path: taskcards/TC-0036-fods-gate8-security-review.md
format_id: fods
product_family: cells
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude-sonnet-4-6
generated_at: "2026-05-08"
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "FODS Gate 8 security review planning taskcard. Created run045 (2026-05-08) after Gate 7 PASSED. Planning only — execution requires explicit Gate 8 execution prompt. DEC-034 independent verification required before human sign-off."
---

# TC-0036: FODS Gate 8 — Security Review

**Taskcard ID:** TC-0036
**Phase:** 3 (Gate 8 — security review)
**Gate:** Gate 8
**Status:** not_started — awaiting explicit Gate 8 execution prompt
**Created:** 2026-05-08 (run045)
**Created by:** claude-sonnet-4-6 (run045)
**Prerequisite:** Gate 7 PASSED ✓ (Babar Raza, 2026-05-08, run045)
**Blocking:** Gate 8 human sign-off + DEC-034 independent verification

---

## STOP — Authorization Required

**This taskcard must not be executed until a human issues an explicit Gate 8 execution prompt.**

Per AGENTS.md: Gate 8 security review requires an explicit human prompt. This planning
document is created in run045, but execution is blocked until the next session with explicit
authorization naming Gate 8 and the FODS format.

Gate 8 requires a human security reviewer sign-off — it cannot be self-approved by an agent.

---

## Objective

Execute a security review of the FODS parser prototype against all applicable threat categories
from `docs/security.md`. Produce `reports/security/fods.md` with each threat category assessed
as mitigated, deferred, or not applicable. Request human sign-off on the completed report.

---

## Scope

### In scope

1. **Threat category assessment** — evaluate the FODS parser (`prototypes/by-format/fods/fods_parser.py`)
   against all threat categories in `docs/security.md`:
   - TC-1: XML External Entities (XXE) — applicable (FODS is XML)
   - TC-2: DTD and Entity Expansion (Billion Laughs) — applicable (FODS is XML)
   - TC-3: Zip Bombs / Decompression Limits — not applicable (FODS is flat XML, no ZIP)
   - TC-4: Path Traversal in Archive Formats — not applicable (FODS is not ZIP-based)
   - TC-5: Malformed File Handling — applicable (covered by Gate 7 — reference Gate 7 results)
   - TC-6: Memory Limits — applicable (large file / large in-memory parse)
   - TC-7: Recursion Limits — applicable (nested XML elements)
   - TC-8: Binary Parser Safety — not applicable (FODS is pure XML)

2. **Security report** — `reports/security/fods.md`:
   - One section per threat category
   - Status: mitigated | deferred | not-applicable
   - Evidence of mitigation (or rationale for deferral)
   - Residual risks documented
   - Sign-off field for human reviewer
   - Cross-reference to Gate 7 fuzz results (TC-0033)

3. **DEC-034 independent verification** — separate sprint required before human sign-off:
   - All 8 threat categories assessed
   - No unacceptable residual risks present
   - Report structure conforms to `docs/security.md` requirements

### Out of scope — FORBIDDEN

| Item | Reason | Gate |
|---|---|---|
| Product source code | Gate 10+ | `src/python/fods/`, `src/net/fods/` |
| Gate 8 self-approval | Human sign-off required | — |
| Product security hardening | Gate 10+ (prototype review only) | — |
| New neutral model fields | Requires separate TC | — |
| CI workflows | Gate 10+ | — |
| reports/legal/ | Not Gate 8 scope | — |
| schemas/neutral-model/fods/ modifications | Gate 5 complete, no changes | — |

---

## Execution Plan

### Step 1: Read parser prototype
- Read `prototypes/by-format/fods/fods_parser.py` in full
- Read `docs/security.md` threat categories
- Read `acquisition-packs/fods/gate7-malformed-fuzz-report.md` (Gate 7 evidence)

### Step 2: Assess each threat category
For each of TC-1 through TC-8:
- Examine the parser code for the threat
- Determine status: mitigated | deferred | not-applicable
- If mitigated: cite specific code (line numbers and mechanism)
- If deferred: state rationale and phase when it will be addressed
- If not-applicable: state why

### Step 3: Write security report
- Create `reports/security/fods.md` with front matter and sign-off field
- Include: threat matrix table (8 rows), per-category sections, residual risk summary
- Include Gate 7 cross-reference: GATE7_FUZZ_TEST PASS 18/18

### Step 4: DEC-034 sprint
- Create `taskcards/TC-0038-fods-gate8-dec034-verification.md` (separate session)
- Execute TC-0038 in a separate session before requesting human sign-off

### Step 5: Human sign-off
- Present `acquisition-packs/fods/gate8-human-review-packet.md` to human
- Record approval: `approved_by`, `approved_date`, sign-off in report

---

## Related Files

- `docs/security.md` — threat categories TC-1 through TC-8
- `acquisition-packs/fods/gate8-security-plan.md` — execution plan detail (run045)
- `prototypes/by-format/fods/fods_parser.py` — prototype to review
- `acquisition-packs/fods/gate7-malformed-fuzz-report.md` — Gate 7 fuzz evidence
- `reports/security/` — target directory for security report

---

## DEC-034 Requirement

Per DEC-034 and AGENTS.md Section V: after Gate 8 execution, a separate independent
verification sprint (TC-0038) must be run before Gate 8 is submitted for human sign-off.

TC-0038 will be created when Gate 8 execution begins. It must run in a separate session
from the Gate 8 execution session.

---

## Expected Deliverables

| Artifact | Path | Notes |
|---|---|---|
| Security report | `reports/security/fods.md` | All 8 threat categories; sign-off field |
| Human review packet | `acquisition-packs/fods/gate8-human-review-packet.md` | Summary + DEC-034 table |
| DEC-034 verification taskcard | `taskcards/TC-0038-fods-gate8-dec034-verification.md` | Separate session |
| Registry update | `registry/format-registry.yaml` gate_8 | After human sign-off |
| Pack update | `acquisition-packs/fods/pack.yaml` gate_8 | After human sign-off |
