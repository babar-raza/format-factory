# Cross-Stream Adoption Enforcement (Skills R107)

## Purpose

Upgrade R106 enforcement rules from manually-verified to machine-checkable.
R107 wires transcript validation into the inspector, adds registry stability
tests, strengthens validator coverage, and ensures adoption enforcement is
testable -- not just documented.

## What Changed from R106

| Area | R106 State | R107 State |
|------|-----------|-----------|
| Transcript validation | Separate `validate_skill_transcript.py` call in grader | Inspector enriches inspection JSON with transcript fields (Lane B) |
| Registry stability | Manual `validate_claude_commands.py` check | Dedicated stability tests: no duplicates, active entries have command files, required fields non-empty (Lane C) |
| grade_item transcript handling | Grader had to locate and parse transcript independently | Grader reads pre-validated `transcript_found`, `transcript_valid`, `transcript_result` from inspector output (Gate S-08) |
| Source-edit transcript requirement | skill_id required (M-01), transcript required (M-05), but not co-located | New gate M-08 requires transcript evidence co-declared with source evidence on the same work item |
| POC skill reference | Not enforced | New gate A-07 requires POC items to declare `target_skill_id` referencing a registered skill |
| Validator coverage | Validators existed but limited test coverage | Lane F adds unit tests for all new enforcement assertions |

---

## R107 Lane Integration Map

| Lane | Contribution to Enforcement |
|------|----------------------------|
| **B (Inspector transcript enrichment)** | Inspector now extracts transcript fields and inlines them into inspection JSON. Eliminates redundant transcript parsing in grader. Enables gates S-02, S-08, M-05, M-08. |
| **C (Registry stability tests)** | Stability invariants (no duplicate skill_ids, active entries have command files, required_handoff_fields non-empty) are now tested. Enables gates S-06, A-02, A-07. |
| **E (This lane: adoption enforcement)** | Updated checklists with new gates (M-08, S-08, A-07). Cross-stream rules CSE-01 through CSE-06 now have testable assertions. |
| **F (Validator tests)** | Unit tests cover: grade_item with missing transcript => OVERCLAIMED; grade_item with transcript_result=FAIL => REWORK_REQUIRED; POC item with unknown target_skill_id => OVERCLAIMED. |

---

## Enforcement Rules (Cross-Stream)

### RULE CSE-01: Product Source Change Requires skill_id

- **What:** Any work item modifying `src/net/` or `src/python/` MUST declare `skill_id`.
- **How:** `grade_declared_work.py` reads `skill_id_present` from enriched inspection output.
- **Failure:** OVERCLAIMED -- "Product source changed without skill_id routing."
- **R107 change:** Inspector enriches with `skill_id_present` and `skill_id_registered` fields. Grader consumes directly.

### RULE CSE-02: skill_id Requires Valid Transcript

- **What:** Any work item with `skill_id` MUST have a corresponding valid transcript.
- **How:** Inspector enriches with `transcript_found`, `transcript_valid`, `transcript_result`. Grader reads these fields.
- **Failure:** Missing => OVERCLAIMED. Invalid => OVERCLAIMED. `result: FAIL` => REWORK_REQUIRED.
- **R107 change:** Inspector performs transcript discovery and schema validation during inspection pass, not during grading.

### RULE CSE-03: LIVE Source Edit Requires Ledger Entry

- **What:** Skill invocation in `mode: LIVE` editing source MUST reference `ledger_entry_id`.
- **How:** Grader reads `mode` from inspector-extracted transcript fields. Cross-references ledger.
- **Failure:** Missing => OVERCLAIMED. Mismatch => REWORK_REQUIRED.
- **R107 change:** Grader no longer re-parses transcript for mode -- reads from inspector enrichment.

### RULE CSE-04: Acceleration Must Not Edit Product Source

- **What:** Acceleration-tagged items MUST NOT have `src/` paths in evidence.
- **How:** `inspect_declared_evidence.py` scans paths. Supervisor gate S-07 enforces.
- **Failure:** REJECTED.
- **R107 change:** No structural change; retained from R106.

### RULE CSE-05: Acceleration Gap Selection Must Reference Matrix

- **What:** Handoffs MUST reference `gap_id` from `poc-targets.yaml`.
- **How:** Handoff YAML parsed; `gap_id` cross-referenced.
- **Failure:** OVERCLAIMED.
- **R107 change:** No structural change; retained from R106.

### RULE CSE-06: Supervisor Must Grade Transcript When Present

- **What:** Supervisor grading MUST validate and factor transcript results.
- **How:** `grade_declared_work.py` consumes `transcript_result` from inspector output.
- **Failure:** Grading incomplete; autonomous continue blocked.
- **R107 change:** Inspector enrichment makes this deterministic -- grader checks `transcript_found` field existence.

### RULE CSE-07: Source-Editing Items Require Co-Located Transcript (R107 NEW)

