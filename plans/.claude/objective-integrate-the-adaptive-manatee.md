# Plan: Integrate Python Library Extraction Standard into Governance System

## Context

The file `independent-python-format-library-extraction-standard-v1.md` was an unmanaged root-level file — a Version 1.0 engineering contract governing the 10-stage lifecycle for extracting any Python format library from the Format Factory monorepo into a standalone repository. It needed to be relocated, registered, and enforced so that every future extraction automatically includes it and omission triggers a validation failure.

---

## Plan File Hardening Change Log

| Date | Change | Source |
|------|--------|--------|
| 2026-08-10 | Initial plan created | Plan mode exploration |
| 2026-08-10 | Sprint 1 executed: all 10 implementation steps completed | Execution session |
| 2026-08-11 | Plan hardened: audit findings incorporated, taskcards added for remaining gaps, gates and evidence contracts formalized | Evidence bundle + working-tree audit |

---

## Audit Findings Incorporated

Source: Evidence bundle (scratchpad `evidence-bundle.md`) + working-tree state audit 2026-08-11.

### Sprint 1 Audit Results

| Step | Item | Classification | Evidence |
|------|------|---------------|----------|
| 1 | File relocated to `docs/governance/python-library-extraction-standard.md` | completed_verified | Root file absent; new location confirmed (18127 bytes, SHA-256 `f4548b54...`) |
| 2 | Registered in `governance-binding.yaml` | completed_verified | `validate_governance_binding.py` → `[PASS]` for this entry |
| 3 | V_CERT_06 validator implemented | completed_verified | 5/5 unit tests PASS; live repo PASS; negative control FAIL |
| 4 | V_CERT_06 wired into runner | completed_verified | Full suite runs; V_CERT_06 present in output |
| 5 | Validator manifest updated (5→6) | completed_verified | `expected_count` derived correctly from manifest |
| 6 | V_CERT_06 registered in validator-id-authority | completed_verified | grep confirms entry |
| 7 | Extraction gate enriched | completed_verified | `extraction_standard_present`, `extraction_standard_sha256`, `governance_seed_files` added to output |
| 8 | State machine updated (CERTIFY→EXTRACT) | completed_verified | Transition row includes standard verification requirement |
| 9 | Knowledge contract updated | completed_verified | Two new rules in `python-production-package.yaml` |
| 10 | Tests written (5 cases) | completed_verified | 19/19 PASS in `test_governance_validators_certification.py` |

### Gaps Identified (not covered by Sprint 1)

| Gap ID | Description | Category |
|--------|-------------|----------|
| GAP-ES-001 | Changes not committed — all 10 files are uncommitted working-tree modifications | evidence_gap |
| GAP-ES-002 | No extraction-to-external-repository skill exists; propagation model is specified but not automated | implementation_gap |
| GAP-ES-003 | Extraction gate reports for 6 formats are stale (lack new `extraction_standard_*` fields) | artifact_freshness_gap |
| GAP-ES-004 | `docs/governance/python-library-extraction-standard.md` is untracked (not staged) | evidence_gap |
| GAP-ES-005 | No capability registry entry for this governance integration work | governance_gap |
| GAP-ES-006 | Pre-existing governance-binding hash mismatches for 5 other bound files | pre_existing_gap |

---

## Resolved / Preserved Work

All 10 implementation steps from Sprint 1 are verified in the working tree:

1. **File relocation:** Root file gone; `docs/governance/python-library-extraction-standard.md` exists (18127 bytes)
2. **Governance binding:** Entry with SHA-256 `f4548b54628cc7ada6b98936a47098d036cd92953c8be6cdc43527056b2b48db` and role `python_library_extraction_contract`
3. **V_CERT_06 validator:** `validate_extraction_standard_present` in `governance_validators_certification.py`
4. **Runner wiring:** Import + call in `governance_validator_runner.py` lines 1064-1082
5. **Manifest:** certification count: 6 with V_CERT_06 entry
6. **Authority:** V_CERT_06 registered in `validator-id-authority.yaml`
7. **Gate enrichment:** `independent_repository_extraction_gate.py` records standard evidence
8. **State machine:** CERTIFY→EXTRACT transition updated
9. **Knowledge contract:** Two extraction rules added
10. **Tests:** 5 V_CERT_06 tests in `test_governance_validators_certification.py` (19/19 PASS)

