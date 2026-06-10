# Final Plan Hardening Review
Sprint ID: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-HEALING-PLAN-REPAIR-FINAL-HARDENING-001
Reviewed: 2026-06-04

## Scope

This review assesses the repaired-final-single-go-execution-prompt.md (output of TC-REPAIR-011)
across 10 hardening dimensions. Phase 1 fixed all 9 structural defects. This review identifies
10 remaining portability, shell-safety, and governance-completeness issues.

---

## Dimension 1 — Absolute Path Portability

**Question:** Do any output files or commands still contain `C:\Users\prora\`?

**Finding:** NEEDS_HARDENING

The TC-REPAIR-011 prompt correctly removed `C:\Users\prora\` from architectural content
and verdict templates. However, the SHA-256 computation script uses inline Python that
may receive the ZIP_PATH as a variable that could be set to a hardcoded value if the
execution agent does not follow the REPO_ROOT pattern. The prompt needs to make REPO_ROOT
detection mandatory and show the ZIP_PATH derivation explicitly so no agent can substitute
a hardcoded path.

**Verdict:** NEEDS_HARDENING — REPO_ROOT detection pattern must be explicitly mandatory in Step 0

---

## Dimension 2 — Banned-String Scan Completeness

**Question:** Does the keyword/banned-string check cover ALL generated artifacts?

**Finding:** NEEDS_HARDENING

The V07 check in the repaired prompt scans only `final-execution-prompt.md` for the 24
required keywords. The banned-string scan is mentioned in repair-decision-log.md but is
not explicitly embedded as a runnable command covering ALL generated artifact files.
An execution agent following the V01–V12 list could complete validation without scanning
gap-analysis.md, repair-decision-log.md, or evidence YAML files.

**Verdict:** NEEDS_HARDENING — banned-string scan must be a standalone V-check covering all files

---

## Dimension 3 — Evidence Root Ambiguity

**Question:** Are the two evidence roots clearly labeled throughout all taskcards?

**Finding:** NEEDS_HARDENING

The repaired prompt correctly defines the evidence roots in Section 3. However, the
naming similarity between `specification-authority-layer-production-healing/` and
`specification-authority-layer-production-healing-plan-repair/` means any agent working
from memory rather than from the prompt text could write to the wrong root. The 4 canonical
labels (HEALING_SPRINT_EVIDENCE_ROOT, REPAIR_SPRINT_EVIDENCE_ROOT, etc.) need to be
referenced throughout the execution sequence, not just defined once in Section 3.

**Verdict:** NEEDS_HARDENING — canonical labels must be referenced at each write point

---

## Dimension 4 — Preflight Governance Reads

**Question:** Does the runbook require reading CLAUDE.md, AGENTS.md, session-resume.md,
and approval-gates.md before lane work begins?

**Finding:** NEEDS_HARDENING

The repaired prompt (TC-REPAIR-011) has no preflight governance reads section. The CLAUDE.md
project instructions require reading session-resume.md and approval-gates.md at session start.
An execution agent that skips this step may proceed in a state where AUTONOMOUS_CONTINUE: NO
is in effect (blocking continuation) without knowing it.

**Verdict:** NEEDS_HARDENING — mandatory governance reads + AUTONOMOUS_CONTINUE gate missing

---

## Dimension 5 — Shell Portability

**Question:** Is the PYTHON setup provided in both Bash and PowerShell syntax?

**Finding:** NEEDS_HARDENING

The TC-REPAIR-011 prompt provides both Bash and PowerShell blocks — this is ALREADY_HANDLED
in Section 1. However, the subsequent runbook steps and validation commands only show
Bash syntax. The REPO_ROOT variable is set differently in Bash vs PowerShell. Commands
using `$PYTHON` work in both shells, but commands using `[ -f ... ]` or `&&` are Bash-only.
The final prompt needs clearer per-command shell notes.

**Verdict:** NEEDS_HARDENING (partial) — PYTHON blocks present; other Bash-only syntax not annotated

---

## Dimension 6 — TC-REPAIR-013b Closure Ordering

**Question:** Does the taskcard specify that CLOSED_VERIFIED requires ALL 6 gate items?

**Finding:** NEEDS_HARDENING

The TC-REPAIR-011 Section 4 mentions the 6-item gate for the evidence closeout taskcard,
which is an improvement. However, the exact 6 items are listed without explicit check
commands. An execution agent needs to know precisely when it is allowed to transition
to CLOSED_VERIFIED — the gate must be actionable, not just descriptive.

**Verdict:** NEEDS_HARDENING — 6-item gate needs explicit actionable check commands

---

## Dimension 7 — Fallback ZIP Contents

**Question:** If build_declaration_review_package.py is unavailable, is the exact fallback
ZIP file list specified?

**Finding:** NEEDS_HARDENING

The TC-REPAIR-011 Section 10 mentions "Create ZIP manually" with "all output files from
reports/..." but does not enumerate the exact list. The `fallback-package-manifest.json`
is not mentioned. A complete, explicit file list is required so an execution agent creates
a valid fallback ZIP without guessing.

**Verdict:** NEEDS_HARDENING — fallback ZIP needs explicit file list including fallback-package-manifest.json

---

## Dimension 8 — Validation Scope Clarity

**Question:** Does the validation section explicitly state that only local validation is
required?

**Finding:** NEEDS_HARDENING

V08 says `git diff HEAD --name-only` (a local command) but does not explicitly state that
no GitHub Actions, no CI pipeline, and no remote push are required. Some execution agents
may interpret "validation" as requiring a CI run. This needs to be made explicit.

**Verdict:** NEEDS_HARDENING — "LOCAL ONLY" must be stated explicitly with CI exclusion list

---

## Dimension 9 — Final Verdict Prose Fallback

**Question:** Does the final response contract prohibit any generic verdict prose?

**Finding:** NEEDS_HARDENING

The TC-REPAIR-011 Section 11 correctly lists 3 macro verdicts and prohibits
"VERDICT: COMPLETE/BLOCKED/PARTIAL". However, it does not explicitly prohibit prose
like "Sprint complete.", "All done.", or "Repair done." — sentences that could act as
implicit verdicts without using a macro string. The prohibition needs to be more explicit.

**Verdict:** NEEDS_HARDENING — explicit prose fallback prohibition needed

---

## Dimension 10 — Final Ready-to-Send Prompt

**Question:** Is there a single `final-ready-to-send-execution-prompt.md` that consolidates
all Phase 1 + Phase 2 repairs?

**Finding:** NEEDS_HARDENING

The `repaired-final-single-go-execution-prompt.md` from TC-REPAIR-011 incorporates all 9
Phase 1 fixes and is directionally correct. However, it predates Phase 2 hardening. A
consolidated `final-ready-to-send-execution-prompt.md` incorporating all 10 hardening fixes
must be produced as the definitive output.

**Verdict:** NEEDS_HARDENING — consolidated final prompt does not yet exist

---

## Summary

| Dimension | Assessment |
|-----------|-----------|
| 1. Absolute path portability | NEEDS_HARDENING |
| 2. Banned-string scan completeness | NEEDS_HARDENING |
| 3. Evidence root ambiguity | NEEDS_HARDENING |
| 4. Preflight governance reads | NEEDS_HARDENING |
| 5. Shell portability | NEEDS_HARDENING (partial) |
| 6. TC-REPAIR-013b closure ordering | NEEDS_HARDENING |
| 7. Fallback ZIP contents | NEEDS_HARDENING |
| 8. Validation scope clarity | NEEDS_HARDENING |
| 9. Final verdict prose fallback | NEEDS_HARDENING |
| 10. Final ready-to-send prompt | NEEDS_HARDENING |

All 10 dimensions require hardening. Final prompt (TC-HARD-011) will address all 10.

---

HARDENING_REQUIRED