- **What:** Work items with `src/` evidence paths MUST also declare transcript evidence.
- **How:** Inspector checks that items with `src/` paths also have `**/skill-transcripts/*.json` in evidence_paths.
- **Failure:** OVERCLAIMED -- "Source-editing work item declared without transcript evidence."
- **Why:** Closes loophole where skill_id and transcript could be declared on different items.
- **Mainstream gate:** M-08.

### RULE CSE-08: POC Items Must Reference Registered Skills (R107 NEW)

- **What:** POC work items that will eventually require source changes MUST declare `target_skill_id`.
- **How:** Inspector checks POC-tagged items for `target_skill_id`; cross-references registry.
- **Failure:** Unknown skill => OVERCLAIMED. Missing field => ACCEPTED_WITH_LIMITATIONS.
- **Acceleration gate:** A-07.

---

## Grade Impact Matrix

| Violation | Grade Impact | Autonomous Repair? |
|-----------|-------------|-------------------|
| Source change without skill_id (CSE-01) | OVERCLAIMED | Yes -- add skill_id and transcript |
| Missing transcript for skill_id (CSE-02) | OVERCLAIMED | Yes -- write transcript |
| Invalid transcript schema (CSE-02) | OVERCLAIMED | Yes -- fix transcript |
| Transcript result=FAIL (CSE-02) | REWORK_REQUIRED | Yes -- fix code and re-run |
| Missing ledger for LIVE edit (CSE-03) | OVERCLAIMED | Yes -- create ledger entry |
| Acceleration direct source edit (CSE-04) | REJECTED | No -- must re-route |
| Handoff without matrix gap_id (CSE-05) | OVERCLAIMED | Yes -- add gap_id |
| Supervisor skips transcript grading (CSE-06) | Grading incomplete | Yes -- re-run grading |
| Source-edit without co-located transcript (CSE-07) | OVERCLAIMED | Yes -- add transcript to evidence |
| POC item with unknown target_skill_id (CSE-08) | OVERCLAIMED | Yes -- register skill or fix reference |
| POC item without target_skill_id (CSE-08) | ACCEPTED_WITH_LIMITATIONS | Yes -- add field |

---

## Validator Commands Reference

| Validator | Command | Exit 0 = Pass |
|-----------|---------|----------------|
| Transcript validator | `.local/venv/Scripts/python tools/supervisor/validate_skill_transcript.py <path>` | Valid transcript |
| Ledger validator | `.local/venv/Scripts/python tools/supervisor/validate_product_code_ledger.py` | Ledger consistent |
| Command validator | `.local/venv/Scripts/python tools/supervisor/validate_claude_commands.py` | All commands valid |
| Grading engine | `.local/venv/Scripts/python tools/supervisor/grade_declared_work.py --inspection <i> --declaration <d> --output-dir <o>` | Grade computed |

---

## Testable Enforcement Assertions (R107 NEW)

These assertions are the key R107 deliverable. Each is unit-testable.

| ID | Assertion | Expected Result | Test Location |
|----|-----------|-----------------|---------------|
| TE-01 | Inspection of skill_id item includes `transcript_found` | Field present in JSON | `tests/supervisor/` |
| TE-02 | grade_item with skill_id + transcript_found=false | Grade = OVERCLAIMED | `tests/supervisor/` |
| TE-03 | grade_item with transcript_result=FAIL | Grade = REWORK_REQUIRED | `tests/supervisor/` |
| TE-04 | grade_item with transcript_result=PARTIAL | Grade = ACCEPTED_WITH_LIMITATIONS | `tests/supervisor/` |
| TE-05 | src/ evidence without co-located transcript | Grade = OVERCLAIMED | `tests/supervisor/` |
| TE-06 | POC item with target_skill_id not in registry | Grade = OVERCLAIMED | `tests/supervisor/` |
| TE-07 | Registry has no duplicate skill_ids | validate_claude_commands exit 0 | `tests/supervisor/` |
| TE-08 | All active skills have command files | validate_claude_commands exit 0 | `tests/supervisor/` |

---

## Integration Timeline

- **R106:** Rules documented with validator commands. Enforcement manual.
- **R107 (this sprint):** Inspector enrichment wired (Lane B). Registry stability tested (Lane C). Adoption enforcement testable (Lane E). Validator tests added (Lane F).
- **R108+:** Pre-sprint pipeline runs all enforcement gates automatically before grading begins. Handoff validator (`validate_handoff.py`) implemented for A-01/A-03.

---

## Decision: ENFORCED and TESTABLE

All eight rules above are REQUIRED enforcement. R107 advances them from
"enforced by procedure" to "enforced by code with test coverage." If a rule
cannot be enforced in a given sprint, the item MUST declare
`skill_enforcement_bypass: true` with a documented reason, and the grade is
capped at `ACCEPTED_WITH_LIMITATIONS`.
