# Independent Verification Prompt Template

**Mode:** EXECUTION MODE
**Sprint type:** INDEPENDENT VERIFICATION
**Purpose:** Use this template for DEC-034 independent verification sprints. These sprints verify prior sprint claims by inspecting repo artifacts and evidence bundles without re-executing the work.

---

MODE:
EXECUTION MODE.

Sprint type:
INDEPENDENT VERIFICATION (DEC-034).

Sprint name:
Independent Verification: <sprint or gate being verified>.

Project:
format-factory

Repo path:
C:\Users\prora\OneDrive\Documents\GitHub\format-factory

Primary evidence input:
<absolute Windows path to the evidence bundle being verified>

Goal:
Independently verify the claims made in the evidence bundle for <sprint/gate name>.
This sprint does not re-execute work. It inspects existing artifacts and either confirms
or disputes the prior sprint's claims. Produce a DEC-034 verification report.

This prompt does NOT authorize:
1. Executing any gate work.
2. Modifying any approved artifacts.
3. Creating product source.
4. Pushing.
5. Cleaning, stashing, resetting, restoring, or hiding unrelated working-tree changes.

Hard prohibitions:
Do not modify existing artifacts or evidence.
Do not approve gates (gate approval is human-only).
Do not use git stash, git reset, git restore, git checkout -- <path>, or git clean.
Do not use git add . or git add -A.
Do not push.

Read first:

1. Extract the primary evidence bundle and read:
   - bundle-metadata/git-log.txt (confirm exact HEAD commit)
   - bundle-metadata/git-status-final.txt (confirm clean working tree)
   - bundle-metadata/bundle-manifest.yaml (confirm entry count)
   - bundle-metadata/verdict.md (read prior sprint's verdict)
2. Read the specific artifacts claimed in the prior sprint (list them from the bundle).
3. Read relevant taskcards.
4. Run git log --oneline -10 to confirm the commit exists.
5. Run python tools/governance/check_git_safety.py --metadata-dir <verification-metadata-dir> --classification-file <dirty-state-classification-report>, if a classification file is required by current state.
6. Run python tools/evidence/check_current_state_consistency.py.

Verification steps:

A. Bundle integrity check
1. Validate the bundle: python tools/evidence/validate_evidence_bundle.py --bundle <path> --contract <contract>. Expected: BUNDLE_VALIDATION: PASS.
2. Confirm entry count matches bundle-manifest.yaml.
3. Confirm no forbidden paths.

B. Claim verification
For each major claim in the prior sprint verdict.md:
1. Read the artifact that supports the claim.
2. Confirm the artifact exists and contains the claimed content.
3. Mark each claim CONFIRMED or DISPUTED with evidence.

C. Gate criteria check (if applicable)
1. Read docs/gates.md for the gate being verified.
2. Check each gate criterion against the artifact evidence.
3. Produce a pass/fail result per criterion.

D. DEC-034 report
Create the verification report with:
- Sprint/gate being verified.
- Bundle commit verified.
- Each claim: CONFIRMED or DISPUTED.
- Gate criteria (if applicable): PASS or FAIL per criterion.
- Overall DEC-034 result: PASS or FAIL.

Evidence contract

Contract path: tools/evidence/contracts/<verification-sprint-name>.yaml
Minimum metadata: 20 files
Output: .local/evidence-bundles/<verification-sprint-name>-YYYYMMDD-HHMMSS.zip

Self-challenge

1. Did I inspect the bundle rather than re-run work?
2. Did I verify the bundle commit exists in git?
3. Did I check bundle integrity?
4. Did I verify each major claim against actual artifact content?
5. Did I avoid modifying existing artifacts?
6. Did I avoid gate self-approval?
7. Did I avoid pushing?
8. Did the verification bundle validate?
9. Did I avoid git stash/reset/restore/checkout cleanup/clean?
10. Did I avoid broad staging?

Final response format:

1. Verification summary.
2. Bundle commit verification result.
3. Claim-by-claim verification table (CONFIRMED/DISPUTED).
4. Gate criteria check (if applicable).
5. DEC-034 result: PASS or FAIL.
6. Commit hash.
7. Stream declaration.
8. NO_STASH_RESET_RESTORE_CLEAN_USED: YES

EVIDENCE_BUNDLE: <absolute Windows path to zip>
