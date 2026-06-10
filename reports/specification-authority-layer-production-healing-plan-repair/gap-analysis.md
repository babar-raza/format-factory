# Gap Analysis — Specification Authority Layer Production Blocker Healing Plan
Sprint ID: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-HEALING-PLAN-REPAIR-001

All 9 defects identified in 00-review.md are documented below with root cause and fix.

---

## Defect 1 — Missing autonomous-cycle closeout

**Symptom:** Evidence closeout goes directly to build_declaration_review_package without
running autonomous-cycle.

**Root cause:** Plan omitted the mandatory supervisor grading step. The autonomous-cycle
is the authoritative mechanism by which the supervisor grades a sprint declaration and
determines whether continuation is allowed.

**Impact:** Sprint cannot be accepted. Supervisor will not generate next-sprint.md.
Work-item grades remain unset. Without exit code 0, the AUTONOMOUS_CONTINUE flag cannot
be set to YES.

**Fix:** Add autonomous-cycle step before package build. Command:
  `$PYTHON tools/supervisor/autonomous_cycle.py --declaration <evidence-declaration.yaml>`
Handle exit codes: 0=accepted, 3=rework required, other=runtime failure.

---

## Defect 2 — Missing allowed path for review package

**Symptom:** `.local/supervisor/reviews/specification-authority-layer-production-healing/**`
not listed in the allowed paths section of the plan.

**Root cause:** Review package destination path was implicitly assumed but not declared
in the plan's allowed paths list.

**Impact:** A strict execution agent may refuse to write to an unlisted path. Even without
strict enforcement, the missing declaration makes it unclear whether writing to this path
is authorized.

**Fix:** Add `.local/supervisor/reviews/specification-authority-layer-production-healing/**`
explicitly to the global allowed paths list in the repaired prompt.

---

## Defect 3 — Hardcoded brittle counts

**Symptom:** Validation section asserts "exactly 19 taskcards", "exactly 25 output files",
"exactly 20 Markdown files".

**Root cause:** Counts were written at plan-authoring time without a mechanism to stay
synchronized with the actual task list. Any plan update changes the correct count but not
the assertion.

**Impact:** Spurious validation failures if any count changes during execution (e.g., a
taskcard is added or an output file changes type). The agent may abort a successful sprint
based on a count mismatch that is not actually a problem.

**Fix:** Replace count assertions with declared-vs-materialized checks:
- taskcard-state.json is the source of truth for taskcard count
- file-ownership-map.json is the source of truth for expected output files
- evidence-manifest.yaml is the source of truth for evidence artifacts
Validate that every declared entry exists as a real file — not that a count matches.

---

## Defect 4 — Incorrect taskcard initialization

**Symptom:** taskcard-state.json initialized with all taskcards as IN_PROGRESS.

**Root cause:** Plan author used IN_PROGRESS as a synonym for "planned" rather than
"actively executing". The taskcard lifecycle is not the same as a todo list.

**Impact:** Cannot identify which taskcard is actually active. Lifecycle tracing is broken.
The supervisor grading pipeline cannot determine which taskcards completed successfully
and which are genuinely in flight.

**Fix:** Initialize all taskcards as READY. Mark only the active taskcard as IN_PROGRESS
when work on it begins. Mark CLOSED_VERIFIED only after evidence_paths are populated.
Lifecycle: READY → IN_PROGRESS → CLOSED_VERIFIED.

---

## Defect 5 — Pre-filled PASS verdict

**Symptom:** evidence-declaration.yaml template has `worker_self_verdict: PASS` pre-filled.

**Root cause:** Plan author assumed success before validation ran. The verdict field was
treated as a template placeholder rather than a post-validation result.

**Impact:** Supervisor may downgrade or reject the declaration for non-honest self-assessment.
Pre-filling PASS when validation may not have passed is an integrity violation in the
evidence schema.

