---
version: "1.1"
last-updated: "2026-05-17"
phase-available: "all"
gate-required: null
created-by: memory-planning-methodology-and-agent-handoff sprint
---

# /evidence-review-next-prompt

Review a provided evidence bundle, challenge the prior sprint claims, and produce the next execution prompt.

## Steps

0. **DEPENDENCY PREFLIGHT** — Verify required files exist before proceeding:
   - `memory/00-index.md`
   - `plans/master-plan.md`
   - `docs/planning-methodology.md`
   - `docs/agent-execution-handoff-standard.md`
   - `tools/evidence/check_current_state_consistency.py`
   - `tools/evidence/validate_evidence_bundle.py`

   If any file is missing: print `BLOCKED: missing dependency <path>` and stop.

1. Read `memory/00-index.md` to identify the most recent memory file. Read that file plus `plans/master-plan.md` Section 33 for current state. Read `docs/planning-methodology.md` and `docs/agent-execution-handoff-standard.md`.
2. Read the evidence bundle (inspect zip entries, read key metadata files):
   - bundle-metadata/git-log.txt (confirm HEAD commit)
   - bundle-metadata/git-status-final.txt (confirm clean tree)
   - bundle-metadata/bundle-manifest.yaml (confirm entry count)
   - bundle-metadata/verdict.md (prior sprint verdict)
   - bundle-metadata/self-challenge.md (any NO answers)
3. For each major claim in the verdict, read the supporting artifact in repo/.
4. Challenge each claim: CONFIRMED, DISPUTED, MISSING, or INCOMPLETE.
5. Run python tools/evidence/check_current_state_consistency.py.
6. Run python tools/evidence/validate_evidence_bundle.py --bundle <path> --contract <contract_file>.
   Select the contract file from `tools/evidence/contracts/` matching the sprint being reviewed.
   Use the file whose name matches the sprint ID. If uncertain, list `tools/evidence/contracts/`
   sorted by modification time (`ls -lt tools/evidence/contracts/` on bash) and use the most
   recent file. Fallback: `tools/evidence/contracts/base-run.yaml`.
7. Produce the next execution prompt using docs/prompts/execution-handoff-prompt-template.md.
8. Do not create repo files. Do not commit. Do not push.

## Output Format

1. Bundle review summary:
   - HEAD commit verified.
   - Clean tree confirmed.
   - Entry count verified.
   - Claim-by-claim table (CONFIRMED / DISPUTED / MISSING).
2. Current-state consistency result.
3. Bundle validation result: BUNDLE_VALIDATION: PASS or FAIL.
4. Identified defects or gaps (to be addressed in next sprint).
5. Next execution prompt (complete, using execution-handoff-prompt-template.md).
6. Final line: NEXT_PROMPT_READY: yes

## Validation

The next prompt must reference the reviewed bundle as its primary evidence input.
The next prompt must include any defects found as repair steps at the start.

## Changelog

- 1.0 (2026-05-08): Initial version. Created in memory-planning-methodology-and-agent-handoff sprint.
- 1.1 (2026-05-17): Add Step 0 dependency preflight. Replace hardcoded memory/09 reference in Step 1 with dynamic most-recent-memory lookup. Add contract selection guidance to Step 6 (was `--contract <contract>` placeholder with no guidance; 93+ contracts exist in directory). Sprint: FORMAT-FACTORY-SKILLS-PRD-HARDENING-001.
