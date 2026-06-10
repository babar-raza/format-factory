# Cross-Stream Adoption Enforcement (Skills R106)

## Purpose

Upgrade R104/R105 advisory checklists into validator-checkable enforcement rules.
Every rule specifies: what is checked, how it is checked, what happens on failure, and who is responsible.

## Design Principle

R104 produced enforcement YAML packages. R105 added tests for transcript grading. R106 closes the gap: every rule maps to a concrete validator invocation that the supervisor grading pipeline can execute automatically. Advisory ("SHOULD") is eliminated -- rules are either enforced (block/downgrade on failure) or explicitly deferred with a documented reason.

---

## Stream Enforcement Summary

| Stream | Enforcement Document | Validator Integration Point |
|--------|---------------------|-----------------------------|
| Mainstream | `adoption-checklists/mainstream-checklist.md` | `grade_declared_work.py` item-level grading |
| Supervisor | `adoption-checklists/supervisor-checklist.md` | `autonomous_cycle.py` pre-grade pipeline |
| Acceleration | `adoption-checklists/acceleration-checklist.md` | `inspect_declared_evidence.py` path scan |

---

## Enforcement Rules (Cross-Stream)

### RULE CSE-01: Product Source Change Requires skill_id

- **What:** Any work item that modifies files under `src/net/` or `src/python/` MUST declare a `skill_id` field in the evidence declaration.
- **How:** `grade_declared_work.py` inspects `item.evidence_paths` for `src/` prefixes. If found and no `skill_id` field exists, the item is flagged.
- **Failure:** Grade downgraded to `OVERCLAIMED`. Message: "Product source changed without skill_id routing."
- **Responsible:** Mainstream worker (declares skill_id); Supervisor grader (enforces check).

### RULE CSE-02: skill_id Requires Valid Transcript

- **What:** Any work item with a `skill_id` MUST have a corresponding transcript JSON at a declared evidence path.
- **How:** `validate_skill_transcript.py <transcript_path>` called during grading. Transcript must contain: `invocation_id`, `skill_id`, `mode`, `inputs`, `allowed_files`, `actual_files_changed`, `tests_run`, `result`, `timestamp`.
- **Failure:** Missing transcript => `OVERCLAIMED`. Invalid transcript (schema fail) => `OVERCLAIMED`. Valid transcript with `result: FAIL` => `REWORK_REQUIRED`.
- **Responsible:** Mainstream worker (writes transcript); Supervisor grader (validates).

### RULE CSE-03: LIVE Source Edit Requires Ledger Entry

- **What:** Any skill invocation in `mode: LIVE` that edits product source MUST reference a `ledger_entry_id`.
- **How:** `validate_product_code_ledger.py` confirms the `ledger_entry_id` exists in `reports/r90/product-code-change-ledger.json` and matches the declared files.
- **Failure:** Missing ledger entry => `OVERCLAIMED`. Ledger entry does not cover actual changed files => `REWORK_REQUIRED`.
- **Responsible:** Mainstream worker (creates ledger entry before editing); Supervisor grader (validates).

### RULE CSE-04: Acceleration Must Not Edit Product Source

- **What:** Work items attributed to the Acceleration stream MUST NOT have `actual_files_changed` entries under `src/net/` or `src/python/`.
- **How:** `inspect_declared_evidence.py` scans each acceleration-tagged item's evidence paths and transcript `actual_files_changed`. Any `src/` path triggers rejection.
- **Failure:** `REJECTED`. Message: "Acceleration stream edited product source directly. Route through Mainstream via handoff."
- **Responsible:** Acceleration worker (must delegate via handoff); Supervisor grader (enforces boundary).

### RULE CSE-05: Acceleration Gap Selection Must Reference Matrix

- **What:** Every acceleration-generated handoff MUST reference a `gap_id` from `product-capability-matrix/poc-targets.yaml`.
- **How:** Handoff YAML parsed; `gap_id` field checked against matrix entries. Missing or unrecognized `gap_id` flagged.
- **Failure:** `OVERCLAIMED`. Message: "Handoff generated without valid matrix gap_id reference."
- **Responsible:** Acceleration worker (sets gap_id); Skills stream (validates handoff).

### RULE CSE-06: Supervisor Must Grade Transcript When Present

- **What:** When a work item's evidence includes a skill transcript (file matching `**/skill-transcripts/*.json`), the supervisor grading pipeline MUST validate it and factor the result into the grade.
- **How:** `grade_declared_work.py` checks for transcript files in `evidence_paths_found`. If present, calls `validate_skill_transcript.py`. Transcript `result` field feeds into grade decision.
- **Failure:** If supervisor ignores a present transcript, the grading output is considered incomplete. Self-audit: `autonomous_cycle.py` verifies transcript files were processed.
- **Responsible:** Supervisor grading pipeline.

---

## Validator Commands Reference

| Validator | Command | Exit 0 = Pass |
|-----------|---------|----------------|
| Transcript validator | `.local/venv/Scripts/python tools/supervisor/validate_skill_transcript.py <path>` | Valid transcript |
| Ledger validator | `.local/venv/Scripts/python tools/supervisor/validate_product_code_ledger.py` | Ledger consistent |
| Command validator | `.local/venv/Scripts/python tools/supervisor/validate_claude_commands.py` | All commands valid |
| Grading engine | `.local/venv/Scripts/python tools/supervisor/grade_declared_work.py --inspection <i> --declaration <d> --output-dir <o>` | Grade computed |

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

---

## Integration Timeline

- **R106:** Rules documented with validator commands. Enforcement is manual (worker follows rules, supervisor checks).
- **R107+:** `grade_declared_work.py` gains `skill_id` awareness in code. Automatic enforcement in grading loop.
- **R108+:** Pre-sprint pipeline runs command validation and registry consistency automatically.

---

## Decision: ENFORCED (not advisory)

All six rules above are REQUIRED enforcement. There are no RECOMMENDED/OPTIONAL rules in R106. If a rule cannot be enforced in a given sprint (e.g., no transcript validator available), the item MUST declare `skill_enforcement_bypass: true` with a documented reason, and the grade is capped at `ACCEPTED_WITH_LIMITATIONS`.