**Fix:** Select worker_self_verdict only after all validation checks pass. Use conditional
logic:
  IF all taskcards CLOSED_VERIFIED AND all V-checks pass AND autonomous-cycle exit = 0:
    worker_self_verdict: PASS
  ELIF validation passes with known limitations:
    worker_self_verdict: PARTIAL
  ELSE:
    worker_self_verdict: FAIL

---

## Defect 6 — Non-portable Python command

**Symptom:** All Python commands use bare `python`.

**Root cause:** Python detection was not addressed in the original plan. The plan assumed
`python` is always the correct interpreter.

**Impact:** Commands fail silently on Windows where the venv Python is at
`.local/venv/Scripts/python` and the system `python` may not be on PATH, may be a
different version, or may not have the required packages.

**Fix:** Define a PYTHON variable at the start of the runbook with detection logic:
  Windows preferred: PYTHON=".local/venv/Scripts/python"
  Linux/macOS fallback: PYTHON=".local/venv/bin/python"
  System fallback: PYTHON="python"
Verify: `$PYTHON --version` — must succeed; if not, abort.
All commands use $PYTHON.

---

## Defect 7 — Machine-specific input path

**Symptom:** Plan references `C:\Users\prora\.claude\plans\ticklish-dancing-lobster.md`
as the input plan file for TC-REPAIR-001.

**Root cause:** The plan file was stored in a user-specific Claude session storage location.
This absolute path is only valid on the original user's machine.

**Impact:** Execution fails on any agent or machine that does not have this exact path.
The plan becomes non-portable.

**Fix:** Embed the key architectural decisions inline in the repaired execution prompt
(Option A). No external file path reference is needed when the plan content is included
directly in the prompt as a fenced reference block.

---

## Defect 8 — Generic verdict strings

**Symptom:** Final response format uses `VERDICT: COMPLETE | BLOCKED | PARTIAL`.

**Root cause:** Generic template not replaced with project-specific verdict strings. The
plan was authored using a template that was not customized for this sprint.

**Impact:** Supervisor grading cannot identify the healing sprint outcome correctly. The
pipeline looks for specific macro verdict strings, not generic words.

**Fix:** Use only the three project macro verdicts for the downstream healing sprint:
  SPECIFICATION_AUTHORITY_LAYER_PLAN_HEALED_READY_FOR_MWP_EXECUTION
  SPECIFICATION_AUTHORITY_LAYER_PLAN_HEALED_WITH_LIMITATIONS
  SPECIFICATION_AUTHORITY_LAYER_PLAN_STILL_BLOCKED
Remove all uses of COMPLETE, BLOCKED, PARTIAL as verdict strings.

---

## Defect 9 — Weak validation

**Symptom:** Validation uses hardcoded counts (see Defect 3) and does not check YAML
validity, duplicate file ownership, unresolved taskcards, or autonomous-cycle completion.

**Root cause:** Validation section was written as a checklist template, not as a
comprehensive gate. Individual checks were added ad hoc without a systematic coverage model.

**Impact:** Sprint could pass validation with silent failures. For example, a malformed
YAML file or an unresolved taskcard would not be caught.

**Fix:** Replace count assertions with declared-vs-materialized; add 12 systematic checks:
  V01: All files in file-ownership-map.json exist as real files
  V02: All Markdown files have H1 headings
  V03: All JSON files parse without error
  V04: All YAML files parse without error
  V05: file-ownership-map.json has no duplicate keys
  V06: taskcard-state.json: all entries in terminal state (CLOSED_VERIFIED or CLOSED_SKIPPED_WITH_REASON)
  V07: Final execution prompt contains all 24 required keywords
  V08: No forbidden path changed (git diff --name-only src/ tests/ registry/ product-capability-matrix/)
  V09: autonomous-cycle was run and exit code captured
  V10: Review package ZIP exists at declared path
  V11: SHA-256 computed and recorded in review-package-proof.md
  V12: Final git status captured in final-git-status.txt
