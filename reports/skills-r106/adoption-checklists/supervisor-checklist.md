# Supervisor Adoption Checklist (Skills R106) -- Enforcement Gates

This checklist replaces the R105 advisory version. The supervisor grading pipeline MUST
execute these gates. Skipping a gate makes the grading output incomplete and blocks
autonomous continuation.

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

---

## GATE S-04: Scope Boundary Enforcement (REQUIRED when skill_id present)

- **What:** Verify that `actual_files_changed` in the transcript is a subset of `allowed_files`.
- **How:** `validate_skill_transcript.py` performs this check when both fields are present.
- **Failure:** Out-of-scope files => REWORK_REQUIRED with message listing excess files.
- **Responsible:** Supervisor grading pipeline.

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

---

## GATE S-07: Acceleration Boundary Check (REQUIRED)

- **What:** For work items tagged as acceleration stream, verify no `src/` files in `actual_files_changed`.
- **How:** `inspect_declared_evidence.py` scans acceleration-tagged items. Any `src/net/` or `src/python/` path triggers rejection.
- **Failure:** REJECTED -- "Acceleration stream edited product source directly."
- **Responsible:** Supervisor grading pipeline.

---

## Self-Audit (autonomous_cycle.py)

After grading completes, `autonomous_cycle.py` MUST verify:

1. Every work item with `skill_id` had its transcript processed (gate S-02 executed).
2. Every LIVE src-edit item had ledger validation attempted (gate S-03 executed).
3. No acceleration-tagged item has `src/` in evidence paths (gate S-07 executed).

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
