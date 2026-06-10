# Supervisor Adoption Checklist (Skills R107) -- Enforcement Gates

This checklist supersedes the R106 version. All R106 gates are retained.
R107 additions are marked with **(R107 NEW)** and represent concrete wiring
of transcript validation into the inspector and grader, making enforcement
machine-checkable rather than procedural.

---

## GATE S-01: Detect skill_id in Work Items (REQUIRED)

- **What:** During grading, check each work item for a `skill_id` field.
- **How:** `grade_declared_work.py` reads `item_inspection["skill_id"]` from the inspection JSON. If the field is present, gates S-02 through S-04 activate.
- **Integration:** `inspect_declared_evidence.py` propagates `skill_id` from the evidence declaration into the inspection output.
- **Failure:** If `skill_id` is present but not processed, grading is incomplete. `autonomous_cycle.py` self-audit detects unprocessed skill_ids.
- **Responsible:** Supervisor grading pipeline.

---

## GATE S-02: Validate Transcript (REQUIRED when skill_id present)

- **What:** Locate and validate the skill transcript for any work item with `skill_id`.
- **How:** Search `evidence_paths_found` for files matching `**/skill-transcripts/*.json`. Call `validate_skill_transcript.py` on each match.
- **Validator:** `validate_skill_transcript.py` -- exit 0 = valid.
- **Command:** `.local/venv/Scripts/python tools/supervisor/validate_skill_transcript.py <path>`
- **Grade mapping:**

| Transcript State | Supervisor Grade |
|-----------------|-----------------|
| No transcript found | OVERCLAIMED |
| Transcript exists, schema invalid | OVERCLAIMED |
| Transcript valid, `result: PASS` | Eligible for ACCEPTED_VERIFIED |
| Transcript valid, `result: FAIL` | REWORK_REQUIRED |
| Transcript valid, `result: PARTIAL` | ACCEPTED_WITH_LIMITATIONS |

- **Failure:** Supervisor ignores present transcript => grading incomplete => autonomous continue blocked.
- **Responsible:** Supervisor grading pipeline (`grade_declared_work.py`).

### R107 Inspector Enrichment (R107 NEW)

- `inspect_declared_evidence.py` now performs transcript discovery as part of
  its standard inspection pass. For each work item with `skill_id`, it:
  1. Scans `evidence_paths_found` for `**/skill-transcripts/*.json`.
  2. If found, reads the JSON and extracts `result`, `mode`,
     `actual_files_changed`, and `tests_run`.
  3. Writes enriched fields into the inspection output:
     - `transcript_found: true|false`
     - `transcript_path: <path>` (when found)
     - `transcript_valid: true|false` (basic schema check)
     - `transcript_result: PASS|FAIL|PARTIAL|null`
     - `transcript_tests_run: <count>`
     - `transcript_files_changed: [<paths>]`
- This eliminates the need for `grade_declared_work.py` to independently
  locate and parse transcript files -- it reads pre-validated fields.
- **Testable assertion:** Inspection JSON for a skill_id item MUST contain
  `transcript_found` field. If absent, the inspector is not wired correctly.

---

## GATE S-03: Validate Ledger Cross-Reference (REQUIRED when skill_id + LIVE mode)

- **What:** When transcript shows `mode: LIVE` and item touches `src/` paths, verify `ledger_entry_id` against the product code ledger.
- **How:** Extract `ledger_entry_id` from transcript. Run `validate_product_code_ledger.py`.
- **Validator:** `validate_product_code_ledger.py` -- exit 0 = pass.
- **Grade mapping:**

| Ledger State | Supervisor Grade |
|-------------|-----------------|
| `ledger_entry_id` present, validator pass | No downgrade |
| `ledger_entry_id` missing for LIVE src edit | OVERCLAIMED |
| `ledger_entry_id` present, validator fail | REWORK_REQUIRED |

- **Responsible:** Supervisor grading pipeline.

### R107 Enhancement (R107 NEW)

- `grade_declared_work.py` now reads `transcript_result` from the enriched
  inspection output (Gate S-02 enrichment) and cross-references it with the
  `mode` field. When `mode: LIVE`, it checks for `ledger_entry_id` in the
  transcript data extracted by the inspector.
- This means ledger validation no longer requires a separate transcript-parse
  step in the grader -- the inspector has already extracted the needed fields.

---

## GATE S-04: Scope Boundary Enforcement (REQUIRED when skill_id present)

- **What:** Verify that `actual_files_changed` in the transcript is a subset of `allowed_files`.
- **How:** `validate_skill_transcript.py` performs this check when both fields are present.
- **Failure:** Out-of-scope files => REWORK_REQUIRED with message listing excess files.
- **Responsible:** Supervisor grading pipeline.

### R107 Enhancement (R107 NEW)

- The inspector now exposes `transcript_files_changed` in the enriched output.
  `grade_declared_work.py` can cross-check this against `allowed_files` from
  the registry skill definition without re-parsing the transcript.

---

## GATE S-05: Pre-Sprint Command Validation (REQUIRED)

