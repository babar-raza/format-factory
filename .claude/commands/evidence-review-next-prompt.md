---
version: "1.0"
last-updated: "2026-05-08"
phase-available: "all"
gate-required: null
created-by: memory-planning-methodology-and-agent-handoff sprint
---

# /evidence-review-next-prompt

Review a provided evidence bundle, challenge the prior sprint claims, and produce the next execution prompt.

## Steps

1. Read memory/00-index.md, plans/master-plan.md, and memory/09-current-state-before-phase1.md.
2. Read docs/planning-methodology.md and docs/agent-execution-handoff-standard.md.
3. Read the evidence bundle (inspect zip entries, read key metadata files):
   - bundle-metadata/git-log.txt (confirm HEAD commit)
   - bundle-metadata/git-status-final.txt (confirm clean tree)
   - bundle-metadata/bundle-manifest.yaml (confirm entry count)
   - bundle-metadata/verdict.md (prior sprint verdict)
   - bundle-metadata/self-challenge.md (any NO answers)
4. For each major claim in the verdict, read the supporting artifact in repo/.
5. Challenge each claim: CONFIRMED, DISPUTED, MISSING, or INCOMPLETE.
6. Run python tools/evidence/check_current_state_consistency.py.
7. Run python tools/evidence/validate_evidence_bundle.py --bundle <path> --contract <contract>.
8. Produce the next execution prompt using docs/prompts/execution-handoff-prompt-template.md.
9. Do not create repo files. Do not commit. Do not push.

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