---

## Unresolved Work Register

| ID | Description | Status | Blocks Completion? |
|----|-------------|--------|--------------------|
| GAP-ES-001 | Commit all changes | not_attempted | Yes — changes exist only in working tree |
| GAP-ES-002 | Extraction-to-repo skill automation | follow_up | No — propagation model specified; automation is Wave 7 scope |
| GAP-ES-003 | Regenerate extraction gate reports with new fields | follow_up | No — pre-existing reports retain validity for original claim |
| GAP-ES-004 | Stage `docs/governance/python-library-extraction-standard.md` | not_attempted | Yes — file is untracked |
| GAP-ES-005 | No capability registry entry | follow_up | No — capability sync handles this via `/sync-capabilities` |
| GAP-ES-006 | Pre-existing binding hash mismatches | pre_existing_gap | No — out of scope for this plan |

---

## Taskcard Register

### TC-ES-001: Commit Integration Changes

- **Title:** Commit all extraction standard integration changes
- **Source audit finding:** GAP-ES-001, GAP-ES-004
- **Why it matters:** All implementation exists only in the working tree; a crash, reset, or checkout would lose everything
- **Current status:** CLOSED (commit 64c11db0af51186ecfa17f57b06d662656e3c1ab, 2026-08-11)
- **Priority:** P0 (blocks completion)
- **Lane owner:** SCM
- **Required work:**
  1. Stage `docs/governance/python-library-extraction-standard.md` (untracked → add)
  2. Stage the 9 modified files (governance-binding.yaml, governance_validators_certification.py, governance_validator_runner.py, validator-manifest.yaml, validator-id-authority.yaml, independent_repository_extraction_gate.py, STATE-MACHINE-AND-TASKCARD-PROTOCOL.md, python-production-package.yaml, test_governance_validators_certification.py)
  3. Do NOT stage unrelated dirty files (oracle reports, capability-layer reports, settings.json, etc.)
  4. Commit with message: `feat(governance): integrate python library extraction standard into enforcement system`
- **Required verification:** `git log -1 --stat` shows exactly the 10 target files
- **Required evidence:** Commit SHA
- **Acceptance criteria:** All 10 files committed; no unrelated files included
- **Stop conditions:** If `Bash(git commit *)` is denied by permissions, classify as `EXTERNAL_BLOCKER: git_commit_permission_denied`
- **Allowed actions:** `git add <specific-file>`, `git commit`
- **Forbidden actions:** `git add -A`, `git add .`, `git push`, staging unrelated files
- **Dependencies:** None
- **Closeout rules:** Commit SHA recorded; `git status` shows no dirty state for the 10 files

### TC-ES-002: Extraction-to-Repository Skill (Follow-Up)

- **Title:** Create governed skill for extracting a format library to a dedicated external repository
- **Source audit finding:** GAP-ES-002
- **Why it matters:** The propagation model specifies that `EXTRACTION-STANDARD.md` must be copied to extracted repos, but no skill automates this; it relies on manual execution during Wave 7
- **Current status:** CLOSED (deferred to Wave 7 — out of scope for this plan per closeout criteria)
- **Priority:** P2 (deferred — Wave 7 scope)
- **Lane owner:** Machinery / Skills
- **Required work:**
  1. Create `.claude/commands/extract-to-independent-repository.md`
  2. Register in `.supervisor/skill-registry.yaml`
  3. Implement propagation: copy `docs/governance/python-library-extraction-standard.md` → target repo `EXTRACTION-STANDARD.md`
  4. Verify SHA-256 of copied file matches `governance-binding.yaml` entry
  5. Record propagation evidence in extraction manifest
- **Required verification:** Pilot extraction on one format with standard propagation confirmed
- **Required evidence:** Skill transcript showing standard copied and hash verified
- **Acceptance criteria:** Skill exists, is registered, propagates standard, verifies hash
- **Stop conditions:** This is follow-up work for Wave 7; not required for current plan completion
- **Allowed actions:** Create skill, register, test
- **Forbidden actions:** Modify extraction standard content; bypass hash verification
- **Dependencies:** TC-ES-001 (changes must be committed first)
- **Closeout rules:** Skill registered and piloted; extraction manifest includes `governance_seed_files`

### TC-ES-003: Regenerate Extraction Gate Reports (Follow-Up)