- **What:** Before grading begins, validate all active command files against the registry.
- **How:** `validate_claude_commands.py` -- exit 0 = all active commands valid.
- **Command:** `.local/venv/Scripts/python tools/supervisor/validate_claude_commands.py`
- **Failure:** Non-zero exit => warning in evidence review. Does not block grading but documented as risk.
- **Responsible:** Supervisor pre-sprint pipeline.

---

## GATE S-06: Registry Consistency (REQUIRED)

- **What:** Verify all `status: active` skills in `.supervisor/skill-registry.yaml` have corresponding command files in `.claude/commands/`.
- **How:** `validate_claude_commands.py` performs cross-reference check.
- **Failure:** Missing command file for active skill => warning. Orphan command file => logged.
- **Responsible:** Skills stream (fix orphans); Supervisor (detect and report).

### R107 Registry Stability Tests (R107 NEW)

- Lane C adds registry stability tests that verify:
  1. All `status: active` entries have non-empty `command_file` paths.
  2. All `command_file` paths resolve to existing files on disk.
  3. No duplicate `skill_id` values exist in the registry.
  4. All `required_handoff_fields` lists are non-empty arrays.
- These tests run as part of `validate_claude_commands.py` and are also
  exercised by dedicated test cases in `tests/supervisor/`.
- **Testable assertion:** `validate_claude_commands.py` exit 0 implies all
  four stability invariants hold.

---

## GATE S-07: Acceleration Boundary Check (REQUIRED)

- **What:** For work items tagged as acceleration stream, verify no `src/` files in `actual_files_changed`.
- **How:** `inspect_declared_evidence.py` scans acceleration-tagged items. Any `src/net/` or `src/python/` path triggers rejection.
- **Failure:** REJECTED -- "Acceleration stream edited product source directly."
- **Responsible:** Supervisor grading pipeline.

---

## GATE S-08: grade_item Handles Transcript Results (REQUIRED) (R107 NEW)

- **What:** The `grade_item()` function in `grade_declared_work.py` MUST
  consume the enriched transcript fields from the inspection output and
  factor them into the grade decision.
- **How:** When `transcript_found: true` in the inspection JSON:
  1. If `transcript_valid: false` => cap grade at OVERCLAIMED.
  2. If `transcript_result: FAIL` => cap grade at REWORK_REQUIRED.
  3. If `transcript_result: PARTIAL` => cap grade at ACCEPTED_WITH_LIMITATIONS.
  4. If `transcript_result: PASS` => no cap from transcript (other gates may
     still downgrade).
  5. If `transcript_found: false` and `skill_id` is present => OVERCLAIMED.
- **Failure:** If `grade_item()` does not check `transcript_found` when
  `skill_id` is present, the self-audit in `autonomous_cycle.py` flags it.
- **Responsible:** Supervisor grading pipeline.

| Inspector Field | grade_item Behavior |
|----------------|---------------------|
| `transcript_found: true, transcript_valid: true, transcript_result: PASS` | No transcript-based cap |
| `transcript_found: true, transcript_valid: true, transcript_result: FAIL` | Cap at REWORK_REQUIRED |
| `transcript_found: true, transcript_valid: true, transcript_result: PARTIAL` | Cap at ACCEPTED_WITH_LIMITATIONS |
| `transcript_found: true, transcript_valid: false` | Cap at OVERCLAIMED |
| `transcript_found: false` + `skill_id` present | Cap at OVERCLAIMED |
| `transcript_found` absent (no `skill_id`) | No transcript check needed |

### Testable Assertions

- Unit test: feed `grade_item()` an inspection dict with `skill_id: X` and
  `transcript_found: false` => output grade MUST be OVERCLAIMED.
- Unit test: feed `grade_item()` an inspection dict with `transcript_result: FAIL`
  => output grade MUST be REWORK_REQUIRED.
- These tests belong in Lane F validator coverage.

---

## Self-Audit (autonomous_cycle.py)

After grading completes, `autonomous_cycle.py` MUST verify:

1. Every work item with `skill_id` had its transcript processed (gate S-02 executed).
2. Every LIVE src-edit item had ledger validation attempted (gate S-03 executed).
3. No acceleration-tagged item has `src/` in evidence paths (gate S-07 executed).
4. **(R107 NEW)** Every work item with `skill_id` has `transcript_found` in its
   inspection output (gate S-08 prerequisite met).

If self-audit fails, `autonomous_continue` is set to `false` with reason: "Supervisor enforcement gates not fully executed."

---

## Quick Reference: Validator Commands

```
# Validate all commands against registry
.local/venv/Scripts/python tools/supervisor/validate_claude_commands.py

# Validate a single transcript
.local/venv/Scripts/python tools/supervisor/validate_skill_transcript.py <path>

# Validate product code ledger
.local/venv/Scripts/python tools/supervisor/validate_product_code_ledger.py

# Run full grading
.local/venv/Scripts/python tools/supervisor/grade_declared_work.py --inspection <i> --declaration <d> --output-dir <o>
```
