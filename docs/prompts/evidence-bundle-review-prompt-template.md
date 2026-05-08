# Evidence Bundle Review and Next Prompt Template

**Mode:** PLAN MODE ONLY
**Purpose:** Use this template when reviewing an evidence bundle and producing the next execution prompt. Do not produce the next prompt from the summary alone.

---

MODE:
PLAN MODE ONLY.

Sprint type:
PLAN MODE -- Evidence Bundle Review.

Sprint name:
Evidence Bundle Review: <bundle name or sprint name>.

Project:
format-factory

Repo path:
C:\Users\prora\OneDrive\Documents\GitHub\format-factory

Primary evidence input:
<absolute Windows path to the evidence bundle to review>

Goal:
Review the evidence bundle for <sprint/gate name>. Verify the prior sprint claims against
actual bundle contents. Identify any gaps or defects. Produce the next execution prompt.

This is PLAN MODE ONLY. Do not create or modify any repo files. Do not commit. Do not push.

Bundle review steps:

1. Extract the bundle (the agent should inspect its zip entries, not physically extract).
2. Read bundle-metadata/git-log.txt. Confirm HEAD commit.
3. Read bundle-metadata/git-status-final.txt. Confirm clean working tree.
4. Read bundle-metadata/bundle-manifest.yaml. Confirm entry count.
5. Read bundle-metadata/verdict.md. Note the prior sprint verdict.
6. Read bundle-metadata/self-challenge.md. Note any NO answers.
7. For each major claim in the verdict, find and read the supporting artifact in repo/.
8. Run git log --oneline -5 to confirm commits match.
9. Run python tools/evidence/check_current_state_consistency.py.

Challenge checklist:

For each claim in the prior sprint:
- Is the artifact present in the bundle repo/ folder?
- Does the artifact contain the claimed content?
- Is the evidence sufficient to advance to the next gate or sprint?
- Are any taskcards in an unexpected status?
- Are any metadata files missing or incomplete?
- Are there any PENDING markers in the bundle?

Classification:

- CONFIRMED: artifact exists, content matches claim.
- DISPUTED: artifact exists but content does not match claim.
- MISSING: artifact not in bundle.
- INCOMPLETE: artifact exists but content is partial.

Produce the next prompt:

After reviewing the bundle, produce a single-go execution handoff prompt for the next sprint.
Use docs/prompts/execution-handoff-prompt-template.md as the starting structure.
Include:
1. Any defects found in the review as repair steps at the start.
2. The exact primary evidence input path (the bundle just reviewed).
3. The exact next gate or sprint goal.
4. All forbidden paths from the current sprint, plus any new ones identified.
5. All taskcards that need updating.

Do not push.
Do not commit.

Final line:
NEXT_PROMPT_READY: yes