- **Title:** Re-run extraction gate for 6 formats to populate new `extraction_standard_*` fields
- **Source audit finding:** GAP-ES-003
- **Why it matters:** Existing gate reports (ipynb, xliff, safetensors, ubl, nrrd, ora) lack the new `extraction_standard_present` and `governance_seed_files` fields; future audits may flag them as incomplete
- **Current status:** CLOSED (deferred — advisory enrichment, not required per closeout criteria)
- **Priority:** P3 (low — pre-existing reports remain valid for their original claim)
- **Lane owner:** Certification
- **Required work:**
  1. Run `python tools/certification/independent_repository_extraction_gate.py --format {fmt} --output reports/certification/{fmt}/independent-repository-extraction-gate.json` for each of: ipynb, xliff, safetensors, ubl, nrrd, ora
  2. Verify each output JSON contains `extraction_standard_present: true`
- **Required verification:** All 6 reports contain `extraction_standard_sha256` matching governance-binding entry
- **Required evidence:** 6 updated JSON report files
- **Acceptance criteria:** All 6 reports have `extraction_standard_present: true` and correct SHA-256
- **Stop conditions:** Build environment failure → classify as `BLOCKER: build_environment`
- **Allowed actions:** Run gate tool, inspect output
- **Forbidden actions:** Manually edit gate output JSON
- **Dependencies:** TC-ES-001
- **Closeout rules:** 6 reports regenerated and committed

---

## Lane Ownership

| Lane | Owner | Scope |
|------|-------|-------|
| SCM | Agent (SCM policy) | TC-ES-001: staging and committing |
| Governance | Agent | V_CERT_06 implementation, binding, manifest, authority (DONE) |
| Certification | Agent | TC-ES-003: gate report regeneration |
| Machinery / Skills | Agent | TC-ES-002: extraction skill creation |

---

## Gate Contract

### Gate: Extraction Standard Integration Complete

**Trigger:** All TC-ES-001 taskcards closed.

**Required evidence:**
1. `docs/governance/python-library-extraction-standard.md` exists at HEAD
2. `registry/governance-binding.yaml` contains entry with matching SHA-256
3. V_CERT_06 returns PASS against the repository
4. `validate_governance_binding.py` returns `[PASS]` for the standard entry
5. 19/19 tests pass in `test_governance_validators_certification.py`
6. Commit SHA recorded for the integration commit
7. Negative control: V_CERT_06 returns FAIL when file is absent

**Not required for this gate (follow-up):**
- Extraction skill (TC-ES-002) — Wave 7 scope
- Regenerated gate reports (TC-ES-003) — advisory enrichment
- Pre-existing binding mismatches (GAP-ES-006) — out of scope

---

## Evidence Contract

| Evidence Type | Source | Required For |
|---------------|--------|-------------|
| Unit test results (19/19 PASS) | `.venv/Scripts/pytest tests/supervisor/test_governance_validators_certification.py -v` | Gate |
| Live validator result (PASS) | V_CERT_06 against real repo | Gate |
| Negative control (FAIL) | V_CERT_06 against empty temp dir | Gate |
| Governance binding validation | `python tools/supervisor/validate_governance_binding.py` → `[PASS]` for standard entry | Gate |
| Full validator suite (no regression) | `run_all_governance_validators()` → V_CERT_06 PASS, count_delta unchanged | Gate |
| Commit SHA | `git log -1 --oneline` after TC-ES-001 | Gate |

---

## Verification Matrix

| Verification | Command | Expected Result | Status |
|-------------|---------|-----------------|--------|
| File exists at new location | `ls docs/governance/python-library-extraction-standard.md` | File present, 18127 bytes | PASS |
| Old file absent | `ls independent-python-format-library-extraction-standard-v1.md` | Not found | PASS |
| SHA-256 matches binding | `python -c "import hashlib; ..."` | `f4548b54...` | PASS |
| V_CERT_06 unit tests | `.venv/Scripts/pytest tests/supervisor/test_governance_validators_certification.py -v` | 19/19 PASS | PASS |
| V_CERT_06 live | Run against real repo | PASS | PASS |
| V_CERT_06 negative | Run against empty dir | FAIL (correctly detected) | PASS |
| Governance binding | `python tools/supervisor/validate_governance_binding.py` | `[PASS]` for standard | PASS |
| Full validator suite | `run_all_governance_validators({}, Path('.'))` | V_CERT_06 in results, count_delta unchanged at -9 | PASS |
| No stale references | `grep -r "independent-python-format-library-extraction-standard"` | No matches | PASS |
| Commit | `git log -1 --stat` | 10 files committed | PASS (64c11db0af, 2026-08-11) |

---

## Repair Loop

If any verification fails:
1. Read the failing validator/test output
2. Identify root cause (file missing, hash mismatch, import error, wiring gap)
3. Apply minimal targeted fix to the specific file
4. Re-run the failing verification
5. Re-run the full test suite to check for regressions
6. Update this plan's verification matrix status
7. Continue to next taskcard

If V_CERT_06 fails after commit:
1. Check if `governance-binding.yaml` hash matches the committed file
2. If file was modified during commit hooks, recompute SHA-256 and update binding
3. Re-run `validate_governance_binding.py` to confirm

---

## Anti-Overclaim Rules

1. **Tests are not proof of production behavior.** Unit tests for V_CERT_06 prove validator logic; they do not prove the extraction gate tool works end-to-end (that requires running it against a real format).
2. **Gate enrichment is not gate enforcement.** The extraction gate tool now *records* the standard's presence; it does not *block* extraction if the standard is absent. V_CERT_06 is the enforcement mechanism.
3. **Working-tree changes are not committed changes.** Until TC-ES-001 closes, all implementation exists only in the working tree and can be lost.
4. **State machine documentation is not state machine enforcement.** The CERTIFY→EXTRACT transition was updated in documentation only; no code enforces this transition requirement.
5. **Propagation model specification is not propagation automation.** TC-ES-002 documents what must happen; no skill automates it yet.
6. **Pre-existing gate reports are valid for original claims only.** The 6 existing `independent-repository-extraction-gate.json` reports prove build independence; they do not prove standard propagation.

---

## Closeout Criteria

This plan is **COMPLETE** when:
1. TC-ES-001 is closed (all 10 files committed)
2. All verification matrix entries show PASS
3. No unresolved P0 items remain in the taskcard register
4. Evidence bundle path is recorded

This plan has **FOLLOW-UP** items (not blockers):
- TC-ES-002 (extraction skill — Wave 7)
- TC-ES-003 (gate report regeneration — advisory)
- GAP-ES-006 (pre-existing binding mismatches — out of scope)

---

## Remaining True Blockers

| Blocker | Type | Resolution |
|---------|------|------------|
| TC-ES-001: Changes not committed | Requires SCM permission (git commit) | If permission denied → `EXTERNAL_BLOCKER: git_commit_permission_denied` |

No TRUE_EXTERNAL_GATEs identified. The commit is agent-owned per SCM policy (AGENTS.md §AG4). If the user's permission configuration blocks `git commit`, that is an external blocker requiring user action.

---

## Implementation Record (Sprint 1 — Completed 2026-08-10)

### Files Changed

| # | File | Change |
|---|------|--------|
| 1 | `docs/governance/python-library-extraction-standard.md` | NEW (relocated from root) |
| 2 | `registry/governance-binding.yaml` | Added binding entry |
| 3 | `tools/supervisor/governance_validators_certification.py` | Added V_CERT_06 validator |
| 4 | `tools/supervisor/governance_validator_runner.py` | Wired V_CERT_06 import + call |
| 5 | `tools/supervisor/validator-manifest.yaml` | certification count 5→6, added V_CERT_06 |
| 6 | `registry/governance/validator-id-authority.yaml` | Registered V_CERT_06 |
| 7 | `tools/certification/independent_repository_extraction_gate.py` | Added standard evidence fields |
| 8 | `plans/codex/handover/STATE-MACHINE-AND-TASKCARD-PROTOCOL.md` | Updated CERTIFY→EXTRACT transition |
| 9 | `.supervisor/knowledge/contracts/python-production-package.yaml` | Added 2 extraction rules |
| 10 | `tests/supervisor/test_governance_validators_certification.py` | Added 5 V_CERT_06 test cases |

### Evidence Bundle

`C:\Users\prora\AppData\Local\Temp\claude\c--Users-prora-OneDrive-Documents-GitHub-format-factory\bf29e67a-3d49-4ffa-a84d-657962452b7a\scratchpad\evidence-bundle.md`


<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-08-10T19:40:17.807727+00:00"
  locked_by: "fc8c551049fb"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
